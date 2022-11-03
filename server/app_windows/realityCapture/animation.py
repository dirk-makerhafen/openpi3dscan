import os, time, glob
from multiprocessing.pool import ThreadPool

from pyhtmlgui import Observable
from selenium import webdriver


class Animation(Observable):
    def __init__(self, rc_job):
        super().__init__()
        self.rc_job = rc_job
        self.status = "idle"

    def set_status(self, new_status):
        if self.status == new_status:
            return
        self.status = new_status
        self.notify_observers()

    def create(self, output_model_path, filetype):
        images_path = os.path.join(self.rc_job.source_folder, self.rc_job.export_foldername)
        a_file = os.path.join(self.rc_job.source_folder, "%s.%s" % (self.rc_job.export_foldername.replace("_gif", ""), filetype))
        self._convert_glb_to_images(output_model_path, images_path)
        self._screenshots_to_animation(images_path, a_file, filetype)
        return a_file

    def _convert_glb_to_images(self, glb_path, output_path):
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--allow-file-access-from-files")
        browser = webdriver.Chrome(executable_path=os.path.join(SCRIPT_DIR, "chromedriver.exe"), options=options)
        browser.set_window_position(0, 0)
        browser.set_window_size(1200, 1200)

        browser.get("file:\\%s?src=%s" % (os.path.join(SCRIPT_DIR, "modelview.html"), glb_path.replace('\\', '/')))

        time.sleep(5)
        angle = 0
        angle_add = 8
        if self.rc_job.quality == "high":
            angle_add = 6
        elif self.rc_job.quality == "normal":
            angle_add = 8
        elif self.rc_job.quality == "low":
            angle_add = 10

        while angle < 360:
            browser.save_screenshot(os.path.join(output_path, "screenshot_%s.png" % ("%s" % angle).zfill(3)))
            angle += angle_add
            browser.execute_script("rotate(%s);" % angle)
            time.sleep(0.3)
        browser.close()
        os.remove(glb_path)

    def _screenshots_to_animation(self, path, output_file, filetype):
        files = glob.glob(os.path.join(path, "screenshot_*.png"))
        if len(files) == 0:
            print("no screenshots found")
            return

        size = 1100
        if self.rc_job.quality == "high":
            size = 1400
        elif self.rc_job.quality == "normal":
            size = 1100
        elif self.rc_job.quality == "low":
            size = 900

        def f(file):
            os.system('mogrify.exe -resize %sx "%s"' % (size, file))
            os.system('optipng.exe -clobber "%s"' % file)
            os.system('convert.exe "%s" "%s"' % (file, "%s.gif" % file[:-4]))

        ThreadPool(8).map(f, files)
        total_duration = 400  # in 1/100s of seconds
        delay = int(round(total_duration / len(files), 0))
        os.system('gifsicle.exe --optimize=3 --delay=%s --loop "%s\\screenshot_*.gif" > "%s\\tmp.gif" ' % (delay, path, path))
        if os.path.exists(os.path.join(path, "tmp.gif")):
            if filetype == "gif":
                os.rename(os.path.join(path, "tmp.gif"), output_file)
            if filetype == "webp":
                os.system('convert.exe "%s\\tmp.gif" "%s"' % (path, output_file))

        for f in glob.glob(os.path.join(path, "screenshot_*.*")):
            os.remove(f)
        if os.path.exists(os.path.join(path, "tmp.gif")):
            os.remove(os.path.join(path, "tmp.gif"))
