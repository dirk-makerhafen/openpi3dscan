import datetime
import math
import re
import threading
import time
import random
from pyhtmlgui import Observable
from app.devices.devices import DevicesInstance
from app.files.shots import ShotsInstance
from app.settings.settings import SettingsInstance


class Task_CreateShot(Observable):
    def __init__(self):
        super().__init__()
        self.shot_quality = "speed"
        self.status = "idle"
        self.shot_count_down = 0
        self.processed_percent = 0
        self.worker = None

    def set_status(self, value):
        self.status = value
        self.notify_observers()

    def run(self, shot_name, shot_quality):
        if self.worker is None:
            self.worker = threading.Thread(target=self._run, daemon=True, args=[shot_name, shot_quality])
            self.worker.start()

    def _run(self, shot_name, shot_quality):
        if self.status != "idle":
            self.worker = None
            return
        self.set_status("preparing")
        now = datetime.datetime.now()

        self.shot_quality = shot_quality
        shot_name = self._clean_name(shot_name)
        shot_name = "%s.%s.%s %s:%s:%s %s" % (now.year, ("%s" % now.month).zfill(2), ("%s" % now.day).zfill(2), ("%s" % now.hour).zfill(2), ("%s" % now.minute).zfill(2), ("%s" % now.second).zfill(2), shot_name)
        shot_name = shot_name.strip()
        shot_id = "%s.%s.%s %s%s%s" % (now.year, ("%s" % now.month).zfill(2), ("%s" % now.day).zfill(2), ("%s" % now.hour).zfill(2), ("%s" % now.minute).zfill(2), ("%s" % now.second).zfill(2))
        self.notify_observers()

        cameras    = [c for c in DevicesInstance().cameras.list()    if c.is_available]
        projectors = [c for c in DevicesInstance().projectors.list() if c.is_available]
        lights     = [c for c in DevicesInstance().lights.list()     if c.is_available]

        if len(cameras) == 0:
            print("no cameras for shot found")
            self.set_status("idle")
            self.worker = None
            return

        print("new shot: id:", shot_id, shot_name)
        random.shuffle(cameras)
        for device in cameras:
            device.lock(6)  # lock early to prevent previews and other querys to camera

        shot = ShotsInstance().create(shot_id, shot_name)

        if self.shot_quality == "quality":
            image_aquisition_time = 1.0 / 3.5
            seqs = SettingsInstance().sequenceSettingsQuality
        else:
            image_aquisition_time = 1.0 / 9.0
            seqs = SettingsInstance().sequenceSettingsSpeed

        global_start_time = time.time() + seqs.startup_delay + image_aquisition_time*2
        global_start_time = global_start_time - (global_start_time % image_aquisition_time)

        shot1_start_time = global_start_time
        shot1_end_time   = shot1_start_time + image_aquisition_time
        shot2_start_time = shot1_end_time + (seqs.image_delay * image_aquisition_time)
        shot2_end_time   = shot2_start_time + image_aquisition_time

        start_at = shot1_start_time + seqs.image1.offset/1000
        self.shot_count_down = math.floor(start_at - time.time())
        self.set_status("waiting")

        light_sequence = [
            [shot1_start_time + seqs.image1.offset/1000 , seqs.image1.light ],
            [shot2_start_time + seqs.image2.offset/1000 , seqs.image2.light ],
            [shot2_end_time + image_aquisition_time     , -1                ],
        ]
        projector_sequence = [
            [shot1_start_time + seqs.image1.offset/1000 , "enable" if seqs.image1.projection is True else "disable" ],
            [shot2_start_time + seqs.image2.offset/1000 , "enable" if seqs.image2.projection is True else "disable" ],
            [shot2_end_time   + image_aquisition_time   , "default"                                                 ]
        ]
        for device in projectors:
            device.projector.sequence(projector_sequence)

        for device in lights:
            device.light.sequence(light_sequence)

        projection_first = True
        if seqs.image1.projection is False and seqs.image2.projection is True:
            projection_first = False

        for device in cameras:
            device.camera.shots.create(shot, sequence=[shot1_end_time, shot2_end_time], shot_quality=self.shot_quality, projection_first=projection_first)

        while start_at > time.time():
            start_in = start_at - time.time()
            self.shot_count_down = int(round(start_in,0))
            sleeptime = start_in - math.floor(start_in)
            self.notify_observers()
            if sleeptime > 0:
                time.sleep(sleeptime + 0.01)

        self.set_status("shot")

        sleeptime = (shot2_end_time + 0.1) - time.time()
        if sleeptime > 0:
            time.sleep(sleeptime)
        else:
            time.sleep(0.2)

        processing_time = 9
        self.processed_percent = 0
        self.set_status("processing")
        for i in range(int(math.ceil(processing_time))):
            self.processed_percent = int(round((100/processing_time) * i ))
            self.notify_observers()
            time.sleep(1)

        self.set_status("idle")
        shot.notify_observers()
        self.worker = None

    def _clean_name(self, name):
        if name != "":
            name = name.replace("ä", "ae").replace("ü", "ue").replace("Ü", "Ue")
            name = name.replace("ö", "oe").replace("Ä", "Ae").replace("Ö", "Oe")
            name = re.sub('\s+', ' ', name)
            name = re.sub('[^A-Za-z0-9_. ]+', '', name)
            name = name.replace("..", ".").replace("__", "_").replace("  ", " ")
            name = name.strip()
            while name[-1] in ["_", "."]:
                name = name[:-1].strip()
            while name[0] in ["_", "."]:
                name = name[1:].strip()
        return name


_taskCreateShotInstance = None


def TaskCreateShotInstance():
    global _taskCreateShotInstance
    if _taskCreateShotInstance is None:
        _taskCreateShotInstance = Task_CreateShot()
    return _taskCreateShotInstance
