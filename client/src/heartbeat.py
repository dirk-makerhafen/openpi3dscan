import threading
import time, requests, random
from .settings import Settings
import shutil

class Heartbeat():
    def __init__(self):
        self._locked = False
        self.hardware = None

    def lock(self):
        self._locked = True

    def unlock(self):
        self._locked = False

    def start(self):
        self.t = threading.Thread(target=self._worker, daemon=True)
        self.t.start()

    def send(self):
        while self._locked is True:
            time.sleep(random.randint(10,30))
        total, used, free = shutil.disk_usage("/")
        uptime_seconds = -1
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
        except:
            pass
        data = {
            "ID"      : Settings.ID,
            "TYPE"    : Settings.TYPE,
            "NAME"    : Settings.NAME,
            "VERSION" : Settings.VERSION,
            "DISK"    : [int(total/1024/1024) , int(free/1024/1024)],
            "UPTIME"  : uptime_seconds,
        }
        if self.hardware is not None:
            try:
                data.update(self.hardware.to_dict())
            except Exception as e:
                pass
        try:
            r = requests.post("http://192.168.99.254/heartbeat", json=data, timeout=20).text
        except Exception as e:
            print(e)
            r = None
        return r == "OK"

    def _worker(self):
        time.sleep(20)
        while True:
            if self.send() is True:
                time.sleep(random.randint(300, 500))
            else:
                time.sleep(random.randint(30, 40))


_heartbeatInstance = None
def HeartbeatInstance():
    global _heartbeatInstance
    if _heartbeatInstance is None:
        _heartbeatInstance = Heartbeat()
    return _heartbeatInstance
