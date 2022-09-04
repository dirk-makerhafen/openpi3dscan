from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.app import App
from pyhtmlgui import PyHtmlView
from .settingsView import SettingsView
from .shotView import ShotView
from .devicesView import DevicesView
from .liveView import LiveView
from .sidebar.sidebarView import SidebarView

class AppView(PyHtmlView):
    DOM_ELEMENT_CLASS = "AppView container"
    TEMPLATE_STR = '''
        <div class="row" >
            {{ pyview.sidebar.render() }}
            {{ pyview.current_view.render()}}
        </div>
    '''

    def __init__(self, subject: App, parent):
        super().__init__(subject, parent)
        self.sidebar = SidebarView(subject=subject, parent=self)
        self.devices = DevicesView(subject=subject.devices, parent=self)
        self.liveView = LiveView(subject=subject, parent=self)
        self.shotView = ShotView(subject=subject, parent=self)
        self.settings = SettingsView(self.subject.settings, self)
        self.current_view = self.devices

    def show_devicesView(self):
        if self.current_view != self.devices:
            self.current_view = self.devices
            self.update()

    def show_settingsView(self):
        if self.current_view != self.settings:
            self.current_view = self.settings
            self.update()

    def show_liveView(self):
        if self.current_view != self.liveView:
            self.current_view = self.liveView
            self.update()

    def show_shotView(self, shot):
        self.shotView.show_shot(shot)
        if self.current_view != self.shotView:
            self.current_view = self.shotView
            self.update()
