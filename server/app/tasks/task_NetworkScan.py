import json
import threading
from multiprocessing.pool import ThreadPool
import subprocess

import requests
from pyhtmlgui import Observable

from app.devices.devices import DevicesInstance

from .task import Task
from ..devices.device import Device

class Task_NetworkScan(Observable):
    def __init__(self):
        super().__init__()
        self.name = "NetworkScan"
        self.shot_quality = "speed"
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
            self.worker = None
            return
        self.set_status("ping_scan")

        ips = []
        ip_base = "192.168.99"
        for i in range(99,253):
            ip = "%s.%s" % (ip_base, i)
            ips.append(ip)

        with ThreadPool(15) as pool:
            ping_results = pool.map(lambda ip: self._ping(ip), ips)
            ips_active = [ips[i] for i,item in enumerate(ping_results) if item is not False]
            self.set_status("api_scan")
            device_id_results = pool.map(lambda ip: self._device_id(ip), ips_active)
            self.set_status("inspecting")
            for i, device_id_result in enumerate(device_id_results):
                ip = ips_active[i]
                if device_id_result is not None:  # req has some result from our api
                    device = DevicesInstance().get_device_by_id(device_id_result["id"])  # just in cast we have some unknown id in our network
                    if device is None:
                        device = Device()
                        device.device_id = device_id_result["id"]
                        device.ip = ip
                        device.name =  device_id_result["name"]
                        device.device_type = device_id_result["type"]
                        try:
                            device.version = device_id_result["version"]
                        except:
                            device.version = "unknown"
                        DevicesInstance().devices.append(device)
                        if device.device_type == "camera":
                            device.camera.shots.refresh_list()
                            #device.camera.performance.receive()

                    device.online_api = True
                    if device.ip != ip: # ip changed or new id:
                        old_device = DevicesInstance().get_device_by_ip(ip)
                        if old_device is not None:
                            old_device.ip = ""
                            old_device.online_ping = False
                            old_device.shotlist = []
                            old_device.notify_observers()
                        device.ip = ip
                    device.notify_observers()

                else: # no api response
                    device = DevicesInstance().get_device_by_ip(ip)
                    if device is not None:
                        device.notify_observers()

            for i, ping_result in enumerate(ping_results):
                ip = ips[i]
                device = DevicesInstance().get_device_by_ip(ip)
                if device is None and ping_result is not False:
                    device = Device()
                    device.ip = ip
                    DevicesInstance().devices.append(device)
                if device is not None:
                    device.online_ping = ping_result
                    device.notify_observers()
            self.set_status("ssh_scan")
            # check ssh
            devices = [d for d in DevicesInstance().devices if d.online_ping != False]
            ssh_results = pool.map(lambda device: device.check_ssh_connection(), devices)
            self.set_status("trigger_heartbeat")
            trigger_results = pool.map(lambda ip: self._trigger_heartbeat(ip), ips_active)

        self.set_status("idle")
        self.worker = None

    def _ping(self, host):
        try:
            stdout = subprocess.check_output("ping -c 1 -t 2 " + host, shell=True, timeout=10, stderr=subprocess.STDOUT)
            ping_time = round(float(stdout.split(b"\n")[-2].split(b"/")[4]),2)
            return ping_time
        except Exception as e:
            return False

    def _device_id(self, ip):
        try:
            result = requests.get("http://%s:8080/id" % ip, timeout=5)
            return json.loads(result.text)
        except Exception as e:
            print(e)
        return None

    def _trigger_heartbeat(self, ip):
        try:
            result = requests.get("http://%s:8080/heartbeat" % ip, timeout=5)
            return json.loads(result.text)
        except Exception as e:
            print(e)
        return None



_taskNetworkScanInstance = None
def TaskNetworkScanInstance():
    global _taskNetworkScanInstance
    if _taskNetworkScanInstance is None:
        _taskNetworkScanInstance = Task_NetworkScan()
    return _taskNetworkScanInstance
