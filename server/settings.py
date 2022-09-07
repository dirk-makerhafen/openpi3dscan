import json
import subprocess
import threading
import time
from pyhtmlgui import Observable
import glob
import os
devicesInstance = None
VERSION = "2022.09.06-03.10"


class Settings_Wireless(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.save = parent.save
        self.ssid = ""
        self.password = ""
        self.status = "not_connected"
        self.ip = ""
        self.apply_worker = None
        self.status_worker = None

        self.get_connection_status()

    def set_status(self, status):
        self.status = status
        self.notify_observers()

    def to_dict(self):
        return {
            "ssid" : self.ssid,
            "password" : self.password,
        }
    def from_dict(self, data):
        self.ssid = data["ssid"]
        self.password = data["password"]

    def apply(self,ssid, password):
        if self.apply_worker is not None:
            return
        if ssid == self.ssid and password == self.password:
            return
        self.ssid = ssid
        self.password = password
        self.save()

        self.apply_worker = threading.Thread(target=self._apply, daemon=True)
        self.apply_worker.start()

    def _apply(self):
        t = '''
country=de
update_config=1
ctrl_interface=/var/run/wpa_supplicant
network={
    scan_ssid=1
    ssid="%s"
    psk="%s"
}
        ''' % (self.ssid, self.password)
        open("/etc/wpa_supplicant/wpa_supplicant.conf","w").write(t)
        self.set_status("configure")
        subprocess.call("sudo wpa_cli -i wlan0 reconfigure", shell=True)
        self.set_status("connecting")
        subprocess.call("sudo systemctl restart wpa_supplicant", shell=True)
        time.sleep(8)
        self.get_connection_status()
        self.apply_worker = None

    def get_connection_status(self):
        if self.status_worker is not None:
            return
        self.status_worker = threading.Thread(target=self._get_connection_status, daemon=True)
        self.status_worker.start()

    def _get_connection_status(self):
        self.set_status("checking")
        time.sleep(2)
        try:
            stdout = subprocess.check_output("ifconfig wlan0|grep -i inet", shell=True, timeout=10, stderr=subprocess.STDOUT).decode("UTF-8")
            if "192.168" in stdout:
                self.ip = "192.168%s" % (stdout.split("192.168")[1].split(" ")[0])
                self.set_status("connected")
            else:
                self.ip = ""
                self.set_status("not_connected")
        except Exception as e:
            self.ip = ""
            self.set_status("not_connected")
        self.status_worker = None


class Settings_FirmwareImage(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.save = parent.save
        self.current_image = ""
        self.image_files = []
        self.load()

    def set_image(self, value):
        self.current_image = value
        if self.current_image not in self.image_files and len( self.image_files) > 0:
            self.current_image = self.image_files[-1]

    def delete_image(self, image):
        img_path = os.path.join("/opt/openpi3dscan/firmware/", image )
        if os.path.exists(img_path):
            os.remove(img_path)
            self.load()

    def load(self):
        self.image_files = [f.replace("/opt/openpi3dscan/firmware/","") for f in glob.glob("/opt/openpi3dscan/firmware/*.img")]
        self.image_files.sort()
        if self.current_image not in self.image_files and len( self.image_files) > 0:
            self.current_image = self.image_files[-1]
        self.notify_observers()

    def to_dict(self):
        return {
            "current_image" : self.current_image,
        }
    def from_dict(self, data):
        self.current_image = data["current_image"]
        self.load()

class Settings_SequenceImage(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.save = parent.save
        self._projection = False
        self._light = 0
        self._offset = 0

    def _get_projection(self):
        return self._projection
    def _set_projection(self, value):
        value = bool(value)
        self._projection = value
        self.save()
        self.notify_observers()
    projection = property(_get_projection, _set_projection)

    def _get_light(self):
        return self._light
    def _set_light(self, value):
        value = float(value)
        self._light = value
        self.save()
        self.notify_observers()
    light = property(_get_light, _set_light)

    def _get_offset(self):
        return self._offset
    def _set_offset(self, value):
        value = float(value)
        self._offset = value
        self.save()
        self.notify_observers()
    offset = property(_get_offset, _set_offset)

    def to_dict(self):
        return {
            "projection" : self._projection,
            "light" : self._light,
            "offset" : self._offset,
        }
    def from_dict(self, data):
        self._projection = data["projection"]
        self._light = data["light"]
        self._offset = data["offset"]

class Settings_Sequence(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.save = parent.save
        self.image1 = Settings_SequenceImage(self)
        self.image2 = Settings_SequenceImage(self)

    def to_dict(self):
        return {
            "image1" : self.image1.to_dict(),
            "image2" : self.image2.to_dict(),
        }
    def from_dict(self, data):
        self.image1.from_dict(data["image1"])
        self.image2.from_dict(data["image2"])

class Settings_Cameras(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.save = parent.save
        self._quality = "speed"
        self._iso = 100
        self._shutter_speed = 20000
        self._exposure_mode = 'backlight' # off','auto','night', 'nightpreview', 'backlight', 'spotlight', 'sports', 'snow', 'beach', 'verylong', 'fixedfps', 'antishake', 'fireworks'
        self._meter_mode = 'backlit' # 'average','spot','backlit','matrix'
        self._awb_mode = 'auto' #'off', 'auto', 'sunlight', 'cloudy', 'shade', 'tungsten', 'fluorescent', 'incandescent', 'flash', 'horizon'
        self._awb_gains = [1,1]

    def _get_quality(self):
        return self._quality
    def _set_quality(self, value):
        self._quality= value
        self.save()
        self.notify_observers()
        devicesInstance.cameras.set_quality(value)
    quality = property(_get_quality, _set_quality)

    def _get_iso(self):
        return self._iso
    def _set_iso(self, value):
        value = int(value)
        self._iso = value
        self.save()
        self.notify_observers()
        devicesInstance.cameras.set_iso(value)
    iso = property(_get_iso, _set_iso)

    def _get_shutter_speed(self):
        return self._shutter_speed
    def _set_shutter_speed(self, value):
        value = int(value)
        self._shutter_speed = value
        self.save()
        self.notify_observers()
        devicesInstance.cameras.set_shutter_speed(value)
    shutter_speed = property(_get_shutter_speed, _set_shutter_speed)

    def _get_exposure_mode(self):
        return self._exposure_mode
    def _set_exposure_mode(self, value):
        self._exposure_mode = value
        self.save()
        self.notify_observers()
        devicesInstance.cameras.set_exposure_mode(value)
    exposure_mode = property(_get_exposure_mode, _set_exposure_mode)

    def _get_meter_mode(self):
        return self._meter_mode
    def _set_meter_mode(self, value):
        self._meter_mode = value
        self.save()
        self.notify_observers()
        devicesInstance.cameras.set_meter_mode(value)
    meter_mode = property(_get_meter_mode, _set_meter_mode)

    def _get_awb_mode(self):
        return self._awb_mode
    def _set_awb_mode(self, value):
        self._awb_mode = value
        self.save()
        self.notify_observers()
    awb_mode = property(_get_awb_mode, _set_awb_mode)

    def _get_awb_gains(self):
        return self._awb_gains
    def _set_awb_gains(self, awb_gains):
        self._awb_gains = awb_gains
        self.save()
        self.notify_observers()
        devicesInstance.cameras.set_awb_gains(awb_gains)
    awb_gains = property(_get_awb_gains, _set_awb_gains)

    def to_dict(self):
        return {
            "quality": self.quality,
            "iso": self.iso,
            "shutter_speed": self.shutter_speed,
            "exposure_mode": self.exposure_mode,
            "meter_mode": self.meter_mode,
            "awb_mode": self.awb_mode,
            "awb_gains": self.awb_gains,
        }

    def from_dict(self, data):
        try:
            self.iso = data["iso"]
            self.shutter_speed = data["shutter_speed"]
            self.exposure_mode = data["exposure_mode"]
            self.meter_mode = data["meter_mode"]
            self.awb_mode = data["awb_mode"]
            self.awb_gains = data["awb_gains"]
            self.quality = data["quality"]
        except:
            pass

class Settings(Observable):
    def __init__(self):
        super().__init__()
        self.sequenceSettingsSpeed = Settings_Sequence(self)
        self.sequenceSettingsQuality = Settings_Sequence(self)
        self.cameraSettings = Settings_Cameras(self)
        self.firmwareSettings = Settings_FirmwareImage(self)
        self.wirelessSettings = Settings_Wireless(self)
        self.VERSION = VERSION
        self.load()

    def save(self):
        data = {
            "sequenceSettingsSpeed" : self.sequenceSettingsSpeed.to_dict(),
            "sequenceSettingsQuality" : self.sequenceSettingsQuality.to_dict(),
            "cameraSettings" : self.cameraSettings.to_dict(),
            "firmwareSettings" : self.firmwareSettings.to_dict(),
            "wirelessSettings" : self.wirelessSettings.to_dict()
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
        except Exception as e:
            print("error loading settings:", e)
        self.save()
        self.notify_observers()



_settingsInstance = None
def SettingsInstance(_devicesInstance = None):
    global _settingsInstance
    global devicesInstance
    if _devicesInstance is not None:
        devicesInstance = _devicesInstance
    if _settingsInstance is None:
        _settingsInstance = Settings()
    return _settingsInstance
