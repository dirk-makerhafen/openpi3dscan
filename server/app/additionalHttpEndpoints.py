import glob
import json
import os
import queue
import random
import subprocess
import threading
import time
import zipfile
from zipfile import ZIP_STORED

import bottle
import gevent
import zipstream
from bottle import request

from app.devices.devices import DevicesInstance
from app.settings.settings import SettingsInstance
from app.shots import ShotsInstance
from views.imageCarousel.imageCarouselLive import PreviewQueueInstance

bottle.BaseRequest.MEMFILE_MAX = 800 * 1024 * 1024


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
            filename, shot_id, image_type, device_id = data
            image = ShotsInstance().get(shot_id).get_image(image_type, "normal", device_id)
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
            gevent.sleep(sleeptime)
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
        bottle.route("/shots/list")(self._shot_list)
        bottle.route("/shots/<shot_id>/processing_failed/<model_id>")(self._shot_processing_failed)
        bottle.route("/shots/<shot_id>/upload/<model_id>", method="POST")(self._shot_upload_model)
        bottle.route("/shots/<shot_id>/download/<model_id>")(self._shot_download_model)
        bottle.route("/shots/<shot_id>/download/<model_id>/<filename>")(self._shot_download_model_file)
        bottle.route("/shots/<shot_id>/<image_mode>/<image_type>/<device_id>.jpg")(self._shot_get_image)  # return remote shot as jpeg
        bottle.route("/shots/<shot_id>.zip")(self._shot_get_images_zip)
        bottle.route("/live/<device_id>.jpg")(self._live)
        bottle.route("/heartbeat", method="POST")(self._heartbeat)
        bottle.route("/windows_pack.zip")(self.download_windows_pack)
        bottle.route("/force_update")(self.force_update)
        bottle.route("/realityCaptureProcess")(self.realityCaptureProcess)

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
            data["models"].append(model)
        if len(data["models"]) > 0:
            data["markers"] = SettingsInstance().realityCaptureSettings.markers
            dia = SettingsInstance().realityCaptureSettings.diameter
            data["box_dimensions"] = [dia, dia, SettingsInstance().realityCaptureSettings.height]
        return json.dumps(data)

    def _shot_list(self):
        return json.dumps([shot.shot_id for shot in ShotsInstance().shots])

    def _shot_download_model(self, shot_id, model_id):
        model = ShotsInstance().get(shot_id).get_model_by_id(model_id)
        if model is None or model.filename == "":
            return bottle.HTTPResponse(status=404)
        headers = {
            'Content-Type': "application/zip",
            'Content-Disposition': 'attachment; filename="%s"' % model.filename
        }
        return bottle.HTTPResponse(open(model.get_path(), "rb"), **headers)

    def _shot_download_model_file(self, shot_id, model_id, filename):
        model = ShotsInstance().get(shot_id).get_model_by_id(model_id)
        if model is None or model.filename == "":
            return bottle.HTTPResponse(status=404)
        headers = {
            'Content-Type': "application/%s" % filename.split(".")[-1],
            'Content-Disposition': 'attachment; filename="%s"' % model.filename,
            'Cache-Control': "public, max-age=3600"
        }
        with zipfile.ZipFile(model.get_path(), 'r') as zip_ref:
            return bottle.HTTPResponse(zip_ref.read(filename), **headers)

    def _shot_processing_failed(self, shot_id, model_id):
        ShotsInstance().get(shot_id).get_model_by_id(model_id).set_status("failed")

    def _shot_upload_model(self, shot_id, model_id):
        file = request.files.get('upload_file').file
        ShotsInstance().get(shot_id).get_model_by_id(model_id).write_file(file)

    # image_mode = normal | preview , image_type = normal | projection
    def _shot_get_image(self, shot_id, image_mode, image_type, device_id):
        shot = ShotsInstance().get(shot_id)
        if shot is None:
            return bottle.HTTPResponse(status=404)
        image = shot.get_image(image_type, image_mode, device_id)
        if image is None:
            return bottle.HTTPResponse(status=503)
        headers = {
            'Content-Type': "image/jpeg",
            'Cache-Control': "public, max-age=36000"
        }
        return bottle.HTTPResponse(image, **headers)

    def download_windows_pack(self):
        files = glob.glob("/opt/openpi3dscan/realityCapture/*.*")
        zs = zipstream.ZipStream(compress_type=ZIP_STORED)
        for file in files:
            name = file.split("/")[-1]
            zs.add_path(file, "windows_scripts/%s" % name)
        zs.add_path("/etc/hostname", "windows_scripts/hostname")
        headers = {
            'Content-Type': "application/zip",
            'Content-Disposition': 'attachment; filename="windows_scripts.zip"'
        }
        return bottle.HTTPResponse(zs, **headers)

    def _shot_get_images_zip(self, shot_id):
        shot = self.app.shots_remote.get(shot_id)
        if shot is None:
            return bottle.HTTPResponse(status=404)

        filelist = []
        for i in range(101, 213):
            device_id = "%s" % i
            if shot.image_may_exist("normal", "normal", device_id):  # image_mode = normal | preview , image_type = normal | projection
                filelist.append(["normal/%s.jpg" % device_id, shot_id, "normal", device_id])
            if shot.image_may_exist("projection", "normal", device_id):
                filelist.append(["projection/%s.jpg" % device_id, shot_id, "projection", device_id])

        random.shuffle(filelist)

        ds = DownloadStreamer(filelist)
        zs = zipstream.ZipStream(compress_type=ZIP_STORED)
        for f in filelist:
            zs.add(ds.get(f[0]), f[0])

        headers = {
            'Content-Type': "application/zip",
            'Content-Disposition': 'attachment; filename="%s.zip"' % shot.get_clean_shotname()
        }
        return bottle.HTTPResponse(zs, **headers)

    def _heartbeat(self):
        ip = request.environ.get('REMOTE_ADDR')
        data = request.json
        DevicesInstance().heartbeat_received(ip, data)
        return "OK"

    def _live(self, device_id):
        headers = {
            'Content-Type': "image/jpeg",
            'Cache-Control': "public, max-age=0"
        }
        response = bottle.HTTPResponse(PreviewQueueInstance().get_image(device_id), **headers)
        return response

    def force_update(self):
        output = "Update and system reboot triggered, this will take 2-3 minutes!\n\n"
        output += "UPDATE LOG:\n"
        if os.path.exists("/home/pi/openpi3dscan"):
            output += subprocess.check_output("cd /home/pi/openpi3dscan ; sudo git reset --hard ; sudo git clean -f -d ; sudo git pull", shell=True,stderr=subprocess.STDOUT).decode("utf-8")
        else:
            output += subprocess.check_output("cd /home/pi/ ; git clone 'https://github.com/dirk-makerhafen/openpi3dscan.git'", shell=True, stderr=subprocess.STDOUT).decode("utf-8")
        output += "\n"
        output += subprocess.check_output("cd /home/pi/openpi3dscan/server ; sudo python3 install.py", shell=True, stderr=subprocess.STDOUT).decode("utf-8")
        def f():
            time.sleep(5)
            os.system("sudo reboot &")
        threading.Thread(target=f, daemon=True).run()
        headers = {
            'Content-Type': "text/plain ; charset=UTF-8",
            'Cache-Control': "public, max-age=0"
        }
        return bottle.HTTPResponse(output, **headers)
