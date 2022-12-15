import datetime
import glob
import json
import os
import queue
import random
import subprocess
import threading
import time
import bottle
import gevent
import zipstream
from zipfile import ZIP_STORED

from app_windows.files.shots import ShotsInstance
from app_windows.settings.settings import SettingsInstance

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
            gevent.sleep(sleeptime)
            cnt += 1
        try:
            image = self.results[filename]
            del self.results[filename]
        except:
            image = b''
        yield image


class HttpEndpoints:
    def __init__(self, app, gui):
        self.app = app
        self.gui = gui
        # image_mode = normal | preview, image_type = normal | projection
        bottle.route("/shots/<shot_id>/download/<model_id>")(self._shot_download_model)
        bottle.route("/shots/<shot_id>/download/<model_id>/<filename>")(self._shot_download_model_file)
        bottle.route("/shots/<shot_id>/<image_mode>/<image_type>/<fname>.jpg")(self._shot_get_image)  # return remote shot as jpeg
        bottle.route("/shots/<shot_id>.zip")(self._shot_get_images_zip)
        bottle.route("/modelview.html")(self._modelview_html)
        bottle.route("/model-viewer.min.js")(self._modelview_js)
        bottle.route("/rc_cache/<path:path>")(self.rc_cache)
        bottle.route("/settings_backup")(self._settings_backup)

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
        return bottle.HTTPResponse(json.dumps(SettingsInstance().to_dict()), **headers)

    def rc_cache(self, path):
        filename = path.split("/")[-1]
        path = os.path.realpath(os.path.abspath(os.path.join("c:\\rc_cache", path.replace('/',"\\"))))
        if not os.path.exists(path) or not path.lower().startswith("c:\\rc_cache\\"):
            return bottle.HTTPResponse(status=404)
        headers = {
            'Content-Type': "application/%s" % filename.split(".")[-1],
            'Content-Disposition': 'attachment; filename="%s"' % filename,
            'Cache-Control': "public, max-age=3600"
        }
        with open(path, "rb") as f:
            return bottle.HTTPResponse(f.read(), **headers)

    def _modelview_html(self):
        response = bottle.static_file("modelview.html", root=self.gui.static_dir)
        response.set_header("Content-Type", "text/html")
        response.set_header("Cache-Control", "public, max-age=36000")
        return response

    def _modelview_js(self):
        response = bottle.static_file("js/model-viewer.min.js", root=self.gui.static_dir)
        response.set_header("Content-Type", "application/javascript")
        response.set_header("Cache-Control", "public, max-age=36000")
        return response

    def _shot_download_model(self, shot_id, model_id):
        model = ShotsInstance().get(shot_id).get_model_by_id(model_id)
        if model is None or model.filename == "":
            return bottle.HTTPResponse(status=404)
        mf = model.get_model_file()
        if mf is None:
            return bottle.HTTPResponse(status=404)
        filename, data = mf
        headers = {
            'Content-Type': "application/%s" % filename.split(".")[-1],
            'Content-Disposition': 'attachment; filename="%s"' % filename
        }
        return bottle.HTTPResponse(data, **headers)

    def _shot_download_model_file(self, shot_id, model_id, filename):
        model = ShotsInstance().get(shot_id).get_model_by_id(model_id)
        if model is None or model.filename == "":
            return bottle.HTTPResponse(status=404)
        mf = model.get_model_file(filename)
        if mf is None:
            return bottle.HTTPResponse(status=404)
        filename, data = mf
        headers = {
            'Content-Type': "application/%s" % filename.split(".")[-1],
            'Content-Disposition': 'attachment; filename="%s"' % filename,
            'Cache-Control': "public, max-age=3600"
        }
        return bottle.HTTPResponse(data, **headers)

    # image_mode = normal | preview , image_type = normal | projection
    def _shot_get_image(self, shot_id, image_mode, image_type, fname):
        shot = ShotsInstance().get(shot_id)
        segment = fname.split("-")[0].replace("seg","").strip()
        row = fname.split("-")[1].replace("cam","").strip()

        if shot is None:
            return bottle.HTTPResponse(status=404)
        image = shot.get_image(image_type, image_mode, segment, row)
        if image is None:
            return bottle.HTTPResponse(status=503)
        headers = {
            'Content-Type': "image/jpeg",
            'Cache-Control': "public, max-age=36000"
        }
        return bottle.HTTPResponse(image, **headers)


    def _shot_get_images_zip(self, shot_id):
        shot = self.app.shots.get(shot_id)
        if shot is None:
            return bottle.HTTPResponse(status=404)


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
        return bottle.HTTPResponse(zs, **headers)
