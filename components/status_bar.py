from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel

class StatusBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(30)
        layout = QHBoxLayout(self)
        self.status_icon = QLabel()
        self.status_text = QLabel("运行中")
        layout.addWidget(self.status_icon)
        layout.addWidget(self.status_text)
        layout.addStretch() 