import os

from app_windows.realityCapture.genericTask import GenericTask

class Alignment(GenericTask):
    def __init__(self, rc_job, distances, ground_points):
        super().__init__(rc_job)
        self.distances = distances
        self.ground_points = ground_points
        self.alignments_were_recreated = False
        self.alignments = []
        self.box_center_correction = [0,0,0]

    def run(self):
        alignments_csv = self.get_path("%s_alignments.csv")
        rc_proj_file = os.path.join(self.rc_job.workingdir, "%s.rcproj" % self.rc_job.realityCapture_filename)
        raw_exists_file = os.path.join(self.rc_job.workingdir, "%s.raw_exists" % self.rc_job.realityCapture_filename)
        force_reload = self.status != "idle"
        self.set_status("active")

        if force_reload is True and os.path.exists(alignments_csv):
            self.log.append("Removing cached alignments file %s" % alignments_csv)
            os.remove(alignments_csv)

        if os.path.exists(alignments_csv):
            self._load_alignments_csv(alignments_csv)
            self.log.append("%s aligned cameras loaded from cache" % (len(self.alignments)))
            if len(self.alignments) > 30:
                self.set_status("success")
                return
            self.log.append("less than 30 aligned cameras found, must run alignment")

        if os.path.exists(alignments_csv):
            os.remove(alignments_csv)
        if os.path.exists(rc_proj_file):
            os.remove(rc_proj_file)
        if os.path.exists(raw_exists_file):
            os.remove(raw_exists_file)

        cmd = self._get_cmd_start()
        cmd += self._get_cmd_new_scene()
        cmd += '-align '
        cmd += '-detectMarkers "%s" ' % self.get_path("DetectMarkersParams.xml")
        cmd += self._get_cmd_defineDistance()
        cmd += '-selectMaximalComponent '
        cmd += '-detectFeatures '
        cmd += '-align '
        cmd += self._import_ground_plane()
        cmd += '-update '
        cmd += '-renameSelectedComponent "MAIN" '
        cmd += '-selectComponent "Component 0" '
        cmd += '-deleteSelectedComponent '
        cmd += '-selectComponent "MAIN" '
        cmd += '-setReconstructionRegion "%s" ' % self.get_path("box.rcbox")
        cmd += '-exportRegistration "%s" "%s" ' % (self.get_path("%s_alignments.csv"), self.get_path("exportRegistrationSettings.xml"))
        cmd += '-exportXMP "%s" ' %  self.get_path("xmp_settings.xml")
        cmd += '-save "%s\\%s.rcproj" ' % (self.rc_job.workingdir, self.rc_job.realityCapture_filename)
        cmd += '-quit '
        self._run_command(cmd, "load_alignments")

        self._load_alignments_csv(alignments_csv)
        self.log.append("%s cameras aligned" % (len(self.alignments)))

        if len(self.alignments) < 30:
            self.alignments_were_recreated = False
            self.log.append("less than 30 cameras aligned, failed")
            self.set_status("failed")
        else:
            self.alignments_were_recreated = True
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
        if len(self.alignments) > 2:
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

    def _import_ground_plane(self):
        ground_plane_file = self.get_path("%s_ground.csv")
        lines = ["%s, %s, %s, %s" % (g[0], g[1], g[2], g[3]) for g in self.ground_points if g[0] in self.rc_job.markers.available_markers  ]
        if len(lines) == 0:
            return ""

        with open(ground_plane_file, "w") as f:
            f.write("\n".join(lines))

        return '-importGroundControlPoints "%s" "%s" ' % (ground_plane_file, self.get_path("groundPlaneImport.xml"))