import os
import shutil

import requests
from app_windows.realityCapture.genericTask import GenericTask


class Download(GenericTask):
    def __init__(self, rc_job):
        super().__init__(rc_job)

    def run(self):
        self.set_status("active")
        if os.path.exists(os.path.join(self.rc_job.workingdir, "images")):
            self.log.append("Not downloading, exists in cache")
        else:
            self.log.append("Download from %s" % self.rc_job.source_ip)
            try:
                data = requests.get("http://%s/shots/%s.zip" % (self.rc_job.source_ip, self.rc_job.shot_id)).content
                with open(os.path.join(self.rc_job.workingdir, "%s.zip" % self.rc_job.shot_id), "wb") as f:
                    f.write(data)
            except Exception as e:
                self.log.append("Download failed")
                self.set_status("failed")
                return None
            if self._unpack_zip(os.path.join(self.rc_job.workingdir, "%s.zip" % self.rc_job.shot_id)) is False:
                self.set_status("failed")
                return None
        self.set_status("success")

    def _unpack_zip(self, path):
        path = os.path.abspath(path)
        name = path.split("\\")[-1].split(".zip")[0]
        dir = "\\".join(path.split("\\")[0:-1])
        target_dir = os.path.join(dir, name)
        self.log.append("Unzip download")
        if os.path.exists(target_dir):
            try:
                shutil.rmtree(target_dir)
            except:
                pass
        os.system("cd \"%s\" & powershell -command \"Expand-Archive '%s.zip'\"" % (dir, name))
        os.remove(path)
        if not os.path.exists(os.path.join(target_dir, "images")):
            os.mkdir(os.path.join(target_dir, "images"))
        shutil.move(os.path.join(target_dir, "normal"), os.path.join(target_dir, "images"))
        shutil.move(os.path.join(target_dir, "projection"), os.path.join(target_dir, "images"))
        if os.path.exists(os.path.join(target_dir, "normal")):
            shutil.rmtree(os.path.join(target_dir, "normal"))
        if os.path.exists(os.path.join(target_dir, "projection")):
            shutil.rmtree(os.path.join(target_dir, "projection"))
