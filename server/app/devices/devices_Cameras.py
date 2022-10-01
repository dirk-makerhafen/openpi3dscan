
class Cameras:
    def __init__(self, devices):
        self._devices = devices

    def list(self):
        return [d for d in self._devices if d.device_type == "camera"]

    def whitebalance(self):
        for device in self.list():
            device.camera.whitebalance()

    def set_quality(self, new_quality):
        for device in self.list():
            device.camera.settings.set_quality(new_quality)

    def set_iso(self, iso):
        for device in self.list():
            if device.camera.settings.iso != iso:
                device.camera.settings.set_iso(iso)

    #def set_shutter_speed(self, shutter_speed):
    #    for device in self.list():
    #        if device.camera.settings.shutter_speed != shutter_speed:
    #            device.camera.settings.set_shutter_speed(shutter_speed)

    def set_meter_mode(self, meter_mode):
        for device in self.list():
            if device.camera.settings.meter_mode != meter_mode:
                device.camera.settings.set_meter_mode(meter_mode)

    def set_exposure_mode(self, exposure_mode):
        for device in self.list():
            if device.camera.settings.exposure_mode != exposure_mode:
                device.camera.settings.set_exposure_mode(exposure_mode)

    def set_awb_mode(self, awb_mode):
        for device in self.list():
            if device.camera.settings.awb_mode != awb_mode:
                device.camera.settings.set_awb_mode(awb_mode)

    def set_awb_gains(self, awb_gains):
        for device in self.list():
            if abs(device.camera.settings.awb_gains[0] - awb_gains[0]) > 0.01 or abs(device.camera.settings.awb_gains[1] - awb_gains[1]) > 0.01 :
                device.camera.settings.set_awb_gains(awb_gains)

