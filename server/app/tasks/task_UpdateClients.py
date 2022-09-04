import threading
import time
from multiprocessing.pool import ThreadPool
import random
from pyhtmlgui import Observable

from app.devices.devices import DevicesInstance
from settings import SettingsInstance
from views.imageCarousel.imageCarouselLive import PreviewQueueInstance

class Task_UpdateClients(Observable):
    def __init__(self):
        super().__init__()
        self.name = "UpdateClients"
        self.status = "idle"
        self.percent_done = 0
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
        self.percent_done = 0
        self.set_status("deploying")
        devices = [c for c in DevicesInstance().devices if c.status != "installing"]

        ld = len(devices)
        if ld == 0:
            self.set_status("idle")
            return

        with ThreadPool(15) as p:
            r = p.map_async(lambda device: device._deploy(), devices)
            for i in range(20):
                self.percent_done = int((100 / ld) * len([c for c in devices if c.status == "installing"]))
                self.set_status("deploying")
                if self.percent_done > 95:
                    break
                time.sleep(1)
            self.set_status("installing")
            r.wait()
        time.sleep(60)

        self.set_status("idle")
        self.worker = None
        
        
_taskUpdateClientsInstance = None
def TaskUpdateClientsInstance():
    global _taskUpdateClientsInstance
    if _taskUpdateClientsInstance is None:
        _taskUpdateClientsInstance = Task_UpdateClients()
    return _taskUpdateClientsInstance
