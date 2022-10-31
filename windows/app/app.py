from pyhtmlgui import Observable
from app.files.shots import ShotsInstance
import os
from app.settings.settings import SettingsInstance
import time

from realityCapture.process import Processing


class App(Observable):
    def __init__(self):
        super().__init__()
        self.status = "active"
        self.settings = SettingsInstance()
        self.processing = Processing()
        self.shots_remote = ShotsInstance()


_appInstance = None


def AppInstance():
    global _appInstance
    if _appInstance is None:
        _appInstance = App()
    return _appInstance
