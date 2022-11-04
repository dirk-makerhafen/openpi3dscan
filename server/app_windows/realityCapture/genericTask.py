import os
import shlex
import subprocess
import time

from pyhtmlgui import Observable, ObservableList


class GenericTask(Observable):
    def __init__(self, rc_job):
        super().__init__()
        self.rc_job = rc_job
        self.status = "idle"
        self.log = ObservableList()

    def set_status(self, new_status):
        if self.status == new_status:
            return
        self.status = new_status
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
        cmd = '"%s" ' % RCEXE
        #cmd += '-silent "%s\\crash_report.txt" ' % self.workingdir
        #cmd += '-set "appQuitOnError=true" '
        return cmd

    def _run_command(self, cmd, name):
        print("Next Command: %s" % name)
        print(cmd)
        s = time.time()
        subprocess.run(shlex.split(cmd))
        print("Command '%s' took %s seconds" % (name, int(time.time() - s)))
