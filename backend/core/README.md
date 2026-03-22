# 跌倒检测核心模块接口文档

## 概述

本模块提供基于 YOLO-pose + 规则判断的跌倒检测功能：
- **跌倒检测（FALL）**：检测画面中所有人的跌倒状态
- **长时间静止检测（STATIC）**：检测同一人持续静止不动

**数据流向：**
```
前端发送 JPEG 图片字节  →  后端解码为帧  →  core 检测  →  后端返回 JSON 给前端
```
core 只处理帧，不参与网络传输。后端负责解码图片和序列化 JSON。

---

## 文件结构

```
core/
├── __init__.py           # 模块入口
├── types.py              # 数据类型定义
├── session.py            # 会话管理、时序逻辑、多人追踪
├── fall_detector.py      # 检测器主文件
└── models/
    └── yolo11s-pose.onnx # ONNX模型文件
```

---

## 依赖安装

```bash
pip install onnxruntime      # CPU推理
pip install onnxruntime-gpu  # GPU推理（可选，需要 CUDA）
pip install opencv-python
pip install numpy
```

无需安装 PyTorch 和 Ultralytics。

---

## 接口说明

### 1. 初始化检测器

```python
from core import FallDetector

detector = FallDetector(
    model_path="core/models/yolo11s-pose.onnx",  # 模型路径
    conf_threshold=0.3                            # 检测置信度阈值
)
```

> 初始化时加载模型，耗时约 1~2 秒。建议在后端启动时完成，而不是每次请求时初始化。

---

### 2. 创建会话

```python
video_id = detector.create_session()
# 返回: str，如 "a1b2c3d4"
```

每个视频源必须创建独立会话。会话内部维护：
- 每个人的时序状态（用于判断跌倒持续时长、静止时长）
- 跨帧人员追踪（通过 IoU 匹配分配持久 person_id）

---

### 3. 处理帧（同步版本，用于脚本/测试）

```python
result = detector.process_frame(
    video_id=video_id,
    frame=frame,           # numpy 数组，BGR 格式，shape=(H, W, 3)
    timestamp=time.time()  # 时间戳，可选，默认使用当前时间
)
# 返回: SessionResult（见下方数据结构）
```

---

### 4. 处理帧（异步版本，Quart / asyncio 后端必须使用）

```python
result = await detector.process_frame_async(
    video_id=video_id,
    frame=frame,
    timestamp=time.time()
)
# 返回: SessionResult（同上）
```

> **为什么必须用异步版本：**
> `process_frame` 内部执行 ONNX 推理，是 CPU 密集型阻塞操作。
> 在 Quart / asyncio 后端中直接调用同步版本，推理期间事件循环被完全阻塞，服务无法响应任何其他请求。
> `process_frame_async` 内部将推理放入线程池执行，不阻塞事件循环。

---

### 5. 关闭会话

```python
detector.close_session(video_id)
# 返回: bool，True 表示成功关闭
```

视频处理结束后必须调用，否则会话状态会一直占用内存。

---

## 返回数据结构

### SessionResult

| 字段 | 类型 | 说明 |
|------|------|------|
| `video_id` | `str` | 会话ID |
| `frame_result` | `FrameResult` | 当前帧检测结果（可能多人） |
| `events` | `List[Event]` | 本帧触发的所有事件（可能多人同时触发） |
| `processed_frame` | `np.ndarray` \| `None` | 人脸模糊后的帧图像，通常不发给前端 |

---

### FrameResult

| 字段 | 类型 | 说明 |
|------|------|------|
| `detected` | `bool` | 是否检测到人 |
| `persons` | `List[PersonResult]` | 检测到的所有人，最多 `MAX_PERSONS` 个 |

---

### PersonResult

| 字段 | 类型 | 说明 |
|------|------|------|
| `person_id` | `int` | 持久ID，跨帧追踪同一人，由 SessionManager 通过 IoU 匹配分配 |
| `class_id` | `int` \| `None` | 姿态分类：`0`=normal，`1`=falling，`2`=fallen |
| `class_name` | `str` \| `None` | 分类名称：`"normal"` / `"falling"` / `"fallen"` |
| `confidence` | `float` | 检测置信度，范围 0~1 |
| `box` | `List[float]` | 检测框坐标 `[x1, y1, x2, y2]`，像素单位，可直接 JSON 序列化 |
| `keypoints` | `np.ndarray` \| `None` | 关键点 (17, 3)，**不可直接 JSON 序列化，需 `.tolist()`** |
| `features` | `dict` \| `None` | 内部特征，通常不需要发给前端 |

**keypoints 说明：**

共 17 个关键点，COCO 格式：鼻子、左眼、右眼、左耳、右耳、左肩、右肩、左肘、右肘、左腕、右腕、左髋、右髋、左膝、右膝、左踝、右踝。

每个关键点为 `[x, y, confidence]`。

---

### Event

| 字段 | 类型 | 说明 |
|------|------|------|
| `person_id` | `int` | 触发事件的人的持久ID |
| `event_type` | `EventType` | 事件类型，取 `.name` 得到字符串 |
| `risk_level` | `RiskLevel` | 风险等级，取 `.name` 得到字符串 |
| `start_time` | `float` | 事件开始时间戳 |
| `end_time` | `float` | 事件结束时间戳 |
| `duration` | `float` | 持续时长（秒） |
| `frame_count` | `int` | 涉及帧数 |
| `snapshot` | `np.ndarray` \| `None` | 关键帧截图，用于服务端存档 |

