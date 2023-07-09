import os, sys
import time
from pyhtmlgui import PyHtmlGui
import multiprocessing
from pyhtmlgui.apps.qt import PyHtmlQtApp, PyHtmlQtWindow, PyHtmlQtSimpleTray
from views_windows.appView import AppView
from app_windows.app import AppInstance
from app_windows.additionalHttpEndpoints import HttpEndpoints

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

if __name__ == "__main__":
    if hasattr(sys, 'frozen'):
        multiprocessing.freeze_support()

    gui = PyHtmlGui(
        app_instance    = AppInstance(),
        view_class      = AppView,
        template_dir    = os.path.join(SCRIPT_DIR, "templates"),
        static_dir      = os.path.join(SCRIPT_DIR, "static"),
        base_template   = "base_windows.html",
        listen_port     = 18081,
        listen_host     = "127.0.0.1",
        auto_reload     = True,
        shared_secret   = None,
    )
    httpEndpoints = HttpEndpoints(AppInstance(), gui)
    gui.start(show_frontend=False, block=False)
    time.sleep(1)
    qt_app = PyHtmlQtApp()
    window = PyHtmlQtWindow(qt_app, gui.get_url(), [1200, 900], "RCAutomation", icon_path=os.path.join(SCRIPT_DIR, 'static', 'app.ico'))
    tray = PyHtmlQtSimpleTray(qt_app, icon_path=os.path.join(SCRIPT_DIR, 'static', 'app.ico'))
    tray.on_left_clicked.attach_observer(window.show)
    tray.addAction("Show", window.show)
    tray.addAction("Hide", window.close)
    tray.addAction("Exit", qt_app.stop)
    window.on_minimized_event.attach_observer(window.hide)  # we minimize to tray

    window.show()
    qt_app.run()
