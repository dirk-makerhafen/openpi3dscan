from views.shot.shotView import ShotView


class ShotWindowsView(ShotView):

    def __init__(self, subject, parent, settingsInstance, shotsInstance):
        super().__init__(subject, parent, settingsInstance, shotsInstance)
        self.can_sync = False
        self.show_path = True

    def sync_remote(self):
        raise NotImplementedError()

    def available_locations(self):
        return [l.location for l in self.settingsInstance.settingsLocations.locations]

    def set_location(self, location):
        self.subject.set_location(location)
        self.imageCarousel.reset()

    def delete_shot(self):
        self.shotsInstance.delete(self.subject)
        self.subject._deleted = True
        if self.is_visible:
            self.update()