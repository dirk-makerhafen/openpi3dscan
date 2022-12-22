import datetime
import json
import os
import queue
import random
import threading
import time
import zipstream
from zipfile import ZIP_STORED

from app_windows.files.shots import ShotsInstance
from app_windows.settings.settings import SettingsInstance

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
            image = self.results[filename]
            del self.results[filename]
        except:
            image = b''
        yield image


class HttpEndpoints:
    def __init__(self, app, gui):
        self.app = app
        self.gui = gui
        self.flaskApp = flask.current_app
        # image_mode = normal | preview, image_type = normal | projection
        self.flaskApp.route("/shots/<shot_id>/download/<model_id>")(self._shot_download_model)
        self.flaskApp.route("/shots/<shot_id>/download/<model_id>/<filename>")(self._shot_download_model_file)
        self.flaskApp.route("/shots/<shot_id>/<image_mode>/<image_type>/<fname>.jpg")(self._shot_get_image)  # return remote shot as jpeg
        self.flaskApp.route("/shots/<shot_id>.zip")(self._shot_get_images_zip)
        self.flaskApp.route("/modelview.html")(self._modelview_html)
        self.flaskApp.route("/model-viewer.min.js")(self._modelview_js)
        self.flaskApp.route("/rc_cache/<path:path>")(self.rc_cache)
        self.flaskApp.route("/settings_backup")(self._settings_backup)

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

    def rc_cache(self, path):
        filename = path.split("/")[-1]
        path = os.path.realpath(os.path.abspath(os.path.join("c:\\rc_cache", path.replace('/',"\\"))))
        if not os.path.exists(path) or not path.lower().startswith("c:\\rc_cache\\"):
            return flask.abort(404)
        headers = {
            'Content-Type': "application/%s" % filename.split(".")[-1],
            'Content-Disposition': 'attachment; filename="%s"' % filename,
            'Cache-Control': "public, max-age=3600"
        }
        with open(path, "rb") as f:
            return flask.Response(f.read(), headers=headers)

    def _modelview_html(self):
        response = flask.helpers.send_from_directory(self.gui.static_dir, "modelview.html")
        response.headers["Content-Type"] = "text/html"
        response.headers["Cache-Control"] = "public, max-age=36000"
        return response

    def _modelview_js(self):
        response = flask.helpers.send_from_directory(self.gui.static_dir, "js/model-viewer.min.js")
        response.headers["Content-Type"] = "application/javascript"
        response.headers["Cache-Control"] = "public, max-age=36000"
        return response

    def _shot_download_model(self, shot_id, model_id):
        model = ShotsInstance().get(shot_id).get_model_by_id(model_id)
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

    def _shot_download_model_file(self, shot_id, model_id, filename):
        model = ShotsInstance().get(shot_id).get_model_by_id(model_id)
        if model is None or model.filename == "":
            return flask.abort(404)
        mf = model.get_model_file(filename)
        if mf is None:
            return flask.abort(404)
        filename, data = mf
        headers = {
            'Content-Type': "application/%s" % filename.split(".")[-1],
            'Content-Disposition': 'attachment; filename="%s"' % filename,
            'Cache-Control': "public, max-age=3600"
        }
        return flask.Response(data, headers=headers)

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
