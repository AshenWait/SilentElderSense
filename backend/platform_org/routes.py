"""
平台组织与社区组 API

接口:
    GET    /api/platform/users                  - 列出所有平台用户（管理员）
    PUT    /api/platform/users/<id>             - 编辑平台用户 profile（管理员）
    POST   /api/platform/users/<user_id>/groups - 创建社区组（管理员）
    GET    /api/platform/users/<user_id>/groups - 社区组列表（管理员）
    PUT    /api/platform/groups/<id>            - 更新社区组（管理员）
    DELETE /api/platform/groups/<id>            - 挂起社区组（管理员）
    GET    /api/platform/profile                - 当前平台用户 profile
    GET    /api/platform/communities            - 当前平台用户下社区组列表
    GET    /api/platform/stats                  - 聚合统计（平台用户，强制 DP）
    GET    /api/platform/stats/daily            - 每日趋势（平台用户，强制 DP）
    GET    /api/community/groups                - 可选社区组列表（普通用户）
    PUT    /api/user/community                  - 选择/切换社区组
    GET    /api/user/community                  - 获取当前绑定
"""
from datetime import datetime, timedelta
from quart import Blueprint, request, jsonify, current_app
from auth.models import get_db, User
from auth.utils import token_required, admin_required, role_required
from .models import CommunityGroup
from events.models import Event
from dp_stats.budget_manager import BudgetManager
from dp_stats.cache_service import DPResultCache
from dp_stats.stats_service import StatsService

platform_bp = Blueprint('platform', __name__)

# 差分隐私服务（模块级单例）
_plat_budget = BudgetManager(daily_limit=3.0)
_plat_cache = DPResultCache(ttl_minutes=10)
_plat_stats_svc = StatsService(budget_manager=_plat_budget, cache=_plat_cache)


# ── 管理员：平台用户管理 ──────────────────────────

@platform_bp.route('/api/platform/users', methods=['GET'])
@token_required
@admin_required
async def list_platform_users():
    db = next(get_db())
    users = db.query(User).filter_by(role='platform').order_by(User.created_at.desc()).all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'org_name': u.org_name,
        'org_description': u.org_description,
        'org_contact_name': u.org_contact_name,
        'org_contact_phone': u.org_contact_phone,
        'created_at': u.created_at.isoformat() if u.created_at else None,
    } for u in users])


@platform_bp.route('/api/platform/users/<int:user_id>', methods=['PUT'])
@token_required
@admin_required
async def update_platform_user(user_id: int):
    data = await request.get_json()
    db = next(get_db())
    user = db.query(User).filter_by(id=user_id, role='platform').first()
    if not user:
        return jsonify({'error': '平台用户不存在'}), 404

    for field in ['org_name', 'org_description', 'org_contact_name', 'org_contact_phone', 'email']:
        if field in data:
            setattr(user, field, data[field])
    db.commit()
    return jsonify({'message': '更新成功'})


# ── 管理员：社区组 CRUD ──────────────────────────

