from pyhtmlgui import Observable
from app_windows.files.shots import ShotsInstance
from app_windows.files.shotsDropboxDownload import ShotsDropboxDownloadInstance
from app_windows.settings.settings import SettingsInstance
from app_windows.processing import Processing

class App(Observable):
    def __init__(self):
        super().__init__()
        print("init app")
        self.status = "active"
        self.settings = SettingsInstance(None)
        self.shotsDropboxDownload = ShotsDropboxDownloadInstance()
        self.processing = Processing()
        self.shots = ShotsInstance()

_appInstance = None

def AppInstance():
    global _appInstance
    if _appInstance is None:
        _appInstance = App()
    return _appInstance
