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
from .data_xmp import XMPData





class Step_Base(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def prepare(self):
        raise NotImplementedError()

    def run(self):
        raise NotImplementedError()

class Step_PrepareFolder(Step_Base):
    def __init__(self, parent):
        super().__init__(parent)

    def foo(self):
        if not os.path.exists(os.path.join(self.parent.source_folder, "tmp")):
            os.mkdir(os.path.join(self.parent.source_folder, "tmp"))
        with open(os.path.join(self.parent.source_folder, "tmp", "DetectMarkersParams.xml"), "w") as f:
            f.write(DetectMarkersParams_xml)
        with open(os.path.join(self.parent.source_folder, "tmp", "box.rcbox"), "w") as f:
            f.write(box_rcbox % (round(self.box_dimensions[0], 2), round(self.box_dimensions[1], 2), round(self.box_dimensions[2], 2),round(self.box_dimensions[2] / 2, 2)))
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

class Step_NewSceneLoadImages(Step_Base):
    def __init__(self, parent):
        super().__init__(parent)
        self.rc_command  = '-newScene '
        if self.parent.create_mesh_from in ["projection", "all"]:
            self.rc_command  += '-addFolder "%s\\projection" ' % self.parent.images_path
            self.rc_command  += '-selectAllImages '
            self.rc_command  += '-enableTexturingAndColoring false '
            self.rc_command  += '-enableColorNormalization false '

        if self.parent.create_mesh_from in ["normal", "all"] or self.parent.create_textures is True:
            self.rc_command  += '-addFolder "%s\\normal" ' % self.parent.images_path
            self.rc_command  += '-invertImageSelection '
            if self.parent.create_mesh_from == "projection":
                self.rc_command  += '-enableMeshing false '  # don't use normal images for mesh
        self.rc_command  += '-deselectAllImages '

    def run(self):
        self.parent.run_command(self.rc_command)

class Step_AlignImages(Step_Base):
    def __init__(self, parent):
        super().__init__(parent)
        self.rc_command  = '-align '
    def run(self):
        self.parent.run_command(self.rc_command)

class Step_DetectMarkers(Step_Base):
    def __init__(self, parent):
        super().__init__(parent)
        self.markers_csv = parent.get_workfiles_path("markers.cvs")
        self.rc_command = '-detectMarkers "%s\\tmp\\DetectMarkersParams.xml" ' % self.parent.source_path
        self.rc_command += '-getLicense "%s" ' % self.parent.pin
        self.rc_command += '-exportControlPointsMeasurements "%s" ' % (self.markers_csv)

    def run(self):
        self.parent.run_command(self.rc_command)
        self._load_markers_csv()

    def _load_markers_csv(self):
        markers = set()
        if os.path.exists(self.markers_csv):
            self.parent.addlog(["markers", 'Loading markers from "%s"' % self.markers_csv])
            with open(self.markers_csv, "r") as f:
                for line in f.read().split("\n"):
                    if line.startswith("#") or len(line) < 10:
                        continue
                    markers.add(line.split(",")[1].strip())
        else:
            self.parent.addlog(["markers", 'No markers file exists at "%s"' % self.markers_csv])
        self.parent.available_markers = list(markers)

class Step_SetDistancesAndRealign(Step_Base):
    def __init__(self, parent):
        super().__init__(parent)
        self.rc_command = ""

    def prepare(self):
        self.rc_command = ""
        for m1m2d in self.parent.get_available_distances():
            marker1, marker2, distance = m1m2d
            self.rc_command += '-defineDistance "%s" "%s" "%s" "D%s%s" ' % (marker1, marker2, distance, marker1, marker2)
        self.rc_command += '-selectMaximalComponent '
        self.rc_command += "-align "
        self.rc_command += '-renameSelectedComponent "MAIN" '
        self.rc_command += '-selectComponent "Component 0" '
        self.rc_command += '-deleteSelectedComponent '

    def run(self):
        self.parent.run_command(self.rc_command)

class Step_ExportAndLoadAlignments(Step_Base):
    def __init__(self, parent):
        super().__init__(parent)
        self.rc_command = ""
        self.rc_command += '-selectComponent "MAIN" '
        self.rc_command += '-getLicense "%s" ' % self.parent.pin
        self.rc_command += '-exportRegistration "%s" "%s\\tmp\\exportRegistrationSettings.xml" ' % self.parent.source_path

    def run(self):
        self.parent.run_command(self.rc_command)
        self._load_alignments_csv()

    def _load_alignments_csv(self):
        self.alignments = []
        if os.path.exists(self.alignments_csv):
            self.parent.addlog(["alignments", 'Loading alignments from "%s"' % self.alignments_csv])
            with open(self.alignments_csv, "r") as f:
                for line in f.read().split("\n"):
                    if line.startswith("#") or len(line) < 10:
                        continue
                    al = line.split(",")
                    al = [al[0], float(al[1]), float(al[2]), float(al[3]), None]
                    self.alignments.append(al)
        else:
            self.parent.addlog(["alignments", 'No alignments file exists at "%s"' % self.alignments_csv])

        c_x = (max([x[1] for x in self.alignments]) + min([x[1] for x in self.alignments])) / 2
        c_y = (max([x[2] for x in self.alignments]) + min([x[2] for x in self.alignments])) / 2
        c_z = (max([x[3] for x in self.alignments]) + min([x[3] for x in self.alignments])) / 2

        #avg_x = sum([x[1] for x in self.alignments]) / len(self.alignments)
        #avg_y = sum([x[2] for x in self.alignments]) / len(self.alignments)
        #avg_z = sum([x[3] for x in self.alignments]) / len(self.alignments)
        # print("avg", avg_x, avg_y, avg_z)
        c_z = c_z - (self.parent.box_dimensions[2] / 2)
        self.box_center_correction = [c_x, c_y, c_z]
        self.parent.addlog(["alignments", "Box center corrections: %s,%s,%s" % (c_x, c_y, c_z)])

class Step_SetReconstructionRegion(Step_Base):
    def __init__(self, parent):
        super().__init__(parent)
        cc = self.parent.box_center_correction
        self.rc_command = ""
        self.rc_command += '-setReconstructionRegion "%s\\tmp\\box.rcbox" ' % self.parent.source_path
        self.rc_command += '-moveReconstructionRegion "%s" "%s" "%s" ' % (cc[0], cc[1], cc[2])  #

    def run(self):
        self.parent.run_command(self.rc_command)

class Step_CorrectColors(Step_Base):
    def __init__(self, parent):
        super().__init__(parent)
        self.rc_command = ""
        self.rc_command += '-correctColors '

    def run(self):
        self.parent.run_command(self.rc_command)

class Step_CalculateModel(Step_Base):
    def __init__(self, parent):
        super().__init__(parent)
        self.rc_command = ""
        if self.parent.reconstruction_quality == "preview":
            self.rc_command += '-calculatePreviewModel '
        elif self.parent.reconstruction_quality == "high":
            self.rc_command += '-calculateHighModel '
        else:
            self.rc_command += '-calculateNormalModel '

    def run(self):
        self.parent.run_command(self.rc_command)

class Step_CleanupReconstructionRegion(Step_Base):
    def __init__(self, parent):
        super().__init__(parent)
        self.rc_command = ""

        for i in range(3):
            self.rc_command += '-selectTrianglesOutsideReconReg '
            self.rc_command += '-removeSelectedTriangles '
            self.rc_command += self._get_cmd_cleanup_lower_region()
            self.rc_command += '-rotateReconstructionRegion 0 0 30 '  #

    def run(self):
        self.parent.run_command(self.rc_command)

    def _get_cmd_cleanup_lower_region(self):
        offsetxy = self.parent.box_dimensions[0] - 0.20
        offsetz = self.parent.box_dimensions[2] - 0.15
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

class Step_CleanupModel(Step_Base):
    def __init__(self, parent):
        super().__init__(parent)
        self.rc_command = ""
        self.rc_command += '-cleanModel '
        # cmd += '-smooth '
        self.rc_command += '-simplify 4000000 '
        self.rc_command += '-selectLargestModelComponent '
        self.rc_command += '-invertTrianglesSelection '
        self.rc_command += '-removeSelectedTriangles '
        self.rc_command += '-renameSelectedModel "RAW" '
    def run(self):
        self.parent.run_command(self.rc_command)

class Step_ExportXMPFilesAndSave(Step_Base):
    def __init__(self, parent):
        super().__init__(parent)
        self.rc_command = ""
        self.rc_command  += '-exportXMP "%s\\tmp\\xmp_settings.xml" ' % self.parent.source_folder
        self.rc_command += '-save "%s" ' % (self.rc_proj_file)

    def run(self):
            self.parent.run_command(self.rc_command)

class Step_UpdateCalibrationFromXMP(Step_Base):
    def __init__(self, parent):
        super().__init__(parent)
        self.rc_command = ""

    def run(self):
        self.parent.run_command(self.rc_command)

class Step_LoadProject(Step_Base):
    def __init__(self, parent):
        super().__init__(parent)
        self.rc_command = ""
        self.rc_command += '-load "%s" deleteAutosave ' % self.rc_proj_file

    def run(self):
        self.parent.run_command(self.rc_command)

class Step_CreateExportModel(Step_Base):
    def __init__(self, parent):
        super().__init__(parent)
        self.rc_command = ""
        self.rc_command += '-selectComponent "MAIN" '
        self.rc_command += '-selectModel "RAW" '
        if self.parent.export_quality == "high":
            self.rc_command += '-simplify 4000000 '
        if self.parent.export_quality == "normal":
            self.rc_command += '-simplify 1000000 '
        if self.parent.export_quality == "low":
            self.rc_command += '-simplify 500000 '
        self.rc_command += '-cleanModel '
        if self.parent.create_textures is True:
            self.rc_command += '-calculateTexture '
            self.rc_command += '-calculateVertexColors '
        self.rc_command += '-renameSelectedModel "EXPORT" '
        self.rc_command += '-exportModel "EXPORT" "%s\\%s\\%s" ' % (self.parent.source_folder, self.parent.export_foldername, self.parent.export_filename)

class Step_ExportRCPROJ(Step_Base): pass
class Step_ZipResultModel(Step_Base): pass
class Step_CreateImages(Step_Base): pass
class Step_CreateAnimation(Step_Base): pass








class RealityCapture():
    def __init__(self, source_folder, shot_name, filetype, reconstruction_quality, export_quality, create_mesh_from, create_textures, calibrationData, markers, distances, pin, box_dimensions, debug=False):
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
        self.logs = []
        self.steps = []
        self.automatic = True
        self.run_next_step = True
        self.status = "active"

    def setup_steps(self):
        self.steps = []
        if True:  # does not exist:
            self.steps.append(Step_PrepareFolder(self))
            self.steps.append(Step_NewSceneLoadImages(self))
            self.steps.append(Step_AlignImages(self))
            self.steps.append(Step_DetectMarkers(self))
            self.steps.append(Step_SetDistancesAndRealign(self))
            self.steps.append(Step_ExportAndLoadAlignments(self))
            self.steps.append(Step_SetReconstructionRegion(self))
            self.steps.append(Step_CorrectColors(self))
            self.steps.append(Step_CalculateModel(self))
            self.steps.append(Step_CleanupReconstructionRegion(self))
            self.steps.append(Step_CleanupModel(self))
            self.steps.append(Step_ExportXMPFilesAndSave(self))
            self.steps.append(Step_UpdateCalibrationFromXMP(self))

        if self.filetype == "rcproj":
            self.steps.append(Step_ExportRCPROJ(self))

        elif not os.path.exists(output_model_path):
            self.steps.append(Step_LoadProject(self))
            self.steps.append(Step_CreateExportModel(self))

        if self.filetype == "gif":
            self.steps.append(Step_CreateImages(self))
            self.steps.append(Step_CreateAnimation(self, "gif"))
        elif self.filetype == "webp":
            self.steps.append(Step_CreateImages(self))
            self.steps.append(Step_CreateAnimation(self, "webp"))
        else:
            self.steps.append(Step_ZipResultModel(self))

    def run(self):
        current_step_index = 0
        while current_step_index < len(self.steps):
            current_step = self.steps[current_step_index]
            while self.automatic is False and self.status == "active" and self.run_next_step is False:
                time.sleep(1)
            if self.status != "active":
                break
            current_step.run()
            current_step_index += 1

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


    def get_available_distances(self):
        for index1, marker1 in enumerate(self.available_markers):
            for marker2 in [self.available_markers[index2] for index2 in range(index1 + 1, len(self.available_markers))]:
                if marker1 not in self.parent.distances:
                    continue
                if marker2 not in self.parent.distances[marker1]:
                    continue
                yield [marker1, marker2, self.parent.distances[marker1][marker2]]
