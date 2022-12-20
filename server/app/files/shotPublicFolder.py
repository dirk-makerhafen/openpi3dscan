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
        self.expire_time = 0
        self.url = ""
        self.uploads = ObservableList()

    @property
    def can_delete(self):
        if self.status in ["creating", "pending_delete", "deleting", "deleted"]:
            return False
        if True in [u.status in ["uploading", "deleting", "deleted"] for u in self.uploads]:
            return False
        return True

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
        self.uploads.append(upload)
        self.parent_shot.set_publishing_status("can_unpublish")
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
        for old_upload in [u for u in self.uploads if hasattr(u,"model") and u.model is None and upload.target_path == u.target_path]:
            old_upload.delete()
        self.parent_shot.parent_shots.dropboxUploads.add_to_uploadqueue(upload)
        model.set_publishing_status("can_unpublish")
        self.uploads.append(upload)
        self.save()
        self.notify_observers()

    def remove_model(self, model):
        try:
            [m for m in self.uploads if hasattr(m, "model") and m.model == model][0].delete()
        except:
            pass

    def get_by_model(self, model):
        try:
            return [m for m in self.uploads if hasattr(m, "model") and m.model == model][0]
        except:
            return None

    def create_link(self, name, expire_in_weeks, compressed):
        if self.url != "" or self.status != "new":
            return
        self.name = self._clean_for_filesystem(name)
        if self.name == "":
            return
        expire_in_seconds = int(expire_in_weeks) * 7 * 24 * 60 * 60
        self.set_status("creating")
        self.path = "/public/%s" % self.name
        self.compressed = compressed
        self.expire_in = expire_in_seconds
        self.expire_time = time.time() + expire_in_seconds
        self.save()
        t = threading.Thread(target=self._create_thread, daemon=True)
        t.run()

    def delete(self):
        if self.can_delete is False:
            return
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
            "expire_time": self.expire_time,
            "uploads": [  u.to_dict() for u in self.uploads]
        }

    def from_dict(self, data):
        self.status = data["status"]
        self.name = data["name"]
        self.compressed = data["compressed"]
        self.expire_in = data["expire_in"]
        self.url = data["url"]
        self.expire_time = data["expire_time"]
        # new, creating, online, pending_delete, deleting, deleted
        if self.status == "creating":
            self.status = "new"
            self.url = ""
        [u.model.set_publishing_status("can_publish") for u in self.uploads if hasattr(u, "model") and u.model is not None]
        [u.shot.set_publishing_status("can_publish") for u in self.uploads if hasattr(u, "shot") and u.shot is not None]
        self.uploads.clear()
        for upload in data["uploads"]:
            if "model_id" in upload:
                models = [m for m in self.parent_shot.models if m.model_id == upload["model_id"]]
                if len(models) == 1:
                    model = models[0]
                    model.set_publishing_status("can_unpublish")  # can_publish, state_changing, is_public
                else:
                    model = None
                self.uploads.append(DropboxPublicModelShare(self, model=model).from_dict(upload))
            else:
                self.parent_shot.set_publishing_status("can_unpublish")
                self.uploads.append(DropboxPublicImagesShare(self).from_dict(upload))
        if self.status in ["pending_delete", "deleting"]:
            self.delete()

        for upload in self.uploads:
            if upload.all_in_sync == False:
                self.parent_shot.parent_shots.dropboxUploads.add_to_uploadqueue(upload)



    def _create_thread(self):
        self.set_status("creating")
        try:
            with dropbox.Dropbox(oauth2_refresh_token=self.parent_shot.settingsInstance.settingsDropbox.refresh_token, app_key=self.parent_shot.settingsInstance.settingsDropbox.app_key) as dbx:
                if dbx.check_user("pong").result != "pong":
                    raise Exception("Dropbox login failed")
                try:
                    dbx.files_create_folder_v2(self.path)
                except:
                    pass
                self.url = dbx.sharing_create_shared_link_with_settings(self.path).url
                self.set_status("online")
        except Exception as e:
            print("failed to create", e)
            self.url = ""
            self.set_status("new")
        self.save()
        self.notify_observers()
        self.parent_shot.notify_observers()

    def _delete_thread(self):
        self.set_status("deleting")

        [u.model.set_publishing_status("state_changing") for u in self.uploads if hasattr(u, "model")  and u.model is not None]
        [u.shot.set_publishing_status("state_changing") for u in self.uploads if hasattr(u, "shot")  and u.shot is not None]
        try:
            with dropbox.Dropbox(oauth2_refresh_token=self.parent_shot.settingsInstance.settingsDropbox.refresh_token, app_key=self.parent_shot.settingsInstance.settingsDropbox.app_key) as dbx:
                if dbx.check_user("pong").result != "pong":
                    raise Exception("Dropbox login failed")
                try:
                    dbx.files_delete_v2(self.path)
                except:
                    pass
                self.url = ""
                self.expire_time = 0
                [u.model.set_publishing_status("can_publish") for u in self.uploads if hasattr(u,"model") and u.model is not None]
                [u.shot.set_publishing_status("can_publish") for u in self.uploads if hasattr(u,"shot") and u.shot is not None]
                self.uploads.clear()
                self.set_status("new")
        except Exception as e:
            print("failed to delete", e)
            self.set_status("online")
        self.save()
        self.notify_observers()
        self.parent_shot.notify_observers()
