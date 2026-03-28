"""
跌倒检测器 - ONNX版本

使用跌倒检测模型 + Haar Cascade 人脸模糊
返回检测数据，后端自行处理业务逻辑
"""
import cv2
import numpy as np
import onnxruntime as ort
from typing import Optional, List

from .types import FrameResult, PersonResult, SessionResult
from .session import SessionManager


class FallDetector:
    """
    跌倒检测器

    使用方式:
        detector = FallDetector()

        # 创建视频会话
        video_id = detector.create_session()

        # 处理帧
        result = detector.process_frame(video_id, frame)
        for p in result.frame_result.persons:
            print(f"ID={p.person_id}, class={p.class_name}, movement={p.movement}")

        # 结束会话
        detector.close_session(video_id)
    """

    # 单帧最多检测人数
    MAX_PERSONS = 3

    # 类别名称映射
    CLASS_NAMES = {0: 'normal', 1: 'fallen'}

    # 人脸模糊配置
    ENABLE_FACE_BLUR = True
    FACE_BLUR_STRENGTH = 51
    FACE_BLUR_EXPAND_RATIO = 0.5

    def __init__(self,
                 model_path: str = "core/models/fall_detection_v2.onnx",
                 conf_threshold: float = 0.3,
                 tracker_fps: float = 25.0,
                 providers: list = None):
        """
        初始化检测器

        Args:
            model_path: ONNX模型路径
            conf_threshold: 检测置信度阈值
            tracker_fps: 追踪器预期帧率
            providers: ONNX Runtime providers
        """
        self.model_path = model_path
        self.conf_threshold = conf_threshold

        # ONNX推理
        if providers is None:
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        self.session = ort.InferenceSession(model_path, providers=providers)
        self.input_name = self.session.get_inputs()[0].name
        self.img_size = self.session.get_inputs()[0].shape[2]

        # Haar Cascade 人脸检测器
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        # 会话管理（追踪）
        self.session_manager = SessionManager(tracker_fps=tracker_fps)

        # 保存原始图像尺寸
        self.orig_shape = None

    # ==================== 接口 ====================

    def create_session(self) -> str:
        """创建新的视频会话"""
        return self.session_manager.create_session()

    def process_frame(self, video_id: str, frame: np.ndarray) -> SessionResult:
        """
        处理单帧图像

        Args:
            video_id: 会话ID
            frame: BGR图像

        Returns:
            SessionResult: 包含检测结果、处理后的帧
        """
        # 检测单帧
        frame_result = self._detect_single(frame)

        # 人脸模糊
        processed_frame = frame.copy()
        if self.ENABLE_FACE_BLUR and frame_result.detected:
            processed_frame = self._apply_face_blur(processed_frame)

        # 追踪 + 计算 movement
        frame_result = self.session_manager.process(video_id, frame_result, frame)

        return SessionResult(
            video_id=video_id,
            frame_result=frame_result,
            processed_frame=processed_frame
        )

    async def process_frame_async(self, video_id: str, frame: np.ndarray) -> SessionResult:
        """处理单帧图像（异步版本）"""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.process_frame, video_id, frame)

    def close_session(self, video_id: str) -> bool:
        """关闭会话"""
        return self.session_manager.close_session(video_id)

    # ==================== 内部方法 ====================

    def _preprocess(self, frame: np.ndarray) -> np.ndarray:
        """预处理图像"""
        self.orig_shape = frame.shape[:2]
        img = cv2.resize(frame, (self.img_size, self.img_size))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.transpose(2, 0, 1)
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)
        return img

    def _postprocess(self, outputs: tuple) -> List[tuple]:
        """
        后处理模型输出

        YOLO11 ONNX 输出格式：[1, 6, 2100]
        每个锚点 6 维：[cx, cy, w, h, class0_score, class1_score]
        其中 class0=normal, class1=fallen，均为 sigmoid 后的概率值。

        Returns:
            [(box, class_id, score), ...]  经过 NMS 后的结果
        """
        pred = outputs[0]  # (1, 6, 2100)

        # 转置 (1, 6, 2100) -> (2100, 6)
        if pred.shape[1] == 6:
            pred = pred.transpose(0, 2, 1)
        pred = pred[0]  # (2100, 6)

        # 取各锚点最高类别分数及对应类别
        class_scores = pred[:, 4:]          # (2100, 2)
        class_ids = np.argmax(class_scores, axis=1)    # (2100,)
        scores = class_scores[np.arange(len(pred)), class_ids]  # (2100,)

        # 过滤低置信度
        mask = scores > self.conf_threshold
        pred = pred[mask]
        scores = scores[mask]
        class_ids = class_ids[mask]

        if len(pred) == 0:
            return []

        scale_h = self.orig_shape[0] / self.img_size
        scale_w = self.orig_shape[1] / self.img_size

        # 将 cx,cy,w,h 转为 x1,y1,x2,y2（原图坐标）
        cx, cy, w, h = pred[:, 0], pred[:, 1], pred[:, 2], pred[:, 3]
        x1 = (cx - w / 2) * scale_w
        y1 = (cy - h / 2) * scale_h
        x2 = (cx + w / 2) * scale_w
        y2 = (cy + h / 2) * scale_h
        boxes = np.stack([x1, y1, x2, y2], axis=1)  # (N, 4)

        # NMS：用 OpenCV，输入格式为 [x, y, w, h]
        boxes_xywh = np.stack([x1, y1, x2 - x1, y2 - y1], axis=1)
        indices = cv2.dnn.NMSBoxes(
            boxes_xywh.tolist(),
            scores.tolist(),
            score_threshold=self.conf_threshold,
            nms_threshold=0.45,
        )

        if len(indices) == 0:
            return []

        # cv2.dnn.NMSBoxes 返回值在不同版本中可能为 (N,1) 或 (N,)
        indices = np.array(indices).flatten()

        # 按置信度降序，最多取 MAX_PERSONS 个
        indices = sorted(indices, key=lambda i: scores[i], reverse=True)[:self.MAX_PERSONS]

        results = []
        for idx in indices:
            box = [float(boxes[idx, 0]), float(boxes[idx, 1]),
                   float(boxes[idx, 2]), float(boxes[idx, 3])]
            results.append((box, int(class_ids[idx]), float(scores[idx])))

        return results

    def _detect_single(self, frame: np.ndarray) -> FrameResult:
        """单帧检测"""
        img = self._preprocess(frame)
        outputs = self.session.run(None, {self.input_name: img})
        detections = self._postprocess(outputs)

        if not detections:
            return FrameResult(detected=False, persons=[])

        persons = []
        for i, (box, class_id, score) in enumerate(detections):
            class_name = self.CLASS_NAMES.get(class_id, 'unknown')

            persons.append(PersonResult(
                person_id=i,  # 临时ID，追踪后会更新
                class_id=class_id,
                class_name=class_name,
                confidence=score,
                box=box,
                movement=None
            ))

        return FrameResult(detected=True, persons=persons)

    def _apply_face_blur(self, frame: np.ndarray) -> np.ndarray:
        """使用 Haar Cascade 检测人脸并模糊"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(20, 20))

        h, w = frame.shape[:2]

        for (x, y, fw, fh) in faces:
            # 扩大模糊区域
            expand = self.FACE_BLUR_EXPAND_RATIO
            cx, cy = x + fw // 2, y + fh // 2
            new_w = int(fw * (1 + expand))
            new_h = int(fh * (1 + expand))
            x1 = max(0, cx - new_w // 2)
            y1 = max(0, cy - new_h // 2)
            x2 = min(w, cx + new_w // 2)
            y2 = min(h, cy + new_h // 2)

            if x2 - x1 > 5 and y2 - y1 > 5:
                region = frame[y1:y2, x1:x2]
                blurred = cv2.GaussianBlur(region, (self.FACE_BLUR_STRENGTH, self.FACE_BLUR_STRENGTH), 0)
                frame[y1:y2, x1:x2] = blurred

        return frame