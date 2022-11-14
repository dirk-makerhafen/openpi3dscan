import traceback

import bottle
from gevent import monkey
#monkey.patch_all()
import os, sys
import wx
import platform
import time
import tempfile
import ctypes

from cefpython3 import cefpython as cef
from pyhtmlgui import PyHtmlGui
from views_windows.appView import AppView
from app_windows.app import AppInstance
from app_windows.additionalHttpEndpoints import HttpEndpoints

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

WIDTH = 900
HEIGHT = 640

def ExceptHook(exc_type, exc_value, exc_trace):
    msg = "".join(traceback.format_exception(exc_type, exc_value,exc_trace))
    encoding = cef.GetAppSetting("string_encoding") or "utf-8"
    if type(msg) == bytes:
        msg = msg.decode(encoding=encoding, errors="replace")
    msg = msg.encode("ascii", errors="replace")
    msg = msg.decode("ascii", errors="replace")
    print("\n"+msg)
    cef.QuitMessageLoop()
    cef.Shutdown()
    # noinspection PyProtectedMember
    os._exit(1)

class MainFrame(wx.Frame):

    def __init__(self):
        self.browser = None
        size = self.scale_window_size_for_high_dpi(WIDTH, HEIGHT)
        #size = (WIDTH, HEIGHT)
        wx.Frame.__init__(self, parent=None, id=wx.ID_ANY, title='RCAutomation', size=size)
        self.setup_icon()
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.browser_panel = wx.Panel(self, style=wx.WANTS_CHARS)
        self.browser_panel.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
        self.browser_panel.Bind(wx.EVT_SIZE, self.OnSize)
        self.embed_browser()
        self.Show()

    def setup_icon(self):
        icon_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources", "wxpython.png")
        if os.path.exists(icon_file) and hasattr(wx, "IconFromBitmap"):
            icon = wx.IconFromBitmap(wx.Bitmap(icon_file, wx.BITMAP_TYPE_PNG))
            self.SetIcon(icon)

    def embed_browser(self):
        window_info = cef.WindowInfo()
        (width, height) = self.browser_panel.GetClientSize().Get()
        assert self.browser_panel.GetHandle(), "Window handle not available"
        window_info.SetAsChild(self.browser_panel.GetHandle(), [0, 0, width, height])
        self.browser = cef.CreateBrowserSync(window_info, url="http://127.0.0.1:8081")

    def OnSetFocus(self, _):
        if not self.browser: return
        cef.WindowUtils.OnSetFocus(self.browser_panel.GetHandle(), 0, 0, 0)
        self.browser.SetFocus(True)

    def OnSize(self, _):
        if not self.browser: return
        cef.WindowUtils.OnSize(self.browser_panel.GetHandle(), 0, 0, 0)
        self.browser.NotifyMoveOrResizeStarted()

    def OnClose(self, event):
        if not self.browser: return
        self.browser.ParentWindowWillClose()
        event.Skip()
        self.browser = None

    def scale_window_size_for_high_dpi(self, width, height):
        (_, _, max_width, max_height) = wx.GetClientDisplayRect().Get()
        # noinspection PyUnresolvedReferences
        try:
            (width, height) = cef.DpiAware.Scale((width, height))
            if width > max_width:
                width = max_width
            if height > max_height:
                height = max_height
        except:
            pass
        return width, height
class CefApp(wx.App):
    def __init__(self, redirect):
        self.timer = None
        self.timer_id = 1
        self.is_initialized = False
        super(CefApp, self).__init__(redirect=redirect)

    def OnPreInit(self):
        super(CefApp, self).OnPreInit()

    def OnInit(self):
        if self.is_initialized: return
        self.is_initialized = True
        self.create_timer()
        frame = MainFrame()
        self.SetTopWindow(frame)
        frame.Show()
        return True

    def create_timer(self):
        self.timer = wx.Timer(self, self.timer_id)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(10)  # 10ms timer

    def on_timer(self, _):
        cef.MessageLoopWork()

    def OnExit(self):
        self.timer.Stop()
        return 0

def run_wxcef():
    sys.excepthook = ExceptHook  # To shutdown all CEF processes on error

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(0)
        cef.DpiAware.EnableHighDpiSupport()
    except:
        pass

    settings = {'cache_path': tempfile.gettempdir(), "log_severity": cef.LOGSEVERITY_DISABLE}
    if hasattr(sys, '_MEIPASS'):
        settings.update({'locales_dir_path': os.path.join(sys._MEIPASS, 'locales'),
                    'resources_dir_path': sys._MEIPASS,
                    'browser_subprocess_path': os.path.join(sys._MEIPASS, 'subprocess.exe'),
                    'log_file': os.path.join(sys._MEIPASS, 'debug.log')})

    cef.Initialize(settings=settings)
    capp = CefApp(False)
    capp.MainLoop()
    del capp  # Must destroy before calling Shutdown
    cef.Shutdown()

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
    run_wxcef()
