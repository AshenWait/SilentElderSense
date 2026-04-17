from quart import Blueprint, request, jsonify
from .models import User, get_db
from .utils import generate_token, token_required, admin_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/register', methods=['POST'])
async def register():
    """注册接口"""
    data = await request.get_json()

    db = next(get_db())

    existing_user = db.query(User).filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({'error': '用户名已存在'}), 400

    user = User(
        username=data['username'],
        email=data.get('email'),
        role='user'
    )
    user.set_password(data['password'])

    db.add(user)
    db.commit()

    return jsonify({'message': '注册成功'}), 201


@auth_bp.route('/api/login', methods=['POST'])
async def login():
    """登录接口"""
    data = await request.get_json()

    db = next(get_db())

    user = db.query(User).filter_by(username=data['username']).first()

    if user and user.check_password(data['password']):
        token = generate_token(user.id, user.username, user.role)
        result = {
            'message': '登录成功',
            'access_token': token,
            'token_type': 'Bearer',
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'community_group_id': user.community_group_id,
        }
        if user.role == 'platform':
            result['org_name'] = user.org_name
            result['org_description'] = user.org_description
        return jsonify(result), 200
    else:
        return jsonify({'error': '用户名或密码错误'}), 401


@auth_bp.route('/api/protected', methods=['GET'])
@token_required
async def protected_route():
    """受保护的路由示例"""
    user = request.current_user
    return jsonify({
        'message': '这是一个受保护的路由',
        'user_id': user['user_id'],
        'username': user['username'],
        'role': user.get('role', 'user')
    }), 200


@auth_bp.route('/api/users/platform', methods=['POST'])
@token_required
@admin_required
async def create_platform_user():
    """管理员创建平台用户"""
    data = await request.get_json()
    db = next(get_db())

    existing = db.query(User).filter_by(username=data['username']).first()
    if existing:
        return jsonify({'error': '用户名已存在'}), 400

    user = User(
        username=data['username'],
        email=data.get('email'),
        role='platform',
        org_name=data.get('org_name'),
        org_description=data.get('org_description'),
        org_contact_name=data.get('org_contact_name'),
        org_contact_phone=data.get('org_contact_phone'),
    )
    user.set_password(data['password'])

    db.add(user)
    db.commit()

    return jsonify({'message': '平台用户创建成功', 'username': user.username, 'role': user.role}), 201


@auth_bp.route('/api/users', methods=['GET'])
@token_required
@admin_required
async def list_users():
    """管理员获取用户列表"""
    db = next(get_db())
    users = db.query(User).order_by(User.created_at.desc()).all()

    result = []
    for u in users:
        community_group_name = None
        if u.community_group_id:
            from platform_org.models import CommunityGroup
            g = db.query(CommunityGroup).filter_by(id=u.community_group_id).first()
            community_group_name = g.name if g else None

        result.append({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'role': u.role,
            'community_group_id': u.community_group_id,
            'community_group_name': community_group_name,
            'org_name': u.org_name,
            'org_contact_name': u.org_contact_name,
            'org_contact_phone': u.org_contact_phone,
            'created_at': u.created_at.isoformat() if u.created_at else None,
        })

    return jsonify(result)


@auth_bp.route('/api/admin/reset-password', methods=['POST'])
@token_required
@admin_required
async def reset_password():
    """管理员重设用户密码"""
    data = await request.get_json()
    user_id = data.get('user_id')
    new_password = data.get('new_password')

    if not user_id or not new_password:
        return jsonify({'error': '缺少 user_id 或 new_password'}), 400

    if len(new_password) < 4:
        return jsonify({'error': '密码长度至少4位'}), 400

    db = next(get_db())
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    user.set_password(new_password)
    db.commit()
    return jsonify({'message': f'用户 {user.username} 密码已重置'})


# ── 管理员：普通用户管理 ──────────────────────────

@auth_bp.route('/api/admin/users', methods=['POST'])
@token_required
@admin_required
async def admin_create_user():
    """管理员创建普通用户，可指定 community_group_id"""
    data = await request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    if len(password) < 4:
        return jsonify({'error': '密码长度至少4位'}), 400

    db = next(get_db())

    existing = db.query(User).filter_by(username=username).first()
    if existing:
        return jsonify({'error': '用户名已存在'}), 400

    community_group_id = data.get('community_group_id')
    if community_group_id:
        from platform_org.models import CommunityGroup
        group = db.query(CommunityGroup).filter_by(id=community_group_id, status='active').first()
        if not group:
            return jsonify({'error': '社区组不存在或已停用'}), 400

    user = User(
        username=username,
        email=data.get('email'),
        role='user',
        community_group_id=community_group_id,
    )
    user.set_password(password)

    db.add(user)
    db.commit()

    return jsonify({
        'message': '用户创建成功',
        'user_id': user.id,
        'username': user.username,
    }), 201


@auth_bp.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@token_required
@admin_required
async def admin_update_user(user_id: int):
    """管理员更新用户信息"""
    data = await request.get_json()
    db = next(get_db())

    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    if 'email' in data:
        user.email = data['email']

    if user.role == 'user' and 'community_group_id' in data:
        community_group_id = data['community_group_id']
        if community_group_id:
            from platform_org.models import CommunityGroup
            group = db.query(CommunityGroup).filter_by(id=community_group_id, status='active').first()
            if not group:
                return jsonify({'error': '社区组不存在或已停用'}), 400
        user.community_group_id = community_group_id

    db.commit()
    return jsonify({'message': '更新成功'})
