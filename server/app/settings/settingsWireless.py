import subprocess
import threading
import time
from pyhtmlgui import Observable, ObservableList


class WirelessNetwork():
    def __init__(self, bssid, ssid, frequency, channel, signal):
        self.bssid = bssid
        self.ssid = ssid
        self.frequency = frequency
        self.channel = channel
        self.signal = signal


class SettingsWireless(Observable):
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
        self.scan_worker = None
        self.get_connection_status()
        self.wireless_networks = []

    def set_status(self, status):
        self.status = status
        self.notify_observers()

    def to_dict(self):
        return {
            "ssid": self.ssid,
            "password": self.password,
        }

    def from_dict(self, data):
        self.ssid = data["ssid"]
        self.password = data["password"]

    def apply(self, ssid, password):
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
        if ";" in self.ssid and self.ssid.count(":") == 5:
            ssid = self.ssid.split(";")[0]
            bssid = "bssid=%s" % self.ssid.split(";")[1]
        else:
            ssid = self.ssid
            bssid = "#no bssid"

        t = '''
country=de
update_config=1
ctrl_interface=/var/run/wpa_supplicant
network={
    scan_ssid=1
    ssid="%s"
    %s
    psk="%s"
}
        ''' % (ssid, bssid, self.password)
        open("/etc/wpa_supplicant/wpa_supplicant.conf", "w").write(t)
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
                stdout = subprocess.check_output("ifconfig wlan0|grep -i inet", shell=True, timeout=10,stderr=subprocess.STDOUT).decode("UTF-8")
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

    def clear(self):
        self.wireless_networks = []
        self.notify_observers()

    def scan(self):
        if self.scan_worker is not None:
            return
        self.scan_worker = threading.Thread(target=self._scan, daemon=True)
        self.scan_worker.start()

    def _scan(self):
        self.wireless_networks = []
        self.notify_observers()

        stdout = subprocess.check_output("sudo iwlist wlan0 scan", shell=True, timeout=30,stderr=subprocess.STDOUT).decode("UTF-8")
        parts = stdout.split("Address: ")
        for part in parts:
            try:
                bssid = part.split("\n")[0].split("\n")[0].strip()
                ssid = part.split("ESSID:\"")[1].split('"')[0].strip()
                frequency = "2.4ghz"
                if "Frequency:5" in part:
                    frequency = "5ghz"
                channel = part.split("Channel:")[1].split("\n")[0].strip()
                signal = [int(x) for x in part.split("Quality=")[1].split(" ")[0].strip().split("/")]
                signal = int(100.0/signal[1]*signal[0])
                self.wireless_networks.append(WirelessNetwork(bssid,ssid,frequency,channel, signal))
            except:
                pass
        self.wireless_networks = sorted(self.wireless_networks, key=lambda wn: (wn.ssid, wn.frequency, wn.signal, wn.channel ))
        self.scan_worker = None
        self.notify_observers()
