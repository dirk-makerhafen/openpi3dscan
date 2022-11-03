import os, time, glob, shutil
from multiprocessing.pool import ThreadPool

from pyhtmlgui import Observable


class ResultsArchive(Observable):
    def __init__(self, rc_job):
        super().__init__()
        self.rc_job = rc_job
        self.status = "idle"

    def set_status(self, new_status):
        if self.status == new_status:
            return
        self.status = new_status
        self.notify_observers()

    def create(self, force_reload=False):
        output_model_path = os.path.join(self.rc_job.source_folder, self.rc_job.export_foldername, self.rc_job.export_filename.replace(" ","_" if self.rc_job.filetype not in ["3mf","stl", ] else " "))

        if force_reload is True and os.path.exists(output_model_path):
            os.remove(output_model_path)

        if self.rc_job.filetype == "rcproj":
            rcproj = os.path.join(self.rc_job.source_folder, "%s%s.rcproj" % (self.rc_job.realityCapture_filename, self.rc_job.quality_str))
            rcprojdir = os.path.join(self.rc_job.source_folder, "%s%s" % (self.rc_job.realityCapture_filename, self.rc_job.quality_str))
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
