from pyhtmlgui import Observable
import os, glob

class Subtask_Reconstruction(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.rc_proj_file = parent.get_filepath("realityCapture.rcproj")
        self.raw_exists_file = parent.get_workfiles_path("raw.exists")

    def create_raw_model(self, force_reload=False):
        if (not os.path.exists(raw_exists_file) or force_reload == True) and os.path.exists(rc_proj_file):
            cmd = self.parent.get_cmd_start()
            last_changed = os.path.getmtime(rc_proj_file)
            cmd += '-load "%s" ' % self.rc_proj_file
            cmd += '-moveReconstructionRegion "%s" "%s" "%s" ' % (self.parent.subtask_alignment.box_center_correction[0], self.parent.subtask_alignment.box_center_correction[1],
            self.parent.subtask_alignment.box_center_correction[2] - (self.parent.box_dimensions[2] / 2))  #
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
            # cmd += '-smooth '
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
            self.parent.run_command(cmd, "create_raw_model")
            if last_changed != os.path.getmtime(self.rc_proj_file):
                with open(self.raw_exists_file, "w") as f:
                    f.write("raw created")
            else:
                print("Failed to create raw model, no changes in rcproj")
        else:
            print("raw model already exists")

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
