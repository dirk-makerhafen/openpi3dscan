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
from app.files.shotPublicFolder import ShotDropboxPublicFolder
from app_windows.settings.settings import SettingsInstance

SyncThreadPool = ThreadPool(8)

class Shot(Observable):
    def __init__(self, shot_dir, shot_id, parent_shots):
        super().__init__()
        self.parent_shots = parent_shots
        self.settingsInstance = SettingsInstance()
        self.shot_id = shot_id
        self.name = self.shot_id
        self.status = ""
        self.publishing_status = "can_publish"  # can_publish, state_changing, can_unpublish
        self.comment = ""
        #metadata
        self.meta_location = ""
        self.meta_max_segments = 16
        self.meta_max_rows = 7
        self.meta_rotation = 0
        self.meta_camera_one_position = "top"
        self.license_data = ""
        self.nr_of_files = 0
        self.devices = None
        self.path = shot_dir
        self.worker = None
        self.models = ObservableList()
        self.path_exists = False
        self.images_path = os.path.join(self.path, "images")
        if os.path.exists(os.path.join(self.path, "normal")) and os.path.exists(os.path.join(self.path, "projection")):
            self.images_path = self.path
        self.preview_images_path = os.path.join(self.path, "preview_images")
        self.dropboxPublicFolder = ShotDropboxPublicFolder(self)
        self.load()


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

    @property
    def can_delete(self):
        if self.status == "sync":
            return False
        if self.dropboxPublicFolder.can_delete is False:
            return False
        return True

    def set_publishing_status(self, new_status):
        if self.publishing_status == new_status:
            return
        self.publishing_status = new_status
        self.notify_observers()



    def set_name(self, name):
        while "  " in name:
            name = name.replace("  ", " ")
        name = name.strip()
        if self.name == name:
            return
        self.name = name
        self.save()
        self.notify_observers()

    def set_comment(self, comment):
        while "  " in comment:
            comment = comment.replace("  ", " ")
        comment = comment.strip()
        if self.comment == comment:
            return
        self.comment = comment
        self.save()
        self.notify_observers()

    def set_location(self, location):
        if self.meta_location == location:
            return
        l = SettingsInstance().settingsLocations.get_by_location(location)
        if l is None:
            return

        self.meta_location = l.location
        self.meta_max_segments = l.segments
        self.meta_max_rows = l.cameras_per_segment
        self.meta_rotation = l.camera_rotation
        self.meta_camera_one_position = l.camera_one_position
        self.save()
        self.notify_observers()


    def delete(self):
        if self.can_delete is False:
            return
        if os.path.exists(self.path):
            shutil.rmtree(self.path)

    # image_mode = normal | preview , image_type = normal | projection
    def get_image(self, image_type, image_mode, segment, row):
        img_path = os.path.join(self.images_path, image_type, "seg%s-cam%s-%s.jpg" % (segment, row, image_type[0]))
        if image_mode == "preview":
            img_path_preview = os.path.join(self.preview_images_path, image_type, "seg%s-cam%s-%s.jpg" % (segment, row, image_type[0]))
            if not os.path.exists(img_path_preview) and os.path.exists(img_path):
                if not os.path.exists(self.preview_images_path):
                    os.mkdir(self.preview_images_path)
                if not os.path.exists(os.path.join(self.preview_images_path, image_type)):
                    os.mkdir(os.path.join(self.preview_images_path, image_type))

                img = Image.open(img_path)
                width, height = img.size
                if width > height:
                    resolution = [800, 600]
                else:
                    resolution = [600, 800]
                img = img.resize(resolution)
                img.save(img_path_preview, format="jpeg", quality=85)
            img_path = img_path_preview

        if os.path.exists(img_path):
            with open(img_path, "rb") as f:
                return f.read()

        return None

    def create_preview_images(self):
        if not os.path.exists(self.preview_images_path):
            os.mkdir(self.preview_images_path)

        for image_type in ["normal", "projection"]:
            if not os.path.exists(os.path.join(self.preview_images_path, image_type)):
                os.mkdir(os.path.join(self.preview_images_path, image_type))

            files = glob.glob(os.path.join(self.images_path, image_type, "*.jpg"))
            for image in files:
                fname = os.path.split(image)[1]
                preview_img = os.path.join(self.preview_images_path, image_type, fname)
                if not os.path.exists(preview_img):
                    img = Image.open(image)
                    width, height = img.size
                    if width > height:
                        resolution = [800, 600]
                    else:
                        resolution = [600, 800]
                    img = img.resize(resolution)
                    img.save(preview_img, format="jpeg", quality=85)

    def list_possible_images(self, image_type, image_mode):
        if image_mode == "normal":
            files = glob.glob(os.path.join(self.images_path, image_type, "*.jpg"))
        else:
            files = glob.glob(os.path.join(self.preview_images_path, image_type, "*.jpg"))

        results = []
        for file in files:
            segment = os.path.split(file)[1].split("-")[0].replace("seg","")
            row = os.path.split(file)[1].split("-")[1].replace("cam","")
            results.append([image_type, image_mode, segment, row, ])

        return results

    def create_model(self, filetype="obj", reconstruction_quality="high", quality="high", create_mesh_from="projection", create_textures=False, lit=True):
        if self.meta_location == "":
            return
        model = self.get_model(filetype=filetype, reconstruction_quality=reconstruction_quality, quality=quality, create_mesh_from=create_mesh_from, create_textures=create_textures, lit=lit)
        if model is not None:
            if model.status == "failed":
                model.delete()
                model = None
        if model is None:
            model = ModelFile(self, filetype=filetype, reconstruction_quality=reconstruction_quality, quality=quality, create_mesh_from=create_mesh_from, create_textures=create_textures, lit=lit)
            self.parent_shots.unprocessed_models.append(model)
            self.models.append(model)
            self.save()

    def create_models_from_set(self, set_name):
        model_templates = SettingsInstance().realityCaptureSettings.settingsDefaultModelSets.get_models_by_setname(set_name)
        for model_template in model_templates:
            self.create_model(
                filetype=model_template.filetype,
                reconstruction_quality=model_template.reconstruction_quality,
                quality=model_template.export_quality,
                create_mesh_from=model_template.create_mesh_from,
                create_textures=model_template.create_textures,
                lit=model_template.lit
            )

    def get_model(self, filetype="obj", reconstruction_quality="high", quality="high", create_mesh_from="projection", create_textures=False, lit=True):
        try:
            return [m for m in self.models if m.filetype == filetype and m.quality == quality and m.reconstruction_quality == reconstruction_quality and m.create_mesh_from == create_mesh_from and m.create_textures == create_textures and m.lit == lit][0]
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
        if model in self.parent_shots.unprocessed_models:
            self.parent_shots.unprocessed_models.remove(model)
        self.save()

    def count_number_of_files(self):
        self.nr_of_files = len(glob.glob(os.path.join(self.images_path, "normal", "*.jpg"))) + len(glob.glob(os.path.join(self.images_path, "projection", "*.jpg")))

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
                    "license_data": self.license_data,
                    "meta_camera_one_position": self.meta_camera_one_position,
                    "models" : [m.to_dict() for m in self.models],
                    "dropboxPublicFolder": self.dropboxPublicFolder.to_dict(),
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
                        self.license_data = data["license_data"]
                    except:
                        pass
                    try:
                        self.models = ObservableList([ModelFile(self).from_dict(m) for m in data["models"]])
                    except:
                        pass
                    try:
                        self.dropboxPublicFolder.from_dict(data["dropboxPublicFolder"])
                        print("here")
                    except:
                        pass
            except Exception as e:
                print("failed to load %s" % os.path.join(self.path, "metadata.json"), e)

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
