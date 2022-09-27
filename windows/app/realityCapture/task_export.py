import shutil
import time
from multiprocessing.pool import ThreadPool

from pyhtmlgui import Observable
import os, glob

class Subtask_Export(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def create_export_model(self, force_reload=False):
        output_model_path = os.path.join(self.source_folder, self.export_foldername, self.export_filename.replace(" ",
                                                                                                                  "_" if self.filetype not in [
                                                                                                                      "3mf",
                                                                                                                      "stl", ] else " "))

        if force_reload is True and os.path.exists(output_model_path):
            os.remove(output_model_path)

        if self.parent.filetype == "rcproj":
            rcproj = os.path.join(self.source_folder, "%s.rcproj" % self.realityCapture_filename)
            rcprojdir = os.path.join(self.source_folder, self.realityCapture_filename)
            target_dir = os.path.join(self.source_folder, self.export_foldername)
            try:
                shutil.rmtree(target_dir)
            except:
                print("Failed to delete %s" % target_dir)
            os.mkdir(target_dir)
            shutil.copy(rcproj, target_dir)
            shutil.copy("rc_rebase.exe", target_dir)
            shutil.copytree(rcprojdir, os.path.join(target_dir, self.realityCapture_filename))
            shutil.copytree(imgdir, os.path.join(target_dir, "images"))

        elif not os.path.exists(output_model_path):
            cmd = self.parent.get_cmd_start()
            cmd += '-load "%s\\%s.rcproj" ' % (self.source_folder, self.realityCapture_filename)
            cmd += '-selectComponent "MAIN" '
            cmd += '-selectModel "RAW" '
            if self.parent.export_quality == "high":
                cmd += '-simplify 4000000 '
            if self.parent.export_quality == "normal":
                cmd += '-simplify 1000000 '
            if self.parent.export_quality == "low":
                cmd += '-simplify 500000 '
            cmd += '-cleanModel '
            if self.parent.create_textures is True:
                cmd += '-calculateTexture '
                cmd += '-calculateVertexColors '
            cmd += '-renameSelectedModel "EXPORT" '
            cmd += '-getLicense "%s" ' % self.parent.pin
            cmd += '-exportModel "EXPORT" "%s\\%s\\%s" ' % (self.source_folder, self.export_foldername, self.export_filename)
            cmd += '-quit '
            self.parent.run_command(cmd, "create_export_model")

            if not os.path.exists(output_model_path):
                print("%s model not found, error" % output_model_path)
                return

        if self.parent.filetype == "gif":
            images_path = os.path.join(self.source_folder, self.export_foldername)
            gif_file = os.path.join(self.source_folder, "%s.gif" % self.export_foldername.replace("_gif", ""))
            self._convert_glb_to_images(output_model_path, images_path)
            self._screenshots_to_animation(images_path, gif_file, "gif")
            self.model_path = gif_file

        elif self.parent.filetype == "webp":
            images_path = os.path.join(self.source_folder, self.export_foldername)
            webp_file = os.path.join(self.source_folder, "%s.webp" % self.export_foldername.replace("_webp", ""))
            self._convert_glb_to_images(output_model_path, images_path)
            self._screenshots_to_animation(images_path, webp_file, "webp")
            self.model_path = webp_file

        else:
            model_file_zip = os.path.join(self.source_folder, "%s.zip" % self.export_foldername)
            if os.path.exists(model_file_zip):
                os.remove(model_file_zip)
            os.system("cd \"%s\" & powershell -command \"Compress-Archive '%s\\*' '%s.zip'\"" % (
            self.source_folder, self.export_foldername, self.export_foldername))
            if not os.path.exists(model_file_zip):
                print("Failed to create model zip")
                self.model_path = None
            else:
                print("Model zip created")
                self.model_path = model_file_zip

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
        if self.parent.export_quality == "high":
            angle_add = 6
        elif self.parent.export_quality == "normal":
            angle_add = 8
        elif self.parent.export_quality == "low":
            angle_add = 10

        while angle < 360:
            browser.save_screenshot(os.path.join(output_path, "screenshot_%s.png" % ("%s" % angle).zfill(3)))
            angle += angle_add
            browser.execute_script("rotate(%s);" % angle)
            time.sleep(0.3)
        browser.close()
        if DEBUG is False:
            os.remove(glb_path)

    def _screenshots_to_animation(self, path, output_file, filetype):
        files = glob.glob(os.path.join(path, "screenshot_*.png"))
        if len(files) == 0:
            print("no screenshots found")
            return

        size = 1000
        if self.parent.export_quality == "high":
            size = 1400
        elif self.parent.export_quality == "normal":
            size = 1100
        elif self.parent.export_quality == "low":
            size = 900

        def f(file):
            os.system('mogrify.exe -resize %sx "%s"' % (size, file))
            os.system('mogrify.exe -crop %sx%s+100+100 +repage "%s"' % (size - 130, size - 100, file))
            os.system('optipng.exe -clobber "%s"' % file)
            os.system('convert.exe "%s" "%s"' % (file, "%s.gif" % file[:-4]))

        ThreadPool(8).map(f, files)
        total_duration = 400  # in 1/100s of seconds
        delay = int(round(total_duration / len(files), 0))
        os.system(
            'gifsicle.exe --optimize=3 --delay=%s --loop "%s\\screenshot_*.gif" > "%s\\tmp.gif" ' % (delay, path, path))
        if os.path.exists(os.path.join(path, "tmp.gif")):
            if filetype == "gif":
                os.rename(os.path.join(path, "tmp.gif"), output_file)
            if filetype == "webp":
                os.system('convert.exe "%s\\tmp.gif" "%s"' % (path, output_file))

        if DEBUG is False:
            for f in glob.glob(os.path.join(path, "screenshot_*.*")):
                os.remove(f)
            if os.path.exists(os.path.join(path, "tmp.gif")):
                os.remove(os.path.join(path, "tmp.gif"))

