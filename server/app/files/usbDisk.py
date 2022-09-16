import subprocess
import time
from pyhtmlgui import Observable


class UsbDisk(Observable):
    def __init__(self, name, fstype, fsver, label, uuid):
        super().__init__()
        self.name = name
        self.fstype = fstype
        self.fsver = fsver
        self.label = label
        self.uuid = uuid
        self.disk_total = "0G"
        self.disk_free = "0G"

    def mount(self):
        try:
            stdout = subprocess.check_output("sudo mount '%s' '/shots'" % (self.name,), shell=True, timeout=60, stderr=subprocess.STDOUT, ).decode("UTF-8")
        except:
            stdout = ""
        time.sleep(5)
        self.get_diskspace()

    def umount(self):
        try:
            stdout = subprocess.check_output("sudo mxount '%s' '/shots'" % (self.name,), shell=True, timeout=10, stderr=subprocess.STDOUT, ).decode("UTF-8")
        except:
            stdout = ""

    def get_diskspace(self):
        try:
            stdout = subprocess.check_output('df -h | grep "/shots"', shell=True, timeout=10, stderr=subprocess.STDOUT, ).decode("UTF-8")
        except:
            stdout = ""
        line = stdout.split("\n")[0]
        while "  " in line:
            line = line.replace("  ", " ")
        try:
            print(line)
            fs, size, used, avail, usedp, mount = line.split(" ")
            self.disk_total = size
            self.disk_free = avail
        except Exception as e:
            print(e)
            pass
