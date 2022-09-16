import os
import queue
import subprocess
import threading

from pyhtmlgui import ObservableDict, Observable

from app.cardreader.cardReaderCard import CardReaderCard
from app.settings.settings import SettingsInstance


class CardReaderSlot(Observable):
    def __init__(self, device_name):
        super().__init__()
        self.device_name = device_name
        self.path = "/dev/%s" % self.device_name
        self.sdcard = None
        self.status = "idle"
        self.task_queue = queue.Queue()
        self.__worker_thread = threading.Thread(target=self._worker_thread, daemon=True)
        self.__worker_thread.start()

    def _reload(self):
        if self.status != "idle":
            return
        self.status = "reloading"
        self.notify_observers()
        try:
            stdout = subprocess.check_output("sudo fdisk -l %s 2>&1  |xargs -0 echo -ne" % self.path, shell=True, timeout=10, stderr=subprocess.STDOUT, ).decode("UTF-8")
        except:
            stdout = ""
        if stdout.find("No medium found") != -1:
            self.sdcard = None
        else:
            try:
                size = float(stdout.split("\n")[0].split(" ")[2])
                self.sdcard = CardReaderCard(self, size)
                self.sdcard._reload()
            except:
                self.sdcard = None
        self.status = "idle"
        self.notify_observers()


    def write_image_task(self, group, dev_id, name):
        if self.status != "idle":
            return
        self.status = "writing"
        self.notify_observers()
        self.task_queue.put(["write_image", [group, dev_id, name]])
        print("write image", group, dev_id, name)

    def update_card_task(self, group, dev_id, name):
        if self.status != "idle":
            return
        self.status = "update"
        self.notify_observers()
        self.task_queue.put(["update_card", [group, dev_id, name]])
        print("update_card", group, dev_id, name)

    def _worker_thread(self):
        while True:
            task = self.task_queue.get()
            task, options = task
            group, dev_id, name = options
            self.sdcard.info_id = dev_id
            self.sdcard.info_group = group
            self.sdcard.info_name = name
            if task == "write_image":
                self.sdcard.write_image()
                print("run task write_image", group, dev_id, name)

            if task == "update_card":
                self.sdcard.update_card()
                print("run task update_card", group, dev_id, name)

            self.status = "idle"
            self.notify_observers()

    def __eq__(self, other):
        return self.device_name == other.device_name

