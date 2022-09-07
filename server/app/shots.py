import glob
import os
import shutil
import threading
import json
from multiprocessing.pool import ThreadPool
import random
import uuid
import re
import math
import gevent
from PIL import Image
from pyhtmlgui import Observable
from pyhtmlgui import ObservableList
from gevent.fileobject import FileObjectThread

SHOT_DIR = "/shots"

class ModelFile(Observable):
    def __init__(self, parentShot, filetype="obj", reconstruction_quality = "high", quality="high", create_mesh_from="projection", create_textures=False):
        super().__init__()
        self.parentShot = parentShot
        self.model_id = "%s" % uuid.uuid4()
        self.status = "waiting" # ready, failed
        self.filetype = filetype # "obj", obj, 3mf, stl
        self.reconstruction_quality = reconstruction_quality   # normal, high,
        self.quality = quality   # "high", normal, low
        self.create_mesh_from = create_mesh_from # normal, projection, all
        self.filename = ""
        self.filesize = 0
        self.create_textures = create_textures
        self.path = os.path.join(self.parentShot.path, "models")
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def set_status(self, new_status):
        self.status = new_status
        self.parentShot.save()
        self.notify_observers()
        self.parentShot.notify_observers()

    def write_file(self, input_file):
        rcStr = self.reconstruction_quality[0].upper()
        qStr = self.quality[0].upper()
        meshFromStr = self.create_mesh_from[0].upper()
        textureStr = "T" if self.create_textures else ""

        ext = ".zip"
        if self.filetype in ["gif", "webp"]:
            ext = ""
        self.filename = "%s_%s%s%s%s.%s%s" % (self.parentShot.get_clean_shotname(), rcStr, qStr, meshFromStr, textureStr, self.filetype, ext)

        with FileObjectThread(os.path.join(self.path, self.filename), "wb") as f:
            with FileObjectThread(input_file,"rb") as fi:
                buf = fi.read(32000)
                while buf:
                    f.write(buf)
                    buf = fi.read(32000)

        self.filesize = int(round( os.path.getsize(os.path.join(self.path, self.filename)) / 1024 / 1024, 0))
        self.set_status("ready")

    def get_data(self):
        if self.filename != "":
            if os.path.exists(os.path.join(self.path, self.filename)):
                with open(os.path.join(self.path, self.filename), "rb") as f:
                    return f.read()
        return None

    def get_path(self):
        return os.path.join(self.path, self.filename)

    def delete(self):
        if self.filename != "":
            if os.path.exists(os.path.join(self.path, self.filename)):
                os.remove(os.path.join(self.path, self.filename))
        self.parentShot.remove_model(self)

    def to_dict(self):
        return {
            "model_id": self.model_id,
            "status": self.status,
            "filetype": self.filetype,
            "quality": self.quality,
            "create_mesh_from": self.create_mesh_from,
            "filename": self.filename,
            "filesize": self.filesize,
            "create_textures": self.create_textures,
            "reconstruction_quality": self.reconstruction_quality,
        }

    def from_dict(self, data):
        self.status = data["status"]
        self.filetype = data["filetype"]
        self.quality = data["quality"]
        self.filename = data["filename"]
        if self.quality == "ultra": self.quality = "high"
        if self.quality == "default": self.quality = "normal"
        try:
            self.model_id = data["model_id"]
        except:
            pass
        try:
            self.filesize = data["filesize"]
        except:
            pass
        try:
            self.create_textures = data["create_textures"]
        except:
            pass
        try:
            self.create_mesh_from = data["create_mesh_from"]
        except:
            pass
        try:
            self.reconstruction_quality = data["reconstruction_quality"]
        except:
            pass
        return self



