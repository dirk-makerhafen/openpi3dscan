class Projectors:
    def __init__(self, devices):
        self._devices = devices

    def list(self):
        return [d for d in self._devices if d.device_type == "projector"]

    def set(self, enable):
        if enable is True:
            self.enable()
        else:
            self.disable()

    def enable(self):
        for device in self.list():
            device.projector.enable()

    def disable(self):
        for device in self.list():
            device.projector.disable()
