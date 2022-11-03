import math
import random

import requests, json, sys
import os, glob, sys, shutil
import subprocess, shlex, time
import re, glob

from PIL import Image
from selenium import webdriver
import time
import glob
import socket
import traceback
from multiprocessing.pool import ThreadPool

from app_windows.realityCapture.alignment import Alignment
from app_windows.realityCapture.animation import Animation
from app_windows.realityCapture.calibrationData import CalibrationData
from app_windows.realityCapture.exportModel import ExportModel
from app_windows.realityCapture.markers import Markers
from app_windows.realityCapture.rawModel import RawModel
from app_windows.realityCapture.resultsArchive import ResultsArchive

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
    exit(1)
 
try:
    chromeexe = glob.glob("C:\*\Google\Chrome\Application")[0]
except:
    print("################")
    print("Google Chrome not found, install Chrome to your Program directory")
    input('')
    exit(1)


box_rcbox = '''
<ReconstructionRegion globalCoordinateSystem="NONE" globalCoordinateSystemWkt="NONE" globalCoordinateSystemName="NONE"
   isGeoreferenced="0" isLatLon="0" yawPitchRoll="0 -0 -0" widthHeightDepth="%s %s %s">
  <Header magic="5395016" version="2"/>
  <CentreEuclid centre="0 0 %s"/>
  <Residual R="1 0 0 0 1 0 0 0 1" t="0 0 0" s="1" ownerId="{65DB1F2C-807B-4520-937D-FB2D78C646D9}"/>
</ReconstructionRegion>
'''
DetectMarkersParams_xml = '''
<Configuration id="{8D21413B-0848-49A9-BF6E-8EBCCA356BC7}">
  <entry key="minMarkerMeasurements" value="0x4"/>
  <entry key="generateMarkersPaperSize" value="0"/>
  <entry key="generateMarkersMarkersPerPage" value="0x4"/>
  <entry key="generateMarkersCount" value="0x4"/>
  <entry key="imageLayer" value="geometry"/>
  <entry key="markerType" value="Circular1x12Bit"/>
</Configuration>
'''
ExportRegistrationSettings_xml = '''
<Configuration id="{2D5793BC-A65D-4318-A1B9-A05044608385}">
  <entry key="calexTrans" value="1"/>
  <entry key="calexHasDisabled" value="0x0"/>
  <entry key="MvsExportScaleZ" value="1.0"/>
  <entry key="MvsExportIsGeoreferenced" value="0x0"/>
  <entry key="MvsExportIsModelCoordinates" value="0"/>
  <entry key="MvsExportScaleY" value="1.0"/>
  <entry key="MvsExportScaleX" value="1.0"/>
  <entry key="MvsExportRotationY" value="0.0"/>
  <entry key="MvsExportcoordinatesystemtype" value="0"/>
  <entry key="MvsExportNormalFlipZ" value="false"/>
  <entry key="MvsExportRotationX" value="0.0"/>
  <entry key="hasCalexFilePath" value="1"/>
  <entry key="MvsExportNormalFlipY" value="false"/>
  <entry key="MvsExportNormalSpace" value="Mikktspace"/>
  <entry key="calexHasUndistort" value="-1"/>
  <entry key="MvsExportNormalFlipX" value="false"/>
  <entry key="MvsExportRotationZ" value="0.0"/>
  <entry key="calexFileFormat" value="Comma-separated, Name, X, Y, Z, Omega, Phi, Kappa"/>
  <entry key="MvsExportMoveZ" value="0.0"/>
  <entry key="calexFileFormatId" value="{B3EE1544-1D64-4C22-A47D-FC9F78C107B7}"/>
  <entry key="hasCalexFileName" value="1"/>
  <entry key="calexHasImageExport" value="-1"/>
  <entry key="MvsExportMoveX" value="0.0"/>
  <entry key="MvsExportNormalRange" value="ZeroToOne"/>
  <entry key="MvsExportMoveY" value="0.0"/>
</Configuration>
'''

XMPSettings_xml = '''
<Configuration id="{EC40D990-B2AF-42A4-9637-1208A0FD1322}">
  <entry key="xmpMerge" value="true"/>
  <entry key="xmpExGps" value="true"/>
  <entry key="xmpFlags" value="true"/>
  <entry key="xmpCalibGroups" value="true"/>
  <entry key="xmpCamera" value="1"/>
  <entry key="xmpRig" value="true"/>
</Configuration>

'''


def ask(question):
    while True:
        print("############################")
        print("")
        reply = str(input('%s (y/n):\n' % question)).lower().strip()
        if reply == "y":
            return True
        if reply == "n":
            return False


