from pyhtmlgui import Observable


class SettingsSequenceImage(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.save = parent.save
        self._projection = False
        self._light = 0
        self._offset = 0

    def _get_projection(self):
        return self._projection

    def _set_projection(self, value):
        value = bool(value)
        self._projection = value
        self.save()
        self.notify_observers()
    projection = property(_get_projection, _set_projection)

    def _get_light(self):
        return self._light

    def _set_light(self, value):
        value = float(value)
        self._light = value
        self.save()
        self.notify_observers()
    light = property(_get_light, _set_light)

    def _get_offset(self):
        return self._offset

    def _set_offset(self, value):
        value = float(value)
        self._offset = value
        self.save()
        self.notify_observers()
    offset = property(_get_offset, _set_offset)

    def to_dict(self):
        return {
            "projection" : self._projection,
            "light" : self._light,
            "offset" : self._offset,
        }

    def from_dict(self, data):
        self._projection = data["projection"]
        self._light = data["light"]
        self._offset = data["offset"]
