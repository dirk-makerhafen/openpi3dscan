from __future__ import division

import random
import shutil
from fractions import Fraction
from io import BytesIO
from queue import Queue
import time
import threading
from collections import deque

import bottle
import ctypes
import picamera
from picamera import mmal, mmalobj
from RPi import GPIO
import glob
import os
import json
import time
import numpy as np
from PIL import Image
from bottle import route, response, static_file, HTTPResponse
import gc
from .gpu import YUV_to_JPEGInstance, Resize_YUVInstance
storage_dir = "/home/openpi3dscan/shots"

from src.heartbeat import HeartbeatInstance


VIDEO_PORT_NR = 1
STILL_PORT_NR = 2



def clear_memory():
    os.system("sudo sh -c 'sync ; echo 3 > /proc/sys/vm/drop_caches'")
    gc.collect()


class Frame():
    def __init__(self,  timestamp, buffer, framesize):
        self.timestamp = timestamp
        self.image_framesize = framesize
        self.preview_framesize = (800, 600)
        self.image = None
        self.preview = None
        if buffer is not None:
            with buffer as data:
                self.image = bytes(data)

    def create_preview(self, framesize):
        self.preview = Resize_YUVInstance().resize(self.image, from_size=self.image_framesize, to_size=framesize)
        self.preview_framesize = framesize

    def preview_to_jpeg(self, quality):
        self.preview = YUV_to_JPEGInstance().encode(self.preview, framesize=self.preview_framesize, quality=quality)

    def optimise_preview(self):
        self.preview = Image.open(BytesIO(self.preview))

    def save_preview(self, output, quality = 85):
        if type(output) == type(""):
            path = "/".join(output.split("/")[0:-1])
            if not os.path.exists(path):
                os.mkdir(path)
            tpath = "%s_tmp" % output
            self.preview.save(tpath, format="jpeg", quality=quality) # make image smaller
            os.rename(tpath, output)
        else:
            self.preview.save(output, format="jpeg", quality=quality)  # make image smaller

    def image_to_jpeg(self, quality):
        self.image = YUV_to_JPEGInstance().encode(self.image, framesize=self.image_framesize, quality=quality)

    def optimise_image(self):
        self.image = Image.open(BytesIO(self.image))

    def save_image(self, output, quality = 100):
        if type(output) == type(""):
            path = "/".join(output.split("/")[0:-1])
            if not os.path.exists(path):
                os.mkdir(path)
            tpath = "%s_tmp" % output
            self.image.save(tpath, format="jpeg", quality=quality)  # make image smaller
            os.rename(tpath, output)
        else:
            self.image.save(output, format="jpeg", quality=quality)  # make image smaller

    def clear(self):
        self.image = None
        self.preview = None
        self.buffer = None

class Buffer():
    def __init__(self, maxsize = 4):
        self.maxsize = maxsize
        self.queue = Queue(maxsize=self.maxsize)

    def put(self, value):
        while self.queue.qsize() >= self.maxsize:
            self.queue.get()
        self.queue.put(value)

    def get(self, timeout):
        return self.queue.get(timeout=timeout)


