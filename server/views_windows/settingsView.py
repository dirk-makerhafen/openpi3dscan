from pyhtmlgui import PyHtmlView

from views_windows.settings.settingsCacheView import SettingsCacheView
from views_windows.settings.settingsDropboxView import SettingsDropboxView
from views_windows.settings.settingsRealityCaptureView import SettingsRealityCaptureView
from views_windows.settings.settingsLocationsView import SettingsLocationsView
from views_windows.settings.settingsRemoteHostsView import SettingsRemoteHostsView


class SettingsView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="main">
                      
        {{pyview.realityCaptureView.render()}}  
        
        {{pyview.locationsSettingsView.render()}}  
        {{pyview.remoteHostsView.render()}}  
        {{pyview.settingsCacheView.render()}}  
        {{pyview.settingsDropboxView.render()}}  

    </div> 
    
    '''

    def __init__(self, subject, parent):
        super().__init__(subject, parent)
        self.realityCaptureView = SettingsRealityCaptureView(self.subject.settings.realityCaptureSettings, self)
        self.locationsSettingsView = SettingsLocationsView(self.subject.settings.settingsLocations, self)
        self.remoteHostsView = SettingsRemoteHostsView(self.subject.settings.settingsRemoteHosts, self)
        self.settingsCacheView = SettingsCacheView(self.subject.settings.settingsCache, self)
        self.settingsDropboxView = SettingsDropboxView(self.subject.settings.settingsDropbox, self)
