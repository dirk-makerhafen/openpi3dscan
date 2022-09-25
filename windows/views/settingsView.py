from pyhtmlgui import PyHtmlView
from views.settings.settingsRealityCaptureView import RealityCaptureView
from views.settings.settingsScannerView import SettingsScannerView


class TaskUpdateServerView(PyHtmlView):
    TEMPLATE_STR = '''
    {% if pyview.subject.status == "idle" %} 
        <button class="btn" onclick='pyview.subject.run();'> Update Server </button>
    {% else %}
        <p style="color:green">{{pyview.subject.status}}</p>
    {% endif %}
    '''


class SettingsView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="main">
                      
        {{pyview.realityCaptureView.render()}}  
        
        {{pyview.scannerSettingsView.render()}}  
        
        
    </div> 
    
    '''

    def __init__(self, subject, parent):
        super().__init__(subject, parent)
        self.realityCaptureView = RealityCaptureView(self.subject.settings.realityCaptureSettings, self)
        self.scannerSettingsView = SettingsScannerView(self.subject.settings.settingsScanner, self)
