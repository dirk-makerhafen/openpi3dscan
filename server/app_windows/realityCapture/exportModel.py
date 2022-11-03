import os, shutil
from pygltflib import GLTF2, TextureInfo
from pyhtmlgui import Observable


class ExportModel(Observable):
    def __init__(self, rc_job):
        super().__init__()
        self.rc_job = rc_job
        self.output_model_path = os.path.join(self.rc_job.source_folder, self.rc_job.export_foldername, self.rc_job.export_filename.replace(" ","_" if self.rc_job.filetype not in ["3mf","stl", ] else " "))
        self.status = "idle"

    def set_status(self, new_status):
        if self.status == new_status:
            return
        self.status = new_status
        self.notify_observers()

    def create(self, force_reload=False):

        if force_reload is True and os.path.exists(self.output_model_path):
            os.remove(self.output_model_path)

        if not os.path.exists(self.output_model_path):
            cmd = self.rc_job._get_cmd_start()
            cmd += '-load "%s\\%s.rcproj" ' % (self.rc_job.source_folder, self.rc_job.realityCapture_filename)
            cmd += '-selectComponent "MAIN" '
            cmd += '-selectModel "RAW" '
            if self.rc_job.quality == "high":
                cmd += '-simplify 4000000 '
            if self.rc_job.quality == "normal":
                cmd += '-simplify 1000000 '
            if self.rc_job.quality == "low":
                cmd += '-simplify 500000 '
            cmd += '-cleanModel '
            if self.rc_job.create_textures is True:
                cmd += '-calculateTexture '
                cmd += '-calculateVertexColors '
            cmd += '-renameSelectedModel "EXPORT" '
            cmd += '-getLicense "%s" ' % self.rc_job.pin
            if self.rc_job.filetype != "rcproj":
                cmd += '-exportModel "EXPORT" "%s\\%s\\%s" ' % (self.rc_job.source_folder, self.rc_job.export_foldername, self.rc_job.export_filename)
            else:
                cmd += '-save "%s\\%s%s.rcproj" ' % (self.rc_job.source_folder, self.rc_job.realityCapture_filename, self.rc_job.quality_str)
            cmd += '-quit '
            self.rc_job._run_command(cmd, "create_export_model")

            if not os.path.exists(self.output_model_path):
                print("%s model not found, error" % self.output_model_path)
                return

            if self.rc_job.fileextension == "glb" and self.rc_job.lit is False:
                glbf = GLTF2().load(self.output_model_path)
                glbf.materials[0].pbrMetallicRoughness.baseColorFactor = [0, 0, 0, 1]
                glbf.materials[0].emissiveFactor = [1, 1, 1]
                glbf.materials[0].emissiveTexture = TextureInfo(index=0)
                glbf.save(self.output_model_path)






    def creasate(self, force_reload=False):
        self.output_model_path = os.path.join(self.rc_job.source_folder, self.rc_job.export_foldername, self.rc_job.export_filename.replace(" ","_" if self.rc_job.filetype not in ["3mf","stl", ] else " "))

        if force_reload is True and os.path.exists(output_model_path):
            os.remove(output_model_path)



        if self.rc_job.filetype == "rcproj":
            rcproj = os.path.join(self.rc_job.source_folder, "%s.rcproj" % self.rc_job.realityCapture_filename)
            rcprojdir = os.path.join(self.rc_job.source_folder, self.rc_job.realityCapture_filename)
            imgdir = os.path.join(self.rc_job.source_folder, "images")
            target_dir = os.path.join(self.rc_job.source_folder, self.rc_job.export_foldername)
            try:
                shutil.rmtree(target_dir)
            except:
                print("Failed to delete %s" % target_dir)
            os.mkdir(target_dir)
            shutil.copy(rcproj, target_dir)
            shutil.copy("rc_rebase.exe", target_dir)
            shutil.copytree(rcprojdir, os.path.join(target_dir, self.rc_job.realityCapture_filename))
            shutil.copytree(imgdir, os.path.join(target_dir, "images"))

        elif not os.path.exists(output_model_path):
            cmd = self.rc_job._get_cmd_start()
            cmd += '-load "%s\\%s.rcproj" ' % (self.rc_job.source_folder, self.rc_job.realityCapture_filename)
            cmd += '-selectComponent "MAIN" '
            cmd += '-selectModel "RAW" '
            if self.rc_job.quality == "high":
                cmd += '-simplify 4000000 '
            if self.rc_job.quality == "normal":
                cmd += '-simplify 1000000 '
            if self.rc_job.quality == "low":
                cmd += '-simplify 500000 '
            cmd += '-cleanModel '
            if self.rc_job.create_textures is True:
                cmd += '-calculateTexture '
                cmd += '-calculateVertexColors '
            cmd += '-renameSelectedModel "EXPORT" '
            cmd += '-getLicense "%s" ' % self.rc_job.pin
            cmd += '-exportModel "EXPORT" "%s\\%s\\%s" ' % (self.rc_job.source_folder, self.rc_job.export_foldername, self.rc_job.export_filename)
            cmd += '-quit '
            self.rc_job._run_command(cmd, "create_export_model")

            if not os.path.exists(output_model_path):
                print("%s model not found, error" % output_model_path)
                return

            if self.rc_job.fileextension == "glb" and self.rc_job.lit is False:
                glbf = GLTF2().load(output_model_path)
                glbf.materials[0].pbrMetallicRoughness.baseColorFactor = [0, 0, 0, 1]
                glbf.materials[0].emissiveFactor = [1, 1, 1]
                glbf.materials[0].emissiveTexture = TextureInfo(index=0)
                glbf.save(output_model_path)


        if self.rc_job.filetype == "gif":
            self.model_path = self.rc_job.animation.create(output_model_path, "gif")

        elif self.rc_job.filetype == "webp":
            self.model_path = self.animation.create(output_model_path, "webp")

        else:
            model_file_zip = os.path.join(self.rc_job.source_folder, "%s.zip" % self.rc_job.export_foldername)
            if os.path.exists(model_file_zip):
                os.remove(model_file_zip)
            os.system("cd \"%s\" & powershell -command \"Compress-Archive '%s\\*' '%s.zip'\"" % (self.rc_job.source_folder, self.rc_job.export_foldername, self.rc_job.export_foldername))
            if not os.path.exists(model_file_zip):
                print("Failed to create model zip")
                self.model_path = None
            else:
                print("Model zip created")
                self.model_path = model_file_zip

