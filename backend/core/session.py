"""
会话管理 - 时序逻辑处理
"""
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from typing import Optional, List, Dict
import numpy as np

from .types import FrameResult, PersonResult, Event, EventType, RiskLevel


def _iou(box1: List[float], box2: List[float]) -> float:
    """计算两个检测框的 IoU"""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - intersection
    return intersection / (union + 1e-6)


@dataclass
class PersonContext:
    """单个人的时序状态"""
    person_id: int
    last_seen: float = 0.0

    # 历史帧 (timestamp, PersonResult)
    history: deque = field(default_factory=lambda: deque(maxlen=300))

    # 状态计数
    normal_count: int = 0
    falling_count: int = 0
    fallen_count: int = 0

    # 事件追踪
    last_event_time: float = 0.0

    # 静止检测
    last_position: Optional[np.ndarray] = None
    static_frames: int = 0
    static_start_time: Optional[float] = None


@dataclass
class SessionContext:
    """会话上下文"""
    video_id: str
    created_at: float = field(default_factory=time.time)

    # 每个人的状态 {person_id: PersonContext}
    persons: Dict[int, PersonContext] = field(default_factory=dict)

    # 跨帧追踪：记录上一帧的检测框和对应 person_id，用于 IoU 匹配
    prev_boxes: List[List[float]] = field(default_factory=list)
    prev_person_ids: List[int] = field(default_factory=list)
    next_person_id: int = 0

    frame_count: int = 0



