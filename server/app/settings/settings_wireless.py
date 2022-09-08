from pyhtmlgui import Observable
import threading, time, subprocess

class Settings_Wireless(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.save = parent.save
        self.ssid = ""
        self.password = ""
        self.status = "not_connected"
        self.ip = ""
        self.apply_worker = None
        self.status_worker = None

        self.get_connection_status()

    def set_status(self, status):
        self.status = status
        self.notify_observers()

    def to_dict(self):
        return {
            "ssid" : self.ssid,
            "password" : self.password,
        }
    def from_dict(self, data):
        self.ssid = data["ssid"]
        self.password = data["password"]

    def apply(self,ssid, password):
        if self.apply_worker is not None:
            return
        if ssid == self.ssid and password == self.password:
            return
        self.ssid = ssid
        self.password = password
        self.save()

        self.apply_worker = threading.Thread(target=self._apply, daemon=True)
        self.apply_worker.start()

    def _apply(self):
        t = '''
country=de
update_config=1
ctrl_interface=/var/run/wpa_supplicant
network={
    scan_ssid=1
    ssid="%s"
    psk="%s"
}
        ''' % (self.ssid, self.password)
        open("/etc/wpa_supplicant/wpa_supplicant.conf","w").write(t)
        self.set_status("configure")
        subprocess.call("sudo wpa_cli -i wlan0 reconfigure", shell=True)
        self.set_status("connecting")
        subprocess.call("sudo systemctl restart wpa_supplicant", shell=True)
        time.sleep(5)
        self.get_connection_status()
        self.apply_worker = None

    def get_connection_status(self):
        if self.status_worker is not None:
            return
        self.status_worker = threading.Thread(target=self._get_connection_status, daemon=True)
        self.status_worker.start()

    def _get_connection_status(self):
        for i in range(10):
            self.set_status("checking")
            time.sleep(2)
            try:
                stdout = subprocess.check_output("ifconfig wlan0|grep -i inet", shell=True, timeout=10, stderr=subprocess.STDOUT).decode("UTF-8")
                if "192.168" in stdout:
                    self.ip = "192.168%s" % (stdout.split("192.168")[1].split(" ")[0])
                    self.set_status("connected")
                    break
                else:
                    self.ip = ""
                    self.set_status("not_connected")
            except Exception as e:
                self.ip = ""
                self.set_status("not_connected")
        self.status_worker = None
