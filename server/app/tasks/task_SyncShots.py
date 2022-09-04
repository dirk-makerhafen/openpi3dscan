import threading
import time
from multiprocessing.pool import ThreadPool

from pyhtmlgui import Observable

from app.devices.devices import DevicesInstance
from app.shots import ShotsInstance
from settings import SettingsInstance

class Task_SyncShots(Observable):
    def __init__(self):
        super().__init__()
        self.name = "Sync Shots"
        self.status = "idle"
        self.worker = None


    def set_status(self, value):
        self.status = value
        self.notify_observers()

    def run(self):
        if self.worker is None:
            self.worker = threading.Thread(target=self._run, daemon=True)
            self.worker.start()

    def _run(self):
        if self.status != "idle":
            return
        self.set_status("list")
        cameras = DevicesInstance().cameras.list()

        cameras = [c for c in cameras if c.status == "online"]
        with ThreadPool(20) as p:
            p.map(lambda device: device.camera.shots._refresh_list(), cameras)

        self.set_status("shots")
        with ThreadPool(5) as p:
            p.map(lambda shot: shot._sync_remote(), ShotsInstance().shots)

        self.set_status("idle")
        self.worker = None

        
_taskSyncShotsInstance = None
def TaskSyncShotsInstance():
    global _taskSyncShotsInstance
    if _taskSyncShotsInstance is None:
        _taskSyncShotsInstance = Task_SyncShots()
    return _taskSyncShotsInstance