class SessionManager:
    """
    会话管理器

    处理时序逻辑：
    - 跌倒检测：连续 N 帧中 fallen 占比超过阈值
    - 长时间静止：持续 M 秒无明显位移
    - 夜间异常：夜间时段异常活动频率

    多人支持：
    - 每帧检测到的多个人通过 IoU 匹配上一帧，分配持久 person_id
    - 每个人独立维护时序状态
    """

    # 跌倒检测阈值
    FALLEN_FRAMES_THRESHOLD = 10
    FALL_CONFIRM_RATIO = 0.7

    # 静止检测阈值
    STATIC_DURATION_THRESHOLD = 30.0
    STATIC_MOVEMENT_THRESHOLD = 10.0

    # 事件冷却时间（秒）
    EVENT_COOLDOWN = 10.0

    # 人员追踪阈值
    IOU_MATCH_THRESHOLD = 0.3   # IoU 低于此值视为不同人
    PERSON_LOST_TIMEOUT = 2.0   # 超过此秒数未出现则清除该人的状态

    def __init__(self):
        self.sessions: Dict[str, SessionContext] = {}

    def create_session(self) -> str:
        video_id = str(uuid.uuid4())[:8]
        self.sessions[video_id] = SessionContext(video_id=video_id)
        return video_id

    def close_session(self, video_id: str) -> bool:
        if video_id in self.sessions:
            del self.sessions[video_id]
            return True
        return False

    def get_session(self, video_id: str) -> Optional[SessionContext]:
        return self.sessions.get(video_id)

    def process(self, video_id: str, frame_result: FrameResult,
                timestamp: float, frame: np.ndarray = None) -> List[Event]:
        """
        处理帧结果，返回本帧触发的所有事件

        Args:
            video_id: 会话ID
            frame_result: 当前帧检测结果（多人）
            timestamp: 时间戳
            frame: 原始帧（用于保存事件快照）

        Returns:
            本帧触发的事件列表，无事件时为空列表
        """
        ctx = self.sessions.get(video_id)
        if ctx is None:
            return []

        ctx.frame_count += 1
        events = []

        if not frame_result.detected:
            return events

        # 1. IoU 匹配：为当前帧每个检测分配持久 person_id
        curr_boxes = [p.box for p in frame_result.persons]
        assigned_ids = self._assign_person_ids(ctx, curr_boxes)

        # 更新追踪记录
        ctx.prev_boxes = curr_boxes
        ctx.prev_person_ids = assigned_ids

        # 2. 清理长时间未出现的人员状态
        for pid in list(ctx.persons.keys()):
            if timestamp - ctx.persons[pid].last_seen > self.PERSON_LOST_TIMEOUT:
                del ctx.persons[pid]

        # 3. 逐人更新状态并检测事件
        for person, person_id in zip(frame_result.persons, assigned_ids):
            if person_id not in ctx.persons:
                ctx.persons[person_id] = PersonContext(person_id=person_id)
            pctx = ctx.persons[person_id]
            pctx.last_seen = timestamp

            self._update_person_counts(pctx, person, timestamp)

            event = self._check_fall(pctx, person_id, timestamp, frame)
            if event:
                events.append(event)

            event = self._check_static(pctx, person_id, timestamp, frame, person)
            if event:
                events.append(event)

        return events

    def _assign_person_ids(self, ctx: SessionContext,
                           curr_boxes: List[List[float]]) -> List[int]:
        """
        IoU 匹配：将当前帧检测框与上一帧匹配，分配持久 person_id

        匹配成功（IoU > 阈值）：沿用上一帧的 person_id
        匹配失败（新出现的人）：分配新 person_id
        """
        if not ctx.prev_boxes:
            ids = []
            for _ in curr_boxes:
                ids.append(ctx.next_person_id)
                ctx.next_person_id += 1
            return ids

        assigned = [-1] * len(curr_boxes)
        used_prev = set()

        for ci, cbox in enumerate(curr_boxes):
            best_iou = self.IOU_MATCH_THRESHOLD
            best_pi = -1
            for pi, pbox in enumerate(ctx.prev_boxes):
                if pi in used_prev:
                    continue
                iou = _iou(cbox, pbox)
                if iou > best_iou:
                    best_iou = iou
                    best_pi = pi
            if best_pi >= 0:
                assigned[ci] = ctx.prev_person_ids[best_pi]
                used_prev.add(best_pi)

        for ci in range(len(curr_boxes)):
            if assigned[ci] == -1:
                assigned[ci] = ctx.next_person_id
                ctx.next_person_id += 1

        return assigned

    def _update_person_counts(self, pctx: PersonContext, person: PersonResult,
                              timestamp: float):
        pctx.history.append((timestamp, person))

        if person.class_id == 0:
            pctx.normal_count += 1
            pctx.falling_count = max(0, pctx.falling_count - 1)
            pctx.fallen_count = max(0, pctx.fallen_count - 1)
        elif person.class_id == 1:
            pctx.falling_count += 1
        elif person.class_id == 2:
            pctx.fallen_count += 1
            pctx.normal_count = max(0, pctx.normal_count - 1)

    def _check_fall(self, pctx: PersonContext, person_id: int,
                    timestamp: float, frame: np.ndarray = None) -> Optional[Event]:
        if len(pctx.history) < 5:
            return None
        if timestamp - pctx.last_event_time < self.EVENT_COOLDOWN:
            return None

        recent = list(pctx.history)[-self.FALLEN_FRAMES_THRESHOLD:]
        fallen_count = sum(1 for _, r in recent if r.class_id == 2)

        if fallen_count >= self.FALLEN_FRAMES_THRESHOLD * self.FALL_CONFIRM_RATIO:
            start_time = recent[0][0]
            event = Event(
                person_id=person_id,
                event_type=EventType.FALL,
                risk_level=RiskLevel.HIGH,
                start_time=start_time,
                end_time=timestamp,
                duration=timestamp - start_time,
                frame_count=fallen_count,
                snapshot=frame.copy() if frame is not None else None
            )
            pctx.last_event_time = timestamp
            return event

        return None

    def _check_static(self, pctx: PersonContext, person_id: int,
                      timestamp: float, frame: np.ndarray,
                      person: PersonResult) -> Optional[Event]:
        if person.keypoints is None:
            return None
        if timestamp - pctx.last_event_time < self.EVENT_COOLDOWN:
            return None

        valid_kps = person.keypoints[person.keypoints[:, 2] > 0.3]
        if len(valid_kps) < 3:
            return None

        current_pos = np.mean(valid_kps[:, :2], axis=0)

        if pctx.last_position is not None:
            movement = np.linalg.norm(current_pos - pctx.last_position)
            if movement < self.STATIC_MOVEMENT_THRESHOLD:
                pctx.static_frames += 1
                if pctx.static_start_time is None:
                    pctx.static_start_time = timestamp
            else:
                pctx.static_frames = 0
                pctx.static_start_time = None

        pctx.last_position = current_pos

        if pctx.static_start_time is not None:
            static_duration = timestamp - pctx.static_start_time
            if static_duration >= self.STATIC_DURATION_THRESHOLD:
                event = Event(
                    person_id=person_id,
                    event_type=EventType.STATIC,
                    risk_level=RiskLevel.MEDIUM,
                    start_time=pctx.static_start_time,
                    end_time=timestamp,
                    duration=static_duration,
                    frame_count=pctx.static_frames,
                    snapshot=frame.copy() if frame is not None else None
                )
                pctx.last_event_time = timestamp
                return event

        return None

