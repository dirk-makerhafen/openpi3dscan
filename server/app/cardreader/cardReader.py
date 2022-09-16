import queue
import subprocess
import threading
from pyhtmlgui import ObservableDict, Observable

from app.cardreader.cardReaderSlot import CardReaderSlot


class CardReader(Observable):
    def __init__(self):
        super().__init__()
        self.name = ""
        self.status = "idle"
        self.task_queue = queue.Queue()
        self.__worker_thread = threading.Thread(target=self._worker_thread, daemon=True)
        self.__worker_thread.start()
        self.cardReaderSlots = ObservableDict()
        self.task_queue.put(["reload", None])

    def _worker_thread(self):
        while True:
            task = self.task_queue.get()
            task, options = task
            if task == "reload":
                print(" task cardreload")
                self._reload()
            self.status = "idle"
            self.notify_observers()

    def reload_task(self):
        self.task_queue.put(["reload",None])

    def _reload(self):
        self.status = "reloading"
        self.notify_observers()

        try:
            stdout = subprocess.check_output("sudo mount | grep -i shots", shell=True, timeout=10, stderr=subprocess.STDOUT).decode("UTF-8")
            diskdevicename = stdout.split("/shots")[0].split(" ")[0].split("/")[2][:-1]
        except:
            diskdevicename = None

        try:
            stdout = subprocess.check_output("sudo dmesg | grep -i 'removable disk' | cut -d[ -f 3 | cut -d] -f1", shell=True, timeout=10, stderr=subprocess.STDOUT).decode("UTF-8")
        except:
            stdout = ""

        device_names = []
        for line in stdout.split("\n"):
            line = line.strip()
            if len(line) == 3 and line != diskdevicename:
                device_names.append(line)
        active_device_names = []
        for device_name in device_names:
            try:
                stdout = subprocess.check_output("ls -lah /dev/%s" % device_name, shell=True, timeout=10, stderr=subprocess.STDOUT)
                active_device_names.append(device_name)
            except:
                pass

        for key in list(self.cardReaderSlots.keys()):
            if key not in active_device_names:
                del self.cardReaderSlots[key]
        for device_name in active_device_names:
            if device_name not in self.cardReaderSlots:
                self.cardReaderSlots[device_name] = CardReaderSlot(device_name)
        for key, item in self.cardReaderSlots.items():
            item._reload()
        self.notify_observers()


_cardReaderInstance = None


def CardReaderInstance():
    global _cardReaderInstance
    if _cardReaderInstance is None:
        _cardReaderInstance = CardReader()
    return _cardReaderInstance
