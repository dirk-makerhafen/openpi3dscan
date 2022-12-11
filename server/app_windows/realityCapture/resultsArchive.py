import os, time, glob, shutil
import shlex
import subprocess
from multiprocessing.pool import ThreadPool

from app_windows.files.externalFiles import ExternalFilesInstance
from app_windows.realityCapture.genericTask import GenericTask
CREATE_NO_WINDOW = 0x08000000



class ResultsArchive(GenericTask):
    def __init__(self, rc_job):
        super().__init__(rc_job)

    def run(self):
        force_reload = self.status != "idle"
        self.set_status("active")
        input_size = self._get_size(os.path.join(self.rc_job.workingdir, self.rc_job.export_foldername))
        model_file_zip = os.path.join(self.rc_job.workingdir, "%s.zip" % self.rc_job.export_foldername)
        if os.path.exists(model_file_zip):
            os.remove(model_file_zip)
        try:
            subprocess.check_output(shlex.split(
                "powershell -command \"Compress-Archive '%s\\*' '%s'\"" % (self.rc_job.export_foldername, model_file_zip)
            ),shell=False, creationflags=CREATE_NO_WINDOW, cwd=self.rc_job.workingdir)
        except:
            pass


        if not os.path.exists(model_file_zip):
            self.log.append("Failed to create result zip file")
            self.set_status("failed")
        else:
            output_size = self._get_size(model_file_zip)
            self.log.append("%sMb in, %s Mb out" % (input_size, output_size))
            self.rc_job.result_file = model_file_zip
            self.set_status("success")

    def _get_size(self, start_path):
        if not os.path.exists(start_path):
            return 0
        if os.path.isdir(start_path):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(start_path):
                total_size += sum([os.path.getsize(fp) for fp in [os.path.join(dirpath, f) for f in filenames] if
                                   not os.path.islink(fp)])
            total_size = round(total_size / 1024 / 1024, 3)
        else:
            total_size = round(os.path.getsize(start_path) / 1024 / 1024, 3)

        if total_size >= 1:
            total_size = int(total_size)
        return total_size