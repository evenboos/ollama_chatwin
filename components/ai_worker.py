from PyQt6.QtCore import QObject, pyqtSignal, QThreadPool, QRunnable, QThread
import ollama

class AIWorker(QObject):
    charReceived = pyqtSignal(str)
    finished = pyqtSignal()
    requireHumanInput = pyqtSignal(str)

    def __init__(self, model_name):
        super().__init__()
        self.model_name = model_name
        self._active = False

    def process_prompt(self, prompt):
        self._active = True
        try:
            # 模拟需要人工介入的情况
            if "删除" in prompt:
                self.requireHumanInput.emit("需要确认删除操作")
                return
            
            # 调用 Ollama API 进行聊天
            stream = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                stream=True
            )
            
            for chunk in stream:
                if not self._active:
                    break
                content = chunk['message']['content']
                for char in content:
                    if not self._active:
                        break
                    self.charReceived.emit(char)
                    QThread.msleep(50)  # 控制字符发送速度
        except Exception as e:
            self.charReceived.emit(f"错误: {str(e)}")
        finally:
            self.finished.emit()

    def cancel(self):
        self._active = False

class AIRequest(QRunnable):
    def __init__(self, worker, prompt):
        super().__init__()
        self.worker = worker
        self.prompt = prompt

    def run(self):
        self.worker.process_prompt(self.prompt) 