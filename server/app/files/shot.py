import glob
import json
import os
import random
import re
import shutil
import threading
from multiprocessing.pool import ThreadPool
from PIL import Image
from pyhtmlgui import Observable
from pyhtmlgui import ObservableList

from app.dropbox.sharings import DropboxPrivateImagesShare
from app.files.modelFile import ModelFile
from app.files.shotPublicFolder import ShotDropboxPublicFolder
from app.lib.observableValue import ObservableValue

SyncThreadPool = ThreadPool(8)


class Models(ObservableList):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def waiting(self):
        return [m for m in self if m.status == "waiting"]

    @property
    def waiting_or_processing(self):
        return [m for m in self if m.status == "waiting" or m.status == "processing"]

    @property
    def failed(self):
        return [m for m in self if m.status == "failed"]

    def get_by_id(self, model_id):
        try:
            return [m for m in self if m.model_id == model_id][0]
        except:
            return None

    def get(self, filetype="obj", reconstruction_quality="high", quality="high", create_mesh_from="projection",create_textures=False, lit=True):
        try:
            return [m for m in self if m.filetype == filetype and m.quality == quality and m.reconstruction_quality == reconstruction_quality and m.create_mesh_from == create_mesh_from and m.create_textures == create_textures and m.lit == lit][
                0]
        except:
            return None

class LocationData(Observable):
    def __init__(self):
        super().__init__()
        self.name = ""
        self.max_segments = ""
        self.max_rows = ""
        self.rotation = ""
        self.camera_one_position = ""