class RealityCapture():
    def __init__(self, source_folder, shot_name, filetype, reconstruction_quality, quality, create_mesh_from, create_textures, lit, markers, distances, pin, box_dimensions, calibration_data, debug=False):
        self.source_folder = os.path.abspath(source_folder)
        self.shot_name = shot_name
        if self.shot_name == "":
            self.shot_name = self.source_folder.split('\\')[-1]
        self.shot_name = self._clean_shot_name(self.shot_name)
        self.filetype = filetype
        self.fileextension = "glb" if self.filetype in ["gif","webp"] else self.filetype
        self.reconstruction_quality = reconstruction_quality
        self.quality = quality
        self.create_mesh_from = create_mesh_from
        self.create_textures = create_textures
        self.lit = lit
        self.markers = markers
        self.distances = distances
        self.pin = pin
        self.box_dimensions = box_dimensions
        self.debug = debug

        self.reconstruction_quality_str = self.reconstruction_quality[0].upper()
        self.quality_str = self.quality[0].upper()
        self.create_mesh_from_str = create_mesh_from[0].upper()
        self.create_textures_str = "T" if create_textures is True else ""
        self.litUnlitStr = "" if self.filetype not in ["gif", "webp", "glb"] else ("L" if self.lit else "U") if self.create_textures else ""
        self.realityCapture_filename = "rc_%s%s%s" % (self.reconstruction_quality_str, self.create_mesh_from_str, self.create_textures_str)
        self.export_filename   = "%s_%s%s%s%s%s.%s" % ( self.shot_name, self.reconstruction_quality_str, self.quality_str, self.create_mesh_from_str, self.create_textures_str, self.litUnlitStr ,self.fileextension)
        self.export_foldername = "%s_%s%s%s%s%s_%s" % ( self.shot_name, self.reconstruction_quality_str, self.quality_str, self.create_mesh_from_str, self.create_textures_str, self.litUnlitStr, self.filetype)

        self.model_path = None

        self.calibrationData = CalibrationData(self, calibration_data)
        self.markers = Markers(self)
        self.alignments = Alignment(self)
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
        self.prepare_folders()
        first_time_calibration = len(self.calibrationData.data) == 0

        tasks = [
            self.markers.load,
            self.alignments.load,
            self.rawmodel.create,
            self.exportmodel.create,
            self.animation.create if self.animation is not None else self.resultsArchive.create
        ]

        for task in tasks:
            while self.status == "active":
                task(force_reload=first_time_calibration)
                if task.success:
                    break
                while self.status == "active" and task.status == "failed":
                    time.sleep(1)


        if self.alignments.alignments_were_recreated is True:
            self.calibrationData.update_from_xmp()

        if DEBUG is False:
            try:
                shutil.rmtree(os.path.join(self.source_folder, self.export_foldername))
            except:
                print("Failed to delete %s" % os.path.join(self.source_folder, self.export_foldername))

        return self.model_path


    def get_path(self, fname):
        if "%s" in fname:
            fname = fname % self.realityCapture_filename
        return os.path.join(self.source_folder, "tmp", fname)

    def prepare_folders(self):
        if not os.path.exists(os.path.join(self.source_folder, "tmp")):
            os.mkdir(os.path.join(self.source_folder, "tmp"))

        with open(self.get_path("DetectMarkersParams.xml"), "w") as f:
            f.write(DetectMarkersParams_xml)
        with open(self.get_path("box.rcbox"), "w") as f:
            f.write(box_rcbox  % (round(self.box_dimensions[0], 2), round(self.box_dimensions[1], 2), round(self.box_dimensions[2], 2), round(self.box_dimensions[2]/2, 2)))
        with open(self.get_path("exportRegistrationSettings.xml"), "w") as f:
            f.write(ExportRegistrationSettings_xml)
        with open(self.get_path("xmp_settings.xml"), "w") as f:
            f.write(XMPSettings_xml)

        for mode in ["normal", "projection"]:
            for file in glob.glob(os.path.join(os.path.join(self.source_folder, "images", mode), "*.jpg")):
                if os.path.getsize(file) < 100000:
                    os.remove(file)
                else:
                    try:
                        im = Image.open(file)
                        im.verify()
                        im.close()
                        im = Image.open(file)
                        im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                        im.close()
                    except Exception as e:
                        print("removing broken file", file)
                        os.remove(file)
        try:
            os.mkdir(os.path.join(self.source_folder, self.export_foldername))
        except:
            pass
        self.calibrationData.delete_xmp_files()
        self.calibrationData.write_xmp_files()
        with open(os.path.join(self.source_folder, "last_usage"), "w") as f:
            f.write("%s" % int(time.time()))

    def _get_cmd_new_scene(self):
        cmd = '-newScene '
        if self.create_mesh_from in ["projection", "all"]:
            cmd += '-addFolder "%s\\images\\projection" ' % self.source_folder
            cmd += '-selectAllImages '
            cmd += '-enableTexturingAndColoring false '
            cmd += '-enableColorNormalization false '

        if self.create_mesh_from in ["normal", "all"] or self.create_textures is True:
            cmd += '-addFolder "%s\\images\\normal" ' % self.source_folder
            cmd += '-invertImageSelection '
            if self.create_mesh_from == "projection":
                cmd += '-enableMeshing false '  # don't use normal images for mesh
        cmd += '-deselectAllImages '
        return cmd

    def _get_cmd_start(self):
        cmd = '"%s" ' % RCEXE
        #cmd += '-silent "%s\\crash_report.txt" ' % self.source_folder
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
