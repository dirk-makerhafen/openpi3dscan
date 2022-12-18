from pyhtmlgui import PyHtmlView
from app_windows.settings.settings import SettingsInstance
from app_windows.files.shots import ShotsInstance
from views_windows.shot.shotView import ShotWindowsView
from views_windows.processing.processingView import ProcessingView
from views_windows.settings.settingsView import SettingsView

class MainView(PyHtmlView):
    TEMPLATE_STR = '''{{ pyview.current_view.render()}}'''
    def __init__(self, subject, parent):
        super().__init__(subject, parent)
        self.shotView = None
        self.settingsView = SettingsView(self.subject, self)
        self.processingView = ProcessingView(self.subject.processing, self)
        self.current_view = self.settingsView

    def show_settingsView(self):
        return self.set_view(self.settingsView)

    def show_shotView(self, shot):
        if self.shotView is None or self.shotView.subject != shot:
            self.shotView = ShotWindowsView(subject=shot, parent=self, settingsInstance=SettingsInstance(), shotsInstance=ShotsInstance())
        return self.set_view(self.shotView)

    def show_processingView(self):
        return self.set_view(self.processingView)

    def set_view(self, new_view):
        if self.current_view != new_view:
            self.current_view = new_view
            self.update()
            return True
        return False
