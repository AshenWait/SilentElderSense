from quart import Quart, request
from config import Config
from auth import init_db, auth_bp
from detect import detect_bp
from events import events_bp
from alerts import alerts_bp
from detect.BackendMonitoring import monitoring_bp

app = Quart(__name__)
app.config.from_object(Config)

# 允许上传大文件（最大 500MB）
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

# 初始化数据库
init_db(app)

# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(detect_bp)
app.register_blueprint(events_bp)
app.register_blueprint(alerts_bp)
app.register_blueprint(monitoring_bp)

# CORS 中间件（支持预检请求和携带认证的请求）
@app.after_request
async def after_request(response):
    origin = request.headers.get('Origin')
    # 允许的来源
    if origin in ['http://localhost:3000', 'http://127.0.0.1:3000']:
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# 处理 OPTIONS 预检请求
@app.route('/', methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
async def handle_options(path=''):
    origin = request.headers.get('Origin')
    if origin in ['http://localhost:3000', 'http://127.0.0.1:3000']:
        return '', 204, {
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,OPTIONS',
        }
    return '', 204

@app.route('/')
async def index():
    return {'message': 'Backend API is running'}

if __name__ == '__main__':
    app.run(debug=True, port=8000)
