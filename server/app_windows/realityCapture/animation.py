import os, time, glob
from multiprocessing.pool import ThreadPool

from app_windows.files.externalFiles import ExternalFilesInstance
from app_windows.realityCapture.genericTask import GenericTask

from selenium import webdriver


class Animation(GenericTask):
    def __init__(self, rc_job):
        super().__init__(rc_job)

    def run(self):
        self.set_status("active")
        images_path = os.path.join(self.rc_job.workingdir, self.rc_job.export_foldername)
        a_file = os.path.join(self.rc_job.workingdir, "%s.%s" % (self.rc_job.export_foldername.replace("_gif", ""), self.rc_job.filetype))
        self._convert_glb_to_images(self.rc_job.exportmodel.output_model_path, images_path)
        self._screenshots_to_animation(images_path, a_file, self.rc_job.filetype)
        if os.path.exists(a_file):
            self.rc_job.result_file = a_file
            self.set_status("success")
        else:
            self.log.append("No %s file generated, failed" % self.rc_job.filetype)
            self.set_status("failed")

    def _convert_glb_to_images(self, glb_path, output_path):
        options = webdriver.ChromeOptions()
        options.binary_location = ExternalFilesInstance().chromium_exe
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-dev-shm-usage")
        browser = webdriver.Chrome(executable_path=ExternalFilesInstance().chromedriver_exe, options=options)
        browser.set_window_position(0, 0)
        browser.set_window_size(1200, 1200)

        browser.get("http://127.0.0.1:8081/modelview.html?src=http://127.0.0.1:8081/rc_cache/%s" % (glb_path.replace("c:\\rc_cache\\", "").replace("\\","/")))

        time.sleep(5)
        angle = 0
        angle_add = 8
        if self.rc_job.export_quality == "high":
            angle_add = 6
        elif self.rc_job.export_quality == "normal":
            angle_add = 8
        elif self.rc_job.export_quality == "low":
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
        if self.rc_job.export_quality == "high":
            size = 1400
        elif self.rc_job.export_quality == "normal":
            size = 1100
        elif self.rc_job.export_quality == "low":
            size = 900

        if os.path.exists(output_file):
            os.remove(output_file)

        def f(file):
            tmpf = "%s_tmp.png" % file[0:-4]
            os.system('%s -resize %sx "%s" "%s"' % (ExternalFilesInstance().convert_exe, size, file, tmpf))
            os.remove(file)
            os.rename(tmpf, file)
            #os.system('%s -clobber "%s"' % (ExternalFilesInstance().optipng_exe, file))
            os.system('%s "%s" "%s"' % (ExternalFilesInstance().convert_exe, file, "%s.gif" % file[:-4]))

        ThreadPool(8).map(f, files)
        total_duration = 400  # in 1/100s of seconds
        delay = int(round(total_duration / len(files), 0))
        os.system('%s --optimize=3 --delay=%s --loop "%s\\screenshot_*.gif" > "%s\\tmp.gif" ' % (ExternalFilesInstance().gifsicle_exe, delay, path, path))
        if os.path.exists(os.path.join(path, "tmp.gif")):
            if filetype == "gif":
                os.rename(os.path.join(path, "tmp.gif"), output_file)
            if filetype == "webp":
                os.system('%s "%s\\tmp.gif" "%s"' % (ExternalFilesInstance().convert_exe, path, output_file))

        for f in glob.glob(os.path.join(path, "screenshot_*.*")):
            os.remove(f)
        if os.path.exists(os.path.join(path, "tmp.gif")):
            os.remove(os.path.join(path, "tmp.gif"))
