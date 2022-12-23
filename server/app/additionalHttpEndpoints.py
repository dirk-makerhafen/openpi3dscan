import datetime
import json
import os
import queue
import random
import subprocess
import threading
import time
from zipfile import ZIP_STORED
import zipstream

from app.devices.devices import DevicesInstance
from app.settings.settings import SettingsInstance
from app.files.shots import ShotsInstance
from views.images.imagesLiveView import PreviewQueueInstance
import flask

class DownloadStreamer:
    def __init__(self, data):
        self.data_queue = queue.Queue()
        for d in data:
            self.data_queue.put(d)
        self.results = {}
        self.last_request = time.time()
        for i in range(5):
            t = threading.Thread(target=self._worker_thread, daemon=True)
            t.start()
            time.sleep(0.15)

    def _worker_thread(self):
        while True:
            while len(self.results.keys()) > 5 and self.last_request + 120 > time.time():  # 120 second timeout
                time.sleep(1)
            if self.last_request + 120 < time.time():
                break
            try:
                data = self.data_queue.get(timeout=1)
            except Exception:
                break

            filename, shot_id, image_type, segment, row = data
            image = ShotsInstance().get(shot_id).get_image(image_type, "normal", segment, row)
            if image is None:
                self.results[filename] = b''
            else:
                self.results[filename] = image
            self.data_queue.task_done()

    def get(self, filename):
        self.last_request = time.time()
        cnt = 0
        timeout_seconds = 90
        sleeptime = 0.3
        while filename not in self.results and cnt < (timeout_seconds/sleeptime):
            time.sleep(sleeptime)
            cnt += 1
        try:
            item = self.results[filename]
            del self.results[filename]
        except:
            item = b''
        yield item


