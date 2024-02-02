import glob
import json
import os
import subprocess
from pyhtmlgui import ObservableList

from app.files.shot import Shot
from app.settings.settings import SettingsInstance
from app.dropbox.process import DropboxUploads


class Shots:
    def __init__(self, devices):
        self.shots = ObservableList()
        self.cache = {}
        self.devices = devices
        self.deleted_shot_ids = []
        self.unprocessed_models = []
        self.settingsInstance = SettingsInstance()
        self.dropboxUploads = DropboxUploads(self, SettingsInstance())
        self.load()

    @property
    def path(self):
        return os.path.join("/shots/", self.settingsInstance.primary_disk)

    def create(self, shot_id, name):
        try:
            stdout = subprocess.check_output('mount | grep %s' % self.path, shell=True, timeout=10, stderr=subprocess.STDOUT, ).decode("UTF-8")
        except:
            stdout = ""
        if self.path not in stdout:
            return None
        try:
            stdout = subprocess.check_output('lsblk -bfpro MOUNTPOINT,FSAVAIL | grep %s' % self.path, shell=True, timeout=10, stderr=subprocess.STDOUT, ).decode("UTF-8")
        except:
            stdout = ""
        line = stdout.split("\n")[0]
        while "  " in line:
            line = line.replace("  ", " ")
        try:
            mp, fsavail = line.split(" ")
            if int(fsavail) < 10*1024*1024*1024:
                return None
        except:
            pass

        s = Shot(os.path.join(self.path, shot_id), shot_id, self)
        s.meta_location = SettingsInstance().settingsScanner.location
        s.meta_max_segments = SettingsInstance().settingsScanner.segments
        s.meta_max_rows = SettingsInstance().settingsScanner.cameras_per_segment
        s.meta_rotation = SettingsInstance().settingsScanner.camera_rotation
        s.meta_camera_one_position = SettingsInstance().settingsScanner.camera_one_position
        s.create_folders()
        s.set_name(name)
        self.shots.insert(0, s)
        return s

    def get(self, shot_id):
        try:
            return self.cache[shot_id]
        except:
            pass
        try:
            v = [s for s in self.shots if s.shot_id == shot_id][0]
            self.cache[shot_id] = v
            return v
        except:
            pass
        return None

    def add(self, shot_id, device):
        if shot_id in self.deleted_shot_ids:
            device.camera.shots.delete(shot_id)
            return
        s = self.get(shot_id)
        if s is None:
            s = Shot(os.path.join(self.path, shot_id), shot_id, self)
            index = 0
            for i in range(len(self.shots)):
                index = i
                if self.shots[index] < s:
                    break
            self.shots.insert(index, s)
            self.cache[shot_id] = s
        s.add_device(device)
        return s

    def delete(self, shot):
        if shot is not None:
            shot.delete()
            self.shots.remove(shot)
            try:
                del self.cache[shot.shot_id]
            except:
                pass
            self._add_deleted_shot_id(shot.shot_id)
        else:
            print("shot not found")

    def sync_shotlist(self, shot_ids, device):
        for shot_id in shot_ids:
            self.add(shot_id, device)
        for shot in self.shots:
            if shot.shot_id not in shot_ids:
                shot.remove_device(device)

    def get_unprocessed_models(self, limit = 1):
        models = []
        while True:
            try:
                model = self.unprocessed_models[0]
            except:
                return models
            self.unprocessed_models.remove(model)
            if model.status == "waiting":
                models.append(model)
            if len(models) >= limit:
                return models

    def _add_deleted_shot_id(self, shot_id):
        if shot_id not in self.deleted_shot_ids:
            self.deleted_shot_ids.append(shot_id)
        self.deleted_shot_ids.sort()
        while len(self.deleted_shot_ids) >= 1000:
            del self.deleted_shot_ids[0]
        self.save()

    def save(self):
        with open("/opt/openpi3dscan/.shots.json", "w") as f:
            f.write(json.dumps({
                "deleted_shot_ids": self.deleted_shot_ids,
            }))

    def load(self):
        try:
            with open("/opt/openpi3dscan/.shots.json", "r") as f:
                data = json.loads(f.read())
                self.deleted_shot_ids = data["deleted_shot_ids"]
        except:
            pass

    def load_shots_from_dir(self, directory):
        loaded_cnt = 0
        for path in glob.glob(os.path.join(directory, "*")):
            if os.path.exists(os.path.join(path, "metadata.json")) or os.path.exists(os.path.join(path, "images","normal")) or (os.path.exists(os.path.join(path, "normal")) and os.path.exists(os.path.join(path, "projection"))  ):
                shot_id = os.path.split(path)[1]
                shot = self.get(shot_id)
                if shot is None:
                    shot = Shot(path, shot_id, self)
                    self.shots.append(shot)
                    loaded_cnt += 1
                    for model in shot.models:
                        if model.status == "waiting" and model not in self.unprocessed_models:
                            self.unprocessed_models.append(model)
        self.shots.sort(reverse=True)
        return loaded_cnt

    def unload_dir(self, directory):
        for shot in [s for s in self.shots]:
            if shot.path.startswith(directory):
                self.shots.remove(shot)
                try:
                    del self.cache[shot.shot_id]
                except:
                    pass

_shotsInstance = None


def ShotsInstance(devices=None):
    global _shotsInstance
    if _shotsInstance is None:
        _shotsInstance = Shots(devices)
    return _shotsInstance
