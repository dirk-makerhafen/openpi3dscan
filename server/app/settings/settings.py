import json
from pyhtmlgui import Observable

from app.settings.settingsCameras import SettingsCameras
from app.settings.settingsFirmware import SettingsFirmwareImage
from app.settings.settingsHostname import SettingsHostname
from app.settings.settingsPrinters import SettingsPrinters
from app.settings.settingsScanner import SettingsScanner
from app.settings.settingsSequence import SettingsSequence
from app.settings.settingsWireless import SettingsWireless
from app.settings.settingsDropbox import SettingsDropbox
from app.settings.settingsRealityCapture import SettingsRealityCapture

VERSION = "2024.02.23-12:20"

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
        self.settingsPrinters = SettingsPrinters(self)
        self.VERSION = VERSION
        self.locked = False
        self.password = ""
        self.primary_disk = ""
        self.load()


    def to_dict(self):
        return {
            "sequenceSettingsSpeed" : self.sequenceSettingsSpeed.to_dict(),
            "sequenceSettingsQuality" : self.sequenceSettingsQuality.to_dict(),
            "cameraSettings"   : self.cameraSettings.to_dict(),
            "firmwareSettings" : self.firmwareSettings.to_dict(),
            "wirelessSettings" : self.wirelessSettings.to_dict(),
            "hostnameSettings" : self.hostnameSettings.to_dict(),
            "realityCaptureSettings" : self.realityCaptureSettings.to_dict(),
            "settingsScanner"  : self.settingsScanner.to_dict(),
            "settingsDropbox"  : self.settingsDropbox.to_dict(),
            "settingsPrinters" : self.settingsPrinters.to_dict(),
            "locked"           : self.locked,
            "password"         : self.password,
            "primary_disk"     : self.primary_disk,
        }

    def save(self):
        open("/opt/openpi3dscan/.openpi3dscan.json", "w").write(json.dumps(self.to_dict()))

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
        try:
            self.settingsPrinters.from_dict(data["settingsPrinters"])
        except:
            pass
        try:
            self.locked = data["locked"]
            self.password = data["password"]
            self.primary_disk = data["primary_disk"]
        except:
            pass

        self.save()
        self.notify_observers()

    def set_primary_disk(self, disk_uuid):
        self.primary_disk = disk_uuid
        self.save()
        self.notify_observers()

    def lock(self, password):
        self.locked = True
        self.password = password
        self.save()
        self.notify_observers()

    def unlock(self, password):
        if self.password == password:
            self.locked = False
            self.save()
            self.notify_observers()

_settingsInstance = None


def SettingsInstance(devicesInstance=None):
    global _settingsInstance
    if _settingsInstance is None:
        _settingsInstance = Settings(devicesInstance)
    return _settingsInstance
