"""
事件数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from auth.models import Base


class Event(Base):
    """异常事件记录"""
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)  # 关联用户
    video_id = Column(String(32), nullable=False, index=True)  # 会话ID

    # 事件信息
    person_id = Column(Integer, nullable=False)  # 触发事件的人员ID
    event_type = Column(String(32), nullable=False)  # FALL, STATIC, NIGHT_ABNORMAL
    risk_level = Column(String(16), nullable=False)  # LOW, MEDIUM, HIGH

    # 时间信息
    start_time = Column(DateTime, nullable=False)  # 开始时间（固定）
    end_time = Column(DateTime, nullable=False)    # 结束时间（实时更新）

    # 附加信息
    frame_count = Column(Integer, default=0)  # 涉及帧数
    snapshot_path = Column(String(256), nullable=True)  # 快照图片路径
    notes = Column(Text, nullable=True)  # 备注

    # 状态
    status = Column(String(16), default='pending')  # pending, confirmed, false_alarm
    handled_at = Column(DateTime, nullable=True)  # 处理时间
    handled_by = Column(Integer, nullable=True)  # 处理人ID

    created_at = Column(DateTime, default=datetime.now)

    @property
    def duration(self):
        """持续时长（秒），实时计算"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'video_id': self.video_id,
            'person_id': self.person_id,
            'event_type': self.event_type,
            'risk_level': self.risk_level,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'frame_count': self.frame_count,
            'snapshot_path': self.snapshot_path,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
