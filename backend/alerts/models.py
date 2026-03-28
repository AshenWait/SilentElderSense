"""
告警数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Boolean
from datetime import datetime
from auth.models import Base
from enum import Enum


class AlertLevel(Enum):
    """告警级别 - 对应三级响应"""
    LEVEL_1 = 1  # 一级：本地提醒
    LEVEL_2 = 2  # 二级：管理端高亮告警
    LEVEL_3 = 3  # 三级：紧急事件卡片 + 通知流程


class AlertConfig(Base):
    """告警配置 - 按用户和风险等级配置告警方式"""
    __tablename__ = 'alert_configs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)

    # 风险等级对应的告警方式
    high_alert_methods = Column(String(128), default='sms,email,app')  # 高风险
    medium_alert_methods = Column(String(128), default='email,app')    # 中风险
    low_alert_methods = Column(String(128), default='app')             # 低风险

    # 联系人信息
    emergency_contact = Column(String(64), nullable=True)    # 紧急联系人
    emergency_phone = Column(String(20), nullable=True)      # 紧急联系电话
    email = Column(String(120), nullable=True)               # 邮箱

    # 告警时间限制
    quiet_hours_start = Column(String(8), default='22:00')   # 免打扰开始
    quiet_hours_end = Column(String(8), default='07:00')     # 免打扰结束

    # 高风险事件是否忽略免打扰
    bypass_quiet_hours = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'high_alert_methods': self.high_alert_methods.split(',') if self.high_alert_methods else [],
            'medium_alert_methods': self.medium_alert_methods.split(',') if self.medium_alert_methods else [],
            'low_alert_methods': self.low_alert_methods.split(',') if self.low_alert_methods else [],
            'emergency_contact': self.emergency_contact,
            'emergency_phone': self.emergency_phone,
            'email': self.email,
            'quiet_hours_start': self.quiet_hours_start,
            'quiet_hours_end': self.quiet_hours_end,
            'bypass_quiet_hours': self.bypass_quiet_hours
        }


class AlertHistory(Base):
    """告警历史记录"""
    __tablename__ = 'alert_histories'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=True)

    # 告警级别（三级响应）
    alert_level = Column(Integer, default=1)  # 1=本地提醒, 2=管理端告警, 3=紧急通知

    # 告警信息
    alert_type = Column(String(32), nullable=False)   # sms, email, app, push, local
    risk_level = Column(String(16), nullable=False)   # HIGH, MEDIUM, LOW
    event_type = Column(String(32), nullable=False)   # FALL, STATIC, NIGHT_ABNORMAL

    # 告警内容
    title = Column(String(128), nullable=False)
    message = Column(Text, nullable=False)

    # 发送状态
    status = Column(String(16), default='pending')    # pending, sent, failed, acknowledged
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)  # 确认时间
    acknowledged_by = Column(Integer, nullable=True)   # 确认人

    # 接收者信息
    recipient = Column(String(128), nullable=True)    # 手机号/邮箱

    created_at = Column(DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'event_id': self.event_id,
            'alert_level': self.alert_level,
            'alert_type': self.alert_type,
            'risk_level': self.risk_level,
            'event_type': self.event_type,
            'title': self.title,
            'message': self.message,
            'status': self.status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'recipient': self.recipient,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
