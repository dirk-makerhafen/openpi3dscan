import datetime
import json
import os,sys, dropbox
import threading
import time
import unicodedata
import six
import re
from dropbox import exceptions, files
from pyhtmlgui import Observable
from app.settings.settings import SettingsInstance
from dropbox import DropboxOAuth2FlowNoRedirect

class ShotDropboxPublicSharings(Observable):
    def __init__(self):
        super().__init__()
        self.sharings = []

    def get_by_name(self, name):
        pass

    def create(self, shot, name, link_type, compressed, expire_in):
        sharing = self.get_by_name(name)
        if sharing is None:
            sharing = ShotDropboxPublicSharing()
            sharing.name = name
            sharing.link_type = link_type
            sharing.compressed = compressed
            sharing.expire_in = expire_in
        sharing.shots.append(shot)


class ShotDropboxPublicItemUpload(Observable):
    def __init__(self):
        super().__init__()
        self.last_success = None
        self.last_failed = None
        self.last_checked = None
        self.all_in_sync = False
        self.status = "idle"
        self.current_upload_file = ""
        self.current_progress = 0

class ShotDropboxPublicModelUpload(ShotDropboxPublicItemUpload):
    pass
class ShotDropboxPublicImagesUpload(ShotDropboxPublicItemUpload):
    pass

class ShotDropboxPublicSharing(Observable):
    def __init__(self):
        super().__init__()
        self.status = "new"  # new, creating, failed, online
        self.name = ""
        self.link_type = "single"   # single, group
        self.compressed = False
        self.expire_in = 0
        self.url = ""
        self.shots = []
        self.uploads = []

    def add_images(self, shot):
        pass
    def add_model(self, model):
        pass

