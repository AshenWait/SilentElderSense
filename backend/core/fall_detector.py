"""
跌倒检测器 - ONNX版本

整合姿态检测 + 时序逻辑
"""
import cv2
import numpy as np
import onnxruntime as ort
from typing import Optional, Callable

from typing import List

from .types import (
    FrameResult, PersonResult, Event, SessionResult,
    EventType, RiskLevel
)
from .session import SessionManager


class FallDetector:
    """
    跌倒检测器

    使用方式:
        detector = FallDetector("core/models/yolo11s-pose.onnx")

        # 创建视频会话
        video_id = detector.create_session()

        # 处理帧
        result = detector.process_frame(video_id, frame, timestamp)
        if result.event:
            print(f"检测到事件: {result.event.event_type}")

        # 结束会话
        detector.close_session(video_id)
    """

    # 单帧最多检测人数
    MAX_PERSONS = 3

    # 检测框放大比例
    W_SCALE = 1.26
    H_SCALE = 1.10

    # 分类阈值
    ANGLE_THRESHOLD_FALLEN = 60
    ANGLE_THRESHOLD_NORMAL = 35
    RATIO_THRESHOLD_FALLEN = 1.3
    RATIO_THRESHOLD_NORMAL = 1.0

    # ===== 人脸模糊配置 =====
    # 修改这里来控制是否开启人脸模糊
    ENABLE_FACE_BLUR = True           # 是否开启人脸模糊
    FACE_BLUR_STRENGTH = 51           # 模糊强度（奇数，越大越模糊）
    FACE_BLUR_EXPAND_RATIO = 0.5      # 头部区域扩展比例

    def __init__(self, model_path: str = "core/models/yolo11s-pose.onnx",
                 conf_threshold: float = 0.3,
                 providers: list = None):
        """
        初始化检测器

        Args:
            model_path: ONNX模型路径
            conf_threshold: 检测置信度阈值
            providers: ONNX Runtime providers
        """
        self.model_path = model_path
        self.conf_threshold = conf_threshold

        # ONNX推理
        if providers is None:
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        self.session = ort.InferenceSession(model_path, providers=providers)
        self.input_name = self.session.get_inputs()[0].name
        self.input_shape = self.session.get_inputs()[0].shape
        self.img_size = self.input_shape[2]

        # 会话管理
        self.session_manager = SessionManager()

        # 保存原始图像尺寸
        self.orig_shape = None

    # ==================== 接口 ====================

    def create_session(self) -> str:
        """
        创建新的视频会话

        Returns:
            video_id: 会话ID
        """
        return self.session_manager.create_session()

    def process_frame(self, video_id: str, frame: np.ndarray,
                      timestamp: float = None) -> SessionResult:
        """
        处理单帧图像

        Args:
            video_id: 会话ID
            frame: BGR图像
            timestamp: 时间戳(可选，默认使用当前时间)

        Returns:
            SessionResult: 包含帧结果、可能的异常事件、处理后的帧
        """
        import time
        if timestamp is None:
            timestamp = time.time()

        # 检测单帧
        frame_result = self._detect_single(frame)

        # 对每个检测到的人分别做人脸模糊
        processed_frame = frame.copy()
        if frame_result.detected:
            for person in frame_result.persons:
                if person.keypoints is not None:
                    processed_frame = self._apply_face_blur(processed_frame, person.keypoints)

        # 时序处理，返回本帧触发的所有事件
        events = self.session_manager.process(video_id, frame_result, timestamp, processed_frame)

        return SessionResult(
            video_id=video_id,
            frame_result=frame_result,
            events=events,
            processed_frame=processed_frame
        )

    async def process_frame_async(self, video_id: str, frame: np.ndarray,
                                  timestamp: float = None) -> SessionResult:
        """
        处理单帧图像（异步版本，供 Quart / asyncio 后端使用）

        ONNX 推理是 CPU 密集型阻塞操作，直接在协程中调用会卡住事件循环。
        此方法自动将推理放入线程池执行，后端直接 await 即可。

        Args:
            video_id: 会话ID
            frame: BGR图像
            timestamp: 时间戳(可选)

        Returns:
            SessionResult: 同 process_frame
        """
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.process_frame, video_id, frame, timestamp)

    def close_session(self, video_id: str) -> bool:
        """
        关闭会话

        Args:
            video_id: 会话ID

        Returns:
            是否成功关闭
        """
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
        """后处理模型输出，返回最多 MAX_PERSONS 个检测结果，每项为 (box, keypoints, score)"""
        pred = outputs[0]  # (1, 56, num_preds) 或 (1, num_preds, 56)

        # 转置处理 (1, 56, 2100) -> (1, 2100, 56)
        if pred.shape[1] == 56:
            pred = pred.transpose(0, 2, 1)

        pred = pred[0]  # (num_preds, 56)

        # 过滤低置信度
        scores = pred[:, 4]
        mask = scores > self.conf_threshold
        pred = pred[mask]

        if len(pred) == 0:
            return []

        # 按置信度排序，取前 MAX_PERSONS 个
        sorted_idx = np.argsort(pred[:, 4])[::-1][:self.MAX_PERSONS]

        scale_h = self.orig_shape[0] / self.img_size
        scale_w = self.orig_shape[1] / self.img_size

        results = []
        for idx in sorted_idx:
            best = pred[idx]
            cx, cy, w, h = best[:4]
            score = best[4]

            x1 = (cx - w / 2) * scale_w
            y1 = (cy - h / 2) * scale_h
            x2 = (cx + w / 2) * scale_w
            y2 = (cy + h / 2) * scale_h

            box = self._scale_box(np.array([x1, y1, x2, y2]))

            kpts = best[5:].reshape(17, 3).copy()
            kpts[:, 0] *= scale_w
            kpts[:, 1] *= scale_h

            results.append((box, kpts, float(score)))

        return results

    def _scale_box(self, box: np.ndarray) -> np.ndarray:
        """放大检测框"""
        cx = (box[0] + box[2]) / 2
        cy = (box[1] + box[3]) / 2
        w = box[2] - box[0]
        h = box[3] - box[1]
        new_w = w * self.W_SCALE
        new_h = h * self.H_SCALE
        return np.array([
            cx - new_w / 2, cy - new_h / 2,
            cx + new_w / 2, cy + new_h / 2
        ])

    def _extract_features(self, keypoints: np.ndarray) -> Optional[dict]:
        """提取特征"""
        kps = keypoints
        visible = sum(1 for i in range(17) if kps[i][2] > 0.5)
        if visible < 5:
            return None

        features = {'visible': visible}

        # 宽高比
        valid = [kps[i] for i in range(17) if kps[i][2] > 0.3]
        if len(valid) >= 3:
            xs = [kp[0] for kp in valid]
            ys = [kp[1] for kp in valid]
            features['aspect_ratio'] = (max(xs) - min(xs)) / (max(ys) - min(ys) + 1e-6)

        # 脊柱角度
        if all(kps[i][2] > 0.3 for i in [5, 6, 11, 12]):
            shoulder = np.array([(kps[5][0] + kps[6][0]) / 2, (kps[5][1] + kps[6][1]) / 2])
            hip = np.array([(kps[11][0] + kps[12][0]) / 2, (kps[11][1] + kps[12][1]) / 2])
            spine = shoulder - hip
            vertical = np.array([0, -1])
            cos_angle = np.dot(spine, vertical) / (np.linalg.norm(spine) + 1e-6)
            features['spine_angle'] = np.arccos(np.clip(cos_angle, -1, 1)) * 180 / np.pi

        return features

    def _classify(self, features: Optional[dict]) -> Optional[int]:
        """规则分类"""
        if features is None:
            return None

        angle = features.get('spine_angle', 0)
        ratio = features.get('aspect_ratio', 1)

        if angle > self.ANGLE_THRESHOLD_FALLEN and ratio > self.RATIO_THRESHOLD_FALLEN:
            return 2  # fallen
        if angle < self.ANGLE_THRESHOLD_NORMAL and ratio < self.RATIO_THRESHOLD_NORMAL:
            return 0  # normal
        return 1  # falling

    def _detect_single(self, frame: np.ndarray) -> FrameResult:
        """单帧检测，返回所有检测到的人（最多 MAX_PERSONS 个）"""
        img = self._preprocess(frame)
        outputs = self.session.run(None, {self.input_name: img})
        detections = self._postprocess(outputs)

        if not detections:
            return FrameResult(detected=False, persons=[])

        persons = []
        for i, (box, keypoints, score) in enumerate(detections):
            features = self._extract_features(keypoints)
            class_id = self._classify(features)
            class_name = {0: 'normal', 1: 'falling', 2: 'fallen'}.get(class_id)

            # person_id 此处为帧内临时序号，持久 ID 由 SessionManager 通过 IoU 匹配分配
            persons.append(PersonResult(
                person_id=i,
                class_id=class_id,
                class_name=class_name,
                confidence=score,
                box=box.tolist(),
                keypoints=keypoints,
                features=features
            ))

        return FrameResult(detected=True, persons=persons)

    def _get_head_region(self, keypoints: np.ndarray, frame_shape: tuple) -> tuple:
        """
        根据头部关键点计算头部区域边界框

        Args:
            keypoints: 关键点 (17, 3)
            frame_shape: 帧尺寸 (h, w)

        Returns:
            (x1, y1, x2, y2) 或 None
        """
        h, w = frame_shape[:2]

        # 头部关键点索引: 0=鼻子, 1=左眼, 2=右眼, 3=左耳, 4=右耳
        head_indices = [0, 1, 2, 3, 4]
        valid_points = []

        for idx in head_indices:
            x, y, conf = keypoints[idx]
            if conf > 0.3:
                valid_points.append((x, y))

        if len(valid_points) < 2:
            # 头部关键点不足，用肩膀推断
            left_shoulder = keypoints[5]
            right_shoulder = keypoints[6]

            if left_shoulder[2] > 0.3 and right_shoulder[2] > 0.3:
                shoulder_mid_x = (left_shoulder[0] + right_shoulder[0]) / 2
                shoulder_mid_y = (left_shoulder[1] + right_shoulder[1]) / 2
                shoulder_width = abs(right_shoulder[0] - left_shoulder[0])

                head_size = shoulder_width * 0.75
                head_y = shoulder_mid_y - head_size * 1.2

                return (
                    max(0, int(shoulder_mid_x - head_size / 2)),
                    max(0, int(head_y)),
                    min(w, int(shoulder_mid_x + head_size / 2)),
                    min(h, int(head_y + head_size))
                )
            return None

        # 计算头部边界框
        points = np.array(valid_points)
        x_min, y_min = points.min(axis=0)
        x_max, y_max = points.max(axis=0)

        width = x_max - x_min
        height = y_max - y_min
        head_size = max(width, height) * (1 + self.FACE_BLUR_EXPAND_RATIO)

        center_x = (x_min + x_max) / 2
        center_y = (y_min + y_max) / 2

        half_size = head_size / 2
        x1 = max(0, int(center_x - half_size))
        y1 = max(0, int(center_y - half_size))
        x2 = min(w, int(center_x + half_size))
        y2 = min(h, int(center_y + half_size))

        return (x1, y1, x2, y2)

    def _blur_region(self, frame: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
        """对指定区域进行高斯模糊"""
        h, w = frame.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)

        if x1 >= x2 or y1 >= y2:
            return frame

        region = frame[y1:y2, x1:x2]
        blurred = cv2.GaussianBlur(region, (self.FACE_BLUR_STRENGTH, self.FACE_BLUR_STRENGTH), 0)
        frame[y1:y2, x1:x2] = blurred

        return frame

    def _apply_face_blur(self, frame: np.ndarray, keypoints: np.ndarray) -> np.ndarray:
        """
        对帧应用人脸模糊

        Args:
            frame: 原始帧
            keypoints: 关键点

        Returns:
            模糊后的帧
        """
        if not self.ENABLE_FACE_BLUR:
            return frame

        if keypoints is None:
            return frame

        head_box = self._get_head_region(keypoints, frame.shape)
        if head_box:
            x1, y1, x2, y2 = head_box
            if x2 - x1 > 5 and y2 - y1 > 5:
                frame = self._blur_region(frame, x1, y1, x2, y2)

        return frame