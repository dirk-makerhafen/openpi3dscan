from pyhtmlgui import Observable
from app.devices.devices import DevicesInstance
from app.files.shots import ShotsInstance
from app.tasks.tasks import TasksInstance
from app.cardreader.cardReader import CardReaderInstance
from app.files.usbDisks import UsbDisks
import os
from app.settings.settings import SettingsInstance
import time

class App(Observable):
    def __init__(self):
        super().__init__()
        self.status = "active"
        self.devices = DevicesInstance()
        self.settings = SettingsInstance(DevicesInstance())
        self.shots_remote = ShotsInstance(self.devices)
        self.usbDisks = UsbDisks()
        self.tasks = TasksInstance()
        self.cardReader = CardReaderInstance()

    def reboot(self):
        self.status = "reboot"
        self.notify_observers()
        time.sleep(3)
        os.system("sudo reboot &")

    def shutdown(self):
        self.status = "shutdown"
        self.notify_observers()
        time.sleep(3)
        os.system("sudo shutdown -h now &")


_appInstance = None


def AppInstance():
    global _appInstance
    if _appInstance is None:
        _appInstance = App()
    return _appInstance
