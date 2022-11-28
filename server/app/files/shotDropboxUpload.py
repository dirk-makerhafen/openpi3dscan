import datetime
import json
import os,sys, dropbox
import threading
import time
import unicodedata

import six
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
        self.set_status("uploading")
        for i in range(3):
            try:
                self._sync()
            except Exception as e:
                print("failed sync", e)
                time.sleep(5)
                continue
            if self.all_in_sync is True:
                break
            time.sleep(5)
        self.set_status("idle")
        self.worker = None

    def _sync(self):
        self.dropbox = dropbox.Dropbox(SettingsInstance().settingsDropbox.token)
        self.last_checked = time.time()
        all_in_sync = True
        target_dir = "/%s/" % self.shot.shot_id
        for dn, dirs, files in os.walk(self.shot.images_path):
            subfolder = dn[len(self.shot.images_path):].strip(os.path.sep)
            listing = self._list_folder( "%s/%s" % (target_dir, subfolder))
            print('Descending into', subfolder)
            # First do all the files.
            for name in files:
                file_to_upload = os.path.join(dn, name)
                if not isinstance(name, six.text_type):
                    name = name.decode('utf-8')
                nname = unicodedata.normalize('NFC', name)
                if name.startswith('.') or name.startswith('@') or name.endswith('~') or name.endswith('.pyc') or name.endswith('.pyo'):
                    continue

                if nname in listing: # file exists in dropbox
                    mtime_dt = datetime.datetime(*time.gmtime(os.path.getmtime(file_to_upload))[:6])
                    size = os.path.getsize(file_to_upload)
                    if (isinstance(listing[nname], dropbox.files.FileMetadata) and mtime_dt == listing[nname].client_modified and size == listing[nname].size):
                        print(name, 'is already synced [stats match]')
                        continue
                res = self._upload_file(file_to_upload, "%s/%s/%s" % (target_dir, subfolder, name))
                if res is None:
                    all_in_sync = False
            # Then choose which subdirectories to traverse.
            keep = []
            for name in dirs:
                if name.startswith('.') or name.startswith('@') or name.endswith('~') or name == '__pycache__':
                    continue
                keep.append(name)
            dirs[:] = keep

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
                })
                , "%s/%s" % (target_dir, "metadata.json"))
            if res is None:
                all_in_sync = False

        self.all_in_sync = all_in_sync
        self.dropbox.close()
        if self.all_in_sync is True:
            self.last_success = time.time()
        else:
            self.last_failed = time.time()
        self.shot.save()

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
            print('Folder listing failed for', path, '-- assumed empty:', e)
            return {}
        else:
            rv = {}
            for entry in res.entries:
                rv[entry.name] = entry
            return rv

    def _upload_file(self, source, destination):
        with open(source, 'rb') as f:
            return self._upload_data(f.read(), destination)

    def _upload_data(self, data, destination):
        destination = '/%s' % destination.replace(os.path.sep, '/')
        while '//' in destination:
            destination = destination.replace('//', '/')
        self.current_upload_file = destination.split("/")[-1]
        self.notify_observers()
        try:
            res = self.dropbox.files_upload(data, destination, dropbox.files.WriteMode.overwrite, client_modified=datetime.datetime(*time.gmtime(time.time())[:6]), mute=True)
        except Exception as e:
            print('upload error', e)
            return None
        finally:
            self.current_upload_file = ""
            self.notify_observers()
        print('uploaded as', res.name.encode('utf8'))
        return res
