from gevent import monkey
monkey.patch_all()
import os
from pyhtmlgui import PyHtmlGui
from views_windows.appView import AppView
from app_windows.app import AppInstance
from app.additionalHttpEndpoints import HttpEndpoints

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

if __name__ == "__main__":
    gui = PyHtmlGui(
        app_instance    = AppInstance(),
        view_class      = AppView,
        template_dir    = os.path.join(SCRIPT_DIR, "templates"),
        static_dir      = os.path.join(SCRIPT_DIR, "static"),
        base_template   = "base.html",
        listen_port     = 8081,
        listen_host     = "0.0.0.0",
        auto_reload     = False,
        shared_secret   = None,
    )
    httpEndpoints = HttpEndpoints(AppInstance(), gui)
    gui.start(show_frontend=False, block=True)





