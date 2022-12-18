from pyhtmlgui import PyHtmlView
from app.files.shots import ShotsInstance
from app.settings.settings import SettingsInstance
from views.devices.devicesView import DevicesView
from views.live.liveView import LiveView
from views.settings.settingsView import SettingsView
from views.shot.shotView import ShotView

class MainView(PyHtmlView):
    TEMPLATE_STR = '''{{ pyview.current_view.render()}}'''
    def __init__(self, subject, parent):
        super().__init__(subject, parent)
        self.devicesView = DevicesView(subject=subject.devices, parent=self)
        self.liveView = LiveView(subject=subject, parent=self)
        self.shotView = None
        self.settingsView = SettingsView(self.subject, self)
        self.current_view = self.devicesView

    def show_devicesView(self):
        return self.set_view(self.devicesView)

    def show_settingsView(self):
        return self.set_view(self.settingsView)

    def show_liveView(self):
        return self.set_view(self.liveView)

    def show_shotView(self, shot):
        if self.shotView is None or self.shotView.subject != shot:
            if self.shotView is not None:
                self.shotView.delete(remove_from_dom=False)
            self.shotView = ShotView(subject=shot, parent=self, settingsInstance=SettingsInstance(), shotsInstance=ShotsInstance())
        return self.set_view(self.shotView)

    def set_view(self, new_view):
        if self.current_view != new_view:
            self.current_view = new_view
            self.update()
            return True
        return False
