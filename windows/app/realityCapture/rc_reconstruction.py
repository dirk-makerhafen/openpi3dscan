import time

from pyhtmlgui import Observable
import os, glob

class RC_Reconstruction(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.rc_proj_file = parent.get_filepath("realityCapture.rcproj")
        self.raw_exists_file = parent.get_workfiles_path("raw.exists")
        self.status = "idle" # failed_ask_abort, repeat, success, failed

    def run(self):
        if os.path.exists(self.raw_exists_file):
            self.parent.addlog(["reconstruction", 'using raw model from cached project "%s"' % self.rc_proj_file])
            return True

        while not os.path.exists(self.raw_exists_file):
            self._run_rc()
            if os.path.exists(self.raw_exists_file):
                self.parent.addlog(["reconstruction", 'created RAW model in "%s"' % self.rc_proj_file])
                return True
            if not os.path.exists(self.raw_exists_file):
                self.parent.addlog( ["reconstruction", 'Raw model creation failed'])
                self.clear()
                self.set_status("failed_ask_abort")
                while self.status == "failed_ask_abort":
                    time.sleep(1)
                if self.status != "repeat":
                    break
                self.parent.addlog(["reconstruction", 'Repeating RAW model creation'])
        self.clear()
        return False

    def _run_rc(self, force_reload=False):
        self.parent.addlog(["reconstruction", 'Starting reconstruction'])
        cmd = self.parent.get_cmd_start()
        last_changed = os.path.getmtime(self.rc_proj_file)
        cmd += '-load "%s" ' % self.rc_proj_file
        cc = self.parent.rc_alignment.box_center_correction
        cmd += '-moveReconstructionRegion "%s" "%s" "%s" ' % (cc[0], cc[1], cc[2])  #
        cmd += '-correctColors '
        if self.parent.reconstruction_quality == "preview":
            cmd += '-calculatePreviewModel '
        elif self.parent.reconstruction_quality == "high":
            cmd += '-calculateHighModel '
        else:
            cmd += '-calculateNormalModel '

        for i in range(3):
            cmd += '-selectTrianglesOutsideReconReg '
            cmd += '-removeSelectedTriangles '
            cmd += self._get_cmd_cleanup_lower_region()
            cmd += '-rotateReconstructionRegion 0 0 30 '  #
        cmd += '-cleanModel '
        #cmd += '-smooth '
        cmd += '-simplify 4000000 '
        cmd += '-selectLargestModelComponent '
        cmd += '-invertTrianglesSelection '
        cmd += '-removeSelectedTriangles '
        cmd += '-renameSelectedModel "RAW" '
        for i in range(1, 19):
            cmd += '-selectModel "Model %s" ' % i
            cmd += '-deleteSelectedModel '
        cmd += '-save "%s" ' % (self.rc_proj_file)
        cmd += '-clearCache '
        cmd += '-quit '
        self.parent.addlog(["reconstruction", 'Command: %s' % cmd])
        self.parent.run_command(cmd, "create_raw_model")
        if last_changed != os.path.getmtime(self.rc_proj_file):
            with open(self.raw_exists_file, "w") as f:
                f.write("raw created")


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

    def clear(self):
        pass

    def set_status(self, status):
        if self.status != status:
            self.status = status
            self.notify_observers()