class CameraPort():
    def __init__(self, camera, port_nr):
        self._camera = camera
        self.framesize = (camera.max_x, camera.max_y)
        self._port_nr = port_nr
        self.framerate = 9
        if self._port_nr == STILL_PORT_NR:  # STILL PORT
            self.framerate = 3.5 # set framerate

        self.s_per_frame = 1.0 / self.framerate
        self.s_per_half_frame = self.s_per_frame / 2.0

        self._output.framesize = self.framesize
        self._output.framerate = self.framerate
        self._output.format = mmal.MMAL_ENCODING_I420
        self._output.commit()
        self._output.disable()
        self.enabled = False
        self._pll_active = False
        self._frame_capture_started = 0
        self._cb_active = False
        self.buffer = Buffer()
        self.capture_timestamps = []

    @property
    def _output(self):
        return self._camera.mmal_camera.outputs[self._port_nr]

    def capture(self,nr_of_frames= -1, timestamps= None, use_pll = True):
        if timestamps is None:
            timestamps = [-1 for i in range(nr_of_frames)]
        self.capture_timestamps = [ t for t in  timestamps ]

        was_enabled = self.enabled
        pll_was_already_active = self._pll_active

        if self._pll_active is False and use_pll is True:
            self.start_pll()
        self.enable()

        while len(timestamps) > 0:
            try:
                frame = self.buffer.get(timeout=10)
            except:
                break
            while len(timestamps) > 0 and frame.timestamp > (timestamps[0] + self.s_per_half_frame) and timestamps[0] != -1:  # timestamp missed and is too old
                del timestamps[0]
                yield None
            if len(timestamps) > 0 and (abs(frame.timestamp - timestamps[0]) <= self.s_per_half_frame or timestamps[0] == -1):  # hit
                del timestamps[0]
                yield frame
            else:
                frame.clear()

        if pll_was_already_active is False and use_pll is True:
            self.stop_pll()
        if was_enabled is False:
            self.disable()

    def start_pll(self):
        self._pll_active = True

    def stop_pll(self):
        self._pll_active = False

    def enable(self):
        if self.enabled is True:
            return
        self._output.params[mmal.MMAL_PARAMETER_CAPTURE] = True
        self._frame_capture_started = time.time()
        self._output.enable(self._callback)
        self._camera.led = False
        self.enabled = True

    def disable(self):
        if self.enabled is False:
            return
        self._output.params[mmal.MMAL_PARAMETER_CAPTURE] = False
        while self._cb_active is True:
            time.sleep(self.s_per_half_frame/2)
        self._output.disable()
        self.enabled = False

    def _callback(self, port, buffer):
        self._cb_active = True
        timestamp = ( buffer.pts / 1000000.0 ) - ( ( self._output.params[mmal.MMAL_PARAMETER_SYSTEM_TIME] / 1000000.0 ) - time.time() )
        frame_finished = bool(buffer.flags & mmal.MMAL_BUFFER_HEADER_FLAG_FRAME_END)

        if frame_finished is True:
            while len(self.capture_timestamps) > 0 and self.capture_timestamps[0] != -1 and timestamp > (self.capture_timestamps[0] + self.s_per_half_frame):  # timestamp missed and is too old
                del self.capture_timestamps[0]
                self.buffer.put(Frame(timestamp, None, self.framesize))
            if len(self.capture_timestamps) > 0 and ((abs(timestamp - self.capture_timestamps[0]) <= self.s_per_half_frame or self.capture_timestamps[0] == -1)):  # hit
                del self.capture_timestamps[0]
                self.buffer.put(Frame(timestamp, buffer, self.framesize))
            if self._pll_active is True:
                self._pll_adjust(timestamp)

        stop_capture = len(self.capture_timestamps) == 0 and self._pll_active is False and frame_finished is True
        self._cb_active = False
        return stop_capture # return True if end

    def _pll_adjust(self, timestamp):
        raise NotImplementedError()


class CameraPortStill(CameraPort):
    def __init__(self, camera):
        super().__init__(camera, STILL_PORT_NR)
        self._pll_still_frametime_s = self.s_per_frame


    def _pll_adjust(self, timestamp):
        stop_capture = len(self.capture_timestamps) == 0 and self._pll_active is False
        if stop_capture is True:
            return
        offset = timestamp % self.s_per_frame
        if offset < self.s_per_half_frame:  # we are to slow, missed our point
            cor = offset / self.s_per_half_frame
        else:  # we are to fast
            cor = - ((1 / self.s_per_half_frame) * (self.s_per_frame - offset))

        self._pll_still_frametime_s = self._pll_still_frametime_s * (1 - cor/100) # moving average sleeptime
        if self._pll_still_frametime_s > self.s_per_frame*1.2:
            self._pll_still_frametime_s = self.s_per_frame
        elif self._pll_still_frametime_s < self.s_per_frame*0.8:
            self._pll_still_frametime_s = self.s_per_frame

        if cor > 0: # to slow
            delay = self._pll_still_frametime_s - (offset/15)  #adjustment for next step
        else:  # to fast
            delay = self._pll_still_frametime_s + ((self.s_per_frame - offset)/15)
        target_start_time = (self._frame_capture_started + delay)
        sleeptime = target_start_time - time.time()
        if sleeptime > 0.001:
            time.sleep(sleeptime)
        self._output.params[mmal.MMAL_PARAMETER_CAPTURE] = True
        self._frame_capture_started = time.time()


class CameraPortVideo(CameraPort):
    def __init__(self, camera):
        super().__init__(camera, 1)

    def _pll_adjust(self, timestamp):
        offset = timestamp % self.s_per_frame

        if offset < self.s_per_half_frame:  # we are to slow
            cor = offset / self.s_per_half_frame
        else:  # we are to fast
            cor = - ((1 / self.s_per_half_frame) * (self.s_per_frame - offset))

        cor_framerate = self.framerate + cor * 2
        self._output.params[mmal.MMAL_PARAMETER_FRAME_RATE] = cor_framerate



