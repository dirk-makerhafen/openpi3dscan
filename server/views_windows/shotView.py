from __future__ import annotations
from typing import TYPE_CHECKING

from app_windows.settings.settings import SettingsInstance
from views.shotView import ShotView

if TYPE_CHECKING:
    from app_windows.app import App

class ShotView(ShotView):

    def __init__(self, subject: App, parent, settingsInstance):
        super().__init__(subject, parent, settingsInstance)
        self.can_sync = False
        self.show_path = True

    def sync_remote(self):
        raise NotImplementedError()

    def available_locations(self):
        return [l.location for l in SettingsInstance().settingsLocations.locations]

    def set_location(self, location):
        self.current_shot.set_location(location)
        self.imageCarousel.reset()