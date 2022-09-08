import queue
import threading
import time

from pyhtmlgui import Observable, ObservableList

from .device import Device
from .devices_Cameras import Cameras
from .devices_Lights import Lights
from .devices_Projectors import Projectors
from settings import SettingsInstance

class Devices(Observable):
    def __init__(self):
        super().__init__()
        self.devices = ObservableList()
        self.heartbeat_rec_queue = queue.Queue()
        self.id_cache = {}
        self.ip_cache = {}
        self.name_cache = {}
        self.lights = Lights(self.devices)
        self.projectors = Projectors(self.devices)
        self.cameras = Cameras(self.devices)
        self.t = threading.Thread(target=self.process_heartbeats_thread, daemon=True)
        self.t.start()

    def get_device_by_id(self,device_id):
        if device_id in self.id_cache:
            if self.id_cache[device_id].device_id == device_id:
                return self.id_cache[device_id]
            else:
                del self.id_cache[device_id] # if id has changed, invalidate cache
        for device in self.devices:
            self.id_cache[device.device_id] = device # build cache
        if device_id in self.id_cache:
            return self.id_cache[device_id]
        return None

    def get_device_by_ip(self,ip):
        if ip in self.ip_cache:
            if self.ip_cache[ip].ip == ip:
                return self.ip_cache[ip]
            else:
                del self.ip_cache[ip] # if id has changed, invalidate cache
        for device in self.devices:
            self.ip_cache[device.ip] = device # build cache
        if ip in self.ip_cache:
            return self.ip_cache[ip]
        return None

    def get_cameras_by_segment(self, segment):
        return [d for d in self.devices if d.device_type == "camera" and d.name.startswith("SEG%s" % segment)]

    def get_camera_by_position(self, segment, reihe):
        name =  "SEG%s-CAM%s" % (segment, reihe)
        if name in self.name_cache:
            if self.name_cache[name].name == name:
                return self.name_cache[name]
            else:
                del self.name_cache[name] # if name has changed, invalidate cache
        for device in self.devices:
            self.name_cache[device.name] = device # build cache
        if name in self.name_cache:
            return self.name_cache[name]
        return None

    def heartbeat_received(self, ip,data):
        self.heartbeat_rec_queue.put([ip, data])

    def process_heartbeats_thread(self):
        while True:
            try:
                hb = self.heartbeat_rec_queue.get()
                ip, data = hb
                device = self.get_device_by_id(data["ID"])
                if device is None:
                    device = self.get_device_by_ip(ip)
                    if device is not None:
                        device.device_type = data["TYPE"]
                        device.device_id = data["ID"]
                        device.name = data["NAME"]
                if device is None:
                    device = Device()
                    device.device_type = data["TYPE"]
                    device.device_id = data["ID"]
                    device.ip = ip
                    device.name = data["NAME"]
                    self.devices.append(device)
                if device.ip != ip: # device changed or new
                    old_device = self.get_device_by_ip(ip)
                    if old_device is not None: # some other id already uses this ip, remove other
                        old_device.ip = ""
                        old_device.online_ping = False
                        old_device.shotlist = []
                        old_device.notify_observers()
                    device.ip = ip

                last_status =  device.status
                if device.status != "installing":
                    device.status = "online"
                if "UPTIME" in data and data["UPTIME"] < 300:
                    device.status = "warmup"

                if data["TYPE"] == "camera" and device.status == "online" and last_status != "online":
                    device.camera.shots.refresh_list()

                if data["TYPE"] == "camera":
                    if device.camera.settings.locked == False:

                        if "awb_gains" in data:
                            device.camera.settings.awb_gains = data["awb_gains"]
                            if abs(SettingsInstance().cameraSettings.awb_gains[0] - data["awb_gains"][0]) > 0.01 or abs(SettingsInstance().cameraSettings.awb_gains[1] -  data["awb_gains"][1]) > 0.01:
                                device.camera.settings.set_awb_gains(SettingsInstance().cameraSettings.awb_gains)
                        if "analog_gain" in data: device.camera.settings.analog_gain = data["analog_gain"]
                        if "digital_gain" in data: device.camera.settings.digital_gain = data["digital_gain"]
                        if "exposure_speed" in data: device.camera.settings.exposure_speed = data["exposure_speed"]
                        if "quality" in data: device.camera.settings.quality = data["quality"]
                        if "shutter_speed" in data and abs(data["shutter_speed"] - SettingsInstance().cameraSettings.shutter_speed) > 100:
                            device.camera.settings.set_shutter_speed(SettingsInstance().cameraSettings.shutter_speed)
                        if "meter_mode" in data and data["meter_mode"] != SettingsInstance().cameraSettings.meter_mode:
                            device.camera.settings.set_meter_mode(SettingsInstance().cameraSettings.meter_mode)
                        if "iso" in data and data["iso"] != SettingsInstance().cameraSettings.iso:
                            print(data["iso"] , SettingsInstance().cameraSettings.iso, type(data["iso"]), type(SettingsInstance().cameraSettings.iso))
                            device.camera.settings.set_iso(SettingsInstance().cameraSettings.iso)
                        #if "exposure_mode" in data and data["exposure_mode"]!= SettingsInstance().cameraSettings.exposure_mode:
                        #    device.camera.settings.set_exposure_mode(SettingsInstance().cameraSettings.exposure_mode)
                        #if "awb_mode"      in data and data["awb_mode"]     != SettingsInstance().cameraSettings.awb_mode:
                        #    device.camera.settings.set_awb_mode(SettingsInstance().cameraSettings.awb_mode)


                device.ip = ip
                device.name = data["NAME"]
                device.latest_heartbeat_time = int(time.time())
                device.version = data["VERSION"]
                try:
                    device.disksize = data["DISK"][0]
                    device.diskfree = data["DISK"][1]
                except:
                    pass

                device.notify_observers()
            except Exception as e:
                print("Failed to process heartbeat")
                print(e)

    def shutdown(self):
        for device in self.devices:
            device.shutdown()


_devicesInstance = None
def DevicesInstance():
    global _devicesInstance
    if _devicesInstance is None:
        _devicesInstance = Devices()
    return _devicesInstance
