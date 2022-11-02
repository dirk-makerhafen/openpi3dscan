import subprocess
import threading
import time
from pyhtmlgui import Observable
from app.files.shots import ShotsInstance
from app.files.usbDisk import UsbDisk


class UsbDisks(Observable):
    def __init__(self):
        super().__init__()
        self.disks = []
        self.load_worker = None
        self.status = "idle"
        for i in range(5):
            self._load()
            try:
                stdout = subprocess.check_output('mount', shell=True, timeout=20, stderr=subprocess.STDOUT, ).decode("UTF-8")
            except:
                stdout = ""
            if "/shots" in stdout:
                break
            time.sleep(10)
        ShotsInstance().load_shots_from_disk()

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
        else:
            if len(self.disks) > 0:
                self.disks[0].get_diskspace()
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
                line = line.replace("\t", " ").replace("└─", "")
                while "  " in line:
                    line = line.replace("  ", " ")
                if len(line) < 5:
                    continue
                name, fstype, fsver, label, uuid, rest = line.split(" ", 5)
                disk = self.get_disk_by_uid(uuid)
                if disk is None:
                    self.disks.append(UsbDisk(name, fstype, fsver, label, uuid))

            except Exception as e:
                print(e)
        toremove = []
        for disk in self.disks:
            if disk.uuid not in stdout:
                toremove.append(disk)
        for r in toremove:
            self.disks.remove(r)
        self.automount()
        self.set_status("idle")
        self.load_worker = None
        self.notify_observers()

    def get_disk_by_uid(self, uid):
        try:
            return [d for d in self.disks if d.uuid == uid][0]
        except:
            return None

