from pyhtmlgui import Observable


class SettingsCameras(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.save = parent.save
        self._quality = "speed"
        self._iso = 100
        self._shutter_speed = 20000
        self._exposure_mode = 'backlight'  # off','auto','night', 'nightpreview', 'backlight', 'spotlight', 'sports', 'snow', 'beach', 'verylong', 'fixedfps', 'antishake', 'fireworks'
        self._meter_mode = 'backlit'  # 'average','spot','backlit','matrix'
        self._awb_mode = 'auto'  # 'off', 'auto', 'sunlight', 'cloudy', 'shade', 'tungsten', 'fluorescent', 'incandescent', 'flash', 'horizon'
        self._awb_gains = [1, 1]
        self._per_segment_shutter_speeds = []
        self._per_segment_awb_gains = []
        self._shutter_speed_adjustment = 0 # -100% to 100%
        self.adjusted_shutter_speeds = []

    def _get_shutter_speed_adjustment(self):
        return self._shutter_speed_adjustment

    def _set_shutter_speed_adjustment(self, value):
        try:
            value = int(value)
        except:
            return
        if value < -100 or value > 100:
            return
        self._shutter_speed_adjustment = value
        self._update_adjusted_shutter_speeds()
        self.save()
        self.notify_observers()
        for i in range(len(self.adjusted_shutter_speeds)):
            cameras = self.parent.devicesInstance.get_cameras_by_segment(i + 1)
            for device in cameras:
                if device.camera.settings.shutter_speed == 0:
                    continue
                if abs(device.camera.settings.shutter_speed - self.adjusted_shutter_speeds[i]) > 10:
                     device.camera.settings.set_shutter_speed(self.adjusted_shutter_speeds[i])
    shutter_speed_adjustment = property(_get_shutter_speed_adjustment, _set_shutter_speed_adjustment)

    def _get_quality(self):
        return self._quality

    def _set_quality(self, value):
        self._quality = value
        self.save()
        self.notify_observers()
        self.parent.devicesInstance.cameras.set_quality(value)
    quality = property(_get_quality, _set_quality)

    def _get_iso(self):
        return self._iso

    def _set_iso(self, value):
        value = int(value)
        self._iso = value
        self.save()
        self.notify_observers()
        self.parent.devicesInstance.cameras.set_iso(value)
    iso = property(_get_iso, _set_iso)

    def _get_shutter_speed(self):
        return self._shutter_speed

    def _set_shutter_speed(self, value):
        value = int(value)
        self._shutter_speed = value
        self.save()
        self.notify_observers()
        #self.parent.devicesInstance.cameras.set_shutter_speed(value)
    shutter_speed = property(_get_shutter_speed, _set_shutter_speed)

    def _get_per_segment_shutter_speeds(self):
        return self._per_segment_shutter_speeds

    def _update_adjusted_shutter_speeds(self):
        adj = 0
        if self.shutter_speed_adjustment > 0:
            maxadj = 65000 - max(self._per_segment_shutter_speeds)
            if maxadj < 0: maxadj = 0
            adj = maxadj / 100.0 * self.shutter_speed_adjustment
        if self.shutter_speed_adjustment < 0:
            maxadj = min(self._per_segment_shutter_speeds) - 10000
            if maxadj < 0: maxadj = 0
            adj = maxadj / 100.0 * self.shutter_speed_adjustment
        self.adjusted_shutter_speeds = [int(x + adj) for x in self._per_segment_shutter_speeds]

    def _set_per_segment_shutter_speeds(self, values):
        self._per_segment_shutter_speeds = values
        self._update_adjusted_shutter_speeds()
        self.save()
        self.notify_observers()
        for i in range(len(self.adjusted_shutter_speeds)):
            cameras = self.parent.devicesInstance.get_cameras_by_segment(i + 1)
            for device in cameras:
                if abs(device.camera.settings.shutter_speed - self.adjusted_shutter_speeds[i]) > 10:
                     device.camera.settings.set_shutter_speed(self.adjusted_shutter_speeds[i])
    per_segment_shutter_speeds = property(_get_per_segment_shutter_speeds, _set_per_segment_shutter_speeds)

    def _get_per_segment_awb_gains(self):
        return self._per_segment_awb_gains

    def _set_per_segment_awb_gains(self, values):
        self._per_segment_awb_gains = values
        self.save()
        self.notify_observers()
        for i in range(len( self._per_segment_awb_gains)):
            cameras = self.parent.devicesInstance.get_cameras_by_segment(i + 1)
            for device in cameras:
                if abs(device.camera.settings.awb_gains[0]- self._per_segment_awb_gains[i][0]) >  0.01 or abs(device.camera.settings.awb_gains[1]- self._per_segment_awb_gains[i][1]) >  0.01 :
                     device.camera.settings.set_awb_gains(self._per_segment_awb_gains[i])
    per_segment_awb_gains = property(_get_per_segment_awb_gains, _set_per_segment_awb_gains)

    def _get_exposure_mode(self):
        return self._exposure_mode

    def _set_exposure_mode(self, value):
        self._exposure_mode = value
        self.save()
        self.notify_observers()
        self.parent.devicesInstance.cameras.set_exposure_mode(value)
    exposure_mode = property(_get_exposure_mode, _set_exposure_mode)

    def _get_meter_mode(self):
        return self._meter_mode

    def _set_meter_mode(self, value):
        self._meter_mode = value
        self.save()
        self.notify_observers()
        self.parent.devicesInstance.cameras.set_meter_mode(value)
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
        self.parent.devicesInstance.cameras.set_awb_gains(awb_gains)
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
            "per_segment_shutter_speeds": self.per_segment_shutter_speeds,
            "per_segment_awb_gains": self.per_segment_awb_gains,
            "shutter_speed_adjustment": self.shutter_speed_adjustment,
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
            self.per_segment_shutter_speeds = data["per_segment_shutter_speeds"]
            self.per_segment_awb_gains = data["per_segment_awb_gains"]
            self.shutter_speed_adjustment = data["shutter_speed_adjustment"]
        except:
            pass
        self._update_adjusted_shutter_speeds()
