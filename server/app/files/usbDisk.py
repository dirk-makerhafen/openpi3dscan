import os.path
import subprocess
import time
import glob
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
        self.shots_available = 0
        self.oldest_shot = ""
        self.newest_shot = ""

    @property
    def is_primary(self):
        return SettingsInstance().primary_disk == self.uuid

    def set_as_primary(self):
        self.usb_disks.set_primary(self.uuid)

    def set_status(self, status):
        self.status = status
        self.usb_disks.notify_observers()

    def load(self):
        self.set_status("Loading")
        self.mount()
        self.load_stats()
        ShotsInstance().load_shots_from_dir("/shots/%s" % self.uuid)
        self.set_status("Active")

    def unload(self):
        self.set_status("Unloading")
        ShotsInstance().unload_dir("/shots/%s" % self.uuid)
        self.umount()
        self.set_status("")

    def mount(self):
        if not os.path.exists("/shots/%s" % self.uuid):
            os.system("mkdir -p /shots/%s" % self.uuid)
        try:
            stdout = subprocess.check_output("sudo mount '%s' '/shots/%s'" % (self.name, self.uuid), shell=True, timeout=60, stderr=subprocess.STDOUT, ).decode("UTF-8")
        except:
            stdout = ""
        time.sleep(5)

    def umount(self):
        try:
            stdout = subprocess.check_output("sudo umount '%s' '/shots/%s'" % (self.name, self.uuid), shell=True, timeout=10, stderr=subprocess.STDOUT, ).decode("UTF-8")
        except:
            stdout = ""
        try:
            stdout = subprocess.check_output('mount | grep %s' % self.uuid, shell=True, timeout=10, stderr=subprocess.STDOUT, ).decode("UTF-8")
        except:
            stdout = ""
        if self.uuid not in stdout:
            os.rmdir('/shots/%s' % self.uuid)

    def load_stats(self):
        self._get_diskspace()
        self.shots_available = 0
        self.oldest_shot = ""
        self.newest_shot = ""

        if self.status == "":
            self.mount()

        for path in glob.glob(os.path.join("/shots/%s" % self.uuid, "*")):
            if os.path.exists(os.path.join(path, "metadata.json")) or os.path.exists(os.path.join(path, "images", "normal")) or (os.path.exists(os.path.join(path, "normal")) and os.path.exists(os.path.join(path, "projection"))):
                shot_id = os.path.split(path)[1].split(" ")[0]
                if shot_id > self.newest_shot or self.newest_shot == "":
                    self.newest_shot = shot_id
                if shot_id < self.oldest_shot or self.oldest_shot == "":
                    self.oldest_shot = shot_id
                self.shots_available += 1

        if self.status == "":
            self.umount()

    def _get_diskspace(self):
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
            print("failed to get disk space from line'%s'" % line)
        self.notify_observers()