class CameraTasks():
    def __init__(self, camera):
        self.camera = camera
        self.task_queue = Queue()
        self.t = threading.Thread(target=self._task_loop, daemon=True)
        self.t.start()

    def _task_loop(self):
        while True:
            task = self.task_queue.get()
            HeartbeatInstance().lock()
            try:
                if task[0] == "shot":
                    task, shot_id, timestamps, quality, projection_first = task
                    self.camera.create_shot(shot_id, timestamps, quality, projection_first)
                elif task[0] == "benchmark":
                    self.camera.benchmark()
                #elif task[0] == "whitebalance":
                #    self.camera.whitebalance()
                elif task[0] == "set_quality":
                    self.camera.set_quality_locked(task[1])
                    self.camera.save()
            except Exception as e:
                print(e)
            HeartbeatInstance().unlock()

    def create_shot(self, shot_id, timestamps, quality, projection_first):
        self.task_queue.put(["shot", shot_id, timestamps, quality, projection_first])

    #def whitebalance(self):
    #    self.task_queue.put(["whitebalance",])

    def set_quality(self, quality):
        self.task_queue.put(["set_quality", quality])

class Camera():
    def __init__(self):
        self._quality = "speed"
        self.last_usage = time.time()
        self.autopll_timeout = 3600
        self.autopll_active = False
        self.capture_active = False
        self.cameralock = threading.Lock()
        self.revision = 'ov5647'
        self.max_x = 2592
        self.max_y = 1944
        self.mmal_camera = mmalobj.MMALCamera()
        self._setup()
        self.port_still = CameraPortStill(self)
        self.port_video = CameraPortVideo(self)
        self.tasks = CameraTasks(self)
        self.workerqueue = Queue()
        self.load()

        self.t = threading.Thread(target=self._autopll_worker, daemon=True)
        self.t.start()
        self.t = threading.Thread(target=self.worker, daemon=True)
        self.t.start()

    def _setup(self):
        self.mmal_camera.control.params[mmal.MMAL_PARAMETER_CAMERA_CUSTOM_SENSOR_CONFIG] = 2
        if not self.mmal_camera.control.enabled:
            self.mmal_camera.control.enable()


        with mmalobj.MMALCameraInfo() as camera_info:
            if camera_info.info_rev > 1:
                self.revision = camera_info.control.params[mmal.MMAL_PARAMETER_CAMERA_INFO].cameras[0].camera_name.decode('ascii')

        if self.revision == "imx219":
            self.max_x = 3280
            self.max_y = 2464

        cc = self.mmal_camera.control.params[picamera.mmal.MMAL_PARAMETER_CAMERA_CONFIG]
        cc.max_stills_w = self.max_x
        cc.max_stills_h = self.max_y
        cc.stills_yuv422 = 0
        cc.one_shot_stills = 1
        cc.max_preview_video_w = self.max_x
        cc.max_preview_video_h = self.max_y
        cc.num_preview_video_frames = 1
        cc.stills_capture_circular_buffer_height = 0
        cc.fast_preview_resume = 0
        cc.use_stc_timestamp = picamera.mmal.MMAL_PARAM_TIMESTAMP_MODE_RAW_STC
        self.mmal_camera.control.params[picamera.mmal.MMAL_PARAMETER_CAMERA_CONFIG] = cc

        self.shutter_speed = 20000
        self.sharpness = 0
        self.contrast = 0
        self.brightness = 50
        self.saturation = 0
        self.iso = 100
        self.video_stabilization = False
        self.exposure_compensation = 0
        self.exposure_mode = 'auto' # off','auto','night', 'nightpreview', 'backlight', 'spotlight', 'sports', 'snow', 'beach', 'verylong', 'fixedfps', 'antishake', 'fireworks'
        self.meter_mode = 'spot' # 'average','spot','backlit','matrix'
        self.awb_mode = 'off' #'off', 'auto', 'sunlight', 'cloudy', 'shade', 'tungsten', 'fluorescent', 'incandescent', 'flash', 'horizon'

        self.image_effect = 'none'
        self.color_effects = None
        self.rotation = 0
        self.hflip = self.vflip = False
        self.zoom = (0.0, 0.0, 1.0, 1.0)

        self.led_pin = {
            (0, 0): 2,  # compute module (default for cam 0)
            (0, 1): 30,  # compute module (default for cam 1)
            (1, 0): 5,  # Pi 1 model B rev 1
            (2, 0): 5,  # Pi 1 model B rev 2 or model A
            (3, 0): 32,  # Pi 1 model B+ or Pi 2 model B
        }[(GPIO.RPI_REVISION, 0)]
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.led_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.output(self.led_pin, bool(False))
        self.led_status = False

    def get_preview(self, framesize = (640, 480), quality=None):
        if self.workerqueue.qsize() != 0:
            return None
        self.cameralock.acquire()
        try:
            if quality is not None:
                self.quality = quality
            self.last_usage = time.time()
            self.check_autopll()
            frame = [frame for frame in self.port.capture(nr_of_frames=1)][0]
        finally:
            self.cameralock.release()

        if self.capture_active is True: # return quick if capture was started
            frame.clear()
            return None

        frame.create_preview(framesize= framesize)
        frame.image = None
        if self.capture_active is True:# return quick if capture was started
            frame.clear()
            return None

        frame.preview_to_jpeg(quality=100)
        if self.capture_active is True: # return quick if capture was started
            frame.clear()
            return None

        frame.optimise_preview()
        if self.capture_active is True: # return quick if capture was started
            frame.clear()
            return None

        output = BytesIO()
        frame.save_preview(quality=85, output= output)
        output.seek(0)
        return output.read()

    def get_avg_rgb(self):
        image = self.get_preview(framesize= (800, 600))
        image = Image.open(BytesIO(image))
        image = image.crop((375, 250, 425, 350))
        image = np.array(image, dtype=np.uint8)
        meanrgb = list(image.mean(axis=(0, 1)))
        return meanrgb

    def create_shot(self, shot_id, timestamps, quality, projection_first ):
        self.last_usage = time.time()
        self.capture_active = True
        self.cameralock.acquire()
        if projection_first is True:
            names = ["projection", "normal"]
        else:
            names = ["normal", "projection"]

        try:
            self.quality = quality
            self.check_autopll()

            frames = [frame for frame in self.port.capture(timestamps=timestamps, use_pll=True)]

            path = "%s/%s/" % (storage_dir, shot_id)
            if frames[0] is not None:
                self.create_frame_tasks(frames[0], names[0], path)
                frames[0] = None
            if frames[1] is not None:
                self.create_frame_tasks(frames[1], names[1], path)
                frames[1] = None

        finally:
            self.capture_active = False
            self.cameralock.release()

    def create_frame_tasks(self, frame, name, path):
        self.workerqueue.put([frame.create_preview,  { "framesize": (800, 600) } ])
        self.workerqueue.put([frame.image_to_jpeg,   { "quality" :  100 } ])
        self.workerqueue.put([frame.preview_to_jpeg, { "quality"  : 100} ] )
        self.workerqueue.put([frame.optimise_preview,{  } ] )
        self.workerqueue.put([frame.save_preview,    { "output"   : os.path.join(path, "%s_preview.jpg" % name) } ])
        self.workerqueue.put([frame.optimise_image,  {  } ] )
        self.workerqueue.put([frame.save_image,      { "output"   : os.path.join(path, "%s.jpg" % name) } ])
        self.workerqueue.put([frame.clear,           {  } ] )
        self.workerqueue.put([self.clean_shots_dir,  {  } ] )

    def worker(self):
        while True:
            task = self.workerqueue.get()
            self.cameralock.acquire() # dont process if shot is active
            self.cameralock.release()
            try:
                fun, args = task
                fun(**args)
            except Exception as e:
                print("failed to execute function")


    def clean_shots_dir(self, min_disk_free=300):
        if random.randint(0,10) != 1:
            return
        if shutil.disk_usage("/")[2] / 1024 / 1024 > min_disk_free:
            return
        paths = [
            os.path.join("/3dscan/", "*.jpg"),
            os.path.join(storage_dir, "*")
        ]

        for path in paths:
            shots = sorted([path for path in glob.glob(path)])
            free = shutil.disk_usage("/")[2] / 1024 / 1024
            while free < min_disk_free and len(shots) > 0:
                for i in range(30):
                    if len(shots) == 0: break
                    os.system("rm -r '%s'" % shots[0])
                    del shots[0]
                free = shutil.disk_usage("/")[2] / 1024 / 1024

    def deprecated_whitebalance(self):
        try:
            self.last_usage = time.time()
            self.check_autopll()
            if self.autopll_active is False:
                self.port.start_pll()
                self.port.enable()
            self.awb_mode = 'auto'
             #self.exposure_mode = 'backlight'
            time.sleep(5)
            awb_gains = self.awb_gains
            self.awb_mode = 'off'
            self.awb_gains = awb_gains
            for i in range(10):
                time.sleep(1)
                rgb = self.get_avg_rgb()
                diff_r = ( 1.0 / rgb[1] ) * rgb[0]
                diff_b = ( 1.0 / rgb[1] ) * rgb[2]
                if abs(1 - diff_r) > 0.3 and abs(1 - diff_b) > 0.3: # to large, adjust
                    while abs(1 - diff_r) > 0.3 and abs(1 - diff_b) > 0.3: # to large, adjust
                        diff_r = 1 - (1 - diff_r)*0.75
                        diff_b = 1 - (1 - diff_b)*0.75
                    time.sleep(1)
                if abs(1 - diff_r) < 0.005 and abs(1 - diff_b) < 0.005:
                    break
                awb_gains = [ awb_gains[0] / diff_r, awb_gains[1] / diff_b ] #  red, blue
                if abs(awb_gains[0]) > 2 or abs(awb_gains[0]) > 2:
                    awb_gains = [1,1]
                self.awb_gains = awb_gains
            #self.exposure_mode = 'off'

        finally:
            pass
        self.save()

    def set_quality_locked(self, value):
        self.cameralock.acquire()
        self.quality = value
        self.cameralock.release()
    def _get_quality(self):
        return self._quality
    def _set_quality(self, value):
        self.last_usage = time.time()
        if self._quality != value:
            self.port.stop_pll()
            self.port.disable()
            self.autopll_active = False
            self._quality = value
        self.check_autopll()
    quality = property(_get_quality, _set_quality)

    def check_autopll(self):
        if self.last_usage < time.time() - self.autopll_timeout: # pll timeout
            if self.autopll_active is True:
                self.port.stop_pll()
                self.port.disable()
                self.autopll_active = False
        else: # pll not times out
            if self.autopll_active is False:
                self.port.start_pll()
                self.port.enable()
                self.autopll_active = True

    def _autopll_worker(self):
        while True:
            self.cameralock.acquire()
            self.check_autopll()
            self.cameralock.release()
            time.sleep(260)

    def _get_port(self):
        if self.quality == "speed":
            return self.port_video
        if self.quality == "quality":
            return self.port_still
    port = property(_get_port)

    def _get_led(self):
        return self.led_status
    def _set_led(self, value):
        GPIO.output(self.led_pin, bool(value))
    led = property(_get_led, _set_led)

    def _get_iso(self):
        return self.mmal_camera.control.params[mmal.MMAL_PARAMETER_ISO]
    def _set_iso(self, value):
        self.mmal_camera.control.params[mmal.MMAL_PARAMETER_ISO] = value
    iso = property(_get_iso, _set_iso)

    def _get_shutter_speed(self):
        return int(self.mmal_camera.control.params[mmal.MMAL_PARAMETER_SHUTTER_SPEED])
    def _set_shutter_speed(self, value):
        self.mmal_camera.control.params[mmal.MMAL_PARAMETER_SHUTTER_SPEED] = value
    shutter_speed = property(_get_shutter_speed, _set_shutter_speed)

    def _get_exposure_speed(self):
        return self.mmal_camera.control.params[mmal.MMAL_PARAMETER_CAMERA_SETTINGS].exposure
    exposure_speed = property(_get_exposure_speed)

    def _get_awb_gains(self):
        mp = self.mmal_camera.control.params[mmal.MMAL_PARAMETER_CAMERA_SETTINGS]
        return (mmalobj.to_fraction(mp.awb_red_gain), mmalobj.to_fraction(mp.awb_blue_gain))
    def _set_awb_gains(self, value):
        red_gain, blue_gain = value
        if not (0.0 <= red_gain <= 8.0 and 0.0 <= blue_gain <= 8.0):
            raise Exception("Invalid gain(s) in (%f, %f) (valid range: 0.0-8.0)" % (red_gain, blue_gain))
        mp = mmal.MMAL_PARAMETER_AWB_GAINS_T(
            mmal.MMAL_PARAMETER_HEADER_T(
                mmal.MMAL_PARAMETER_CUSTOM_AWB_GAINS,
                ctypes.sizeof(mmal.MMAL_PARAMETER_AWB_GAINS_T)
                ),
            mmalobj.to_rational(red_gain),
            mmalobj.to_rational(blue_gain),
            )
        self.mmal_camera.control.params[mmal.MMAL_PARAMETER_CUSTOM_AWB_GAINS] = mp
    awb_gains = property(_get_awb_gains, _set_awb_gains)

    def _get_exposure_mode(self):
        return picamera.PiCamera._EXPOSURE_MODES_R[self.mmal_camera.control.params[mmal.MMAL_PARAMETER_EXPOSURE_MODE].value]
    def _set_exposure_mode(self, value):
        try:
            mp = self.mmal_camera.control.params[mmal.MMAL_PARAMETER_EXPOSURE_MODE]
            mp.value = picamera.PiCamera.EXPOSURE_MODES[value]
        except KeyError:
            raise Exception("Invalid exposure mode: %s" % value)
        self.mmal_camera.control.params[mmal.MMAL_PARAMETER_EXPOSURE_MODE] = mp
    exposure_mode = property(_get_exposure_mode, _set_exposure_mode)

    def _get_awb_mode(self):
        return picamera.PiCamera._AWB_MODES_R[self.mmal_camera.control.params[mmal.MMAL_PARAMETER_AWB_MODE].value]
    def _set_awb_mode(self, value):
        try:
            mp = self.mmal_camera.control.params[mmal.MMAL_PARAMETER_AWB_MODE]
            mp.value = picamera.PiCamera.AWB_MODES[value]
        except KeyError:
            raise Exception("Invalid auto-white-balance mode: %s" % value)
        self.mmal_camera.control.params[mmal.MMAL_PARAMETER_AWB_MODE] = mp
    awb_mode = property(_get_awb_mode, _set_awb_mode)

    def _get_saturation(self):
        return int(self.mmal_camera.control.params[mmal.MMAL_PARAMETER_SATURATION] * 100)
    def _set_saturation(self, value):
        if not (-100 <= value <= 100):
            raise Exception("Invalid saturation value: %d (valid range -100..100)" % value)
        self.mmal_camera.control.params[mmal.MMAL_PARAMETER_SATURATION] = Fraction(value, 100)
    saturation = property(_get_saturation, _set_saturation)

    def _get_sharpness(self):
        return int(self.mmal_camera.control.params[mmal.MMAL_PARAMETER_SHARPNESS] * 100)
    def _set_sharpness(self, value):
        if not (-100 <= value <= 100):
            raise Exception("Invalid sharpness value: %d (valid range -100..100)" % value)
        self.mmal_camera.control.params[mmal.MMAL_PARAMETER_SHARPNESS] = Fraction(value, 100)
    sharpness = property(_get_sharpness, _set_sharpness)

    def _get_contrast(self):
        return int(self.mmal_camera.control.params[mmal.MMAL_PARAMETER_CONTRAST] * 100)
    def _set_contrast(self, value):
        if not (-100 <= value <= 100):
            raise Exception("Invalid contrast value: %d (valid range -100..100)" % value)
        self.mmal_camera.control.params[mmal.MMAL_PARAMETER_CONTRAST] = Fraction(value, 100)
    contrast = property(_get_contrast, _set_contrast)

    def _get_brightness(self):
        return int(self.mmal_camera.control.params[mmal.MMAL_PARAMETER_BRIGHTNESS] * 100)
    def _set_brightness(self, value):
        if not (0 <= value <= 100):
            raise Exception("Invalid brightness value: %d (valid range 0..100)" % value)
        self.mmal_camera.control.params[mmal.MMAL_PARAMETER_BRIGHTNESS] = Fraction(value, 100)
    brightness = property(_get_brightness, _set_brightness)

    def _get_analog_gain(self):
        return mmalobj.to_fraction(self.mmal_camera.control.params[mmal.MMAL_PARAMETER_CAMERA_SETTINGS].analog_gain)
    analog_gain = property(_get_analog_gain)

    def _get_digital_gain(self):
        return mmalobj.to_fraction(self.mmal_camera.control.params[mmal.MMAL_PARAMETER_CAMERA_SETTINGS].digital_gain)
    digital_gain = property(_get_digital_gain)

    def _get_video_denoise(self):
        return self.mmal_camera.control.params[mmal.MMAL_PARAMETER_VIDEO_DENOISE]
    def _set_video_denoise(self, value):
        self.mmal_camera.control.params[mmal.MMAL_PARAMETER_VIDEO_DENOISE] = value
    video_denoise = property(_get_video_denoise, _set_video_denoise)

    def _get_image_denoise(self):
        return self.mmal_camera.control.params[mmal.MMAL_PARAMETER_STILLS_DENOISE]
    def _set_image_denoise(self, value):
        self.mmal_camera.control.params[mmal.MMAL_PARAMETER_STILLS_DENOISE] = value
    image_denoise = property(_get_image_denoise, _set_image_denoise)

    def _get_drc_strength(self):
        return picamera.PiCamera._DRC_STRENGTHS_R[self.mmal_camera.control.params[mmal.MMAL_PARAMETER_DYNAMIC_RANGE_COMPRESSION].strength]
    def _set_drc_strength(self, value):
        try:
            mp = self.mmal_camera.control.params[mmal.MMAL_PARAMETER_DYNAMIC_RANGE_COMPRESSION]
            mp.strength = picamera.PiCamera.DRC_STRENGTHS[value]
        except KeyError:
            raise Exception("Invalid dynamic range compression strength: %s" % value)
        self.mmal_camera.control.params[mmal.MMAL_PARAMETER_DYNAMIC_RANGE_COMPRESSION] = mp
    drc_strength = property(_get_drc_strength, _set_drc_strength)

    def _get_meter_mode(self):
        return picamera.PiCamera._METER_MODES_R[self.mmal_camera.control.params[mmal.MMAL_PARAMETER_EXP_METERING_MODE].value]
    def _set_meter_mode(self, value):
        try:
            mp = self.mmal_camera.control.params[mmal.MMAL_PARAMETER_EXP_METERING_MODE]
            mp.value = picamera.PiCamera.METER_MODES[value]
        except KeyError:
            raise Exception("Invalid metering mode: %s" % value)
        self.mmal_camera.control.params[mmal.MMAL_PARAMETER_EXP_METERING_MODE] = mp
    meter_mode = property(_get_meter_mode, _set_meter_mode)

    def _get_video_stabilization(self):
        return self.mmal_camera.control.params[mmal.MMAL_PARAMETER_VIDEO_STABILISATION]
    def _set_video_stabilization(self, value):
        self.mmal_camera.control.params[mmal.MMAL_PARAMETER_VIDEO_STABILISATION] = value
    video_stabilization = property(_get_video_stabilization, _set_video_stabilization)

    def _get_exposure_compensation(self):
        return self.mmal_camera.control.params[mmal.MMAL_PARAMETER_EXPOSURE_COMP]
    def _set_exposure_compensation(self, value):
        try:
            if not (-25 <= value <= 25):
                raise Exception("Invalid exposure compensation value: %d (valid range -25..25)" % value)
        except TypeError:
            raise Exception("Invalid exposure compensation value: %s" % value)
        self.mmal_camera.control.params[mmal.MMAL_PARAMETER_EXPOSURE_COMP] = value
    exposure_compensation = property( _get_exposure_compensation, _set_exposure_compensation)

    def to_dict(self):
        return {
            "iso": self.iso,
            "shutter_speed": self.shutter_speed,
            "exposure_mode": self.exposure_mode,
            "meter_mode": self.meter_mode,
            "awb_mode": self.awb_mode,
            "awb_gains": [float(x) for x in self.awb_gains],
            "quality": self.quality,
            "exposure_speed": self.exposure_speed,
            "analog_gain": float(self.analog_gain),
            "digital_gain": float(self.digital_gain),
        }

    def save(self):
        try:
            with open("/home/openpi3dscan/.settings.json","w") as f:
                f.write(json.dumps(self.to_dict()))
        except:
            pass

    def load(self):
        try:
            with open("/home/openpi3dscan/.settings.json","r") as f:
                data = json.loads(f.read())
                self.iso = data["iso"]
                self.shutter_speed = data["shutter_speed"]
                self.exposure_mode = data["exposure_mode"]
                self.meter_mode = data["meter_mode"]
                self.awb_gains = data["awb_gains"]
                self.set_quality_locked(data["quality"])
                self.awb_mode = data["awb_mode"]
        except:
            pass

