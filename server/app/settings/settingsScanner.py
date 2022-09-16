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

    def to_dict(self):
        return {
            "segments": self.segments,
            "cameras_per_segment": self.cameras_per_segment,
        }

    def from_dict(self, data):
        self.segments = data["segments"]
        self.cameras_per_segment = data["cameras_per_segment"]

    def set_segments(self, value):
        if self.segments != value:
            self.segments = value
            self.save()
            self.notify_observers()

    def set_cameras_per_segment(self, value):
        if self.cameras_per_segment != value:
            self.cameras_per_segment = value
            self.save()
            self.notify_observers()