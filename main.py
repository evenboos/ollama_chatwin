import sys
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThreadPool
from PyQt6.QtGui import QPixmap, QColor, QPainter,QFont
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QScrollArea, QPushButton, QSizePolicy)
from qfluentwidgets import (FluentWindow, NavigationItemPosition, 
                           NavigationPushButton, PrimaryPushButton, 
                           BodyLabel, ScrollArea, isDarkTheme,FluentIcon,MSFluentWindow,TextEdit)
from gui import GUIWindow
from shared_styles import *
from components.preview_card import PreviewCard
from components.ai_worker import AIWorker
from components.status_bar import StatusBar

# 自定义预览卡片组件
class PreviewCard(QWidget):
    # 定义跳转信号
    jumpRequested = pyqtSignal()

    def __init__(self, title, parent=None):
        super().__init__(parent)
        # 增加卡片尺寸以显示更多内容
        self.setFixedSize(400, 700)  
        self.title = title
        self.gui_window = None
        self.update_timer = QTimer()
        self.update_timer.setInterval(5000)  # 改为5秒
        self.update_timer.timeout.connect(self.updateThumbnail)
        self.last_content = ""  # 添加上次内容记录
        self.initUI()
        self.setStyleSheet(STYLES["preview_card"])

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # 标题栏
        title_layout = QHBoxLayout()
        self.title_label = BodyLabel(self.title, self)
        self.status_label = BodyLabel("未运行", self)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.status_label)

        # 聊天内容预览区域
        self.chat_preview = TextEdit()
        self.chat_preview.setReadOnly(True)  # 启用只读
        self.chat_preview.setStyleSheet(STYLES["chat_display"])
        self.chat_preview.setMinimumHeight(600)
        self.chat_preview.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.chat_preview.setStyleSheet("""
            TextEdit {
                background-color: #F4F8FF;
                border: 2px solid #C0D8E0;
                border-radius: 8px;
                padding: 10px;
                font-family: Microsoft YaHei;
                font-size: 12px;
            }
        """)

        # 操作按钮
        self.jump_btn = PrimaryPushButton("打开界面")
        self.jump_btn.setStyleSheet("""
            PrimaryPushButton {
                background-color: #6BA8FF;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                min-height: 32px;
            }
            PrimaryPushButton:hover {
                background-color: #5B98E6;
            }
        """)
        self.jump_btn.clicked.connect(self.onJumpClicked)

        layout.addLayout(title_layout)
        layout.addWidget(self.chat_preview)
        layout.addWidget(self.jump_btn)

    def updateThumbnail(self):
        """更新聊天内容预览"""
        if not self.gui_window:
            return
            
        try:
            # 获取完整的聊天记录
            content = self.gui_window.get_dialog_content()
            
            # 检查内容是否发生变化
            if content and content != self.last_content:
                # 保存滚动条位置
                scrollbar = self.chat_preview.verticalScrollBar()
                was_at_bottom = scrollbar.value() == scrollbar.maximum()
                
                # 更新内容
                self.chat_preview.setText(content)
                self.last_content = content
                
                # 根据之前的位置决定是否滚动
                if was_at_bottom:
                    scrollbar.setValue(scrollbar.maximum())
                    
            # 更新状态标签
            if self.gui_window.isVisible():
                self.status_label.setText("运行中")
            else:
                self.status_label.setText("已最小化")
                
        except Exception as e:
            print(f"更新预览内容时出错: {str(e)}")
            self.status_label.setText("更新错误")

    def startUpdates(self):
        """开始更新"""
        if not self.update_timer.isActive():
            self.update_timer.start()

    def stopUpdates(self):
        """停止更新"""
        if self.update_timer.isActive():
            self.update_timer.stop()

    def showEvent(self, event):
        """显示事件处理"""
        super().showEvent(event)
        self.startUpdates()

    def hideEvent(self, event):
        """隐藏事件处理"""
        super().hideEvent(event)
        self.stopUpdates()

    def onJumpClicked(self):
        """点击打开界面"""
        if self.gui_window and self.gui_window.isVisible():
            self.gui_window.activateWindow()
            self.gui_window.raise_()
        else:
            self.jumpRequested.emit()
            # 移除这里的 timer.stop()，让计时器持续运行

    # 删除重复的 showEvent 定义，只保留这一个
    def showEvent(self, event):
        """显示事件处理"""
        super().showEvent(event)
        self.startUpdates()  # 使用统一的启动方法

    def drawPreview(self, content):
        # 使用与 GUIWindow 相同的字体和颜色
        painter = QPainter(self.thumbnail.pixmap())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if content:
            painter.setPen(QColor(PRIMARY_COLOR))
            painter.setFont(QFont("Microsoft YaHei", 10))
            text_rect = self.thumbnail.rect().adjusted(10, 10, -10, -10)  # 增加边距
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, content)
        
        # 统一绘制边框
        painter.setPen(Qt.GlobalColor.darkGray)
        painter.drawRect(0, 0, 269, 139)
        
        # 绘制文本
        text_rect = self.thumbnail.rect().adjusted(10, 10, -10, -10)
        painter.setPen(QColor(PRIMARY_COLOR))
        painter.setFont(QFont("Microsoft YaHei", 10))
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, content)
        
        painter.end()
        self.thumbnail.setPixmap(self.thumbnail.pixmap())

    def mouseDoubleClickEvent(self, event):
        """双击事件处理"""
        self.jumpRequested.emit()
        event.accept()

    def onJumpClicked(self):
        self.update_timer.stop()  # 激活时停止更新
        self.jumpRequested.emit()

    def showEvent(self, event):
        self.update_timer.start()

    def testUpdate(self):
        """测试更新功能"""
        print(f"\n=== {self.title} 测试报告 ===")
        print(f"计时器状态: {'活跃' if self.update_timer.isActive() else '停止'}")
        print(f"计时器间隔: {self.update_timer.interval()}ms")
        if self.gui_window:
            content = self.gui_window.get_dialog_content()
            print(f"GUI窗口内容长度: {len(content) if content else 0}")
            print(f"当前显示内容长度: {len(self.last_content)}")
            print(f"内容是否相同: {content == self.last_content}")
        else:
            print("GUI窗口未创建")

