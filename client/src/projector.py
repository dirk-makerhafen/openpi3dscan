import threading
from queue import Queue
import time
import os
from bottle import route
from src.projector_image import ProjectorImage
from src.heartbeat import HeartbeatInstance

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


class Framebuffer(object):

    def __init__(self, device_no: int):
        self.path = "/dev/fb%d" % device_no
        config_dir = "/sys/class/graphics/fb%d/" % device_no
        os.system('sudo fbset -fb %s -depth 16' % self.path)
        self.size = tuple(self._read_and_convert_to_ints(config_dir + "/virtual_size"))
        self.stride = self._read_and_convert_to_ints(config_dir + "/stride")[0]
        self.bits_per_pixel = self._read_and_convert_to_ints(config_dir + "/bits_per_pixel")[0]
        assert self.stride == self.bits_per_pixel // 8 * self.size[0]
        self.fb_bytesize = self.size[0] * self.size[1] * (self.bits_per_pixel//8)
        self.empty_image = b'\0' * self.fb_bytesize
        self.fb = open(self.path, "wb")
        self.projection_file_name = "projection_%sx%sx%s.fb" % (self.size[0], self.size[1], self.bits_per_pixel)
        self.projection_file_path = os.path.join(SCRIPT_DIR, self.projection_file_name)
        if not os.path.exists(self.projection_file_path):
            pi = ProjectorImage(self.size[0], self.size[1], 11)
            self.fb_image = pi.get_fb()
            with open(self.projection_file_path, "wb") as f:
                f.write(self.fb_image)
        else:
            with open(self.projection_file_path, "rb") as f:
                self.fb_image  = f.read()

    def show(self):
        self.fb.write(self.fb_image)
        self.fb.seek(0)

    def clear(self):
        self.fb.write(self.empty_image)
        self.fb.seek(0)

    def _read_and_convert_to_ints(self, filename):
        with open(filename, "r") as fp:
            content = fp.read()
            tokens = content.strip().split(",")
            return [int(t) for t in tokens if t]

    def __str__(self):
        args = (self.path, self.size, self.stride, self.bits_per_pixel)
        return "%s  size:%s  stride:%s  bits_per_pixel:%s" % args


class Projector():
    def __init__(self):
        self.task_queue = Queue()
        self.framebuffer = Framebuffer(0)
        self.framebuffer.clear()
        self.enabled = False
        self.start()

    def start(self):
        self.t = threading.Thread(target=self._task_loop, daemon=True)
        self.t.start()

    def sequence(self, sequence):
        self.task_queue.put(["sequence",sequence])

    def enable(self):
        self.task_queue.put(["enable"])

    def disable(self):
        self.task_queue.put(["disable"])

    def _task_loop(self):
        while True:
            task = self.task_queue.get()
            HeartbeatInstance().lock()
            try:
                if task[0] == "sequence":
                    task, sequence = task
                    self._run_sequence(sequence)
                elif task[0] == "enable":
                    self._enable()
                elif task[0] == "disable":
                    self._disable()
            except Exception as e:
                print(e)
            HeartbeatInstance().unlock()

    def _run_sequence(self, sequence):
        prev_state = self.enabled
        for item in sequence:
            timestamp, action = item
            while time.time() < timestamp:
                time.sleep(0.0002)
            if action == "enable":
                self._enable()
            elif action == "disable":
                self._disable()
            elif action == "default":
                if prev_state is True:
                    self._enable()
                else:
                    self._disable()

    def _enable(self):
        self.framebuffer.show()
        self.enabled = True

    def _disable(self):
        self.framebuffer.clear()
        self.enabled = False

class ProjectorAPI():
    def __init__(self):
        self.projector = Projector()
        route("/projector/enable")(self.enable)
        route("/projector/disable")(self.disable)
        route("/projector/sequence/<sequence>")(self.sequence)

    def enable(self):
        self.projector.enable()

    def disable(self):
        self.projector.disable()

    def sequence(self, sequence):
        sequence = sequence.split(";")
        sequence = [item.split(":") for item in sequence]
        sequence = [[float(item[0]), item[1]] for item in sequence]
        now = time.time()
        for item in sequence:
            ts, value = item
            if ts - 20 > now:
                print("shot ts out of range", ts)
                return
            if ts < now - 5:
                print("shot in past, ignore", ts)
                return
        self.projector.sequence(sequence)
