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

from app.files.shots import ShotsInstance

bottle.BaseRequest.MEMFILE_MAX = 800 * 1024 * 1024


class HttpEndpoints:
    def __init__(self, app, gui):
        self.app = app
        self.gui = gui
        # image_mode = normal | preview, image_type = normal | projection
        bottle.route("/shots/<shot_id>/download/<model_id>")(self._shot_download_model)
        bottle.route("/shots/<shot_id>/download/<model_id>/<filename>")(self._shot_download_model_file)
        bottle.route("/shots/<shot_id>/<image_mode>/<image_type>/<fname>.jpg")(self._shot_get_image)  # return remote shot as jpeg


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

