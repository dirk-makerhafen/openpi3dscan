import datetime
import glob
import threading

from PIL import Image
from bottle import run, route
import time
import random
import json
import os
import src.settings
from src.heartbeat import HeartbeatInstance
import sys

NOWAIT = False

def device_id():
    return json.dumps({
        "time"      : time.time(),
        "id"        : src.settings.Settings.ID,
        "type"      : src.settings.Settings.TYPE,
        "name"      : src.settings.Settings.NAME,
        "version"   : src.settings.Settings.VERSION,
    })

def shutdown():
    os.system('sudo shutdown -h now &')
    return ""

def reboot():
    os.system('sudo reboot &')
    return ""

def wait(min_time=20, max_time=60):
    if max_time < min_time:
        raise Exception("max time > min time")
    if NOWAIT is False:
        time.sleep(random.randint(min_time, max_time))

def stop_other_processes():
    if NOWAIT is False:
        os.system("ps ax | grep -i listen.py | cut -d? -f1 | cut -dp -f1 | xargs sudo kill")
        os.system("sudo /etc/init.d/apache2 stop")
        os.system("sudo /etc/init.d/triggerhappy stop")
        os.system("sudo /etc/init.d/cron stop")
        os.system("sudo /etc/init.d/rsyslog stop")
        os.system("sudo service rsyslog stop")
        os.system("ps ax | grep -i listen.py | cut -d? -f1 | cut -dp -f1 | xargs sudo kill -9")
        wait(5, 10)
        os.system("sudo sh -c 'sync ; echo 3 > /proc/sys/vm/drop_caches'") # free some memory
        wait(10, 30)

def heartbeat():
    def f():
        time.sleep(random.randint(1,4))
        HeartbeatInstance().send()
    threading.Thread(target=f, daemon=True).start()

def import_old_scans():
    def f():
        files = glob.glob(os.path.join("/3dscan/", "*.jpg"))
        old_shot_ids = set([f.split("/")[-1].split("_")[0] for f in files])
        print(old_shot_ids)
        for old_shot_id in old_shot_ids:
            if os.path.exists("/3dscan/%s_1.jpg" % old_shot_id):
                new_shot_id = "0000.00.00 %s" % (old_shot_id)
                print("new shot id", new_shot_id)
                if not os.path.exists("/home/openpi3dscan/shots/%s" % new_shot_id):
                    pass
                    # os.mkdir("/home/openpi3dscan/shots/%s" % new_shot_id)
                # os.system("mv '/3dscan/%s_1.jpg' '/home/openpi3dscan/shots/%s/normal.jpg'" % (old_shot_id, new_shot_id))
                # os.system("mv '/3dscan/%s_2.jpg' '/home/openpi3dscan/shots/%s/projection.jpg'" % (old_shot_id, new_shot_id))
                # os.system("rm '/3dscan/%s_3.jpg'" % old_shot_id)#
                try:
                    img = Image.open('/home/openpi3dscan/shots/%s/normal.jpg' % new_shot_id)
                    img = img.resize([800, 600])
                    img.save('/home/openpi3dscan/shots/%s/normal_preview.jpg' % new_shot_id, format="jpeg", quality=85)
                except Exception as e:
                    print("Failed to create preview for normal", e)
                try:
                    img = Image.open('/home/openpi3dscan/shots/%s/projection.jpg' % new_shot_id)
                    img = img.resize([800, 600])
                    img.save('/home/openpi3dscan/shots/%s/projection_preview.jpg' % new_shot_id, format="jpeg", quality=85)
                except Exception as e:
                    print("Failed to create preview for projection", e)


    threading.Thread(target=f, daemon=True).start()


if __name__ == "__main__":

    if "nowait" in sys.argv:
        NOWAIT = True

    wait(10,60)

    start = time.time()
    while True:
        if HeartbeatInstance().send() is True: #if master is up we start
            break
        wait(60, 90)

    stop_other_processes()
    os.system("sudo /etc/init.d/chrony restart")

    wait(1, 100)

    route("/id")(device_id)
    route("/shutdown")(shutdown)
    route("/reboot")(reboot)
    route("/heartbeat")(heartbeat)
    quiet = False
    if src.settings.Settings.TYPE == "camera":
        from src import camera
        camera_api = camera.CameraAPI()
        HeartbeatInstance().hardware = camera_api.camera

    if src.settings.Settings.TYPE == "projector":
        from src import projector
        projector_api = projector.ProjectorAPI()
        quiet = True

    if src.settings.Settings.TYPE == "light":
        from src import light
        light_api = light.LightAPI()

    HeartbeatInstance().start()

    run(host='0.0.0.0', port=8080, server='paste', quiet=quiet, debug=True)