class Shot(Observable):
    def __init__(self, shot_id):
        super().__init__()
        self.shot_id = shot_id
        self.name = self.shot_id
        self.status = ""
        self.comment = ""
        self.nr_of_files = 0
        self.devices = set()
        self.path = os.path.join(SHOT_DIR, self.shot_id)
        self.preview_image = "SEG1-CAM4"
        self.worker = None
        self.models = ObservableList()

        if os.path.exists(self.path):
            self.load()
        else:
            os.mkdir(os.path.join(self.path))
            os.mkdir(os.path.join(self.path, "images"))
            os.mkdir(os.path.join(self.path, "images", "normal"))
            os.mkdir(os.path.join(self.path, "images", "projection"))
            os.mkdir(os.path.join(self.path, "preview_images"))
            os.mkdir(os.path.join(self.path, "preview_images", "normal"))
            os.mkdir(os.path.join(self.path, "preview_images", "projection"))
            self.save()
        if self.nr_of_files == 0:
            self.count_number_of_files()

    @property
    def nr_of_devices(self):
        return len(self.devices)

    @property
    def nr_of_models(self):
        return len(self.models)

    @property
    def nr_of_models_waiting(self):
        return len( [m for m in self.models if m.status == "waiting"])

    @property
    def nr_of_models_failed(self):
        return len( [m for m in self.models if m.status == "failed"])

    def set_name(self, name):
        self.name = name
        self.save()
        self.notify_observers()

    def set_comment(self, comment):
        self.comment = comment
        self.save()

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
            self.worker = threading.Thread(target=self._sync_remote, daemon = True)
            self.worker.start()

    # image_mode = normal | preview, image_type = normal | projection
    def _sync_remote(self):
        self.status = "Sync"
        self.notify_observers()
        tasks = []
        existing_images = glob.glob(os.path.join(self.path, "*mages", "*", "*.jpg"))
        for device in [d for d in self.devices if d.status == "online"]:
            for image_mode in [ "normal", "preview" ]:
                for image_type in [ "normal", "projection" ]:
                    if image_mode == "normal":
                        folder_name = "images"
                    else:
                        folder_name = "preview_images"
                    img_path = os.path.join(self.path, folder_name, image_type, "%s.jpg" % device.device_id)
                    if img_path not in existing_images:
                        tasks.append([device, [self.shot_id, image_type, image_mode]])
        if len(tasks) > 0:
            random.shuffle(tasks)
            with ThreadPool(min([4,len(tasks)])) as p:
                p.map(lambda task: task[0].camera.shots.download(*task[1]), tasks)
            p.join()
            self.count_number_of_files()
            self.save()

        existing_images = glob.glob(os.path.join(self.path, "*mages", "*", "*.jpg"))
        for i in range(101,213):
            for image_type in ["normal", "projection"]:
                img_path = os.path.join(self.path, "images", image_type, "%s.jpg" % i)
                preview_path = os.path.join(self.path, "preview_images", image_type, "%s.jpg" % i)
                if not preview_path in existing_images and img_path in existing_images:
                    try:
                        print("creating preview image")
                        img = Image.open(img_path)
                        img = img.resize([800, 600])
                        img.save(preview_path, format="jpeg", quality=85)
                    except Exception as e:
                        print(e)
        self.status = ""
        self.worker = None
        self.notify_observers()

    # image_mode = normal | preview , image_type = normal | projection
    def get_image(self, image_type, image_mode, device_id):
        if image_mode == "normal":
            folder_name = "images"
        else:
            folder_name = "preview_images"
        img_path = os.path.join(self.path, folder_name, image_type, "%s.jpg" % device_id )
        if os.path.exists(img_path):
            with open(img_path,"rb") as f:
                return f.read()
        try:
            device = [d for d in self.devices if d.device_id == device_id and d.status == "online"][0]
        except:
            return None
        img = [b'']
        def f():
            img[0] = device.camera.shots.download(self.shot_id, image_type, image_mode = image_mode)
        t = threading.Thread(target=f, daemon=True)
        t.start()
        while t.is_alive():
            gevent.sleep(0.3)
        if img[0] is None or len(img[0]) < 1000:
            return None
        return img[0]

    def image_may_exist(self, image_type, image_mode, device_id):
        if image_mode == "normal":
            folder_name = "images"
        else:
            folder_name = "preview_images"
        img_path = os.path.join(self.path, folder_name, image_type, "%s.jpg" % device_id )
        if os.path.exists(img_path):
            return True
        try:
            device = [d for d in self.devices if d.device_id == device_id and d.status == "online"][0]
            return True
        except:
            return False

    def add_image(self, image_type, image_mode, device_id, image_data):
        if image_mode == "normal":
            folder_name = "images"
        else:
            folder_name = "preview_images"
        img_path = os.path.join(self.path, folder_name, image_type, "%s.jpg" % device_id )
        with FileObjectThread(img_path, "wb") as f:
            f.write(image_data)
            if image_mode == "normal":
                self.nr_of_files += 1
                self.save()
            self.notify_observers()

    def create_model(self, filetype="obj", reconstruction_quality="high", quality="high", create_mesh_from = "projection", create_textures = False):
        model = self.get_model(filetype=filetype, reconstruction_quality=reconstruction_quality, quality=quality, create_mesh_from=create_mesh_from, create_textures=create_textures)
        if model is not None:
            if model.status == "failed":
                model.delete()
                model = None
        if model is None:
            self.models.append(ModelFile(self, filetype=filetype, reconstruction_quality=reconstruction_quality, quality=quality, create_mesh_from=create_mesh_from, create_textures=create_textures))
            self.save()
        self.notify_observers()

    def get_model(self, filetype="obj",reconstruction_quality="high", quality="high", create_mesh_from = "projection", create_textures= False):
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
        with open(os.path.join(self.path, "metadata.json"), "w") as f:
            f.write(json.dumps({
                "name": self.name,
                "comment": self.comment,
                "preview_image": self.preview_image,
                "models" : [ m.to_dict() for m in self.models]
            }))

    def load(self):
        try:
            with open(os.path.join(self.path, "metadata.json"), "r") as f:
                data = json.loads(f.read())
                self.name = data["name"]
                self.comment = data["comment"]
                self.preview_image = data["preview_image"]
                try:
                    self.models = ObservableList([ ModelFile(self).from_dict(m) for m in data["models"] ])
                except:
                    pass
        except:
            pass
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


