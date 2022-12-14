import os
import shlex
import shutil
import glob
import subprocess

import requests
from app_windows.realityCapture.genericTask import GenericTask

CREATE_NO_WINDOW = 0x08000000

class Download(GenericTask):
    def __init__(self, rc_job):
        super().__init__(rc_job)

    def run(self):
        self.set_status("active")
        if os.path.exists(os.path.join(self.rc_job.workingdir, "images")):
            self.log.append("Not downloading, exists in cache")
            self.set_status("success")
            return

        self.log.append("Downloading from %s" % self.rc_job.source_ip)
        try:
            data = requests.get("http://%s/shots/%s.zip" % (self.rc_job.source_ip, self.rc_job.shot_id)).content
            with open(os.path.join(self.rc_job.workingdir, "%s.zip" % self.rc_job.shot_id), "wb") as f:
                f.write(data)
            self.log.append("%sMb downloaded" % (int(len(data)/1024/1024)))
        except Exception as e:
            self.log.append("Download failed")
            self.set_status("failed")
            return
        nr_of_images = self._unpack_zip(os.path.join(self.rc_job.workingdir, "%s.zip" % self.rc_job.shot_id))
        self.log.append("%s images unpacked" % nr_of_images)
        if nr_of_images == 0:
            self.set_status("failed")
            return
        self.set_status("success")


    def _unpack_zip(self, path):
        path = os.path.abspath(path)
        name = path.split("\\")[-1].split(".zip")[0]
        source_dir = "\\".join(path.split("\\")[0:-1])
        unzip_dir = os.path.join(source_dir, name)
        if os.path.exists(unzip_dir):
            try:
                shutil.rmtree(unzip_dir)
            except:
                pass

        try:
            subprocess.check_output(shlex.split("powershell -command \"Expand-Archive '%s.zip'\"" % (name)),shell=False, creationflags=CREATE_NO_WINDOW, cwd=source_dir)
        except:
            pass
        os.remove(path)
        if not os.path.exists(os.path.join(source_dir, "images")):
            os.mkdir(os.path.join(source_dir, "images"))
        if os.path.exists(os.path.join(unzip_dir, "normal")):
            shutil.move(os.path.join(unzip_dir, "normal"), os.path.join(source_dir, "images"))
        if os.path.exists(os.path.join(unzip_dir, "projection")):
            shutil.move(os.path.join(unzip_dir, "projection"), os.path.join(source_dir, "images"))
        if os.path.exists(unzip_dir):
            try:
                shutil.rmtree(unzip_dir)
            except:
                pass
        nr_of_images = len(glob.glob(os.path.join(self.rc_job.workingdir, "images", "*", "*.jpg")))
        return nr_of_images