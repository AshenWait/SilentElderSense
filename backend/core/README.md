# 跌倒检测核心模块

## 概述

本模块提供跌倒检测功能：
- **检测**：识别画面中的人及其状态（normal/fallen）
- **追踪**：跨帧追踪同一人（ByteTrack）
- **状态数据**：返回每帧位移，供后端判断静止

**职责划分：**
```
core: 检测 + 追踪 + 返回原始数据
后端: 判定阈值 + 告警逻辑 + 事件存储
```

---

## 文件结构

```
core/
├── __init__.py           # 模块入口
├── types.py              # 数据类型定义
├── session.py            # 会话管理、追踪
├── fall_detector.py      # 检测器主文件
└── models/
    └── fall_detection_v2.onnx  # ONNX模型
```

---

## 依赖安装

以下依赖是 **core 检测引擎运行所必需的最小依赖**，不等于仓库根目录中训练/实验脚本所需的完整环境。

```bash
pip install onnxruntime      # CPU 推理
# 或
pip install onnxruntime-gpu  # GPU 推理（二选一）

pip install opencv-python
pip install numpy
pip install boxmot           # ByteTrack 追踪必需依赖
```

默认模型路径为 `core/models/fall_detection_v2.onnx`。

---

## 接口说明

### 1. 初始化检测器

```python
from core import FallDetector

detector = FallDetector(
    model_path="core/models/fall_detection_v2.onnx",
    conf_threshold=0.3,
    tracker_fps=25.0,
)
```

---

### 2. 创建会话

```python
video_id = detector.create_session()
# 返回: str，如 "a1b2c3d4"
```

每个视频源必须创建独立会话。

---

### 3. 处理帧

```python
result = detector.process_frame(video_id, frame)

# 异步版本（Quart / asyncio 后端）
result = await detector.process_frame_async(video_id, frame)
```

---

### 4. 关闭会话

```python
detector.close_session(video_id)
```

---

## 返回数据结构

### SessionResult

| 字段 | 类型 | 说明 |
|------|------|------|
| `video_id` | `str` | 会话ID |
| `frame_result` | `FrameResult` | 当前帧检测结果 |
| `processed_frame` | `np.ndarray` | 人脸模糊后的帧 |

### FrameResult

| 字段 | 类型 | 说明 |
|------|------|------|
| `detected` | `bool` | 是否检测到人 |
| `persons` | `List[PersonResult]` | 检测到的所有人 |

### PersonResult

| 字段 | 类型 | 说明 |
|------|------|------|
| `person_id` | `int` | 追踪ID，跨帧持久 |
| `class_id` | `int` | 本帧分类：0=normal, 1=fallen |
| `class_name` | `str` | 分类名称 |
| `confidence` | `float` | 置信度 0~1 |
| `box` | `List[float]` | 检测框 [x1, y1, x2, y2] |
| `movement` | `float` \| `None` | 相比上一帧位移（像素），首帧为 None |

---

## 后端使用示例

```python
from core import FallDetector
import cv2

detector = FallDetector(tracker_fps=25.0)
video_id = detector.create_session()

# 后端自己维护状态
static_time = {}      # {person_id: 静止秒数}
fallen_frames = {}    # {person_id: 跌倒帧数}
frame_interval = 1.0 / 25.0  # 帧间隔

cap = cv2.VideoCapture("video.mp4")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    result = detector.process_frame(video_id, frame)

    for p in result.frame_result.persons:
        # 静止判断
        if p.movement is not None and p.movement < 10:
            static_time[p.person_id] = static_time.get(p.person_id, 0) + frame_interval
            if static_time[p.person_id] >= 30:
                print(f"[静止告警] ID={p.person_id}, 已静止{static_time[p.person_id]:.1f}秒")
        else:
            static_time[p.person_id] = 0

        # 跌倒判断
        if p.class_id == 1:
            fallen_frames[p.person_id] = fallen_frames.get(p.person_id, 0) + 1
            if fallen_frames[p.person_id] >= 10:
                print(f"[跌倒告警] ID={p.person_id}, 连续{fallen_frames[p.person_id]}帧")
        else:
            fallen_frames[p.person_id] = 0

    # 发送结果给前端
    # response = serialize(result)

detector.close_session(video_id)
cap.release()
```

---

## JSON 序列化示例

```python
response = {
    "detected": result.frame_result.detected,
    "persons": [
        {
            "person_id": p.person_id,
            "class_id": p.class_id,
            "class_name": p.class_name,
            "confidence": p.confidence,
            "box": p.box,
            "movement": p.movement,
        }
        for p in result.frame_result.persons
    ]
}
```

---

## 配置参数

| 参数 | 位置 | 默认值 | 说明 |
|------|------|--------|------|
| `MAX_PERSONS` | `FallDetector` | `3` | 单帧最多检测人数 |
| `ENABLE_FACE_BLUR` | `FallDetector` | `True` | 是否开启人脸模糊 |
| `tracker_fps` | `FallDetector.__init__` | `25.0` | 追踪器预期帧率 |

---

## 注意事项

1. **detector 全局唯一**：整个后端服务只初始化一个实例
2. **会话必须关闭**：视频处理结束后调用 `close_session`
3. **每路视频独立会话**：多用户同时使用时，各自使用自己的 `video_id`
4. **movement 首帧为 None**：后端需处理此情况

---

## ONNX 推理说明

### 模型输出格式

YOLO11 导出的 ONNX **不含 NMS**，输出原始锚点预测：

```
输出形状：[1, 6, 2100]
每个锚点 6 维：[cx, cy, w, h, class0_score, class1_score]
```

- `class0_score`：normal 的概率（sigmoid 后，0–1）
- `class1_score`：fallen 的概率（sigmoid 后，0–1）

**注意**：这两列是各自独立的概率，不是 softmax，不能直接取某一列作为置信度。

### 类别判断方式

正确做法是取两列中的最大值作为置信度，并以 argmax 确定类别：

```python
class_scores = pred[:, 4:]                              # (N, 2)
class_ids = np.argmax(class_scores, axis=1)             # 0=normal, 1=fallen
scores = class_scores[np.arange(N), class_ids]          # 对应类别的置信度
```

❌ 错误做法（永远输出 normal）：
```python
cx, cy, w, h, score, class_id = det  # class_id = float(0.6x) → int → 0
```

### NMS

ONNX 导出不含 NMS，`core` 内部使用 `cv2.dnn.NMSBoxes` 完成后处理，阈值为 `nms_threshold=0.45`，无需调用方额外处理。