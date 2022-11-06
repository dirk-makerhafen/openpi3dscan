import glob
import os
import re
import shutil

from pyhtmlgui import Observable, ObservableList


class SettingsCache(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.save = parent.save
        self.directory = "c:\\rc_cache"
        self.size = 10

    def set_size(self, new_size):
        new_size = int(new_size)
        if new_size < 0:
            new_size = 0
        if self.size == new_size:
            return
        self.size = new_size
        self.clean()

    def to_dict(self):
        return {
            "directory": self.directory,
            "size": self.size,
        }

    def from_dict(self, data):
        self.directory = data["directory"]
        self.size = data["size"]
        return self

    def clean(self):
        shots = []
        for path in glob.glob(os.path.join(self.directory, "*")):
            if os.path.exists(os.path.join(path, "last_usage")):
                with open(os.path.join(path, "last_usage"), "r") as f:
                    try:
                        shots.append([int(f.read()), path])
                    except:
                        pass
        shots.sort()
        while len(shots) > self.size:
            shutil.rmtree(shots[0][1])
            del shots[0]

    def clear_all(self):
        for path in glob.glob(os.path.join(self.directory, "*")):
            if os.path.exists(os.path.join(path, "last_usage")):
                try:
                    shutil.rmtree(path)
                except:
                    pass