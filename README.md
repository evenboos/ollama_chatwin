# Ollama ChatWin

一个基于 PyQt6 和 Ollama 开发的智能助手桌面应用程序，集成了实时视频显示和 AI 对话功能。

## 功能特点

- **双面板设计**
  - 左侧聊天面板：支持与 AI 助手实时对话
  - 右侧视频面板：实时显示摄像头画面

- **AI 对话功能**
  - 基于 Ollama 的 qwen2.5:7b 模型
  - 支持实时字符流式响应
  - 多轮对话队列管理
  - 智能状态管理和错误处理

- **视频功能**
  - 实时摄像头画面显示
  - 自适应窗口大小调整
  - 支持 16:9/3:2 等多种显示比例
  - 流畅的视频帧更新（30fps）

- **界面特性**
  - 现代化 Fluent 设计风格
  - 圆角窗口边框
  - 响应式布局
  - 状态栏实时显示
  - 支持高分屏显示

## 技术栈

- Python 3.x
- PyQt6
- OpenCV (cv2)
- Ollama
- QFluentWidgets

## 安装依赖

```bash
pip install PyQt6 opencv-python ollama qfluentwidgets
```

## 运行方式

```bash
python gui.py
```

## 主要组件

- **GUIWindow**: 主窗口类，继承自 FluentWindow
- **VideoHandler**: 视频处理类，负责摄像头画面捕获和显示
- **AIWorker**: AI 对话处理类，负责与 Ollama 模型交互
- **StatusManager**: 状态管理类，处理应用程序各种状态
- **InputHandler**: 输入处理类，处理用户输入

## 功能说明

1. **对话功能**
   - 支持多轮对话
   - 实时字符显示
   - 自动滚动到最新消息
   - 支持回车发送

2. **视频功能**
   - 自动检测并初始化摄像头
   - 支持视频画面实时缩放
   - 平滑的画面更新

3. **界面交互**
   - 状态实时显示
   - 错误提示
   - 人工确认对话框
   - 窗口拖动时自动暂停更新

## 注意事项

- 需要确保系统已安装摄像头设备
- 需要预先安装 Ollama 并下载相应的模型
- 建议在支持硬件加速的环境下运行

## 开发计划

- [ ] 添加更多 AI 模型支持
- [ ] 优化视频处理性能
- [ ] 添加录制功能
- [ ] 支持更多自定义设置

## 许可证

[MIT License](LICENSE)