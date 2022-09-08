import os
import subprocess
import threading
import time
from pyhtmlgui import Observable

from app.shots import ShotsInstance


class UsbDisk(Observable):
    def __init__(self, NAME, FSTYPE, FSVER, LABEL, UUID):
        super().__init__()
        self.NAME = NAME
        self.FSTYPE = FSTYPE
        self.FSVER = FSVER
        self.LABEL = LABEL
        self.UUID = UUID
        self.disk_total = "0G"
        self.disk_free = "0G"

    def mount(self):
        try:
            stdout = subprocess.check_output("sudo mount '%s' '/shots'" % (self.NAME,), shell=True, timeout=60, stderr=subprocess.STDOUT, ).decode("UTF-8")
        except:
            stdout = ""
        self.get_diskspace()

    def umount(self):
        try:
            stdout = subprocess.check_output("sudo mxount '%s' '/shots'" % (self.NAME,), shell=True, timeout=10, stderr=subprocess.STDOUT, ).decode("UTF-8")
        except:
            stdout = ""

    def get_diskspace(self):
        try:
            stdout = subprocess.check_output('df -h | grep "/shots"', shell=True, timeout=10, stderr=subprocess.STDOUT, ).decode("UTF-8")
        except:
            stdout = ""
        line = stdout.split("\n")[0]
        while "  " in line:
            line = line.replace("  "," ")
        try:
            print(line)
            fs,size,used,avail,usedp,mount = line.split(" ")
            self.disk_total = size
            self.disk_free = avail
        except Exception as e:
            print(e)
            pass

class UsbDisks(Observable):
    def __init__(self):
        super().__init__()
        self.disks = []
        self.load_worker = None
        self.status="idle"
        for i in range(5):
            self._load()
            try:
                stdout = subprocess.check_output('mount', shell=True, timeout=20, stderr=subprocess.STDOUT, ).decode("UTF-8")
            except:
                stdout = ""
            if "/shots" in stdout:
                break
            time.sleep(10)

    def set_status(self, status):
        self.status = status
        self.notify_observers()

    def automount(self):
        try:
            stdout = subprocess.check_output('mount', shell=True, timeout=20, stderr=subprocess.STDOUT, ).decode("UTF-8")
        except:
            stdout = ""
        if "/shots" not in stdout:
            if len(self.disks) > 0:
                self.disks[0].mount()
                ShotsInstance().load_shots_from_disk()
        self.notify_observers()

    def load(self):
        if self.load_worker is None:
            self.load_worker = threading.Thread(target=self._load, daemon=True)
            self.load_worker.run()

    def _load(self):
        self.set_status("reload")
        try:
            stdout = subprocess.check_output('lsblk -fp | grep -i /dev/sd | grep -v EFI | grep -v boot | grep -i fat', shell=True, timeout=30, stderr=subprocess.STDOUT, ).decode("UTF-8")
        except:
            stdout = ""

        for line in stdout.split("\n"):
            try:
                line = line.replace("\t"," ").replace("└─","")
                while "  " in line:
                    line = line.replace("  "," ")
                if len(line) < 5:
                    continue
                NAME, FSTYPE, FSVER, LABEL, UUID, REST = line.split(" ",5)
                disk = self.get_disk_by_uid(UUID)
                if disk is None:
                    self.disks.append(UsbDisk(NAME, FSTYPE, FSVER, LABEL, UUID))
                else:
                    disk.get_diskspace()
            except Exception as e:
                print(e)
        toremove = []
        for disk in self.disks:
            if disk.UUID not in stdout:
                toremove.append(disk)
        for r in toremove:
            self.disks.remove(r)
        self.automount()
        self.set_status("idle")
        self.load_worker = None
        self.notify_observers()


    def get_disk_by_uid(self, uid):
        try:
            return [d for d in self.disks if d.UUID == uid][0]
        except:
            return None

