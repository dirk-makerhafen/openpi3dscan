import json
from pyhtmlgui import Observable

from app.settings.settingsCameras import SettingsCameras
from app.settings.settingsFirmware import SettingsFirmwareImage
from app.settings.settingsHostname import SettingsHostname
from app.settings.settingsScanner import SettingsScanner
from app.settings.settingsSequence import SettingsSequence
from app.settings.settingsWireless import SettingsWireless
from app.settings.settingsDropbox import SettingsDropbox
from app.settings.settingsRealityCapture import SettingsRealityCapture

VERSION = "2022.11.28-00.05"


class Settings(Observable):
    def __init__(self, devicesInstance):
        super().__init__()
        self.devicesInstance = devicesInstance
        self.sequenceSettingsSpeed = SettingsSequence(self)
        self.sequenceSettingsQuality = SettingsSequence(self)
        self.cameraSettings = SettingsCameras(self)
        self.firmwareSettings = SettingsFirmwareImage(self)
        self.wirelessSettings = SettingsWireless(self)
        self.hostnameSettings = SettingsHostname(self)
        self.realityCaptureSettings = SettingsRealityCapture(self)
        self.settingsScanner = SettingsScanner(self)
        self.settingsDropbox = SettingsDropbox(self)
        self.VERSION = VERSION
        self.load()

    def save(self):
        data = {
            "sequenceSettingsSpeed" : self.sequenceSettingsSpeed.to_dict(),
            "sequenceSettingsQuality" : self.sequenceSettingsQuality.to_dict(),
            "cameraSettings" : self.cameraSettings.to_dict(),
            "firmwareSettings" : self.firmwareSettings.to_dict(),
            "wirelessSettings" : self.wirelessSettings.to_dict(),
            "hostnameSettings" : self.hostnameSettings.to_dict(),
            "realityCaptureSettings" : self.realityCaptureSettings.to_dict(),
            "settingsScanner" : self.settingsScanner.to_dict(),
            "settingsDropbox" : self.settingsDropbox.to_dict()
        }
        open("/opt/openpi3dscan/.openpi3dscan.json", "w").write(json.dumps(data))

    def load(self):
        try:
            data = open("/opt/openpi3dscan/.openpi3dscan.json", "r").read()
            data = json.loads(data)
        except Exception as e:
            print("error loading settings:", e)
            return
        try:
            self.sequenceSettingsSpeed.from_dict(data["sequenceSettingsSpeed"])
        except:
            pass
        try:
            self.sequenceSettingsQuality.from_dict(data["sequenceSettingsQuality"])
        except:
            pass
        try:
            self.cameraSettings.from_dict(data["cameraSettings"])
        except:
            pass
        try:
            self.firmwareSettings.from_dict(data["firmwareSettings"])
        except:
            pass
        try:
            self.wirelessSettings.from_dict(data["wirelessSettings"])
        except:
            pass
        try:
            self.hostnameSettings.from_dict(data["hostnameSettings"])
        except:
            pass
        try:
            self.realityCaptureSettings.from_dict(data["realityCaptureSettings"])
        except:
            pass
        try:
            self.settingsScanner.from_dict(data["settingsScanner"])
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
        _settingsInstance = Settings(devicesInstance)
    return _settingsInstance
