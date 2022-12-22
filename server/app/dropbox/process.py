import datetime
import os,sys, dropbox
import queue
import threading
import time
import unicodedata
import six
from dropbox import exceptions, files
from pyhtmlgui import Observable, ObservableList
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
        self.total_upload_bytes = 0
        self.total_uploaded_bytes = 0

    def run(self):
        if self.login() == False:
            self.result_queue.put(False)
            return
        self.total_uploaded_bytes = 0
        if self.dtype == "data":
            self.total_upload_bytes = len(self.source)
            self.result_queue.put([os.path.split(self.destination)[1], 0])
            if self._upload_data(self.source, self.destination) is not None:
                self.total_uploaded_bytes += self.total_upload_bytes
        elif self.dtype == "path":
            if os.path.isdir(self.source):
                self._sync_folder(self.source, self.destination)
            else:
                self.total_upload_bytes = os.path.getsize(self.source)
                self._upload_file(self.source, self.destination)
        self.result_queue.put(True)

    def _sync_folder(self, source_dir, target_dir):
        files_to_upload = []
        self.total_upload_bytes = 0
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
                s = os.path.getsize(file_to_upload)
                self.total_upload_bytes += s
                if nname in listing \
                    and isinstance(listing[nname], dropbox.files.FileMetadata) \
                    and  s == listing[nname].size: # file exists in dropbox
                        self.total_uploaded_bytes  += s
                        continue
                files_to_upload.append([file_to_upload, "%s/%s/%s" % (target_dir, subfolder, name)])
            keep = []
            for name in dirs:
                if name.startswith('.') or name.startswith('@') or name.endswith('~') or name == '__pycache__':
                    continue
                keep.append(name)
            dirs[:] = keep
        self.result_queue.put(  ["", int(100.0 / self.total_upload_bytes * self.total_uploaded_bytes)])
        all_in_sync = True
        for index, file_to_upload in enumerate(files_to_upload):
            source, destination = file_to_upload
            res = self._upload_file(source, destination)
            if res is None:
                all_in_sync = False
        return all_in_sync

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
        destination = '/%s' % destination.replace(os.path.sep, '/')
        while '//' in destination:
            destination = destination.replace('//', '/')
        client_modified = datetime.datetime(*time.gmtime(os.path.getmtime(source))[:6])
        file_size = os.path.getsize(source)
        chunk_size =  8 * 1024 * 1024
        with open(source, 'rb') as f:
            if file_size < chunk_size: # small files
                if self._upload_data(f.read(), destination, client_modified) is not None:
                    self.total_uploaded_bytes += file_size
                    self.result_queue.put([os.path.split(source)[1], int(100.0 / self.total_upload_bytes * self.total_uploaded_bytes)])
            else:
                try:
                    upload_session_start_result = self.dropbox.files_upload_session_start(f.read(chunk_size))
                    cursor = dropbox.files.UploadSessionCursor(
                        session_id=upload_session_start_result.session_id,
                        offset=f.tell(),
                    )
                    commit = dropbox.files.CommitInfo(path=destination)
                    while f.tell() < file_size:
                        rest = file_size - f.tell()
                        if (rest) <= chunk_size:
                            print(self.dropbox.files_upload_session_finish(f.read(chunk_size), cursor, commit )  )
                            self.total_uploaded_bytes += rest
                        else:
                            self.dropbox.files_upload_session_append(f.read(chunk_size),cursor.session_id,cursor.offset,)
                            cursor.offset = f.tell()
                            self.total_uploaded_bytes += chunk_size
                        self.result_queue.put([os.path.split(source)[1], int(100.0 / self.total_upload_bytes * self.total_uploaded_bytes)])

                except Exception as e:
                    print("failed to upload", e)

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
                if dbx.check_user("pong").result != "pong":
                    raise Exception("Dropbox login failed")
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
    def __init__(self, shots, settings_instance):
        super().__init__()
        self.shots = shots
        self.settings_instance = settings_instance
        self.pending_uploads = ObservableList()
        self.to_subprocess_queue = multiprocessing.Manager().Queue()
        #self.to_subprocess_queue = queue.Queue()
        ##self._workers = multiprocessing.Pool(processes=1).apply_async(_uploader_subprocess, args=(self.to_subprocess_queue,))
        multiprocessing.Process(target=_uploader_subprocess, args=(self.to_subprocess_queue,), daemon=True).start()
        #self._uploader_thread = threading.Thread(target=_uploader_subprocess, args=[self.to_subprocess_queue],  daemon=True).start()
        self._upload_thread = threading.Thread(target=self._loop, daemon=True).start()
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True).start()

    def add_to_uploadqueue(self, dropboxUploader):
        if dropboxUploader not in self.pending_uploads:
            self.pending_uploads.append(dropboxUploader)

    def remove_from_uploadqueue(self, dropboxUploader):
        if dropboxUploader in self.pending_uploads:
            self.pending_uploads.remove(dropboxUploader)

    def _cleanup_loop(self):
        time.sleep(10)
        while True:
            for shot in self.shots.shots:
                pf = shot.dropboxPublicFolder
                if pf.expire_time != 0 and pf.expire_time < time.time():
                    if pf.can_delete is True:
                        pf.delete()
            time.sleep(3600)

    def _loop(self):
        time.sleep(30)
        while True:
            if len(self.pending_uploads) == 0 or self.settings_instance.settingsDropbox.is_authorized() is False:
                time.sleep(6)
                continue
            try:
                pending_upload = self.pending_uploads[0]
                pending_upload.last_checked = time.time()
                pending_upload.set_status("uploading")
                if hasattr(pending_upload, "model") and pending_upload.model is not None:
                    pending_upload.model.set_publishing_status("state_changing")
                if hasattr(pending_upload, "shot") and pending_upload.shot is not None and pending_upload.name != "ImagesAndMetadata":
                    pending_upload.shot.set_publishing_status("state_changing")
                if hasattr(pending_upload, "shotPublicFolder"):
                    pending_upload.shotPublicFolder.notify_observers()

            except:
                continue
            pending_upload_datas = pending_upload.get_upload_data()
            all_in_sync = True
            for pending_upload_data in pending_upload_datas:
                dtype, source, destination = pending_upload_data
                #result_queue =  multiprocessing.Manager().Queue()
                result_queue =  queue.Queue()
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
            if hasattr(pending_upload, "model"):
                pending_upload.model.set_publishing_status("can_unpublish")
            if hasattr(pending_upload, "shot") and pending_upload.name != "ImagesAndMetadata":
                pending_upload.shot.set_publishing_status("can_unpublish")
            if hasattr(pending_upload, "shotPublicFolder"):
                pending_upload.shotPublicFolder.notify_observers()
