import queue
import threading
from .task_ColorCalibrate import Task_ColorCalibrate
from pyhtmlgui import Observable


class Tasks(Observable):
    def __init__(self):
        super().__init__()
        self.task_queue = queue.Queue()
        self.current_task = None
        self.t = threading.Thread(target=self._loop, daemon=True)
        self.t.start()

    def _loop(self):
        while True:
            self.current_task = self.task_queue.get()
            self.notify_observers()
            self.current_task.run()
            self.current_task = None
            self.notify_observers()

    def color_calibrate(self):
        self.task_queue.put(Task_ColorCalibrate())


_tasksInstance = None


def TasksInstance():
    global _tasksInstance
    if _tasksInstance is None:
        _tasksInstance = Tasks()
    return _tasksInstance
