from bottle import run, route
import json, os, time, threading, random
from src.heartbeat import HeartbeatInstance
import src.settings


class HttpEndpoints():
    def __init__(self):
        route("/id")(self.device_id)
        route("/shutdown")(self.shutdown)
        route("/reboot")(self.reboot)
        route("/heartbeat")(self.heartbeat)

    def device_id(self):
        return json.dumps({
            "time": time.time(),
            "id": src.settings.Settings.ID,
            "type": src.settings.Settings.TYPE,
            "name": src.settings.Settings.NAME,
            "version": src.settings.Settings.VERSION,
        })

    def shutdown(self):
        os.system('sudo shutdown -h now &')
        return ""

    def reboot(self):
        os.system('sudo reboot &')
        return ""


    def heartbeat(self):
        def f():
            time.sleep(random.randint(1,4))
            HeartbeatInstance().send()
        threading.Thread(target=f, daemon=True).start()
