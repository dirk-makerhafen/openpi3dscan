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

from app_windows.realityCapture.alignment import Alignment
from app_windows.realityCapture.animation import Animation
from app_windows.realityCapture.calibrationData import CalibrationData
from app_windows.realityCapture.download import Download
from app_windows.realityCapture.exportModel import ExportModel
from app_windows.realityCapture.markers import Markers
from app_windows.realityCapture.prepareFolder import PrepareFolder
from app_windows.realityCapture.rawModel import RawModel
from app_windows.realityCapture.resultsArchive import ResultsArchive
from app_windows.realityCapture.upload import Upload
from app_windows.realityCapture.verifyImages import VerifyImages

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

CACHE_DIR = 'c:\shots'
CACHE_SIZE = 25
SERVER = None
DEBUG = "debug" in sys.argv

try:
    RCEXE = glob.glob("C:\*\Capturing Reality\RealityCapture\RealityCapture.exe")[0]
except:
    print("################")
    print("RealityCapture.exe not found, install RealityCapture to your Program directory")
    input('')
    #exit(1)
 
try:
    chromeexe = glob.glob("C:\*\Google\Chrome\Application")[0]
except:
    print("################")
    print("Google Chrome not found, install Chrome to your Program directory")
    input('')
    #exit(1)




def ask(question):
    while True:
        print("############################")
        print("")
        reply = str(input('%s (y/n):\n' % question)).lower().strip()
        if reply == "y":
            return True
        if reply == "n":
            return False
CACHE_DIR = "None"


class RealityCapture():
    def __init__(self, source_ip, source_dir,  shot_id, model_id, shot_name, filetype, reconstruction_quality, export_quality, create_mesh_from, create_textures, lit, distances, pin, box_dimensions, calibration_data, debug=False):
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
        self.workingdir = os.path.join(CACHE_DIR, self.shot_name)

        self.reconstruction_quality_str = self.reconstruction_quality[0].upper()
        self.quality_str = self.export_quality[0].upper()
        self.create_mesh_from_str = create_mesh_from[0].upper()
        self.create_textures_str = "T" if create_textures is True else ""
        self.litUnlitStr = "" if self.filetype not in ["gif", "webp", "glb"] else ("L" if self.lit else "U") if self.create_textures else ""
        self.realityCapture_filename = "rc_%s%s%s" % (self.reconstruction_quality_str, self.create_mesh_from_str, self.create_textures_str)
        self.export_filename   = "%s_%s%s%s%s%s.%s" % ( self.shot_name, self.reconstruction_quality_str, self.quality_str, self.create_mesh_from_str, self.create_textures_str, self.litUnlitStr ,self.fileextension)
        self.export_foldername = "%s_%s%s%s%s%s_%s" % ( self.shot_name, self.reconstruction_quality_str, self.quality_str, self.create_mesh_from_str, self.create_textures_str, self.litUnlitStr, self.filetype)

        self.model_path = None

        self.calibrationData = CalibrationData(self, calibration_data)
        self.prepareFolder = PrepareFolder(self)
        self.download = None if self.source_ip is None else Download(self)
        self.upload   = None if self.source_ip is None else Upload(self)
        self.verifyImages = VerifyImages(self)
        self.markers = Markers(self)
        self.alignments = Alignment(self, distances)
        self.rawmodel = RawModel(self)
        self.exportmodel = ExportModel(self)
        if self.filetype in ["gif","webp"]:
            self.animation = Animation(self)
            self.resultsArchive = None
        else:
            self.animation = None
            self.resultsArchive = ResultsArchive(self)
        self.status = ""

    def process(self):
        first_time_calibration = len(self.calibrationData.data) == 0

        tasks = []
        tasks.append(self.prepareFolder.run)
        if self.download is not None:
            tasks.append(self.download.run)
        tasks.append(self.verifyImages.run)
        tasks.append(self.markers.load)
        tasks.append(self.alignments.load)
        tasks.append(self.rawmodel.create)
        tasks.append(self.exportmodel.create)
        if self.animation is not None:
            tasks.append(self.animation.create)
        else:
            tasks.append(self.resultsArchive.create)
        if self.upload is not None:
            tasks.append(self.upload.run)

        for task in tasks:
            while self.status == "active":
                task()
                if task.success:
                    break
                while self.status == "active" and task.status == "failed":
                    time.sleep(1)


        if self.alignments.alignments_were_recreated is True:
            self.calibrationData.update_from_xmp()

        if DEBUG is False:
            try:
                shutil.rmtree(os.path.join(self.workingdir, self.export_foldername))
            except:
                print("Failed to delete %s" % os.path.join(self.workingdir, self.export_foldername))

        return self.model_path


    def get_path(self, fname):
        if "%s" in fname:
            fname = fname % self.realityCapture_filename
        return os.path.join(self.workingdir, "tmp", fname)


    def _get_cmd_new_scene(self):
        cmd = '-newScene '
        if self.create_mesh_from in ["projection", "all"]:
            cmd += '-addFolder "%s\\images\\projection" ' % self.workingdir
            cmd += '-selectAllImages '
            cmd += '-enableTexturingAndColoring false '
            cmd += '-enableColorNormalization false '

        if self.create_mesh_from in ["normal", "all"] or self.create_textures is True:
            cmd += '-addFolder "%s\\images\\normal" ' % self.workingdir
            cmd += '-invertImageSelection '
            if self.create_mesh_from == "projection":
                cmd += '-enableMeshing false '  # don't use normal images for mesh
        cmd += '-deselectAllImages '
        return cmd

    def _get_cmd_start(self):
        cmd = '"%s" ' % RCEXE
        #cmd += '-silent "%s\\crash_report.txt" ' % self.workingdir
        #cmd += '-set "appQuitOnError=true" '
        return cmd

    def _run_command(self, cmd, name):
        print("Next Command: %s" % name)
        print(cmd)
        s = time.time()
        subprocess.run(shlex.split(cmd))
        print("Command '%s' took %s seconds" % (name, int(time.time() - s)))

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
