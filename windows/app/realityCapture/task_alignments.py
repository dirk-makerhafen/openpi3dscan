from pyhtmlgui import Observable
import os

class Subtask_Alignment(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.alignments = []
        self.box_center_correction = [0,0,0]
        self.alignments_csv = parent.get_workfiles_path("alignments.cvs")
        self.rc_proj_file = parent.get_filepath("realityCapture.rcproj")

    def run(self):
        self._load_alignments_csv()
        if len(self.alignments) < 10:
            self._create_alignments()

        if len(self.alignments) > 10:
            self.parent.subtask_xmp.run()

        # xport xmp
        # list cameras with wrong focal distance
        # for each wrong camera:
        #  if has calibration data:
        #    set calibrationdata to fixed
        # write calibration data as xmp
        # if datachanged:
        #  self._create_alignments()
        # if new alignemnts created:
        #  addto calibration
        print("%s alignments loaded" % len(self.alignments))


    def _create_alignments(self):
        while len(self.alignments) < 10:
            self.clear()
            self._run_rc()
            self._load_alignments_csv()
            if len(self.alignments) < 10:
                self.clear()
                print("No alignments ask continue, break?")
                result = False
                if result == True:
                    break

    def _run_rc(self):
        cmd = self.parent.get_cmd_start()
        cmd += self.parent.get_cmd_new_scene()
        cmd += '-align '
        cmd += '-detectMarkers "%s\\tmp\\DetectMarkersParams.xml" ' % self.parent.source_path
        for m1m2d in self.parent.subtask_markers.get_available_distances():
            marker1, marker2, distance = m1m2d
            cmd += '-defineDistance "%s" "%s" "%s" "D%s%s" ' % (marker1, marker2, distance, marker1, marker2)
        cmd += '-selectMaximalComponent '
        cmd += '-align '
        cmd += '-renameSelectedComponent "MAIN" '
        cmd += '-selectComponent "Component 0" '
        cmd += '-deleteSelectedComponent '
        cmd += '-selectComponent "MAIN" '
        cmd += '-setReconstructionRegion "%s\\tmp\\box.rcbox" ' % self.parent.source_path
        cmd += '-getLicense "%s" ' % self.parent.pin
        cmd += '-exportRegistration "%s" "%s\\tmp\\exportRegistrationSettings.xml" ' % self.parent.source_path
        cmd += '-save "%s" ' % (self.rc_proj_file)
        cmd += '-quit '
        self.parent.run_command(cmd, "load_alignments")

    def _load_alignments_csv(self):
        self.alignments = []
        if os.path.exists(self.alignments_csv):
            with open(self.alignments_csv, "r") as f:
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

    def clear(self):
        if os.path.exists(self.alignments_csv):
            os.remove(self.alignments_csv)
        if os.path.exists(self.rc_proj_file):
            os.remove(self.rc_proj_file)
        self.alignments = []
