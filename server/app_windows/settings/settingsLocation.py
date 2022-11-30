import os
import re

from pyhtmlgui import Observable


class SettingsLocation(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.save = parent.save
        self.location = ""
        self.segments = 16
        self.cameras_per_segment = 7
        self.camera_rotation = 0  # 0, 90, 180, 270
        self.camera_one_position = "top"  # top, bottom
        self.calibration_data = "{}" # json dump of rc data
        self.markers = ""
        self.diameter = 1.8
        self.height = 2.5

    def to_dict(self):
        return {
            "markers": self.markers,
            "diameter": self.diameter,
            "height": self.height,
            "segments": self.segments,
            "cameras_per_segment": self.cameras_per_segment,
            "camera_rotation": self.camera_rotation,
            "camera_one_position": self.camera_one_position,
            "location": self.location,
            "calibration_data": self.calibration_data,

        }

    def from_dict(self, data):
        self.markers = data["markers"]
        self.diameter = data["diameter"]
        self.height = data["height"]
        self.segments = data["segments"]
        self.cameras_per_segment = data["cameras_per_segment"]
        self.camera_rotation = data["camera_rotation"]
        self.camera_one_position = data["camera_one_position"]
        self.location = data["location"]
        self.calibration_data = data["calibration_data"]
        return self

    def set_markers(self, markers):
        self.markers = markers
        self.save()
        self.notify_observers()

    def set_height(self, new_height):
        try:
            new_height = float(new_height)
        except:
            return
        if new_height < 1 or  new_height > 5:
            self.notify_observers()
            return
        self.height = new_height
        self.save()
        self.notify_observers()

    def set_diameter(self, new_diameter):
        try:
            new_diameter = float(new_diameter)
        except:
            return
        if new_diameter < 1 or  new_diameter > 5:
            self.notify_observers()
            return
        self.diameter = new_diameter
        self.save()
        self.notify_observers()


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

    def set_location(self, value):
        if value != self.location:
            self.location = value
            self.save()
            self.notify_observers()

    def set_calibration_data(self, new_calibration_data):
        self.calibration_data = new_calibration_data
        self.save()
        self.notify_observers()

    def reset_calibration(self):
        self.calibration_data = "{}"
        self.save()
        self.notify_observers()

    def remove(self):
        self.parent.remove(self)
        self.notify_observers()

    def calibration_count(self):
        return self.calibration_data.count("FocalLength35mm")


