from PyQt6.QtWidgets import QLineEdit, QPushButton, QWidget, QHBoxLayout

class InputHandler(QWidget):
    def __init__(self, send_callback):
        super().__init__()
        self.send_callback = send_callback
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout(self)
        self.input_field = QLineEdit()
        self.send_btn = QPushButton("发送")
        
        layout.addWidget(self.input_field)
        layout.addWidget(self.send_btn)

        self.send_btn.clicked.connect(self.handle_send)
        self.input_field.returnPressed.connect(self.handle_send)

    def handle_send(self):
        text = self.input_field.text().strip()
        if text:
            self.send_callback(text)
            self.input_field.clear()