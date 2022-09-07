from pyhtmlgui import Observable
from app.devices.devices import DevicesInstance
from app.shots import ShotsInstance
from app.tasks.tasks import TasksInstance
from app.cardReader import CardReaderInstance
from app.usbDisks import UsbDisks
import os
from settings import SettingsInstance

class App(Observable):
    def __init__(self):
        super().__init__()
        self.status = "active"
        self.usbDisks = UsbDisks()
        self.devices = DevicesInstance()
        self.shots_remote = ShotsInstance(self.devices)
        self.tasks = TasksInstance()
        self.cardReader = CardReaderInstance()
        self.settings = SettingsInstance(DevicesInstance())

    def reboot(self):
        self.status = "reboot"
        self.notify_observers()
        os.system("sudo reboot &")

    def shutdown(self):
        self.status = "shutdown"
        self.notify_observers()
        os.system("sudo shutdown -h now &")

_appInstance = None
def AppInstance():
    global _appInstance
    if _appInstance is None:
        _appInstance = App()
    return _appInstance
