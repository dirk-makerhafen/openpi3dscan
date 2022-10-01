import glob
import random
import re
import shlex
import shutil
import subprocess
import time
from multiprocessing.pool import ThreadPool

from pyhtmlgui import Observable
import os, json

from .rc_files import DetectMarkersParams_xml, box_rcbox, ExportRegistrationSettings_xml, XMPSettings_xml, RCEXE
from .data_calibration import CalibrationData
from .rc_markers import RC_Markers
from .rc_alignments import RC_Alignment
from .rc_reconstruction import RC_Reconstruction
from .rc_export import RC_Export
from .data_xmp import XMPData


class RealityCapture():
    def __init__(self, source_folder, shot_name, filetype, reconstruction_quality, export_quality, create_mesh_from, create_textures,calibrationData, markers, distances, pin, box_dimensions, debug=False):
        self.source_folder = os.path.abspath(source_folder)
        self.workfiles_path = os.path.join(self.source_folder, "tmp")
        self.images_path = os.path.join(self.source_folder, "images")
        if not os.path.exists(os.path.join(self.images_path, "normal")):
            self.images_path = os.path.join(self.source_folder)
        self.shot_name = shot_name
        if self.shot_name == "":
            self.shot_name = self.source_folder.split('\\')[-1]
        self.shot_name = self._clean_shot_name(self.shot_name)
        self.filetype = filetype
        self.fileextension = filetype
        if self.fileextension in ["gif", "webp"]:
            self.fileextension = "glb"
        self.reconstruction_quality = reconstruction_quality
        self.export_quality = export_quality
        self.create_mesh_from = create_mesh_from
        self.create_textures = create_textures
        self.pin = pin
        self.box_dimensions = box_dimensions
        self.debug = debug

        self.reconstruction_quality_str = self.reconstruction_quality[0].upper()
        self.quality_str = self.export_quality[0].upper()
        self.create_mesh_from_str = create_mesh_from[0].upper()
        self.create_textures_str = "T" if create_textures is True else ""
        self.export_filename = "%s_%s%s%s%s.%s" % ( self.shot_name, self.reconstruction_quality_str, self.quality_str, self.create_mesh_from_str, self.create_textures_str, self.fileextension)
        self.export_foldername = "%s_%s%s%s%s_%s" % ( self.shot_name, self.reconstruction_quality_str, self.quality_str, self.create_mesh_from_str, self.create_textures_str, self.filetype)

        self.calibrationdata = CalibrationData(self, calibrationData)
        self.xmpdata = XMPData(self)
        self.rc_markers = RC_Markers(self, markers, distances)
        self.rc_alignment = RC_Alignment(self)
        self.rc_reconstruction = RC_Reconstruction(self)
        self.rc_export = RC_Export(self)
        self.logs = []

    def addlog(self, log):
        self.logs.insert(0, log)

    def get_source_path(self, basename):
        return os.path.join(self.source_folder, "%s%s%s_%s" % (self.reconstruction_quality_str, self.create_mesh_from_str, self.create_textures_str, basename))

    def get_workfiles_path(self, basename):
        return os.path.join(self.workfiles_path, "%s%s%s_%s" % (self.reconstruction_quality_str, self.create_mesh_from_str, self.create_textures_str, basename))

    def process(self):
        self.prepare_folders()
        #first_time_calibration = len(calibrationData.data) == 0

        if self.rc_markers.run() is False:
            return None

        if self.calibrationdata.write_as_xmp() is False:
            return None

        if self.rc_alignment.run() is False:
            return None

        if self.rc_reconstruction.run() is False:
            return None

        if self.rc_export.run() is False:
            return None

        if self.rc_alignment.alignments_recreated is True:
            if self.xmpdata.run() is False:
                return None
            self.calibrationdata.add_from_xmp(self.xmpdata.xmp_data)

        if self.debug is False:
            try:
                shutil.rmtree(os.path.join(self.source_folder, self.export_foldername))
            except:
                print("Failed to delete %s" % os.path.join(self.source_folder, self.export_foldername))

        return self.model_path

    def prepare_folders(self):
        if not os.path.exists(os.path.join(self.source_folder, "tmp")):
            os.mkdir(os.path.join(self.source_folder, "tmp"))
        with open(os.path.join(self.source_folder, "tmp", "DetectMarkersParams.xml"), "w") as f:
            f.write(DetectMarkersParams_xml)
        with open(os.path.join(self.source_folder, "tmp", "box.rcbox"), "w") as f:
            f.write(box_rcbox % (round(self.box_dimensions[0], 2), round(self.box_dimensions[1], 2), round(self.box_dimensions[2], 2),
                                 round(self.box_dimensions[2] / 2, 2)))
        with open(os.path.join(self.source_folder, "tmp", "exportRegistrationSettings.xml"), "w") as f:
            f.write(ExportRegistrationSettings_xml)
        with open(os.path.join(self.source_folder, "tmp", "xmp_settings.xml"), "w") as f:
            f.write(XMPSettings_xml)
        for mode in ["normal", "projection"]:
            for file in glob.glob(os.path.join(os.path.join(self.images_path , mode), "*.jpg")):
                if os.path.getsize(file) < 100000:
                    os.remove(file)
        try:
            os.mkdir(os.path.join(self.source_folder, self.export_foldername))
        except:
            pass
        self.xmpdata.clear()


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

    def get_cmd_new_scene(self):
        cmd = '-newScene '
        if self.create_mesh_from in ["projection", "all"]:
            cmd += '-addFolder "%s\\projection" ' % self.images_path
            cmd += '-selectAllImages '
            cmd += '-enableTexturingAndColoring false '

        if self.create_mesh_from in ["normal", "all"] or self.create_textures is True:
            cmd += '-addFolder "%s\\normal" ' % self.images_path
            cmd += '-invertImageSelection '
            if self.create_mesh_from == "projection":
                cmd += '-enableMeshing false '  # don't use normal images for mesh
        cmd += '-deselectAllImages '
        return cmd

    def get_cmd_start(self):
        cmd = '"%s" ' % RCEXE
        # cmd += '-silent "%s\\crash_report.txt" ' % self.source_folder
        # cmd += '-set "appQuitOnError=true" '
        return cmd

    def run_command(self, cmd, name):
        print("Next Command: %s" % name)
        print(cmd)
        s = time.time()
        subprocess.run(shlex.split(cmd))
        print("Command '%s' took %s seconds" % (name, int(time.time() - s)))
