import math
import random

import requests, json, sys
import os, glob, sys, shutil
import subprocess, shlex, time
import re, glob
from selenium import webdriver
import time
import glob
import socket
import traceback
from multiprocessing.pool import ThreadPool

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

CACHE_DIR = 'c:\shots'
CACHE_SIZE = 25
SERVER = None
DEBUG = "debug" in sys.argv
MARKERS = []
DISTANCES = {}
LICENSE_PIN = ""
BOX_DIMENSIONS = [1.9, 1.9, 2.5]
calibrationData = None

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
XMP_TEMPLATE_full = '''
<x:xmpmeta xmlns:x="adobe:ns:meta/">
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description xcr:Version="3" xcr:PosePrior="initial" xcr:Coordinates="absolute"
       xcr:DistortionModel="brown3" xcr:FocalLength35mm="%(FocalLength35mm)s"
       xcr:Skew="0" xcr:AspectRatio="1" xcr:PrincipalPointU="%(PrincipalPointU)s"
       xcr:PrincipalPointV="%(PrincipalPointV)s" xcr:CalibrationPrior="initial"
       xcr:CalibrationGroup="%(Group)s" xcr:DistortionGroup="%(Group)s" xcr:InTexturing="%(InTexturing)s"
       xcr:InMeshing="%(InMeshing)s" xmlns:xcr="http://www.capturingreality.com/ns/xcr/1.1#">
      <xcr:Rotation>%(Rotation)s</xcr:Rotation>
      <xcr:Position>%(Position)s</xcr:Position>
      <xcr:DistortionCoeficients>%(DistortionCoeficients)s</xcr:DistortionCoeficients>
    </rdf:Description>
  </rdf:RDF>
</x:xmpmeta>
'''
XMP_TEMPLATE = '''
<x:xmpmeta xmlns:x="adobe:ns:meta/">
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description xcr:Version="3" xcr:Coordinates="absolute" xcr:DistortionModel="brown3" 
            xcr:FocalLength35mm="%(FocalLength35mm)s"
            xcr:PrincipalPointU="%(PrincipalPointU)s"
            xcr:PrincipalPointV="%(PrincipalPointV)s" 
            xcr:PosePrior="initial"
            xcr:CalibrationPrior="%(CalibrationPrior)s"
            xcr:CalibrationGroup="%(Group)s" 
            xcr:DistortionGroup="%(Group)s" 
            xmlns:xcr="http://www.capturingreality.com/ns/xcr/1.1#">
            <xcr:DistortionCoeficients>%(DistortionCoeficients)s</xcr:DistortionCoeficients>
            <xcr:Rotation>%(Rotation)s</xcr:Rotation>
            <xcr:Position>%(Position)s</xcr:Position>
        </rdf:Description>
</rdf:RDF>
</x:xmpmeta>
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


class CalibrationData():
    def __init__(self):
        self.data = {}

    def reset(self):
        self.data = {}

    def reset_positions(self):
        for key in self.data:
            if "Position" in self.data[key]:
                del self.data[key]["Position"]
            if "Rotation" in self.data[key]:
                del self.data[key]["Rotation"]

    def center(self,center_align):
        x,y,z = center_align
        for key in self.data:
            if "Position" in self.data[key]:
                for index, pos in enumerate(self.data[key]["Position"]):
                    pos = [pos[0] - x, pos[1] - y, pos[2] - z, ]
                    self.data[key]["Position"][index] = pos

    def get_camera_ids(self):
        return ["%s" % key for key in self.data.keys()]

    def get(self, segment, row, key):
        cam_id = "%s-%s" % (segment, row)
        data = self.data[cam_id][key]
        if type(data[0]) == list:
            return [ sum( t[i] for t in data) / len(data) for i in range(0,len(data[0])) ]
        else:
            return sum(data) / len(data)

    def count(self, segment, row, key):
        cam_id = "%s-%s" % (segment, row)
        try:
            return len(self.data[cam_id][key])
        except:
            return 0

    def add_data(self, segment, row, key, data):
        cam_id = "%s-%s" % ( segment, row )
        if cam_id not in self.data:
            self.data[cam_id] = {}
        if key not in self.data[cam_id]:
            self.data[cam_id][key] = []
        self.data[cam_id][key].append(data)
        self.data[cam_id][key] = self.data[cam_id][key][-30:]


class RealityCapture():
    def __init__(self, source_folder, shot_name, filetype, reconstruction_quality, quality, create_mesh_from, create_textures):
        self.source_folder = os.path.abspath(source_folder)
        self.shot_name = shot_name
        if self.shot_name == "":
            self.shot_name = self.source_folder.split('\\')[-1]
        self.shot_name = self._clean_shot_name(self.shot_name)
        self.filetype = filetype
        self.fileextension = filetype
        if self.fileextension in ["gif","webp"]:
            self.fileextension = "glb"
        self.reconstruction_quality = reconstruction_quality
        self.quality = quality
        self.create_mesh_from = create_mesh_from
        self.create_textures = create_textures
        self.reconstruction_quality_str = self.reconstruction_quality[0].upper()
        self.quality_str = self.quality[0].upper()
        self.create_mesh_from_str = create_mesh_from[0].upper()
        self.create_textures_str = "T" if create_textures is True else ""
        self.realityCapture_filename = "realityCapture_%s%s%s" % (self.reconstruction_quality_str, self.create_mesh_from_str, self.create_textures_str)
        self.export_filename   = "%s_%s%s%s%s.%s" % ( self.shot_name, self.reconstruction_quality_str, self.quality_str, self.create_mesh_from_str, self.create_textures_str, self.fileextension)
        self.export_foldername = "%s_%s%s%s%s_%s" % ( self.shot_name, self.reconstruction_quality_str, self.quality_str, self.create_mesh_from_str, self.create_textures_str, self.filetype)
        self.available_markers = []
        self.alignments = []
        self.alignments_were_recreated = False
        self.xmp_exclude = []
        self.model_path = None

    def process(self):
        self.prepare_folders()
        first_time_calibration = len(calibrationData.data) == 0

        self.load_markers(force_reload=first_time_calibration)
        while len(self.available_markers) < 2:
            if ask("%s markers loaded, repeat?" % len(self.available_markers)):
                self.load_markers(force_reload=True)
            else:
                return None

        self.load_alignments(force_reload=first_time_calibration)
        while len(self.alignments) < 2:
            if ask("%s alignments loaded, repeat?" % len(self.alignments) ):
                self.load_alignments(force_reload=True)
            else:
                return None

        self.create_raw_model(force_reload=first_time_calibration)
        while not os.path.exists(os.path.join(self.source_folder, "%s.raw_exists" % self.realityCapture_filename)):
            if ask("No model created, repeat?"):
                self.create_raw_model(force_reload=True)
            else:
                return None

        self.create_export_model(force_reload=first_time_calibration)
        while self.model_path is None:
            if ask("No export model created, repeat?"):
                self.create_export_model(force_reload=True)
            else:
                return None

        if self.alignments_were_recreated is True or first_time_calibration is True:
            self.load_calibrationdata_via_xmp()

        if DEBUG is False:
            try:
                shutil.rmtree(os.path.join(self.source_folder, self.export_foldername))
            except:
                print("Failed to delete %s" % os.path.join(self.source_folder, self.export_foldername))

        return self.model_path

    def prepare_folders(self):
        with open(os.path.join(self.source_folder, "DetectMarkersParams.xml"), "w") as f:
            f.write(DetectMarkersParams_xml)
        with open(os.path.join(self.source_folder, "box.rcbox"), "w") as f:
            f.write(box_rcbox  % (round(BOX_DIMENSIONS[0], 2), round(BOX_DIMENSIONS[1], 2), round(BOX_DIMENSIONS[2], 2), round(BOX_DIMENSIONS[2]/2, 2)))
        with open(os.path.join(self.source_folder, "exportRegistrationSettings.xml"), "w") as f:
            f.write(ExportRegistrationSettings_xml)
        with open(os.path.join(self.source_folder, "xmp_settings.xml"), "w") as f:
            f.write(XMPSettings_xml)
        if not os.path.exists(os.path.join(self.source_folder, "images")):
            os.mkdir(os.path.join(self.source_folder, "images"))
            shutil.move(os.path.join(self.source_folder, "normal"), os.path.join(self.source_folder, "images"))
            shutil.move(os.path.join(self.source_folder, "projection"), os.path.join(self.source_folder, "images"))
        for mode in ["normal", "projection"]:
            for file in glob.glob(os.path.join(os.path.join(self.source_folder, "images", mode), "*.jpg")):
                if os.path.getsize(file) < 100000:
                    os.remove(file)
        try:
            os.mkdir(os.path.join(self.source_folder, self.export_foldername))
        except:
            pass
        self._delete_xmp_files()
        self.write_xmp_files()

    def load_markers(self, force_reload=False):
        markers_csv = os.path.join(self.source_folder, "%s_markers.csv" % self.realityCapture_filename)
        if force_reload is True and os.path.exists(markers_csv):
            os.remove(markers_csv)

        if os.path.exists(markers_csv):
            self._load_markers_csv(markers_csv)

        if len(self.available_markers) < 2 or force_reload is True:
            cmd = self._get_cmd_start()
            cmd += self._get_cmd_new_scene()
            cmd += '-detectMarkers "%s\\DetectMarkersParams.xml" ' % self.source_folder
            cmd += '-getLicense "%s" ' % LICENSE_PIN
            cmd += '-exportControlPointsMeasurements "%s\\%s_markers.csv" ' % (
            self.source_folder, self.realityCapture_filename,)
            cmd += '-quit '
            self._run_command(cmd, "load_markers")
            self._load_markers_csv(markers_csv)

    def _load_markers_csv(self, markers_csv):
        markers = set()
        if os.path.exists(markers_csv):
            with open(markers_csv, "r") as f:
                for line in f.read().split("\n"):
                    if line.startswith("#") or len(line) < 10:
                        continue
                    markers.add(line.split(",")[1].strip())
        self.available_markers = list(markers)
        print("%s markers loaded" % len(self.available_markers))

    def load_alignments(self, force_reload=False):
        alignments_csv = os.path.join(self.source_folder, "%s_alignments.csv" % self.realityCapture_filename)
        rc_proj_file = os.path.join(self.source_folder, "%s.rcproj" % self.realityCapture_filename)
        raw_exists_file = os.path.join(self.source_folder, "%s.raw_exists" % self.realityCapture_filename)

        if os.path.exists(alignments_csv) and force_reload is True:
            os.remove(alignments_csv)

        if os.path.exists(alignments_csv):
            self._load_alignments_csv(alignments_csv)

        if len(self.alignments) < 12 or force_reload is True:
            if os.path.exists(alignments_csv):
                os.remove(alignments_csv)
            if os.path.exists(rc_proj_file):
                os.remove(rc_proj_file)
            if os.path.exists(raw_exists_file):
                os.remove(raw_exists_file)
            cmd = self._get_cmd_start()
            cmd += self._get_cmd_new_scene()
            cmd += '-align '
            cmd += '-detectMarkers "%s\\DetectMarkersParams.xml" ' % self.source_folder
            cmd += self._get_cmd_defineDistance()
            cmd += '-selectMaximalComponent '
            cmd += '-align '
            cmd += '-renameSelectedComponent "MAIN" '
            cmd += '-selectComponent "Component 0" '
            cmd += '-deleteSelectedComponent '
            cmd += '-selectComponent "MAIN" '
            cmd += '-setReconstructionRegion "%s\\box.rcbox" ' % self.source_folder
            cmd += '-getLicense "%s" ' % LICENSE_PIN
            cmd += '-exportRegistration "%s\\%s_alignments.csv" "%s\\exportRegistrationSettings.xml" ' % (self.source_folder, self.realityCapture_filename, self.source_folder)
            cmd += '-save "%s\\%s.rcproj" ' % (self.source_folder, self.realityCapture_filename)
            cmd += '-quit '
            self._run_command(cmd, "load_alignments")
            if os.path.exists(os.path.join(self.source_folder, "%s_alignments.csv" % self.realityCapture_filename)):
                self.alignments_were_recreated = True
            self._load_alignments_csv(alignments_csv)

    def _load_alignments_csv(self, alignments_csv):
        self.alignments = []
        if os.path.exists(alignments_csv):
            with open(alignments_csv, "r") as f:
                for line in f.read().split("\n"):
                    if line.startswith("#") or len(line) < 10:
                        continue
                    al = line.split(",")
                    al = [al[0], float(al[1]), float(al[2]), float(al[3]), None]
                    self.alignments.append(al)
        print("%s alignments loaded" % len(self.alignments))
        c_x = (max([x[1] for x in self.alignments]) + min([x[1] for x in self.alignments])) / 2
        c_y = (max([x[2] for x in self.alignments]) + min([x[2] for x in self.alignments])) / 2
        c_z = (max([x[3] for x in self.alignments]) + min([x[3] for x in self.alignments])) / 2

        avg_x = sum([x[1] for x in self.alignments]) / len(self.alignments)
        avg_y = sum([x[2] for x in self.alignments]) / len(self.alignments)
        avg_z = sum([x[3] for x in self.alignments]) / len(self.alignments)
        # print("avg", avg_x, avg_y, avg_z)
        self.box_center_correction = [c_x, c_y, c_z]
        print("Box center corrections:", c_x, c_y, c_z)

    def load_calibrationdata_via_xmp(self):
        cmd = self._get_cmd_start()
        cmd += '-load "%s\\%s.rcproj" ' % (self.source_folder, self.realityCapture_filename)
        cmd += '-exportXMP "%s\\xmp_settings.xml" ' % self.source_folder
        cmd += '-quit '
        self._run_command(cmd, "export_xmp")

        cam_data = self._read_xmp_files()
        self._delete_xmp_files()
        first_time_calibration = len(calibrationData.data) == 0
        for data in cam_data:
            if data["FocalLength35mm"] > 36.2 or data["FocalLength35mm"] < 34.5:
                print("No adding", data )
                continue
            if data["cam_id"] not in self.xmp_exclude:
                calibrationData.add_data(data["segment"], data["row"], "FocalLength35mm", data["FocalLength35mm"])
                calibrationData.add_data(data["segment"], data["row"], "PrincipalPointU", data["PrincipalPointU"])
                calibrationData.add_data(data["segment"], data["row"], "PrincipalPointV", data["PrincipalPointV"])
                calibrationData.add_data(data["segment"], data["row"], "DistortionCoeficients", data["DistortionCoeficients"])
            if "Rotation" in data:
                calibrationData.add_data(data["segment"], data["row"], "Rotation", data["Rotation"])
            if "Position" in data:
                calibrationData.add_data(data["segment"], data["row"], "Position", data["Position"])

        if first_time_calibration is True:
            positions = [data["Position"] for data in cam_data if "Position" in data]
            c_x = (max([x[0] for x in positions]) + min([x[0] for x in positions])) / 2
            c_y = (max([x[1] for x in positions]) + min([x[1] for x in positions])) / 2
            c_z = (max([x[2] for x in positions]) + min([x[2] for x in positions])) / 2
            center_align = [c_x, c_y, c_z - (BOX_DIMENSIONS[2] / 2)]
            print("new center data", center_align)
            calibrationData.center(center_align)

    def _read_xmp_files(self):
        camera_data = []
        for path in glob.glob(os.path.join(self.source_folder, "images", "*", "*.xmp")):
            img_path = path.replace(".xmp",".jpg")
            if not os.path.exists(img_path):
                continue
            data = open(path, "r").read()
            try:
                cam_data = {
                    "segment"              : path.split('\\')[-1].split("-")[0].replace("seg","").strip(),
                    "row"                  : path.split('\\')[-1].split("-")[1].replace("cam","").strip(),
                    "mode"                 : path.split('\\')[-1].split('-')[2].strip(),
                    "FocalLength35mm"      : float(data.split("FocalLength35mm=")[1].split('"')[1]),
                    "PrincipalPointU"      : float(data.split("PrincipalPointU=")[1].split('"')[1]),
                    "PrincipalPointV"      : float(data.split("PrincipalPointV=")[1].split('"')[1]),
                    "DistortionCoeficients": [float(x) for x in data.split("DistortionCoeficients>")[1].split('<')[0].split(" ")],
                    "CalibrationPrior"     : data.split("CalibrationPrior=")[1].split('"')[1],
                }
                cam_data["cam_id"] = "%s-%s" % (cam_data["segment"], cam_data["row"])
            except Exception as e:
                print("Failed to load",path ,e)
                continue
            try:
                cam_data["Rotation"]= [float(x) for x in data.split("Rotation>")[1].split('<')[0].split(" ")]
            except Exception as e:
                pass
            try:
                cam_data["Position"] = [float(x) for x in data.split("Position>")[1].split('<')[0].split(" ")]
            except Exception as e:
                try:
                    cam_data["Position"] = [float(x) for x in data.split("Position=")[1].split('"')[1].split(" ")]
                except Exception as e:
                    pass

            camera_data.append(cam_data)
        return camera_data

    def _delete_xmp_files(self):
        for path in glob.glob(os.path.join(self.source_folder, "images", "*","*.xmp")):
            os.remove(path)

    def write_xmp_files(self):
        self.xmp_exclude = []
        for cam_id in calibrationData.get_camera_ids():
            segment, row = cam_id.split("-")
            group_id = ( int(segment) * 100 ) + int(row)
            if calibrationData.count(segment, row, "FocalLength35mm") == 0:
               continue

            CalibrationPrior = "initial"
            if calibrationData.count(segment, row, "FocalLength35mm") > 20 and random.random() > 0.10: # 10% chance to adjust focus even if we already have enough data
                CalibrationPrior = "locked"
                self.xmp_exclude.append(cam_id)

            try:
                s = XMP_TEMPLATE % {
                    "FocalLength35mm"       :                             calibrationData.get(segment, row, "FocalLength35mm"),
                    "PrincipalPointU"       :                             calibrationData.get(segment, row, "PrincipalPointU"),
                    "PrincipalPointV"       :                             calibrationData.get(segment, row, "PrincipalPointV"),
                    "DistortionCoeficients" : " ".join(["%s" % x for x in calibrationData.get(segment, row, "DistortionCoeficients")] ),
                    "Rotation"              : " ".join(["%s" % x for x in calibrationData.get(segment, row, "Rotation")] ),
                    "Position"              : " ".join(["%s" % x for x in calibrationData.get(segment, row, "Position")] ),
                    "Group"                 : group_id,
                    "CalibrationPrior"      : CalibrationPrior,
                }
                for mode in ["normal", "projection"]:
                    xmp_path = os.path.join(self.source_folder, "images", mode, "seg%s-cam%s-%s.xmp" % (segment, row, mode[0]))
                    img_path = xmp_path.replace(".xmp", ".jpg")
                    if os.path.exists(img_path):
                        with open(xmp_path, "w") as f:
                            f.write(s)
            except:
                pass

    def create_raw_model(self, force_reload=False):
        raw_exists_file = os.path.join(self.source_folder, "%s.raw_exists" % self.realityCapture_filename)
        rc_proj_file = os.path.join(self.source_folder, "%s.rcproj" % self.realityCapture_filename)
        if (not os.path.exists(raw_exists_file) or force_reload == True) and os.path.exists(rc_proj_file):
            cmd = self._get_cmd_start()
            last_changed = os.path.getmtime(rc_proj_file)
            cmd += '-load "%s\\%s.rcproj" ' % (self.source_folder, self.realityCapture_filename)
            cmd += '-moveReconstructionRegion "%s" "%s" "%s" ' % (self.box_center_correction[0], self.box_center_correction[1], self.box_center_correction[2] - (BOX_DIMENSIONS[2]/2)  )  #
            cmd += '-correctColors '
            if self.reconstruction_quality == "preview":
                cmd += '-calculatePreviewModel '
            elif self.reconstruction_quality == "high":
                cmd += '-calculateHighModel '
            else:
                cmd += '-calculateNormalModel '
            for i in range(3):
                cmd += '-selectTrianglesOutsideReconReg '
                cmd += '-removeSelectedTriangles '
                cmd += self._get_cmd_cleanup_lower_region()
                cmd += '-rotateReconstructionRegion 0 0 30 '  #
            cmd += '-cleanModel '
            # cmd += '-smooth '
            cmd += '-simplify 4000000 '
            cmd += '-selectLargestModelComponent '
            cmd += '-invertTrianglesSelection '
            cmd += '-removeSelectedTriangles '
            cmd += '-renameSelectedModel "RAW" '
            for i in range(1, 19):
                cmd += '-selectModel "Model %s" ' % i
                cmd += '-deleteSelectedModel '
            cmd += '-save "%s\\%s.rcproj" ' % (self.source_folder, self.realityCapture_filename)
            cmd += '-clearCache '
            cmd += '-quit '
            self._run_command(cmd, "create_raw_model")
            if last_changed != os.path.getmtime(rc_proj_file):
                with open(os.path.join(self.source_folder, "%s.raw_exists" % self.realityCapture_filename), "w") as f:
                    f.write("raw created")
            else:
                print("Failed to create raw model, no changes in rcproj")
        else:
            print("raw model already exists")

    def create_export_model(self, force_reload=False):
        output_model_path = os.path.join(self.source_folder, self.export_foldername, self.export_filename.replace(" ","_" if self.filetype not in ["3mf","stl", ] else " "))

        if force_reload is True and os.path.exists(output_model_path):
            os.remove(output_model_path)

        if self.filetype == "rcproj":
            rcproj = os.path.join(self.source_folder, "%s.rcproj" % self.realityCapture_filename)
            rcprojdir = os.path.join(self.source_folder, self.realityCapture_filename)
            imgdir = os.path.join(self.source_folder, "images")
            target_dir = os.path.join(self.source_folder, self.export_foldername)
            try:
                shutil.rmtree(target_dir)
            except:
                print("Failed to delete %s" % target_dir)
            os.mkdir(target_dir)
            shutil.copy(rcproj, target_dir)
            shutil.copy("rc_rebase.exe", target_dir)
            shutil.copytree(rcprojdir, os.path.join(target_dir, self.realityCapture_filename))
            shutil.copytree(imgdir, os.path.join(target_dir, "images"))

        elif not os.path.exists(output_model_path):
            cmd = self._get_cmd_start()
            cmd += '-load "%s\\%s.rcproj" ' % (self.source_folder, self.realityCapture_filename)
            cmd += '-selectComponent "MAIN" '
            cmd += '-selectModel "RAW" '
            if self.quality == "high":
                cmd += '-simplify 4000000 '
            if self.quality == "normal":
                cmd += '-simplify 1000000 '
            if self.quality == "low":
                cmd += '-simplify 500000 '
            cmd += '-cleanModel '
            if self.create_textures is True:
                cmd += '-calculateTexture '
                cmd += '-calculateVertexColors '
            cmd += '-renameSelectedModel "EXPORT" '
            cmd += '-getLicense "%s" ' % LICENSE_PIN
            cmd += '-exportModel "EXPORT" "%s\\%s\\%s" ' % (self.source_folder, self.export_foldername, self.export_filename)
            cmd += '-quit '
            self._run_command(cmd, "create_export_model")

            if not os.path.exists(output_model_path):
                print("%s model not found, error" % output_model_path)
                return

        if self.filetype == "gif":
            images_path = os.path.join(self.source_folder, self.export_foldername)
            gif_file = os.path.join(self.source_folder, "%s.gif" % self.export_foldername.replace("_gif", ""))
            self._convert_glb_to_images(output_model_path, images_path)
            self._screenshots_to_animation(images_path, gif_file, "gif")
            self.model_path = gif_file

        elif self.filetype == "webp":
            images_path = os.path.join(self.source_folder, self.export_foldername)
            webp_file = os.path.join(self.source_folder, "%s.webp" % self.export_foldername.replace("_webp", ""))
            self._convert_glb_to_images(output_model_path, images_path)
            self._screenshots_to_animation(images_path, webp_file, "webp")
            self.model_path = webp_file

        else:
            model_file_zip = os.path.join(self.source_folder, "%s.zip" % self.export_foldername)
            if os.path.exists(model_file_zip):
                os.remove(model_file_zip)
            os.system("cd \"%s\" & powershell -command \"Compress-Archive '%s\\*' '%s.zip'\"" % (self.source_folder, self.export_foldername, self.export_foldername))
            if not os.path.exists(model_file_zip):
                print("Failed to create model zip")
                self.model_path = None
            else:
                print("Model zip created")
                self.model_path = model_file_zip

    def _convert_glb_to_images(self, glb_path, output_path):
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--allow-file-access-from-files")
        browser = webdriver.Chrome(executable_path=os.path.join(SCRIPT_DIR,"chromedriver.exe"), options=options)
        browser.set_window_position(0, 0)
        browser.set_window_size(1200, 1200)
            
        browser.get("file:\\%s?src=%s" % (os.path.join(SCRIPT_DIR,"modelview.html"), glb_path.replace('\\','/')))
        
        time.sleep(5)
        angle = 0
        angle_add = 8
        if self.quality == "high":
            angle_add = 6
        elif self.quality == "normal":
            angle_add = 8
        elif self.quality == "low":
            angle_add = 10

        while angle < 360:    
            browser.save_screenshot(os.path.join(output_path, "screenshot_%s.png" % ("%s"%angle).zfill(3)))
            angle += angle_add
            browser.execute_script("rotate(%s);" % angle)
            time.sleep(0.3)
        browser.close()
        if DEBUG is False:
            os.remove(glb_path)
    
    def _screenshots_to_animation(self, path, output_file, filetype):
        files  = glob.glob(os.path.join(path, "screenshot_*.png"))
        if len(files) == 0:
            print("no screenshots found")
            return

        size = 1000
        if self.quality == "high":
            size = 1400
        elif self.quality == "normal":
            size = 1100
        elif self.quality == "low":
            size = 900

        def f(file):
            os.system('mogrify.exe -resize %sx "%s"' % (size,file))
            os.system('mogrify.exe -crop %sx%s+100+100 +repage "%s"' % (size-130,size-100,file))
            os.system('optipng.exe -clobber "%s"' % file)
            os.system('convert.exe "%s" "%s"' % (file, "%s.gif" % file[:-4]))
        ThreadPool(8).map(f, files)
        total_duration = 400 # in 1/100s of seconds
        delay = int(round(total_duration / len(files),0))
        os.system('gifsicle.exe --optimize=3 --delay=%s --loop "%s\\screenshot_*.gif" > "%s\\tmp.gif" ' % (delay, path, path))
        if os.path.exists(os.path.join(path, "tmp.gif")):
            if filetype == "gif":
                os.rename(os.path.join(path,"tmp.gif"), output_file)
            if filetype == "webp":
                os.system('convert.exe "%s\\tmp.gif" "%s"' % (path, output_file))

        if DEBUG is False:
            for f in glob.glob(os.path.join(path, "screenshot_*.*")):
                os.remove(f)
            if os.path.exists(os.path.join(path, "tmp.gif")):
                os.remove(os.path.join(path, "tmp.gif"))

    def _get_cmd_cleanup_lower_region(self):
        offsetxy = BOX_DIMENSIONS[0] - 0.20
        offsetz  = BOX_DIMENSIONS[2] - 0.15
        cmd = '-moveReconstructionRegion 0 "%s" "-%s" ' % (offsetxy, offsetz)  #
        cmd += '-selectTrianglesInsideReconReg '
        cmd += '-removeSelectedTriangles '
        cmd += '-moveReconstructionRegion 0 "-%s" 0 ' % (offsetxy * 2)  #
        cmd += '-selectTrianglesInsideReconReg '
        cmd += '-removeSelectedTriangles '
        cmd += '-moveReconstructionRegion "%s" "%s" 0 ' % (offsetxy, offsetxy)  #
        cmd += '-selectTrianglesInsideReconReg '
        cmd += '-removeSelectedTriangles '
        cmd += '-moveReconstructionRegion "-%s" 0 0 ' % (offsetxy * 2)  #
        cmd += '-selectTrianglesInsideReconReg '
        cmd += '-removeSelectedTriangles '
        cmd += '-moveReconstructionRegion "%s" 0 "%s" ' % (offsetxy, offsetz)  # return to center
        return cmd

    def _get_cmd_defineDistance(self):
        cmd = ''
        for index1, marker1 in enumerate(self.available_markers):
            for marker2 in [self.available_markers[index2] for index2 in range(index1 + 1, len(self.available_markers))]:
                if marker1 not in DISTANCES:
                    continue
                if marker2 not in DISTANCES[marker1]:
                    continue
                cmd += '-defineDistance "%s" "%s" "%s" "D%s%s" ' % (marker1, marker2, DISTANCES[marker1][marker2], marker1, marker2)
        return cmd

    def _get_cmd_new_scene(self):
        cmd = '-newScene '
        if self.create_mesh_from in ["projection", "all"]:
            cmd += '-addFolder "%s\\images\\projection" ' % self.source_folder
            cmd += '-selectAllImages '
            cmd += '-enableTexturingAndColoring false '
         
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
        models = []
        try:
            d = requests.get("http://%s/realityCaptureProcess" % SERVER).text
            data = json.loads(d)
            models = data["models"]
            if len(models) > 0:
                self._load_settings(data["markers"], data["box_dimensions"], data["pin"], data["calibration"])
        except Exception as e:
            print(e)
        if len(models) > 0:
            print("%s unprocessed models received from server" % len(models))
        return models

    def processing(self, shot_id, model_id):
        try:
            requests.get("http://%s/shots/%s/processing/%s" % (SERVER, shot_id, model_id))
        except:
            print("failed to reach server")

    def upload_model(self, shot_id, model_id, model_path):
        with open(model_path, 'rb') as f:
            print("Uploading model: %s" % model_path)
            try:
                requests.post("http://%s/shots/%s/upload/%s" % (SERVER, shot_id, model_id),files={'upload_file': f})
                print("Upload finished")
            except:
                print("failed to reach server while uploading")
                self.process_failed(shot_id, model_id)

    def upload_calibration_data(self):
        print("Uploading calibration")
        try:
            requests.post("http://%s/upload_calibration" % (SERVER), json= {"data": json.dumps(calibrationData.data)})
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

    def ensure_login(self):
        browser = webdriver.Chrome(executable_path=os.path.join(SCRIPT_DIR, "chromedriver.exe"))
        browser.get("https://www.capturingreality.com/My")
        time.sleep(2)
        try:
            browser.find_element_by_class_name('epic-login').click()
            time.sleep(5)
        except:
            pass

        while True:
            pagesource = browser.getPageSource()
            if pagesource.contains('Account Summary'):
                if pagesource.contains('Your PPI balance is'):   # PPI account, check balance
                    balance = 0
                    try:
                        balance = float(pagesource.split('Your current balance is ')[1].split("PPI")[0])
                        print("Your PPI balance is %s" % balance)
                        if balance < 300:
                            print("NOT ENOUGH CREDITS, charge your RealityCapture account")
                        else:
                            print("RealityCapture login successfull")
                            break
                    except Exception as e:
                        print("Failed to get balance from capturingreality.com/My")
                else:
                    print("RealityCapture login successfull")
                    break
            else:
                print("Use open browser window to login to capturingreality.com/My")
            time.sleep(5)
        browser.close()

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

    def _load_settings(self, markers_str, box_dimensions, pin, calibration ):
        global MARKERS
        global DISTANCES
        global BOX_DIMENSIONS
        global LICENSE_PIN

        try:
            calibrationData.data = json.loads(calibration)
        except:
            print("Failed to load calibration data")

        MARKERS = []
        DISTANCES = {}
        BOX_DIMENSIONS = box_dimensions
        LICENSE_PIN = pin

        for line in sorted(markers_str.split("\n")):
            line = line.split("#")[0].strip()
            if " - " not in line:
                continue
            try:
                m1, m2, distance = line.split(" - ")
                m1 = m1.strip()
                m2 = m2.strip()
                distance = float(distance.strip())
                MARKERS.append(m1)
                MARKERS.append(m2)
                if m1 not in DISTANCES:
                    DISTANCES[m1] = {}
                if m2 not in DISTANCES:
                    DISTANCES[m2] = {}
                DISTANCES[m1][m2] = distance
                DISTANCES[m2][m1] = distance
            except:
                pass
        MARKERS = list(set(MARKERS))
        print("%s Markers loaded from server" % len(MARKERS))


class Processing():
    def __init__(self):
        self._setup()

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

    def loop(self):
        api = WebAPI()
        while True:
            models = api.get_unprocessed_models()

            if len(models) == 0:
                print("Nothing to do, waiting some time")
                time.sleep(45)
                continue

            for model in models:
                api.processing(model["shot_id"], model["model_id"])
                self._clean_shot_dir()

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
                    create_textures=model["create_textures"]
                )

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
                    if DEBUG is False:
                        os.remove(model_result_path)
                else:
                    api.process_failed(model["shot_id"], model["model_id"])
                    if DEBUG is False and os.path.exists(shot_path):
                        print("Not caching shot %s" % shot_path )
                        try:
                            shutil.rmtree(shot_path)
                        except:
                            print("Failed to delete %s" % shot_path)


    def _clean_shot_dir(self):
        shots = []
        for path in glob.glob(os.path.join(CACHE_DIR, "*")):
            shots.append(path)
        shots.sort()
        while len(shots) > CACHE_SIZE:
            shutil.rmtree(shots[0])
            del shots[0]


calibrationData = CalibrationData()
processing = Processing()
processing.loop()