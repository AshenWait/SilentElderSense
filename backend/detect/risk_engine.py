"""
风险判定引擎

基于 core 返回的逐帧检测数据，在后端判定事件类型和风险等级。
不依赖 core 内部逻辑，仅消费 PersonResult 数据。

风险规则：
  FALLEN:         连续 5 帧 fallen → MEDIUM；持续 ≥1s → HIGH
  STILLNESS:      30s 窗口内 movement 始终 < 5px → LOW；持续 ≥60s → MEDIUM
  NIGHT_ABNORMAL: 夜间(22:00-07:00) + STILLNESS + 实时流 → MEDIUM（不升级）

  FALLEN 是唯一能到 HIGH 的路径。
  FALLEN 与 NIGHT_ABNORMAL 完全独立，同时存在时均对用户显示。
"""
import logging
import os
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple

from core.types import PersonResult


# ==================== 日志配置 ====================
LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'log')
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger('risk_engine')
logger.setLevel(logging.DEBUG)
logger.handlers.clear()  # 避免重复添加

# 文件处理器
log_file = os.path.join(LOG_DIR, 'risk_engine.log')
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
logger.addHandler(file_handler)


# ==================== 风险常量 ====================

class RiskLevel(Enum):
    """风险等级"""
    NORMAL = 'NORMAL'
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'

    @classmethod
    def order(cls) -> Dict[str, int]:
        """返回风险等级优先级映射，用于比较"""
        return {'NORMAL': 0, 'LOW': 1, 'MEDIUM': 2, 'HIGH': 3}


class RiskReason(Enum):
    """风险原因"""
    FALLEN = 'fallen'
    STILLNESS = 'stillness'
    NIGHT_ABNORMAL = 'night_abnormal'


# BGR 颜色映射（用于绘制检测框）
RISK_COLORS_BGR = {
    'HIGH': (0, 0, 255),      # 红色
    'MEDIUM': (0, 255, 255),  # 黄色
    'LOW': (255, 191, 0),     # 浅蓝
    'NORMAL': (0, 255, 0),    # 绿色
}

# 中文标签映射（用于帧上文字）
RISK_REASON_LABELS = {
    'fallen': '跌倒',
    'stillness': '长时间静止',
    'night_abnormal': '夜间异常',
}


# 默认判定参数（当数据库配置不可用时使用）
DEFAULT_CONFIG = {
    'FALLEN_CONFIRM_FRAMES': 5,
    'FALLEN_ESCALATE_SECS': 1.0,
    'STILLNESS_WINDOW_SECS': 30.0,
    'STILLNESS_MOVEMENT_THRESHOLD': 5.0,
    'STILLNESS_ESCALATE_SECS': 60.0,
    'NIGHT_START_HOUR': 22,
    'NIGHT_END_HOUR': 7,
    'LOST_GRACE_SECS': 1.0
}


@dataclass
class PersonRisk:
    """单人当前帧的风险结果"""
    person_id: int
    box: List[float]
    risk_level: str              # NORMAL / LOW / MEDIUM / HIGH
    risk_reason: Optional[str]   # fallen / stillness / night_abnormal / None
    event_type: Optional[str]    # FALLEN / STILLNESS / NIGHT_ABNORMAL / None


@dataclass
class EventChange:
    """事件生命周期变更信号，供路由层持久化使用"""
    change_type: str          # 'started' | 'risk_upgraded' | 'ended'
    person_id: int
    event_type: str           # 'FALLEN' | 'STILLNESS'
    risk_level: str
    start_ts: float
    end_ts: Optional[float] = None
    frame_count: int = 0


@dataclass
class _MovementEntry:
    ts: float
    movement: float


