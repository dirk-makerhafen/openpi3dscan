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

1x12:047 - 1x12:048 - 0.095
1x12:049 - 1x12:04a - 0.095
1x12:04b - 1x12:04d - 0.095
1x12:04e - 1x12:04f - 0.095
1x12:051 - 1x12:052 - 0.095
1x12:053 - 1x12:055 - 0.095
1x12:056 - 1x12:057 - 0.095
1x12:059 - 1x12:05a - 0.095
1x12:05b - 1x12:05c - 0.095
1x12:05d - 1x12:05e - 0.095
1x12:05f - 1x12:063 - 0.095
1x12:065 - 1x12:066 - 0.095
1x12:067 - 1x12:069 - 0.095
1x12:06a - 1x12:06b - 0.095
1x12:06c - 1x12:06d - 0.095
1x12:06e - 1x12:06f - 0.095
1x12:071 - 1x12:072 - 0.095
1x12:073 - 1x12:074 - 0.095
1x12:075 - 1x12:076 - 0.095
1x12:077 - 1x12:079 - 0.095
1x12:07a - 1x12:07b - 0.095
1x12:07d - 1x12:07e - 0.095
1x12:07f - 1x12:092 - 0.095
1x12:093 - 1x12:095 - 0.095
1x12:096 - 1x12:097 - 0.095
1x12:099 - 1x12:09a - 0.095
1x12:09b - 1x12:09c - 0.095
'''


class SettingsRealityCapture(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.save = parent.save
        self.markers = MARKERS_PRELOAD
        self.diameter = 1.9
        self.height = 2.5
        self.pin = ""
        self.default_reconstruction_quality = "normal" # preview, normal, high
        self.default_export_quality = "normal"  # "high", normal, low
        self.default_create_mesh_from = "projection" # normal, projection, all
        self.default_create_textures = True

    def to_dict(self):
        return {
            "markers": self.markers,
            "diameter": self.diameter,
            "height": self.height,
            "pin": self.pin,
            "default_reconstruction_quality": self.default_reconstruction_quality,
            "default_export_quality": self.default_export_quality,
            "default_create_mesh_from": self.default_create_mesh_from,
            "default_create_textures": self.default_create_textures,
        }

    def from_dict(self, data):
        self.markers = data["markers"]
        self.diameter = data["diameter"]
        self.height = data["height"]
        self.pin = data["pin"]
        self.default_reconstruction_quality = data["default_reconstruction_quality"]
        self.default_export_quality = data["default_export_quality"]
        self.default_create_mesh_from = data["default_create_mesh_from"]
        self.default_create_textures = data["default_create_textures"]

    def set_markers(self, markers):
        self.markers = markers
        self.save()
        self.notify_observers()

    def set_pin(self, pin):
        self.pin = pin.strip()
        self.save()
        self.notify_observers()

    def set_height(self, new_height):
        try:
            new_height = float(new_height)
        except:
            return
        if new_height < 1 or  new_height > 5:
            self.notify_observers()
            return
        self.height = new_height
        self.save()
        self.notify_observers()

    def set_diameter(self, new_diameter):
        try:
            new_diameter = float(new_diameter)
        except:
            return
        if new_diameter < 1 or  new_diameter > 5:
            self.notify_observers()
            return
        self.diameter = new_diameter
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

    def set_default_create_textures(self, new_default_create_textures):
        self.default_create_textures =  bool(new_default_create_textures)
        self.save()
        self.notify_observers()


