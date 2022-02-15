from datetime import datetime
import queue
import logging

from PyQt6 import QtCore

__author__ = "Nikolay Golub (nikolay.v.golub@gmail.com)"
__copyright__ = "Copyright 2012 - 2018, Nikolay Golub"
__license__ = "GPL"

logger = logging.getLogger(__name__)


class BaseThread(QtCore.QThread):
    """Base class for thread in pyjtt. Not used directly"""
    exception_raised = QtCore.pyqtSignal(Exception)
    task_started = QtCore.pyqtSignal()
    task_done = QtCore.pyqtSignal()
    sleep_timeout = 200

    def __init__(self, tasks_queue):
        """Initializes tasks_queue and statuses.

        """
        super(BaseThread, self).__init__()
        self.queue = tasks_queue

    def _run(self, func):
        """Should be implemented in child classes."""
        raise NotImplementedError

    def run(self):
        """Prepares execution and handles status messages."""
        while True:
            try:
                job = self.queue.get()
                self.task_started.emit()
                self._run(job)
            except queue.Empty:
                pass
            except Exception as exc:
                logger.error('Exception "{msg}" '
                             'raised in thread'
                             ' {thread}'.format(thread=self.currentThreadId(),
                                                msg=str(exc)))
                self.exception_raised.emit(exc)
            finally:
                self.task_done.emit()
                self.msleep(self.sleep_timeout)


class NoResultThread(BaseThread):
    """Simple thread for I/O operations which don't return anything"""

    def __init__(self, queue_instance):
        logger.info('Initialize simple I/O thread')
        super(NoResultThread, self).__init__(queue_instance)
        logger.debug('I/O thread initialized')

    def _run(self, func):
        logger.debug('Start I/O function')
        func()
        self.task_done.emit()


class TrackingWorker(QtCore.QThread):
    """Thread for tracking timer.

    It is created when time starts and ended when timer stops.
    It wakes up every self.sleep_timeout seconds
    """
    timer_updated = QtCore.pyqtSignal(int)

    sleep_timeout = 300

    def __init__(self, parent=None):
        super(TrackingWorker, self).__init__(parent)
        logger.debug('Initialize timer')
        self.delta = 0
        self.is_tracking = False
        self.started = None

    def run(self):
        self.started = datetime.now()
        while True:
            spent_seconds = (datetime.now() - self.started).total_seconds()
            self.timer_updated.emit(int(round(spent_seconds)))
            self.msleep(self.sleep_timeout)
