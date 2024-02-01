import os.path
import subprocess
import time
from pyhtmlgui import Observable
from app.files.shots import ShotsInstance
from app.settings.settings import SettingsInstance


class UsbDisk(Observable):
    def __init__(self, usb_disks, name, fssize, label, uuid):
        super().__init__()
        self.usb_disks = usb_disks
        self.name = name
        self.fssize = fssize
        self.label = label
        self.uuid = uuid
        self.disk_total = fssize
        self.disk_free = ""
        self.status = ""

    @property
    def is_primary(self):
        return SettingsInstance().primary_disk == self.uuid

    def set_as_primary(self):
        self.usb_disks.set_primary(self.uuid)

    def set_status(self, status):
        self.status = status
        self.notify_observers()

    def mount(self):
        self.set_status("Loading")
        if not os.path.exists("/shots/%s" % self.uuid):
            os.system("mkdir -p /shots/%s" % self.uuid)
        try:
            stdout = subprocess.check_output("sudo mount '%s' '/shots/%s'" % (self.name, self.uuid), shell=True, timeout=60, stderr=subprocess.STDOUT, ).decode("UTF-8")
        except:
            stdout = ""
        time.sleep(5)
        self.get_diskspace()
        ShotsInstance().load_shots_from_dir("/shots/%s" % self.uuid)
        self.set_status("Active")

    def umount(self):
        self.set_status("Unloading")
        ShotsInstance().unload_dir("/shots/%s" % self.uuid)
        try:
            stdout = subprocess.check_output("sudo umount '%s' '/shots/%s'" % (self.name, self.uuid), shell=True, timeout=10, stderr=subprocess.STDOUT, ).decode("UTF-8")
        except:
            stdout = ""
        self.set_status("")


    def get_diskspace(self):
        try:
            stdout = subprocess.check_output('lsblk -fpro UUID,FSAVAIL,FSSIZE | grep %s' % self.uuid, shell=True, timeout=10, stderr=subprocess.STDOUT, ).decode("UTF-8")
        except:
            stdout = ""
        line = stdout.split("\n")[0]
        while "  " in line:
            line = line.replace("  ", " ")
        try:
            uuid, self.disk_free, self.disk_total = line.split(" ")
        except Exception as e:
            print(e)
            pass
        self.notify_observers()
