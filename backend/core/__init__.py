"""
跌倒检测核心模块

接口:
    FallDetector               - 检测器类
    create_session()           - 创建会话
    process_frame()            - 处理帧（同步，用于脚本/测试）
    process_frame_async()      - 处理帧（异步，用于 Quart/asyncio 后端）
    close_session()            - 关闭会话
"""

from .types import (
    PersonResult,
    FrameResult,
    SessionResult,
)

from .fall_detector import FallDetector

__all__ = [
    # 检测器
    'FallDetector',
    # 类型
    'PersonResult',
    'FrameResult',
    'SessionResult',
]