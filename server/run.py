import glob
import math

from gevent import monkey
monkey.patch_all()
from pyhtmlgui import PyHtmlGui
from views.appView import AppView
from app.app import AppInstance
import os
import time
from app.additionalHttpEndpoints import HttpEndpoints


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def convert_shots_dir():
    for shot_path in glob.glob("/shots/*"):
        if os.path.exists(os.path.join(shot_path, "metadata.json")) or os.path.exists(os.path.join(shot_path, "images")):
            for device_id in range(101, 213):
                segment = math.floor(((device_id - 101) / 7) + 1)
                row = ((device_id - 101) % 7) + 1
                for image_type in ["normal", "projection"]:
                    for image_mode in ["", "preview_"]:
                        path = os.path.join(shot_path, "%simages" % image_mode, image_type)
                        img_path = os.path.join(path, "%s.jpg" % device_id)
                        if os.path.exists(img_path):
                            new_path = os.path.join(path, "seg%s-cam%s-%s.jpg" % (segment, row, image_type[0]))
                            print(img_path,new_path)


if __name__ == "__main__":
    time.sleep(20)  # wait for system
    os.system("sudo ntpdate -u de.pool.ntp.org")

    gui = PyHtmlGui(
        app_instance    = AppInstance(),
        view_class      = AppView,
        template_dir    = os.path.join(SCRIPT_DIR, "templates"),
        static_dir      = os.path.join(SCRIPT_DIR, "static"),
        base_template   = "base.html",
        listen_port     = 80,
        listen_host     = "0.0.0.0",
        auto_reload     = False,
        shared_secret   = None,
    )
    httpEndpoints = HttpEndpoints(AppInstance(), gui)
    gui.start(show_frontend=False, block=True)





