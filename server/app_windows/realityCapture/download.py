import os
import shutil

import requests
from app_windows.realityCapture.genericTask import GenericTask


class Download(GenericTask):
    def __init__(self, rc_job):
        super().__init__(rc_job)

    def download(self):
        self.set_status("active")
        if os.path.exists(os.path.join(self.rc_job.workingdir, "images")):
            print("shot '%s' was already downloaded as %s" % (shot_id, self.rc_job.workingdir))
        else:
            print("Download shot id %s" % shot_id)
            try:
                data = requests.get("http://%s/shots/%s.zip" % (self.rc_job.source_ip, shot_id)).content
                with open(os.path.join(self.rc_job.workingdir, "%s.zip" % shot_id), "wb") as f:
                    f.write(data)
            except Exception as e:
                print("failed to download shot '%s'" % shot_id)
                return None
            self._unpack_zip(os.path.join(self.rc_job.workingdir, "%s.zip" % shot_id))


    def _unpack_zip(self, path):
        path = os.path.abspath(path)
        name = path.split("\\")[-1].split(".zip")[0]
        dir = "\\".join(path.split("\\")[0:-1])
        target_dir = os.path.join(dir, name)
        print("Unpack %s" % path)
        if os.path.exists(target_dir):
            try:
                shutil.rmtree(target_dir)
            except:
                print("Failed to delete %s" % target_dir)
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
