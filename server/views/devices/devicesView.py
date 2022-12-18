from __future__ import annotations

import re
from typing import TYPE_CHECKING

from app.tasks.task_NetworkScan import TaskNetworkScanInstance
from app.tasks.task_SyncShots import TaskSyncShotsInstance
from app.tasks.task_UpdateClients import TaskUpdateClientsInstance

if TYPE_CHECKING:
    from app.app import App
from pyhtmlgui import PyHtmlView, ObservableListView
from app.devices.devices import DevicesInstance


class DevicesView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="main">
        <div class="topMenu row" style="height:50px">
            <div class="col-md-2 topMenuItem">
                <button class="btn" onclick='pyview.shutdown();'> Shutdown Devices </button>
            </div>
            {{ pyview.task_networkscan.render() }}
            {{ pyview.task_updateclients.render() }}  
            <!--- { { pyview.task_syncshots.render() } } --->
            <div class="col-md-4"></div>
        </div>
        <div class="devicelist">
            <table id="devicetable" class="table">
                <thead>
                    <tr>
                        <th onclick="pyview.sort_by('ip-{{pyview.other_sort_dir}}')">IP</th>
                        <th onclick="pyview.sort_by('id-{{pyview.other_sort_dir}}')">ID</th>
                        <th onclick="pyview.sort_by('type-{{pyview.other_sort_dir}}')">Type</th>
                        <th onclick="pyview.sort_by('name-{{pyview.other_sort_dir}}')">Name</th>
                        <th onclick="pyview.sort_by('status-{{pyview.other_sort_dir}}')">Status</th>
                        <th onclick="pyview.sort_by('version-{{pyview.other_sort_dir}}')">Version</th>
                        <th onclick="pyview.sort_by('heartbeat-{{pyview.other_sort_dir}}')">Heartbeat</th>
                        <th onclick="pyview.sort_by('diskfree-{{pyview.other_sort_dir}}')">Disk Free/Total</th>
                        <th>AWB gains</th>
                        <th>D/A gains</th>
                        <th>Exposure</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                {{ pyview.device_list.render() }}
            </table>            
        </div>      
    </div>      
    '''

    def __init__(self, subject: App, parent):
        super().__init__(subject, parent)
        self.device_list = ObservableListView(subject=subject.devices, parent=self, item_class=DeviceRowView, dom_element="tbody", sort_key=lambda x: x.subject.device_id)
        self.task_networkscan = TaskNetworkscanView(TaskNetworkScanInstance(), self)
        self.task_syncshots = TaskSyncShotsView(TaskSyncShotsInstance(), self)
        self.task_updateclients = TaskUpdateClientsView(TaskUpdateClientsInstance(), self)
        self.current_sort_key = "ip"
        self.current_sort_dir = "a"
        self.other_sort_dir = "d"

    def sort_by(self, keydir):
        key, direction = keydir.split("-")
        if key == "ip":
            self.device_list.sort_key = lambda x:x.subject.ip
        elif key == "id":
            self.device_list.sort_key = lambda x: x.subject.device_id
        elif key == "type":
            self.device_list.sort_key = lambda x: x.subject.device_type
        elif key == "name":
            self.device_list.sort_key = lambda x: [re.sub("[0-9-]", "", x.subject.name), ] + [v.zfill(3) for v in re.sub("[^0-9-]", "", x.subject.name).split("-")]
        elif key == "status":
            self.device_list.sort_key = lambda x: x.subject.status
        elif key == "version":
            self.device_list.sort_key = lambda x: x.subject.version
        elif key == "heartbeat":
            self.device_list.sort_key = lambda x: x.subject.latest_heartbeat_time_diff
        elif key == "diskfree":
            self.device_list.sort_key = lambda x: x.subject.diskfree
        self.device_list.sort_reverse = direction == "d"
        self.current_sort_key = key
        self.current_sort_dir = direction
        self.other_sort_dir = "a" if direction == "d" else "d"
        if self.is_visible:
            self.update()

    def shutdown(self):
        DevicesInstance().shutdown()

    def sync(self):
        DevicesInstance().cameras.sync_shotlists()


class DeviceRowView(PyHtmlView):
    DOM_ELEMENT = "tr"
    TEMPLATE_STR = '''
    <td> {{pyview.subject.ip}} </td>
    <td> {{pyview.subject.device_id}} </td>
    <td> {{pyview.subject.device_type}} </td>
    <td> {{pyview.subject.name}} </td>
    <td> {{pyview.subject.status}} </td>
    <td> {{pyview.subject.version}} </td>
    <td> {{pyview.subject.latest_heartbeat_time_diff}} </td>
    <td> {{pyview.subject.diskfree}}/{{pyview.subject.disksize}} </td>
    {% if pyview.subject.device_type == "camera" %}
        <td> {{"%.3f"|format(pyview.subject.camera.settings.awb_gains[0])}} / {{"%.3f"|format(pyview.subject.camera.settings.awb_gains[1])}} </td>
        <td> {{"%.3f"|format(pyview.subject.camera.settings.digital_gain)}} / {{"%.3f"|format(pyview.subject.camera.settings.analog_gain)}}  </td>
        <td> {{pyview.subject.camera.settings.exposure_speed}} </td>
    {% else %}
        <td> </td>
        <td> </td>
        <td> </td>
    {% endif %}
    <td style="color:#000">
        <button class="btn" onclick="pyview.install_device()"> Update </button>
        <button class="btn" onclick="pyview.reboot_device()"> Reboot </button>
    </td>
    '''

    def install_device(self):
        self.subject.deploy()

    def reboot_device(self):
        self.subject.reboot()


# idle, ping_scan, api_scan, inspecting, ssh_scan
class TaskNetworkscanView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="col-md-2 topMenuItem" >
        {% if pyview.subject.status == "idle" %} 
            <button class="btn" onclick='pyview.start_scan();'> Search Devices </button>
        {% else %}
            {% if pyview.subject.status == "ping_scan"  %} Step 1/5 Ping scan {% endif %}
            {% if pyview.subject.status == "api_scan"   %} Step 2/5 API scan{% endif %}
            {% if pyview.subject.status == "inspecting" %} Step 3/5 Inspecting results{% endif %}
            {% if pyview.subject.status == "ssh_scan"   %} Step 4/5 SSH scan {% endif %}
            {% if pyview.subject.status == "trigger_heartbeat" %} Step 5/5 Trigger Heartbeat {% endif %}
        {% endif %}
    </div>
    '''

    def __init__(self, subject, parent):
        super().__init__(subject, parent)

    def start_scan(self):
        self.subject.run()


class TaskUpdateClientsView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="col-md-2 topMenuItem" >
        {% if pyview.subject.status == "idle" %} 
            <button class="btn" onclick='pyview.subject.run();'> Update Devices </button>
        {% else %}
            {% if pyview.subject.status == "deploying"  %} Deploying ({{pyview.subject.percent_done}}%) {% endif %}
            {% if pyview.subject.status == "installing"   %} Installing{% endif %}
        {% endif %}
    </div>
    '''

    def __init__(self, subject, parent):
        super().__init__(subject, parent)


# idle, ping_scan, api_scan, inspecting, ssh_scan
class TaskSyncShotsView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="col-md-2 topMenuItem" >
        {% if pyview.subject.status == "idle" %} 
            <button class="btn" onclick='pyview.start_sync();'> Sync Shotlists </button>
        {% else %}
             {% if pyview.subject.status == "list" %}Syncing lists {% endif %}
             {% if pyview.subject.status == "shots" %}Syncing shots{% endif %}
        {% endif %}
    </div>
    '''

    def __init__(self, subject, parent):
        super().__init__(subject, parent)

    def start_sync(self):
        self.subject.run()
