import os, time, glob, shutil
import shlex
import subprocess
from multiprocessing.pool import ThreadPool

from app_windows.realityCapture.genericTask import GenericTask
CREATE_NO_WINDOW = 0x08000000


class ResultsArchive(GenericTask):
    def __init__(self, rc_job):
        super().__init__(rc_job)

    def run(self):
        force_reload = self.status != "idle"
        self.set_status("active")

        output_model_path = os.path.join(self.rc_job.workingdir, self.rc_job.export_foldername, self.rc_job.export_filename.replace(" ","_" if self.rc_job.filetype not in ["3mf","stl", ] else " "))

        if force_reload is True and os.path.exists(output_model_path):
            self.log.append("Removing cached result %s" % output_model_path)
            os.remove(output_model_path)

        if self.rc_job.filetype == "rcproj":
            rcproj = os.path.join(self.rc_job.workingdir, "%s%s.rcproj" % (self.rc_job.realityCapture_filename, self.rc_job.quality_str))
            rcprojdir = os.path.join(self.rc_job.workingdir, "%s%s" % (self.rc_job.realityCapture_filename, self.rc_job.quality_str))
            imgdir = os.path.join(self.rc_job.workingdir, "images")
            target_dir = os.path.join(self.rc_job.workingdir, self.rc_job.export_foldername)
            try:
                shutil.rmtree(target_dir)
            except:
                print("Failed to delete %s" % target_dir)
            os.mkdir(target_dir)
            shutil.copy(rcproj, target_dir)
            shutil.copy("rc_rebase.exe", target_dir)
            shutil.copytree(rcprojdir, os.path.join(target_dir, self.rc_job.realityCapture_filename))
            shutil.copytree(imgdir, os.path.join(target_dir, "images"))

        model_file_zip = os.path.join(self.rc_job.workingdir, "%s.zip" % self.rc_job.export_foldername)
        if os.path.exists(model_file_zip):
            os.remove(model_file_zip)
        try:
            subprocess.check_output(shlex.split(
                "powershell -command \"Compress-Archive '%s\\*' '%s.zip'\"" % (self.rc_job.export_foldername, self.rc_job.export_foldername)
            ),shell=False, creationflags=CREATE_NO_WINDOW, cwd=self.rc_job.workingdir)
        except:
            pass


        if not os.path.exists(model_file_zip):
            self.log.append("Failed to create result zip file")
            self.set_status("failed")
        else:
            self.rc_job.result_file = model_file_zip
            self.set_status("success")
