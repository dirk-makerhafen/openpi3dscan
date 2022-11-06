import math
import random

import requests, json, sys
import os, glob, sys, shutil
import subprocess, shlex, time
import re, glob

from PIL import Image
#from selenium import webdriver
import time
import glob
import socket
import traceback
from multiprocessing.pool import ThreadPool

from pyhtmlgui import Observable

from app_windows.realityCapture.alignment import Alignment
from app_windows.realityCapture.animation import Animation
from app_windows.realityCapture.calibrationData import CalibrationData
from app_windows.realityCapture.calibrationDataUpdate import CalibrationDataUpdate
from app_windows.realityCapture.calibrationDataWrite import CalibrationDataWrite
from app_windows.realityCapture.download import Download
from app_windows.realityCapture.exportModel import ExportModel
from app_windows.realityCapture.markers import Markers
from app_windows.realityCapture.prepareFolder import PrepareFolder
from app_windows.realityCapture.rawModel import RawModel
from app_windows.realityCapture.resultsArchive import ResultsArchive
from app_windows.realityCapture.upload import Upload
from app_windows.realityCapture.verifyImages import VerifyImages
from app_windows.settings.settings import SettingsInstance

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

SERVER = None
DEBUG = "debug" in sys.argv

try:
    RCEXE = glob.glob("C:\*\Capturing Reality\RealityCapture\RealityCapture.exe")[0]
except:
    print("################")
    print("RealityCapture.exe not found, install RealityCapture to your Program directory")

try:
    chromeexe = glob.glob("C:\*\Google\Chrome\Application")[0]
except:
    print("################")
    print("Google Chrome not found, install Chrome to your Program directory")





def ask(question):
    while True:
        print("############################")
        print("")
        reply = str(input('%s (y/n):\n' % question)).lower().strip()
        if reply == "y":
            return True
        if reply == "n":
            return False


class RealityCapture(Observable):
    def __init__(self, source_ip, source_dir, shot_id, model_id, shot_name, filetype, reconstruction_quality,
                 export_quality, create_mesh_from, create_textures, lit, distances, pin, box_dimensions,
                 calibration_data, debug=False):
        super().__init__()
        self.source_ip = source_ip
        self.source_dir = source_dir
        self.shot_id = shot_id
        self.model_id = model_id
        self.shot_name = self._clean_shot_name(shot_name if shot_name != "" else self.shot_id)
        self.filetype = filetype
        self.fileextension = "glb" if self.filetype in ["gif","webp"] else self.filetype
        self.reconstruction_quality = reconstruction_quality
        self.export_quality = export_quality
        self.create_mesh_from = create_mesh_from
        self.create_textures = create_textures
        self.lit = lit
        self.pin = pin
        self.box_dimensions = box_dimensions
        self.debug = debug
        self.workingdir = os.path.join(SettingsInstance().settingsCache.directory, self.shot_name)

        self.reconstruction_quality_str = self.reconstruction_quality[0].upper()
        self.quality_str = self.export_quality[0].upper()
        self.create_mesh_from_str = create_mesh_from[0].upper()
        self.create_textures_str = "T" if create_textures is True else ""
        self.litUnlitStr = "" if self.filetype not in ["gif", "webp", "glb"] else ("L" if self.lit else "U") if self.create_textures else ""
        self.realityCapture_filename = "rc_%s%s%s" % (self.reconstruction_quality_str, self.create_mesh_from_str, self.create_textures_str)
        self.export_filename   = "%s_%s%s%s%s%s.%s" % ( self.shot_name, self.reconstruction_quality_str, self.quality_str, self.create_mesh_from_str, self.create_textures_str, self.litUnlitStr ,self.fileextension)
        self.export_foldername = "%s_%s%s%s%s%s_%s" % ( self.shot_name, self.reconstruction_quality_str, self.quality_str, self.create_mesh_from_str, self.create_textures_str, self.litUnlitStr, self.filetype)

        self.result_file = None

        self.calibrationData = CalibrationData(self, calibration_data)
        self.prepareFolder = PrepareFolder(self)
        self.calibrationDataWrite = CalibrationDataWrite(self)
        self.calibrationDataUpdate = CalibrationDataUpdate(self)
        self.download = None if self.source_ip is None else Download(self)
        self.verifyImages = VerifyImages(self)
        self.markers = Markers(self, distances)
        self.alignments = Alignment(self, distances)
        self.rawmodel = RawModel(self)
        self.exportmodel = ExportModel(self)
        if self.filetype in ["gif","webp"]:
            self.animation = Animation(self)
            self.resultsArchive = None
        else:
            self.animation = None
            self.resultsArchive = ResultsArchive(self)
        self.upload   = None if self.source_ip is None else Upload(self)
        self.status = ""

    def process(self):
        self.status = "active"

        tasks = [
            self.prepareFolder,
            self.download,
            self.verifyImages,
            self.calibrationDataWrite,
            self.markers,
            self.alignments,
            self.calibrationDataUpdate,
            self.rawmodel,
            self.exportmodel,
            self.animation,
            self.resultsArchive,
            self.upload,
        ]
        tasks = [task for task in tasks if task is not None]
        for task in tasks:
            while self.status == "active":
                task.run()

        if DEBUG is False:
            try:
                shutil.rmtree(os.path.join(self.workingdir, self.export_foldername))
            except:
                print("Failed to delete %s" % os.path.join(self.workingdir, self.export_foldername))
        self.status = "idle"


    def _clean_shot_name(self, name):
        name = name.replace("ä", "ae").replace("ü", "ue").replace("Ü", "Ue")
        name = name.replace("ö", "oe").replace("Ä", "Ae").replace("Ö", "Oe")
        name = re.sub('\s+', ' ', name)
        name = re.sub('[^A-Za-z0-9_. ]+', '', name)
        name = name.replace("..", ".").replace("__", "_").replace("  ", " ")
        name = name.strip()
        while name[-1] in ["_", "."]:
            name = name[:-1].strip()
        while name[0] in ["_", "."]:
            name = name[1:].strip()
        return name