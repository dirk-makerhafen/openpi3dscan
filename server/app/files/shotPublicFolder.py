import datetime
import json
import os,sys, dropbox
import threading
import time
import unicodedata
import six
import re
from dropbox import exceptions, files
from pyhtmlgui import Observable, ObservableList
from app.dropbox.sharings import DropboxPublicModelShare, DropboxPublicImagesShare


class ShotDropboxPublicFolder(Observable):
    def __init__(self, parent_shot):
        super().__init__()
        self.parent_shot = parent_shot
        self.status = "new"  # new, creating, online, pending_delete, deleting, deleted
        self.name = ""
        self.path = ""
        self.compressed = False
        self.expire_in = 0
        self.url = ""
        self.uploads = ObservableList()
        self.share_images = False

    def save(self):
        self.parent_shot.save()

    def set_status(self, status):
        if self.status != status:
            self.status = status
            self.save()
            self.notify_observers()

    def add_images(self):
        if len([m for m in self.uploads if not hasattr(m,"model")]) > 0:
            return
        upload = DropboxPublicImagesShare(self)
        self.share_images = True
        self.uploads.append(upload)
        self.parent_shot.parent_shots.dropboxUploads.add_to_uploadqueue(upload)
        self.save()
        self.notify_observers()
        self.parent_shot.notify_observers()

    def remove_images(self):
        try:
            [m for m in self.uploads if not hasattr(m,"model")][0].delete()
        except:
            pass

    def add_model(self, model):
        if model in [m.model for m in self.uploads if hasattr(m,"model")]:
            return
        upload = DropboxPublicModelShare(self, model)
        self.parent_shot.parent_shots.dropboxUploads.add_to_uploadqueue(upload)
        model.is_shared = True
        model.notify_observers()
        self.uploads.append(upload)
        self.save()
        self.notify_observers()

    def remove_model(self, model):
        try:
            [m for m in self.uploads if hasattr(m, "model") and m.model == model][0].delete()
        except:
            pass


    def create_link(self, name, expire_in, compressed):
        if self.url != "" or self.status != "new":
            return
        self.name = self._clean_for_filesystem(name)
        if self.name == "":
            return
        self.set_status("creating")
        self.path = "/public/%s" % self.name
        self.compressed = compressed
        self.expire_in = expire_in
        self.save()
        t = threading.Thread(target=self._create_thread, daemon=True)
        t.run()

    def delete(self):
        t = threading.Thread(target=self._delete_thread, daemon=True)
        t.run()

    def _clean_for_filesystem(self, value):
        name = value
        for rp in [["ä", "ae"], ["ö", "oe"], ["ü", "ue"], ["Ä", "Ae"], ["Ö", "Oe"], ["Ü", "Ue"]]:
            name = name.replace(rp[0], rp[1])
        name = re.sub('\s+', ' ', name)
        name = re.sub('[^A-Za-z0-9_. ]+', '', name)
        for rp in [["..", "."], ["__", "_"], ["  ", " "]]:
            while rp[0] in name:
                name = name.replace(rp[0], rp[1]).strip()
        name = name.strip()
        while name[-1] in ["_", "."]:
            name = name[:-1].strip()
        while name[0] in ["_", "."]:
            name = name[1:].strip()
        return name


    def to_dict(self):
        return {
            "status": self.status,
            "name": self.name,
            "compressed": self.compressed,
            "expire_in": self.expire_in,
            "url": self.url,
            "uploads": [  u.to_dict() for u in self.uploads]
        }

    def from_dict(self, data):
        self.status = data["status"]
        self.name = data["name"]
        self.compressed = data["compressed"]
        self.expire_in = data["expire_in"]
        self.url = data["url"]
        if self.status == "creating":
            self.status = "new"
            self.url = ""
        self.uploads.clear()
        return
        for upload in data["uploads"]:
            if "model_id" in upload:
                models = [m for m in self.parent_shot.models if m.model_id == uploads["model_id"]]
                if len(models) == 1:
                    model = models[0]
                    model.is_shared = True
                    model.notify_observers()
                else:
                    model = None
                self.uploads.append(DropboxPublicModelUpload(self, model=model).from_dict(upload))
            else:
                self.uploads.append(DropboxPublicImagesUpload(self).from_dict(upload))
                self.share_images = True
        for upload in self.uploads():
            if upload.all_in_sync == False:
                self.parent_shot.parent_shots.dropboxUploads.add_to_uploadqueue(upload)

    def _create_thread(self):
        self.set_status("creating")
        try:
            with dropbox.Dropbox(oauth2_refresh_token=self.parent_shot.settingsInstance.settingsDropbox.refresh_token, app_key=self.parent_shot.settingsInstance.settingsDropbox.app_key) as dbx:
                try:
                    dbx.files_create_folder_v2(self.path)
                except:
                    pass
                self.url = dbx.sharing_create_shared_link_with_settings(self.path).url
                self.set_status("online")
        except:
            self.url = ""
            self.set_status("new")
        self.save()
        self.notify_observers()
        self.parent_shot.notify_observers()

    def _delete_thread(self):
        if self.status != "online":
            return
        self.set_status("deleting")
        try:
            with dropbox.Dropbox(oauth2_refresh_token=self.parent_shot.settingsInstance.settingsDropbox.refresh_token, app_key=self.parent_shot.settingsInstance.settingsDropbox.app_key) as dbx:
                try:
                    dbx.files_delete_v2(self.path)
                except:
                    pass
                self.url = ""
                self.uploads.clear()
                self.set_status("new")
        except:
            self.set_status("online")
        self.save()
        self.notify_observers()
        self.parent_shot.notify_observers()
