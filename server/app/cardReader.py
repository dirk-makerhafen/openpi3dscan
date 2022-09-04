import os
import queue
import subprocess
import threading

from pyhtmlgui import ObservableDict, Observable
from settings import SettingsInstance


def shell(cmd):
    print("-> %s" % cmd)
    subprocess.call(cmd, shell=True)

class Partition(Observable):
    def __init__(self, card, partition_name, size, fstype):
        super().__init__()
        self.card = card
        self.partition_name = partition_name
        self.size = size
        self.fstype = fstype
        self.mount_dir = None


class SDCard(Observable):
    def __init__(self, slot, size):
        super().__init__()
        self.slot = slot
        self.size = size
        self.partitions = ObservableDict()
        self.info_group = ""
        self.info_id = ""
        self.info_name = ""

    def _reload(self):
        try:
            stdout = subprocess.check_output("sudo fdisk -l %s 2>&1  |xargs -0 echo -ne" % self.slot.path, shell=True, timeout=10, stderr=subprocess.STDOUT, ).decode("UTF-8")
        except:
            stdout = ""
        partition_names = []
        for line in stdout.split("\n"):
            line = ' '.join(line.split()).strip()
            if line.startswith(self.slot.path):
                partition_name = line.split(" ")[0]
                size = line.split(" ")[4]
                fstype = " ".join(line.split(" ")[6:])
                partition_names.append([partition_name, fstype, size])
        for key in list(self.partitions.keys()):
            if key not in [p[0] for p in partition_names]:
                del self.partitions[key]
        for partition in partition_names:
            partition_name, fstype, size = partition
            if partition_name not in self.partitions:
                self.partitions[partition_name] = Partition(self, partition_name, size, fstype)
        self._reload_fs_info()


    def _reload_fs_info(self):
        self.info_group = ""
        self.info_name = ""
        self.info_id = ""

        keys = [k for k in self.partitions.keys()]
        mount_dir = "/tmp/mnt/%s" % self.slot.device_name
        shell("sudo mkdir -p '%s'" % mount_dir)
        if len(keys) == 2 and self.partitions[keys[1]].fstype.find("FAT32") != 1:
            shell('sudo mount %s %s ; sudo mount %s %s/boot' % ( self.partitions[keys[1]].partition_name, mount_dir,self.partitions[keys[0]].partition_name, mount_dir))
            try:
                devsettings = open("%s/boot/device.settings" % mount_dir, "r").read()
                self.info_group = devsettings.split("TYPE")[1].split("=")[1].split("\n")[0].strip()
                self.info_id = devsettings.split("ID")[1].split("=")[1].split("\n")[0].strip()
                self.info_name =  devsettings.split("NAME")[1].split("=")[1].split("\n")[0].strip()
            except:
                try:
                    self.info_group = open("%s/boot/group.txt" % mount_dir, "r").read().strip()
                    if self.info_group == "1": self.info_group = "camera"
                    if self.info_group == "2": self.info_group = "projector"
                    self.info_id = open("%s/boot/id.txt" % mount_dir, "r").read().strip()
                except:
                    pass
            shell('sudo umount %s/boot ; sudo umount %s ; rm -d %s' % (mount_dir, mount_dir, mount_dir))

        self.notify_observers()

    def write_image(self):
        imgpath = "/opt/openpi3dscan/server/firmware/%s" % SettingsInstance().firmwareSettings.current_image
        if not os.path.exists(imgpath):
            return
        shell('sudo dd if="%s" of="%s" bs=4M conv=fsync' % (imgpath, self.slot.path))
        shell("fsck -y %s1" % self.slot.path)
        shell("fsck -y %s2" % self.slot.path)
        shell('sudo parted %s resizepart 2 -- -1' % self.slot.path)
        shell('sudo e2fsck -y -f %s2' % self.slot.path)
        shell('sudo resize2fs %s2' % self.slot.path)
        self.update_card()

    def update_card(self):
        mount_dir = "/tmp/mnt/%s" % self.slot.device_name
        shell("fsck -y %s1" % self.slot.path)
        shell("fsck -y %s2" % self.slot.path)
        shell("sudo mkdir -p '%s' ; sudo mount %s2 %s ; sudo mount %s1 %s/boot " % (mount_dir, self.slot.path, mount_dir, self.slot.path, mount_dir))

        try:
            with open("%s/tmp/id.txt" % mount_dir, "w") as f:
                f.write( self.info_id )

            with open("%s/tmp/group.txt" % mount_dir, "w") as f:
                if self.info_group == "camera":    f.write("1")
                if self.info_group == "projector": f.write("2")

            with open("%s/tmp/device.settings" % mount_dir, "w") as f:
                f.write("TYPE = %s\n" % self.info_group)
                f.write("ID   = %s\n" % self.info_id)
                f.write("NAME = %s"   % self.info_name)
        except:
            print("failed to write Files")

        shell("sudo mkdir -p %s/opt/openpi3dscan/;" % mount_dir)
        shell("sudo rsync -r /opt/openpi3dscan/client %s/opt/openpi3dscan;" % mount_dir)
        shell("sudo mv %s/tmp/device.settings  %s/boot/device.settings;" % (mount_dir, mount_dir))
        shell("sudo mv %s/tmp/group.txt        %s/boot/group.txt;"       % (mount_dir, mount_dir))
        shell("sudo mv %s/tmp/id.txt           %s/boot/id.txt;"          % (mount_dir, mount_dir))
        shell('sudo chroot %s /bin/bash -c "cd /opt/openpi3dscan/client ; python3 install.py"' % mount_dir)
        shell('sudo umount %s/boot ; sudo umount %s ; rm -d %s' % (mount_dir, mount_dir, mount_dir))

        self._reload_fs_info()


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
                self.sdcard = SDCard(self, size)
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
        self.task_queue.put(["write_image", [ group, dev_id, name]])
        print("write image", group, dev_id, name)

    def update_card_task(self, group, dev_id, name):
        if self.status != "idle":
            return
        self.status = "update"
        self.notify_observers()
        self.task_queue.put(["update_card", [ group, dev_id, name]])
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
            stdout = subprocess.check_output("sudo dmesg | grep -i 'removable disk' | cut -d[ -f 3 | cut -d] -f1", shell=True, timeout=10, stderr=subprocess.STDOUT).decode("UTF-8")
        except:
            stdout = ""
        device_names = []
        for line in stdout.split("\n"):
            line = line.strip()
            if len(line) == 3:
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
