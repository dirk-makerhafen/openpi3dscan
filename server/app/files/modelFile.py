import os
import uuid
from pyhtmlgui import Observable, ObservableList
import zipfile
from zipfile import ZIP_STORED
import shutil
import zipstream

from app.lib.observableValue import ObservableValue


class PrintQueueItem(Observable):
    def __init__(self, model, color, printer):
        super().__init__()
        self.model = model
        self.color = color
        self.printer = printer
        self.status = "waiting"  # printing, failed, printed
        self.created = ""
        self.printed = ""
        self.failed  = ""

    def to_dict(self):
        return {
            "color": self.color,
            "printer": self.printer,
            "status": self.status,
        }

    def from_dict(self, data):
        self.color = data["color"]
        self.printer = data["printer"]
        self.status = data["status"]
        return self


class ModelFile(Observable):
    def __init__(self, parentShot, filetype="obj", reconstruction_quality="high", quality="high", create_mesh_from="projection", create_textures=False, lit=True):
        super().__init__()
        self.parentShot = parentShot
        self.model_id = "%s" % uuid.uuid4()
        self.is_custom_upload = False
        self.status = "waiting"  # ready, failed
        self.publishing_status = ObservableValue("no_publish") # "can_publish"  # can_publish, state_changing, can_unpublish
        self.filetype = filetype  # "obj", obj, 3mf, stl
        self.reconstruction_quality = reconstruction_quality  # preview, normal, high,
        self.quality = quality   # "high", normal, low
        self.create_mesh_from = create_mesh_from  # normal, projection, all
        self.lit = lit # unlit = No shadows, lit = with shadows
        self.filename = ""
        self.is_folder = None
        self.filesize = 0
        self.create_textures = create_textures
        self.path = os.path.join(self.parentShot.path, "models")
        self.printqueue = ObservableList()
        self.printqueue.attach_observer(self.parentShot.notify_observers)

    def print(self, color = "", printer = ""):
        self.printqueue.append(PrintQueueItem(self, color=color, printer=printer))
        self.parentShot.save()

    def from_custom_upload(self, filename, input_file):
        self.is_custom_upload = True
        self.filetype = filename.split(".")[-1]
        self.filename = filename
        self.path = os.path.join(self.parentShot.path, "uploads")
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        if filename.endswith(".zip"):
            self.filetype = "zip"
            if "_" in filename:
                maybe_ext = filename.split("_")[-1].split(".")[0]
                if maybe_ext in ["mp4", "obj", "glb", "gif", "stl", "fbx"]:
                    self.filetype = maybe_ext
        self.reconstruction_quality = "-"
        self.quality = "-"
        self.create_mesh_from = "-"
        for key in ["HH", "HN", "HL", "NH", "NN", "NL", "PH", "PN", "PL"]:
            if "_%s" % key in filename:
                markers = filename.split("_%s" % key)[1].split("_")[0].split(".")[0]
                markers = "%s%s" % (key, markers)
                if markers[0] == "H":
                    self.reconstruction_quality = "high"
                elif markers[0] == "N":
                    self.reconstruction_quality = "normal"
                elif markers[0] == "P":
                    self.reconstruction_quality = "preview"
                else:
                    self.reconstruction_quality = "-"

                if markers[1] == "H":
                    self.quality = "high"
                elif markers[1] == "N":
                    self.quality = "normal"
                elif markers[1] == "L":
                    self.quality = "low"
                else:
                    self.quality = "-"

                if markers[2] == "P":
                    self.create_mesh_from = "projection"
                elif markers[2] == "N":
                    self.create_mesh_from = "normal"
                elif markers[2] == "A":
                    self.create_mesh_from = "all"
                else:
                    self.create_mesh_from = "-"

                if "T" in markers:
                    self.create_textures = True
                else:
                    self.create_textures = False
                if "L" in markers:
                    self.lit = True
                elif "U" in markers:
                    self.lit = False
                break
        self.write_file(input_file, filename)

    def set_status(self, new_status):
        if self.status == new_status:
            return
        self.status = new_status
        self.parentShot.save()
        self.notify_observers()
        self.parentShot.models.notify_observers()

    def write_file(self, input_file, filename = None):
        if filename == None:
            if self.filetype in ["gif", "webp", "holobox"]:
                self.filename = self._create_filename("%s_%s%s%s%s%s.%s")
            else:
                self.filename = self._create_filename("%s_%s%s%s%s%s_%s.zip")

        if not os.path.exists(self.path):
            os.mkdir(self.path)
        with open(os.path.join(self.path, self.filename), "wb") as f:
            buf = input_file.read(32000)
            while buf:
                f.write(buf)
                buf = input_file.read(32000)

        self.filesize = round(os.path.getsize(os.path.join(self.path, self.filename)) / 1024 / 1024, 3)
        if self.filesize >= 1:
            self.filesize = int(round(self.filesize,0))
        self.is_folder = False
        self.set_status("ready")
        self.publishing_status.set("can_publish")

    def write_folder(self, sourcefolder):
        self.filename = self._create_filename("%s_%s%s%s%s%s_%s")
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        target_dir = os.path.join(self.path, self.filename)
        if os.path.exists(target_dir):
            try:
                shutil.rmtree(target_dir)
            except:
                pass
        shutil.copytree(sourcefolder, target_dir)

        def get_size(start_path):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(start_path):
                total_size += sum([os.path.getsize(fp) for fp in [os.path.join(dirpath, f) for f in filenames] if not os.path.islink(fp)])
            return total_size

        self.filesize = round(get_size(target_dir) / 1024 / 1024, 3)
        if self.filesize >= 1:
            self.filesize = int(round(self.filesize,0))
        self.is_folder = True
        self.set_status("ready")
        self.publishing_status.set("can_publish")

    def _create_filename(self, pattern):
        rcStr = self.reconstruction_quality[0].upper()
        qStr = self.quality[0].upper()
        meshFromStr = self.create_mesh_from[0].upper()
        textureStr = "T" if self.create_textures else ""
        if self.filetype in ["gif", "webp", "glb","holobox"]:
            litUnlitStr = ("L" if self.lit else "U") if self.create_textures else ""
        else:
            litUnlitStr = ""
        ext = self.filetype if self.filetype != "holobox" else "mp4"
        filename = pattern % (self.parentShot.get_clean_shotname(), rcStr, qStr, meshFromStr, textureStr, litUnlitStr, ext)
        return filename

    def get_model_file(self, filename = None):
        if self.filetype in ["gif", "webp", "holobox"]:
            return [self.filename, open(self.get_path(), "rb")]
        if self.filename.endswith(".zip"):
            if filename is None:
                return [self.filename, open(self.get_path(), "rb")]
            else:
                with zipfile.ZipFile(self.get_path(), 'r') as zip_ref:
                    return [filename, zip_ref.read(filename)]
        if os.path.isdir(os.path.join(self.path, self.filename)):
            if filename is not None:
                fullpath = os.path.join(self.path, self.filename, filename)
                if os.path.exists(fullpath):
                    return [self.filename, open(fullpath, "rb")]
            else:
                zs = zipstream.ZipStream(compress_type=ZIP_STORED)
                source_dir = os.path.join(self.path, self.filename)
                for root, dirnames, filenames in os.walk(source_dir):
                    dirname = root[len(source_dir)+1:]
                    for fn in filenames:
                        zs.add(os.path.join(root, fn), os.path.join(dirname, fn))
                return ["%s.zip" % self.filename, zs]
        return [self.filename, open(self.get_path(), "rb")]

    def get_path(self):
        return os.path.join(self.path, self.filename)

    def delete(self):
        if self.filename != "":
            path = os.path.join(self.path, self.filename)
            if os.path.exists(path):
                if os.path.isdir(path):
                    try:
                        shutil.rmtree(path)
                    except:
                        pass
                else:
                    os.remove(path)
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
            "lit": self.lit,
            "is_custom_upload": self.is_custom_upload,
            "printqueue": [p.to_dict() for p in self.printqueue]
        }

    def from_dict(self, data):
        self.status = data["status"]
        self.filetype = data["filetype"]
        self.quality = data["quality"]
        self.filename = data["filename"]
        if self.quality == "ultra":
            self.quality = "high"
        if self.quality == "default":
            self.quality = "normal"
        self.model_id = data["model_id"]
        self.filesize = data["filesize"]
        self.create_textures = data["create_textures"]
        self.create_mesh_from = data["create_mesh_from"]
        self.reconstruction_quality = data["reconstruction_quality"]
        self.lit = data["lit"]
        try:
            self.is_custom_upload = data["is_custom_upload"]
        except:
            self.is_custom_upload = False
        if self.is_custom_upload:
            self.path = os.path.join(self.parentShot.path, "uploads")

        try:
            #self.printqueue.clear()
            self.printqueue.extend([PrintQueueItem(self,"","").from_dict(item) for item in data["printqueue"]])
        except Exception as e:
            print("faild", e)
            #self.printqueue.clear()

        if self.status == "ready":
            self.publishing_status._value = "can_publish"

        return self

