import glob
import json
import os
import re
from multiprocessing.pool import ThreadPool
from PIL import Image
from pyhtmlgui import ObservableList
from app.files.modelFile import ModelFile
from app.files.shot import Shot

SyncThreadPool = ThreadPool(8)

class ShotWindows(Shot):
    def __init__(self, shot_dir, shot_id, parent_shots):
        super().__init__(shot_dir, shot_id, parent_shots)
        self.devices = None


    def set_name(self, name):
        if name == self.name:
            return
        super().set_name(name)
        l = self._clean_for_filesystem(self.meta_location)
        n = self._clean_for_filesystem(name)
        if len(l) > 0:
            l = "%s " % l
        if len(n) > 0:
            n = " %s" % n
        folder_name = "%s%s" % (l, n)
        if folder_name == "":
            return
        folder_name = os.path.abspath(os.path.join(self.path, "..", folder_name))
        new_folder_name = folder_name
        i=1
        while os.path.exists(new_folder_name):
            new_folder_name = "%s-%s" % (new_folder_name, i)
            i+=1
        os.rename(self.path, new_folder_name)
        self.path = new_folder_name
        self.path_exists = os.path.exists(self.path)
        self.images_path = os.path.join(self.path, "images")
        if os.path.exists(os.path.join(self.path, "normal")) and os.path.exists(os.path.join(self.path, "projection")):
            self.images_path = self.path
        self.preview_images_path = os.path.join(self.path, "preview_images")
        self.save()
        self.notify_observers()

    def _clean_for_filesystem(self, value):
        name = value
        for rp in [["ä", "ae"], ["ö", "oe"], ["ü", "ue"], ["Ä", "Ae"], ["Ö", "Oe"], ["Ü", "Ue"]]:
            name = name.replace(rp[0], rp[1])
        name = re.sub('\s+', ' ', name)
        name = re.sub('[^A-Za-z0-9_. ]+', '', name)
        for rp in [["..", "."], ["__", "_"], ["  ", " "]]:
            while rp[0] in name:
                name = name.replace(rp[0], rp[1]).strip()
        name = name.strip()

        while len(name) > 0 and name[-1] in ["_", "."]:
            name = name[:-1].strip()
        while len(name) > 0 and name[0] in ["_", "."]:
            name = name[1:].strip()
        return name

    def set_location(self, location):
        if self.meta_location == location:
            return
        l = self.settingsInstance.settingsLocations.get_by_location(location)
        if l is None:
            return
        self.meta_location = l.location
        self.meta_max_segments = l.segments
        self.meta_max_rows = l.cameras_per_segment
        self.meta_rotation = l.camera_rotation
        self.meta_camera_one_position = l.camera_one_position
        self.save()
        self.notify_observers()

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
                    try:
                        img = Image.open(image)
                        width, height = img.size
                        if width > height:
                            resolution = [800, 600]
                        else:
                            resolution = [600, 800]
                        img = img.resize(resolution)
                        img.save(preview_img, format="jpeg", quality=85)
                    except:
                        pass

    def save(self):
        if os.path.exists(self.path):
            with open(os.path.join(self.path, "metadata.json"), "w") as f:
                f.write(json.dumps({
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
                }))

    def load(self):
        if os.path.exists(os.path.join(self.path, "metadata.json")):
            try:
                with open(os.path.join(self.path, "metadata.json"), "r") as f:
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
                        self.dropboxPublicFolder.from_dict(data["dropboxPublicFolder"])
                    except:
                        pass
            except Exception as e:
                print("failed to load %s" % os.path.join(self.path, "metadata.json"), e)

        self.path_exists = os.path.exists(self.path)
        if self.path_exists is True and self.nr_of_files.value == 0:
            self.count_number_of_files()
        self.notify_observers()

    def backup_meta(self):
        pass