**事件类型：**

| `event_type.name` | 说明 | `risk_level.name` |
|-------------------|------|-------------------|
| `"FALL"` | 跌倒 | `"HIGH"` |
| `"STATIC"` | 长时间静止 | `"MEDIUM"` |
| `"NIGHT_ABNORMAL"` | 夜间异常 | `"LOW"` |

> **NIGHT_ABNORMAL 不由 core 检测。**
> 判断"现在是否夜间"依赖时间语境（上传视频 vs 实时摄像头不同），属于业务逻辑，由后端负责。
> `EventType.NIGHT_ABNORMAL` 类型保留，供后端构造事件时使用。

---

## 后端集成示例（Quart）

后端的职责：
1. 接收前端发来的 JPEG 图片字节，解码为 numpy 帧
2. 调用 `process_frame_async` 获取检测结果
3. 将结果序列化为 JSON 返回给前端（**不返回图片**）

```python
from quart import Quart, websocket, jsonify
from core import FallDetector
import cv2
import numpy as np

app = Quart(__name__)

# 后端启动时初始化一次
detector = FallDetector("core/models/yolo11s-pose.onnx")


@app.post("/session/create")
async def create_session():
    video_id = detector.create_session()
    return jsonify({"video_id": video_id})


@app.post("/session/close/<video_id>")
async def close_session(video_id):
    success = detector.close_session(video_id)
    return jsonify({"success": success})


@app.websocket("/ws/detect/<video_id>")
async def ws_detect(video_id):
    while True:
        # 1. 接收 JPEG 字节
        data = await websocket.receive()

        # 2. 解码为 numpy 帧（BGR）
        nparr = np.frombuffer(data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            continue

        # 3. 检测（必须用异步版本）
        result = await detector.process_frame_async(video_id, frame)

        # 4. 序列化多人结果
        persons = []
        for p in result.frame_result.persons:
            persons.append({
                "person_id": p.person_id,
                "class_name": p.class_name,
                "confidence": p.confidence,
                "box": p.box,  # 已经是 list，可直接序列化
                "keypoints": p.keypoints.tolist() if p.keypoints is not None else None,
            })

        events = []
        for e in result.events:
            events.append({
                "person_id": e.person_id,
                "type": e.event_type.name,
                "risk": e.risk_level.name,
                "duration": e.duration,
            })

        response = {
            "detected": result.frame_result.detected,
            "persons": persons,
            "events": events,
        }

        await websocket.send_json(response)
```

---

## 完整使用示例（本地测试）

```python
from core import FallDetector
import cv2
import time

detector = FallDetector("core/models/yolo11s-pose.onnx")
video_id = detector.create_session()

cap = cv2.VideoCapture("video.mp4")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    result = detector.process_frame(video_id, frame, time.time())

    # 多人检测结果
    for p in result.frame_result.persons:
        print(f"P{p.person_id}: {p.class_name}  conf={p.confidence:.2f}")

    # 触发的事件
    for e in result.events:
        print(f"[告警] P{e.person_id} {e.event_type.name}  持续 {e.duration:.1f}s")

detector.close_session(video_id)
cap.release()
```

---

## 时序逻辑说明

时序逻辑由 core 内部自动维护，后端无需额外处理。

| 事件 | 触发条件 | 冷却时间 |
|------|----------|----------|
| FALL | 同一 person_id 最近 10 帧中 70% 以上为 fallen 状态 | 10 秒 |
| STATIC | 同一 person_id 持续 30 秒无明显位移（< 10 像素） | 10 秒 |

**多人追踪：**
- 通过 IoU 匹配跨帧追踪同一人，分配持久 `person_id`
- 若检测框与上一帧匹配失败（IoU < 0.3），视为新人，分配新 ID
- 超过 2 秒未出现的人，其状态会被清除

---

## 参数配置

以下参数集中定义在各自的类中，每个参数只有一处定义。

| 参数 | 位置 | 默认值 | 说明 |
|------|------|--------|------|
| `MAX_PERSONS` | `FallDetector` | `3` | 单帧最多检测人数 |
| `IOU_MATCH_THRESHOLD` | `SessionManager` | `0.3` | 人员追踪 IoU 阈值 |
| `FALLEN_FRAMES_THRESHOLD` | `SessionManager` | `10` | 跌倒判定所需帧数 |
| `FALL_CONFIRM_RATIO` | `SessionManager` | `0.7` | 跌倒判定占比阈值 |
| `STATIC_DURATION_THRESHOLD` | `SessionManager` | `30.0` | 静止判定秒数 |
| `EVENT_COOLDOWN` | `SessionManager` | `10.0` | 事件冷却时间（秒） |
| `ENABLE_FACE_BLUR` | `FallDetector` | `True` | 是否开启人脸模糊 |

---

## 注意事项

1. **`detector` 全局唯一**：整个后端服务只初始化一个 `FallDetector` 实例。
2. **会话必须关闭**：视频处理结束后调用 `close_session`。
3. **每路视频独立会话**：多用户同时上传时，每路使用自己的 `video_id`。
4. **帧率建议 15~30fps**：过低会影响时序事件检测准确性。
5. **`keypoints` 序列化**：发给前端前必须调用 `.tolist()`，`box` 不需要。