import datetime
import json
import os,sys, dropbox
import queue
import threading
import time
import unicodedata
import six
import re
from dropbox import exceptions, files
from pyhtmlgui import Observable, ObservableList
from dropbox import DropboxOAuth2FlowNoRedirect
import multiprocessing
try:
    multiprocessing.set_start_method("spawn")
except:
    pass
class DropboxUploaderProcess():
    def __init__(self, refresh_token, app_key, dtype, source, destination, result_queue ):
        self.refresh_token = refresh_token
        self.app_key = app_key
        self.dtype = dtype
        self.source = source
        self.destination = destination
        self.result_queue = result_queue
        self.dropbox = None

    def run(self):
        if self.login() == False:
            self.result_queue.put(False)
            return
        if self.dtype == "data":
            self.result_queue.put([os.path.split(self.destination)[1], 0])
            self._upload_data(self.source, self.destination)
        elif self.dtype == "path":
            if os.path.isdir(self.source):
                self._sync_folder(self.source, self.destination)
            else:
                self.result_queue.put([os.path.split(self.source)[1], 0])
                self._upload_file(self.source, self.destination)
        self.result_queue.put(True)

    def _sync_folder(self, source_dir, target_dir):
        files_to_upload = []
        for dn, dirs, files in os.walk(source_dir):
            subfolder = dn[len(source_dir):].strip(os.path.sep)
            listing = self._list_folder( "%s/%s" % (target_dir, subfolder))
            if listing is None:
                break
            for name in files:
                file_to_upload = os.path.join(dn, name)
                if not isinstance(name, six.text_type):
                    name = name.decode('utf-8')
                if name.startswith('.') or name.startswith('@') or name.endswith('~'):
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
        current_progress = 0
        for index, file_to_upload in enumerate(files_to_upload):
            source, destination = file_to_upload
            self.result_queue.put([ os.path.split(source)[1], current_progress])
            res = self._upload_file(source, destination)
            if res is None:
                all_in_sync = False
            current_progress = int(100 / len(files_to_upload) * (index+1))


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
        try:
            res = self.dropbox.files_upload(data, destination, dropbox.files.WriteMode.overwrite, client_modified=client_modified, mute=True)
        except Exception as e:
            print('upload error', e)
            return None
        return res

    def login(self):

        try:
            with dropbox.Dropbox(oauth2_refresh_token=self.refresh_token, app_key=self.app_key) as dbx:
                dbx.users_get_current_account()
                self.dropbox =  dbx
                return True
        except Exception as e:
            print('Error: %s' % (e,))
        return False


def _uploader_subprocess(input_queue):
    while True:
        task = input_queue.get()
        if task == None:
            return
        refresh_token, app_key, dtype, source, destination, result_queue = task
        uploader = DropboxUploaderProcess(refresh_token, app_key, dtype, source, destination, result_queue)
        try:
            uploader.run()
        except Exception as e:
            print("failed to upload", e)
            result_queue.put(False)

class DropboxUploads(Observable):
    def __init__(self, settings_instance):
        super().__init__()
        self.settings_instance = settings_instance
        self.pending_uploads = ObservableList()
        self.to_subprocess_queue = multiprocessing.Manager().Queue()
        #self._workers = multiprocessing.Pool(processes=1).apply_async(_uploader_subprocess, args=(self.to_subprocess_queue,))
        multiprocessing.Process(target=_uploader_subprocess, args=(self.to_subprocess_queue,), daemon=True).start()
        self._upload_thread = threading.Thread(target=self._loop, daemon=True).start()

    def add_to_uploadqueue(self, dropboxUploader):
        if dropboxUploader not in self.pending_uploads:
            self.pending_uploads.append(dropboxUploader)

    def remove_from_uploadqueue(self, dropboxUploader):
        if dropboxUploader in self.pending_uploads:
            self.pending_uploads.remove(dropboxUploader)


    def _loop(self):
        while True:
            if len(self.pending_uploads) == 0 or self.settings_instance.settingsDropbox.is_authorized() is False:
                print("waiting")
                time.sleep(6)
                continue
            try:
                pending_upload = self.pending_uploads[0]
                pending_upload.last_checked = time.time()
                pending_upload.set_status("uploading")
            except:
                continue
            pending_upload_datas = pending_upload.get_upload_data()
            all_in_sync = True
            for pending_upload_data in pending_upload_datas:
                dtype, source, destination = pending_upload_data
                result_queue =  multiprocessing.Manager().Queue()
                self.to_subprocess_queue.put([
                    self.settings_instance.settingsDropbox.refresh_token,
                    self.settings_instance.settingsDropbox.app_key,
                    dtype,
                    source,
                    destination,
                    result_queue
                ])
                while True:
                    result = result_queue.get()
                    if result == False:
                        all_in_sync = False
                    if result == True or result == False:
                        break
                    current_file, progress = result
                    pending_upload.current_upload_file = current_file
                    pending_upload.progress = progress
                    pending_upload.notify_observers()
                pending_upload.current_upload_file = ""
                pending_upload.notify_observers()
                if all_in_sync is False:
                    break
            if all_in_sync is True and pending_upload.url != None:
                try:
                    with dropbox.Dropbox(oauth2_refresh_token=self.settings_instance.settingsDropbox.refresh_token, app_key=self.settings_instance.settingsDropbox.app_key) as dbx:
                        pending_upload.url = dbx.sharing_create_shared_link_with_settings(pending_upload.target_path).url
                except Exception as e:
                    print(e)
                    all_in_sync = False

            pending_upload.all_in_sync = all_in_sync
            if all_in_sync is True:
                pending_upload.last_failed = None
                pending_upload.last_success = time.time()
                pending_upload.progress = 100
                pending_upload.set_status("online")
                self.pending_uploads.remove(pending_upload)
            else:
                pending_upload.last_failed = time.time()
                pending_upload.last_success = None
                pending_upload.set_status("pending")
                self.pending_uploads.remove(pending_upload)
                self.pending_uploads.append(pending_upload)
