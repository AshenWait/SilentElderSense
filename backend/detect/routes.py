"""
视频检测接口

接口:
    POST /api/video/upload         - 上传视频文件
    WebSocket /ws/video/<video_id> - 实时返回处理进度和检测结果
"""
import os
import uuid
import asyncio
from datetime import datetime
from quart import Blueprint, jsonify, request, websocket
import cv2
import numpy as np
from core import FallDetector

detect_bp = Blueprint('detect', __name__)

# 视频存储目录
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'videos')
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 全局检测器实例
_detector = None

# 视频处理状态存储
video_status = {}  # video_id -> {status, progress, results, total_frames}


def get_detector() -> FallDetector:
    """获取全局检测器实例"""
    global _detector
    if _detector is None:
        _detector = FallDetector()
    return _detector


@detect_bp.route('/api/video/upload', methods=['POST'])
async def upload_video():
    """
    上传视频文件

    Returns:
        {"video_id": "xxx", "filename": "xxx.mp4"}
    """
    files = await request.files
    if 'video' not in files:
        return jsonify({'error': '未找到视频文件'}), 400

    video_file = files['video']
    if not video_file.filename:
        return jsonify({'error': '文件名为空'}), 400

    # 生成唯一ID
    video_id = str(uuid.uuid4())[:8]

    # 保存文件
    ext = os.path.splitext(video_file.filename)[1] or '.mp4'
    filename = f"{video_id}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    await video_file.save(filepath)

    # 初始化状态
    video_status[video_id] = {
        'status': 'uploaded',
        'progress': 0,
        'total_frames': 0,
        'results': []
    }

    return jsonify({
        'video_id': video_id,
        'filename': video_file.filename
    })


@detect_bp.websocket('/ws/video/<video_id>')
async def process_video_ws(video_id: str):
    """
    WebSocket 视频处理

    发送格式:
    {
        "type": "progress" | "frame" | "complete" | "error",
        "progress": 0-100,        // 进度时
        "frame_id": 1.5,          // 帧结果时
        "persons": [...],         // 帧结果时
        "events": [...],          // 帧结果时
        "total_frames": 100,      // 完成时
        "results": [...]          // 完成时
    }
    """
    # 查找视频文件
    video_path = None
    for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
        candidate = os.path.join(UPLOAD_DIR, f"{video_id}{ext}")
        if os.path.exists(candidate):
            video_path = candidate
            break

    if not video_path:
        await websocket.send_json({'type': 'error', 'message': '视频文件不存在'})
        await websocket.close()
        return

    detector = get_detector()
    session_id = detector.create_session()

    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            await websocket.send_json({'type': 'error', 'message': '无法打开视频文件'})
            await websocket.close()
            return

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        frame_interval = 1  # 处理每一帧

        await websocket.send_json({
            'type': 'info',
            'total_frames': total_frames,
            'fps': fps,
            'frame_interval': frame_interval
        })

        frame_count = 0
        processed_count = 0
        all_results = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # 按间隔采样
            if frame_count % frame_interval == 0:
                # 计算帧时间戳（秒）
                frame_time = frame_count / fps

                # 缩放帧尺寸以提高处理速度
                resized = cv2.resize(frame, (640, 480))

                # 检测
                timestamp = datetime.now().timestamp()
                result = await detector.process_frame_async(session_id, resized, timestamp)

                # 在帧上绘制检测框
                for person in result.frame_result.persons:
                    x1, y1, x2, y2 = [int(x) for x in person.box]
                    # fallen 红色, falling 黄色, 其他绿色
                    color = (0, 0, 255) if person.class_name == 'fallen' else \
                            (0, 255, 255) if person.class_name == 'falling' else (0, 255, 0)

                    cv2.rectangle(resized, (x1, y1), (x2, y2), color, 2)

                    label = f"{person.class_name} {person.confidence * 100:.0f}%"
                    cv2.putText(resized, label, (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                # 编码帧图像为 hex
                _, buffer = cv2.imencode('.jpg', resized, [cv2.IMWRITE_JPEG_QUALITY, 80])
                frame_hex = buffer.tobytes().hex()

                # 构建响应（不再需要 persons 的 box 信息，前端只展示）
                frame_result = {
                    'type': 'frame',
                    'frame_id': round(frame_time, 2),
                    'frame_number': frame_count,
                    'image': frame_hex,
                    'persons': [],
                    'events': []
                }

                for person in result.frame_result.persons:
                    frame_result['persons'].append({
                        'person_id': person.person_id,
                        'class_name': person.class_name,
                        'confidence': round(person.confidence, 3)
                    })

                for event in result.events:
                    frame_result['events'].append({
                        'person_id': event.person_id,
                        'event_type': event.event_type.name,
                        'risk_level': event.risk_level.name,
                        'duration': round(event.duration, 2)
                    })

                all_results.append(frame_result)
                processed_count += 1

                # 发送帧结果
                await websocket.send_json(frame_result)

                # 发送进度
                progress = int((frame_count / total_frames) * 100)
                await websocket.send_json({
                    'type': 'progress',
                    'progress': progress,
                    'processed': processed_count
                })

        cap.release()
        detector.close_session(session_id)

        # 发送完成消息
        await websocket.send_json({
            'type': 'complete',
            'total_frames': frame_count,
            'processed_frames': processed_count,
            'results': all_results
        })

    except Exception as e:
        await websocket.send_json({'type': 'error', 'message': str(e)})
    finally:
        await websocket.close()


# ── 保留原有的实时帧检测接口（供摄像头使用） ──────────────────────────
import struct
import base64


@detect_bp.route('/api/session/create', methods=['POST'])
async def create_session():
    """创建实时检测会话"""
    detector = get_detector()
    video_id = detector.create_session()
    return jsonify({'video_id': video_id})


@detect_bp.route('/api/session/close/<video_id>', methods=['POST'])
async def close_session(video_id: str):
    """关闭实时检测会话"""
    detector = get_detector()
    success = detector.close_session(video_id)
    return jsonify({'success': success})


@detect_bp.websocket('/ws/detect/<video_id>')
async def detect_ws(video_id: str):
    """WebSocket 实时帧检测（摄像头）"""
    detector = get_detector()

    if detector.session_manager.get_session(video_id) is None:
        await websocket.send_json({'error': 'Invalid video_id'})
        await websocket.close()
        return

    while True:
        try:
            data = await websocket.receive()

            if isinstance(data, bytes):
                frame = decode_jpeg(data)
            elif isinstance(data, str):
                frame_bytes = base64.b64decode(data)
                frame = decode_jpeg(frame_bytes)
            else:
                continue

            if frame is None:
                await websocket.send_json({'error': 'Invalid frame data'})
                continue

            timestamp = datetime.now().timestamp()
            result = await detector.process_frame_async(video_id, frame, timestamp)
            response = build_response(result)
            await websocket.send_json(response)

        except Exception as e:
            print(f"WebSocket error: {e}")
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

    for person in result.frame_result.persons:
        response['persons'].append({
            'person_id': person.person_id,
            'class_name': person.class_name,
            'confidence': round(person.confidence, 3),
            'box': [round(x, 1) for x in person.box]
        })

    for event in result.events:
        response['events'].append({
            'person_id': event.person_id,
            'event_type': event.event_type.name,
            'risk_level': event.risk_level.name,
            'duration': round(event.duration, 2)
        })

    return response