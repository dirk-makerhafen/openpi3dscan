import glob
import json
import os
import shutil
import socket
import threading
import time
import traceback

import requests
from pyhtmlgui import Observable, ObservableList


class WebAPI():
    def download_shot(self, shot_id):
        if os.path.exists(os.path.join(CACHE_DIR, shot_id, "images")):
            print("shot '%s' was already downloaded" % shot_id)
        else:
            print("Download shot id %s" % shot_id)
            try:
                data = requests.get("http://%s/shots/%s.zip" % (SERVER, shot_id)).content
                with open(os.path.join(CACHE_DIR, "%s.zip" % shot_id), "wb") as f:
                    f.write(data)
            except Exception as e:
                print("failed to download shot '%s'" % shot_id)
                return None
            self._unpack_zip(os.path.join(CACHE_DIR, "%s.zip" % shot_id))
        return os.path.join(CACHE_DIR, shot_id)

    def get_unprocessed_models(self):
        print("Checking Server for work")
        data = {}
        try:
            d = requests.get("http://%s/realityCaptureProcess" % SERVER).text
            data = json.loads(d)
        except Exception as e:
            print(e)
            data["models"] = []
        if len(data["models"]) > 0:
            print("%s unprocessed models received from server" % len(data["models"]))
        return data

    def processing(self, shot_id, model_id):
        try:
            requests.get("http://%s/shots/%s/processing/%s" % (SERVER, shot_id, model_id))
        except:
            print("failed to reach server")

    def upload_model(self, shot_id, model_id, model_path):
        with open(model_path, 'rb') as f:
            print("Uploading model: %s" % model_path)
            try:
                requests.post("http://%s/shots/%s/upload/%s" % (SERVER, shot_id, model_id), files={'upload_file': f})
                print("Upload finished")
            except:
                print("failed to reach server while uploading")
                self.process_failed(shot_id, model_id)

    def upload_calibration_data(self):
        print("Uploading calibration")
        try:
            requests.post("http://%s/upload_calibration" % (SERVER), json={"data": json.dumps(calibrationData.data)})
            print("Upload finished")
        except:
            print("failed to reach server while uploading")

    def process_failed(self, shot_id, model_id):
        print("Failed to process %s  Model %s" % (shot_id, model_id))
        for i in range(10):
            try:
                requests.get("http://%s/shots/%s/processing_failed/%s" % (SERVER, shot_id, model_id))
                return
            except:
                print("failed to reach server")
                time.sleep(10)

    def _unpack_zip(self, path):
        path = os.path.abspath(path)
        name = path.split("\\")[-1].split(".zip")[0]
        dir = "\\".join(path.split("\\")[0:-1])
        target_dir = os.path.join(dir, name)
        print("Unpack %s" % path)
        if os.path.exists(target_dir):
            try:
                shutil.rmtree(target_dir)
            except:
                print("Failed to delete %s" % target_dir)
        os.system("cd \"%s\" & powershell -command \"Expand-Archive '%s.zip'\"" % (dir, name))
        os.remove(path)
        if not os.path.exists(os.path.join(target_dir, "images")):
            os.mkdir(os.path.join(target_dir, "images"))
        shutil.move(os.path.join(target_dir, "normal"), os.path.join(target_dir, "images"))
        shutil.move(os.path.join(target_dir, "projection"), os.path.join(target_dir, "images"))
        if os.path.exists(os.path.join(target_dir, "normal")):
            shutil.rmtree(os.path.join(target_dir, "normal"))
        if os.path.exists(os.path.join(target_dir, "projection")):
            shutil.rmtree(os.path.join(target_dir, "projection"))



