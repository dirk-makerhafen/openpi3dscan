import threading
import time
import queue
import os

from app.settings.settings import SettingsInstance
from views.imageCarousel.imageCarousel import ImageCarousel
from app.devices.devices import DevicesInstance

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
loading_img_path = os.path.join(SCRIPT_DIR, "..", "..", "static", "images", "nophoto.jpg")


class PreviewQueue:
    def __init__(self):
        self.queue = queue.Queue()
        self.data_in_q = []
        self.imageRowViews = {}
        self.preview_data = {}
        for i in range(20):
            t = threading.Thread(target=self._worker_thread, daemon=True)
            t.start()
        self.loading_img = open(loading_img_path, "rb").read()

    def put(self, imageRowView):
        self.imageRowViews[imageRowView._device.device_id] = imageRowView

    def _worker_thread(self):
        resolutions = [
            [ 320, 240],
            [ 480, 360],
            [ 640, 480],
            [ 800, 600],
            [1024, 768],
            [1240, 930],
            [1440, 1080],
            [1920, 1440],
            [2592, 1944],
        ]

        while True:
            device_id = self.queue.get()
            if device_id in self.imageRowViews:
                img = None
                try:

                    device = DevicesInstance().get_device_by_id(device_id)
                    max_display_width = 3600
                    width_per_image = max_display_width /  self.imageRowViews[device_id].parent.parent.segments_shown
                    resolution = None
                    if SettingsInstance().settingsScanner.camera_rotation in [0, 180]:
                        index = 0
                    else:
                        index = 1
                    for r in resolutions:
                        if r[index] >= width_per_image:
                            resolution = r
                            break
                    if resolution is None:
                        resolution = resolutions[-1]
                    if SettingsInstance().settingsScanner.camera_rotation not in [0, 180]:
                        resolution = list(reversed(resolution))
                    try:
                        img = device.camera.preview(resolution)
                    except:
                        img = None
                except:
                    pass
                if device_id in self.data_in_q:
                    self.data_in_q.remove(device_id)
                try:
                    if img is not None:
                        self.preview_data[device_id] = {
                            "image" : img,
                            "timestamp": time.time()
                        }
                    elif device_id in self.preview_data:
                        if self.preview_data[device_id]["timestamp"] < time.time()-60:
                            del self.preview_data[device_id]

                    if device_id in self.preview_data and device_id in self.imageRowViews:
                        imageRowView = self.imageRowViews[device_id]
                        if imageRowView.is_visible:
                            imageRowView.update()
                        else:
                            try:
                                del self.imageRowViews[device_id]
                            except:
                                pass
                except:
                    pass
            else:
                try:
                    self.data_in_q.remove(device_id)
                except:
                    pass

    def get_image(self,  device_id):
        if device_id not in self.data_in_q:
            self.data_in_q.append(device_id)
            self.queue.put(device_id)
        if device_id in self.preview_data:
            if self.preview_data[device_id]["timestamp"] < time.time() - 60:
                del self.preview_data[device_id]
                return self.loading_img
            return self.preview_data[device_id]["image"]
        return self.loading_img


class ImageCarouselLive(ImageCarousel):
    DOM_ELEMENT_CLASS = "ImageCarousel"

    def __init__(self, subject, parent):
        super().__init__(subject, parent)

    def get_image_source(self, imageRowView):
        device = DevicesInstance().get_camera_by_position(imageRowView.parent.seg_nr, imageRowView.row_nr)
        if device is None or device.is_available is False:
            return '/static/images/nophoto.jpg'
        imageRowView._device = device
        PreviewQueueInstance().put(imageRowView)
        return '/live/%s.jpg?ts=%s' % (device.device_id, time.time())

    def switch_type(self):
        super().switch_type()
        DevicesInstance().projectors.set(self.image_type == "projection")


_previewQueue = None


def PreviewQueueInstance():
    global _previewQueue
    if _previewQueue is None:
        _previewQueue = PreviewQueue()
    return _previewQueue
