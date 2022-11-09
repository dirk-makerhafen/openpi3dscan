import io
import math
import os
import queue
import threading
import time

import gevent
import pexpect
import requests
from pyhtmlgui import Observable

from .device_Camera import Camera
from .device_Light import Light
from .device_Projector import Projector
from ..settings.settings import SettingsInstance

SSH_OPTIONS = '-q -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -oPubkeyAuthentication=no'
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


class Device(Observable):
    def __init__(self):
        super().__init__()
        self.camera = Camera(self)
        self.projector = Projector(self)
        self.light = Light(self)

        self.device_type = "device"
        self.ip = ""
        self.device_id = ""
        self.name = ""
        self.username = "openpi3dscan"
        self.password = "openpi3dscan"

        self.version = ""

        self.status = "offline"
        # offline   -> default state
        # online    -> device is ready to be used
        # warmup    -> for cam after first heartbeart and before benchmark is finished
        # shutdown  -> after shutdown has been called successfuly
        # installing -> installing client
        # rebooting  -> reboot triggered

        self.latest_heartbeat_time = 0
        self.disksize = -1
        self.diskfree = -1
        self.online_ping = False
        self.busy_until = 0
        self.task_queue = queue.Queue()
        self.task_thread = threading.Thread(target=self._task_thread, daemon=True)
        self.task_thread.start()

    @property
    def latest_heartbeat_time_diff(self):
        if self.latest_heartbeat_time == 0:
            return -1
        return int(time.time() - self.latest_heartbeat_time)

    @property
    def is_available(self):
        if self.device_type == "device":
            return False
        if self.latest_heartbeat_time_diff > 650 and self.status == "online":
            self._set_status("offline")
        return self.status == "online"

    def _set_status(self, new_status):
        self.status = new_status
        self.notify_observers()

    def check_ssh_connection(self):
        self.task_queue.put(self._check_ssh_connection)

    def _check_ssh_connection(self):
        result = self._ssh("cat /boot/device.settings", timeout=15)
        if result is None:
            self.notify_observers()
            return
        if result.find("TYPE") != -1:  # our config exists
            self.device_id = result.split("ID", 1)[1].split("=", 1)[1].split("\n")[0].strip()
            self.device_type = result.split("TYPE", 1)[1].split("=", 1)[1].split("\n")[0].strip()
            self.name = result.split("NAME", 1)[1].split("=", 1)[1].split("\n")[0].strip()
        elif result.lower().find("no such file or") != -1:  # our config does not exist
            self.name = ""
            legacy_id = self._ssh("cat /boot/id.txt", timeout=15)
            try:
                legacy_id = int(legacy_id)
            except:
                legacy_id = "no such file"
            if legacy_id.lower().find("no such file") != -1:  # legacy config does not exist
                self.device_id = ""
                self.device_type = "device"
            else:
                self.device_id = int(legacy_id)
                legacy_type = self._ssh("cat /boot/group.txt", timeout=15).strip()
                if legacy_type == "1":
                    self.device_type = "camera"
                    self.name = "unknown"
                if legacy_type == "2":
                    self.device_type = "projector"
                    self.name = "P%s" % self.device_id
        self.notify_observers()

    def deploy(self):
        self.task_queue.put(self._deploy)

    def _deploy(self):
        self._set_status("installing")
        client_dir = os.path.join(SCRIPT_DIR, "..", "..", "..", "client")
        self._ssh_exec('scp -r %s "%s" %s@%s:/home/%s/' % (SSH_OPTIONS, client_dir, self.username, self.ip, self.username), 180)
        rotation = SettingsInstance().settingsScanner.camera_rotation
        if self.name != "" and self.device_type == "camera":
            if self.name in SettingsInstance().settingsScanner.flipped_cameras:# this camera is flipped
                if rotation   ==   0: rotation = 180
                elif rotation ==  90: rotation = 270
                elif rotation == 180: rotation = 0
                elif rotation == 270: rotation = 90
        self._ssh('cd /home/%s/client ; python3 run.py install "%s" "%s" "%s" "%s" "install_after_reboot"' % (self.username, self.device_id, self.device_type, self.name, rotation), timeout=180)
        self.latest_heartbeat_time = 0
        self._ssh('sudo reboot & ', timeout=10)
        self.notify_observers()

    def reboot(self):
        self.task_queue.put(self._reboot)

    def _reboot(self):
        self._set_status("reboot")
        r = None
        try:
            r = self.api_request("/reboot", timeout=5)
        except:
            pass
        if r is None:
            print("reboot via sshd")
            self._ssh('sudo reboot & ', timeout=10)

    def shutdown(self):
        self.task_queue.put(self._shutdown)

    def _shutdown(self):
        self._set_status("shutdown")
        r = None
        try:
            r =self.api_request("/shutdown", timeout=5)
        except:
            pass
        if r is None:
            print("shutdown via sshd")
            self._ssh("sudo shutdown -h now &", timeout=10)

    def api_request(self, url, max_time=9, max_tries=5, timeout=6):
        result = None
        trynr = 0
        timeout_time = time.time() + max_time
        url = "http://%s:8080%s" % (self.ip, url)
        while True:
            trynr += 1
            try:
                result = requests.get(url, timeout=timeout)
                break
            except Exception as e:
                print(e)
                if trynr >= max_tries:
                    break
                if time.time() > timeout_time:
                    break

        try:
            if result.ok is False:
                result = None
        except:
            result = None

        return result

    def _task_thread(self):
        while True:
            task = self.task_queue.get()
            try:
                if type(task) == list:
                    args = task[1:]
                    task = task[0]
                    task(*args)
                else:
                    task()
            except Exception as e:
                print("failed to execute task", task, e)

    def _ssh(self, cmd, timeout=120):
        ssh_cmd = 'ssh %s@%s %s "%s"' % (self.username, self.ip, SSH_OPTIONS, cmd)
        return self._ssh_exec(ssh_cmd, timeout)

    def _ssh_exec(self, ssh_cmd, timeout):
        try:
            child = pexpect.spawnu(ssh_cmd, timeout=timeout)  # spawnu for Python 3
            child.expect(['[pP]assword: '])
            child.sendline(self.password)
        except:
            return None
        child.logfile = io.StringIO()
        try:
            child.expect(pexpect.EOF)
        except Exception as e:
            print("EOF FAILED", e)
            return None
        finally:
            child.close()
        return child.logfile.getvalue()

    def wait_locked(self):
        while self.busy_until > time.time():
            gevent.sleep(0.3)

    def lock(self, seconds):
        self.busy_until = time.time() + seconds

    def unlock(self):
        self.busy_until = 0
