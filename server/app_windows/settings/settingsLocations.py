from .settingsLocation import SettingsLocation
from pyhtmlgui import Observable, ObservableList


class SettingsLocations(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.save = parent.save
        self.locations = ObservableList()

    def new_location(self):
        l = SettingsLocation(self)
        self.locations.append(l)
        self.save()
        self.notify_observers()
        return l

    def get_by_location(self, location):
        try:
            return [l for l in self.locations if l.location.lower() == location.lower()][0]
        except :
            return None

    def remove(self, location):
        if location in self.locations:
            self.locations.remove(location)
        self.save()
        self.notify_observers()

    def to_dict(self):
        return {
            "locations": [l.to_dict() for l in self.locations],
        }

    def from_dict(self, data):
        self.locations.extend([SettingsLocation(self).from_dict(ldata) for ldata in data["locations"] ])
        self.notify_observers()
