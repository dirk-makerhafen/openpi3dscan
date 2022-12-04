from __future__ import annotations
from typing import TYPE_CHECKING

from app_windows.settings.settings import SettingsInstance
from views.shotView import ShotView
if TYPE_CHECKING:
    from app_windows.app import App

class ShotWindowsView(ShotView):

    def __init__(self, subject: App, parent, settingsInstance, shotsInstance):
        super().__init__(subject, parent, settingsInstance, shotsInstance)
        self.can_sync = False
        self.show_path = True

    def sync_remote(self):
        raise NotImplementedError()

    def available_locations(self):
        return [l.location for l in SettingsInstance().settingsLocations.locations]

    def set_location(self, location):
        self.current_shot.set_location(location)
        self.imageCarousel.reset()

    def delete_shot(self):
        self.shotsInstance.delete(self.current_shot)
        self.current_shot._deleted = True
        if self.is_visible:
            self.update()