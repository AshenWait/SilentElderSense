"""
WebSocket 检测端点

接口:
    POST /api/session/create     - 创建检测会话
    POST /api/session/close/<video_id> - 关闭会话
    WebSocket /ws/detect/<video_id>    - 实时帧检测
"""
import time
import cv2
import numpy as np
from quart import Blueprint, jsonify, websocket
from core import FallDetector

detect_bp = Blueprint('detect', __name__)

# 全局检测器实例（延迟初始化）
_detector = None


def get_detector() -> FallDetector:
    """获取全局检测器实例"""
    global _detector
    if _detector is None:
        _detector = FallDetector()
    return _detector


@detect_bp.route('/api/session/create', methods=['POST'])
async def create_session():
    """
    创建检测会话

    Returns:
        {"video_id": "xxx"}
    """
    detector = get_detector()
    video_id = detector.create_session()
    return jsonify({'video_id': video_id})


@detect_bp.route('/api/session/close/<video_id>', methods=['POST'])
async def close_session(video_id: str):
    """
    关闭检测会话

    Args:
        video_id: 会话ID

    Returns:
        {"success": true/false}
    """
    detector = get_detector()
    success = detector.close_session(video_id)
    return jsonify({'success': success})


@detect_bp.websocket('/ws/detect/<video_id>')
async def detect_ws(video_id: str):
    """
    WebSocket 实时帧检测

    前端发送: JPEG 字节流
    后端返回: JSON 检测结果

    返回格式:
    {
        "detected": true,
        "persons": [
            {
                "person_id": 0,
                "class_name": "normal",
                "confidence": 0.95,
                "box": [x1, y1, x2, y2]
            }
        ],
        "events": [
            {
                "person_id": 0,
                "event_type": "FALL",
                "risk_level": "HIGH",
                "duration": 1.5
            }
        ]
    }
    """
    detector = get_detector()

    # 验证会话存在
    if detector.session_manager.get_session(video_id) is None:
        await websocket.send_json({'error': 'Invalid video_id'})
        await websocket.close()
        return

    while True:
        try:
            # 接收 JPEG 帧数据
            data = await websocket.receive()

            # 解码图像
            if isinstance(data, bytes):
                frame = decode_jpeg(data)
            elif isinstance(data, str):
                # 如果是 base64 编码的字符串
                import base64
                frame_bytes = base64.b64decode(data)
                frame = decode_jpeg(frame_bytes)
            else:
                continue

            if frame is None:
                await websocket.send_json({'error': 'Invalid frame data'})
                continue

            # 处理帧
            timestamp = time.time()
            result = await detector.process_frame_async(video_id, frame, timestamp)

            # 构建响应
            response = build_response(result)
            await websocket.send_json(response)

        except Exception as e:
            # 连接关闭或其他错误
            break


def decode_jpeg(data: bytes) -> np.ndarray:
    """解码 JPEG 字节流为 BGR 图像"""
    try:
        arr = np.frombuffer(data, dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return frame
    except Exception:
        return None


def build_response(result) -> dict:
    """构建 JSON 响应"""
    response = {
        'detected': result.frame_result.detected,
        'persons': [],
        'events': []
    }

    # 添加人员检测结果
    for person in result.frame_result.persons:
        response['persons'].append({
            'person_id': person.person_id,
            'class_name': person.class_name,
            'confidence': round(person.confidence, 3),
            'box': [round(x, 1) for x in person.box]
        })

    # 添加事件
    for event in result.events:
        response['events'].append({
            'person_id': event.person_id,
            'event_type': event.event_type.name,
            'risk_level': event.risk_level.name,
            'duration': round(event.duration, 2)
        })

    return response
