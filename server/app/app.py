from pyhtmlgui import Observable
from app.devices.devices import DevicesInstance
from app.shots import ShotsInstance
from app.tasks.tasks import TasksInstance
from app.cardReader import CardReaderInstance
from settings import SettingsInstance

class App(Observable):
    def __init__(self):
        super().__init__()
        self.devices = DevicesInstance()
        self.shots_remote = ShotsInstance(self.devices)
        self.tasks = TasksInstance()
        self.cardReader = CardReaderInstance()
        self.settings = SettingsInstance(DevicesInstance())
