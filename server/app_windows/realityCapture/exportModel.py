import os, shutil
from pygltflib import GLTF2, TextureInfo
from app_windows.realityCapture.genericTask import GenericTask


class ExportModel(GenericTask):
    def __init__(self, rc_job):
        super().__init__(rc_job)
        self.export_model_path = os.path.join(self.rc_job.workingdir, self.rc_job.export_foldername,self.rc_job.export_filename)

        if self.rc_job.filetype != "rcproj":
            self.output_model_path = os.path.join(self.rc_job.workingdir, self.rc_job.export_foldername, self.rc_job.export_filename.replace(" ","_" if self.rc_job.filetype not in ["3mf","stl", ] else " "))


    def run(self):
        force_reload = self.status != "idle"
        self.set_status("active")
        if force_reload is True and os.path.exists(self.output_model_path):
            self.log.append("Removing cached export file")
            os.remove(self.output_model_path)

        if os.path.exists(self.output_model_path):
            if self.rc_job.compress_results is False and self.rc_job.filetype != "rcproj":
                self.rc_job.result_path = os.path.join(self.rc_job.workingdir, self.rc_job.export_foldername)
            self.log.append("Using from cache")
            self.set_status("success")
            return

        cmd = self._get_cmd_start()
        cmd += '-load "%s\\%s.rcproj" deleteAutosave ' % (self.rc_job.workingdir, self.rc_job.realityCapture_filename)
        cmd += '-selectComponent "MAIN" '
        cmd += '-selectModel "RAW" '
        if self.rc_job.export_quality == "high":
            cmd += '-simplify 4000000 '
        if self.rc_job.export_quality == "normal":
            cmd += '-simplify 1000000 '
        if self.rc_job.export_quality == "low":
            cmd += '-simplify 500000 '
        cmd += '-cleanModel '
        cmd += '-closeHoles '
        if self.rc_job.create_textures is True and self.rc_job.filetype not in ["stl"]:
            cmd += '-calculateTexture '
            cmd += '-calculateVertexColors '
        cmd += '-renameSelectedModel "EXPORT" '
        if self.rc_job.filetype == "rcproj":
            cmd += '-save "%s" ' % self.export_model_path
        else:
            cmd += '-exportModel "EXPORT" "%s" ' % self.export_model_path

        cmd += '-quit '
        self._run_command(cmd, "create_export_model")

        if not os.path.exists(self.output_model_path):
            self.log.append("Export model not created, %s not found." % self.output_model_path)
            self.set_status("failed")
            return

        if self.rc_job.fileextension == "glb" and self.rc_job.lit is False and self.rc_job.create_textures is True:
            glbf = GLTF2().load(self.output_model_path)
            glbf.materials[0].pbrMetallicRoughness.baseColorFactor = [0, 0, 0, 1]
            glbf.materials[0].emissiveFactor = [1, 1, 1]
            glbf.materials[0].emissiveTexture = TextureInfo(index=0)
            glbf.save(self.output_model_path)

        if self.rc_job.compress_results is False and self.rc_job.filetype != "rcproj":
            self.rc_job.result_path = os.path.join(self.rc_job.workingdir, self.rc_job.export_foldername)

        if os.path.exists("%s.rcInfo" % self.output_model_path):
            os.remove("%s.rcInfo" % self.output_model_path)
        self.log.append("Export model created")
        self.set_status("success")

