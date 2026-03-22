"""
数据类型定义
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum
import numpy as np


class EventType(Enum):
    """事件类型"""
    NONE = 0
    FALL = 1           # 跌倒
    STATIC = 2         # 长时间静止
    NIGHT_ABNORMAL = 3 # 夜间异常


class RiskLevel(Enum):
    """风险等级"""
    LOW = 0
    MEDIUM = 1
    HIGH = 2


@dataclass
class PersonResult:
    """单个人的检测结果"""
    person_id: int                      # 跨帧持久ID，由 SessionManager 分配
    class_id: Optional[int]             # 0=normal, 1=falling, 2=fallen
    class_name: Optional[str]
    confidence: float
    box: List[float]                    # [x1, y1, x2, y2]
    keypoints: Optional[np.ndarray]     # (17, 3)，每点为 [x, y, confidence]
    features: Optional[Dict]            # spine_angle, aspect_ratio（内部调试用）


@dataclass
class FrameResult:
    """单帧检测结果（多人）"""
    detected: bool                      # 是否检测到任何人
    persons: List[PersonResult]         # 检测到的所有人，最多 MAX_PERSONS 个


@dataclass
class Event:
    """异常事件"""
    person_id: int                      # 触发事件的人的 ID，夜间异常为 -1
    event_type: EventType
    risk_level: RiskLevel
    start_time: float                   # 事件开始时间戳
    end_time: float                     # 事件结束时间戳
    duration: float                     # 持续时长（秒）
    frame_count: int                    # 涉及帧数
    snapshot: Optional[np.ndarray] = None  # 触发时的关键帧（BGR），可用于存档


@dataclass
class SessionResult:
    """会话处理结果"""
    video_id: str
    frame_result: FrameResult
    events: List[Event] = field(default_factory=list)  # 本帧触发的所有事件（可能多人同时触发）
    processed_frame: Optional[np.ndarray] = None       # 人脸模糊后的帧，不需要发给前端时可忽略