class Shot(Observable):
    def __init__(self, shot_dir, shot_id, parent_shots):
        super().__init__()
        self.settingsInstance = parent_shots.settingsInstance
        self.path = shot_dir
        self.shot_id = shot_id
        self.parent_shots = parent_shots

        self.name = self.shot_id
        self.status = ""
        self.publishing_status = ObservableValue("can_publish") # can_publish, state_changing, can_unpublish
        self.comment = ObservableValue("")
        self.meta_location = ""
        self.meta_max_segments = 16
        self.meta_max_rows = 7
        self.meta_rotation = 0
        self.meta_camera_one_position = "top"
        self.license_data = ""
        self.nr_of_files = ObservableValue(0)
        self.worker = None
        self.devices = ObservableList()
        self.models = Models()
        self.path_exists = os.path.exists(self.path)
        self.images_path = os.path.join(self.path, "images")
        if os.path.exists(os.path.join(self.path, "normal")) and os.path.exists(os.path.join(self.path, "projection")):
            self.images_path = self.path
        self.preview_images_path = os.path.join(self.path, "preview_images")
        self.dropboxUpload = DropboxPrivateImagesShare(self)
        self.dropboxPublicFolder = ShotDropboxPublicFolder(self)
        self.load()

    @property
    def printqueue(self):
        pq = []
        for m in self.models:
            pq.extend([p for p in m.printqueue])
        pq.sort(key=lambda x:x.created)
        return pq

    @property
    def can_delete(self):
        if self.status == "sync":
            return False
        if self.dropboxPublicFolder.can_delete is False:
            return False
        return True

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
        self.notify_observers()

    def set_comment(self, comment):
        while "  " in comment:
            comment = comment.replace("  ", " ")
        comment = comment.strip()
        if self.comment.value == comment:
            return
        self.comment.set(comment)
        self.save()

    def add_device(self, device):
        if device not in self.devices:
            self.devices.append(device)

    def remove_device(self, device):
        if device in self.devices:
            self.devices.remove(device)

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
            segment = device.name.split("-")[0].replace("SEG", "")
            row = device.name.split("-")[1].replace("CAM", "")
            for image_mode in ["normal", "preview"]:
                for image_type in ["normal", "projection"]:
                    if image_mode == "normal":
                        img_path = os.path.join(self.images_path, image_type,
                                                "seg%s-cam%s-%s.jpg" % (segment, row, image_type[0]))
                    else:
                        img_path = os.path.join(self.preview_images_path, image_type,
                                                "seg%s-cam%s-%s.jpg" % (segment, row, image_type[0]))

                    if img_path not in existing_images:
                        tasks.append([device, [self.shot_id, image_type, image_mode, False]])
        if len(tasks) > 0:
            random.shuffle(tasks)
            SyncThreadPool.map(lambda task: task[0].camera.shots.download(*task[1]), tasks)
            self.count_number_of_files()

        resolution = [800, 600] if self.settingsInstance.settingsScanner.camera_rotation in [0, 180] else [600, 800]
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
            img_path = os.path.join(self.preview_images_path, image_type,"seg%s-cam%s-%s.jpg" % (segment, row, image_type[0]))

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
            segment = os.path.split(file)[1].split("-")[0].replace("seg", "")
            row = os.path.split(file)[1].split("-")[1].replace("cam", "")
            results.append([image_type, image_mode, segment, row, ])

        if self.devices is not None:
            for device in self.devices:
                if device.status != "online":
                    continue
                segment = device.name.split("-")[0].replace("SEG", "")
                row = device.name.split("-")[1].replace("CAM", "")
                try:
                    [x for x in results if x[2] == segment and x[3] == row][0]
                except:  # does not exist, but may
                    results.append([image_type, image_mode, segment, row])

        return results

    def add_image(self, image_type, image_mode, device_name, image_data):
        if self.path_exists is False:
            return
        if image_mode == "normal":
            img_path = os.path.join(self.images_path, image_type, "%s-%s.jpg" % (device_name.lower(), image_type[0]))
        else:
            img_path = os.path.join(self.preview_images_path, image_type, "%s-%s.jpg" % (device_name.lower(), image_type[0]))

        with open(img_path, "wb") as f:
            f.write(image_data)
            if image_mode == "normal":
                self.nr_of_files.value += 1

    def create_model(self, filetype="obj", reconstruction_quality="high", quality="high", create_mesh_from="projection", create_textures=False, lit=True):
        if self.status != "":
            return
        self.create_folders()
        model = self.models.get(filetype=filetype, reconstruction_quality=reconstruction_quality, quality=quality, create_mesh_from=create_mesh_from, create_textures=create_textures, lit=lit)
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
        model_templates = self.settingsInstance.realityCaptureSettings.settingsDefaultModelSets.get_models_by_setname(set_name)
        for model_template in model_templates:
            self.create_model(
                filetype=model_template.filetype,
                reconstruction_quality=model_template.reconstruction_quality,
                quality=model_template.export_quality,
                create_mesh_from=model_template.create_mesh_from,
                create_textures=model_template.create_textures,
                lit=model_template.lit
            )

    def remove_model(self, model):
        self.models.remove(model)
        if model in self.parent_shots.unprocessed_models:
            self.parent_shots.unprocessed_models.remove(model)
        self.save()

    def count_number_of_files(self):
        self.nr_of_files.value = len(glob.glob(os.path.join(self.images_path, "normal", "*.jpg"))) + len( glob.glob(os.path.join(self.images_path, "projection", "*.jpg")))

    def save(self):
        try:
            data = json.dumps({
                "name": self.name,
                "comment": self.comment.value,
                "meta_location": self.meta_location,
                "meta_max_rows": self.meta_max_rows,
                "meta_max_segments": self.meta_max_segments,
                "meta_rotation": self.meta_rotation,
                "meta_camera_one_position": self.meta_camera_one_position,
                "license_data": self.license_data,
                "models": [m.to_dict() for m in self.models],
                "dropboxPublicFolder": self.dropboxPublicFolder.to_dict(),
                "dropbox": self.dropboxUpload.to_dict(),
            })
        except:
            print("failed to save")
            return

        if os.path.exists(self.path):
            with open(os.path.join(self.path, "metadata.json"), "w") as f:
                f.write(data)

        if os.path.exists("/opt/openpi3dscan/meta/"):
            with open('/opt/openpi3dscan/meta/%s.json' % self.shot_id, "w") as f:
                f.write(data)


    def load(self):
        print("loading %s" % self.path)

        if os.path.exists(os.path.join(self.path, "metadata.json")):
            path = os.path.join(self.path, "metadata.json")
        elif os.path.exists('/opt/openpi3dscan/meta/%s.json' % self.shot_id):
            path = '/opt/openpi3dscan/meta/%s.json' % self.shot_id
        else:
            path = None

        if path is not None:
            try:
                with open(path, "r") as f:
                    data = json.loads(f.read())
                    self.name = data["name"]
                    self.comment._value = data["comment"]
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
                    self.meta_location = self.settingsInstance.settingsScanner.location
                    self.meta_max_segments = self.settingsInstance.settingsScanner.segments
                    self.meta_max_rows = self.settingsInstance.settingsScanner.cameras_per_segment
                    self.meta_rotation = self.settingsInstance.settingsScanner.camera_rotation
                    self.meta_camera_one_position = self.settingsInstance.settingsScanner.camera_one_position
                    self.save()
            except Exception as e:
                print("failed to load %s" % os.path.join(self.path, "metadata.json"), e)

        self.path_exists = os.path.exists(self.path)
        if self.path_exists is True and self.nr_of_files.value == 0:
            self.count_number_of_files()

        if os.path.exists(os.path.join(self.path, "models")):
            modelfiles = [f for f in glob.glob(os.path.join(self.path, "models", "*.*"))]
            stored_model_filenames = [m.filename for m in self.models]
            if len(modelfiles) > 0:
                for modelfile in modelfiles:
                    fname = os.path.split(modelfile)[1]
                    if fname in stored_model_filenames:
                        continue
                    try:
                        if fname.endswith(".zip"):
                            if "." in fname.replace(".zip","").split("_")[-1]:
                                filetype = fname.split(".")[-2]
                                s = fname.split(".")[-3].split("_")[-1]
                            else:
                                filetype = fname.replace(".zip","").split("_")[-1]
                                s = fname.replace(".zip","").split("_")[-2]
                        else:
                            filetype = fname.split(".")[-1]
                            s = fname.split(".")[-2].split("_")[-1]

                        reconstruction_quality = {"H": "high", "N": "normal", "P": "preview"}[s[0]]
                        export_quality = {"H": "high", "N": "normal", "L": "low"}[s[1]]
                        create_mesh_from = {"N": "normal", "P": "projection", "A": "all"}[s[2]]
                        create_textures = False
                        lit = True
                        if len(s) > 3 and s[3] == "T":
                            create_textures = True
                        if s[-1] == "U":
                            lit = False

                        m = ModelFile(self,
                            filetype = filetype,
                            reconstruction_quality = reconstruction_quality,
                            quality = export_quality,
                            create_mesh_from = create_mesh_from,
                            create_textures  = create_textures,
                            lit = lit
                        )
                        m.filename = fname
                        m.filesize = round(os.path.getsize(modelfile) / 1024 / 1024, 3)
                        if m.filesize >= 1:
                            m.filesize = int(round(m.filesize, 0))
                        m.is_folder = False
                        self.models.append(m)
                        m.publishing_status.set("can_publish")
                        m.set_status("ready")
                    except Exception as e:
                        print("Failed to load %s" % e)

        if self.path_exists is True and not os.path.exists(os.path.join(self.path, "metadata.json")):
            self.save()

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
