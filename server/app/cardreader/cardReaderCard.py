import os
import subprocess

from pyhtmlgui import ObservableDict, Observable

from app.cardreader.cardReaderPartition import CardReaderPartition
from app.settings.settings import SettingsInstance


class CardReaderCard(Observable):
    def __init__(self, slot, size):
        super().__init__()
        self.slot = slot
        self.size = size
        self.partitions = ObservableDict()
        self.info_group = ""
        self.info_id = ""
        self.info_name = ""
        self.info_segment = ""
        self.info_row = ""

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
                self.partitions[partition_name] = CardReaderPartition(self, partition_name, size, fstype)
        self._reload_fs_info()

    def _reload_fs_info(self):
        self.info_group = ""
        self.info_name = ""
        self.info_id = ""

        keys = [k for k in self.partitions.keys()]
        mount_dir = "/tmp/mnt/%s" % self.slot.device_name
        self.shell("sudo mkdir -p '%s'" % mount_dir)
        if len(keys) == 2 and self.partitions[keys[1]].fstype.find("FAT32") != 1:
            self.shell('sudo mount %s %s ; sudo mount %s %s/boot' % (self.partitions[keys[1]].partition_name, mount_dir, self.partitions[keys[0]].partition_name, mount_dir))
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
            self.info_segment = ""
            self.info_row = ""
            if self.info_group == "camera":
                try:
                    self.info_segment = self.info_name.split("-")[0]
                    self.info_row = self.info_name.split("-")[1]
                except:
                    pass
            self.shell('sudo umount %s/boot ; sudo umount %s ; rm -d %s' % (mount_dir, mount_dir, mount_dir))

        self.notify_observers()

    def write_image(self):
        imgpath = "/opt/openpi3dscan/firmware/%s" % SettingsInstance().firmwareSettings.current_image
        if not os.path.exists(imgpath):
            print(imgpath, "does not exist")
            return
        self.shell('sudo dd if="%s" of="%s" bs=4M conv=fsync' % (imgpath, self.slot.path))
        self.shell("fsck -y %s1" % self.slot.path)
        self.shell("fsck -y %s2" % self.slot.path)
        self.shell('sudo parted %s resizepart 2 -- -1' % self.slot.path)
        self.shell('sudo e2fsck -y -f %s2' % self.slot.path)
        self.shell('sudo resize2fs %s2' % self.slot.path)
        self.update_card()

    def update_card(self):
        mount_dir = "/tmp/mnt/%s" % self.slot.device_name
        self.shell("fsck -y %s1" % self.slot.path)
        self.shell("fsck -y %s2" % self.slot.path)
        self.shell("sudo mkdir -p '%s' ; sudo mount %s2 %s ; sudo mount %s1 %s/boot " % (mount_dir, self.slot.path, mount_dir, self.slot.path, mount_dir))

        try:
            with open("%s/tmp/id.txt" % mount_dir, "w") as f:
                f.write(self.info_id)

            with open("%s/tmp/group.txt" % mount_dir, "w") as f:
                if self.info_group == "camera":    f.write("1")
                if self.info_group == "projector": f.write("2")

            with open("%s/tmp/device.settings" % mount_dir, "w") as f:
                f.write("TYPE = %s\n" % self.info_group)
                f.write("ID   = %s\n" % self.info_id)
                f.write("NAME = %s"   % self.info_name)
        except:
            print("failed to write Files")

        self.shell("sudo mkdir -p %s/opt/openpi3dscan/;" % mount_dir)
        self.shell("sudo rsync -r /opt/openpi3dscan/client %s/opt/openpi3dscan;" % mount_dir)
        self.shell("sudo mv %s/tmp/device.settings  %s/boot/device.settings;" % (mount_dir, mount_dir))
        self.shell("sudo mv %s/tmp/group.txt        %s/boot/group.txt;"       % (mount_dir, mount_dir))
        self.shell("sudo mv %s/tmp/id.txt           %s/boot/id.txt;"          % (mount_dir, mount_dir))
        self.shell('sudo chroot %s /bin/bash -c "cd /opt/openpi3dscan/client ; python3 install.py"' % mount_dir)
        self.shell('sudo umount %s/boot ; sudo umount %s ; rm -d %s' % (mount_dir, mount_dir, mount_dir))

        self._reload_fs_info()

    def shell(self, cmd):
        print("-> %s" % cmd)
        subprocess.call(cmd, shell=True)

