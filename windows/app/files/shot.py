import glob
import json
import multiprocessing
import os
import random
import re
import shutil
import threading
from multiprocessing.pool import ThreadPool
from multiprocessing import Process

import gevent
from PIL import Image
from gevent.fileobject import FileObjectThread
from pyhtmlgui import Observable
from pyhtmlgui import ObservableList

from app.files.modelFile import ModelFile
from app.settings.settings import SettingsInstance

SyncThreadPool = ThreadPool(8)

class Shot(Observable):
    def __init__(self, shot_dir, shot_id):
        super().__init__()
        self.shot_id = shot_id
        self.name = self.shot_id
        self.status = ""
        self.comment = ""
        #metadata
        self.meta_location = ""
        self.meta_max_segments = 16
        self.meta_max_rows = 7
        self.meta_rotation = 0
        self.meta_camera_one_position = "top"

        self.nr_of_files = 0
        self.path = os.path.join(shot_dir, self.shot_id)
        self.models = ObservableList()
        self.load()
        self.count_number_of_files()

    @property
    def nr_of_models(self):
        return len(self.models)

    @property
    def nr_of_models_waiting(self):
        return len([m for m in self.models if m.status == "waiting"])
    @property
    def nr_of_models_waiting_or_processing(self):
        return len([m for m in self.models if m.status == "waiting" or m.status == "processing" ])

    @property
    def nr_of_models_failed(self):
        return len([m for m in self.models if m.status == "failed"])

    def set_name(self, name):
        if self.name == name:
            return
        self.name = name
        self.save()
        self.backup_meta()
        self.notify_observers()

    def set_comment(self, comment):
        if self.comment == comment:
            return
        self.comment = comment
        self.save()
        self.backup_meta()
        self.notify_observers()

    def delete(self):
        if os.path.exists(self.path):
            shutil.rmtree(self.path)

    # image_mode = normal | preview , image_type = normal | projection
    def get_image(self, image_type, image_mode, segment, row):
        if image_mode == "normal":
            folder_name = "images"
        else:
            folder_name = "preview_images"
        img_path = os.path.join(self.path, folder_name, image_type, "seg%s-cam%s-%s.jpg" % (segment, row, image_type[0]))
        if os.path.exists(img_path):
            with open(img_path, "rb") as f:
                return f.read()
        return None

    def create_model(self, filetype="obj", reconstruction_quality="high", quality="high", create_mesh_from="projection", create_textures=False):
        model = self.get_model(filetype=filetype, reconstruction_quality=reconstruction_quality, quality=quality, create_mesh_from=create_mesh_from, create_textures=create_textures)
        if model is not None:
            if model.status == "failed":
                model.delete()
                model = None
        if model is None:
            self.models.append(ModelFile(self, filetype=filetype, reconstruction_quality=reconstruction_quality, quality=quality, create_mesh_from=create_mesh_from, create_textures=create_textures))
            self.save()
        self.notify_observers()

    def get_model(self, filetype="obj", reconstruction_quality="high", quality="high", create_mesh_from="projection", create_textures=False):
        try:
            return [m for m in self.models if m.filetype == filetype and m.quality == quality and m.reconstruction_quality == reconstruction_quality and m.create_mesh_from == create_mesh_from and m.create_textures == create_textures][0]
        except:
            return None

    def get_models_by_status(self, status):
        return [m for m in self.models if m.status == status]

    def get_models_by_filetype(self, filetype):
        return [m for m in self.models if m.filetype == filetype]

    def get_model_by_id(self, model_id):
        try:
            return [m for m in self.models if m.model_id == model_id][0]
        except:
            return None

    def remove_model(self, model):
        self.models.remove(model)
        self.save()
        self.notify_observers()

    def count_number_of_files(self):
        self.nr_of_files = len(glob.glob(os.path.join(self.path, "images", "normal", "*.jpg"))) + len(glob.glob(os.path.join(self.path, "images", "projection", "*.jpg")))

    def save(self):
        if os.path.exists(self.path):
            with open(os.path.join(self.path, "metadata.json"), "w") as f:
                f.write(json.dumps({
                    "name": self.name,
                    "comment": self.comment,
                    "meta_location": self.meta_location,
                    "meta_max_rows": self.meta_max_rows,
                    "meta_max_segments": self.meta_max_segments,
                    "meta_rotation": self.meta_rotation,
                    "meta_camera_one_position": self.meta_camera_one_position,
                    "models" : [m.to_dict() for m in self.models]
                }))
        if not os.path.exists('/opt/openpi3dscan/meta/%s.json' % self.shot_id):
            self.backup_meta()

    def backup_meta(self):
        with open('/opt/openpi3dscan/meta/%s.json' % self.shot_id, "w") as f:
            f.write(json.dumps({
                "name": self.name,
                "comment": self.comment,
                "meta_location": self.meta_location,
                "meta_max_rows": self.meta_max_rows,
                "meta_max_segments": self.meta_max_segments,
                "meta_rotation": self.meta_rotation,
                "meta_camera_one_position": self.meta_camera_one_position,
            }))

    def load(self):
        if os.path.exists(os.path.join(self.path, "metadata.json")):
            try:
                with open(os.path.join(self.path, "metadata.json"), "r") as f:
                    data = json.loads(f.read())
                    self.name = data["name"]
                    self.comment = data["comment"]
                    try:
                        self.meta_location = data["meta_location"]
                        self.meta_max_rows = data["meta_max_rows"]
                        self.meta_max_segments = data["meta_max_segments"]
                        self.meta_rotation = data["meta_rotation"]
                        self.meta_camera_one_position = data["meta_camera_one_position"]
                    except:
                        pass
                    try:
                        self.models = ObservableList([ModelFile(self).from_dict(m) for m in data["models"]])
                    except:
                        pass
            except Exception as e:
                print("failed to load", e)
        elif os.path.exists('/opt/openpi3dscan/meta/%s.json' % self.shot_id):
            try:
                with open('/opt/openpi3dscan/meta/%s.json' % self.shot_id, "r") as f:
                    data = json.loads(f.read())
                    self.name = data["name"]
                    self.comment = data["comment"]
                    try:
                        self.meta_location = data["meta_location"]
                        self.meta_max_rows = data["meta_max_rows"]
                        self.meta_max_segments = data["meta_max_segments"]
                        self.meta_rotation = data["meta_rotation"]
                        self.meta_camera_one_position = data["meta_camera_one_position"]
                    except:
                        pass
            except Exception as e:
                print("failed to load1", e)
        self.path_exists = os.path.exists(self.path)
        if self.path_exists is True and self.nr_of_files == 0:
            self.count_number_of_files()

        self.notify_observers()

    def get_clean_shotname(self):
        name = self.name.replace("ä", "ae").replace("ü", "ue").replace("Ü", "Ue")
        name = name.replace("ö", "oe").replace("Ä", "Ae").replace("Ö", "Oe")
        name = re.sub('\s+', ' ', name)
        name = re.sub('[^A-Za-z0-9_. ]+', '', name)
        while ".." in name:
            name = name.replace("..", ".")
        while "__" in name:
            name = name.replace("__", "_")
        while "  " in name:
            name = name.replace("  ", " ")
        name = name.strip()
        while name[-1] in ["_", "."]:
            name = name[:-1].strip()
        while name[0] in ["_", "."]:
            name = name[1:].strip()
        return name

    def __eq__(self, other):
        return other is not None and self.shot_id == other.shot_id

    def __lt__(self, other):
        return other is not None and self.shot_id < other.shot_id
