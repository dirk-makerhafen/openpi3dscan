from __future__ import annotations
from typing import TYPE_CHECKING

from views.sidebar.sidebarShotsView import SidebarShotsView

if TYPE_CHECKING:
    from app.app import App
    from views.appView import AppView
from pyhtmlgui import PyHtmlView
from app_windows.settings.settings import SettingsInstance



class SidebarTopView(PyHtmlView):
    DOM_ELEMENT_CLASS = "row menu"
    TEMPLATE_STR = '''
        <div class="col-md-12 item {% if pyview._mainView.current_view == pyview._mainView.settingsView %} selected {% endif %}" onclick='pyview.parent.show_settings();'>
            Settings
        </div>
        <div {% if pyview._mainView.processingView.subject.status == "failed" %}style="color:#ff0000bb !important"{% endif %} class="col-md-12 item {% if pyview._mainView.current_view == pyview._mainView.processingView %} selected {% endif %}" onclick='pyview.parent.show_processing();'>
            Processing {% if pyview._mainView.processingView.subject.status == "failed" %}failed{% endif %}
        </div>
        <div class="col-md-12 item" style="height:3px"'> </div> 
    '''
    def __init__(self, subject: App, parent):
        super().__init__(subject, parent)
        self._mainView = self.parent._mainView
        self.add_observable(self._mainView.processingView.subject)

class SidebarView(PyHtmlView):
    DOM_ELEMENT_CLASS = "Sidebar col-md-3"
    TEMPLATE_STR = '''
    {{pyview.buttonsView.render()}}
    {{pyview.shotsView.render()}}
    <div class="row" style="overflow-y:scroll;position: absolute;bottom: 0px; width: 100%;">
        <div class="col-md-12" style="padding-right: 0px;">
            <input id="_search_input" value="{{pyview.current_search}}" onKeyUp='pyview.search($("#_search_input").val())' onchange='pyview.search($("#_search_input").val())' style="width:100%;font-size: 1.3em;" placeholder="SEARCH" type="text"/>
        </div>
    </div>
    '''

    def __init__(self, subject: App, parent: AppView):
        super().__init__(subject, parent)
        self._mainView = self.parent.mainView
        self.shotsView = SidebarShotsView(subject=subject.shots.shots, parent=self, settingsInstance=SettingsInstance())
        self.buttonsView = SidebarTopView(subject=subject, parent=self)
        self.current_search = ""

    def show_settings(self):
        self.shotsView.select_shot(None)
        if self._mainView.show_settingsView() is True:
            self.buttonsView.update()

    def show_processing(self):
        self.shotsView.select_shot(None)
        if self._mainView.show_processingView() is True:
            self.buttonsView.update()

    def show_shot(self, shot):
        if self._mainView.show_shotView(shot) is True:
            self.buttonsView.update()

    def search(self, value):
        self.current_search = value
        self.shotsView.search(value)