@dataclass
class PersonRiskState:
    """单人的跨帧状态"""
    # FALLEN
    fallen_count: int = 0
    fallen_event_start_ts: Optional[float] = None  # None 表示无活跃 FALLEN 事件

    # STILLNESS（优化：用计数器代替全窗口扫描）
    movement_window: deque = field(default_factory=deque)  # deque of _MovementEntry
    movement_above_threshold_count: int = 0                 # 窗口内 movement >= 阈值的条目数
    stillness_event_start_ts: Optional[float] = None       # None 表示无活跃 STILLNESS 事件

    # 持久化事件追踪（对应数据库中的一条记录）
    db_event_type: Optional[str] = None        # 当前正在写库的事件类型
    db_event_risk_level: Optional[str] = None  # 当前写库事件的风险等级
    db_event_start_ts: Optional[float] = None  # 当前写库事件的开始时间戳
    db_event_frame_count: int = 0              # 当前写库事件累积帧数


class _SessionState:
    def __init__(self, is_live: bool, user_id: Optional[int] = None, config: Dict = None):
        self.is_live = is_live
        self.user_id = user_id
        self.config = config or DEFAULT_CONFIG.copy()
        self.persons: Dict[int, PersonRiskState] = {}
        self.pending_removal: Dict[int, float] = {}  # person_id -> 消失时间戳

    def get_person(self, person_id: int) -> PersonRiskState:
        if person_id not in self.persons:
            self.persons[person_id] = PersonRiskState()
        return self.persons[person_id]


