import os
import re

from pyhtmlgui import Observable


class SettingsScanner(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.save = parent.save
        self.segments = 16
        self.cameras_per_segment = 7
        self.camera_rotation = 0  # 0, 90, 180, 270
        self.camera_one_position = "top"  # top, bottom

    def to_dict(self):
        return {
            "segments": self.segments,
            "cameras_per_segment": self.cameras_per_segment,
            "camera_rotation": self.camera_rotation,
            "camera_one_position": self.camera_one_position,
        }

    def from_dict(self, data):
        self.segments = data["segments"]
        self.cameras_per_segment = data["cameras_per_segment"]
        self.camera_rotation = data["camera_rotation"]
        self.camera_one_position = data["camera_one_position"]

    def set_segments(self, value):
        try:
            value = int(value)
        except:
            return
        if self.segments != value:
            self.segments = value
            self.save()
            self.notify_observers()

    def set_cameras_per_segment(self, value):
        try:
            value = int(value)
        except:
            return
        if self.cameras_per_segment != value:
            self.cameras_per_segment = value
            self.save()
            self.notify_observers()

    def set_camera_rotation(self, value):
        try:
            value = int(value)
        except:
            return
        if value not in [0, 90, 180, 270]:
            return
        if value != self.camera_rotation:
            self.camera_rotation = value
            self.save()
            self.notify_observers()

    def set_camera_one_position(self, value):
        if value not in ["top", "bottom"]:
            return
        if value != self.camera_one_position:
            self.camera_one_position = value
            self.save()
            self.notify_observers()



