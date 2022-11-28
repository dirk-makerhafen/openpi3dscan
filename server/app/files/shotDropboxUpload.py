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


class ShotDropboxUpload(Observable):
    def __init__(self, shot):
        super().__init__()
        self.shot = shot
        self.dropbox = None
        self.last_success = None
        self.last_failed = None
        self.last_checked = None
        self.all_in_sync = False
        self.status = "idle"
        self.current_upload_file = ""
        self.current_progress = 0
        self.worker = None

    def to_dict(self):
        return {
            "last_success": self.last_success,
            "last_failed": self.last_failed,
            "last_checked": self.last_checked,
            "all_in_sync": self.all_in_sync,
        }
    def from_dict(self, data):
        self.last_success = data["last_success"]
        self.last_failed = data["last_failed"]
        self.last_checked = data["last_checked"]
        self.all_in_sync = data["all_in_sync"]
        self.notify_observers()

    def sync(self):
        if SettingsInstance().settingsDropbox.enabled is True and SettingsInstance().settingsDropbox.token != "":
            if self.worker is None:
                self.worker = threading.Thread(target=self._sync_thread, daemon=True)
                self.worker.start()

    def set_status(self, new_status):
        if new_status != self.status:
            self.status = new_status
            self.notify_observers()

    def _sync_thread(self):
        self.shot._sync_remote()
        self.dropbox = dropbox.Dropbox(SettingsInstance().settingsDropbox.token)
        self.set_status("uploading")
        if self.check_apitoken() is False:
            self.last_success = None
            self.last_failed = int(time.time())
            self.set_status("idle")
            self.dropbox.close()
            return
        for i in range(3):
            try:
                self._sync()
            except Exception as e:
                print("failed sync", e)
                self.last_success = None
                self.last_failed = int(time.time())
                time.sleep(5)
                continue
            if self.all_in_sync is True:
                break
            time.sleep(5)
        self.dropbox.close()
        self.set_status("idle")
        self.worker = None

    def _sync(self):
        self.last_checked = int(time.time())
        self.current_progress = 0
        self.notify_observers()
        l = self._clean_for_filesystem(SettingsInstance().settingsScanner.location)
        n = self._clean_for_filesystem(self.shot.name.replace(":","").replace(self.shot.shot_id,"").replace(self.shot.shot_id.split(" ")[0],"").replace(self.shot.shot_id.split(" ")[-1],""))
        if len(l) > 0:
            l = "%s " % l
        target_dir = "/%s%s %s/" % (l, self.shot.shot_id, n)
        files_to_upload = []
        for dn, dirs, files in os.walk(self.shot.images_path):
            subfolder = dn[len(self.shot.images_path):].strip(os.path.sep)
            listing = self._list_folder( "%s/%s" % (target_dir, subfolder))
            if listing is None:
                break
            for name in files:
                file_to_upload = os.path.join(dn, name)
                if not isinstance(name, six.text_type):
                    name = name.decode('utf-8')
                if name.startswith('.') or name.startswith('@') or name.endswith('~') or name.endswith('.pyc') or name.endswith('.pyo'):
                    continue
                nname = unicodedata.normalize('NFC', name)
                if nname in listing \
                    and isinstance(listing[nname], dropbox.files.FileMetadata) \
                    and os.path.getsize(file_to_upload) == listing[nname].size: # file exists in dropbox
                        continue
                files_to_upload.append([file_to_upload, "%s/%s/%s" % (target_dir, subfolder, name)])
            keep = []
            for name in dirs:
                if name.startswith('.') or name.startswith('@') or name.endswith('~') or name == '__pycache__':
                    continue
                keep.append(name)
            dirs[:] = keep

        all_in_sync = True
        for index, file_to_upload in enumerate(files_to_upload):
            self.current_progress = int(100 / len(files_to_upload) * (index+1))
            source, destination = file_to_upload
            res = self._upload_file(source, destination)
            if res is None:
                all_in_sync = False

        if all_in_sync is True:
            res = self._upload_data(
                json.dumps({
                    "name": self.shot.name,
                    "comment": self.shot.comment,
                    "meta_location": self.shot.meta_location,
                    "meta_max_rows": self.shot.meta_max_rows,
                    "meta_max_segments": self.shot.meta_max_segments,
                    "meta_rotation": self.shot.meta_rotation,
                    "meta_camera_one_position": self.shot.meta_camera_one_position,
                }).encode("UTF-8")
                , "%s/%s" % (target_dir, "metadata.json"))
            if res is None:
                all_in_sync = False

        self.all_in_sync = all_in_sync

        if self.all_in_sync is True:
            self.last_success = int(time.time())
            self.last_failed = None
        else:
            self.last_failed = int(time.time())
            self.last_success = None
        self.shot.save()

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

    def _list_folder(self, path):
        """List a folder.
        Return a dict mapping unicode filenames to FileMetadata|FolderMetadata entries.
        """
        path = '/%s' % path.replace(os.path.sep, '/')
        while '//' in path:
            path = path.replace('//', '/')
        path = path.rstrip('/')
        try:
            res = self.dropbox.files_list_folder(path)
        except Exception as e:
            if type(e) == dropbox.exceptions.AuthError:
                return None
            return {}
        else:
            rv = {}
            for entry in res.entries:
                rv[entry.name] = entry
            return rv

    def check_apitoken(self):
        try:
            res = self.dropbox.files_list_folder("")
            return True
        except Exception as e:
            print(e)
        return False

    def _upload_file(self, source, destination):
        with open(source, 'rb') as f:
            client_modified = datetime.datetime(*time.gmtime(os.path.getmtime(source))[:6])
            return self._upload_data(f.read(), destination, client_modified)

    def _upload_data(self, data, destination, client_modified = None):
        if client_modified is None:
            client_modified = datetime.datetime(*time.gmtime(int(time.time()))[:6])
        destination = '/%s' % destination.replace(os.path.sep, '/')
        while '//' in destination:
            destination = destination.replace('//', '/')
        self.current_upload_file = destination.split("/")[-1]
        self.notify_observers()
        try:
            res = self.dropbox.files_upload(data, destination, dropbox.files.WriteMode.overwrite, client_modified=client_modified, mute=True)
        except Exception as e:
            print('upload error', e)
            return None
        finally:
            self.current_upload_file = ""
            self.notify_observers()
        return res
