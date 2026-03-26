"""
摄像头监控路由

提供摄像头控制和视频流推送接口
"""
import asyncio
import json
from quart import Blueprint, jsonify, request, websocket
from .camera import camera_service

monitoring_bp = Blueprint('monitoring', __name__)


@monitoring_bp.route('/api/camera/list', methods=['GET'])
async def list_cameras():
    """
    获取可用摄像头列表

    Returns:
        {"cameras": [{"id": 0, "name": "Camera 0", "width": 640, "height": 480}]}
    """
    cameras = camera_service.list_cameras()
    return jsonify({'cameras': cameras})


@monitoring_bp.route('/api/camera/start', methods=['POST'])
async def start_camera():
    """
    启动摄像头

    Request Body:
        {"camera_id": 0, "width": 640, "height": 480}

    Returns:
        {"success": true, "status": {...}}
    """
    data = await request.get_json() or {}
    camera_id = data.get('camera_id', 0)
    width = data.get('width', 640)
    height = data.get('height', 480)

    success = camera_service.start_capture(camera_id, width, height)

    return jsonify({
        'success': success,
        'status': camera_service.status
    })


@monitoring_bp.route('/api/camera/stop', methods=['POST'])
async def stop_camera():
    """
    停止摄像头

    Returns:
        {"success": true}
    """
    success = camera_service.stop_capture()
    return jsonify({'success': success})


@monitoring_bp.route('/api/camera/status', methods=['GET'])
async def get_camera_status():
    """
    获取摄像头状态

    Returns:
        {"status": {...}}
    """
    return jsonify({'status': camera_service.status})


@monitoring_bp.route('/api/camera/frame', methods=['GET'])
async def get_frame():
    """
    获取当前帧 (Base64)

    Returns:
        {"frame": "base64_encoded_jpeg"}
    """
    frame = camera_service.get_frame_base64()
    if frame:
        return jsonify({'frame': frame})
    return jsonify({'error': 'No frame available'}), 404


@monitoring_bp.route('/api/camera/stream')
async def mjpeg_stream():
    """
    MJPEG 视频流 (用于浏览器 <img> 标签)

    Usage:
        <img src="/api/camera/stream" />
    """
    from quart import Response

    def generate():
        for frame in camera_service.gen_frames():
            yield frame

    return Response(
        generate(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@monitoring_bp.websocket('/ws/camera')
async def camera_ws():
    """
    WebSocket 实时视频流

    前端连接后持续接收视频帧

    消息格式:
        {"type": "frame", "data": "base64_encoded_jpeg"}
        {"type": "status", "data": {...}}
    """
    import base64

    # 发送初始状态
    await websocket.send_json({
        'type': 'status',
        'data': camera_service.status
    })

    # 帧回调队列
    frame_queue = asyncio.Queue()

    def on_frame(frame_data: bytes):
        """帧回调函数"""
        try:
            frame_base64 = base64.b64encode(frame_data).decode('utf-8')
            # 将帧放入队列（非阻塞）
            try:
                frame_queue.put_nowait(frame_base64)
            except asyncio.QueueFull:
                pass
        except Exception as e:
            print(f"Frame callback error: {e}")

    # 订阅帧更新
    camera_service.subscribe(on_frame)

    try:
        while True:
            # 接收客户端消息（可选）
            try:
                msg = await asyncio.wait_for(websocket.receive(), timeout=0.1)
                # 处理客户端消息
                if msg:
                    try:
                        data = json.loads(msg)
                        if data.get('type') == 'ping':
                            await websocket.send_json({'type': 'pong'})
                    except json.JSONDecodeError:
                        pass
            except asyncio.TimeoutError:
                pass

            # 发送帧
            try:
                frame_base64 = frame_queue.get_nowait()
                await websocket.send_json({
                    'type': 'frame',
                    'data': frame_base64
                })
            except asyncio.QueueEmpty:
                pass

            # 控制帧率
            await asyncio.sleep(1.0 / 30)

    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # 取消订阅
        camera_service.unsubscribe(on_frame)