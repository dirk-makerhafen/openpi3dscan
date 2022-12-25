import os
import traceback

import dropbox
import threading
import time
from dropbox import files, exceptions
from pyhtmlgui import Observable
from app_windows.settings.settings import SettingsInstance
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
        self.current_download_shotid = ""
        self.current_download_file = ""
        self.current_progress = 0
        self.worker = None

        self._bg_thread = threading.Thread(target=self.bg_thread, daemon=True)
        self._bg_thread.start()

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

    def bg_thread(self):
        while True:
            if SettingsInstance().settingsDropbox.enabled \
            and SettingsInstance().settingsDropbox.refresh_token != "" \
            and SettingsInstance().settingsDropbox.auth_flow is None \
            and time.time() > SettingsInstance().settingsDropbox.next_sync_time:
                SettingsInstance().settingsDropbox.set_next_sync_time(time.time() + 1800)
                self.sync()
            time.sleep(60)
            self.notify_observers()

    def sync(self):
        if SettingsInstance().settingsDropbox.enabled is True and SettingsInstance().settingsDropbox.refresh_token != "":
            if self.worker is None:
                self.worker = threading.Thread(target=self._sync_thread, daemon=True)
                self.worker.start()

    def set_status(self, new_status):
        if new_status != self.status:
            self.status = new_status
            self.notify_observers()

    def _sync_thread(self):
        self.set_status("downloading")
        if self.login() is False:
            print("failed token")
            self.last_success = None
            self.last_failed = int(time.time())
            self.set_status("idle")
            self.worker = None
            return
        for i in range(3):
            try:
                self._sync()
            except Exception as e:
                print("failed sync", e)
                traceback.print_exc()
                self.last_success = None
                self.last_failed = int(time.time())
                time.sleep(5)
                continue
            if self.all_in_sync is True:
                break
            time.sleep(5)

        if self.all_in_sync is True:
            self.last_success = int(time.time())
            self.last_failed = None
        else:
            self.last_success = None
            self.last_failed = int(time.time())
        SettingsInstance().settingsDropbox.set_next_sync_time(time.time() + 1800)
        self.dropbox.close()
        self.set_status("idle")
        self.worker = None

    def _sync(self):
        self.last_checked = time.time()
        all_in_sync = True
        self.current_progress = 0
        self.notify_observers()
        source_dir = "/private"
        listing = self._list_folder(source_dir)
        for name in listing:
            if not isinstance(listing[name], dropbox.files.FolderMetadata):
                continue
            self.current_progress = 0
            self.notify_observers()
            sublisting = self._list_folder("%s/%s" % (source_dir, name))
            if "metadata.json" in sublisting:
                all_success = True
                self.current_download_shotid = name
                self.notify_observers()
                files_to_download = []
                if not os.path.exists(os.path.join(ShotsInstance().path, name, "metadata.json")):
                    result = self.download( "%s/%s/metadata.json" % (source_dir, name) , os.path.join(ShotsInstance().path, name, "metadata.json") )
                    if result is False:
                        all_success = False
                for imgtype in ["normal", "projection"]:
                    imageslisting = self._list_folder("%s/%s/%s" % (source_dir, name, imgtype))
                    for imagename in imageslisting:
                        if not isinstance(imageslisting[imagename], dropbox.files.FileMetadata):
                            continue
                        if not os.path.exists(os.path.join(ShotsInstance().path, name, "images",  imgtype, imagename)):
                            files_to_download.append(["%s/%s/%s/%s" % (source_dir, name, imgtype, imagename), os.path.join(ShotsInstance().path, name, "images", imgtype, imagename) ])
                shot = None
                if all_success is True:
                    shot = ShotsInstance().load_shot_from_disk(os.path.join(ShotsInstance().path, name))

                for index, file_to_download in enumerate(files_to_download):
                    self.current_progress = int(100 / len(files_to_download) * (index + 1))
                    source, destination = file_to_download
                    result = self.download(source,destination)
                    if result is False:
                        all_success = False
                    else:
                        if shot is not None:
                            shot.nr_of_files.value += 1
                self.current_progress =  100
                self.notify_observers()
                if all_success is True:
                    if shot is None:
                        shot = ShotsInstance().load_shot_from_disk(os.path.join(ShotsInstance().path, name))
                    shot.count_number_of_files()
                    shot.notify_observers()
                    shot.create_preview_images()
                    shot.save()
                    if shot.meta_location != "" and SettingsInstance().settingsLocations.get_by_location(shot.meta_location) == None:
                        location = SettingsInstance().settingsLocations.new_location()
                        location.location = shot.meta_location
                        location.segments = shot.meta_max_segments
                        location.cameras_per_segment = shot.meta_max_rows
                        location.camera_rotation = shot.meta_rotation
                        location.camera_one_position = shot.meta_camera_one_position
                        location.save()
                        location.notify_observers()
                    self.dropbox.files_delete_v2("%s/%s" % (source_dir, name))
                else:
                    all_in_sync = False

        self.current_download_shotid = ""
        self.notify_observers()
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

    def login(self):
        try:
            with dropbox.Dropbox(oauth2_refresh_token=SettingsInstance().settingsDropbox.refresh_token, app_key=SettingsInstance().settingsDropbox.app_key) as dbx:
                dbx.users_get_current_account()
                self.dropbox = dbx
                return True
        except Exception as e:
            print('Error: %s' % (e,))
        return False



_shotsDropboxDownloadInstance = None

def ShotsDropboxDownloadInstance():
    global _shotsDropboxDownloadInstance
    if _shotsDropboxDownloadInstance is None:
        _shotsDropboxDownloadInstance = ShotsDropboxDownload()
    return _shotsDropboxDownloadInstance
