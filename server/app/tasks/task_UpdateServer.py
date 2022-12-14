import subprocess
import threading
import time
from pyhtmlgui import Observable
import os

from app.app import AppInstance


class Task_UpdateServer(Observable):
    def __init__(self):
        super().__init__()
        self.name = "UpdateServer"
        self.status = "idle"
        self.worker = None

    def set_status(self, value):
        self.status = value
        self.notify_observers()

    def run(self):
        if self.worker is None:
            self.worker = threading.Thread(target=self._run, daemon=True)
            self.worker.start()

    def _run(self):
        if self.status != "idle":
            return

        self.set_status("download")
        if os.path.exists("/home/pi/openpi3dscan"):
            subprocess.call("cd /home/pi/openpi3dscan ; sudo git reset --hard ; sudo git clean -f -d ; sudo git pull", shell=True)
        else:
            subprocess.call("cd /home/pi/ ; git clone 'https://github.com/dirk-makerhafen/openpi3dscan.git'", shell=True)

        if not os.path.exists("/home/pi/openpi3dscan"):
            self.set_status("download failed")
            time.sleep(10)
        else:
            app_dir_name = "server"
            if os.path.exists("/opt/openpi3dscan/apps/app/settings/settings.py"):
                app_dir_name = "apps"
            if os.path.exists("/opt/openpi3dscan/%s/app/settings/settings.py" % app_dir_name):
                installed_version = 0
                try:
                    installed_version = open("/opt/openpi3dscan/%s/app/settings/settings.py" % app_dir_name, "r").read().split("VERSION")[1].split("\n")[0].split("=")[1].strip()
                except Exception as e:
                    print(e)
                new_version = installed_version
                try:
                    new_version = open("/home/pi/openpi3dscan/%s/app/settings/settings.py" % app_dir_name, "r").read().split("VERSION")[1].split("\n")[0].split("=")[1].strip()
                except:
                    pass
                if installed_version == new_version:
                    self.set_status("up to date")
                    time.sleep(10)
                else:
                    self.set_status("installing")
                    subprocess.call("cd /home/pi/openpi3dscan/%s ; sudo python3 run.py install" % app_dir_name, shell=True)
                    self.set_status("rebooting")
                    time.sleep(3)
                    AppInstance().reboot()

        self.set_status("idle")
        self.worker = None
        
        
_taskUpdateServerInstance = None


def TaskUpdateServerInstance():
    global _taskUpdateServerInstance
    if _taskUpdateServerInstance is None:
        _taskUpdateServerInstance = Task_UpdateServer()
    return _taskUpdateServerInstance
