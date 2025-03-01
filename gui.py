import sys
import cv2
import ollama  # 添加 ollama 导入
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QObject, QThreadPool, QRunnable, QSize, QEvent, QRectF
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor, QPainterPath
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSizePolicy
from qfluentwidgets import (
    FluentWindow, BodyLabel, TextEdit, LineEdit, PrimaryPushButton,
    isDarkTheme, applyThemeColor, MessageBox, StateToolTip,MSFluentWindow,FluentIcon
)
from shared_styles import *
from components.preview_card import PreviewCard  # 更新导入
from components.ai_worker import AIWorker, AIRequest  # 修改导入语句
from components.status_bar import StatusBar
from components.input_handler import InputHandler
from components.status_manager import StatusManager

# 在文件顶部添加
MAIN_BG = "#F4F8FF"
CARD_BG = "#E0EEF0" 
BORDER_COLOR = "#C0D8E0"
PRIMARY_COLOR = "#6BA8FF"

class VideoHandler:
    def __init__(self, label):
        self.label = label  # 确保 label 被正确赋值
        self.cap = None
        self.timer = QTimer()  # 初始化 timer

    def init_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(100)

    def update_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # 转换颜色空间 BGR -> RGB
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                
                # 创建 QImage
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                
                # 根据标签尺寸保持比例缩放
                label_size = self.label.size()  # 每次更新时获取最新的标签大小
                scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
                    label_size, 
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.label.setPixmap(scaled_pixmap)  # 使用 self.label
                print("摄像头画面已更新到视频标签")

    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
        if self.timer:
            self.timer.stop()

class GUIWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.model_name = "qwen2.5:7b"
        self.thread_pool = QThreadPool()
        self.ai_worker = AIWorker(self.model_name)
        self.ai_worker.charReceived.connect(self.append_char)
        self.ai_worker.finished.connect(self.on_response_finished)

        self.initUI()  # 先初始化 UI
        self.video_handler = VideoHandler(self.video_label)  # 初始化视频处理
        self.status_manager = StatusManager()
        self.input_handler = InputHandler(self.handle_send)
        
        self.request_queue = []  # 添加请求队列
        self.is_processing = False  # 处理状态标志
        self.current_request = None  # 当前请求

        self.initCamera()  # 初始化摄像头

    def initUI(self):
        self.setWindowTitle('智能助手界面')
        self.resize(1200, 800)
        
        # 主容器样式
        main_widget = QWidget()
        main_widget.setObjectName("mainInterface")
        main_widget.setStyleSheet("background-color: #D2E2F9;")
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # ================= 左侧聊天面板 =================
        left_panel = QWidget()
        left_panel.setStyleSheet("background-color: #F4F8FF; border-radius: 15px;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(15)

        # ================= 状态栏 =================
        status_bar = QWidget()
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(5, 2, 5, 2)
        
        self.status_icon = QLabel()  # 确保使用 self. 前缀
        self.status_icon.setFixedSize(16, 16)
        self.status_text = BodyLabel("运行中")  # 确保使用 self. 前缀
        
        status_layout.addWidget(self.status_icon)
        status_layout.addWidget(self.status_text)
        status_layout.addStretch()

        # 聊天记录显示区域
        self.chat_display = TextEdit()
        self.chat_display.setStyleSheet(STYLES["chat_display"])
        self.chat_display.setMinimumHeight(400)

        # 输入区域容器
        input_container = QWidget()
        input_container.setFixedHeight(60)  # 固定高度
        input_container.setStyleSheet("""
            background-color: #F4F8FF;
            border-radius: 10px;
            padding: 10px;  # 减少内边距
        """)

        # 调整布局参数
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(10)
        input_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # 用户输入框
        self.input_field = LineEdit()
        self.input_field.setStyleSheet("""
            LineEdit {
                background-color: #FFFFFF;
                border: 2px solid #C0D8E0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                min-height: 40px;
                max-height: 40px;
            }
        """)

        # 发送按钮
        self.send_btn = PrimaryPushButton("发送")
        self.send_btn.setStyleSheet("""
            PrimaryPushButton {
                background-color: #6BA8FF;
                color: white;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                min-height: 40px;
                height: 40px;
                min-width: 80px;
            }
            PrimaryPushButton:hover {
                background-color: #5B98E6;
            }
        """)

        input_layout.addWidget(self.input_field, 15)  # 15份比例
        input_layout.addWidget(self.send_btn, 1)     # 1份比例

        # 组装左侧面板
        left_layout.addWidget(status_bar)
        left_layout.addWidget(self.chat_display, 85)
        left_layout.addWidget(input_container, 15)

        # ================= 右侧视频面板 =================
        right_panel = QWidget()
        right_panel.setObjectName("right_panel")  # 设置 objectName
        right_panel.setStyleSheet("""
            background-color: #F4F8FF;
            border-radius: 15px;
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)
        
        # 视频显示区域
        self.video_label = QLabel(self)
        self.video_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.video_label.setFixedSize(720,480)  # 设置固定大小

        self.video_label.setStyleSheet("""
            background-color: #F4F8FF;
            border: 2px solid #C0D8E0;
            border-radius: 10px;
        """)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.video_label)
        right_layout.setStretch(0, 1)  # 使 video_label 占满可用空间

        # ================= 整体布局 =================
        layout.addWidget(left_panel, 13)  # 40% 宽度
        layout.addWidget(right_panel, 33)  # 60% 宽度
        
        main_widget.setObjectName("mainInterface")
        self.addSubInterface(main_widget, FluentIcon.HOME, '主界面')
        
        # ================= 事件绑定 =================
        self.send_btn.clicked.connect(self.handle_send)
        self.input_field.returnPressed.connect(self.handle_send)
        
        # 初始化消息
        self.chat_display.append("系统: 界面初始化完成，等待用户输入...")
        
        # 初始状态
        self.update_status("normal")
        
        # 调整标题栏按钮边距
        self.titleBar.maxBtn.setGeometry(
            self.width() - 46, 8, 30, 24)
        self.titleBar.closeBtn.setGeometry(
            self.width() - 76, 8, 30, 24)

        self.titleBar.setStyleSheet(f"""
            TitleBar {{
                background-color: {TITLE_BG};
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }}
            TitleBar QToolButton {{
                background-color: transparent;
                border: none;
            }}
        """)

    def initCamera(self):
        """初始化摄像头设备"""
        try:
            print("尝试初始化摄像头...")
            self.video_handler.cap = cv2.VideoCapture(0)  # 尝试使用索引 0
            if not self.video_handler.cap.isOpened():
                raise Exception("无法打开摄像头")
            
            # 设置摄像头分辨率
            self.video_handler.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.video_handler.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            print("摄像头初始化成功，分辨率设置为640x480")
            
            # 连接定时器
            self.video_handler.timer.timeout.connect(self.video_handler.update_frame)  # 连接定时器
            self.video_handler.timer.start(33)  # 约30fps
            print("定时器已启动，帧更新频率为30fps")
            
        except Exception as e:
            error_msg = f"摄像头初始化失败: {str(e)}"
            print(error_msg)
            self.chat_display.append(f"系统: {error_msg}")
            if self.video_label:
                self.video_label.setText("摄像头未就绪")

    def handle_send(self):
        """处理发送消息"""
        text = self.input_field.text().strip()
        if text:
            self.update_status("normal")
            self.request_queue.append(text)  # 将请求加入队列
            self.input_field.clear()
            self.process_next_request()

    def process_next_request(self):
        """处理下一个请求"""
        if self.is_processing or not self.request_queue:
            return

        self.is_processing = True
        text = self.request_queue.pop(0)  # 从队列中取出下一个请求

        # 显示用户输入
        self.chat_display.append(f"用户: {text}")
        self.current_response = "AI: "
        self.chat_display.append(self.current_response)

        # 提交新请求
        self.current_request = AIRequest(self.ai_worker, text)
        self.thread_pool.start(self.current_request)

    def on_response_finished(self):
        """响应完成处理"""
        self.is_processing = False
        self.current_request = None
        self.process_next_request()  # 处理下一个请求

    def append_char(self, char):
        """添加单个字符到显示"""
        self.current_response += char
        # 更新最后一行
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.movePosition(cursor.MoveOperation.StartOfBlock, cursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(self.current_response)
        
        # 滚动到底部
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )

    def closeEvent(self, event):
        """窗口关闭事件"""
        if hasattr(self, 'timer') and self.timer:
            self.timer.stop()
        if hasattr(self, 'cap') and self.cap:
            self.cap.release()
        super().closeEvent(event)

    def modify(self):
        """修改窗口状态"""
        print("修改窗口状态")

    def status(self):
        """获取窗口状态"""
        return "运行中"

    def save_state(self):
        """保存窗口状态"""
        print("保存窗口状态")

    def get_dialog_content(self):
        """获取对话框内容"""
        return self.chat_display.toPlainText()
    def showEvent(self, event):
        super().showEvent(event)
        # 移除之前的样式重置代码
        # self.setStyleSheet('')
        # self.setStyleSheet(STYLES["main_window"])
        # 改为仅刷新子控件
        self.style().unpolish(self)
        self.style().polish(self)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # 创建带圆角的遮罩区域
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 10, 10)
        painter.setClipPath(path)
        
        # 绘制背景
        painter.fillPath(path, QColor(MAIN_BG))
        super().paintEvent(event)

    def changeEvent(self, event):
        """处理窗口状态变化"""
        if event.type() == QEvent.Type.WindowStateChange:
            self.titleBar.update()
        super().changeEvent(event)

    def moveEvent(self, event):
        """窗口移动时暂停更新"""
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        super().moveEvent(event)

    def moveEndEvent(self, event):
        """窗口移动结束时恢复更新"""
        if hasattr(self, 'timer') and not self.timer.isActive():
            self.timer.start(50)
        super().moveEndEvent(event)

    def update_status(self, state):
        """更新状态栏
        Args:
            state: normal | waiting | error
        """
        color_map = {
            "normal": ("#00FF00", "运行中"),
            "waiting": ("#FFA500", "等待用户输入"),
            "error": ("#FF0000", "发生错误")
        }
        
        color, text = color_map.get(state, ("#666666", "未知状态"))
        
        # 创建圆形图标
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setBrush(QColor(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, 16, 16)
        painter.end()
        
        self.status_icon.setPixmap(pixmap)
        self.status_text.setText(text)

    def on_require_human_input(self, message):
        """需要人工介入时的处理"""
        self.need_human_intervention = True
        self.update_status("waiting")
        
        # 禁用输入
        self.input_field.setEnabled(False)
        self.send_btn.setEnabled(False)
        
        # 显示状态提示
        self.state_tooltip = StateToolTip("需要确认", message, self)
        self.state_tooltip.move(self.state_tooltip.getSuitablePos())
        self.state_tooltip.show()
        
        # 创建确认对话框
        dialog = MessageBox(
            "操作确认",
            message,
            self
        )
        dialog.yesSignal.connect(self.on_confirmation_approved)
        dialog.noSignal.connect(self.on_confirmation_rejected)
        dialog.exec()

    def on_confirmation_approved(self):
        """用户确认操作"""
        self.state_tooltip.setContent("操作已确认")
        self.state_tooltip.setState(True)
        self.state_tooltip.close()
        
        # 恢复输入
        self.input_field.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.update_status("normal")
        self.need_human_intervention = False

    def on_confirmation_rejected(self):
        """用户取消操作"""
        self.state_tooltip.setContent("操作已取消")
        self.state_tooltip.setState(False)
        self.state_tooltip.close()
        # 恢复输入
        self.input_field.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.update_status("normal")
        self.need_human_intervention = False
        self.chat_display.append("系统: 用户已取消该操作")

if __name__ == '__main__':
    # 高分屏适配
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app = QApplication(sys.argv)
    window = GUIWindow()
    window.show()
    sys.exit(app.exec())