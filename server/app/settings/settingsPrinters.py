import os
import re
import time

import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect
from pyhtmlgui import Observable

class SettingsPrinters(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.save = parent.save
        self.enabled = False
        self.colors = ""
        self.printers = ""

    def to_dict(self):
        return {
            "enabled": self.enabled,
            "colors": self.colors,
            "printers": self.printers,
        }

    def from_dict(self, data):
        self.enabled = data["enabled"]
        self.colors = data["colors"]
        self.printers = data["printers"]

    def set_enabled(self, new_enabled):
        if self.enabled != new_enabled:
            self.enabled = new_enabled
            self.save()
            self.notify_observers()

    def set_colors(self, new_colors):
        if self.colors != new_colors:
            self.colors = new_colors
            self.save()
            self.notify_observers()

    def set_printers(self, new_printers):
        if self.printers != new_printers:
            self.printers = new_printers
            self.save()
            self.notify_observers()

