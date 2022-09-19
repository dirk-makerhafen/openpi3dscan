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
        self.camera_orientation = "landscape"   # landscape,  portrait
        self.camera_one_position = "top"  # top, bottom

    def to_dict(self):
        return {
            "segments": self.segments,
            "cameras_per_segment": self.cameras_per_segment,
            "camera_orientation": self.camera_orientation,
            "camera_one_position": self.camera_one_position,
        }

    def from_dict(self, data):
        self.segments = data["segments"]
        self.cameras_per_segment = data["cameras_per_segment"]
        self.camera_orientation = data["camera_orientation"]
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

    def set_camera_orientation(self, value):
        if value not in ["landscape", "portrait"]:
            return
        if value != self.camera_orientation:
            self.camera_orientation = value
            self.save()
            self.notify_observers()

    def set_camera_one_position(self, value):
        if value not in ["top", "bottom"]:
            return
        if value != self.camera_one_position:
            self.camera_one_position = value
            self.save()
            self.notify_observers()