@platform_bp.route('/api/platform/users/<int:platform_user_id>/groups', methods=['POST'])
@token_required
@admin_required
async def create_group(platform_user_id: int):
    db = next(get_db())
    user = db.query(User).filter_by(id=platform_user_id, role='platform').first()
    if not user:
        return jsonify({'error': '平台用户不存在'}), 404

    data = await request.get_json()
    group = CommunityGroup(
        platform_user_id=platform_user_id,
        name=data['name'],
        description=data.get('description'),
        address=data.get('address'),
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    return jsonify({'message': '社区组创建成功', 'group': group.to_dict()}), 201


@platform_bp.route('/api/platform/users/<int:platform_user_id>/groups', methods=['GET'])
@token_required
@admin_required
async def list_groups(platform_user_id: int):
    db = next(get_db())
    groups = db.query(CommunityGroup).filter_by(platform_user_id=platform_user_id).order_by(CommunityGroup.created_at.desc()).all()
    return jsonify([g.to_dict() for g in groups])


@platform_bp.route('/api/platform/groups/<int:group_id>', methods=['PUT'])
@token_required
@admin_required
async def update_group(group_id: int):
    data = await request.get_json()
    db = next(get_db())
    group = db.query(CommunityGroup).filter_by(id=group_id).first()
    if not group:
        return jsonify({'error': '社区组不存在'}), 404

    for field in ['name', 'description', 'address', 'status']:
        if field in data:
            setattr(group, field, data[field])
    db.commit()
    db.refresh(group)
    return jsonify({'message': '更新成功', 'group': group.to_dict()})


@platform_bp.route('/api/platform/groups/<int:group_id>', methods=['DELETE'])
@token_required
@admin_required
async def suspend_group(group_id: int):
    db = next(get_db())
    group = db.query(CommunityGroup).filter_by(id=group_id).first()
    if not group:
        return jsonify({'error': '社区组不存在'}), 404
    group.status = 'suspended'
    db.commit()
    return jsonify({'message': '社区组已挂起'})


# ── 平台用户：profile 与社区组 ──────────────────────────

@platform_bp.route('/api/platform/profile', methods=['GET'])
@token_required
@role_required('platform')
async def get_my_profile():
    user_id = request.current_user['user_id']
    db = next(get_db())
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    return jsonify({
        'id': user.id,
        'username': user.username,
        'org_name': user.org_name,
        'org_description': user.org_description,
        'org_contact_name': user.org_contact_name,
        'org_contact_phone': user.org_contact_phone,
    })


@platform_bp.route('/api/platform/communities', methods=['GET'])
@token_required
@role_required('platform')
async def list_my_communities():
    user_id = request.current_user['user_id']
    db = next(get_db())

    groups = db.query(CommunityGroup).filter_by(
        platform_user_id=user_id,
        status='active',
    ).all()

    result = []
    for g in groups:
        member_count = db.query(User).filter_by(community_group_id=g.id).count()
        d = g.to_dict()
        d['member_count'] = member_count
        result.append(d)

    return jsonify(result)


# ── 平台用户：聚合统计 ──────────────────────────

def _get_platform_user_ids(db, platform_user_id: int, community_group_id: int = None):
    """获取平台用户下社区组的用户ID列表，可按单个社区组过滤"""
    query = db.query(CommunityGroup).filter(
        CommunityGroup.platform_user_id == platform_user_id,
        CommunityGroup.status == 'active',
    )
    if community_group_id is not None:
        query = query.filter(CommunityGroup.id == community_group_id)
    group_ids = [g.id for g in query.all()]
    if not group_ids:
        return []
    return [u.id for u in db.query(User).filter(
        User.community_group_id.in_(group_ids),
    ).all()]


@platform_bp.route('/api/platform/stats', methods=['GET'])
@token_required
@role_required('platform')
async def platform_stats():
    user_id = request.current_user['user_id']
    days = int(request.args.get('days', 7))
    community_group_id = request.args.get('community_group_id', type=int)

    db = next(get_db())
    member_ids = _get_platform_user_ids(db, user_id, community_group_id)

    now = datetime.now()
    start_date = now - timedelta(days=days)
    prev_start = start_date - timedelta(days=days)

    current_events = db.query(Event).filter(
        Event.created_at >= start_date,
        Event.user_id.in_(member_ids),
    ).all() if member_ids else []

    prev_events = db.query(Event).filter(
        Event.created_at >= prev_start,
        Event.created_at < start_date,
        Event.user_id.in_(member_ids),
    ).all() if member_ids else []

    stats = {'total': len(current_events), 'by_type': {}, 'by_risk': {}, 'by_status': {}}
    prev_stats = {'total': len(prev_events), 'by_type': {}, 'by_risk': {}, 'by_status': {}}

    for e in current_events:
        stats['by_type'][e.event_type] = stats['by_type'].get(e.event_type, 0) + 1
        stats['by_risk'][e.risk_level] = stats['by_risk'].get(e.risk_level, 0) + 1
        stats['by_status'][e.status] = stats['by_status'].get(e.status, 0) + 1

    for e in prev_events:
        prev_stats['by_type'][e.event_type] = prev_stats['by_type'].get(e.event_type, 0) + 1
        prev_stats['by_risk'][e.risk_level] = prev_stats['by_risk'].get(e.risk_level, 0) + 1
        prev_stats['by_status'][e.status] = prev_stats['by_status'].get(e.status, 0) + 1

    # 强制 DP
    budget_enabled = current_app.config.get('DP_BUDGET_ENABLED', True)
    epsilon = current_app.config.get('DP_DEFAULT_EPSILON', 0.8)

    query_key = f"stats_{days}days_group_{community_group_id or 'all'}"
    try:
        private_result = _plat_stats_svc.get_private_stats(
            user_id=f"platform_{user_id}",
            query_key=query_key,
            stats={'total': stats['total'], 'by_type': stats['by_type'], 'by_risk': stats['by_risk'], 'by_status': stats['by_status']},
            epsilon=epsilon,
            now=now,
            check_budget=budget_enabled,
        )
        noisy = private_result['value']
        stats['total'] = noisy['total']
        stats['by_type'] = noisy['by_type']
        stats['by_risk'] = noisy['by_risk']
        stats['by_status'] = noisy['by_status']
        stats['display'] = private_result.get('display', {})
        stats['privacy_notice'] = f'统计结果已采用差分隐私技术处理（ε={epsilon}），数值与原始数据可能存在轻微差异'
    except ValueError as e:
        return jsonify({'error': '隐私预算已用完，请稍后再试', 'detail': str(e)}), 429

    def calc_trend(cur, prev):
        return round((cur - prev) / prev * 100, 1) if prev else None

    stats['trends'] = {
        'total': calc_trend(stats['total'], prev_stats['total']),
        'by_type': {k: calc_trend(stats['by_type'].get(k, 0), prev_stats['by_type'].get(k, 0)) for k in stats['by_type']},
        'by_risk': {k: calc_trend(stats['by_risk'].get(k, 0), prev_stats['by_risk'].get(k, 0)) for k in stats['by_risk']},
    }
    stats['member_count'] = len(member_ids)
    return jsonify(stats)


@platform_bp.route('/api/platform/stats/daily', methods=['GET'])
@token_required
@role_required('platform')
async def platform_daily_trend():
    user_id = request.current_user['user_id']
    days = int(request.args.get('days', 7))
    community_group_id = request.args.get('community_group_id', type=int)

    db = next(get_db())
    member_ids = _get_platform_user_ids(db, user_id, community_group_id)
    now = datetime.now()
    start_date = (now - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)

    events = db.query(Event).filter(
        Event.start_time >= start_date,
        Event.user_id.in_(member_ids),
    ).all() if member_ids else []

    event_types = ['FALLEN', 'STILLNESS', 'NIGHT_ABNORMAL']
    dates = []
    daily_data = {}
    for i in range(days):
        date = (now - timedelta(days=days - 1 - i)).strftime('%m-%d')
        dates.append(date)
        daily_data[date] = {t: 0 for t in event_types}

    for e in events:
        date_key = e.start_time.strftime('%m-%d')
        if date_key in daily_data and e.event_type in event_types:
            daily_data[date_key][e.event_type] += 1

    budget_enabled = current_app.config.get('DP_BUDGET_ENABLED', True)
    epsilon = current_app.config.get('DP_DEFAULT_EPSILON', 0.8)

    query_key = f"daily_stats_{days}days_group_{community_group_id or 'all'}"
    try:
        private_result = _plat_stats_svc.get_private_daily_trend(
            user_id=f"platform_{user_id}",
            query_key=query_key,
            daily_data=daily_data,
            epsilon=epsilon,
            now=now,
            check_budget=budget_enabled,
        )
        noisy_daily_data = private_result['value']
    except ValueError as e:
        return jsonify({'error': '隐私预算已用完，请稍后再试', 'detail': str(e)}), 429

    return jsonify({
        'dates': dates,
        'by_type': {t: [noisy_daily_data[d].get(t, 0) for d in dates] for t in event_types},
    })


# ── 普通用户：社区组选择 ──────────────────────────

@platform_bp.route('/api/community/groups', methods=['GET'])
@token_required
@role_required('user', 'admin')
async def available_groups():
    """获取可选社区组列表"""
    db = next(get_db())
    search = request.args.get('search', '').strip()

    query = db.query(CommunityGroup).filter_by(status='active')
    if search:
        query = query.filter(CommunityGroup.name.contains(search))

    groups = query.order_by(CommunityGroup.name).all()

    result = []
    for g in groups:
        # 通过 platform_user_id 找到平台用户的 org_name
        platform_user = db.query(User).filter_by(id=g.platform_user_id, role='platform').first()
        member_count = db.query(User).filter_by(community_group_id=g.id).count()
        d = g.to_dict()
        d['org_name'] = platform_user.org_name if platform_user else ''
        d['member_count'] = member_count
        result.append(d)

    return jsonify(result)


@platform_bp.route('/api/user/community', methods=['GET'])
@token_required
@role_required('user', 'admin')
async def get_user_community():
    user_id = request.current_user['user_id']
    db = next(get_db())
    user = db.query(User).filter_by(id=user_id).first()

    if not user or not user.community_group_id:
        return jsonify({'community': None})

    group = db.query(CommunityGroup).filter_by(id=user.community_group_id).first()
    if not group:
        return jsonify({'community': None})

    platform_user = db.query(User).filter_by(id=group.platform_user_id, role='platform').first()
    d = group.to_dict()
    d['org_name'] = platform_user.org_name if platform_user else ''
    return jsonify({'community': d})


@platform_bp.route('/api/user/community', methods=['PUT'])
@token_required
@role_required('user', 'admin')
async def set_user_community():
    user_id = request.current_user['user_id']
    data = await request.get_json()
    group_id = data.get('community_group_id')

    db = next(get_db())
    user = db.query(User).filter_by(id=user_id).first()

    if group_id is None:
        user.community_group_id = None
        db.commit()
        return jsonify({'message': '已取消社区组绑定', 'community': None})

    group = db.query(CommunityGroup).filter_by(id=group_id, status='active').first()
    if not group:
        return jsonify({'error': '社区组不存在或已停用'}), 404

    user.community_group_id = group_id
    db.commit()
    return jsonify({'message': '社区组已更新', 'community': group.to_dict()})
