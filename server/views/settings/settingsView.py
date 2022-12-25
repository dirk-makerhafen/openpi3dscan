from pyhtmlgui import PyHtmlView
from views.settings.settingsCameraView import CameraSettingsView
from views.settings.settingsCardReaderView import CardReaderView
from views.settings.settingsDropboxView import SettingsDropboxView
from views.settings.settingsFirmwareView import FirmwareSettingsView
from views.settings.settingsHostnameView import HostnameSettingsView
from views.settings.settingsImageCalibrationView import CameraImageCalibationView
from views.settings.settingsRealityCaptureView import RealityCaptureView
from views.settings.settingsRebootView import RebootShutdownView
from views.settings.settingsScannerView import SettingsScannerView
from views.settings.settingsSequenceView import SequenceSettingsView
from views.settings.settingsUpdateView import SettingsUpdateView
from views.settings.settingsUsbStorageView import UsbStorageView
from views.settings.settingsWirelessView import WirelessSettingsView
from views.settings.settingsBackupView import SettingsBackupView


class SettingsView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="main">
        {{ pyview.lockSettingsView.render() }}
        {% if pyview.subject.settings.locked == False %}
            {{pyview.cameraSettingsView.render()}}
        {% endif %}
        {{pyview.cameraImageCalibationView.render()}}  
        
        {% if pyview.subject.settings.locked == False %}
            {{pyview.sequenceSettingsSpeedView.render()}}  
        {% endif %}
        
        {{pyview.cardReaderView.render()}}  

        {{pyview.wirelessSettingsView.render()}}  

        {{pyview.usbStorageView.render()}}  
        
        {% if pyview.subject.settings.locked == False %}
            {{pyview.firmwareSettingsView.render()}}  
            {{pyview.realityCaptureView.render()}}  
            {{pyview.scannerSettingsView.render()}} 
            {{pyview.dropboxSettingsView.render()}}  
            {{pyview.settingsUpdateView.render()}}          
            {{pyview.hostnameView.render()}}  
            {{pyview.settingsBackupView.render()}}  
        {% endif %}
        {{pyview.rebootShutdownView.render()}}  
    </div> 
    
    '''

    def __init__(self, subject, parent):
        super().__init__(subject, parent)
        self.add_observable(self.subject.settings)
        self.sequenceSettingsSpeedView = SequenceSettingsView(self.subject.settings.sequenceSettingsSpeed, self)
        self.cameraSettingsView = CameraSettingsView(self.subject.settings.cameraSettings, self)
        self.cameraImageCalibationView = CameraImageCalibationView(self.subject.settings.cameraSettings, self)
        self.firmwareSettingsView = FirmwareSettingsView(self.subject.settings.firmwareSettings, self)
        self.wirelessSettingsView = WirelessSettingsView(self.subject.settings.wirelessSettings, self)
        self.realityCaptureView = RealityCaptureView(self.subject.settings.realityCaptureSettings, self)
        self.usbStorageView = UsbStorageView(self.subject.usbDisks, self)
        self.rebootShutdownView = RebootShutdownView(self.subject, self)
        self.cardReaderView = CardReaderView(self.subject.cardReader, self)
        self.hostnameView = HostnameSettingsView(self.subject.settings.hostnameSettings, self)
        self.scannerSettingsView = SettingsScannerView(self.subject.settings.settingsScanner, self)
        self.dropboxSettingsView = SettingsDropboxView(self.subject.settings.settingsDropbox, self)
        self.settingsBackupView = SettingsBackupView(self.subject.settings, self)
        self.settingsUpdateView = SettingsUpdateView(self.subject.settings, self)
        self.lockSettingsView = LockSettingsView(self.subject.settings, self)