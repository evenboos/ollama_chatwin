import cv2
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QLabel

class VideoHandler:
    def __init__(self, label):
        self.label = label
        self.cap = None
        self.timer = None

    def init_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(100)

    def update_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # 处理帧并更新标签
                pass

    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
        if self.timer:
            self.timer.stop() 