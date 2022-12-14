import subprocess
import threading
import webbrowser
import os, sys
import shlex
import win32con
import wx
import wx.adv
import time
import win32gui

from pyhtmlgui import PyHtmlGui
import multiprocessing
from views_windows.appView import AppView
from app_windows.app import AppInstance
from app_windows.additionalHttpEndpoints import HttpEndpoints
from app_windows.files.externalFiles import ExternalFilesInstance
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def kill_chrome():
    cmd = "wmic Path win32_process Where \"CommandLine Like '%RCAutomation\\\\bin\\\\chromium\\\\chrome.exe%'\" Call Terminate"
    try:
        CREATE_NO_WINDOW = 0x08000000
        subprocess.check_output(cmd, shell=False,creationflags=CREATE_NO_WINDOW)
    except:
        pass

class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, icon, tooltip, frame):
        self._browser_thread = None
        self._last_usage = 0
        wx.adv.TaskBarIcon.__init__(self)
        self.SetIcon(icon, tooltip)
        self.frame = frame
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_UP, self.OnShow)
        self.Bind(wx.EVT_MENU, self.OnShow, id=1)
        self.Bind(wx.EVT_MENU, self.OnExit, id=2)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(1, 'Show')
        menu.Append(2, 'Exit')
        return menu

    def OnExit(self, event):
         self.frame.Close()

    def OnShow(self, event= None):
        if os.path.exists(ExternalFilesInstance().chromium_exe):
            hwnd = win32gui.FindWindowEx(0, 0, 0, "RCAutomation")
            if hwnd != 0:
                win32gui.SetForegroundWindow(hwnd)
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST  , 0, 0, 0, 0, win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
                win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_SHOWWINDOW + win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
            else:
                if time.time() - self._last_usage > 4: # lock button for some time so chromium can launch after multiple clicks
                    self._last_usage = time.time()
                    if self._browser_thread is not None:
                        kill_chrome()
                    self._browser_thread = threading.Thread(target=self._browser, daemon=True)
                    self._browser_thread.start()
        else:
            webbrowser.open("http://127.0.0.1:18081",2)

    def _browser(self):
        ws = "--start-maximized"
        cmd = "\"%s\" %s --no-default-browser-check --disable-logging --overscroll-history-navigation=0 --disable-pinch --user-data-dir=\"%s\" --app=http://127.0.0.1:18081" % (ExternalFilesInstance().chromium_exe, ws,  os.path.join(os.environ["APPDATA"], "RCAutomation", "data"))
        try:
            subprocess.check_output(shlex.split(cmd), shell=False)
        except:
            pass
        self._browser_thread = None

class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Minimize to Tray")
        self.frame_icon = wx.Icon(os.path.join(SCRIPT_DIR, 'static', 'app.ico'), wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.frame_icon)
        self.trayicon = TaskBarIcon(self.frame_icon, "RCAutomation", self)
        self.Bind(wx.EVT_ICONIZE, self.on_iconify)
        self.Bind(wx.EVT_ICONIZE, self.onMinimize)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Hide()
        self.trayicon.OnShow()

    def on_iconify(self, e):
        self.Hide()

    def onClose(self, evt):
        self.trayicon.Destroy()
        self.Destroy()

    def onMinimize(self, event):
        if self.IsIconized():
            self.Hide()



if __name__ == "__main__":
    if hasattr(sys, 'frozen'):
        multiprocessing.freeze_support()
    kill_chrome()

    gui = PyHtmlGui(
        app_instance    = AppInstance(),
        view_class      = AppView,
        template_dir    = os.path.join(SCRIPT_DIR, "templates"),
        static_dir      = os.path.join(SCRIPT_DIR, "static"),
        base_template   = "base_windows.html",
        listen_port     = 18081,
        listen_host     = "127.0.0.1",
        auto_reload     = False,
        shared_secret   = None,
    )
    httpEndpoints = HttpEndpoints(AppInstance(), gui)
    gui.start(show_frontend=False, block=False)
    time.sleep(1)

    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()

    gui.stop()
    kill_chrome()