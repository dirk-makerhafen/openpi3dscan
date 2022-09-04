class Lights:
    def __init__(self, devices):
        self._devices = devices
        self.value = 0

    def list(self):
        return [d for d in self._devices if d.device_type == "light"]

    def set(self, value):
        value = float(value)
        if value > 100:
            value = 100
        if value < 0:
            value = 0
        self.value = value
        for device in self.list():
            device.light.set(value)

