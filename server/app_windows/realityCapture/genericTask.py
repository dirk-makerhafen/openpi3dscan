import os
import shlex
import subprocess
import time

from pyhtmlgui import Observable, ObservableList
from app_windows.files.externalFiles import ExternalFilesInstance
from app_windows.settings.settings import SettingsInstance


class LogItem(Observable):
    def __init__(self, value):
        super().__init__()
        self.value = value
class Log(ObservableList):
    def append(self, value):
        value = LogItem(value)
        super().append(value)

class GenericTask(Observable):
    def __init__(self, rc_job):
        super().__init__()
        self.rc_job = rc_job
        self.status = "idle"
        self.log = Log()
        self.last_try_failed = False
        self.is_last_try = False

    def reset(self, is_last_try):
        self.is_last_try = is_last_try
        while len(self.log) > 0:
            del self.log[0]
        if self.status != "idle":
            if self.status == "failed" and is_last_try is True:
                self.last_try_failed = True
            self.set_status("repeat")

    def set_status(self, new_status):
        if self.status == new_status:
            return
        self.status = new_status
        if self.status == "success":
            self.last_try_failed = False
        self.notify_observers()

    def get_path(self, fname):
        if "%s" in fname:
            fname = fname % self.rc_job.realityCapture_filename
        return os.path.join(self.rc_job.workingdir, "tmp", fname)

    def _get_cmd_new_scene(self):
        cmd = '-newScene '
        if self.rc_job.create_mesh_from in ["projection", "all"]:
            cmd += '-addFolder "%s\\images\\projection" ' % self.rc_job.workingdir
            cmd += '-selectAllImages '
            cmd += '-enableTexturingAndColoring false '
            cmd += '-enableColorNormalization false '

        if self.rc_job.create_mesh_from in ["normal", "all"] or self.rc_job.create_textures is True:
            cmd += '-addFolder "%s\\images\\normal" ' % self.rc_job.workingdir
            cmd += '-invertImageSelection '
            if self.rc_job.create_mesh_from == "projection":
                cmd += '-enableMeshing false '  # don't use normal images for mesh
        cmd += '-deselectAllImages '
        return cmd

    def _get_cmd_start(self):
        cmd = '"%s" ' % ExternalFilesInstance().RealityCapture_exe
        if SettingsInstance().realityCaptureSettings.hide_realitycapture is True and self.last_try_failed is False:
            cmd += '-headless '
            cmd += '-silent "%s\\tmp\\crash_report.txt" ' % self.rc_job.workingdir
            cmd += '-set "appQuitOnError=true" '
        if self.rc_job.token != "":
            cmd += '-activate %s ' % self.rc_job.token

        lp = self.get_path("license.rclicense")
        if os.path.exists(lp):
            cmd += '-importLicense "%s" ' % lp

        return cmd

    def _run_command(self, cmd, name):
        print("Next Command: %s" % name)
        print(cmd)
        s = time.time()
        subprocess.run(shlex.split(cmd))
        print("Command '%s' took %s seconds" % (name, int(time.time() - s)))
