"""
告警 API 端点

接口:
    GET    /api/alerts/config      - 获取告警配置
    PUT    /api/alerts/config      - 更新告警配置
    GET    /api/alerts/history     - 查询告警历史
    POST   /api/alerts/trigger     - 手动触发告警
    POST   /api/alerts/<id>/send   - 重发告警
"""
from datetime import datetime, timedelta
from quart import Blueprint, request, jsonify
from auth.models import get_db
from auth.utils import token_required
from .models import AlertConfig, AlertHistory
from .service import AlertService

alerts_bp = Blueprint('alerts', __name__)

# 全局告警服务实例
_alert_service = None


def get_alert_service() -> AlertService:
    """获取告警服务实例"""
    global _alert_service
    if _alert_service is None:
        _alert_service = AlertService()
    return _alert_service


@alerts_bp.route('/api/alerts/config', methods=['GET'])
@token_required
async def get_config():
    """获取当前用户告警配置"""
    user_id = request.current_user['user_id']
    service = get_alert_service()
    config = service.get_config(user_id)

    if not config:
        # 返回默认配置
        return jsonify({
            'user_id': user_id,
            'high_alert_methods': AlertService.DEFAULT_METHODS['HIGH'],
            'medium_alert_methods': AlertService.DEFAULT_METHODS['MEDIUM'],
            'low_alert_methods': AlertService.DEFAULT_METHODS['LOW'],
            'quiet_hours_start': '22:00',
            'quiet_hours_end': '07:00',
            'bypass_quiet_hours': True
        })

    return jsonify(config.to_dict())


@alerts_bp.route('/api/alerts/config', methods=['PUT'])
@token_required
async def update_config():
    """
    更新告警配置

    请求体:
    {
        "high_alert_methods": ["sms", "email", "app"],
        "medium_alert_methods": ["email", "app"],
        "low_alert_methods": ["app"],
        "emergency_contact": "张三",
        "emergency_phone": "13800138000",
        "email": "user@example.com",
        "quiet_hours_start": "22:00",
        "quiet_hours_end": "07:00",
        "bypass_quiet_hours": true
    }
    """
    user_id = request.current_user['user_id']
    data = await request.get_json()

    # 处理数组字段
    kwargs = {}
    for field in ['high_alert_methods', 'medium_alert_methods', 'low_alert_methods']:
        if field in data:
            kwargs[field] = ','.join(data[field]) if isinstance(data[field], list) else data[field]

    # 处理其他字段
    for field in ['emergency_contact', 'emergency_phone', 'email',
                   'quiet_hours_start', 'quiet_hours_end', 'bypass_quiet_hours']:
        if field in data:
            kwargs[field] = data[field]

    service = get_alert_service()
    config = service.create_or_update_config(user_id, **kwargs)

    return jsonify({
        'message': '配置更新成功',
        'config': config.to_dict()
    })


@alerts_bp.route('/api/alerts/history', methods=['GET'])
@token_required
async def list_history():
    """
    查询告警历史

    查询参数:
        status: 状态（可选）
        risk_level: 风险等级（可选）
        page: 页码
        per_page: 每页数量
    """
    user_id = request.current_user['user_id']
    db = next(get_db())

    query = db.query(AlertHistory).filter(AlertHistory.user_id == user_id)

    status = request.args.get('status')
    if status:
        query = query.filter(AlertHistory.status == status)

    risk_level = request.args.get('risk_level')
    if risk_level:
        query = query.filter(AlertHistory.risk_level == risk_level)

    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    total = query.count()
    alerts = query.order_by(AlertHistory.created_at.desc()) \
        .offset((page - 1) * per_page) \
        .limit(per_page) \
        .all()

    return jsonify({
        'total': total,
        'page': page,
        'per_page': per_page,
        'alerts': [a.to_dict() for a in alerts]
    })


@alerts_bp.route('/api/alerts/trigger', methods=['POST'])
@token_required
async def trigger_alert():
    """
    手动触发告警

    请求体:
    {
        "user_id": 1,
        "event_id": 123,
        "event_type": "FALL",
        "risk_level": "HIGH",
        "duration": 2.5
    }
    """
    data = await request.get_json()

    service = get_alert_service()
    alerts = service.trigger_alert(
        user_id=data['user_id'],
        event_id=data['event_id'],
        event_type=data['event_type'],
        risk_level=data['risk_level'],
        duration=data.get('duration', 0)
    )

    return jsonify({
        'message': f'已触发 {len(alerts)} 条告警',
        'alerts': [a.to_dict() for a in alerts]
    })


@alerts_bp.route('/api/alerts/<int:alert_id>/send', methods=['POST'])
@token_required
async def resend_alert(alert_id: int):
    """重发告警"""
    user_id = request.current_user['user_id']
    db = next(get_db())
    alert = db.query(AlertHistory).filter_by(id=alert_id, user_id=user_id).first()

    if not alert:
        return jsonify({'error': '告警记录不存在'}), 404

    service = get_alert_service()
    service._send_alert(alert)

    db.refresh(alert)
    return jsonify({
        'message': '告警已重发',
        'alert': alert.to_dict()
    })


@alerts_bp.route('/api/alerts/<int:alert_id>/acknowledge', methods=['POST'])
@token_required
async def acknowledge_alert(alert_id: int):
    """确认告警"""
    user_id = request.current_user['user_id']

    service = get_alert_service()
    success = service.acknowledge_alert(alert_id, user_id)

    if not success:
        return jsonify({'error': '告警记录不存在'}), 404

    return jsonify({'message': '告警已确认'})


@alerts_bp.route('/api/alerts/stats', methods=['GET'])
@token_required
async def alert_stats():
    """
    告警统计

    查询参数:
        days: 统计天数（默认7）
    """
    user_id = request.current_user['user_id']
    days = int(request.args.get('days', 7))

    start_date = datetime.now() - timedelta(days=days)

    db = next(get_db())
    query = db.query(AlertHistory).filter(
        AlertHistory.created_at >= start_date,
        AlertHistory.user_id == user_id
    )

    alerts = query.all()

    stats = {
        'total': len(alerts),
        'by_type': {},
        'by_risk': {},
        'by_status': {},
        'sent_count': 0,
        'failed_count': 0
    }

    for alert in alerts:
        # 按告警类型统计
        if alert.alert_type not in stats['by_type']:
            stats['by_type'][alert.alert_type] = 0
        stats['by_type'][alert.alert_type] += 1

        # 按风险等级统计
        if alert.risk_level not in stats['by_risk']:
            stats['by_risk'][alert.risk_level] = 0
        stats['by_risk'][alert.risk_level] += 1

        # 按状态统计
        if alert.status not in stats['by_status']:
            stats['by_status'][alert.status] = 0
        stats['by_status'][alert.status] += 1

        if alert.status == 'sent':
            stats['sent_count'] += 1
        elif alert.status == 'failed':
            stats['failed_count'] += 1

    return jsonify(stats)
