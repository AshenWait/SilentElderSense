"""
检测配置数据模型

用户级别配置，用于风险判定参数的动态调整
"""
from sqlalchemy import Column, Integer, Float, DateTime
from datetime import datetime
from auth.models import Base


class DetectionConfig(Base):
    """检测配置 - 用户级别参数"""
    __tablename__ = 'detection_configs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True, unique=True)

    # 跌倒检测参数
    fallen_confirm_frames = Column(Integer, default=5)      # 连续跌倒帧数确认阈值
    fallen_escalate_secs = Column(Float, default=1.0)       # 跌倒升级时间（秒）

    # 静止检测参数
    stillness_window_secs = Column(Float, default=30.0)     # 静止判定窗口（秒）
    stillness_movement_threshold = Column(Float, default=5.0)  # 静止判定阈值（像素）
    stillness_escalate_secs = Column(Float, default=60.0)   # 静止升级时间（秒）

    # 夜间时段参数
    night_start_hour = Column(Integer, default=22)          # 夜间开始时段（22:00）
    night_end_hour = Column(Integer, default=7)             # 夜间结束时段（07:00）

    # 人员追踪参数
    lost_grace_secs = Column(Float, default=1.0)            # 人员消失宽限期（秒）

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'fallen_confirm_frames': self.fallen_confirm_frames,
            'fallen_escalate_secs': self.fallen_escalate_secs,
            'stillness_window_secs': self.stillness_window_secs,
            'stillness_movement_threshold': self.stillness_movement_threshold,
            'stillness_escalate_secs': self.stillness_escalate_secs,
            'night_start_hour': self.night_start_hour,
            'night_end_hour': self.night_end_hour,
            'lost_grace_secs': self.lost_grace_secs,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def get_defaults(cls):
        """返回默认配置值"""
        return {
            'fallen_confirm_frames': 5,
            'fallen_escalate_secs': 1.0,
            'stillness_window_secs': 30.0,
            'stillness_movement_threshold': 5.0,
            'stillness_escalate_secs': 60.0,
            'night_start_hour': 22,
            'night_end_hour': 7,
            'lost_grace_secs': 1.0
        }