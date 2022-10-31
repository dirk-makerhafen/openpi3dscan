import os
import uuid
from gevent.fileobject import FileObjectThread
from pyhtmlgui import Observable


class ModelFile(Observable):
    def __init__(self, parentShot, filetype="obj", reconstruction_quality="high", quality="high", create_mesh_from="projection", create_textures=False):
        super().__init__()
        self.parentShot = parentShot
        self.model_id = "%s" % uuid.uuid4()
        self.status = "waiting"  # ready, failed
        self.filetype = filetype  # "obj", obj, 3mf, stl
        self.reconstruction_quality = reconstruction_quality  # preview, normal, high,
        self.quality = quality   # "high", normal, low
        self.create_mesh_from = create_mesh_from  # normal, projection, all
        self.lit = True # unlit = No shadows, lit = with shadows
        self.filename = ""
        self.filesize = 0
        self.create_textures = create_textures
        self.path = os.path.join(self.parentShot.path, "models")

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
        if self.filetype in ["gif", "webp", "glb"]:
            litUnlitStr = ("L" if self.lit else "U") if self.create_textures else ""
        else:
            litUnlitStr = ""
        ext = ".zip"
        if self.filetype in ["gif", "webp"]:
            ext = ""
        self.filename = "%s_%s%s%s%s%s.%s%s" % (self.parentShot.get_clean_shotname(), rcStr, qStr, meshFromStr, textureStr, litUnlitStr, self.filetype, ext)
        #self.filename = "%s_%s%s%s%s.%s%s" % (self.parentShot.get_clean_shotname(), rcStr, qStr, meshFromStr, textureStr, self.filetype, ext)
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        with FileObjectThread(os.path.join(self.path, self.filename), "wb") as f:
            with FileObjectThread(input_file, "rb") as fi:
                buf = fi.read(32000)
                while buf:
                    f.write(buf)
                    buf = fi.read(32000)

        self.filesize = int(round(os.path.getsize(os.path.join(self.path, self.filename)) / 1024 / 1024, 0))
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

