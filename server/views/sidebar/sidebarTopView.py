from pyhtmlgui import PyHtmlView, ObservableListView, ObservableList

class SidebarTopView(PyHtmlView):
    DOM_ELEMENT_CLASS = "row menu"
    TEMPLATE_STR = '''
    <div class="col-md-12 item {% if pyview._mainView.current_view == pyview._mainView.settingsView %} selected {% endif %}" onclick='pyview.parent.show_settings();'>
        Settings
    </div>
    <div class="col-md-12 item {% if pyview._mainView.current_view == pyview._mainView.devicesView %} selected {% endif %}" onclick='pyview.parent.show_devices();'>
        Devices
    </div>
    <div class="col-md-12 item {% if pyview._mainView.current_view == pyview._mainView.liveView %} selected {% endif %}" onclick='pyview.parent.show_liveview();'>
       Live
    </div>
    <div class="col-md-12 item" style="height:3px"'> </div> 
    '''
    def __init__(self, subject, parent, **kwargs):
        super().__init__(subject, parent, **kwargs)
        self._mainView = self.parent._mainView