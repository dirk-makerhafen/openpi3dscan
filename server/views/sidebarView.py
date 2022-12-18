from pyhtmlgui import PyHtmlView
from views.sidebar.sidebarShotsView import SidebarShotsView
from app.settings.settings import SettingsInstance
from views.sidebar.sidebarTopView import SidebarTopView


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

    def __init__(self, subject, parent):
        super().__init__(subject, parent)
        self._mainView = self.parent.mainView
        self.shotsView = SidebarShotsView(subject=subject.shots.shots, parent=self, settingsInstance=SettingsInstance())
        self.buttonsView = SidebarTopView(subject=subject, parent=self)
        self.current_search = ""

    def show_devices(self):
        self.shotsView.select_shot(None)
        if self.parent.currentView.show_devicesView() is True:
            self.buttonsView.update()

    def show_settings(self):
        self.shotsView.select_shot(None)
        if self.parent.currentView.show_settingsView() is True:
            self.buttonsView.update()

    def show_liveview(self):
        self.shotsView.select_shot(None)
        if self.parent.currentView.show_liveView() is True:
            self.buttonsView.update()

    def show_shot(self, shot):
        if self.parent.currentView.show_shotView(shot) is True:
            self.buttonsView.update()

    def search(self, value):
        self.current_search = value
        self.shotsView.search(value)
