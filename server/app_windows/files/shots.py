import glob
import json
import os
from pyhtmlgui import ObservableList

from app_windows.files.shot import Shot

# All local and remote Shots
class Shots:
    def __init__(self):
        self.shots = ObservableList()
        self.path = "c:\\my_shots"
        if not os.path.exists(self.path):
            os.mkdir(self.path)
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
            self.load_shot_from_disk(path, do_sort=False)
        self.shots.sort(reverse=True)

    def load_shot_from_disk(self, path, do_sort = True):
        if os.path.exists(os.path.join(path, "metadata.json")) or os.path.exists( os.path.join(path, "images", "normal")) or (  os.path.exists(os.path.join(path, "normal")) and os.path.exists(os.path.join(path, "projection"))):
            shot_id = os.path.split(path)[1]
            shot = self.get(shot_id)
            if shot is None:
                shot = Shot(path, shot_id)
                self.shots.append(shot)
            else:
                shot.load()
            if do_sort is True:
                self.shots.sort(reverse=True)
            return shot
        return None

_shotsInstance = None


def ShotsInstance():
    global _shotsInstance
    if _shotsInstance is None:
        _shotsInstance = Shots()
    return _shotsInstance
