import os
import re

from pyhtmlgui import Observable


class SettingsDropbox(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.save = parent.save
        self.enabled = False
        self.token = ""

    def to_dict(self):
        return {
            "enabled": self.enabled,
            "token": self.token,
        }

    def from_dict(self, data):
        self.token = data["token"]
        self.enabled = data["enabled"]

    def set_token(self, new_token):
        if self.token != new_token:
            self.token = new_token
            self.save()
            self.notify_observers()

    def set_enabled(self, new_enabled):
        if self.enabled != new_enabled:
            self.token = new_enabled
            self.save()
            self.notify_observers()




