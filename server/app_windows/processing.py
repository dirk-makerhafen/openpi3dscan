import glob
import json
import os
import shutil
import threading
import time
import traceback
import socket
import requests
from pyhtmlgui import Observable, ObservableList

from app_windows.files.shots import ShotsInstance
from app_windows.realityCapture.realityCapture import RealityCapture
from app_windows.settings.settings import SettingsInstance

class LogItem(Observable):
    def __init__(self, value):
        super().__init__()
        self.value = value
class Log(ObservableList):
    def append(self, value):
        value = LogItem(value)
        super().append(value)

class Processing(Observable):
    def __init__(self):
        super().__init__()
        self.log = Log()
        self.dns_cache = {}
        self.status = "idle"
        self.rc_tasks = ObservableList()
        self.shots_instance = ShotsInstance()
        self.settings_instance = SettingsInstance()
        self.worker = threading.Thread(target=self._loop, daemon=True)
        self.worker.start()

    def _loop(self):
        while True:
            work_done = False

            for host in self.settings_instance.settingsRemoteHosts.hosts:
                host = self._resolve_host(host)
                if host is not None:
                    if self._request_remote(host) is True:
                        work_done = True

            if self._request_local() is True:
                work_done = True

            if work_done is False:
                print("no results, waiting some time ")
                self.log.append("no results, waiting some time ")
            else:
                self.settings_instance.settingsCache.clean()
            time.sleep(5)

    def set_status(self, status):
        if self.status != status:
            self.status = status
            self.notify_observers()

    def _resolve_host(self, host):
        if host in self.dns_cache:
            return self.dns_cache[host]
        for _ in range(10):
            try:
                for ip in socket.getaddrinfo(host, 80):
                    if ":" in ip[4][0]:
                        continue
                    self.dns_cache[host] = ip[4][0]
                    return self.dns_cache[host]
            except Exception as e:
                print("Failed to resolve server IP")
            time.sleep(1)
        return None

    def _request_local(self):
        models = self.shots_instance.get_unprocessed_models(limit=1)
        if len(models) == 0:
            return False

        self.set_status("processing")

        for model in models:
            model.set_status("processing")
            location = self.settings_instance.settingsLocations.get_by_location(model.parentShot.meta_location)
            if location is None:
                model.set_status("failed")
                continue

            rc = RealityCapture(
                source_dir             = model.parentShot.path,
                source_ip              = None,
                shot_id                = model.parentShot.shot_id,
                model_id               = model.model_id,
                shot_name              = model.parentShot.name,
                filetype               = model.filetype,
                reconstruction_quality = model.reconstruction_quality,
                export_quality         = model.quality,
                create_mesh_from       = model.create_mesh_from,
                create_textures        = model.create_textures,
                lit                    = model.lit,
                distances              = self._parse_markers_str(location.markers),
                pin                    = self.settings_instance.realityCaptureSettings.pin,
                token                  = self.settings_instance.realityCaptureSettings.token,
                box_dimensions         = [location.diameter, location.diameter, location.height],
                calibration_data       = json.loads(location.calibration_data),
            )
            self.rc_tasks.insert(0, rc)
            while True:
                self.set_status("processing")
                try:
                    rc.process()
                except Exception as e:
                    traceback.print_exc()
                    print("Failed to process", e)
                if rc.result_file is not None:
                    break
                self.set_status("failed")
                while self.status == "failed":
                    time.sleep(2)
                if self.status != "repeat":
                    break

            if rc.result_file is not None:
                location.set_calibration_data(json.dumps(rc.calibrationData.data))
                model.write_file(rc.result_file)
            else:
                model.set_status("failed")

        self.set_status("idle")
        return True

    def _request_remote(self, server_ip):
        data = self.get_unprocessed_models(server_ip)
        if len(data["models"]) == 0:
            return False

        self.set_status("processing")

        for model in data["models"]:
            self.processing(server_ip, model["shot_id"], model["model_id"])
            rc = RealityCapture(
                source_dir             = None,
                source_ip              = server_ip,
                shot_id                = model["shot_id"],
                model_id               = model["model_id"],
                shot_name              = model["shot_name"],
                filetype               = model["filetype"],
                reconstruction_quality = model["reconstruction_quality"],
                export_quality         = model["quality"],
                create_mesh_from       = model["create_mesh_from"],
                create_textures        = model["create_textures"],
                lit                    = model["lit"],
                distances              = self._parse_markers_str(data["markers"]),
                pin                    = data["pin"],
                token                  = data["token"],
                box_dimensions         = data["box_dimensions"],
                calibration_data       = json.loads(data["calibration"]),
            )
            self.rc_tasks.insert(0, rc)

            while True:
                self.set_status("processing")
                try:
                    rc.process()
                except Exception as e:
                    traceback.print_exc()
                    print("Failed to process", e)
                if rc.result_file is not None:
                    break
                self.set_status("failed")
                while self.status == "failed":
                    time.sleep(2)
                if self.status != "repeat":
                    break

            if rc.result_file is None:
                self.process_failed(server_ip, model["shot_id"], model["model_id"])
            else:
                if "shot_location" in model:
                    location = self.settings_instance.settingsLocations.get_by_location(model["shot_location"])
                    if location is not None:
                        location.set_calibration_data(json.dumps(rc.calibrationData.data))

        self.set_status("idle")
        return True


    def _parse_markers_str(self, markers_str):
        distances = {}
        for line in sorted(markers_str.split("\n")):
            line = line.split("#")[0].strip()
            if " - " not in line:
                continue
            try:
                m1, m2, distance = line.split(" - ")
                m1 = m1.strip()
                m2 = m2.strip()
                distance = float(distance.strip())
                if m1 not in distances:
                    distances[m1] = {}
                if m2 not in distances:
                    distances[m2] = {}
                distances[m1][m2] = distance
                distances[m2][m1] = distance
            except:
                pass
        print("%s distances loaded from server" % len(distances))
        return distances

    def get_unprocessed_models(self, server_ip):
        data = {}
        try:
            d = requests.get("http://%s/realityCaptureProcess" % server_ip).text
            data = json.loads(d)
        except Exception as e:
            print(e)
            data["models"] = []
        if len(data["models"]) > 0:
            print("%s unprocessed models received from server" % len(data["models"]))
        return data

    def processing(self, server_ip, shot_id, model_id):
        try:
            requests.get("http://%s/shots/%s/processing/%s" % (server_ip, shot_id, model_id))
        except:
            print("failed to reach server %s", server_ip)

    def process_failed(self, server_ip, shot_id, model_id):
        print("Failed to process %s  Model %s" % (shot_id, model_id))
        for i in range(10):
            try:
                requests.get("http://%s/shots/%s/processing_failed/%s" % (server_ip, shot_id, model_id))
                return
            except:
                print("failed to reach server")
                time.sleep(10)

