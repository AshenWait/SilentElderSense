"""
摄像头捕获服务

使用 OpenCV 获取本机摄像头，支持推流
"""
import cv2
import threading
import time
import base64
from typing import Optional, Generator, List, Callable


class CameraService:
    """摄像头服务类"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.cap: Optional[cv2.VideoCapture] = None
        self.camera_id: int = 0
        self.is_running: bool = False
        self._frame_lock = threading.Lock()
        self._current_frame: Optional[bytes] = None
        self._thread: Optional[threading.Thread] = None
        self._subscribers: List[Callable] = []
        self._fps: int = 30
        self._width: int = 640
        self._height: int = 480

    def list_cameras(self, max_test: int = 5) -> List[dict]:
        """
        列出可用的摄像头

        Args:
            max_test: 最大测试的摄像头数量

        Returns:
            摄像头列表 [{"id": 0, "name": "Camera 0"}, ...]
        """
        cameras = []
        for i in range(max_test):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                cameras.append({
                    "id": i,
                    "name": f"Camera {i}",
                    "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                })
                cap.release()
        return cameras

    def start_capture(self, camera_id: int = 0, width: int = 640, height: int = 480) -> bool:
        """
        启动摄像头捕获

        Args:
            camera_id: 摄像头ID
            width: 视频宽度
            height: 视频高度

        Returns:
            是否启动成功
        """
        if self.is_running:
            self.stop_capture()

        self.camera_id = camera_id
        self._width = width
        self._height = height

        self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            return False

        # 设置分辨率
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        self.is_running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

        return True

    def stop_capture(self) -> bool:
        """停止摄像头捕获"""
        self.is_running = False

        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None

        if self.cap:
            self.cap.release()
            self.cap = None

        self._current_frame = None
        return True

    def _capture_loop(self):
        """摄像头捕获循环"""
        while self.is_running and self.cap:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue

            # 缩放帧
            if frame.shape[1] != self._width or frame.shape[0] != self._height:
                frame = cv2.resize(frame, (self._width, self._height))

            # 编码为 JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ret:
                with self._frame_lock:
                    self._current_frame = buffer.tobytes()

                # 通知订阅者
                for callback in self._subscribers[:]:
                    try:
                        callback(self._current_frame)
                    except Exception:
                        self._subscribers.remove(callback)

            time.sleep(1.0 / self._fps)

    def get_frame(self) -> Optional[bytes]:
        """获取当前帧 (JPEG 字节流)"""
        with self._frame_lock:
            return self._current_frame

    def get_frame_base64(self) -> Optional[str]:
        """获取当前帧 (Base64 编码)"""
        frame = self.get_frame()
        if frame:
            return base64.b64encode(frame).decode('utf-8')
        return None

    def gen_frames(self) -> Generator[bytes, None, None]:
        """
        生成帧流 (用于 MJPEG 流)

        Yields:
            JPEG 帧数据
        """
        while self.is_running:
            frame = self.get_frame()
            if frame:
                yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
            time.sleep(1.0 / self._fps)

    def subscribe(self, callback: Callable[[bytes], None]):
        """订阅帧更新"""
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[bytes], None]):
        """取消订阅"""
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    @property
    def status(self) -> dict:
        """获取摄像头状态"""
        return {
            "is_running": self.is_running,
            "camera_id": self.camera_id,
            "width": self._width,
            "height": self._height,
            "fps": self._fps
        }


# 全局摄像头服务实例
camera_service = CameraService()