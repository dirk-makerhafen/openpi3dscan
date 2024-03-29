import random
import os


class Settings():
    def __init__(self):
        self.ID = "%s" % random.randint(1000, 99999)
        self.TYPE = "camera"
        self.NAME = "noname"
        self.VERSION = "2024.02.23-11:12"
        self.ROTATION = 0
        self.load()

    def save(self):
        s = ''
        s += 'TYPE = %s\n' % self.TYPE
        s += 'ID   = %s\n' % self.ID
        s += 'NAME = %s' % self.NAME
        open("/tmp/device.settings", "w").write(s)
        os.system("sudo cp /tmp/device.settings /boot/device.settings ")

    def load(self):
        settings_lines = open("/boot/device.settings", "r").read().split("\n")
        for line in settings_lines:
            if "=" in line:
                key, value = line.split("=")
                key = key.strip()
                value = value.strip()
                if key == "ID":
                    self.ID = value
                elif key == "TYPE":
                    self.TYPE = value
                elif key == "NAME":
                    self.NAME = value
                elif key == "ROTATION":
                    self.ROTATION = int(value)

Settings = Settings()
