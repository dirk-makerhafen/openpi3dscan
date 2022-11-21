import os, sys

from pyhtmlgui import Observable
import glob


SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.abspath(sys.argv[0])))

class ExternalFiles(Observable):
    def __init__(self):
        super().__init__()
        try:
            self.RealityCapture_exe = glob.glob("C:\*\Capturing Reality\RealityCapture\RealityCapture.exe")[0]
        except:
            self.RealityCapture_exe = None
        basepath = os.path.join(SCRIPT_DIR, "bin")
        if not os.path.exists(basepath):
            basepath = os.path.join(SCRIPT_DIR, "..", "realityCapture")
        self.chromedriver_exe = os.path.join(basepath, "chromedriver.exe")
        self.chromium_exe = os.path.join(basepath, "RCA.exe")
        self.convert_exe = os.path.join(basepath, "convert.exe")
        self.gifsicle_exe = os.path.join(basepath, "gifsicle.exe")
        self.modelview_html = os.path.join(basepath, "modelview.html")


_externalFilesInstance = None

def ExternalFilesInstance():
    global _externalFilesInstance
    if _externalFilesInstance is None:
        _externalFilesInstance = ExternalFiles()
    return _externalFilesInstance
