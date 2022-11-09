from gevent import monkey
#monkey.patch_all()
import os, sys
import wx
import platform
import time
import tempfile
from cefpython3 import cefpython as cef
from pyhtmlgui import PyHtmlGui
from views_windows.appView import AppView
from app_windows.app import AppInstance
from app_windows.additionalHttpEndpoints import HttpEndpoints

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
WINDOWS = (platform.system() == "Windows")
LINUX = (platform.system() == "Linux")
MAC = (platform.system() == "Darwin")

WIDTH = 900
HEIGHT = 640

class MainFrame(wx.Frame):

    def __init__(self):
        self.browser = None

        if WINDOWS:
            # noinspection PyUnresolvedReferences, PyArgumentList
            print("[wxpython.py] System DPI settings: %s" % str(cef.DpiAware.GetSystemDpi()))
        if hasattr(wx, "GetDisplayPPI"):
            print("[wxpython.py] wx.GetDisplayPPI = %s" % wx.GetDisplayPPI())
        print("[wxpython.py] wx.GetDisplaySize = %s" % wx.GetDisplaySize())

        print("[wxpython.py] MainFrame declared size: %s" % str((WIDTH, HEIGHT)))
        size = self.scale_window_size_for_high_dpi(WIDTH, HEIGHT)
        print("[wxpython.py] MainFrame DPI scaled size: %s" % str(size))

        wx.Frame.__init__(self, parent=None, id=wx.ID_ANY, title='RC Automation', size=size)
        print("[wxpython.py] MainFrame actual size: %s" % self.GetSize())

        self.setup_icon()
        self.create_menu()
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.browser_panel = wx.Panel(self, style=wx.WANTS_CHARS)
        self.browser_panel.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
        self.browser_panel.Bind(wx.EVT_SIZE, self.OnSize)
        self.embed_browser()
        self.Show()

    def setup_icon(self):
        icon_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources", "wxpython.png")
        # wx.IconFromBitmap is not available on Linux in wxPython 3.0/4.0
        if os.path.exists(icon_file) and hasattr(wx, "IconFromBitmap"):
            icon = wx.IconFromBitmap(wx.Bitmap(icon_file, wx.BITMAP_TYPE_PNG))
            self.SetIcon(icon)

    def create_menu(self):
        pass
        #filemenu = wx.Menu()
        #filemenu.Append(1, "Some option")
        #filemenu.Append(2, "Another option")
        #menubar = wx.MenuBar()
        #menubar.Append(filemenu, "&File")
        #self.SetMenuBar(menubar)

    def embed_browser(self):
        window_info = cef.WindowInfo()
        (width, height) = self.browser_panel.GetClientSize().Get()
        assert self.browser_panel.GetHandle(), "Window handle not available"
        window_info.SetAsChild(self.browser_panel.GetHandle(), [0, 0, width, height])
        self.browser = cef.CreateBrowserSync(window_info, url="http://127.0.0.1:8081")

    def OnSetFocus(self, _):
        if not self.browser: return
        if WINDOWS:
            cef.WindowUtils.OnSetFocus(self.browser_panel.GetHandle(), 0, 0, 0)
        self.browser.SetFocus(True)

    def OnSize(self, _):
        if not self.browser: return
        if WINDOWS:
            cef.WindowUtils.OnSize(self.browser_panel.GetHandle(), 0, 0, 0)
        self.browser.NotifyMoveOrResizeStarted()

    def OnClose(self, event):
        if not self.browser: return
        self.browser.ParentWindowWillClose()
        event.Skip()
        self.browser = None

    def scale_window_size_for_high_dpi(self, width, height):
        if not WINDOWS:
            return width, height
        (_, _, max_width, max_height) = wx.GetClientDisplayRect().Get()
        # noinspection PyUnresolvedReferences
        (width, height) = cef.DpiAware.Scale((width, height))
        if width > max_width:
            width = max_width
        if height > max_height:
            height = max_height
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
        if self.is_initialized:
            return
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
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
    if WINDOWS:
        # noinspection PyUnresolvedReferences, PyArgumentList
        cef.DpiAware.EnableHighDpiSupport()
    cef.Initialize(settings={'cache_path': tempfile.gettempdir()})
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
