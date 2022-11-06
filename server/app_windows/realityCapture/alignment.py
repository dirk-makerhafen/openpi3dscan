import os

from app_windows.realityCapture.genericTask import GenericTask


class Alignment(GenericTask):
    def __init__(self, rc_job, distances):
        super().__init__(rc_job)
        self.distances = distances
        self.alignments_were_recreated = False
        self.alignments = []
        self.box_center_correction = [0,0,0]

    def run(self):
        alignments_csv = self.rc_job.get_path("%s_alignments.csv")
        rc_proj_file = os.path.join(self.rc_job.workingdir, "%s.rcproj" % self.rc_job.realityCapture_filename)
        raw_exists_file = os.path.join(self.rc_job.workingdir, "%s.raw_exists" % self.rc_job.realityCapture_filename)
        force_reload = self.status != "idle"
        self.set_status("active")

        if force_reload is True and os.path.exists(alignments_csv):
            self.log.append("Removing cached alignments file %s" % alignments_csv)
            os.remove(alignments_csv)

        if os.path.exists(alignments_csv):
            self._load_alignments_csv(alignments_csv)
            self.log.append("%s aligned cameras loaded from cache %s" % (len(self.alignments), alignments_csv))

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
            cmd += '-detectMarkers "%s" ' % self.rc_job.get_path("DetectMarkersParams.xml")
            cmd += self._get_cmd_defineDistance()
            cmd += '-selectMaximalComponent '
            cmd += '-align '
            cmd += '-renameSelectedComponent "MAIN" '
            cmd += '-selectComponent "Component 0" '
            cmd += '-deleteSelectedComponent '
            cmd += '-selectComponent "MAIN" '
            cmd += '-setReconstructionRegion "%s" ' % self.rc_job.get_path("box.rcbox")
            cmd += '-getLicense "%s" ' % self.rc_job.pin
            cmd += '-exportRegistration "%s" "%s" ' % (self.rc_job.get_path("%s_alignments.csv"), self.rc_job.get_path("exportRegistrationSettings.xml"))
            cmd += '-save "%s\\%s.rcproj" ' % (self.rc_job.workingdir, self.rc_job.realityCapture_filename)
            cmd += '-quit '
            self.rc_job._run_command(cmd, "load_alignments")
            if os.path.exists(self.rc_job.get_path("%s_alignments.csv")):
                self.alignments_were_recreated = True
            self._load_alignments_csv(alignments_csv)
            self.log.append("%s aligned cameras detected" % (len(self.alignments)))

        if len(self.alignments) < 30:
            self.log.append("less than 30 aligned cameras detected, failed")
            self.set_status("failed")
        else:
            self.set_status("success")

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
        c_x = (max([x[1] for x in self.alignments]) + min([x[1] for x in self.alignments])) / 2
        c_y = (max([x[2] for x in self.alignments]) + min([x[2] for x in self.alignments])) / 2
        c_z = (max([x[3] for x in self.alignments]) + min([x[3] for x in self.alignments])) / 2

        avg_x = sum([x[1] for x in self.alignments]) / len(self.alignments)
        avg_y = sum([x[2] for x in self.alignments]) / len(self.alignments)
        avg_z = sum([x[3] for x in self.alignments]) / len(self.alignments)
        # print("avg", avg_x, avg_y, avg_z)
        self.box_center_correction = [c_x, c_y, c_z]


    def _get_cmd_defineDistance(self):
        cmd = ''
        for index1, marker1 in enumerate(self.rc_job.markers.available_markers):
            for marker2 in [self.rc_job.markers.available_markers[index2] for index2 in range(index1 + 1, len(self.rc_job.markers.available_markers))]:
                if marker1 not in self.distances:
                    continue
                if marker2 not in self.distances[marker1]:
                    continue
                cmd += '-defineDistance "%s" "%s" "%s" "D%s%s" ' % (marker1, marker2, self.distances[marker1][marker2], marker1, marker2)
        return cmd
