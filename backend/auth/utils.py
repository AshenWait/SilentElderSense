# 工具函数模块
# 用于存放认证相关的辅助函数
import jwt
from datetime import datetime, timedelta
from functools import wraps
from quart import request, jsonify
import os

# JWT配置
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key-change-this-in-production')
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)


def generate_token(user_id, username):
    """生成JWT token"""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + JWT_ACCESS_TOKEN_EXPIRES,
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
    return token


def verify_token(token):
    """验证JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """JWT认证装饰器"""
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': '缺少认证令牌'}), 401

        # 移除 "Bearer " 前缀
        if token.startswith('Bearer '):
            token = token[7:]
        else:
            return jsonify({'error': '无效的令牌格式'}), 401

        payload = verify_token(token)

        if not payload:
            return jsonify({'error': '无效或过期的令牌'}), 401

        # 将用户信息传递给路由函数
        request.current_user = payload

        return await f(*args, **kwargs)

    return decorated_function