"""
告警模块

提供风险分级处理和告警触发功能
"""

from .routes import alerts_bp
from .service import AlertService

__all__ = ['alerts_bp', 'AlertService']
