import os, shutil
import requests

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
TARGETFOLDER = os.path.join(SCRIPT_DIR,"dist","bin")

def download(url, filename):
    with open(os.path.join(TARGETFOLDER, filename),"wb") as f:
        f.write(requests.get(url).content)

os.system("pyinstaller app_windows.spec")

if not os.path.exists(TARGETFOLDER):
    os.mkdir(TARGETFOLDER)

if not os.path.exists(os.path.join(TARGETFOLDER,"convert.exe")):
    download("https://imagemagick.org/archive/binaries/ImageMagick-7.1.0-portable-Q16-x64.zip", "imagemagick.zip")
    os.system("cd \"%s\" & powershell -command \"Expand-Archive '%s'\"" % (TARGETFOLDER, "imagemagick.zip"))
    shutil.move(os.path.join(TARGETFOLDER,"imagemagick","convert.exe"), TARGETFOLDER)

if not os.path.exists(os.path.join(TARGETFOLDER,"gifsicle.exe")):
    download("https://eternallybored.org/misc/gifsicle/releases/gifsicle-1.92-win64.zip", "gifsicle.zip")
    os.system("cd \"%s\" & powershell -command \"Expand-Archive '%s'\"" % (TARGETFOLDER, "gifsicle.zip"))
    shutil.move(os.path.join(TARGETFOLDER,"gifsicle","gifsicle-1.92","gifsicle.exe"), TARGETFOLDER)

if not os.path.exists(os.path.join(TARGETFOLDER,"chromedriver.exe")):
    download("https://chromedriver.storage.googleapis.com/103.0.5060.134/chromedriver_win32.zip", "chromedriver.zip")
    os.system("cd \"%s\" & powershell -command \"Expand-Archive '%s'\"" % (TARGETFOLDER, "chromedriver.zip"))
    shutil.move(os.path.join(TARGETFOLDER,"chromedriver","chromedriver.exe"), TARGETFOLDER)

if not os.path.exists(os.path.join(TARGETFOLDER,"RCA.exe")):
    download("https://github.com/portapps/ungoogled-chromium-portable/releases/download/103.0.5060.114-15/ungoogled-chromium-portable-win64-103.0.5060.114-15.7z", "chromium.7z")
    os.system("cd \"%s\" & \"c:\\Program Files\\7-Zip\\7z.exe\" x \"%s\"" % (TARGETFOLDER, os.path.join(TARGETFOLDER,"chromium.7z")))
    shutil.move(os.path.join(TARGETFOLDER,"ungoogled-chromium-portable.exe"),os.path.join(TARGETFOLDER,"RCA.exe"))

filesToRemove = [ os.path.join(TARGETFOLDER, f) for f in [
    "imagemagick",
    "imagemagick.zip",
    "gifsicle",
    "gifsicle.zip",
    "chromedriver",
    "chromedriver.zip",
    "chromium.7z",
    "CHANGELOG.md",
    "README.md"
]]

for fileToRemove in filesToRemove:
    if os.path.exists(fileToRemove):
        if os.path.isdir(fileToRemove):
            shutil.rmtree(fileToRemove)
        else:
            os.remove(fileToRemove)

