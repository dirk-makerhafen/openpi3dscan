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


if __name__ == "__main__":

    if "nowait" in sys.argv:
        NOWAIT = True

    wait(20,60)

    start = time.time()
    while True:
        if HeartbeatInstance().send() is True: #if master is up we start
            break
        time.sleep(60)
        #if start < time.time() - 600: # exit after 10 minutes without master
        #    exit(0)

    stop_other_processes()
    wait(10, 60)

    route("/id")(device_id)
    route("/shutdown")(shutdown)
    route("/reboot")(reboot)
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