class CameraAPI():
    def __init__(self):
        self.camera = Camera()

        route("/camera/preview/img.jpg")(self.preview)
        route("/camera/preview/<resolution>/img.jpg")(self.preview)
        route("/camera/preview/<resolution>/<quality>/img.jpg")(self.preview)
        #route("/camera/settings/get")(self.camera.json)
        route("/camera/settings/iso")(self.get_iso)
        route("/camera/settings/iso/<iso>")(self.set_iso)
        route("/camera/settings/exposure_speed")(self.get_exposure_speed)
        route("/camera/settings/shutter_speed")(self.get_shutter_speed)
        route("/camera/settings/shutter_speed/<shutter_speed>")(self.set_shutter_speed)
        route("/camera/settings/awb_gains")(self.get_awb_gains)
        route("/camera/settings/awb_gains/<gains>")(self.set_awb_gains)
        route("/camera/settings/meter_mode")(self.camera._get_meter_mode)
        route("/camera/settings/meter_mode/<meter_mode>")(self.set_meter_mode)
        route("/camera/settings/awb_mode")(self.camera._get_awb_mode)
        route("/camera/settings/awb_mode/<awb_mode>")(self.set_awb_mode)
        route("/camera/settings/exposure_mode")(self.camera._get_exposure_mode)
        route("/camera/settings/exposure_mode/<exposure_mode>")(self.set_exposure_mode)
        route("/camera/settings/quality/<quality>")(self.set_quality)

        #route("/camera/calibrate/whitebalance")(self.camera.tasks.whitebalance)
        route("/camera/calibrate/get_avg_rgb")(self.get_avg_rgb)

        route("/camera/shots/list")(self.shots_list)
        route("/camera/shots/create/<shot_id>/<timestamps>/<quality>/<projection_first>")(self.shots_create)
        route("/camera/shots/get/<shot_id>/<image_mode>/<image_type>.jpg")(self.shots_get)
        route("/camera/shots/delete/<shot_id>")(self.delete_shot)

    def preview(self, resolution = "640,480", quality = None):
        resolution = [int(r) for r in resolution.split(",")]
        img_data = self.camera.get_preview(resolution, quality)
        if img_data is None:
            return bottle.HTTPResponse(status=503)
        response.set_header('Content-type', 'image/jpeg')
        return img_data

    def set_quality(self, quality):
        self.camera.tasks.set_quality(quality)

    def set_meter_mode(self, meter_mode):
        self.camera.meter_mode = meter_mode
        self.camera.save()
        return "%s" % self.camera.meter_mode

    def set_exposure_mode(self, exposure_mode):
        self.camera.exposure_mode = exposure_mode
        self.camera.save()
        return "%s" % self.camera.exposure_mode

    def set_awb_mode(self, awb_mode):
        self.camera.awb_mode = awb_mode
        self.camera.save()
        return "%s" % self.camera.awb_mode

    def get_iso(self):
        return "%s" % self.camera.iso

    def set_iso(self, iso):
        self.camera.iso = int(iso)
        self.camera.save()
        return "%s" % self.camera.iso

    def set_shutter_speed(self, shutter_speed):
        self.camera.shutter_speed = int(shutter_speed)
        self.camera.save()
        return "%s" % self.camera.shutter_speed

    def get_shutter_speed(self):
        return "%s" % self.camera.shutter_speed

    def get_exposure_speed(self):
        return "%s" % self.camera.exposure_speed

    def get_awb_gains(self):
        return json.dumps([float(g) for g in self.camera.awb_gains ])

    def set_awb_gains(self, gains):
        gains = [float(g) for g in gains.split(";")]
        self.camera.awb_gains = gains
        self.camera.save()
        return json.dumps([float(g) for g in self.camera.awb_gains ])

    def get_avg_rgb(self):
        return json.dumps(self.camera.get_avg_rgb())

    def shots_list(self):
        shots = []
        for path in glob.glob(os.path.join(storage_dir, "*")):
            path = path[len(storage_dir)+1:]
            shots.append(path)
        return json.dumps(shots)

    def shots_create(self, shot_id, timestamps, quality, projection_first):
        timestamps = [float(x) for x in timestamps.split(";")]
        projection_first = projection_first in [ "True", "true"]
        now = time.time()
        for ts in timestamps:
            if ts - 20 > now:
                print("shot ts out of range", ts)
                return
            if ts < now - 10:
                print("shot in past, ignore", ts)
                return
        self.camera.tasks.create_shot(shot_id, timestamps, quality, projection_first)

    # image_mode = normal | preview
    # image_type = normal | projection
    def shots_get(self, shot_id, image_mode, image_type ):
        if image_mode == "normal":
            image_mode = ""
        if image_mode == "preview":
            image_mode = "_preview"
        filepath = os.path.join(shot_id, "%s%s.jpg" % ( image_type, image_mode))
        if not os.path.exists(os.path.join(storage_dir, filepath)):
            return HTTPResponse(status=404)
        return static_file(filepath, root=storage_dir)

    def delete_shot(self, shot_id):
        p = os.path.join(storage_dir, shot_id)
        if not os.path.exists(p):
            return HTTPResponse(status=404)
        os.system("rm -r '%s'" % p)

if __name__ == "__main__":
    cam = Camera()
    time.sleep(3)
    print("FRAMES:")
    for frame in cam.port_still.capture(nr_of_frames=10, use_pll=True):
        print(frame)
        #print(len(frame.data.data))
