"""
会话管理 - 追踪 + 状态统计
"""
import time
import uuid
from typing import Optional, List, Dict
import numpy as np

from boxmot import ByteTrack

from .types import FrameResult, PersonResult


class SessionContext:
    """会话上下文"""
    def __init__(self, video_id: str, tracker_fps: float = 25.0):
        self.video_id = video_id
        self.created_at = time.time()
        self.frame_count = 0

        # ByteTrack 追踪器
        self.tracker = ByteTrack(
            track_thresh=0.3,
            match_thresh=0.8,
            frame_rate=tracker_fps,
            max_age=30,
            min_hits=1,
        )

        # 记录每个人上一帧的位置，用于计算 movement
        self.last_positions: Dict[int, np.ndarray] = {}


class SessionManager:
    """
    会话管理器

    只负责：
    - 多人追踪 (ByteTrack)
    - 计算每人的位移 (movement)
    """

    def __init__(self, tracker_fps: float = 25.0):
        self.sessions: Dict[str, SessionContext] = {}
        self.tracker_fps = tracker_fps

    def create_session(self) -> str:
        video_id = str(uuid.uuid4())[:8]
        self.sessions[video_id] = SessionContext(video_id, self.tracker_fps)
        return video_id

    def close_session(self, video_id: str) -> bool:
        if video_id in self.sessions:
            del self.sessions[video_id]
            return True
        return False

    def get_session(self, video_id: str) -> Optional[SessionContext]:
        return self.sessions.get(video_id)

    def process(self, video_id: str, frame_result: FrameResult,
                frame: np.ndarray = None) -> FrameResult:
        """
        处理帧结果，返回带有追踪ID和位移的检测结果

        Args:
            video_id: 会话ID
            frame_result: 当前帧检测结果
            frame: 原始帧（用于ByteTrack追踪）

        Returns:
            FrameResult: 带有 person_id 和 movement 的检测结果
        """
        ctx = self.sessions.get(video_id)
        if ctx is None:
            return frame_result

        ctx.frame_count += 1

        if not frame_result.detected:
            return frame_result

        # 1. 使用 ByteTrack 追踪
        tracked_persons = self._track(ctx, frame_result, frame)

        # 2. 计算每个人的 movement
        for person in tracked_persons:
            person.movement = self._calculate_movement(ctx, person)

        # 3. 清理丢失的追踪
        current_ids = {p.person_id for p in tracked_persons}
        for pid in list(ctx.last_positions.keys()):
            if pid not in current_ids:
                del ctx.last_positions[pid]

        return FrameResult(detected=True, persons=tracked_persons)

    def _track(self, ctx: SessionContext, frame_result: FrameResult,
               frame: np.ndarray) -> List[PersonResult]:
        """使用 ByteTrack 追踪"""
        if frame is None:
            return frame_result.persons

        # 构建检测框 [x1, y1, x2, y2, conf, cls]
        detections = []
        for p in frame_result.persons:
            det = p.box + [p.confidence, p.class_id]
            detections.append(det)

        if not detections:
            tracks = ctx.tracker.update(np.empty((0, 6)), frame)
        else:
            dets = np.array(detections)
            tracks = ctx.tracker.update(dets, frame)

        # 构建追踪结果
        tracked = []
        for track in tracks:
            x1, y1, x2, y2, track_id, conf, cls = track[:7]
            track_id = int(track_id)

            tracked.append(PersonResult(
                person_id=track_id,
                class_id=int(cls),
                class_name={0: "normal", 1: "fallen"}.get(int(cls), "unknown"),
                confidence=float(conf),
                box=[float(x1), float(y1), float(x2), float(y2)],
                movement=None  # 稍后计算
            ))

        return tracked

    def _calculate_movement(self, ctx: SessionContext, person: PersonResult) -> Optional[float]:
        """计算相比上一帧的位移"""
        box = person.box
        current_pos = np.array([(box[0] + box[2]) / 2, (box[1] + box[3]) / 2])

        last_pos = ctx.last_positions.get(person.person_id)
        ctx.last_positions[person.person_id] = current_pos

        if last_pos is None:
            return None  # 首帧无位移

        movement = np.linalg.norm(current_pos - last_pos)
        return float(movement)