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

class Processing(Observable):
    def __init__(self):
        super().__init__()
        self.dns_cache = {}
        self.status = "idle"
        self.rc_tasks = ObservableList()
        self.shots_instance = ShotsInstance()
        self.settings_instance = SettingsInstance()
        self.worker = threading.Thread(target=self._loop, daemon=True)
        self.worker.start()
        self.pre_pause_status = ""

    def _loop(self):
        while True:
            work_done = False
            for host in self.settings_instance.settingsRemoteHosts.hosts:
                self.check_pause()
                self.set_status("idle")
                host = self._resolve_host(host)
                if host is not None:
                    if self._request_remote(host) is True:
                        work_done = True

            self.check_pause()
            self.set_status("idle")
            if self._request_local() is True:
                work_done = True
            if work_done is False:
                time.sleep(60)
            else:
                self.settings_instance.settingsCache.clean()

    def pause(self):
        if self.status != "paused":
            self.pre_pause_status = self.status
            self.set_status("paused")

    def unpause(self):
        self.set_status(self.pre_pause_status)

    def set_status(self, status):
        if self.status != status:
            self.status = status
            self.notify_observers()

    def _resolve_host(self, host):
        if host in self.dns_cache:
            return self.dns_cache[host]
        for _ in range(2):
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
            self.check_pause()
            model.set_status("processing")
            location = self.settings_instance.settingsLocations.get_by_location(model.parentShot.meta_location)
            if location is None:
                model.set_status("failed")
                continue

            rc = RealityCapture(
                parent                 = self,
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
                ground_points          = self._parse_groundpoints_str(location.ground_points),
                pin                    = self.settings_instance.realityCaptureSettings.pin,
                token                  = self.settings_instance.realityCaptureSettings.token,
                license_data           = model.parentShot.license_data,
                box_dimensions         = [location.diameter, location.diameter, location.height],
                calibration_data       = json.loads(location.calibration_data),
                compress_results       = self.settings_instance.realityCaptureSettings.compress_models,
            )
            self.rc_tasks.insert(0, rc)
            while len(self.rc_tasks) > 20:
                del self.rc_tasks[-1]

            while True:
                self.set_status("processing")
                try:
                    rc.process()
                except Exception as e:
                    traceback.print_exc()
                    print("Failed to process", e)
                if rc.result_file is not None or (rc.result_path is not None and rc.compress_results is False):
                    break
                self.set_status("failed")
                while self.status == "failed":
                    time.sleep(2)
                if self.status != "repeat":
                    break

            if (rc.result_file is not None or rc.result_path is not None) and rc.status != "failed":
                location.set_calibration_data(json.dumps(rc.calibrationData.data))
                if rc.result_file is not None:
                    model.write_file(rc.result_file)
                else:
                    model.write_folder(rc.result_path)
                if os.path.exists(os.path.join(rc.workingdir, "tmp", "license.rclicense")):
                    data = open(os.path.join(rc.workingdir, "tmp", "license.rclicense"),"r").read()
                    if len(data) > len(model.parentShot.license_data):
                        model.parentShot.license_data = data
                        model.parentShot.save()
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
            self.check_pause()
            self.set_status("processing")
            self.processing(server_ip, model["shot_id"], model["model_id"])
            rc = RealityCapture(
                parent                 = self,
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
                ground_points          = self._parse_groundpoints_str(data["ground_points"]),
                pin                    = data["pin"],
                token                  = data["token"],
                license_data           = model["license_data"],
                box_dimensions         = data["box_dimensions"],
                calibration_data       = json.loads(data["calibration"]),
                compress_results       = True,
            )
            self.rc_tasks.insert(0, rc)
            while len(self.rc_tasks) > 4:
                del self.rc_tasks[-1]

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

            if rc.result_file is None or rc.status == "failed":
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
            line = line.split("#")[0].lower().strip()
            while "  " in line:
                line = line.replace("  "," ").strip()
            if " - " in line:
                split = " - "
            elif line.count(" ") == 2:
                split = " "
            else:
                continue
            try:
                m1, m2, distance = line.split(split)
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

    def _parse_groundpoints_str(self, groundpoints_str):
        ground_points = []
        for line in sorted(groundpoints_str.split("\n")):
            line = line.split("#")[0].lower().strip()
            while "  " in line:
                line = line.replace("  "," ").strip()
            if line.count(" ") == 3:
                ground_points.append(line.split(" "))
        return ground_points

    def check_pause(self):
        while self.status == "paused":
            time.sleep(2)

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

