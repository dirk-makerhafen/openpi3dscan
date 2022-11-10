import glob
import os
from PIL import Image
from pyhtmlgui import ObservableList

from app_windows.realityCapture.genericTask import GenericTask


class VerifyImages(GenericTask):
    def __init__(self, rc_job):
        super().__init__(rc_job)
        self.broken_images = ObservableList()

    def run(self):
        force_reload = self.status != "idle"

        checked_images = []
        if os.path.exists(self.get_path("checked_images")):
            if force_reload is False:
                with open(self.get_path("checked_images"),"r") as f:
                    checked_images = f.read().split("\n")

        self.set_status("active")
        cnt = 0
        cnt_cache = 0
        cnt_removed = 0
        for mode in ["normal", "projection"]:
            for file in glob.glob(os.path.join(os.path.join(self.rc_job.workingdir, "images", mode), "*.jpg")):
                cnt +=1
                if file in checked_images:
                    cnt_cache += 1
                    continue
                checked_images.append(file)
                fname = os.path.split(file)[1]
                if os.path.getsize(file) < 500000:
                    os.remove(file)
                    cnt_removed += 1
                    self.log.append("removed %s, to small" % fname)
                    self.broken_images.append(fname)
                else:
                    try:
                        im = Image.open(file)
                        im.verify()
                        im.close()
                        im = Image.open(file)
                        im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                        im.close()
                    except Exception as e:
                        os.remove(file)
                        cnt_removed += 1
                        self.log.append("removed %s, corrupted" % fname)
                        self.broken_images.append(fname)

        self.log.append("%s images verified, %s from cache, %s removed" % (cnt, cnt_cache, cnt_removed))

        with open(self.get_path("checked_images"), "w") as f:
            f.write("\n".join(checked_images))
        if cnt > 0:
            self.set_status("success")
        else:
            self.set_status("failed")