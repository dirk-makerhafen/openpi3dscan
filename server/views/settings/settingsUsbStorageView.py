from pyhtmlgui import PyHtmlView,ObservableListView

from app.settings.settings import CLEANUP_DELETE_PERCENT_MAX, SettingsInstance


class UsbDiskView(PyHtmlView):
    TEMPLATE_STR = '''
        <tr style="border-top: 1px solid lightgray;   line-height: 3em;">
        <td>{{pyview.subject.label}}</td>
        <td>{{pyview.subject.status}}</td>
        <td>{{pyview.subject.disk_free}} / {{pyview.subject.disk_total}}</td>
        <td> {{pyview.subject.shots_available}}</td>
        <td>{{pyview.subject.oldest_shot}} / {{pyview.subject.newest_shot}}</td>
        <td>{{pyview.subject.is_primary}}</td>
        <td>
            {% if pyview.subject.status == "Active" %}
                <button style="width:50%" class="btn btnfw" onclick="pyview.subject.unload()">Eject</button>
            {% elif  pyview.subject.status == "" %}
                <button style="width:50%"  class="btn btnfw" onclick="pyview.subject.load()">Activate</button>
            {% endif %}
            {% if pyview.subject.is_primary == false %}
                <button style="width:50%" class="btn btnfw" onclick="pyview.subject.set_as_primary()">Set as Primary</button>
            {% endif %}
        </td>
        </tr>
    '''

class UsbStorageView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="Storage">
        <div class="row justify-content-center" style="width:100%">
            <div class="col-md-12">
                <div class="list-group mb-5 shadow">
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Storage</div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-3">
                                <strong class="mb-0">USB-Disks</strong>
                                <p class="text-muted mb-0">List of connected USB Disks</p>
                                {% if pyview.subject.status == "idle" %}
                                    <button class="btn btnfw" onclick="pyview.subject.load()">Reload</button>
                                {% else %}
                                    <p>{{pyview.subject.status }}</p>
                                {% endif %}
                            </div>
                            <div class="col-md-9">
                                <table style="width:100%;text-align:center">
                                    <thead>
                                        <tr>
                                            <th style="text-align:center">Name</th>
                                            <th style="text-align:center">Status</th>
                                            <th style="text-align:center">Disk Free / Size</th>
                                            <th style="text-align:center">Nr of Shots</th>
                                            <th style="text-align:center">From / To</th>
                                            <th style="text-align:center">Primary</th>
                                            <th style="text-align:center">Action</th>
                                        </tr>
                                    </thead>
                                    {{ pyview.disks.render() }}
                                </table>
                            </div>
                        </div>
                    </div>
                    {% if pyview.settingsInstance.locked == False %}
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <strong class="mb-0">Cleanup old scans</strong>
                                <p class="text-muted mb-0">Delete the oldest {{pyview.settingsInstance.cleanup_delete_percent}}% of scans on the primary disk to free space. This cannot be undone.</p>
                                {% if pyview.cleanup_status %}<p class="text-danger mb-0">{{pyview.cleanup_status}}</p>{% endif %}
                            </div>
                            <div class="col-md-2">
                                <label class="mb-0" for="cleanup_percent">Delete oldest (%)</label>
                                <input class="form-control" id="cleanup_percent" type="number" min="0" max="{{pyview.max_delete_percent}}" value="{{pyview.settingsInstance.cleanup_delete_percent}}"/>
                                <button class="btn btnfw" style="margin-top:5px" onclick='pyview.save_delete_percent($("#cleanup_percent").val())'>Save</button>
                            </div>
                            <div class="col-md-2" style="text-align:center">
                                {% if pyview.subject.primary_disk and pyview.subject.primary_disk.status == "Active" %}
                                    <button class="btn btn-warning" onclick='pyview.show_cleanup_confirm()'> Cleanup old scans </button>
                                {% else %}
                                    <p class="text-muted mb-0">No active primary disk</p>
                                {% endif %}
                            </div>
                        </div>
                        {% if pyview.confirm_visible %}
                            <div style="z-index:999;position:fixed;left:30%;top:20%;width:40%;background-color:white;padding:10px;border:5px solid #f33;">
                                <div style="font-weight:bold;padding-bottom:10px;text-align:center">
                                    Delete old scans from {{pyview.subject.primary_disk.label}}?
                                </div>
                                <p class="text-muted mb-0">{{pyview.cleanup_info}}</p>
                                <div class="row">
                                    <div class="col-md-6" style="font-weight:bold;">
                                        <button class="btn btn-danger" onclick='pyview.cleanup_old_scans()'>DELETE</button>
                                    </div>
                                    <div class="col-md-6" style="font-weight:bold;">
                                        <button class="btn btn-success" onclick='pyview.hide_cleanup_confirm()'>Cancel</button>
                                    </div>
                                </div>
                            </div>
                        {% endif %}
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
    '''

    def __init__(self, subject, parent):
        super().__init__(subject, parent)
        self.disks = ObservableListView(subject=subject.disks, parent=self, item_class=UsbDiskView, dom_element="tbody")
        self.settingsInstance = SettingsInstance()
        self.max_delete_percent = CLEANUP_DELETE_PERCENT_MAX
        self.cleanup_status = ""
        self.cleanup_info = ""
        self.confirm_visible = False

    def save_delete_percent(self, value):
        self.settingsInstance.set_cleanup_delete_percent(value)
        self.cleanup_status = "Deleting oldest %d%% on cleanup." % self.settingsInstance.cleanup_delete_percent
        if self.is_visible:
            self.update()

    def show_cleanup_confirm(self):
        if self.settingsInstance.locked:
            return
        disk = self.subject.primary_disk
        if disk is None or disk.status != "Active":
            self.cleanup_status = "No active primary disk."
            self.confirm_visible = False
            if self.is_visible:
                self.update()
            return
        preview = self.subject.cleanup_preview()
        gb = 1024 ** 3
        info = "Delete %d of %d scan(s) (oldest %d%%)? Free space: %.1f GB." % (
            preview["count"], preview["total"], self.settingsInstance.cleanup_delete_percent,
            preview["free_bytes"] / gb,
        )
        if preview["skipped"]:
            info += " %d scan(s) in use will be skipped." % preview["skipped"]
        self.cleanup_info = info
        self.confirm_visible = True
        if self.is_visible:
            self.update()

    def hide_cleanup_confirm(self):
        self.confirm_visible = False
        if self.is_visible:
            self.update()

    def cleanup_old_scans(self):
        if self.settingsInstance.locked:
            return
        stats = self.subject.cleanup_old_scans()
        gb = 1024 ** 3
        self.cleanup_status = "Deleted %d scan(s), freed %.1f GB." % (
            stats["deleted"], (stats["free_after"] - stats["free_before"]) / gb,
        )
        self.confirm_visible = False
        if self.is_visible:
            self.update()
