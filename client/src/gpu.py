from __future__ import division

import ctypes
import threading
from io import BytesIO
from picamera import mmal, mmalobj
from threading import Event

gpulock = threading.Lock()

class Resize_YUV():
    def __init__(self):
        self.resizer = mmalobj.MMALResizer()
        self.resizer.inputs[0].format = mmal.MMAL_ENCODING_I420
        self.resizer.inputs[0].framesize = (2592, 1944)
        self.resizer.inputs[0].commit()
        self.resizer.outputs[0].format = mmal.MMAL_ENCODING_I420
        self.resizer.outputs[0].framesize = (800, 600)
        self.resizer.outputs[0].commit()
        self.finished = Event()
        self.output = None


    def _callback(self, port, buf):
        finished = bool(buf.flags & mmal.MMAL_BUFFER_HEADER_FLAG_FRAME_END)
        if finished is True:
            with buf as data:
                if self.output is None:
                    self.output = bytes(data)
                else:
                    self.output.write(data)
            self.finished.set()
        return finished

    def resize(self, YUV_DATA, output = None, from_size = (2592, 1944), to_size = (800, 600)):
        gpulock.acquire()
        try:
            if type(output) == str:
                self.output = open(output, "wb")

            self.resizer.inputs[0].framesize  = from_size
            self.resizer.inputs[0].commit()
            self.resizer.inputs[0].enable(lambda port, buf: True)

            self.resizer.outputs[0].framesize = to_size
            self.resizer.outputs[0].commit()
            self.resizer.outputs[0].enable(self._callback)

            buf = self.resizer.inputs[0].get_buffer()
            buf.data = YUV_DATA
            self.resizer.inputs[0].send_buffer(buf)

            if not self.finished.wait(10):
                raise Exception('resizer timed out')
            self.finished.clear()

            self.resizer.outputs[0].disable()
            self.resizer.inputs[0].disable()

            r = None
            if type(output) == str:
                self.output.close()
            else:
                r = self.output
            self.output = None
        finally:
            gpulock.release()
        return r

class YUV_to_JPEG():
    def __init__(self):
        self.encoder = mmalobj.MMALImageEncoder()
        self.encoder.inputs[0].format = mmal.MMAL_ENCODING_I420
        self.encoder.inputs[0].framesize = (2592, 1944)
        self.encoder.inputs[0].commit()
        self.encoder.outputs[0].copy_from(self.encoder.inputs[0])
        self.encoder.outputs[0].format = mmal.MMAL_ENCODING_JPEG
        self.encoder.outputs[0].params[mmal.MMAL_PARAMETER_JPEG_Q_FACTOR] = 100
        self.encoder.outputs[0].commit()
        self.finished = Event()
        self.output = None

    def _callback(self, port, buf):
        finished = bool(buf.flags & mmal.MMAL_BUFFER_HEADER_FLAG_FRAME_END)
        if finished is True:
            with buf as data:
                if self.output is None:
                        self.output = bytes(data)
                else:
                    self.output.write(data)
            self.finished.set()
        return finished

    def encode(self, YUV_DATA, output = None, framesize = (2592, 1944), quality = 100):
        gpulock.acquire()
        try:
            if type(output) == str:
                self.output = open(output, "wb")

            self.encoder.inputs[0].framesize = framesize
            self.encoder.inputs[0].commit()
            self.encoder.inputs[0].enable(lambda port, buf: True)

            self.encoder.outputs[0].params[mmal.MMAL_PARAMETER_JPEG_Q_FACTOR] = quality
            self.encoder.outputs[0].framesize = framesize
            self.encoder.outputs[0].commit()
            self.encoder.outputs[0].enable(self._callback)

            buf = self.encoder.inputs[0].get_buffer()
            buf.data = YUV_DATA
            self.encoder.inputs[0].send_buffer(buf)

            if not self.finished.wait(30):
                raise Exception('encode timed out')
            self.finished.clear()

            self.encoder.outputs[0].disable()
            self.encoder.inputs[0].disable()

            r = None
            if type(output) == str:
                self.output.close()
            else:
                r = self.output
            self.output = None
        finally:
            gpulock.release()
        return r




_resize_YUVInstance = None
def Resize_YUVInstance():
    global _resize_YUVInstance
    if _resize_YUVInstance is None:
        _resize_YUVInstance = Resize_YUV()
    return _resize_YUVInstance

_YUV_to_JPEGInstance = None
def YUV_to_JPEGInstance():
    global _YUV_to_JPEGInstance
    if _YUV_to_JPEGInstance is None:
        _YUV_to_JPEGInstance = YUV_to_JPEG()
    return _YUV_to_JPEGInstance
