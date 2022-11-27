from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.app import App
    from views.appView import AppView
from pyhtmlgui import PyHtmlView
from views.sidebar.shotsView import ShotsView
from app_windows.settings.settings import SettingsInstance



class SidebarButtonsView(PyHtmlView):
    DOM_ELEMENT_CLASS = "row menu"
    TEMPLATE_STR = '''
    <div class="col-md-12 item {% if pyview.parent.parent.currentView.current_view == pyview.parent.parent.currentView.settingsView %} selected {% endif %}" onclick='pyview.parent.show_settings();'>
        Settings
    </div>
    <div {% if pyview.parent.parent.currentView.processingView.subject.status == "failed" %}style="color:#ff0000bb !important"{% endif %} class="col-md-12 item {% if pyview.parent.parent.currentView.current_view == pyview.parent.parent.currentView.processingView %} selected {% endif %}" onclick='pyview.parent.show_processing();'>
        Processing {% if pyview.parent.parent.currentView.processingView.subject.status == "failed" %}failed{% endif %}
    </div>
    <div class="col-md-12 item" style="height:3px"'> </div> 
    '''
    def __init__(self, subject: App, parent):
        super().__init__(subject, parent)
        self.add_observable(self.parent.parent.currentView.processingView.subject)

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
        self.shotsView = ShotsView(subject=subject.shots.shots, parent=self, settingsInstance=SettingsInstance())
        self.buttonsView = SidebarButtonsView(subject=subject, parent=self)
        self.current_search = ""

    def show_settings(self):
        self.shotsView.select_shot(None)
        if self.parent.currentView.show_settingsView() is True:
            self.buttonsView.update()

    def show_processing(self):
        self.shotsView.select_shot(None)
        if self.parent.currentView.show_processingView() is True:
            self.buttonsView.update()

    def show_shot(self, shot):
        if self.parent.currentView.show_shotView(shot) is True:
            self.buttonsView.update()

    def search(self, value):
        self.current_search = value
        self.shotsView.search(value)
