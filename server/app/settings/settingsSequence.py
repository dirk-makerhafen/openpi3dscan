from pyhtmlgui import Observable

from app.settings.settingsSequenceImage import SettingsSequenceImage


class SettingsSequence(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.save = parent.save
        self.image1 = SettingsSequenceImage(self)
        self.image2 = SettingsSequenceImage(self)
        self.startup_delay = 3  # seconds
        self.image_delay = 0  # frames

    def set_startup_delay(self, value):
        try:
            value = int(value)
        except:
            value = 3
        if value < 2:
            value = 2
        if value > 10:
            value = 10
        if self.startup_delay != value:
            self.startup_delay = value
            self.save()

    def set_image_delay(self, value):
        try:
            value = int(value)
        except:
            value = 0
        if value < 0:
            value = 0
        if value > 10:
            value = 10
        if self.image_delay != value:
            self.image_delay = value
            self.save()

    def to_dict(self):
        return {
            "image1": self.image1.to_dict(),
            "image2": self.image2.to_dict(),
            "startup_delay": self.startup_delay,
            "image_delay": self.image_delay,
        }

    def from_dict(self, data):
        self.image1.from_dict(data["image1"])
        self.image2.from_dict(data["image2"])
        try:
            self.startup_delay = data["startup_delay"]
        except:
            self.startup_delay = 3
        try:
            self.image_delay = data["image_delay"]
        except:
            self.image_delay = 0
