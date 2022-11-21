import threading
import webbrowser
import os, sys

import win32con
import wx
import wx.adv
import time
import win32gui

from pyhtmlgui import PyHtmlGui
from views_windows.appView import AppView
from app_windows.app import AppInstance
from app_windows.additionalHttpEndpoints import HttpEndpoints
from app_windows.files.externalFiles import ExternalFilesInstance
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

WIDTH = 900
HEIGHT = 640

class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, icon, tooltip, frame):
        self._browser_thread = None
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
            if self._browser_thread is None:
                self._browser_thread = threading.Thread(target=self._browser, daemon=True)
                self._browser_thread.start()
            else:
                hwnd = win32gui.FindWindowEx(0, 0, 0, "RC Automation")
                win32gui.SetForegroundWindow(hwnd)
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
                win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_SHOWWINDOW + win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
        else:
            webbrowser.open("http://127.0.0.1:8081",2)

    def _browser(self):
        os.system("\"%s\" --app=http://127.0.0.1:8081" % ExternalFilesInstance().chromium_exe)
        self._browser_thread = None

class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Minimize to Tray")
        self.frame_icon = wx.Icon(os.path.join(SCRIPT_DIR, 'static', 'app.ico'), wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.frame_icon)
        self.trayicon = TaskBarIcon(self.frame_icon, "RC Automation", self)
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

    gui = PyHtmlGui(
        app_instance    = AppInstance(),
        view_class      = AppView,
        template_dir    = os.path.join(SCRIPT_DIR, "templates"),
        static_dir      = os.path.join(SCRIPT_DIR, "static"),
        base_template   = "base.html",
        listen_port     = 8081,
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
