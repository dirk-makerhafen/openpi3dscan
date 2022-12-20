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

from app.dropbox.sharings import DropboxPrivateImagesShare
from app.files.modelFile import ModelFile
from app.files.old_shotDropboxUpload import ShotDropboxUpload
from app.files.shotPublicFolder import ShotDropboxPublicFolder
from app.settings.settings import SettingsInstance

SyncThreadPool = ThreadPool(8)

class Shot(Observable):
    def __init__(self, shot_dir, shot_id, parent_shots):
        super().__init__()
        self.parent_shots = parent_shots
        self.settingsInstance = SettingsInstance()
        self.shot_id = shot_id
        self.publishing_status = "can_publish"  # can_publish, state_changing, can_unpublish
        self.name = self.shot_id
        self.status = ""
        self.comment = ""
        self.meta_location = ""
        self.meta_max_segments = 16
        self.meta_max_rows = 7
        self.meta_rotation = 0
        self.meta_camera_one_position = "top"
        self.license_data = ""
        self.nr_of_files = 0
        self.devices = set()
        self.path = os.path.join(shot_dir, self.shot_id)
        self.worker = None
        self.models = ObservableList()
        self.path_exists = False
        self.images_path = os.path.join(self.path, "images")
        if os.path.exists(os.path.join(self.path, "normal")) and os.path.exists(os.path.join(self.path, "projection")):
            self.images_path = self.path
        self.preview_images_path = os.path.join(self.path, "preview_images")
        self.dropboxUpload = DropboxPrivateImagesShare(self)
        self.dropboxPublicFolder = ShotDropboxPublicFolder(self)
        self.load()

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
        while "  " in name:
            name = name.replace("  ", " ")
        name = name.strip()
        if self.name == name:
            return
        self.name = name
        self.save()
        self.backup_meta()
        self.notify_observers()

    def set_comment(self, comment):
        while "  " in comment:
            comment = comment.replace("  ", " ")
        comment = comment.strip()
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
        if self.can_delete is False:
            return
        if self.devices is not None:
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
        self.status = "sync"
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
                preview_path = os.path.join(self.preview_images_path, image_type, os.path.split(existing_image)[1])
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
        if self.devices is None:
            return None
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
            segment = os.path.split(file)[1].split("-")[0].replace("seg","")
            row = os.path.split(file)[1].split("-")[1].replace("cam","")
            results.append([image_type, image_mode, segment, row, ])

        if self.devices is not None:
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
            model = ModelFile(self, filetype=filetype, reconstruction_quality=reconstruction_quality, quality=quality, create_mesh_from=create_mesh_from, create_textures=create_textures, lit=lit)
            self.parent_shots.unprocessed_models.append(model)
            self.models.append(model)
            self.save()
        self.notify_observers()

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
        self.notify_observers()

    def count_number_of_files(self):
        self.nr_of_files = len(glob.glob(os.path.join(self.images_path, "normal", "*.jpg"))) + len(glob.glob(os.path.join(self.images_path, "projection", "*.jpg")))

    def save(self):
        if os.path.exists(self.path):
            try:
                data = json.dumps({
                        "name": self.name,
                        "comment": self.comment,
                        "meta_location": self.meta_location,
                        "meta_max_rows": self.meta_max_rows,
                        "meta_max_segments": self.meta_max_segments,
                        "meta_rotation": self.meta_rotation,
                        "meta_camera_one_position": self.meta_camera_one_position,
                        "license_data": self.license_data,
                        "models" : [m.to_dict() for m in self.models],
                        "dropbox" : self.dropboxUpload.to_dict(),
                        "dropboxPublicFolder" : self.dropboxPublicFolder.to_dict(),
                    })
                with open(os.path.join(self.path, "metadata.json"), "w") as f:
                    f.write(data)
            except:
                print("failed to save metadata")

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
                "license_data": self.license_data,
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
                        self.models.clear()
                        self.models.extend([ModelFile(self).from_dict(m) for m in data["models"]])
                    except:
                        pass
                    try:
                        self.dropboxUpload.from_dict(data["dropbox"])
                    except:
                        pass
                    try:
                        self.dropboxPublicFolder.from_dict(data["dropboxPublicFolder"])
                    except:
                        pass
                if self.meta_location == "":
                    self.meta_location = SettingsInstance().settingsScanner.location
                    self.meta_max_segments = SettingsInstance().settingsScanner.segments
                    self.meta_max_rows = SettingsInstance().settingsScanner.cameras_per_segment
                    self.meta_rotation = SettingsInstance().settingsScanner.camera_rotation
                    self.meta_camera_one_position = SettingsInstance().settingsScanner.camera_one_position
                    self.save()
            except Exception as e:
                print("failed to load %s" % os.path.join(self.path, "metadata.json"), e)

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
                        self.license_data = data["license_data"]
                    except:
                        pass
            except Exception as e:
                print("failed to load1", e)
        self.path_exists = os.path.exists(self.path)
        if self.path_exists is True and self.nr_of_files == 0:
            self.count_number_of_files()

        self.notify_observers()

    def get_clean_shotname(self):
        name = self.name
        for rp in [["ä", "ae"], ["ö", "oe"], ["ü", "ue"], ["Ä", "Ae"], ["Ö", "Oe"], ["Ü", "Ue"]]:
            name = name.replace(rp[0], rp[1])
        name = re.sub('\s+', ' ', name)
        name = re.sub('[^A-Za-z0-9_. ]+', '', name)
        for rp in [["..", "."], ["__", "_"], ["  ", " "]]:
            while rp[0] in name:
                name = name.replace(rp[0], rp[1]).strip()
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