class HttpEndpoints:
    def __init__(self, app, gui):
        self.app = app
        self.gui = gui
        # image_mode = normal | preview, image_type = normal | projection
        self.flaskApp = flask.current_app
        self.flaskApp.route("/shots/list")(self._shot_list)
        self.flaskApp.route("/shots/<shot_id>/processing/<model_id>")(self._shot_processing)
        self.flaskApp.route("/shots/<shot_id>/processing_failed/<model_id>")(self._shot_processing_failed)
        self.flaskApp.route("/shots/<shot_id>/upload/<model_id>", methods=["POST"])(self._shot_upload_model)
        self.flaskApp.route("/shots/<shot_id>/upload_license", methods=["POST"])(self._shot_upload_license)
        self.flaskApp.route("/shots/<shot_id>/download/<model_id>")(self._shot_download_model)
        self.flaskApp.route("/shots/<shot_id>/download/<model_id>/<filename>")(self._shot_download_model_file)
        self.flaskApp.route("/shots/<shot_id>/<image_mode>/<image_type>/<fname>.jpg")(self._shot_get_image)  # return remote shot as jpeg
        self.flaskApp.route("/shots/<shot_id>.zip")(self._shot_get_images_zip)
        self.flaskApp.route("/live/<device_id>.jpg")(self._live)
        self.flaskApp.route("/heartbeat", methods=["POST"])(self._heartbeat)
        self.flaskApp.route("/force_update")(self.force_update)
        self.flaskApp.route("/realityCaptureProcess")(self.realityCaptureProcess)
        self.flaskApp.route("/upload_calibration", methods=["POST"])(self.upload_calibration)
        self.flaskApp.route("/settings_backup")(self._settings_backup)

    def realityCaptureProcess(self):
        data = {
            "models" : [],
            "markers" : "",
        }
        for model in ShotsInstance().get_unprocessed_models(limit=1):
            shot = model.parentShot
            model = model.to_dict()
            model["shot_id"] = shot.shot_id
            model["shot_name"] = shot.name
            model["shot_location"] = shot.meta_location
            model["license_data"] = shot.license_data
            data["models"].append(model)
        if len(data["models"]) > 0:
            data["markers"] = SettingsInstance().realityCaptureSettings.markers
            data["ground_points"] = SettingsInstance().realityCaptureSettings.ground_points
            dia = SettingsInstance().realityCaptureSettings.diameter
            data["box_dimensions"] = [dia, dia, SettingsInstance().realityCaptureSettings.height]
            data["pin"] = SettingsInstance().realityCaptureSettings.pin
            data["token"] = SettingsInstance().realityCaptureSettings.token
            data["calibration"] = SettingsInstance().realityCaptureSettings.calibration_data
        return json.dumps(data)

    def _shot_list(self):
        return json.dumps([shot.shot_id for shot in ShotsInstance().shots])

    def _shot_download_model(self, shot_id, model_id):
        model = ShotsInstance().get(shot_id).models.get_by_id(model_id)
        if model is None or model.filename == "":
            return flask.abort(404)
        mf = model.get_model_file()
        if mf is None:
            return flask.abort(404)
        filename, data = mf
        headers = {
            'Content-Type': "application/%s" % filename.split(".")[-1],
            'Content-Disposition': 'attachment; filename="%s"' % filename
        }
        return flask.Response(data, headers=headers)

    def _settings_backup(self):
        fname = "Backup-Settings"
        if SettingsInstance().settingsScanner.location != "":
            fname = "%s-%s" % (fname, SettingsInstance().settingsScanner.location)
        now = datetime.datetime.now()
        fname = "%s-%s.%s.%s %s%s.json" % (fname, now.year, ("%s" % now.month).zfill(2), ("%s" % now.day).zfill(2), ("%s" % now.hour).zfill(2), ("%s" % now.minute).zfill(2))
        headers = {
            'Content-Type': "application/json",
            'Content-Disposition': 'attachment; filename="%s"' % fname
        }
        return flask.Response(json.dumps(SettingsInstance().to_dict()), headers=headers)

    def _shot_download_model_file(self, shot_id, model_id, filename):
        model = ShotsInstance().get(shot_id).models.get_by_id(model_id)
        if model is None or model.filename == "":
            print("no model")
            return flask.abort(404)
        mf = model.get_model_file(filename)
        if mf is None:
            print("no model file")
            return flask.abort(404)
        filename, data = mf
        headers = {
            'Content-Type': "application/%s" % filename.split(".")[-1],
            'Content-Disposition': 'attachment; filename="%s"' % filename,
            'Cache-Control': "public, max-age=3600"
        }
        return flask.Response(data, headers=headers)

    def _shot_processing_failed(self, shot_id, model_id):
        ShotsInstance().get(shot_id).models.get_by_id(model_id).set_status("failed")

    def _shot_processing(self, shot_id, model_id):
        ShotsInstance().get(shot_id).models.get_by_id(model_id).set_status("processing")

    def _shot_upload_model(self, shot_id, model_id):
        file = flask.request.files['file']
        ShotsInstance().get(shot_id).models.get_by_id(model_id).write_file(file)

    def _shot_upload_license(self, shot_id):
        shot = ShotsInstance().get(shot_id)
        if shot is not None and len(shot.license_data) < len(flask.request.json["data"]):
            shot.license_data = flask.request.json["data"]
            shot.save()

    # image_mode = normal | preview , image_type = normal | projection
    def _shot_get_image(self, shot_id, image_mode, image_type, fname):
        shot = ShotsInstance().get(shot_id)
        segment = fname.split("-")[0].replace("seg","").strip()
        row = fname.split("-")[1].replace("cam","").strip()

        if shot is None:
            return flask.abort(404)
        image = shot.get_image(image_type, image_mode, segment, row)
        if image is None:
            return flask.abort(503)
        headers = {
            'Content-Type': "image/jpeg",
            'Cache-Control': "public, max-age=36000"
        }
        return flask.Response(image, headers=headers)

    def _shot_get_images_zip(self, shot_id):
        shot = self.app.shots.get(shot_id)
        if shot is None:
            return flask.abort(404)


        filelist = []
        for _image_type in ["normal", "projection"]:
            for file in shot.list_possible_images(_image_type, "normal"):
                image_type, image_mode, segment, row = file
                filelist.append(["%s/seg%s-cam%s-%s.jpg" % (image_type, segment, row, image_type[0]), shot_id, image_type, segment, row])
        random.shuffle(filelist)

        ds = DownloadStreamer(filelist)
        zs = zipstream.ZipStream(compress_type=ZIP_STORED)
        for f in filelist:
            zs.add(ds.get(f[0]), f[0])

        zs.add(json.dumps({
            "name": shot.name,
            "comment": shot.comment,
            "meta_location": shot.meta_location,
            "meta_max_rows": shot.meta_max_rows,
            "meta_max_segments": shot.meta_max_segments,
            "meta_rotation": shot.meta_rotation,
            "meta_camera_one_position": shot.meta_camera_one_position,
        }), "metadata.json")

        headers = {
            'Content-Type': "application/zip",
            'Content-Disposition': 'attachment; filename="%s.zip"' % shot.get_clean_shotname()
        }
        return flask.Response(zs, headers=headers)

    def _heartbeat(self):
        ip = flask.request.remote_addr
        DevicesInstance().heartbeat_received(ip, flask.request.json)
        return "OK"

    def upload_calibration(self):
        data = flask.request.json["data"]
        try:
            if len(json.loads(data)) < 50:# broken data?
                print("rejecting data")
                return
        except Exception as e:
            print("Failed to load calibration data", e)
            return "Failed"

        SettingsInstance().realityCaptureSettings.set_calibration_data(data)
        return "OK"

    def _live(self, device_id):
        headers = {
            'Content-Type': "image/jpeg",
            'Cache-Control': "public, max-age=0"
        }
        response = flask.Response(PreviewQueueInstance().get_image(device_id), headers=headers)
        return response

    def force_update(self):
        app_dir_name = "server"
        if os.path.exists("/home/pi/openpi3dscan/apps"):
            app_dir_name = "apps"

        output = "Update and system reboot triggered, this will take 2-3 minutes!\n\n"
        output += "UPDATE LOG:\n"
        if os.path.exists("/home/pi/openpi3dscan"):
            output += subprocess.check_output("cd /home/pi/openpi3dscan ; sudo git reset --hard ; sudo git clean -f -d ; sudo git pull", shell=True,stderr=subprocess.STDOUT).decode("utf-8")
        else:
            output += subprocess.check_output("cd /home/pi/ ; git clone 'https://github.com/dirk-makerhafen/openpi3dscan.git'", shell=True, stderr=subprocess.STDOUT).decode("utf-8")
        output += "\n"
        output += subprocess.check_output("cd /home/pi/openpi3dscan/%s ; sudo python3 run.py install" % app_dir_name, shell=True, stderr=subprocess.STDOUT).decode("utf-8")
        def f():
            time.sleep(5)
            os.system("sudo reboot &")
        threading.Thread(target=f, daemon=True).run()
        headers = {
            'Content-Type': "text/plain ; charset=UTF-8",
            'Cache-Control': "public, max-age=0"
        }
        return flask.Response(output, headers=headers)
