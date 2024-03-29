import os
import re

from pyhtmlgui import Observable


MARKERS_PRELOAD = '''
#marker1   marker2    distance
1x12:011   1x12:012   0.500
1x12:011   1x12:013   0.866
1x12:011   1x12:014   1.000
1x12:011   1x12:015   0.866
1x12:011   1x12:016   0.500
1x12:012   1x12:013   0.500
1x12:012   1x12:014   0.866
1x12:012   1x12:015   1.000
1x12:012   1x12:016   0.866
1x12:013   1x12:014   0.500
1x12:013   1x12:015   0.866
1x12:013   1x12:016   1.000
1x12:014   1x12:015   0.500
1x12:014   1x12:016   0.866
1x12:015   1x12:016   0.500
'''
GROUND_PRELOAD = '''
# marker     X       Y      Z
1x12:011  -0.433  -0.250  0.000
1x12:012  -0.433   0.250  0.000
1x12:013   0.000   0.500  0.000
1x12:014   0.433   0.250  0.000
1x12:015   0.433  -0.250  0.000
1x12:016   0.000  -0.500  0.000

'''

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
        self.first_camera_number = 1
        self.calibration_data = "{}" # json dump of rc data
        self.markers = MARKERS_PRELOAD
        self.ground_points = GROUND_PRELOAD
        self.diameter = 1.8
        self.height = 2.5

    def to_dict(self):
        return {
            "markers": self.markers,
            "ground_points": self.ground_points,
            "diameter": self.diameter,
            "height": self.height,
            "segments": self.segments,
            "cameras_per_segment": self.cameras_per_segment,
            "camera_rotation": self.camera_rotation,
            "camera_one_position": self.camera_one_position,
            "location": self.location,
            "calibration_data": self.calibration_data,
            "first_camera_number": self.first_camera_number,

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
        try:
            self.ground_points = data["ground_points"]
            self.first_camera_number = data["first_camera_number"]
        except:
            pass

        return self

    def set_markers(self, markers):
        self.markers = markers
        self.save()
        self.notify_observers()


    def set_ground_points(self, ground_points):
        self.ground_points = ground_points
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

    def set_first_camera_number(self, value):
        if value != self.first_camera_number:
            self.first_camera_number = value
            self.save()
            self.notify_observers()

