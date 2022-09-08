from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.app import App
    from views.appView import AppView
from pyhtmlgui import PyHtmlView
from views.sidebar.shotsView import ShotsView


class SidebarView(PyHtmlView):
    DOM_ELEMENT_CLASS = "Sidebar col-md-3"
    TEMPLATE_STR = '''
    <div class="row menu">
        <div class="col-md-12 item {% if pyview.parent.currentView.current_view == pyview.parent.settingsView %} selected {% endif %}" onclick='pyview.show_settings();'>
            Settings
        </div>
        <div class="col-md-12 item {% if pyview.parent.currentView.current_view == pyview.parent.devicesView %} selected {% endif %}" onclick='pyview.show_devices();'>
            Devices
        </div>
        <div class="col-md-12 item {% if pyview.parent.currentView.current_view == pyview.parent.liveView %} selected {% endif %}" onclick='pyview.show_liveview();'>
           Live
        </div>
        <div class="col-md-12 item" style="height:3px"'>
        </div>
    </div>
   
    {{pyview.shotsView.render()}}
    <div class="row" style="overflow-y:scroll;position: absolute;bottom: 0px; width: 100%;">
        <div class="col-md-12" style="padding-right: 0px;">
            <input id="_search_input" value="{{pyview.current_search}}" onKeyUp='pyview.search($("#_search_input").val())' onchange='pyview.search($("#_search_input").val())' style="width:100%;font-size: 1.3em;" placeholder="SEARCH" type="text"/>
        </div>
    </div>
    '''

    def __init__(self, subject: App, parent: AppView):
        super().__init__(subject, parent)
        self.shotsView = ShotsView(subject=subject.shots_remote.shots, parent=self)
        self.current_search = ""

    def show_devices(self):
        self.shotsView.select_shot(None)
        self.parent.show_devicesView()

    def show_settings(self):
        self.shotsView.select_shot(None)
        self.parent.show_settingsView()

    def show_liveview(self):
        self.shotsView.select_shot(None)
        self.parent.show_liveView()

    def show_shot(self, shot):
        self.parent.show_shotView(shot)

    def search(self, value):
        self.current_search = value
        self.shotsView.search(value)
