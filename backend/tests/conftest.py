"""
测试配置文件

提供测试用的 fixtures
"""
import pytest
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope='function')
def test_app():
    """创建测试应用（使用内存数据库）"""
    from quart import Quart
    from auth.models import Base, init_db
    from events.models import Event  # noqa: F401
    from alerts.models import AlertConfig, AlertHistory  # noqa: F401

    # 使用内存数据库
    database_url = 'sqlite:///:memory:'

    # 创建新的 Quart 应用
    app = Quart(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url

    # 初始化数据库
    init_db(app)

    # 注册蓝图
    from auth import auth_bp
    from detect import detect_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(detect_bp)

    # CORS 中间件
    @app.after_request
    async def after_request(response):
        from quart import request
        origin = request.headers.get('Origin')
        if origin in ['http://localhost:3000', 'http://127.0.0.1:3000']:
            response.headers.add('Access-Control-Allow-Origin', origin)
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/')
    async def index():
        return {'message': 'Backend API is running'}

    yield app


@pytest.fixture
def test_client(test_app):
    """测试客户端"""
    return test_app.test_client()


@pytest.fixture
def test_db():
    """测试数据库会话"""
    from auth.models import SessionLocal

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@pytest.fixture
def test_user(test_db):
    """创建测试用户"""
    from auth.models import User

    user = User(
        username='testuser',
        email='test@example.com'
    )
    user.set_password('password123')
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user):
    """生成认证 token"""
    from auth.utils import generate_token
    return generate_token(test_user.id, test_user.username)


@pytest.fixture
def auth_headers(auth_token):
    """认证请求头"""
    return {'Authorization': f'Bearer {auth_token}'}