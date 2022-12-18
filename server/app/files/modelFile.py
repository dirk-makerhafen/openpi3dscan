import os
import uuid
from gevent.fileobject import FileObjectThread
from pyhtmlgui import Observable
import zipfile
from zipfile import ZIP_STORED
import shutil
import zipstream

class ModelFile(Observable):
    def __init__(self, parentShot, filetype="obj", reconstruction_quality="high", quality="high", create_mesh_from="projection", create_textures=False, lit=True):
        super().__init__()
        self.parentShot = parentShot
        self.model_id = "%s" % uuid.uuid4()
        self.status = "waiting"  # ready, failed
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


    def set_status(self, new_status):
        self.status = new_status
        self.parentShot.save()
        self.notify_observers()
        self.parentShot.notify_observers()

    def write_file(self, input_file):
        if self.filetype in ["gif", "webp"]:
            self.filename = self._create_filename("%s_%s%s%s%s%s.%s")
        else:
            self.filename = self._create_filename("%s_%s%s%s%s%s_%s.zip")

        if not os.path.exists(self.path):
            os.mkdir(self.path)
        with FileObjectThread(os.path.join(self.path, self.filename), "wb") as f:
            with FileObjectThread(input_file, "rb") as fi:
                buf = fi.read(32000)
                while buf:
                    f.write(buf)
                    buf = fi.read(32000)

        self.filesize = round(os.path.getsize(os.path.join(self.path, self.filename)) / 1024 / 1024, 3)
        if self.filesize >= 1:
            self.filesize = int(round(self.filesize,0))
        self.is_folder = False
        self.set_status("ready")

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

    def _create_filename(self, pattern):
        rcStr = self.reconstruction_quality[0].upper()
        qStr = self.quality[0].upper()
        meshFromStr = self.create_mesh_from[0].upper()
        textureStr = "T" if self.create_textures else ""
        if self.filetype in ["gif", "webp", "glb"]:
            litUnlitStr = ("L" if self.lit else "U") if self.create_textures else ""
        else:
            litUnlitStr = ""
        filename = pattern % (self.parentShot.get_clean_shotname(), rcStr, qStr, meshFromStr, textureStr, litUnlitStr, self.filetype)
        return filename

    def get_model_file(self, filename = None):
        if self.filetype in ["gif", "webp"]:
            return [self.filename, open(self.get_path(), "rb")]
        if self.filename.endswith(".zip"):
            if filename is None:
                return [self.filename, open(self.get_path(), "rb")]
            else:
                with zipfile.ZipFile(self.get_path(), 'r') as zip_ref:
                    return [filename, zip_ref.read(filename)]
        if os.path.isdir(os.path.join(self.path, self.filename)):
            print("is dir", filename)
            if filename is not None:
                fullpath = os.path.join(self.path, self.filename, filename)
                print("fp", fullpath, os.path.exists(fullpath))
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
        try:
            self.lit = data["lit"]
        except:
            pass

        return self

