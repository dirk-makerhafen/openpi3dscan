import glob
import json
import os
from pyhtmlgui import ObservableList

from app_windows.files.shot import Shot
from app_windows.settings.settings import SettingsInstance

# All local and remote Shots
class Shots:
    def __init__(self):
        self.shots = ObservableList()
        #self.path = "c:\\my_shots"
        self.path = "/Users/Dirk 1/Downloads"
        self.cache = {}
        self.load_shots_from_disk()

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

    def delete(self, shot):
        if shot is not None:
            shot.delete()
            self.shots.remove(shot)
            try:
                del self.cache[shot.shot_id]
            except:
                pass
        else:
            print("shot not found")

    def get_unprocessed_models(self, limit = None):
        models = []
        for shot in self.shots:
            for m in shot.get_models_by_status("waiting"):
                models.append(m)
                if limit is not None and len(models) >= limit:
                    return models
        return models

    def load_shots_from_disk(self):
        for path in glob.glob(os.path.join(self.path, "*")):
            if os.path.exists(os.path.join(path, "metadata.json")) or os.path.exists(os.path.join(path, "images","normal")) or (os.path.exists(os.path.join(path, "normal")) and os.path.exists(os.path.join(path, "projection"))  ):
                shot_id = path.split("/")[-1]
                shot = self.get(shot_id)
                if shot is None:
                    self.shots.append(Shot(self.path, shot_id))
                else:
                    shot.load()
        self.shots.sort(reverse=True)


_shotsInstance = None


def ShotsInstance():
    global _shotsInstance
    if _shotsInstance is None:
        _shotsInstance = Shots()
    return _shotsInstance
