import json, os
from pyhtmlgui import Observable

from app_windows.settings.settingsCache import SettingsCache
from app_windows.settings.settingsDropbox import SettingsDropboxWindows
from app_windows.settings.settingsLocations import SettingsLocations
from app_windows.settings.settingsRealityCapture import SettingsRealityCapture
from app_windows.settings.settingsRemoteHosts import SettingsRemoteHosts

VERSION = "2023.06.27-00.09"


class Settings(Observable):
    def __init__(self):
        super().__init__()
        self.save_dir = os.path.join(os.environ["APPDATA"], "RCAutomation")
        if not os.path.exists(self.save_dir):
            os.mkdir(self.save_dir)
        self.save_file = os.path.join(self.save_dir, "settings.json")
        self.realityCaptureSettings = SettingsRealityCapture(self)
        self.settingsLocations = SettingsLocations(self)
        self.settingsRemoteHosts = SettingsRemoteHosts(self)
        self.settingsCache = SettingsCache(self)
        self.settingsDropbox = SettingsDropboxWindows(self)
        self.VERSION = VERSION
        self.load()

    def save(self):
        data = {
            "realityCaptureSettings" : self.realityCaptureSettings.to_dict(),
            "settingsLocations" : self.settingsLocations.to_dict(),
            "settingsRemoteHosts" : self.settingsRemoteHosts.to_dict(),
            "settingsCache" : self.settingsCache.to_dict(),
            "settingsDropbox" : self.settingsDropbox.to_dict(),
        }
        open(self.save_file, "w").write(json.dumps(data))

    def load(self):
        try:
            data = open(self.save_file, "r").read()
            data = json.loads(data)
        except Exception as e:
            print("error loading settings:", e)
            return
        try:
            self.realityCaptureSettings.from_dict(data["realityCaptureSettings"])
        except:
            pass
        try:
            self.settingsLocations.from_dict(data["settingsLocations"])
        except:
            pass
        try:
            self.settingsRemoteHosts.from_dict(data["settingsRemoteHosts"])
        except:
            pass
        try:
            self.settingsCache.from_dict(data["settingsCache"])
        except:
            pass
        try:
            self.settingsDropbox.from_dict(data["settingsDropbox"])
        except:
            pass
        self.save()
        self.notify_observers()


_settingsInstance = None


def SettingsInstance(devicesInstance=None):
    global _settingsInstance
    if _settingsInstance is None:
        _settingsInstance = Settings()
    return _settingsInstance
