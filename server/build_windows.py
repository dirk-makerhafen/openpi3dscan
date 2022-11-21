import os, shutil
import requests

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
TARGETFOLDER = os.path.join(SCRIPT_DIR,"dist","bin")

#shutil.rmtree("build")
#shutil.rmtree("dist")
os.system("pyinstaller app_windows.spec")
exit(0)
if not os.path.exists(TARGETFOLDER):
    os.mkdir(TARGETFOLDER)

def download(url, filename):
    with open(os.path.join(TARGETFOLDER, filename),"wb") as f:
        f.write(requests.get(url).content)

download("https://imagemagick.org/archive/binaries/ImageMagick-7.1.0-portable-Q16-x64.zip", "imagemagick.zip")
os.system("cd \"%s\" & powershell -command \"Expand-Archive '%s'\"" % (TARGETFOLDER, "imagemagick.zip"))
shutil.move(os.path.join(TARGETFOLDER,"imagemagick","convert.exe"), TARGETFOLDER)

download("https://eternallybored.org/misc/gifsicle/releases/gifsicle-1.92-win64.zip", "gifsicle.zip")
os.system("cd \"%s\" & powershell -command \"Expand-Archive '%s'\"" % (TARGETFOLDER, "gifsicle.zip"))
shutil.move(os.path.join(TARGETFOLDER,"gifsicle","gifsicle-1.92","gifsicle.exe"), TARGETFOLDER)

download("https://chromedriver.storage.googleapis.com/103.0.5060.134/chromedriver_win32.zip", "chromedriver.zip")
os.system("cd \"%s\" & powershell -command \"Expand-Archive '%s'\"" % (TARGETFOLDER, "chromedriver.zip"))
shutil.move(os.path.join(TARGETFOLDER,"chromedriver","chromedriver.exe"), TARGETFOLDER)

download("https://github.com/portapps/ungoogled-chromium-portable/releases/download/103.0.5060.114-15/ungoogled-chromium-portable-win64-103.0.5060.114-15.7z", "chromium.7z")
os.system("cd \"%s\" & \"c:\\Program Files\\7-Zip\\7z.exe\" x \"%s\"" % (TARGETFOLDER, os.path.join(TARGETFOLDER,"chromium.7z")))
shutil.move(os.path.join(TARGETFOLDER,"ungoogled-chromium-portable.exe"),os.path.join(TARGETFOLDER,"RCAfrontend.exe"))

for file in ["imagemagick","imagemagick.zip", "gifsicle", "gifsicle.zip", "chromedriver", "chromedriver.zip", "chromium.7z", "CHANGELOG.md", "README.md"]:
    file = os.path.join(TARGETFOLDER, file)
    if os.path.exists(file):
        if os.path.isdir(file):
            shutil.rmtree(file)
        else:
            os.remove(file)