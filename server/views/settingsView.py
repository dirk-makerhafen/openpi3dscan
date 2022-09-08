from pyhtmlgui import PyHtmlView
from app.tasks.task_UpdateServer import TaskUpdateServerInstance
from views.settings.settingsCameraView import CameraSettingsView
from views.settings.settingsCardReaderView import CardReaderView
from views.settings.settingsFirmwareView import FirmwareSettingsView
from views.settings.settingsHostnameView import HostnameSettingsView
from views.settings.settingsRealityCaptureView import RealityCaptureView
from views.settings.settingsRebootView import RebootShutdownView
from views.settings.settingsSequenceView import SequenceSettingsView
from views.settings.settingsUsbStorageView import UsbStorageView
from views.settings.settingsWirelessView import WirelessSettingsView


class TaskUpdateServerView(PyHtmlView):
    TEMPLATE_STR = '''
        {% if pyview.subject.status == "idle" %} 
            <button class="btn" onclick='pyview.subject.run();'> Update Server </button>
        {% else %}
            <p class="btn">{{pyview.subject.status}}</p>
        {% endif %}
    '''


class SettingsView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="main">
    
        {{pyview.cameraSettingsView.render()}}
    
        {{pyview.sequenceSettingsSpeedView.render()}}  
    
        {{pyview.cardReaderView.render()}}  

        {{pyview.wirelessSettingsView.render()}}  

        {{pyview.firmwareSettingsView.render()}}  
                  
        {{pyview.realityCaptureView.render()}}  
        
        {{pyview.usbStorageView.render()}}  
        
          
        <div class="System">
            <div class="row justify-content-center" style="width:100%">
                <div class="col-md-12">
                    <div class="list-group mb-5 shadow">
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Version</div>
                            </div>
                        </div>
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-10">
                                    <strong class="mb-0">Version</strong>
                                    <p class="text-muted mb-0">Current server version</p>
                                </div>
                                <div class="col-auto">
                                    {{pyview.subject.settings.VERSION}}
                                </div>
                            </div>
                        </div>
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-10">
                                    <strong class="mb-0">Online Updates</strong>
                                    <p class="text-muted mb-0">Check for updates and install if available. Server will reboot after updates are installed.</p>
                                </div>
                                <div class="col-auto">
                                    {{pyview.updateServerView.render()}}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>   
            </div>
        </div>    

        {{pyview.rebootShutdownView.render()}}  

         {{pyview.hostnameView.render()}}  

    </div> 
    
    '''

    def __init__(self, subject, parent):
        super().__init__(subject, parent)
        self.sequenceSettingsSpeedView = SequenceSettingsView(self.subject.settings.sequenceSettingsSpeed, self)
        self.cameraSettingsView = CameraSettingsView(self.subject.settings.cameraSettings, self)
        self.firmwareSettingsView = FirmwareSettingsView(self.subject.settings.firmwareSettings, self)
        self.wirelessSettingsView = WirelessSettingsView(self.subject.settings.wirelessSettings, self)
        self.updateServerView = TaskUpdateServerView(TaskUpdateServerInstance(), self)
        self.realityCaptureView = RealityCaptureView(self.subject, self)
        self.usbStorageView = UsbStorageView(self.subject.usbDisks, self)
        self.rebootShutdownView = RebootShutdownView(self.subject, self)
        self.cardReaderView = CardReaderView(self.subject.cardReader, self)
        self.hostnameView = HostnameSettingsView(self.subject.settings.hostnameSettings, self)

