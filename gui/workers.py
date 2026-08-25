"""异步任务 Worker 模块"""

import io
from contextlib import redirect_stdout
from PySide6.QtCore import QThread, Signal


class ScraperWorker(QThread):
    """抓取/提取任务后台线程"""
    log_message = Signal(str)
    finished_ok = Signal(bool, str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._interrupted = False

    def request_interruption(self):
        """请求中断任务"""
        self._interrupted = True
        super().requestInterruption()

    def is_interrupted(self) -> bool:
        return self._interrupted

    def run(self):
        log_buffer = io.StringIO()
        try:
            with redirect_stdout(log_buffer):
                self.func(*self.args, **self.kwargs)

            for line in log_buffer.getvalue().split('\n'):
                if line.strip():
                    self.log_message.emit(line)

            if self._interrupted:
                self.finished_ok.emit(False, "用户中断")
            else:
                self.finished_ok.emit(True, "任务完成")
        except Exception as e:
            self.log_message.emit(f"[ERROR] {e}")
            self.finished_ok.emit(False, str(e))
