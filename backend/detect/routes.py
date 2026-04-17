"""
视频检测接口

接口:
    POST /api/video/upload         - 上传视频文件
    WebSocket /ws/video/<video_id> - 实时返回处理进度和检测结果
"""
import os
import time
import uuid
import asyncio
import base64
import struct
import json
from quart import Blueprint, jsonify, request, websocket
import cv2
import numpy as np
from secure_core import SecureCore
from secure_core.risk_engine import RISK_COLORS_BGR, RISK_REASON_LABELS
from auth.utils import token_required, role_required
from auth.models import get_db
from events.models import Event
from alerts.service import AlertService
from datetime import datetime

detect_bp = Blueprint('detect', __name__)

# 视频存储目录
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'videos')
SNAPSHOT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'snapshots')
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

# 全局 SecureCore 实例
_secure_core = None

# 视频处理状态存储
video_status = {}  # video_id -> {status, progress, results, total_frames}


def get_secure_core() -> SecureCore:
    """获取全局可信核心实例"""
    global _secure_core
    if _secure_core is None:
        _secure_core = SecureCore()
        _secure_core.initialize()
    return _secure_core


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

    查询参数:
        persist: 是否持久化事件到数据库
        user_id: 用户ID（持久化模式下必需）

    发送格式:
    {
        "type": "progress" | "frame" | "complete" | "error",
        "progress": 0-100,        // 进度时
        "frame_id": 1.5,          // 帧结果时
        "persons": [...],         // 帧结果时，每人含 risk_level/risk_reason/box
        "total_frames": 100,      // 完成时
        "results": [...]          // 完成时
    }
    """
    # 获取查询参数
    query_string = websocket.query_string or b''
    from urllib.parse import parse_qs
    params = parse_qs(query_string.decode())
    persist = params.get('persist', ['false'])[0].lower() == 'true'
    user_id = int(params.get('user_id', [0])[0]) if persist else 0

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

    core = get_secure_core()
    session_info = core.start_session(is_live=persist, user_id=user_id if persist else None)
    session_id = session_info["session_id"]

    # 持久化模式下的活跃事件跟踪
    active_events = {} if persist else None
    last_db_update = time.time() if persist else 0

    async def update_active_events_end_time():
        """每秒更新活跃事件的 end_time（持久化模式）"""
        nonlocal last_db_update
        if not persist or not active_events:
            return
        now = time.time()
        if now - last_db_update < 1.0:
            return
        from auth.models import SessionLocal
        db = SessionLocal()
        try:
            now_dt = datetime.fromtimestamp(now)
            for (person_id, event_type) in active_events.keys():
                db.query(Event).filter(
                    Event.video_id == video_id,
                    Event.person_id == person_id,
                    Event.event_type == event_type,
                ).update({'end_time': now_dt})
            db.commit()
            last_db_update = now
        except Exception as e:
            print(f"[ERROR] 更新 end_time 失败: {e}")
            db.rollback()
        finally:
            db.close()

    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            await websocket.send_json({'type': 'error', 'message': '无法打开视频文件'})
            await websocket.close()
            return

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        frame_interval = 1

        await websocket.send_json({
            'type': 'info',
            'total_frames': total_frames,
            'fps': fps,
            'frame_interval': frame_interval,
            'persist': persist
        })

        frame_count = 0
        processed_count = 0
        all_results = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            if frame_count % frame_interval == 0:
                frame_time = frame_count / fps
                resized = cv2.resize(frame, (640, 480))

                # 通过 SecureCore 处理帧
                core_result = await core.process_frame_async(session_id, resized)
                processed = core_result.processed_frame  # 已模糊的帧
                now = time.time()

                risk_results = core_result.risk_results
                event_changes = core_result.event_changes

                # 持久化事件变更（持久化模式）
                if persist and event_changes and user_id:
                    from auth.models import SessionLocal
                    db = SessionLocal()
                    try:
                        for ch in event_changes:
                            _persist_event_change(db, ch, video_id, user_id,
                                                  core.core_hash, core.model_version,
                                                  snapshot_frame=processed)
                            key = (ch.person_id, ch.event_type)
                            if ch.change_type == 'ended':
                                active_events.pop(key, None)
                            else:
                                active_events[key] = now
                        db.commit()
                    except Exception as e:
                        print(f"[ERROR] 事件持久化失败: {e}")
                        db.rollback()
                    finally:
                        db.close()
                    await update_active_events_end_time()

                # 在已模糊的帧上绘制风险框
                for risk in risk_results:
                    x1, y1, x2, y2 = [int(x) for x in risk.box]
                    color = RISK_COLORS_BGR.get(risk.risk_level, (0, 255, 0))
                    cv2.rectangle(processed, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(processed, risk.risk_level, (x1, y1 - 8),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                # 编码帧图像
                _, buffer = cv2.imencode('.jpg', processed, [cv2.IMWRITE_JPEG_QUALITY, 80])
                frame_hex = buffer.tobytes().hex()

                frame_result = {
                    'type': 'frame',
                    'frame_id': round(frame_time, 2),
                    'frame_number': frame_count,
                    'image': frame_hex,
                    'persons': [
                        {
                            'person_id': r.person_id,
                            'box': [round(x, 1) for x in r.box],
                            'risk_level': r.risk_level,
                            'risk_reason': r.risk_reason,
                        }
                        for r in risk_results
                    ],
                }

                all_results.append(frame_result)
                processed_count += 1

                await websocket.send_json(frame_result)

                progress = int((frame_count / total_frames) * 100)
                await websocket.send_json({
                    'type': 'progress',
                    'progress': progress,
                    'processed': processed_count
                })

        cap.release()

        # 持久化模式下关闭会话时处理未结束的事件
        ended_changes = core.close_session(session_id, now=time.time()) if persist else None
        if persist and ended_changes and user_id:
            from auth.models import SessionLocal
            db = SessionLocal()
            try:
                for ch in ended_changes:
                    _persist_event_change(db, ch, video_id, user_id,
                                          core.core_hash, core.model_version)
                db.commit()
            except Exception as e:
                print(f"[ERROR] 事件持久化失败: {e}")
                db.rollback()
            finally:
                db.close()
        else:
            core.close_session(session_id)

        await websocket.send_json({
            'type': 'complete',
            'total_frames': frame_count,
            'processed_frames': processed_count,
            'results': all_results
        })

    except Exception as e:
        await websocket.send_json({'type': 'error', 'message': str(e)})
    finally:
        await websocket.close(1000)  # 1000 = 正常关闭


# ── 实时帧检测接口（供摄像头使用） ──────────────────────────

@detect_bp.route('/api/session/create', methods=['POST'])
@token_required
@role_required('user', 'admin')
async def create_session():
    """创建实时检测会话（需要登录）"""
    user_id = request.current_user['user_id']

    core = get_secure_core()
    session_info = core.start_session(is_live=True, user_id=user_id)
    video_id = session_info["session_id"]

    return jsonify({'video_id': video_id, 'user_id': user_id})


@detect_bp.route('/api/session/close/<video_id>', methods=['POST'])
@token_required
@role_required('user', 'admin')
async def close_session(video_id: str):
    """关闭实时检测会话"""
    user_id = request.current_user['user_id']
    core = get_secure_core()
    now = time.time()
    ended_changes = core.close_session(video_id, now=now)

    if ended_changes:
        from auth.models import SessionLocal
        db = SessionLocal()
        try:
            for ch in ended_changes:
                _persist_event_change(db, ch, video_id, user_id,
                                      core.core_hash, core.model_version)
            db.commit()
        except Exception as e:
            print(f"[ERROR] 事件持久化失败: {e}")
            db.rollback()
        finally:
            db.close()

        # 告警触发（在事务提交后单独处理）
        for ch in ended_changes:
            if ch.change_type == 'ended' and ch.risk_level in ['HIGH', 'MEDIUM']:
                try:
                    alert_service = AlertService()
                    # duration 从 start_time 和 end_time 计算
                    duration = ch.end_ts - ch.start_ts if ch.end_ts and ch.start_ts else 0
                    alert_service.trigger_alert(
                        user_id=user_id,
                        event_id=None,
                        event_type=ch.event_type,
                        risk_level=ch.risk_level,
                        duration=duration
                    )

                    # 跌倒高风险持续超过40秒 → 模拟拨打120
                    if ch.risk_level == 'HIGH' and ch.event_type == 'FALLEN' and duration >= 40:
                        alert_service.simulate_call_120(user_id, duration=duration)
                except Exception as e:
                    print(f"[WARN] 告警触发失败: {e}")

    return jsonify({'success': True})


@detect_bp.websocket('/ws/detect/<video_id>')
async def detect_ws(video_id: str):
    """WebSocket 实时帧检测（摄像头）- 跳帧策略，跳过队列中的旧帧"""
    core = get_secure_core()

    if core.session_manager.get_session(video_id) is None:
        await websocket.send_json({'type': 'error', 'message': 'Invalid video_id'})
        await websocket.close()
        return

    processed_count = 0
    skipped_count = 0

    # 活跃事件跟踪：{(person_id, event_type): last_update_time}
    active_events = {}
    last_db_update = time.time()

    async def update_active_events_end_time():
        """每秒更新活跃事件的 end_time"""
        nonlocal last_db_update
        now = time.time()

        # 每秒更新一次
        if now - last_db_update < 1.0:
            return

        if not active_events:
            return

        user_id = core.get_user_id(video_id)
        if not user_id:
            return

        from auth.models import SessionLocal
        db = SessionLocal()
        try:
            now_dt = datetime.fromtimestamp(now)
            for (person_id, event_type) in active_events.keys():
                db.query(Event).filter(
                    Event.video_id == video_id,
                    Event.person_id == person_id,
                    Event.event_type == event_type,
                ).update({'end_time': now_dt})
            db.commit()
            last_db_update = now
        except Exception as e:
            print(f"[ERROR] 更新 end_time 失败: {e}")
            db.rollback()
        finally:
            db.close()

    async def process_frame(frame, frame_ts):
        """处理单个帧"""
        nonlocal processed_count

        resized = cv2.resize(frame, (640, 480))

        # 通过 SecureCore 处理
        core_result = await core.process_frame_async(video_id, resized)
        processed = core_result.processed_frame  # 已模糊的帧
        now = time.time()

        risk_results = core_result.risk_results
        event_changes = core_result.event_changes

        # 持久化事件变更
        if event_changes:
            user_id = core.get_user_id(video_id)
            if user_id:
                from auth.models import SessionLocal
                db = SessionLocal()
                try:
                    for ch in event_changes:
                        _persist_event_change(db, ch, video_id, user_id,
                                          core.core_hash, core.model_version,
                                          snapshot_frame=processed)
                        # 更新活跃事件跟踪
                        key = (ch.person_id, ch.event_type)
                        if ch.change_type == 'ended':
                            active_events.pop(key, None)
                        else:
                            active_events[key] = now
                    db.commit()
                except Exception as e:
                    print(f"[ERROR] 事件持久化失败: {e}")
                    db.rollback()
                finally:
                    db.close()

        # 每秒更新活跃事件的 end_time
        await update_active_events_end_time()

        # 在已模糊的帧上绘制检测框
        for risk in risk_results:
            x1, y1, x2, y2 = [int(x) for x in risk.box]
            color = RISK_COLORS_BGR.get(risk.risk_level, (0, 255, 0))
            cv2.rectangle(processed, (x1, y1), (x2, y2), color, 2)
            cv2.putText(processed, risk.risk_level, (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # 编码帧图像
        _, buffer = cv2.imencode('.jpg', processed, [cv2.IMWRITE_JPEG_QUALITY, 80])
        frame_hex = buffer.tobytes().hex()

        processed_count += 1
        latency_ms = int((now - frame_ts) * 1000)

        return {
            'type': 'frame',
            'frame_id': processed_count,
            'image': frame_hex,
            'persons': [
                {
                    'person_id': r.person_id,
                    'box': [round(x, 1) for x in r.box],
                    'risk_level': r.risk_level,
                    'risk_reason': r.risk_reason,
                }
                for r in risk_results
            ],
            'latency_ms': latency_ms,
            'skipped': skipped_count,
        }

    while True:
        try:
            # 接收帧
            data = await websocket.receive()

            if isinstance(data, bytes):
                frame = decode_jpeg(data)
            elif isinstance(data, str):
                frame_bytes = base64.b64decode(data)
                frame = decode_jpeg(frame_bytes)
            else:
                continue

            if frame is None:
                continue

            # 尝试清空队列中的旧帧，只保留最新帧
            while True:
                try:
                    # 非阻塞读取：如果有更多消息，读取并丢弃旧帧
                    next_data = await asyncio.wait_for(websocket.receive(), timeout=0.001)
                    if isinstance(next_data, bytes):
                        next_frame = decode_jpeg(next_data)
                    elif isinstance(next_data, str):
                        next_frame = decode_jpeg(base64.b64decode(next_data))
                    else:
                        continue

                    if next_frame is not None:
                        frame = next_frame  # 用新帧覆盖旧帧
                        skipped_count += 1
                except asyncio.TimeoutError:
                    # 队列已空，没有更多消息
                    break
                except Exception:
                    break

            # 处理最新帧
            frame_ts = time.time()
            result = await process_frame(frame, frame_ts)
            await websocket.send_json(result)

        except Exception as e:
            print(f"WebSocket error: {e}")
            break


def _persist_event_change(db, ch, video_id: str, user_id: int,
                          core_hash: str = "", model_version: str = "",
                          snapshot_frame=None):
    """将事件变更写入数据库"""
    if ch.change_type == 'started':
        # 匿名化 person_id
        from secure_core.event_builder import EventBuilder
        anon_person_id = EventBuilder.anonymize_id(ch.person_id)

        # 保存模糊帧快照
        snapshot_path = None
        if snapshot_frame is not None:
            filename = f"evt_{video_id}_{ch.person_id}_{int(ch.start_ts)}.jpg"
            filepath = os.path.join(SNAPSHOT_DIR, filename)
            cv2.imwrite(filepath, snapshot_frame)
            snapshot_path = filepath

        # 事件开始：使用 EventChange 中的时间
        event = Event(
            user_id=user_id,
            video_id=video_id,
            person_id=ch.person_id,
            anon_person_id=anon_person_id,
            event_type=ch.event_type,
            risk_level=ch.risk_level,
            start_time=datetime.fromtimestamp(ch.start_ts),
            end_time=datetime.fromtimestamp(ch.start_ts),
            frame_count=ch.frame_count,
            snapshot_path=snapshot_path,
            feature_summary=json.dumps(ch.feature_summary, ensure_ascii=False) if ch.feature_summary else None,
            core_hash=core_hash,
            model_version=model_version,
            status='pending',
        )
        db.add(event)
    elif ch.change_type == 'risk_upgraded':
        # 风险升级：使用 start_time 精确匹配事件
        db.query(Event).filter(
            Event.video_id == video_id,
            Event.person_id == ch.person_id,
            Event.event_type == ch.event_type,
            Event.start_time == datetime.fromtimestamp(ch.start_ts),
        ).update({
            'risk_level': ch.risk_level,
            'frame_count': ch.frame_count,
            'end_time': datetime.fromtimestamp(ch.start_ts),
        })
    elif ch.change_type == 'ended':
        # 事件结束：使用 start_time 精确匹配事件
        db.query(Event).filter(
            Event.video_id == video_id,
            Event.person_id == ch.person_id,
            Event.event_type == ch.event_type,
            Event.start_time == datetime.fromtimestamp(ch.start_ts),
        ).update({
            'end_time': datetime.fromtimestamp(ch.end_ts),
            'frame_count': ch.frame_count,
        })


def decode_jpeg(data: bytes) -> np.ndarray:
    """解码 JPEG 字节流为 BGR 图像"""
    try:
        arr = np.frombuffer(data, dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return frame
    except Exception:
        return None


def build_response(detected: bool, risk_results) -> dict:
    """构建给前端的 JSON 响应"""
    return {
        'detected': detected,
        'persons': [
            {
                'person_id': r.person_id,
                'box': [round(x, 1) for x in r.box],
                'risk_level': r.risk_level,
                'risk_reason': r.risk_reason,
            }
            for r in risk_results
        ],
    }


# ── 检测配置接口 ──────────────────────────

@detect_bp.route('/api/detect/config', methods=['GET'])
@token_required
@role_required('user', 'admin')
async def get_detect_config():
    """获取当前用户的检测配置"""
    from .service import get_detection_config_service
    user_id = request.current_user['user_id']
    service = get_detection_config_service()
    config = service.get_config(user_id)
    return jsonify(config.to_dict())


@detect_bp.route('/api/detect/config', methods=['PUT'])
@token_required
@role_required('user', 'admin')
async def update_detect_config():
    """
    更新当前用户的检测配置

    请求体:
    {
        "fallen_confirm_frames": 5,
        "fallen_escalate_secs": 1.0,
        "stillness_window_secs": 30.0,
        "stillness_movement_threshold": 5.0,
        "stillness_escalate_secs": 60.0,
        "night_start_hour": 22,
        "night_end_hour": 7,
        "lost_grace_secs": 1.0
    }
    """
    from .service import get_detection_config_service
    user_id = request.current_user['user_id']
    data = await request.get_json()

    # 过滤有效字段
    valid_fields = [
        'fallen_confirm_frames', 'fallen_escalate_secs',
        'stillness_window_secs', 'stillness_movement_threshold',
        'stillness_escalate_secs', 'night_start_hour',
        'night_end_hour', 'lost_grace_secs',
        'face_detection_confidence', 'face_blur_strength', 'face_blur_expand_ratio'
    ]
    kwargs = {k: v for k, v in data.items() if k in valid_fields}

    service = get_detection_config_service()
    config = service.update_config(user_id, **kwargs)

    return jsonify({
        'message': '检测配置更新成功',
        'config': config.to_dict()
    })