class RiskEngine:
    """
    风险判定引擎

    使用方式:
        engine = RiskEngine()
        engine.create_session(video_id, is_live=True, user_id=1)
        risks = engine.process(video_id, frame_result.persons, time.time())
        engine.close_session(video_id)
    """

    def __init__(self):
        self._sessions: Dict[str, _SessionState] = {}

    def _load_user_config(self, user_id: int) -> Dict:
        """从数据库加载用户配置"""
        try:
            from .service import get_detection_config_service
            service = get_detection_config_service()
            return service.get_runtime_config(user_id)
        except Exception as e:
            logger.warning(f"加载用户 {user_id} 检测配置失败，使用默认配置: {e}")
            return DEFAULT_CONFIG.copy()

    def get_user_id(self, video_id: str) -> Optional[int]:
        session = self._sessions.get(video_id)
        return session.user_id if session else None

    def create_session(self, video_id: str, is_live: bool = False, user_id: Optional[int] = None):
        # 加载用户配置
        config = DEFAULT_CONFIG.copy()
        if user_id:
            config = self._load_user_config(user_id)
        self._sessions[video_id] = _SessionState(is_live=is_live, user_id=user_id, config=config)

    def close_session(self, video_id: str, now: Optional[float] = None) -> List[EventChange]:
        """关闭会话，返回所有未结束事件的 ended 变更"""
        session = self._sessions.pop(video_id, None)
        if session is None:
            return []
        if now is None:
            now = time.time()
        changes = []
        all_persons = {**session.persons}
        for pid, state in all_persons.items():
            if state.db_event_type:
                changes.append(EventChange(
                    change_type='ended',
                    person_id=pid,
                    event_type=state.db_event_type,
                    risk_level=state.db_event_risk_level,
                    start_ts=state.db_event_start_ts,
                    end_ts=now,
                    frame_count=state.db_event_frame_count,
                ))
        return changes

    def process(self, video_id: str, persons: List[PersonResult], now: float) -> Tuple[List[PersonRisk], List[EventChange]]:
        """
        处理一帧的检测结果，返回每人的风险评估和本帧产生的事件变更。

        Args:
            video_id: 会话 ID
            persons:  core 返回的本帧人员列表
            now:      当前时间戳（time.time()）

        Returns:
            (每人的 PersonRisk 列表, 本帧事件变更列表)
        """
        session = self._sessions.get(video_id)
        if session is None:
            logger.warning(f"[{video_id}] Session not found")
            return [], []

        # 使用会话的配置
        config = session.config

        event_changes: List[EventChange] = []

        # 先处理宽限期超时的人员：强制结束其事件
        expired_pids = [pid for pid, ts in session.pending_removal.items() if now - ts >= config['LOST_GRACE_SECS']]
        for pid in expired_pids:
            state = session.persons.get(pid)
            if state and state.db_event_type:
                event_changes.append(EventChange(
                    change_type='ended',
                    person_id=pid,
                    event_type=state.db_event_type,
                    risk_level=state.db_event_risk_level,
                    start_ts=state.db_event_start_ts,
                    end_ts=now,
                    frame_count=state.db_event_frame_count,
                ))
            if pid in session.persons:
                del session.persons[pid]
            del session.pending_removal[pid]

        # 记录追踪状态
        prev_ids = set(session.persons.keys()) | set(session.pending_removal.keys())
        results = []
        current_person_ids = set()

        person_info = [(p.person_id, p.class_name, f"{p.movement:.1f}" if p.movement else "None") for p in persons]
        logger.debug(f"[{video_id}] Detected: {len(persons)} persons | {person_info}")

        for person in persons:
            current_person_ids.add(person.person_id)

            # 若在宽限期内重新出现，从 pending_removal 恢复
            if person.person_id in session.pending_removal:
                del session.pending_removal[person.person_id]

            state = session.get_person(person.person_id)
            fallen_risk, fallen_reason, fallen_event = self._eval_fallen(state, person, now, config)
            stillness_risk, stillness_reason, stillness_event = self._eval_stillness(
                state, person, now, session.is_live, config
            )

            # FALLEN 进行中时抑制 STILLNESS（重置 stillness 状态，防止虚假积累）
            if fallen_event == 'FALLEN':
                state.stillness_event_start_ts = None
                risk_level = fallen_risk
                risk_reason = fallen_reason
                event_type = fallen_event
            else:
                risk_order = RiskLevel.order()
                if risk_order[fallen_risk] >= risk_order[stillness_risk]:
                    risk_level = fallen_risk
                    risk_reason = fallen_reason
                    event_type = fallen_event
                else:
                    risk_level = stillness_risk
                    risk_reason = stillness_reason
                    event_type = stillness_event

            # 记录风险结果
            if risk_level != 'NORMAL':
                logger.info(f"[{video_id}] Person {person.person_id}: {risk_level} | {risk_reason} | fallen_count={state.fallen_count}")

            results.append(PersonRisk(
                person_id=person.person_id,
                box=person.box,
                risk_level=risk_level,
                risk_reason=risk_reason,
                event_type=event_type,
            ))

            # ── 事件持久化信号 ──
            if event_type is None:
                # 当前无风险事件
                if state.db_event_type:
                    event_changes.append(EventChange(
                        change_type='ended',
                        person_id=person.person_id,
                        event_type=state.db_event_type,
                        risk_level=state.db_event_risk_level,
                        start_ts=state.db_event_start_ts,
                        end_ts=now,
                        frame_count=state.db_event_frame_count,
                    ))
                    state.db_event_type = None
                    state.db_event_risk_level = None
                    state.db_event_start_ts = None
                    state.db_event_frame_count = 0
            elif state.db_event_type != event_type:
                # 事件类型切换：先结束旧事件，再开始新事件
                if state.db_event_type:
                    event_changes.append(EventChange(
                        change_type='ended',
                        person_id=person.person_id,
                        event_type=state.db_event_type,
                        risk_level=state.db_event_risk_level,
                        start_ts=state.db_event_start_ts,
                        end_ts=now,
                        frame_count=state.db_event_frame_count,
                    ))
                state.db_event_type = event_type
                state.db_event_risk_level = risk_level
                state.db_event_start_ts = now
                state.db_event_frame_count = 1
                event_changes.append(EventChange(
                    change_type='started',
                    person_id=person.person_id,
                    event_type=event_type,
                    risk_level=risk_level,
                    start_ts=now,
                    frame_count=1,
                ))
            else:
                # 同一事件持续
                state.db_event_frame_count += 1
                if risk_level != state.db_event_risk_level:
                    state.db_event_risk_level = risk_level
                    event_changes.append(EventChange(
                        change_type='risk_upgraded',
                        person_id=person.person_id,
                        event_type=event_type,
                        risk_level=risk_level,
                        start_ts=state.db_event_start_ts,
                        frame_count=state.db_event_frame_count,
                    ))

        # 新消失的人员进入宽限期
        lost_ids = (set(session.persons.keys()) - current_person_ids) - set(session.pending_removal.keys())
        new_ids = current_person_ids - prev_ids

        if lost_ids:
            logger.debug(f"[{video_id}] Lost IDs (grace): {lost_ids}")
        if new_ids:
            logger.debug(f"[{video_id}] New IDs: {new_ids}")

        for pid in lost_ids:
            session.pending_removal[pid] = now

        return results, event_changes

    def _eval_fallen(
        self, state: PersonRiskState, person: PersonResult, now: float, config: Dict
    ) -> Tuple[str, Optional[str], Optional[str]]:
        """返回 (risk_level, risk_reason, event_type)"""
        if person.class_id == 1:
            state.fallen_count += 1
        else:
            # 离开 fallen 状态，重置；同时清空 stillness 窗口防止虚假触发
            state.fallen_count = 0
            state.fallen_event_start_ts = None
            state.stillness_event_start_ts = None
            state.movement_window.clear()
            state.movement_above_threshold_count = 0
            return RiskLevel.NORMAL.value, None, None

        # 连续帧达到阈值，激活事件
        if state.fallen_count >= config['FALLEN_CONFIRM_FRAMES']:
            if state.fallen_event_start_ts is None:
                state.fallen_event_start_ts = now

            elapsed = now - state.fallen_event_start_ts
            if elapsed >= config['FALLEN_ESCALATE_SECS']:
                return RiskLevel.HIGH.value, RiskReason.FALLEN.value, 'FALLEN'
            return RiskLevel.MEDIUM.value, RiskReason.FALLEN.value, 'FALLEN'

        return RiskLevel.NORMAL.value, None, None

    def _eval_stillness(
        self, state: PersonRiskState, person: PersonResult, now: float, is_live: bool, config: Dict
    ) -> Tuple[str, Optional[str], Optional[str]]:
        """返回 (risk_level, risk_reason, event_type)"""
        movement = person.movement

        # 首帧 movement 为 None，跳过
        if movement is None:
            return RiskLevel.NORMAL.value, None, None

        # 添加新条目，更新计数器
        is_above = movement >= config['STILLNESS_MOVEMENT_THRESHOLD']
        state.movement_window.append(_MovementEntry(ts=now, movement=movement))
        if is_above:
            state.movement_above_threshold_count += 1

        # 剔除过期条目，同步更新计数器
        cutoff = now - config['STILLNESS_WINDOW_SECS']
        while state.movement_window and state.movement_window[0].ts < cutoff:
            removed = state.movement_window.popleft()
            if removed.movement >= config['STILLNESS_MOVEMENT_THRESHOLD']:
                state.movement_above_threshold_count -= 1

        # 窗口时长不足（允许 10% 容差），认为还在积累数据
        if not state.movement_window:
            return RiskLevel.NORMAL.value, None, None
        window_duration = now - state.movement_window[0].ts
        if window_duration < config['STILLNESS_WINDOW_SECS'] * 0.9:
            state.stillness_event_start_ts = None
            return RiskLevel.NORMAL.value, None, None

        # 使用计数器判断：窗口内存在超出阈值的帧 → 不静止，重置
        if state.movement_above_threshold_count > 0:
            state.stillness_event_start_ts = None
            return RiskLevel.NORMAL.value, None, None

        # 静止成立，激活事件
        if state.stillness_event_start_ts is None:
            state.stillness_event_start_ts = state.movement_window[0].ts

        elapsed = now - state.stillness_event_start_ts

        # 夜间异常（仅实时流）：覆盖普通静止，始终 MEDIUM
        if is_live and self._is_night(now, config):
            return RiskLevel.MEDIUM.value, RiskReason.NIGHT_ABNORMAL.value, 'NIGHT_ABNORMAL'

        if elapsed >= config['STILLNESS_ESCALATE_SECS']:
            return RiskLevel.MEDIUM.value, RiskReason.STILLNESS.value, 'STILLNESS'
        return RiskLevel.LOW.value, RiskReason.STILLNESS.value, 'STILLNESS'

    def _is_night(self, ts: float, config: Dict) -> bool:
        """判断时间戳是否处于夜间"""
        hour = datetime.fromtimestamp(ts).hour
        return hour >= config['NIGHT_START_HOUR'] or hour < config['NIGHT_END_HOUR']


# 全局单例
risk_engine = RiskEngine()
