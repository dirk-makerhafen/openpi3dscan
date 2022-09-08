import os
import re

from pyhtmlgui import Observable


class SettingsHostname(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.save = parent.save
        self.hostname = "openpi3dscan"

    def to_dict(self):
        return {
            "hostname": self.hostname,
        }

    def from_dict(self, data):
        self.hostname = data["hostname"]

    def set_hostname(self, new_hostname):
        new_hostname = re.sub('[^0-9a-zA-Z]+', '', new_hostname).lower()
        if len(new_hostname) < 3:
            return
        if new_hostname == self.hostname:
            return
        self.hostname = new_hostname
        self.save()
        self.notify_observers()
        open("/tmp/1", "w").write("%s\n" % self.hostname)
        os.system("sudo mv /tmp/1 /etc/hostname")
        os.system(
            "cat /etc/hosts | grep -v '192.168.99.' | grep -v localhost | grep -v raspberrypi | grep -v openpi3dscan > 1")
        os.system("echo '192.168.99.254   openpi3dscan' >> 1")
        os.system("echo '192.168.99.254   %s # openpi3dscan' >> 1" % self.hostname)
        os.system("echo '127.0.0.1      localhost' >> 1")
        os.system("sudo mv 1 /etc/hosts")
