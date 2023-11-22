import json
import random
import sys
import os
import glob
import shutil

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
storage_dir = "/home/openpi3dscan/shots"

class Installer():
    def __init__(self):
        self.device_id = None
        self.device_type = None
        self.name = None
        self.rotation = None
        self.install_after_reboot = False

    def _parse_args(self):
        self.install_after_reboot = "install_after_reboot" in sys.argv
        try:
            self.device_id = sys.argv[2]
            self.device_type = sys.argv[3]
            self.name = sys.argv[4]
            self.rotation = sys.argv[5]
        except:  # try reading from settings
            if not os.path.exists("/boot/device.settings"):
                print("No settings provided as installer arguments and no /boot/device.settings file exists, ERROR")
                exit(1)
            settings_str = open("/boot/device.settings", "r").read()
            self.device_id = settings_str.split("ID", 1)[1].split("=", 1)[1].split('\n')[0].strip()
            self.device_type = settings_str.split("TYPE", 1)[1].split("=", 1)[1].split('\n')[0].strip()
            self.name = settings_str.split("NAME", 1)[1].split("=", 1)[1].split('\n')[0].strip()
            try:
                self.rotation = int(settings_str.split("ROTATION", 1)[1].split("=", 1)[1].split('\n')[0].strip())
            except:
                self.rotation = 0

        self.device_id = int(self.device_id)
        if self.device_id < 1 or self.device_id > 9999:
            raise Exception("Id Must be beween 1 and 9999")
        if self.device_type not in ["camera", "projector", "light"]:
            raise Exception("no known device_type")

    def run(self):
        self._parse_args()
        self.clean_shots_dir()

        if SCRIPT_DIR != "/opt/openpi3dscan/client/src":
            self.shell("sudo mkdir -p /opt/openpi3dscan/client")
            self.shell("sudo rsync --delete -r %s/../* /opt/openpi3dscan/client/ " % SCRIPT_DIR)
        self.shell("sudo rm /opt/openpi3dscan/client/src/projection_*.fb")

        # FIX HOSTS
        self.shell('cat  /etc/hosts | grep -v CAM > 1')
        self.shell('echo "127.0.0.1 CAM%s" >> 1' % self.device_id)
        self.shell('echo "192.168.99.254 openpi3dscan" >> 1')
        self.shell('sudo chown root:root 1 ; sudo mv 1 /etc/hosts')

        # SETTINGS
        s = 'ID   = %s\n' % self.device_id
        s += 'TYPE = %s\n' % self.device_type
        s += 'NAME = %s\n' % self.name
        s += 'ROTATION = %s' % self.rotation
        open("/tmp/device.settings", "w").write(s)
        self.shell("sudo cp /tmp/device.settings /boot/device.settings ")

        if os.path.exists("/proc/uptime") and self.install_after_reboot == False:  # we are not in chroot
            # kill running process
            self.shell('ps ax|grep -i python |grep -i run.py | grep -v "run.py install"|cut -d\  -f 1|xargs sudo kill')

            # Fix ROUTING
            self.shell('sudo route add default gw 192.168.99.254')

            # fix legacy state of distri
            #legacy.raspbian.or
            if "legacy.raspbian.org" not in open("/etc/apt/sources.list","r").read():
                self.shell('echo "deb http://legacy.raspbian.org/raspbian/ stretch main contrib non-free rpi" >> /etc/apt/sources.list')

            # REQUIREMENTS
            self.shell('sudo DEBIAN_FRONTEND=noninteractive sudo dpkg --configure -a')
            self.shell('sudo DEBIAN_FRONTEND=noninteractive apt-get update', tries=2)
            self.shell(
                'sudo DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" remove python3-numpy man-db')
            self.shell(
                'sudo DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" install '
                'python-pygame python-picamera python3-rpi.gpio chrony ntpdate python3-pip libopenjp2-7 ffmpeg libgstreamer1.0-0 '
                'imagemagick python3-smbus i2c-tools  libqt4-test libqtgui4 libcblas3 libatlas-base-dev libjasper-dev  '
                'libgtk2.0-dev libcv2.4 libgtk-3-0 python-wxgtk3.0-dev  libopenblas-base libopenblas-dev   '
                'python-dev gcc gfortran  libhdf5-dev libhdf5-serial-dev', tries=2)
            self.shell('sudo DEBIAN_FRONTEND=noninteractive apt-get -y autoclean')
            self.shell('sudo DEBIAN_FRONTEND=noninteractive apt-get -y clean')
            self.shell("cd /opt/openpi3dscan/client/ ; sudo python3 -m pip install -r requirements.txt", tries=2)
            # if shell("sudo python3 -c 'import cv2'") != 0:
            #    shell("cd /opt/openpi3dscan/client/ ; sudo pip3 install  --force-reinstall  --ignore-installed  opencv-contrib-python==3.4.6.27 numpy==1.13.3")
            if self.device_type == "light":
                self.shell('sudo raspi-config nonint do_i2c 0')

            #  NTP/chrony chrony
            self.shell('sudo systemctl stop systemd-timesyncd ; ')
            self.shell('sudo systemctl disable systemd-timesyncd ; ')
            self.shell('cat /etc/chrony/chrony.conf | grep -v "server 192.168." | grep -v "^pool " > 1 ')
            self.shell('echo "server 192.168.99.254 prefer iburst minpoll 4 maxpoll 7" >> 1')
            self.shell('sudo mv 1 /etc/chrony/chrony.conf')
            self.shell('sudo systemctl enable chrony')
            self.shell('sudo /etc/init.d/chrony restart')
            if self.device_type == "camera":
                self.download_shots()

        # Add user for ssh login
        self.shell('sudo useradd openpi3dscan')
        self.shell('echo openpi3dscan:openpi3dscan | sudo chpasswd')
        self.shell(
            'echo "openpi3dscan ALL=(ALL) NOPASSWD: ALL" > 1 ; sudo chown root:root 1 ; sudo mv 1 "/etc/sudoers.d/010_openpi3dscan-nopasswd"')
        self.shell('sudo mkdir -p /home/openpi3dscan/shots ; sudo chmod 777 /home/openpi3dscan/shots')
        self.shell('sudo chown -R openpi3dscan:openpi3dscan /home/openpi3dscan ')

        # AUTOSTART
        self.shell('cat /etc/rc.local | grep -v openpi3dscan | grep -v "exit 0" | grep -v "192.168.99" | grep -v camsoft > 1')
        if os.path.exists("/proc/uptime") and self.install_after_reboot == False:  # we are not in chroot
            self.shell('echo "sudo nice -n -2 python3 /opt/openpi3dscan/client/run.py &" >> 1')
        else:
            self.shell('echo "sudo python3 /opt/openpi3dscan/client/run.py install &" >> 1')
        self.shell('echo "sudo route add default gw 192.168.99.254" >> 1')
        self.shell('echo "exit 0" >> 1')
        self.shell('sudo chown root:root 1 ; sudo chmod +x 1 ; sudo mv 1 /etc/rc.local')

        if len(sys.argv) == 2 and os.path.exists("/proc/uptime"):  # most likely autostarted install
            self.shell("sudo reboot &")

    def shell(self, cmd, tries=1):
        r = 0
        for i in range(tries):
            if i >= 1:
                print("repeat command: %s" % cmd)
            else:
                print(cmd)
            r = os.system(cmd)
            if r == 0:
                break
        return r

    def clean_shots_dir(self, min_disk_free=300):
        for path in glob.glob(os.path.join(storage_dir, "20*")):
            nimg = os.path.join(path, "normal.jpg")
            pimg = os.path.join(path, "projection.jpg")
            if os.path.exists(nimg) and os.path.getsize(nimg) < 10000:
                os.remove(nimg)
            if os.path.exists(pimg) and os.path.getsize(pimg) < 10000:
                os.remove(pimg)
            if not os.path.exists(nimg) and not os.path.exists(pimg):
                shutil.rmtree(path)
        if shutil.disk_usage("/")[2] / 1024 / 1024 > min_disk_free:
            return

        paths = [
            os.path.join("/3dscan/", "*.jpg"),
            os.path.join(storage_dir, "*")
        ]
        for path in paths:
            shots = sorted([path for path in glob.glob(path)])
            free = shutil.disk_usage("/")[2] / 1024 / 1024
            while free < min_disk_free and len(shots) > 0:
                for i in range(10):
                    if len(shots) == 0: break
                    os.system("rm -r '%s'" % shots[0])
                    del shots[0]
                free = shutil.disk_usage("/")[2] / 1024 / 1024

    def download_shots(self, min_disk_free=1000):
        try:
            import requests
        except:
            print("failed to import python requests")
            return
        total, used, free = shutil.disk_usage("/")
        free = free / 1024 / 1024
        if free > min_disk_free:
            try:
                r = requests.get("http://192.168.99.254/shots/list", timeout=20).text
            except Exception as e:
                print(e)
                return
            shot_ids = json.loads(r)
            shot_ids.sort(reverse=True)
            for shot_id in shot_ids:
                shot_dir = os.path.join(storage_dir, shot_id)
                if not os.path.exists(shot_dir):
                    for image_type in ["normal", "projection"]:
                        try:
                            img = requests.get(
                                "http://192.168.99.254/shots/%s/normal/%s/%s-%s.jpg" % (shot_id, image_type, self.name.lower(),image_type[0]),
                                timeout=25).content
                            if len(img) < 30000:
                                continue
                            if not os.path.exists(shot_dir):
                                os.mkdir(shot_dir)
                            with open(os.path.join(shot_dir, "%s.jpg" % image_type), "wb") as f:
                                f.write(img)
                        except Exception as e:
                            print("error1:", e)
                if random.randint(0, 4) == 1:
                    total, used, free = shutil.disk_usage("/")
                    free = free / 1024 / 1024
                    if free < min_disk_free:
                        break


'''
#i2cdetect -y 1

wget https://project-downloads.drogon.net/wiringpi-latest.deb
sudo dpkg -i wiringpi-latest.deb

code




To get over this error I changed line 105 in file /usr/local/lib/python3.9/dist-packages/Adafruit_GPIO/Platform.py

Original:

elif match.group(1) == 'BCM2835':

Changed:

elif match.group(1) == 'BCM2711':


'''
# shell("sudo reboot")