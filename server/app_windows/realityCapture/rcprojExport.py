import os, time, glob, shutil
import shlex
import subprocess
from multiprocessing.pool import ThreadPool

from app_windows.files.externalFiles import ExternalFilesInstance
from app_windows.realityCapture.genericTask import GenericTask


class RcprojExport(GenericTask):
    def __init__(self, rc_job):
        super().__init__(rc_job)

    def run(self):
        force_reload = self.status != "idle"
        self.set_status("active")

        target_dir = os.path.join(self.rc_job.workingdir, self.rc_job.export_foldername)

        if self.rc_job.filetype == "rcproj":
            rcproj = os.path.join(self.rc_job.workingdir, "%s%s.rcproj" % (self.rc_job.realityCapture_filename, self.rc_job.quality_str))
            rcprojdir = os.path.join(self.rc_job.workingdir, "%s%s" % (self.rc_job.realityCapture_filename, self.rc_job.quality_str))
            imgdir = os.path.join(self.rc_job.workingdir, "images")
            if os.path.exists(target_dir):
                try:
                    shutil.rmtree(target_dir)
                except:
                    print("Failed to delete %s" % target_dir)
            os.mkdir(target_dir)
            shutil.copy(rcproj, target_dir)
            shutil.copy(ExternalFilesInstance().rc_rebase_exe, target_dir)
            shutil.copytree(rcprojdir, os.path.join(target_dir, self.rc_job.realityCapture_filename))
            shutil.copytree(imgdir, os.path.join(target_dir, "images"))

        if not os.path.exists(target_dir):
            if self.rc_job.compress_results is False:
                self.rc_job.result_path = target_dir
            self.log.append("Failed to export rcproj")
            self.set_status("failed")
        else:
            self.set_status("success")
