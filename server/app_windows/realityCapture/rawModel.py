import os

from app_windows.realityCapture.genericTask import GenericTask


class RawModel(GenericTask):
    def __init__(self, rc_job):
        super().__init__(rc_job)

    def run(self):
        force_reload = self.status != "idle"
        self.set_status("active")
        raw_exists_file = os.path.join(self.rc_job.workingdir, "%s.raw_exists" % self.rc_job.realityCapture_filename)
        rc_proj_file = os.path.join(self.rc_job.workingdir, "%s.rcproj" % self.rc_job.realityCapture_filename)
        if (not os.path.exists(raw_exists_file) or force_reload == True) and os.path.exists(rc_proj_file):
            cmd = self.rc_job._get_cmd_start()
            last_changed = os.path.getmtime(rc_proj_file)
            cmd += '-load "%s\\%s.rcproj" ' % (self.rc_job.workingdir, self.rc_job.realityCapture_filename)
            #cmd += '-moveReconstructionRegion "%s" "%s" "%s" ' % (self.box_center_correction[0], self.box_center_correction[1], self.box_center_correction[2] - (self.box_dimensions[2]/2)  )  #
            cmd += '-correctColors '
            if self.rc_job.reconstruction_quality == "preview":
                cmd += '-calculatePreviewModel '
            elif self.rc_job.reconstruction_quality == "high":
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
            cmd += '-save "%s\\%s.rcproj" ' % (self.rc_job.workingdir, self.rc_job.realityCapture_filename)
            cmd += '-clearCache '
            cmd += '-quit '
            self.rc_job._run_command(cmd, "create_raw_model")
            if last_changed != os.path.getmtime(rc_proj_file):
                with open(os.path.join(self.rc_job.workingdir, "%s.raw_exists" % self.rc_job.realityCapture_filename), "w") as f:
                    f.write("raw created")
                self.set_status("success")
            else:
                self.log.append("No model created, failed")
                self.set_status("failed")
        else:
            self.log.append("Using model from cache")
            self.set_status("success")


    def _get_cmd_cleanup_lower_region(self):
        offsetxy = self.rc_job.box_dimensions[0] - 0.20
        offsetz  = self.rc_job.box_dimensions[2] - 0.15
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