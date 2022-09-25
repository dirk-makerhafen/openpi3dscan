from app.settings.settingsLocation import SettingsLocation
from pyhtmlgui import Observable


class SettingsLocations(Observable):
    def __init__(self, parent):
        super().__init__()
        self.locations = []

    def to_dict(self):
        return {
            "locations": [l.to_dict() for l in self.locations],
        }

    def from_dict(self, data):
        self.locations = [SettingsLocation(self).from_dict(ldata) for ldata in data["locations"] ]
        self.notify_observers()
