import glob
import os

from pyhtmlgui import Observable


class SettingsFirmwareImage(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.save = parent.save
        self.current_image = ""
        self.image_files = []
        self.load()

    def set_image(self, value):
        self.current_image = value
        if self.current_image not in self.image_files:
            if len(self.image_files) > 0:
                self.current_image = self.image_files[-1]
            else:
                self.current_image = ""
        self.save()
        self.notify_observers()

    def delete_image(self, image):
        img_path = os.path.join("/opt/openpi3dscan/firmware/", image)
        if os.path.exists(img_path):
            os.remove(img_path)
            self.load()

    def load(self):
        self.image_files = [f.replace("/opt/openpi3dscan/firmware/", "") for f in glob.glob("/opt/openpi3dscan/firmware/*.img")]
        self.image_files.sort()
        if self.current_image != "" and self.current_image not in self.image_files:
            if len(self.image_files) > 0:
                self.current_image = self.image_files[-1]
            else:
                self.current_image = ""
        self.notify_observers()

    def to_dict(self):
        return {
            "current_image" : self.current_image,
        }

    def from_dict(self, data):
        self.current_image = data["current_image"]
        self.load()
