import glob
import json
import os
from pyhtmlgui import ObservableList

from app.files.shot import Shot
from app.settings.settings import SettingsInstance

SHOT_DIR = "/shots"

# All local and remote Shots
class Shots:
    def __init__(self):
        self.shots = ObservableList()
        self.path = "/shots/"
        self.cache = {}

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
        s = self.get(shot_id)
        if s is None:
            s = Shot(SHOT_DIR, shot_id)
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
        else:
            print("shot not found")

    def load_shots_from_disk(self):
        for path in glob.glob("/shots/*"):
            if os.path.exists(os.path.join(path, "metadata.json")) or os.path.exists(os.path.join(path, "images")) :
                shot_id = path.split("/")[-1]
                shot = self.get(shot_id)
                if shot is None:
                    self.shots.append(Shot(SHOT_DIR, shot_id))
                else:
                    shot.load()
        self.shots.sort()


_shotsInstance = None


def ShotsInstance():
    global _shotsInstance
    if _shotsInstance is None:
        _shotsInstance = Shots()
    return _shotsInstance
