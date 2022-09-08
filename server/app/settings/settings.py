import json
from pyhtmlgui import Observable

from app.settings.settings_cameras import Settings_Cameras
from app.settings.settings_firmware import Settings_FirmwareImage
from app.settings.settings_hostname import Settings_Hostname
from app.settings.settings_sequence import Settings_Sequence
from app.settings.settings_wireless import Settings_Wireless

VERSION = "2022.09.08-17.00"


class Settings(Observable):
    def __init__(self, devicesInstance):
        super().__init__()
        self.devicesInstance = devicesInstance
        self.sequenceSettingsSpeed = Settings_Sequence(self)
        self.sequenceSettingsQuality = Settings_Sequence(self)
        self.cameraSettings = Settings_Cameras(self)
        self.firmwareSettings = Settings_FirmwareImage(self)
        self.wirelessSettings = Settings_Wireless(self)
        self.hostnameSettings = Settings_Hostname(self)
        self.VERSION = VERSION
        self.load()

    def save(self):
        data = {
            "sequenceSettingsSpeed" : self.sequenceSettingsSpeed.to_dict(),
            "sequenceSettingsQuality" : self.sequenceSettingsQuality.to_dict(),
            "cameraSettings" : self.cameraSettings.to_dict(),
            "firmwareSettings" : self.firmwareSettings.to_dict(),
            "wirelessSettings" : self.wirelessSettings.to_dict(),
            "hostnameSettings" : self.hostnameSettings.to_dict()
        }
        open("/opt/openpi3dscan/.openpi3dscan.json","w").write(json.dumps(data))

    def load(self):
        try:
            data = open("/opt/openpi3dscan/.openpi3dscan.json", "r").read()
            data = json.loads(data)
            self.sequenceSettingsSpeed.from_dict(data["sequenceSettingsSpeed"])
            self.sequenceSettingsQuality.from_dict(data["sequenceSettingsQuality"])
            self.cameraSettings.from_dict(data["cameraSettings"])
            self.firmwareSettings.from_dict(data["firmwareSettings"])
            self.wirelessSettings.from_dict(data["wirelessSettings"])
            self.hostnameSettings.from_dict(data["hostnameSettings"])
        except Exception as e:
            print("error loading settings:", e)
        self.save()
        self.notify_observers()


_settingsInstance = None
def SettingsInstance(devicesInstance = None):
    global _settingsInstance
    if _settingsInstance is None:
        _settingsInstance = Settings(devicesInstance)
    return _settingsInstance
