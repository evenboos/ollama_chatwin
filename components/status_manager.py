from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel

class StatusManager(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout(self)
        self.status_icon = QLabel()
        self.status_text = QLabel("运行中")
        layout.addWidget(self.status_icon)
        layout.addWidget(self.status_text)
        layout.addStretch()

    def update_status(self, state):
        # 更新状态逻辑
        pass 