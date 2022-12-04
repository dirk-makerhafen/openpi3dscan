import os, shutil
import requests

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
BUILDFOLDER = os.path.join(SCRIPT_DIR, "build", "bin")
TARGETFOLDER = os.path.join(SCRIPT_DIR, "dist", "RCAutomation", "bin")

def download(url, filename):
    with open(os.path.join(BUILDFOLDER, filename),"wb") as f:
        f.write(requests.get(url).content)

def unzip(filename):
    os.system("cd \"%s\" & powershell -command \"Expand-Archive '%s'\"" % (BUILDFOLDER, filename))

def un7zip(filename):
    os.system("cd \"%s\" & \"c:\\Program Files\\7-Zip\\7z.exe\" x \"%s\"" % (BUILDFOLDER, os.path.join(BUILDFOLDER, filename)))


os.system("pyinstaller --noconfirm app_windows.spec")
os.system("pyinstaller --noconfirm --onefile app_windows/rc_rebase.py")

if not os.path.exists(BUILDFOLDER):
    os.mkdir(BUILDFOLDER)

if not os.path.exists(os.path.join(BUILDFOLDER,"convert.exe")):
    download("https://imagemagick.org/archive/binaries/ImageMagick-7.1.0-portable-Q16-x64.zip", "imagemagick.zip")
    unzip("imagemagick.zip")
    shutil.move(os.path.join(BUILDFOLDER,"imagemagick","convert.exe"), BUILDFOLDER)

if not os.path.exists(os.path.join(BUILDFOLDER,"gifsicle.exe")):
    download("https://eternallybored.org/misc/gifsicle/releases/gifsicle-1.92-win64.zip", "gifsicle.zip")
    unzip("gifsicle.zip")
    shutil.move(os.path.join(BUILDFOLDER,"gifsicle","gifsicle-1.92","gifsicle.exe"), BUILDFOLDER)

if not os.path.exists(os.path.join(BUILDFOLDER,"chromedriver.exe")):
    download("https://chromedriver.storage.googleapis.com/103.0.5060.134/chromedriver_win32.zip", "chromedriver.zip")
    unzip("chromedriver.zip")
    shutil.move(os.path.join(BUILDFOLDER,"chromedriver","chromedriver.exe"), BUILDFOLDER)

if not os.path.exists(os.path.join(BUILDFOLDER,"chromium")):
    download("https://github.com/portapps/ungoogled-chromium-portable/releases/download/103.0.5060.114-15/ungoogled-chromium-portable-win64-103.0.5060.114-15.7z", "chromium.7z")
    un7zip("chromium.7z")
    shutil.move(os.path.join(BUILDFOLDER,"app"), os.path.join(BUILDFOLDER,"chromium"))

filesToRemove = [ os.path.join(BUILDFOLDER, f) for f in [
    "imagemagick",
    "imagemagick.zip",
    "gifsicle",
    "gifsicle.zip",
    "chromedriver",
    "chromedriver.zip",
    "chromium.7z",
    "CHANGELOG.md",
    "README.md",
    "ungoogled-chromium-portable.exe",
    "portapp.json",
    "portapp-prev.json",
]]

for fileToRemove in filesToRemove:
    if os.path.exists(fileToRemove):
        if os.path.isdir(fileToRemove):
            shutil.rmtree(fileToRemove)
        else:
            os.remove(fileToRemove)

shutil.copytree(BUILDFOLDER, TARGETFOLDER)

if not os.path.exists(os.path.join(TARGETFOLDER, "rc_rebase.exe")):
    shutil.move(os.path.join(SCRIPT_DIR, "dist", "rc_rebase.exe"), os.path.join(TARGETFOLDER, "rc_rebase.exe"))
