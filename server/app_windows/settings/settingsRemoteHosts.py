import os
import re

from pyhtmlgui import Observable, ObservableList


class SettingsRemoteHosts(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.save = parent.save
        self.hosts =[]


    def to_dict(self):
        return {
            "hosts": list(self.hosts),
        }

    def from_dict(self, data):
        self.hosts = ObservableList(data["hosts"])
        return self

    def add_host(self, host):
        host = host.strip()
        if len(host) < 3:
            return
        if host not in self.hosts:
            self.hosts.append(host)
            self.save()
            self.notify_observers()

    def remove_host(self, host):
        host = host.strip()
        if host in self.hosts:
            self.hosts.remove(host)
            self.save()
            self.notify_observers()
