import math
import threading
import time
from multiprocessing.pool import ThreadPool
import random

from pyhtmlgui import Observable

from app.devices.devices import DevicesInstance
from app.settings.settings import SettingsInstance
from views.imageCarousel.imageCarouselLive import PreviewQueueInstance


class Task_CameraBalance(Observable):
    def __init__(self):
        super().__init__()
        self.name = "CameraBalance"
        self.status = "idle"
        self.worker = None

    def set_status(self, value):
        self.status = value
        self.notify_observers()

    def run(self):
        if self.worker is None:
            self.worker = threading.Thread(target=self._run, daemon=True)
            self.worker.start()

    def _run(self):
        if self.status != "idle":
            return
        self.set_status("active")
        cameras = DevicesInstance().cameras.list()
        cameras = [c for c in cameras if c.status == "online" or c.status == "warmup"]
        lc = len(cameras)
        if lc == 0:
            self.set_status("idle")
            return
        random.shuffle(cameras)

        for device in cameras:
            device.camera.settings.locked = True  # prevent changes of settings by heartbeat
            PreviewQueueInstance().get_image(device_id=device.device_id)  # trigger pll in case cameras are in sleep
        time.sleep(1)  # wait for heartbeat queue to empty

        for device in cameras:
            device.camera.settings.set_shutter_speed(0)
            device.camera.settings.set_exposure_mode(SettingsInstance().cameraSettings.exposure_mode)
            device.camera.settings.set_iso(SettingsInstance().cameraSettings.iso)
            device.camera.settings.set_awb_mode(SettingsInstance().cameraSettings.awb_mode)

        time.sleep(5)
        results_exposure_speed = []
        results_awg_gains = []
        cameras_exposure_speed = {}
        cameras_awb_gains = {}

        try:
            with ThreadPool(20) as p:
                for _ in range(5):
                    results_exposure_speed.append(p.map_async(lambda device: device.camera.settings.get_exposure_speed(), cameras))
                    results_awg_gains.append(p.map_async(lambda device: device.camera.settings.get_awb_gains(), cameras))
                    time.sleep(1)
            for index, r in enumerate(results_exposure_speed):
                results_exposure_speed[index] = r.get(timeout=30)
            for index, r in enumerate(results_awg_gains):
                results_awg_gains[index] = r.get(timeout=30)
            for index, camera in enumerate(cameras):
                r = [r[index] for r in results_exposure_speed if r[index] is not None and r[index] > 0 ]
                if len(r) == 0: continue
                cameras_exposure_speed[camera.name] = sum(r) / len(r)
                r = [r[index] for r in results_awg_gains if r[index] is not None and r[index][0] > 0 and r[index][1] > 0]
                if len(r) == 0: continue
                cameras_awb_gains[camera.name] = [sum([g[0] for g in r]) / len(r), sum([g[1] for g in r]) / len(r)]
        except Exception as e:
            print("Failed1:", e)

        try:
            per_segment_exposure_speeds, per_segment_awb_gains = self._calculate(cameras_exposure_speed, cameras_awb_gains)
        except Exception as e:
            print("Failed2:", e)

        # set awb_mode to off
        for device in cameras:
            device.camera.settings.set_exposure_mode("off")
            device.camera.settings.set_awb_mode("off")

        try:
            SettingsInstance().cameraSettings.per_segment_shutter_speeds = per_segment_exposure_speeds
            SettingsInstance().cameraSettings.per_segment_awb_gains = per_segment_awb_gains

            time.sleep(3)
            for device in cameras:
                device.camera.settings.locked = False
            with ThreadPool(10) as p:
                p.map_async(lambda device: device.camera.settings.get_exposure_speed(), cameras)
        except Exception as e:
            print("Failed2:", e)
        self.set_status("idle")
        self.worker = None

    def _calculate(self, cameras_exposure_speed, cameras_awb_gains):
        per_segment_exposure_speeds = []
        per_segment_awb_gains = []
        nr_of_segments = SettingsInstance().settingsScanner.segments
        rows = SettingsInstance().settingsScanner.cameras_per_segment
        if SettingsInstance().settingsScanner.camera_one_position == "top":
            doublerows = [rows-2, rows-3]
        else:
            doublerows = [3, 4]

        for segment in range(0, nr_of_segments):
            next_segment = segment + 1 if segment != nr_of_segments-1 else  0
            nextnext_segment = next_segment + 1 if next_segment != nr_of_segments-1 else  0
            prev_segment = segment - 1 if segment !=  0 else nr_of_segments-1
            prevprev_segment = prev_segment - 1 if prev_segment !=  0 else nr_of_segments-1
            cameras  = DevicesInstance().get_cameras_by_segment(segment)
            cameras += DevicesInstance().get_cameras_by_segment(next_segment)
            cameras += DevicesInstance().get_cameras_by_segment(nextnext_segment)
            cameras += DevicesInstance().get_cameras_by_segment(prev_segment)
            cameras += DevicesInstance().get_cameras_by_segment(prevprev_segment)
            doublecams = []
            for row in doublerows:
                for device in cameras:
                    if device.name.endswith("CAM%s" % row):
                        doublecams.append(device)
            cameras += doublecams

            cameras = [ c for c in cameras if c.name in cameras_exposure_speed and c.name in cameras_awb_gains]
            cameras = [ c for c in cameras if cameras_exposure_speed[c.name] is not None and cameras_exposure_speed[c.name] >= 0 ]
            cameras = [ c for c in cameras if cameras_awb_gains[c.name]      is not None and cameras_awb_gains[c.name][0] > 0 and cameras_awb_gains[c.name][1] > 0  ]

            badcameras = []
            cameras = sorted(cameras, key=lambda x:cameras_exposure_speed[x.name])
            badcameras.extend(cameras[:2])
            badcameras.extend(cameras[-2:])
            cameras = sorted(cameras, key=lambda x:cameras_awb_gains[x.name][0])
            badcameras.extend(cameras[:2])
            badcameras.extend(cameras[-2:])
            cameras = sorted(cameras, key=lambda x:cameras_awb_gains[x.name][1])
            badcameras.extend(cameras[:2])
            badcameras.extend(cameras[-2:])

            cameras1 = [ c for c in cameras if c not in badcameras and (c.status == "online" or c.status == "warmup")]
            if len(cameras1) == 0:
                cameras = [c for c in cameras if (c.status == "online" or c.status == "warmup")]
            else:
                cameras = cameras1
            avg_exposure_speed = int(sum([cameras_exposure_speed[c.name] for c in cameras] ) / len(cameras))
            per_segment_exposure_speeds.append(avg_exposure_speed)

            awb_gains = [cameras_awb_gains[c.name] for c in cameras ]
            per_segment_awb_gains.append([round(sum([g[0] for g in awb_gains]) / len(awb_gains), 3),round(sum([g[1] for g in awb_gains]) / len(awb_gains), 3)])
        print("per_segment_exposure_speeds", per_segment_exposure_speeds)
        print("per_segment_awb_gains", per_segment_awb_gains)
        return per_segment_exposure_speeds, per_segment_awb_gains

_taskCameraBalanceInstance = None


def TaskCameraBalanceInstance():
    global _taskCameraBalanceInstance
    if _taskCameraBalanceInstance is None:
        _taskCameraBalanceInstance = Task_CameraBalance()
    return _taskCameraBalanceInstance
