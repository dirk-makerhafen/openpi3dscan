import os
import subprocess
from pyhtmlgui import Observable


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
        self.get_diskspace()

    def mount(self):
        os.system("sudo mount '%s' '/shots'" % (self.NAME,))
        self.get_diskspace()

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
        self.load()
        self.automount()

    def automount(self):
        try:
            stdout = subprocess.check_output('mount', shell=True, timeout=10, stderr=subprocess.STDOUT, ).decode("UTF-8")
        except:
            stdout = ""
        if "/shots" not in stdout:
            if len(self.disks) > 0:
                self.disks[0].mount()
        self.notify_observers()

    def load(self):
        try:
            stdout = subprocess.check_output('lsblk -fp | grep -i /dev/sd | grep -v EFI | grep -v boot | grep -i fat', shell=True, timeout=10, stderr=subprocess.STDOUT, ).decode("UTF-8")
        except:
            stdout = ""
        for line in stdout.split("\n"):
            line = line.replace("\t"," ").replace("└─","")
            while "  " in line:
                line = line.replace("  "," ")
            if len(line) < 5:
                continue
            try:
                NAME, FSTYPE, FSVER, LABEL, UUID, REST = line.split(" ",5)
                if self.get_disk_by_uid(UUID) is None:
                    self.disks.append(UsbDisk(NAME, FSTYPE, FSVER, LABEL, UUID))
            except Exception as e:
                print(e)
        toremove = []
        for disk in self.disks:
            if disk.UUID not in stdout:
                toremove.append(disk)
        for r in toremove:
            self.disks.remove(r)
        self.notify_observers()

    def get_disk_by_uid(self, uid):
        try:
            return [d for d in self.disks if d.UUID == uid][0]
        except:
            return None

