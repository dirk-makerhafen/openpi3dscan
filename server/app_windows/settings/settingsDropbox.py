import os
import re
import time

from pyhtmlgui import Observable



class SettingsDropbox(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.save = parent.save
        self.enabled = False
        self.token = ""
        self.next_sync_time = time.time()

    def to_dict(self):
        return {
            "enabled": self.enabled,
            "token": self.token,
            "next_sync_time": self.next_sync_time,
        }

    def from_dict(self, data):
        self.token = data["token"]
        self.enabled = data["enabled"]
        self.next_sync_time = data["next_sync_time"]

    def set_token(self, new_token):
        if self.token != new_token:
            self.token = new_token
            self.save()
            self.notify_observers()

    def set_enabled(self, new_enabled):
        if self.enabled != new_enabled:
            self.enabled = new_enabled
            self.save()
            self.notify_observers()

    def set_next_sync_time(self, new_next_sync_time):
        if self.next_sync_time != new_next_sync_time:
            self.next_sync_time = new_next_sync_time
            self.save()
            self.notify_observers()

    def get_next_sync_minutes(self):
        return (self.next_sync_time - time.time()) / 60

    def set_sync_now(self):
        self.set_next_sync_time( time.time())
        from app_windows.files.shotsDropboxDownload import ShotsDropboxDownloadInstance
        ShotsDropboxDownloadInstance().sync()
