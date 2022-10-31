from __future__ import annotations

from typing import TYPE_CHECKING

from .processingView import ProcessingView

if TYPE_CHECKING:
    from app.app import App
from pyhtmlgui import PyHtmlView
from .settingsView import SettingsView
from .shotView import ShotView
from .sidebar.sidebarView import SidebarView

class CurrentView(PyHtmlView):
    TEMPLATE_STR = '''{{ pyview.current_view.render()}}'''
    def __init__(self, subject, parent):
        super().__init__(subject, parent)
        self.shotView = ShotView(subject=subject, parent=self)
        self.settingsView = SettingsView(self.subject, self)
        self.processingView = ProcessingView(self.subject, self)
        self.current_view = self.settingsView

    def show_settingsView(self):
        return self.set_view(self.settingsView)

    def show_processing(self):
        return self.set_view(self.processingView)

    def show_shotView(self, shot):
        self.shotView.show_shot(shot)
        return self.set_view(self.shotView)

    def set_view(self, new_view):
        if self.current_view != new_view:
            self.current_view = new_view
            self.update()
            return True
        return False

class AppView(PyHtmlView):
    DOM_ELEMENT_CLASS = "AppView container"
    TEMPLATE_STR = '''
    {% if pyview.subject.status == "active"%}
        <div class="row" >
            {{ pyview.sidebarView.render() }}
            {{ pyview.currentView.render()}}
        </div>
    {% else %}
        <div style="width:100%;text-align:center;font-size:3em;padding-top: 20%;color:#aaa">
            {% if  pyview.subject.status == "reboot"%}
                Reboot in progress, this may take 2-3 minutes
                <script> setTimeout(function(){ location.reload();}, 130000); </script>
            {% endif %}
            {% if  pyview.subject.status == "shutdown"%}
                System Shutdown
            {% endif %}
        </div>
    {% endif %}
    '''

    def __init__(self, subject: App, parent):
        super().__init__(subject, parent)
        self.currentView = CurrentView(subject, self)
        self.sidebarView = SidebarView(subject=subject, parent=self)


