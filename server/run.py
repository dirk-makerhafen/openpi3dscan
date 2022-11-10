from gevent import monkey
monkey.patch_all()
import os
import time
from pyhtmlgui import PyHtmlGui
from views.appView import AppView
from app.app import AppInstance
from app.additionalHttpEndpoints import HttpEndpoints


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

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