# 主界面类
class MainWindow(MSFluentWindow):
    def __init__(self):
        super().__init__()
        self.thread_pool = QThreadPool.globalInstance()  # 使用全局线程池
        self.setWindowTitle("智能助手主界面")
        self.resize(1200, 800)
        self.setStyleSheet(f"""
            MSFluentWindow {{
                background-color: {MAIN_BG};
            }}
        """)
        
        # 初始化组件
        self.preview_cards = []  # 存储所有预览卡片
        self.gui_windows = []    # 存储所有子界面实例
        
        # 创建主展示区域
        self.mainInterface = QWidget()
        self.mainInterface.setObjectName("mainInterface")
        self.initMainInterface()
        self.addSubInterface(
            self.mainInterface,
            FluentIcon.HOME,
            '主界面',
            position=NavigationItemPosition.TOP
        )

        # 添加导航按钮
        self.addNavigationButtons()

        # 在 MainWindow 初始化中添加
        self.titleBar.setStyleSheet(f"""
            TitleBar {{
                background-color: {TITLE_BG};
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }}
        """)

        self.navigationInterface.setStyleSheet(f"""
            NavigationPanel {{
                background-color: {NAV_BG};
                border-radius: 8px;
                margin: 10px;
            }}
            NavigationItemWidget {{
                color: black;
                padding: 8px;
            }}
        """)

    def initMainInterface(self):
        """初始化主展示区域"""
        scroll = ScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.card_container = QWidget()
        self.card_layout = QHBoxLayout()
        self.card_layout.setContentsMargins(30, 30, 30, 30)
        self.card_layout.setSpacing(30)
        self.card_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        self.card_container.setLayout(self.card_layout)
        scroll.setWidget(self.card_container)
        
        # 修复：将浮点数转换为整数
        scroll.wheelEvent = lambda event: scroll.horizontalScrollBar().setValue(
            scroll.horizontalScrollBar().value() + int(event.angleDelta().y() / 2)
        )
        
        layout = QVBoxLayout(self.mainInterface)
        layout.addWidget(scroll)
        layout.setContentsMargins(0, 0, 0, 0)

    def addNavigationButtons(self):
        """添加侧边栏导航按钮"""
        add_btn = NavigationPushButton(
            FluentIcon.ADD,
            '添加界面',
            isSelectable=False
        )
        add_btn.clicked.connect(self.addPreviewCard)
        self.navigationInterface.addWidget(
            routeKey="add_button",
            widget=add_btn,
            onClick=None,
            position=NavigationItemPosition.TOP
        )
    def addPreviewCard(self):
        """添加新的预览卡片"""
        card = PreviewCard(f"界面 {len(self.preview_cards)+1}")
        card.jumpRequested.connect(lambda: self.lazyLoadGUI(card))
        self.preview_cards.append(card)
        self.card_layout.addWidget(card)
        
    #    # 添加测试按钮
    #    test_btn = PrimaryPushButton("测试状态")
    #    test_btn.clicked.connect(card.testUpdate)
    #    card.layout().addWidget(test_btn)
        
        # 更新缩略图（示例）
        card.updateThumbnail()

    def lazyLoadGUI(self, card):
        """按需加载GUI窗口"""
        if not card.gui_window:
            card.gui_window = GUIWindow()
            card.gui_window.hide()
        self.showGUIWindow(card.gui_window)
        card.startUpdates()  # 确保计时器启动

    def showGUIWindow(self, window):
        """显示或激活子界面"""
        if window.isHidden():
            window.show()
        else:
            window.activateWindow()
            window.raise_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())