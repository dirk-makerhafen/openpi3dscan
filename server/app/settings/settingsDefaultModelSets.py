import os
import re
import time
from pyhtmlgui import Observable, ObservableList


class SettingsDefaultModel(Observable):
    def __init__(self, parent, setname="", filetype="obj", reconstruction_quality="high", export_quality="high", create_mesh_from="projection", create_textures=False, lit=True):
        super().__init__()
        self.parent = parent
        self.save = parent.save
        self.setname = setname
        self.filetype = filetype  # "obj", obj, 3mf, stl
        self.reconstruction_quality = reconstruction_quality  # preview, normal, high,
        self.export_quality = export_quality  # "high", normal, low
        self.create_mesh_from = create_mesh_from  # normal, projection, all
        self.create_textures = create_textures  #
        self.lit = lit  # unlit = No shadows, lit = with shadows

    def delete(self):
        self.parent.removeDefaultModel(self)

    def to_dict(self):
        return {
            "setname": self.setname,
            "filetype": self.filetype,
            "reconstruction_quality": self.reconstruction_quality,
            "export_quality": self.export_quality,
            "create_mesh_from": self.create_mesh_from,
            "create_textures": self.create_textures,
            "lit": self.lit,
        }

    def from_dict(self, data):
        self.setname = data["setname"]
        self.filetype = data["filetype"]
        self.reconstruction_quality = data["reconstruction_quality"]
        self.export_quality = data["export_quality"]
        self.create_mesh_from = data["create_mesh_from"]
        self.create_textures = data["create_textures"]
        self.lit = data["lit"]
        return self



class SettingsDefaultModelSets(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.save = parent.save
        self.default_models = ObservableList()

    def get_set_names(self):
        return list(set([l.setname for l in self.default_models]))

    def get_models_by_setname(self, setname):
        return [m for m in self.default_models if m.setname == setname]

    def to_dict(self):
        return {
            "default_models": [x.to_dict() for x in self.default_models],
        }

    def from_dict(self, data):
        try:
            self.default_models.clear()
            self.default_models.extend([SettingsDefaultModel(self).from_dict(m) for m in data["default_models"]])
        except:
            pass
        self.default_models.sort(key=lambda x:[x.setname, x.create_mesh_from, x.reconstruction_quality, x.export_quality, x.create_textures, x.lit ])
        return self

    def addDefaultModel(self, setname, filetype, reconstruction_quality, export_quality, create_mesh_from, create_textures, lit):
        if self._defaultModelExists(setname, filetype, reconstruction_quality, export_quality, create_mesh_from, create_textures, lit):
            return
        self.default_models.append(SettingsDefaultModel(self, setname, filetype, reconstruction_quality, export_quality, create_mesh_from, create_textures, lit))
        self.default_models.sort(key=lambda x:[x.setname, x.create_mesh_from, x.reconstruction_quality, x.export_quality, x.create_textures, x.lit ])
        self.save()
        self.notify_observers()

    def _defaultModelExists(self, setname, filetype, reconstruction_quality, export_quality, create_mesh_from, create_textures, lit):
        return len([m for m in self.default_models if
                m.setname == setname and
                m.filetype == filetype  and
                m.reconstruction_quality == reconstruction_quality and
                m.export_quality == export_quality and
                m.create_mesh_from == create_mesh_from and
                m.create_textures == create_textures and
                m.lit == lit
        ]) != 0

    def removeDefaultModel(self, model):
        if model in self.default_models:
            self.default_models.remove(model)
            self.save()
