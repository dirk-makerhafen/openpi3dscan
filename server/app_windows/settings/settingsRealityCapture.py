from pyhtmlgui import Observable


MARKERS_PRELOAD = '''
#marker1 - marker2  - distance
1x12:011 - 1x12:012 - 0.500
1x12:011 - 1x12:013 - 0.866
1x12:011 - 1x12:014 - 1.000
1x12:011 - 1x12:015 - 0.866
1x12:011 - 1x12:016 - 0.500
1x12:012 - 1x12:013 - 0.500
1x12:012 - 1x12:014 - 0.866
1x12:012 - 1x12:015 - 1.000
1x12:012 - 1x12:016 - 0.866
1x12:013 - 1x12:014 - 0.500
1x12:013 - 1x12:015 - 0.866
1x12:013 - 1x12:016 - 1.000
1x12:014 - 1x12:015 - 0.500
1x12:014 - 1x12:016 - 0.866
1x12:015 - 1x12:016 - 0.500
'''


class SettingsRealityCapture(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.save = parent.save
        self.pin = ""
        self.default_reconstruction_quality = "normal" # preview, normal, high
        self.default_export_quality = "normal"  # "high", normal, low
        self.default_create_mesh_from = "projection" # normal, projection, all
        self.default_create_textures = True
        self.default_lit = True

    def to_dict(self):
        return {
            "pin": self.pin,
            "default_reconstruction_quality": self.default_reconstruction_quality,
            "default_export_quality": self.default_export_quality,
            "default_create_mesh_from": self.default_create_mesh_from,
            "default_create_textures": self.default_create_textures,
            "default_lit": self.default_create_textures,
        }

    def from_dict(self, data):
        self.pin = data["pin"]
        self.default_reconstruction_quality = data["default_reconstruction_quality"]
        self.default_export_quality = data["default_export_quality"]
        self.default_create_mesh_from = data["default_create_mesh_from"]
        self.default_create_textures = data["default_create_textures"]
        self.default_lit = data["default_lit"]

    def set_pin(self, pin):
        self.pin = pin.strip()
        self.save()
        self.notify_observers()

    def set_default_reconstruction_quality(self, new_default_reconstruction_quality):
        if new_default_reconstruction_quality not in ["preview", "normal", "high"]:
            self.notify_observers()
            return
        self.default_reconstruction_quality = new_default_reconstruction_quality
        self.save()
        self.notify_observers()

    def set_default_export_quality(self, new_default_export_quality):
        if new_default_export_quality not in ["low", "normal", "high"]:
            self.notify_observers()
            return
        self.default_export_quality = new_default_export_quality
        self.save()
        self.notify_observers()

    def set_default_create_mesh_from(self, new_default_create_mesh_from):
        if new_default_create_mesh_from not in ["normal", "projection", "all"]:
            self.notify_observers()
            return
        self.default_create_mesh_from = new_default_create_mesh_from
        self.save()
        self.notify_observers()

    def set_default_lit(self, new_default_lit):
        self.default_lit = bool(new_default_lit)
        self.save()
        self.notify_observers()

    def set_default_create_textures(self, new_default_create_textures):
        self.default_create_textures = bool(new_default_create_textures)
        self.save()
        self.notify_observers()
