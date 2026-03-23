"""
事件 API 端点

接口:
    POST /api/events          - 记录事件
    GET  /api/events          - 查询事件列表
    GET  /api/events/<id>     - 获取事件详情
    PUT  /api/events/<id>     - 更新事件状态
"""
import os
from datetime import datetime
from quart import Blueprint, request, jsonify
from auth.models import get_db, Base, engine
from .models import Event

events_bp = Blueprint('events', __name__)


def init_events_table():
    """初始化事件表"""
    Event.metadata.create_all(engine)


@events_bp.route('/api/events', methods=['POST'])
async def create_event():
    """
    记录事件

    请求体:
    {
        "user_id": 1,
        "video_id": "abc123",
        "person_id": 0,
        "event_type": "FALL",
        "risk_level": "HIGH",
        "start_time": "2024-03-23T10:00:00",
        "end_time": "2024-03-23T10:00:02",
        "duration": 2.0,
        "frame_count": 10
    }
    """
    data = await request.get_json()

    db = next(get_db())

    # 解析时间
    start_time = datetime.fromisoformat(data['start_time']) if isinstance(data['start_time'], str) else datetime.fromtimestamp(data['start_time'])
    end_time = datetime.fromisoformat(data['end_time']) if isinstance(data['end_time'], str) else datetime.fromtimestamp(data['end_time'])

    event = Event(
        user_id=data['user_id'],
        video_id=data['video_id'],
        person_id=data['person_id'],
        event_type=data['event_type'],
        risk_level=data['risk_level'],
        start_time=start_time,
        end_time=end_time,
        duration=data['duration'],
        frame_count=data.get('frame_count', 0),
        notes=data.get('notes')
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return jsonify({
        'message': '事件记录成功',
        'event': event.to_dict()
    }), 201


@events_bp.route('/api/events', methods=['GET'])
async def list_events():
    """
    查询事件列表

    查询参数:
        user_id: 用户ID（可选）
        event_type: 事件类型（可选）
        risk_level: 风险等级（可选）
        status: 状态（可选）
        start_date: 开始日期（可选）
        end_date: 结束日期（可选）
        page: 页码（默认1）
        per_page: 每页数量（默认20）
    """
    db = next(get_db())

    # 构建查询
    query = db.query(Event)

    user_id = request.args.get('user_id')
    if user_id:
        query = query.filter(Event.user_id == int(user_id))

    event_type = request.args.get('event_type')
    if event_type:
        query = query.filter(Event.event_type == event_type)

    risk_level = request.args.get('risk_level')
    if risk_level:
        query = query.filter(Event.risk_level == risk_level)

    status = request.args.get('status')
    if status:
        query = query.filter(Event.status == status)

    start_date = request.args.get('start_date')
    if start_date:
        query = query.filter(Event.start_time >= datetime.fromisoformat(start_date))

    end_date = request.args.get('end_date')
    if end_date:
        query = query.filter(Event.end_time <= datetime.fromisoformat(end_date))

    # 分页
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    total = query.count()
    events = query.order_by(Event.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        'total': total,
        'page': page,
        'per_page': per_page,
        'events': [e.to_dict() for e in events]
    })


@events_bp.route('/api/events/<int:event_id>', methods=['GET'])
async def get_event(event_id: int):
    """获取事件详情"""
    db = next(get_db())
    event = db.query(Event).filter_by(id=event_id).first()

    if not event:
        return jsonify({'error': '事件不存在'}), 404

    return jsonify({'event': event.to_dict()})


@events_bp.route('/api/events/<int:event_id>', methods=['PUT'])
async def update_event(event_id: int):
    """
    更新事件状态

    请求体:
    {
        "status": "confirmed",  // pending, confirmed, false_alarm
        "notes": "已确认为误报"
    }
    """
    data = await request.get_json()

    db = next(get_db())
    event = db.query(Event).filter_by(id=event_id).first()

    if not event:
        return jsonify({'error': '事件不存在'}), 404

    if 'status' in data:
        event.status = data['status']
        event.handled_at = datetime.utcnow()

    if 'notes' in data:
        event.notes = data['notes']

    db.commit()
    db.refresh(event)

    return jsonify({
        'message': '更新成功',
        'event': event.to_dict()
    })


@events_bp.route('/api/events/stats', methods=['GET'])
async def event_stats():
    """
    事件统计

    查询参数:
        user_id: 用户ID（可选）
        days: 统计天数（默认7）
    """
    db = next(get_db())

    user_id = request.args.get('user_id')
    days = int(request.args.get('days', 7))

    from datetime import timedelta
    start_date = datetime.utcnow() - timedelta(days=days)

    query = db.query(Event).filter(Event.created_at >= start_date)
    if user_id:
        query = query.filter(Event.user_id == int(user_id))

    events = query.all()

    # 统计
    stats = {
        'total': len(events),
        'by_type': {},
        'by_risk': {},
        'by_status': {}
    }

    for event in events:
        # 按类型统计
        if event.event_type not in stats['by_type']:
            stats['by_type'][event.event_type] = 0
        stats['by_type'][event.event_type] += 1

        # 按风险等级统计
        if event.risk_level not in stats['by_risk']:
            stats['by_risk'][event.risk_level] = 0
        stats['by_risk'][event.risk_level] += 1

        # 按状态统计
        if event.status not in stats['by_status']:
            stats['by_status'][event.status] = 0
        stats['by_status'][event.status] += 1

    return jsonify(stats)
