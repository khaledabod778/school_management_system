"""
نظام تحميل بسيط في الخلفية بدون تجميد الواجهة.
"""

from PyQt6.QtCore import QRunnable, QThreadPool, QObject, pyqtSignal
from typing import Callable, Optional
import traceback
import logging

logger = logging.getLogger(__name__)


class WorkerSignals(QObject):
    """إشارات العامل."""
    result = pyqtSignal(object)
    error = pyqtSignal(str)
    finished = pyqtSignal()


class AsyncWorker(QRunnable):
    """عامل تنفيذ في الخلفية."""
    
    def __init__(self, fn: Callable, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.setAutoDelete(True)
    
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(f"خطأ: {error_msg}\n{traceback.format_exc()}")
            self.signals.error.emit(error_msg)
        finally:
            self.signals.finished.emit()


def run_async(fn: Callable, *args, 
              on_result: Optional[Callable] = None,
              on_error: Optional[Callable] = None,
              on_finished: Optional[Callable] = None,
              **kwargs) -> AsyncWorker:
    """تشغيل مهمة في الخلفية."""
    worker = AsyncWorker(fn, *args, **kwargs)
    
    if on_result:
        worker.signals.result.connect(on_result)
    if on_error:
        worker.signals.error.connect(on_error)
    if on_finished:
        worker.signals.finished.connect(on_finished)
    
    QThreadPool.globalInstance().start(worker)
    return worker