# All remote Shots
class Shots:
    def __init__(self, devices ):
        self.shots = ObservableList()
        self.path = "/shots/"
        self.cache = {}
        self.devices = devices
        self.deleted_shot_ids = []
        self.load()

    def create(self, shot_id, name):
        s = Shot(shot_id)
        s.set_name(name)
        self.shots.insert(0,s)
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
            s = Shot(shot_id)
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

    def get_unprocessed_models(self):
        models = []
        [models.extend(shot.get_models_by_status("waiting")) for shot in self.shots]

        return models

    def _add_deleted_shot_id(self, shot_id):
        if shot_id not in self.deleted_shot_ids:
            self.deleted_shot_ids.append(shot_id)
        self.deleted_shot_ids.sort()
        while len(self.deleted_shot_ids) >= 1000:
            del self.deleted_shot_ids[0]
        self.save()

    def save(self):
        with open(os.path.join("/shots/", "shots.json"), "w") as f:
            f.write(json.dumps({
                "deleted_shot_ids": self.deleted_shot_ids,
            }))

    def load(self):
        try:
            with open(os.path.join("/shots/", "shots.json"), "r") as f:
                data = json.loads(f.read())
                self.deleted_shot_ids = data["deleted_shot_ids"]
        except:
            pass

        for path in glob.glob("/shots/*"):
            if os.path.exists(os.path.join(path, "metadata.json")) or os.path.exists(os.path.join(path, "images")) :
                shot_id = path.split("/")[-1]
                self.shots.append(Shot(shot_id))
        self.shots.sort()



_shotsInstance = None
def ShotsInstance(devices = None):
    global _shotsInstance
    if _shotsInstance is None:
        _shotsInstance = Shots(devices)
    return _shotsInstance
