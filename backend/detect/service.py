"""
检测配置服务

提供检测配置的获取、更新和运行时参数访问（用户级别）
"""
from auth.models import get_db, SessionLocal
from .models import DetectionConfig


class DetectionConfigService:
    """检测配置服务"""

    def get_config(self, user_id: int) -> DetectionConfig:
        """
        获取用户的检测配置
        如果用户没有配置记录，自动创建默认配置
        """
        db = next(get_db())
        config = db.query(DetectionConfig).filter(DetectionConfig.user_id == user_id).first()

        if config is None:
            # 创建默认配置
            config = DetectionConfig(user_id=user_id, **DetectionConfig.get_defaults())
            db.add(config)
            db.commit()
            db.refresh(config)

        return config

    def update_config(self, user_id: int, **kwargs) -> DetectionConfig:
        """
        更新用户的检测配置

        Args:
            user_id: 用户ID
            **kwargs: 配置字段和值

        Returns:
            更新后的配置对象
        """
        db = next(get_db())
        config = db.query(DetectionConfig).filter(DetectionConfig.user_id == user_id).first()

        if config is None:
            config = DetectionConfig(user_id=user_id, **DetectionConfig.get_defaults())
            db.add(config)

        # 更新字段
        for key, value in kwargs.items():
            if hasattr(config, key) and key not in ['id', 'user_id', 'created_at', 'updated_at']:
                setattr(config, key, value)

        db.commit()
        db.refresh(config)
        return config

    def get_runtime_config(self, user_id: int) -> dict:
        """
        获取用户的运行时配置字典（供 risk_engine 使用）
        """
        config = self.get_config(user_id)
        return {
            'FALLEN_CONFIRM_FRAMES': config.fallen_confirm_frames,
            'FALLEN_ESCALATE_SECS': config.fallen_escalate_secs,
            'STILLNESS_WINDOW_SECS': config.stillness_window_secs,
            'STILLNESS_MOVEMENT_THRESHOLD': config.stillness_movement_threshold,
            'STILLNESS_ESCALATE_SECS': config.stillness_escalate_secs,
            'NIGHT_START_HOUR': config.night_start_hour,
            'NIGHT_END_HOUR': config.night_end_hour,
            'LOST_GRACE_SECS': config.lost_grace_secs
        }


# 全局单例
_detection_config_service = None


def get_detection_config_service() -> DetectionConfigService:
    """获取检测配置服务实例"""
    global _detection_config_service
    if _detection_config_service is None:
        _detection_config_service = DetectionConfigService()
    return _detection_config_service