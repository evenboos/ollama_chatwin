from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from qfluentwidgets import PrimaryPushButton
from shared_styles import STYLES

class PreviewCard(QWidget):
    jumpRequested = pyqtSignal()

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 200)
        self.title = title
        self.gui_window = None
        self.update_timer = QTimer()
        self.update_timer.setInterval(1000)
        self.update_timer.timeout.connect(self.updateThumbnail)
        self.initUI()
        self.setStyleSheet(STYLES["preview_card"])

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        title_layout = QHBoxLayout()
        self.title_label = QLabel(self.title, self)
        self.status_label = QLabel("未运行", self)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.status_label)

        self.thumbnail = QLabel(self)
        self.thumbnail.setMinimumSize(270, 140)
        self.thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail.setStyleSheet("""
            QLabel {
                background-color: #E0EEF0;
                border: 2px solid #C0D8E0;
                border-radius: 8px;
            }
        """)
        self.updateThumbnail()

        self.jump_btn = PrimaryPushButton("打开界面")
        self.jump_btn.clicked.connect(self.onJumpClicked)

        layout.addLayout(title_layout)
        layout.addWidget(self.thumbnail)
        layout.addWidget(self.jump_btn)

    def updateThumbnail(self):
        if self.gui_window:
            content = self.gui_window.get_chat_history()[-3:]
            self.drawPreview(content)

    def drawPreview(self, content):
        # 绘制缩略图的逻辑
        pass

    def onJumpClicked(self):
        self.update_timer.stop()
        self.jumpRequested.emit()

    def showEvent(self, event):
        self.update_timer.start() 