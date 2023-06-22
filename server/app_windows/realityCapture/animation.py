import os, time, glob
import shlex
import subprocess
import threading
from multiprocessing.pool import ThreadPool
from PIL import Image
from app_windows.files.externalFiles import ExternalFilesInstance
from app_windows.realityCapture.genericTask import GenericTask

from selenium import webdriver

CREATE_NO_WINDOW = 0x08000000


class Animation(GenericTask):
    def __init__(self, rc_job):
        super().__init__(rc_job)

        if self.rc_job.filetype == "holobox":
            self.resolution = [2160, 3840 ]
            if self.rc_job.export_quality == "high":
                self.framerate = 60
            elif self.rc_job.export_quality == "normal":
                self.framerate = 48
            else: # low
                self.framerate = 24
        else:
            if self.rc_job.export_quality == "high":
                self.resolution = [720, 1280 ]
                self.framerate = 20
            elif self.rc_job.export_quality == "normal":
                self.resolution = [576, 1024 ]
                self.framerate = 15
            else:  # low
                self.resolution = [450, 800 ]
                self.framerate = 10
        self.animation_time = 4 # in seconds

    def run(self):
        self.set_status("active")
        images_path = os.path.join(self.rc_job.workingdir, self.rc_job.export_foldername)
        ext = self.rc_job.filetype if self.rc_job.filetype != "holobox" else "mp4"
        output_file = os.path.join(self.rc_job.workingdir, "%s.%s" % (self.rc_job.export_foldername.replace("_gif", "").replace("_webp", "").replace("_holobox", ""), ext))
        self._convert_glb_to_images(self.rc_job.exportmodel.output_model_path, images_path)
        self._screenshots_to_animation(images_path, output_file, self.rc_job.filetype)
        if os.path.exists(output_file):
            self.rc_job.result_file = output_file
            self.set_status("success")
        else:
            self.log.append("No %s file generated, failed" % self.rc_job.filetype)
            self.set_status("failed")

    def _convert_glb_to_images(self, glb_path, output_path):
        for f in glob.glob(os.path.join(output_path, "screenshot_*.*")):
            os.remove(f)

        options = webdriver.ChromeOptions()
        options.binary_location = ExternalFilesInstance().chromium_exe
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-dev-shm-usage")
        browser = webdriver.Chrome(executable_path=ExternalFilesInstance().chromedriver_exe, options=options)
        browser.set_window_position(0, 0)
        if self.rc_job.filetype == "holobox":
            browser.set_window_size(2160, 3840)
        else:
            browser.set_window_size(1080, 1920)

        browser.get("http://127.0.0.1:18081/modelview.html?src=http://127.0.0.1:18081/rc_cache/%s" % (glb_path.replace("c:\\rc_cache\\", "").replace("\\","/")))

        time.sleep(5)

        self.log.append("Generating %s frames" % (self.framerate*self.animation_time))
        angle_step = 360 / (self.animation_time * self.framerate)

        angle = 0
        cnt = 0
        while angle < 360:
            browser.execute_script("rotate(%s);" % angle)
            time.sleep(1.3)
            browser.save_screenshot(os.path.join(output_path, "screenshot_%s.png" % ("%s" % cnt).zfill(3)))
            angle += angle_step
            cnt += 1

        browser.close()

    def cmd(self, cmd):
        r = subprocess.check_output(shlex.split(cmd), shell=False, creationflags=CREATE_NO_WINDOW)
        print(cmd, r)

    def _screenshots_to_animation(self, path, output_file, filetype):
        files = glob.glob(os.path.join(path, "screenshot_*.png"))
        if len(files) == 0:
            print("no screenshots found")
            return

        if os.path.exists(output_file):
            os.remove(output_file)

        def f(file):
            tmpf = "%s_tmp.png" % file[0:-4]
            try:
                self.cmd('"%s" -resize %sx%s "%s" "%s"' % (ExternalFilesInstance().convert_exe,  self.resolution[0], self.resolution[1], file, tmpf))
                if os.path.exists(tmpf):
                    os.remove(file)
                    os.rename(tmpf, file)
                self.cmd('"%s" "%s" "%s"' % (ExternalFilesInstance().convert_exe, file, "%s.gif" % file[:-4]))
            except Exception as e:
                print(e)
                pass

        if self.rc_job.filetype != "holobox":
            self.log.append("Optimizing %s images" % len(files))
            ThreadPool(8).map(f, files)

        self.log.append("Rendering animation")
        if filetype == "holobox":
            self.cmd('"%s" -f image2 -framerate %s -i "%s\\screenshot_%%3d.png" -vcodec libx264 -vf scale=%sx%s -crf 10 -pix_fmt yuv420p "%s" ' % (ExternalFilesInstance().ffmpeg, self.framerate, path,  self.resolution[0], self.resolution[1], output_file))
        else:
            try:
                delay = int(100 / self.framerate)  # in 100th of seconds
                self.cmd('"%s" --optimize=3 --delay=%s --loop "%s\\screenshot_*.gif" -o "%s\\tmp.gif" ' % (ExternalFilesInstance().gifsicle_exe, delay, path, path))
            except:
                pass

            if os.path.exists(os.path.join(path, "tmp.gif")):
                if filetype == "gif":
                    os.rename(os.path.join(path, "tmp.gif"), output_file)
                if filetype == "webp":
                    try:
                        self.cmd('"%s" "%s\\tmp.gif" "%s"' % (ExternalFilesInstance().convert_exe, path, output_file))
                    except:
                        pass

        for f in glob.glob(os.path.join(path, "screenshot_*.*")):
            os.remove(f)
        if os.path.exists(os.path.join(path, "tmp.gif")):
            os.remove(os.path.join(path, "tmp.gif"))
