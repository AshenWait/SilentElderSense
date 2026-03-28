"""
数据类型定义
"""
from dataclasses import dataclass
from typing import Optional, List
import numpy as np


@dataclass
class PersonResult:
    """单个人的检测结果"""
    person_id: int                      # 追踪ID (ByteTrack)
    class_id: int                       # 0=normal, 1=fallen
    class_name: str                     # "normal" / "fallen"
    confidence: float                   # 置信度
    box: List[float]                    # [x1, y1, x2, y2]
    movement: Optional[float] = None    # 相比上一帧的位移（像素），首帧为 None


@dataclass
class FrameResult:
    """单帧检测结果（多人）"""
    detected: bool                      # 是否检测到任何人
    persons: List[PersonResult]         # 检测到的所有人


@dataclass
class SessionResult:
    """会话处理结果"""
    video_id: str
    frame_result: FrameResult
    processed_frame: Optional[np.ndarray] = None  # 人脸模糊后的帧