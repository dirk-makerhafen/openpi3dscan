import os, sys
from selenium import webdriver
import time
import glob, shutil
from multiprocessing.pool import ThreadPool


SCRIPT_DIR = os.path.dirname(sys.argv[0])

print(SCRIPT_DIR)
INPUT_FILE = sys.argv[-1]
if not INPUT_FILE.endswith(".glb"):
    print("%s is not a glb file" % INPUT_FILE)
    time.sleep(10)
    exit(1)


class glb2gif():

    def convert(self, input_file):
        try:
            path = os.path.dirname(os.path.abspath(input_file))
            tmp_path = os.path.join(path, "_tmp")
            if os.path.exists(tmp_path):
                shutil.rmtree(tmp_path)
            os.mkdir(tmp_path)
            self.glb_to_images(input_file, tmp_path)
            glbfile = "%s.gif" % input_file[:-4]
            self.screenshots_to_animation(tmp_path,glbfile ,"gif")
        except Exception as e:
            print(e)
        if os.path.exists(tmp_path):
            shutil.rmtree(tmp_path)
        
    def glb_to_images(self, glb_path, output_path):
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

        while angle < 360:
            browser.save_screenshot(os.path.join(output_path, "screenshot_%s.png" % ("%s" % angle).zfill(3)))
            angle += angle_add
            browser.execute_script("rotate(%s);" % angle)
            time.sleep(0.3)
        browser.close()

    def screenshots_to_animation(self, path, output_file, filetype):
        files = glob.glob(os.path.join(path, "screenshot_*.png"))
        if len(files) == 0:
            print("no screenshots found")
            return

        size = 1100

        def f(file):
            os.system('%s -resize %sx "%s"' % (os.path.join(SCRIPT_DIR, "mogrify.exe"), size, file))
            os.system('%s -crop %sx%s+70+100 +repage "%s"' % (os.path.join(SCRIPT_DIR, "mogrify.exe"), size - 100, size - 100, file))
            os.system('%s -clobber "%s"' % (os.path.join(SCRIPT_DIR, "optipng.exe"), file))
            os.system('%s "%s" "%s"' % (os.path.join(SCRIPT_DIR, "convert.exe"), file, "%s.gif" % file[:-4]))

        ThreadPool(8).map(f, files)
        total_duration = 400  # in 1/100s of seconds
        delay = int(round(total_duration / len(files), 0))
        os.system('%s --optimize=3 --delay=%s --loop "%s\\screenshot_*.gif" > "%s\\tmp.gif" ' % (os.path.join(SCRIPT_DIR, "gifsicle.exe"), delay, path, path))
        if os.path.exists(os.path.join(path, "tmp.gif")):
            if filetype == "gif":
                os.rename(os.path.join(path, "tmp.gif"), output_file)
            if filetype == "webp":
                os.system('%s "%s\\tmp.gif" "%s"' % (os.path.join(SCRIPT_DIR, "convert.exe"), path, output_file))

        for f in glob.glob(os.path.join(path, "screenshot_*.*")):
            os.remove(f)
        if os.path.exists(os.path.join(path, "tmp.gif")):
            os.remove(os.path.join(path, "tmp.gif"))


instance = glb2gif()
instance.convert(INPUT_FILE)

