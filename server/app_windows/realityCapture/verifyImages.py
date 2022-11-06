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
        self.set_status("active")
        for mode in ["normal", "projection"]:
            for file in glob.glob(os.path.join(os.path.join(self.rc_job.workingdir, "images", mode), "*.jpg")):
                fname = file.split("/")[-1]
                if os.path.getsize(file) < 500000:
                    os.remove(file)
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
                        self.log.append("removed %s, corrupted" % fname)
                        self.broken_images.append(fname)

        self.set_status("success")