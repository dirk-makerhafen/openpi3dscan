import json
from pyhtmlgui import Observable

from app_windows.settings.settingsCache import SettingsCache
from app_windows.settings.settingsLocations import SettingsLocations
from app_windows.settings.settingsRealityCapture import SettingsRealityCapture
from app_windows.settings.settingsRemoteHosts import SettingsRemoteHosts

VERSION = "2022.11.24-08.09"


class Settings(Observable):
    def __init__(self):
        super().__init__()
        self.realityCaptureSettings = SettingsRealityCapture(self)
        self.settingsLocations = SettingsLocations(self)
        self.settingsRemoteHosts = SettingsRemoteHosts(self)
        self.settingsCache = SettingsCache(self)
        self.VERSION = VERSION
        self.load()

    def save(self):
        data = {
            "realityCaptureSettings" : self.realityCaptureSettings.to_dict(),
            "settingsLocations" : self.settingsLocations.to_dict(),
            "settingsRemoteHosts" : self.settingsRemoteHosts.to_dict(),
            "settingsCache" : self.settingsCache.to_dict(),
        }
        open("windows.json", "w").write(json.dumps(data))

    def load(self):
        try:
            data = open("windows.json", "r").read()
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

        self.save()
        self.notify_observers()


_settingsInstance = None


def SettingsInstance(devicesInstance=None):
    global _settingsInstance
    if _settingsInstance is None:
        _settingsInstance = Settings()
    return _settingsInstance
