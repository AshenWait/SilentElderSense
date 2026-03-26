from quart import Blueprint, request, jsonify
from .models import User, get_db
from .utils import generate_token, token_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/register', methods=['POST'])
async def register():
    """注册接口"""
    data = await request.get_json()

    db = next(get_db())

    # 检查用户是否已存在
    existing_user = db.query(User).filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({'error': '用户名已存在'}), 400

    # 创建新用户
    user = User(
        username=data['username'],
        email=data.get('email')
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

    # 查找用户
    user = db.query(User).filter_by(username=data['username']).first()

    # 验证密码
    if user and user.check_password(data['password']):
        token = generate_token(user.id, user.username)
        return jsonify({
            'message': '登录成功',
            'access_token': token,
            'token_type': 'Bearer',
            'user_id': user.id,
            'username': user.username
        }), 200
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
        'username': user['username']
    }), 200