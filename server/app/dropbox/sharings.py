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
from dropbox import DropboxOAuth2FlowNoRedirect

class DropboxGenericShare(Observable):
    def __init__(self):
        super().__init__()
        self.last_checked = None
        self.last_success = None
        self.last_failed = None
        self.all_in_sync = False
        self.status = "pending"  # # idle, pending, uploading, online, deleting, deleted
        self.current_upload_file = ""
        self.progress = 0
        self.source_path = ""
        self.target_path = ""
        self.url = None

    def save(self):
        raise NotImplementedError()

    def delete(self):
        raise NotImplementedError()

    def set_status(self, status):
        if status != self.status:
            self.status = status
            self.save()
            self.notify_observers()

    def to_dict(self):
        return {
            "last_checked": self.last_checked,
            "last_success": self.last_success,
            "last_failed": self.last_failed,
            "all_in_sync": self.all_in_sync,
            "status": self.status,
            "progress": self.progress,
            "source_path": self.source_path,
            "target_path": self.target_path,
            "url": self.url,
        }

    def from_dict(self, data):
        self.last_checked = data["last_checked"]
        self.last_success = data["last_success"]
        self.last_failed = data["last_failed"]
        self.all_in_sync = data["all_in_sync"]
        self.status = data["status"]
        self.progress = data["progress"]
        self.source_path = data["source_path"]
        self.target_path = data["target_path"]
        self.url = data["url"]
        if self.status == "uploading":
            self.status = "pending"
        if self.status in ["deleting", "deleted"]:
            self.delete()
        return self

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

        while len(name) > 0 and name[-1] in ["_", "."]:
            name = name[:-1].strip()
        while len(name) > 0 and name[0] in ["_", "."]:
            name = name[1:].strip()
        return name

    def get_upload_data(self):
        return [
            [ "path", self.source_path, self.target_path],
        ]

class DropboxPublicModelShare(DropboxGenericShare):
    def __init__(self, shotPublicFolder, model = None):
        super().__init__()
        self.shotPublicFolder = shotPublicFolder
        self.model = model
        if model is not None:
            self.name = self.model.filename
            self.source_path = self.model.get_path()
            self.target_path = "/public/%s/%s" % (self._clean_for_filesystem(self.shotPublicFolder.name), self.model.filename)
        else:
            self.name = ""
            self.source_path = ""
            self.target_path = ""
        self.url = ""

    def delete(self):
        if self.model is not None:
            self.model.set_publishing_status("state_changing")
        t = threading.Thread(target=self._delete_thread, daemon=True)
        t.run()

    def _delete_thread(self):
        self.shotPublicFolder.parent_shot.parent_shots.dropboxUploads.remove_from_uploadqueue(self)
        self.set_status("deleting")
        self.shotPublicFolder.notify_observers()
        old_status = self.status
        try:
            with dropbox.Dropbox(oauth2_refresh_token=self.shotPublicFolder.parent_shot.settingsInstance.settingsDropbox.refresh_token, app_key=self.shotPublicFolder.parent_shot.settingsInstance.settingsDropbox.app_key) as dbx:
                try:
                    dbx.files_delete_v2(self.target_path)
                except:
                    pass
                self.shotPublicFolder.uploads.remove(self)
                if self.model is not None:
                    self.model.set_publishing_status("can_publish")
        except:
            self.set_status(old_status)
            if self.model is not None:
                self.model.set_publishing_status("can_unpublish")
        self.save()
        self.notify_observers()
        self.shotPublicFolder.notify_observers()

    def to_dict(self):
        d = super().to_dict()
        if self.model is not None:
            d["model_id"] = self.model.model_id
        else:
            d["model_id"] = None
        d["name"] = self.name
        return d

    def from_dict(self, data):
        super().from_dict(data)
        self.name = data["name"]
        return self

    def save(self):
        self.shotPublicFolder.save()

class DropboxPublicImagesShare(DropboxGenericShare):
    def __init__(self, shotPublicFolder):
        super().__init__()
        self.shotPublicFolder = shotPublicFolder
        self.name = "Images"
        self.shot = self.shotPublicFolder.parent_shot
        self.source_path = self.shot.images_path
        f = self._clean_for_filesystem(self.shotPublicFolder.name)
        n = self._clean_for_filesystem(self.shot.name)
        if f != n:
            self.target_path = "/public/%s/%s_Images" % (f ,n)
            self.name = "%s Images" % n
        else:
            self.target_path = "/public/%s/Images" % (f)
        self.url = ""

    def delete(self):
        self.shotPublicFolder.parent_shot.set_publishing_status("state_changing")
        t = threading.Thread(target=self._delete_thread, daemon=True)
        t.run()

    def _delete_thread(self):
        self.shotPublicFolder.parent_shot.parent_shots.dropboxUploads.remove_from_uploadqueue(self)
        old_status = self.status
        self.set_status("deleting")
        self.shotPublicFolder.notify_observers()

        try:
            with dropbox.Dropbox(oauth2_refresh_token=self.shotPublicFolder.parent_shot.settingsInstance.settingsDropbox.refresh_token, app_key=self.shotPublicFolder.parent_shot.settingsInstance.settingsDropbox.app_key) as dbx:
                try:
                    dbx.files_delete_v2(self.target_path)
                except:
                    pass
                self.shotPublicFolder.uploads.remove(self)
                self.shotPublicFolder.parent_shot.set_publishing_status("can_publish")
                self.shotPublicFolder.notify_observers()
                self.shotPublicFolder.parent_shot.notify_observers()
        except:
            self.shotPublicFolder.parent_shot.set_publishing_status("can_unpublish")
            self.set_status(old_status)
        self.save()
        self.notify_observers()
        self.shotPublicFolder.notify_observers()

    def to_dict(self):
        d = super().to_dict()
        return d

    def save(self):
        self.shotPublicFolder.save()


class DropboxPrivateImagesShare(DropboxGenericShare):
    def __init__(self, shot):
        super().__init__()
        self.shot = shot
        self.status = "idle"
        self.name = "ImagesAndMetadata"

    def upload(self):
        self.set_status("pending")
        self.shot.parent_shots.dropboxUploads.add_to_uploadqueue(self)

    def save(self):
        self.shot.save()

    def get_upload_data(self):
        self.source_path = self.shot.images_path
        self.shot = self.shot
        l = self._clean_for_filesystem(self.shot.meta_location)
        n = self._clean_for_filesystem(self.shot.name.replace(":", "").replace(self.shot.shot_id, "").replace(self.shot.shot_id.split(" ")[0], "").replace(self.shot.shot_id.split(" ")[-1], ""))
        if len(l) > 0:
            l = "%s " % l
        if len(n) > 0:
            n = " %s" % n
        self.target_path = "/private/%s%s%s/" % (l, self.shot.shot_id, n)

        data = super().get_upload_data()
        metadata = json.dumps({
            "name": self.shot.name,
            "comment": self.shot.comment,
            "meta_location": self.shot.meta_location,
            "meta_max_rows": self.shot.meta_max_rows,
            "meta_max_segments": self.shot.meta_max_segments,
            "meta_rotation": self.shot.meta_rotation,
            "meta_camera_one_position": self.shot.meta_camera_one_position,
        }).encode("UTF-8")
        data.append([ "data",metadata, "%s/%s" % (self.target_path, "metadata.json")])
        return data

    def to_dict(self):
        d = super().to_dict()
        return d

    def from_dict(self, data):
        d = super().from_dict(data)
        if d.status == "pending":
            self.shot.parent_shots.dropboxUploads.add_to_uploadqueue(self)
        return d