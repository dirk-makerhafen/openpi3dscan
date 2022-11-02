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
        self.devices = set()
        self.path = os.path.join(shot_dir, self.shot_id)
        self.worker = None
        self.models = ObservableList()
        self.path_exists = False
        self.load()
        self.images_path         = os.path.join(self.path, "images")
        self.preview_images_path = os.path.join(self.path, "preview_images")
        if os.path.exists(self.path):
            self.path_exists = True
            if os.path.exists(os.path.join(self.path, "normal")) and os.path.exists(os.path.join(self.path, "projection")):
                self.images_path = self.path
            self.count_number_of_files()

    @property
    def nr_of_devices(self):
        return len(self.devices)

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

    def create_folders(self):
        if not os.path.exists(self.path):
            self.path_exists = True
            os.mkdir(self.path)
            os.mkdir(self.images_path)
            os.mkdir(os.path.join(self.images_path, "normal"))
            os.mkdir(os.path.join(self.images_path, "projection"))
            os.mkdir(self.preview_images_path)
            os.mkdir(os.path.join(self.preview_images_path, "normal"))
            os.mkdir(os.path.join(self.preview_images_path, "projection"))
            self.save()

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

    def add_device(self, device):
        if device not in self.devices:
            self.devices.add(device)
            self.notify_observers()

    def remove_device(self, device):
        if device in self.devices:
            self.devices.remove(device)
            self.notify_observers()

    def delete(self):
        for device in self.devices:
            device.camera.shots.delete(self.shot_id)
        if os.path.exists(self.path):
            shutil.rmtree(self.path)

    def sync_remote(self):
        if self.worker is None:
            self.worker = threading.Thread(target=self._sync_remote, daemon=True)
            self.worker.start()

    # image_mode = normal | preview, image_type = normal | projection
    def _sync_remote(self):
        self.status = "Sync"
        self.notify_observers()
        self.create_folders()
        tasks = []
        existing_images = glob.glob(os.path.join(self.images_path, "*", "*.jpg"))
        existing_images.extend(glob.glob(os.path.join(self.preview_images_path, "*", "*.jpg")))
        for device in [d for d in self.devices if d.status == "online"]:
            segment = device.name.split("-")[0].replace("SEG","")
            row = device.name.split("-")[1].replace("CAM","")
            for image_mode in ["normal", "preview"]:
                for image_type in ["normal", "projection"]:
                    if image_mode == "normal":
                        img_path = os.path.join(self.images_path, image_type, "seg%s-cam%s-%s.jpg" % (segment, row, image_type[0]))
                    else:
                        img_path = os.path.join(self.preview_images_path, image_type, "seg%s-cam%s-%s.jpg" % (segment, row, image_type[0]))

                    if img_path not in existing_images:
                        tasks.append([device, [self.shot_id, image_type, image_mode, False]])
        if len(tasks) > 0:
            random.shuffle(tasks)
            SyncThreadPool.map(lambda task: task[0].camera.shots.download(*task[1]), tasks)
            self.count_number_of_files()

        resolution = [800, 600] if SettingsInstance().settingsScanner.camera_rotation in [0, 180] else [600, 800]
        for image_type in ["normal", "projection"]:
            existing_images = glob.glob(os.path.join(self.images_path, image_type, "*.jpg"))
            existing_previews = glob.glob(os.path.join(self.preview_images_path, image_type, "*.jpg"))
            for existing_image in existing_images:
                preview_path = os.path.join(self.preview_images_path, image_type, existing_image.split("/")[-1])
                if preview_path not in existing_previews:
                    try:
                        img = Image.open(existing_image)
                        img = img.resize(resolution)
                        img.save(preview_path, format="jpeg", quality=85)
                    except:
                        print("Failed to create preview")
        self.status = ""
        self.worker = None
        self.notify_observers()

    # image_mode = normal | preview , image_type = normal | projection
    def get_image(self, image_type, image_mode, segment, row):
        if image_mode == "normal":
            img_path = os.path.join(self.images_path, image_type, "seg%s-cam%s-%s.jpg" % (segment, row, image_type[0]))
        else:
            img_path = os.path.join(self.preview_images_path, image_type, "seg%s-cam%s-%s.jpg" % (segment, row, image_type[0]))

        if os.path.exists(img_path):
            with open(img_path, "rb") as f:
                return f.read()
        try:
            device = [d for d in self.devices if d.name == "SEG%s-CAM%s" % (segment, row) and d.status == "online"][0]
        except:
            return None
        img = device.camera.shots.download(self.shot_id, image_type, image_mode=image_mode)
        if img is None or len(img) < 1000:
            return None
        return img

    def list_possible_images(self, image_type, image_mode):
        if image_mode == "normal":
            files = glob.glob(os.path.join(self.images_path, image_type, "*.jpg"))
        else:
            files = glob.glob(os.path.join(self.preview_images_path, image_type, "*.jpg"))

        results = []
        for file in files:
            segment = file.split("/")[-1].split("-")[0].replace("seg","")
            row = file.split("/")[-1].split("-")[1].replace("cam","")
            results.append([image_type, image_mode, segment, row, ])
        for device in self.devices:
            if device.status != "online":
                continue
            segment = device.name.split("-")[0].replace("SEG","")
            row = device.name.split("-")[1].replace("CAM","")
            try:
                [x for x in results if x[2] == segment and x[3] == row][0]
            except: # does not exist, but may
                results.append([image_type, image_mode, segment, row ])

        return results

    def add_image(self, image_type, image_mode, device_name, image_data):
        if self.path_exists is False:
            return
        if image_mode == "normal":
            img_path = os.path.join(self.images_path, image_type, "%s-%s.jpg" % (device_name.lower(), image_type[0]))
        else:
            img_path = os.path.join(self.preview_images_path, image_type, "%s-%s.jpg" % (device_name.lower(), image_type[0]))

        with FileObjectThread(img_path, "wb") as f:
            f.write(image_data)
            if image_mode == "normal":
                self.nr_of_files += 1
                self.notify_observers()

    def create_model(self, filetype="obj", reconstruction_quality="high", quality="high", create_mesh_from="projection", create_textures=False, lit=True):
        self.create_folders()
        model = self.get_model(filetype=filetype, reconstruction_quality=reconstruction_quality, quality=quality, create_mesh_from=create_mesh_from, create_textures=create_textures, lit=lit)
        if model is not None:
            if model.status == "failed":
                model.delete()
                model = None
        if model is None:
            self.models.append(ModelFile(self, filetype=filetype, reconstruction_quality=reconstruction_quality, quality=quality, create_mesh_from=create_mesh_from, create_textures=create_textures, lit=lit))
            self.save()
        self.notify_observers()

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
        self.save()
        self.notify_observers()

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
