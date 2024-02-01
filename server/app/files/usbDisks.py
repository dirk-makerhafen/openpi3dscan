import subprocess
import threading
import time
from pyhtmlgui import Observable, ObservableList
from app.files.usbDisk import UsbDisk
from app.settings.settings import SettingsInstance

class UsbDisks(Observable):
    def __init__(self):
        super().__init__()
        self.disks = ObservableList()
        self.load_worker = None
        self.status = "idle"
        time.sleep(10)
        for i in range(5):
            self._load()
            if len(self.disks) > 1:
                break
            time.sleep(10)

    def set_primary(self, uuid):
        SettingsInstance().set_primary_disk(uuid)
        self.notify_observers()

    def set_status(self, status):
        self.status = status
        self.notify_observers()

    def load(self):
        if self.load_worker is None:
            self.load_worker = threading.Thread(target=self._load, daemon=True)
            self.load_worker.run()

    def _load(self):
        self.set_status("reload")
        try:
            stdout = subprocess.check_output('lsblk -fpro NAME,FSSIZE,LABEL,UUID,MOUNTPOINT | grep -i /dev/sd ', shell=True, timeout=30, stderr=subprocess.STDOUT, ).decode("UTF-8")
        except:
            stdout = ""

        for line in stdout.split("\n"):
            try:
                if len(line) < 5:
                    continue
                name, fssize, label, uuid, mountpoint = line.split(" ")
                if uuid.strip() == "":
                    continue
                disk = self.get_disk_by_uid(uuid)
                if disk is None:
                    disk = UsbDisk(self, name, fssize, label, uuid)
                    self.disks.append(disk)
                    disk.load()

            except Exception as e:
                print(e)
        toremove = []
        for disk in self.disks:
            if disk.uuid not in stdout:
                toremove.append(disk)
        for r in toremove:
            self.disks.remove(r)
        for disk in self.disks:
            disk.load_stats()
        self.load_worker = None
        self.set_status("idle")

    def get_disk_by_uid(self, uid):
        try:
            return [d for d in self.disks if d.uuid == uid][0]
        except:
            return None

