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

from app.files.shots import ShotsInstance
from app_windows.realityCapture.realityCapture import RealityCapture
from app_windows.settings.settings import SettingsInstance

CACHE_DIR = "None"
CACHE_SIZE = 16

SERVER = "127.0.0.1"

class LogItem():
    def __init__(self, log):
        self.log = log

class Processing(Observable):
    def __init__(self):
        super().__init__()
        self.log = ObservableList()

        self._setup()
        self.status = "idle"
        self.rc_tasks = ObservableList()
        rc = RealityCapture(
            source_dir=None,
            source_ip="1.2.3.4",
            shot_id="foobar",
            model_id="foobar",
            shot_name="foobar",
            filetype="gif",
            reconstruction_quality="high",
            export_quality="high",
            create_mesh_from="projection",
            create_textures=True,
            lit=True,
            distances={},
            pin="",
            box_dimensions=[1,2,3],
            calibration_data={},
        )
        self.rc_tasks.append(rc)

        self.current_task = None
        self.processing_tasks = ObservableList()
        self.worker = threading.Thread(target=self.loop, daemon=True)
        self.worker.start()

    def loop(self):
        while True:
            rr = self._request_remote(["127.0.0.1"])
            rl = self._request_local()
            if rr == False and rl == False:
                print("no results, waiting some time ")
                self.log.insert(0, LogItem("no results, waiting some time "))
                time.sleep(3)

    def set_status(self, status):
        if self.status != status:
            self.status = status
            #self.notify_observers()

    def _setup(self):
        if not os.path.exists(CACHE_DIR):
            os.mkdir(CACHE_DIR)
        global SERVER
        while SERVER is None:
            hostname = open("hostname", "r").read().strip()
            print("Resolving %s.local" % hostname)
            try:
                for ip in socket.getaddrinfo("%s.local" % hostname, 80):
                    if ":" in ip[4][0]:
                        continue
                    SERVER = ip[4][0]
            except Exception as e:
                print("Failed to resolve server IP")
            time.sleep(1)

    def _request_local(self):
        models = ShotsInstance().get_unprocessed_models(limit=1)
        if len(models) == 0:
            return False

        self.set_status("processing")
        for model in models:
            shot = model.parentShot
            location = SettingsInstance().locations.get_by_location(shot.location)
            rc = RealityCapture(
                source_dir="TODO",
                source_ip=None,
                shot_id=shot.shot_id,
                model_id=model.model_id,
                shot_name=shot.name,
                filetype=model.filetype,
                reconstruction_quality=model.reconstruction_quality,
                export_quality=model.export_quality,
                create_mesh_from=model.create_mesh_from,
                create_textures=model.create_textures,
                lit=model.lit,
                distances=self._parse_markers_str(location.markers),
                pin=SettingsInstance().realityCaptureSettings.pin,
                box_dimensions=[location.diameter, location.diameter, location.height],
                calibration_data=json.loads(location.calibration_data),
            )
            self.rc_tasks.append(rc)
            self.current_task = rc
            model_result_path = None
            try:
                model_result_path = rc.process()
            except Exception as e:
                traceback.print_exc()
                print(e)
                print("Failed to process", e)
            if model_result_path is not None:
                location.calibration_data = json.dumps(rc.calibrationData.data)
            self.set_status("processing")
        self.current_task = None
        return True

    def _request_remote(self, server_ip):
        self.set_status("requesting_remote")
        data = self.get_unprocessed_models(server_ip)

        if len(data["models"]) == 0:
            self.set_status("idle")
            return False

        for model in data["models"]:
            self.processing(server_ip, model["shot_id"], model["model_id"])
            self._clean_shot_dir()
            self.set_status("download")
            rc = RealityCapture(
                source_dir=None,
                source_ip=server_ip,
                shot_id=model["shot_id"],
                model_id=model["model_id"],
                shot_name=model["shot_name"],
                filetype=model["filetype"],
                reconstruction_quality=model["reconstruction_quality"],
                export_quality=model["quality"],
                create_mesh_from=model["create_mesh_from"],
                create_textures=model["create_textures"],
                lit=model["lit"],
                distances= self._parse_markers_str(data["markers"]),
                pin=data["pin"],
                box_dimensions=data["box_dimensions"],
                calibration_data=json.loads(data["calibration"]),
            )
            self.rc_tasks.append(rc)
            self.current_task = rc
            self.set_status("processing")
            model_result_path = None
            try:
                model_result_path = rc.process()
            except Exception as e:
                traceback.print_exc()
                print(e)
                print("Failed to process", e)

            if model_result_path is not None:
                self.upload_calibration_data(rc.calibrationData.data)
                try:
                    SettingsInstance().locations.get_by_location(shot.location).calibration_data = json.dumps(rc.calibrationData.data)
                except Exception as e:
                    print(e)
                self.upload_model(model["shot_id"], model["model_id"], model_result_path)
                os.remove(model_result_path)
            else:
                self.process_failed(model["shot_id"], model["model_id"])
                if os.path.exists(shot_path):
                    print("Not caching shot %s" % shot_path)
                    try:
                        shutil.rmtree(shot_path)
                    except:
                        print("Failed to delete %s" % shot_path)
        self.current_task = None
        self.set_status("idle")
        return True

    def _clean_shot_dir(self):
        shots = []
        for path in glob.glob(os.path.join(CACHE_DIR, "*")):
            shots.append(path)

        for index, path in enumerate(shots):
            with open(os.path.join(path, "last_usage"), "r") as f:
                shots[index] = [int(f.read()), path]

        shots.sort()
        while len(shots) > CACHE_SIZE:
            shutil.rmtree(shots[0][1])
            del shots[0]

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
        print("Checking Server for work")
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