class Processing(Observable):
    def __init__(self):
        super().__init__()
        self._setup()
        self.status = "idle"
        self.processing_tasks = ObservableList()
        self.worker = threading.Thread(target=self.loop, daemon=True)
        self.worker.start()

    def loop(self):
        while True:
            rr = self._request_remote()
            rl = self._request_local()
            if rr == False and rl == False:
                print("no results, waiting some time ")
                self.set_status("waiting")
                time.sleep(30)


    def set_status(self, status):
        if self.status != status:
            self.status = status
            self.notify_observers()

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
        self.set_status("requesting_local")
        models = ShotsInstance().get_unprocessed_models(limit=1)
        if len(models) == 0:
            self.set_status("idle")
            return False
        for model in models:
            shot = model.parentShot
            location = SettingsInstance().locations.get_by_location(shot.location)
            calibrationData = json.loads(location.calibration_data)
            markers, distances = self._parse_markers_str(location.markers)

            rc = RealityCapture(
                source_folder="TODO",
                shot_name=shot.name,
                filetype=model.filetype,
                reconstruction_quality=model.reconstruction_quality,
                quality=model.export_quality,
                create_mesh_from=model.create_mesh_from,
                create_textures=model.create_textures,
                calibrationData=calibrationData,
                markers=markers,
                distances=distances,
                pin=SettingsInstance().realityCaptureSettings.pin,
                box_dimensions= [location.diameter, location.diameter, location.height]
            )
            self.set_status("processing")
            self.processing_tasks.insert(0, rc )
            model_result_path = None
            try:
                model_result_path = rc.process()
            except Exception as e:
                traceback.print_exc()
                print(e)
                print("Failed to process", e)
        self.set_status("idle")
        return True

    def _request_remote(self):
        self.set_status("requesting_remote")
        api = WebAPI()
        data = api.get_unprocessed_models()

        if len(data["models"]) == 0:
            self.set_status("idle")
            return False

        calibrationData = json.loads(data["calibration"])
        markers, distances = self._parse_markers_str(data["markers"])

        for model in data["models"]:
            api.processing(model["shot_id"], model["model_id"])
            self._clean_shot_dir()
            self.set_status("download")
            shot_path = api.download_shot(model["shot_id"])
            if shot_path is None:
                api.process_failed(model["shot_id"], model["model_id"])
                continue
            rc = RealityCapture(
                source_folder=shot_path,
                shot_name=model["shot_name"],
                filetype=model["filetype"],
                reconstruction_quality=model["reconstruction_quality"],
                quality=model["quality"],
                create_mesh_from=model["create_mesh_from"],
                create_textures=model["create_textures"],
                calibrationData=calibrationData,
                markers=markers,
                distances=distances,
                pin=data["pin"],
                box_dimensions=data["box_dimensions"]
            )
            self.set_status("processing")
            self.processing_tasks.insert(0, rc)
            model_result_path = None
            try:
                model_result_path = rc.process()
            except Exception as e:
                traceback.print_exc()
                print(e)
                print("Failed to process", e)

            if model_result_path is not None:
                api.upload_calibration_data()
                api.upload_model(model["shot_id"], model["model_id"], model_result_path)
                if self.parent.debug is False:
                    os.remove(model_result_path)
            else:
                api.process_failed(model["shot_id"], model["model_id"])
                if self.parent.debug is False and os.path.exists(shot_path):
                    print("Not caching shot %s" % shot_path)
                    try:
                        shutil.rmtree(shot_path)
                    except:
                        print("Failed to delete %s" % shot_path)
        self.set_status("idle")
        return True


    def _clean_shot_dir(self):
        shots = []
        for path in glob.glob(os.path.join(CACHE_DIR, "*")):
            shots.append(path)
        shots.sort()
        while len(shots) > CACHE_SIZE:
            shutil.rmtree(shots[0])
            del shots[0]

    def _parse_markers_str(self, markers_str):
        markers = []
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
                markers.append(m1)
                markers.append(m2)
                if m1 not in distances:
                    distances[m1] = {}
                if m2 not in distances:
                    distances[m2] = {}
                distances[m1][m2] = distance
                distances[m2][m1] = distance
            except:
                pass
        markers = list(set(markers))
        print("%s Markers loaded from server" % len(markers))
        return markers, distances
