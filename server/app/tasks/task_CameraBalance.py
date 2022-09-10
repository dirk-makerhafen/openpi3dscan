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
        time.sleep(3)  # wait for heartbeat queue to empty

        for device in cameras:
            device.camera.settings.set_shutter_speed(0)
            device.camera.settings.set_exposure_mode(SettingsInstance().cameraSettings.exposure_mode)
            device.camera.settings.set_iso(SettingsInstance().cameraSettings.iso)
            device.camera.settings.set_awb_mode(SettingsInstance().cameraSettings.awb_mode)

        time.sleep(12)

        with ThreadPool(20) as p:
            exposure_speeds = p.map(lambda device: device.camera.settings.get_exposure_speed(), cameras)
            awb_gains = p.map(lambda device: device.camera.settings.get_awb_gains(), cameras)

        for device in cameras:
            # add rows 6,5,4 to bias color to small people only visible on lower cameras
            if device.name.endswith("CAM6") or device.name.endswith("CAM5") or device.name.endswith("CAM4"):
                exposure_speeds.append(device.camera.settings.exposure_speed)
                awb_gains.append(device.camera.settings.awb_gains)

        exposure_speeds = [g for g in exposure_speeds if g is not None and g != 0]
        awb_gains = [g for g in awb_gains if g is not None and g[0] != 0]

        # average exposure_speeds
        avg_exposure_speed = round(sum([g for g in exposure_speeds]) / len(exposure_speeds), 3)
        print("avg_exposure_speeds", avg_exposure_speed)
        avg_awb_gains = [ round(sum([g[0] for g in awb_gains]) / len(awb_gains), 3), round(sum([g[1] for g in awb_gains]) / len(awb_gains), 3)]
        print("avg_awb_gains", avg_awb_gains)

        # set awb_mode to off
        for device in cameras:
            device.camera.settings.set_exposure_mode("off")
            device.camera.settings.set_awb_mode("off")

        SettingsInstance().cameraSettings.shutter_speed = avg_exposure_speed
        SettingsInstance().cameraSettings.awb_gains = avg_awb_gains

        time.sleep(3)
        for device in cameras:
            device.camera.settings.locked = False
        self.set_status("idle")
        self.worker = None


_taskCameraBalanceInstance = None


def TaskCameraBalanceInstance():
    global _taskCameraBalanceInstance
    if _taskCameraBalanceInstance is None:
        _taskCameraBalanceInstance = Task_CameraBalance()
    return _taskCameraBalanceInstance
