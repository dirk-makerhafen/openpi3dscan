import datetime
import json
import os,sys, dropbox
import threading
import time
import unicodedata
from dropbox import files, exceptions
import six
from pyhtmlgui import Observable

from app.settings.settings import SettingsInstance
from app_windows.files.shots import ShotsInstance


class ShotsDropboxDownload(Observable):
    def __init__(self):
        super().__init__()
        self.dropbox = None
        self.last_success = None
        self.last_failed = None
        self.last_checked = None
        self.all_in_sync = True
        self.status = "idle"
        self.current_download_file = ""
        self.worker = None

    def to_dict(self):
        return {
            "last_success": self.last_success,
            "last_failed": self.last_failed,
            "last_checked": self.last_checked,
        }

    def from_dict(self, data):
        self.last_success = data["last_success"]
        self.last_failed = data["last_failed"]
        self.last_checked = data["last_checked"]

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
        self.dropbox = dropbox.Dropbox(SettingsInstance().settingsDropbox.token)
        self.set_status("downloading")
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
        self.last_checked = time.time()
        all_in_sync = True

        source_dir = "/"
        listing = self._list_folder(source_dir)
        for name in listing:
            if not isinstance(listing[name], dropbox.files.FolderMetadata):
                continue
            sublisting = self._list_folder("%s/%s" % (source_dir, name))
            print(sublisting)
            if "metadata.json" in sublisting:
                print("metadata exists")
                files_to_download = []
                if not os.path.exists(os.path.join(ShotsInstance().path, name, "metadata.json")):
                    files_to_download.append([ "%s/%s/metadata.json" % (source_dir, name) , os.path.join(ShotsInstance().path, name, "metadata.json") ])
                for imgtype in ["normal", "projection"]:
                    imageslisting = self._list_folder("%s/%s/%s" % (source_dir, name, imgtype))
                    for imagename in imageslisting:
                        if not isinstance(imageslisting[imagename], dropbox.files.FileMetadata):
                            continue
                        if not os.path.exists(os.path.join(ShotsInstance().path, name, "images",  imgtype, imagename)):
                            files_to_download.append(["%s/%s/%s/%s" % (source_dir, name, imgtype, imagename), os.path.join(ShotsInstance().path, name, "images", imgtype, imagename) ])
                all_success = True
                print(files_to_download)
                for file_to_download in files_to_download:
                    source, destination = file_to_download
                    result = self.download(source,destination)
                    if result is False:
                        all_success = False

                if all_success is True:
                    ShotsInstance().load_shot_from_disk(os.path.join(ShotsInstance().path, name))
                    #self.dropbox.files_delete_v2("%s/%s" % (source_dir, name))
                else:
                    all_in_sync = False
            else:
                all_in_sync = False
        self.all_in_sync = all_in_sync

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

    def download(self, source, destination):
        source = source.replace(os.path.sep, '/')
        while '//' in source:
            source = source.replace('//', '/')
        self.current_download_file = source.split("/")[-1]
        self.notify_observers()
        try:
            md, res = self.dropbox.files_download(source)
        except Exception as e:
            print('Download error', e)
            return False
        finally:
            self.current_download_file = ""
            self.notify_observers()
        destination_dir = os.path.dirname(os.path.abspath(destination))
        os.makedirs(destination_dir, exist_ok=True)
        with open(destination,"wb") as f:
            f.write(res.content)

        return True

    def check_apitoken(self):
        try:
            res = self.dropbox.files_list_folder("")
            return True
        except Exception as e:
            print(e)
        return False



_shotsDropboxDownloadInstance = None

def ShotsDropboxDownloadInstance():
    global _shotsDropboxDownloadInstance
    if _shotsDropboxDownloadInstance is None:
        _shotsDropboxDownloadInstance = ShotsDropboxDownload()
    return _shotsDropboxDownloadInstance
