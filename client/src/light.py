import math
import struct
import threading
from queue import Queue
import time
from bottle import route
import RPi.GPIO as GPIO
try:
    import Adafruit_PCA9685
except:
    class Adafruit_PCA9685():
        class PCA9685():
            def __init__(self, address): pass
            def set_pwm_freq(self, value): pass
            def set_pwm(self, channel, on, off):
                print("set", channel, on, off)

from src.heartbeat import HeartbeatInstance

#     9   16   7   14
#  2			        5
# 11    		       12
#  4      	            3
# 13                   10
#     6   15   8   1
channel_offsets = { 0:1, 1:8, 2:15, 3:6, 4:13, 5:4, 6:11, 7:2, 8:9, 9:16, 10:7, 11:14, 12:5, 13:12, 14:3, 15:10}

class Light():
    def __init__(self):
        self.use_gpio = False
        self.gpio_pins = [4, 17, 22, 27]
        try:
            self.pwm = Adafruit_PCA9685.PCA9685(address=0x40)
            self.pwm.set_pwm_freq(323)
        except:
            print("Failed to init i2c, using gpio")
            self.use_gpio = True
            GPIO.setmode(GPIO.BOARD)
            for pin in  self.gpio_pins:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, False)

        self.task_queue = Queue()
        self.last_usage = time.time()
        self.light_segment_adjustments = [1.0] * 16
        self.current_value = 0
        self.set(self.current_value )

        self.screensaver_timeout = 600
        self._screensaver_active = False
        self._screensaver_values = [
            1.000, 0.050, 0.000, 0.000, 0.000, 0.000, 0.000, 0.050,
            1.000, 0.050, 0.000, 0.000, 0.000, 0.000, 0.000, 0.050]
        self._screensaver_max_steps = 1024
        self._screensaver_values_full = [0] * self._screensaver_max_steps
        self._screensaver_steps_per_col = self._screensaver_max_steps / 16
        #self.interpolate_screensaver_data()
        self.start()
        self.current_pwm_values = [[-1,-1] for i in range(16)]

    def interpolate_screensaver_data(self):
        ## init screensaver data
        for i in range(0, self._screensaver_max_steps):
            current_step = i / self._screensaver_steps_per_col
            current_step_index = int(math.floor(current_step))
            value = self._screensaver_values[current_step_index]
            rest = current_step - current_step_index
            if current_step_index == 15:
                next_value = self._screensaver_values[0]
            else:
                next_value = self._screensaver_values[current_step_index + 1]
            interpolated_value = value + (next_value - value ) * rest
            self._screensaver_values_full[i] = interpolated_value

    def start(self):
        self.t = threading.Thread(target=self._task_loop, daemon=True)
        self.t.start()

    def sequence(self, sequence):
        self.last_usage = time.time()
        self.task_queue.put(["sequence",sequence])

    def set(self, value):
        self.last_usage = time.time()
        self.task_queue.put(["set", value])

    def adjust(self, values):
        self.last_usage = time.time()
        self.task_queue.put(["adjust", values])

    def enable_screensaver(self):
        self.last_usage = time.time() - (self.screensaver_timeout + 10)

    def _task_loop(self):
        while True:
            try:
                task = self.task_queue.get(timeout=60)
            except:
                continue
            HeartbeatInstance().lock()
            try:
                if task[0] == "sequence":
                    self._run_sequence(task[1])
                elif task[0] == "set":
                    self._set(task[1])
                elif task[0] == "adjust":
                    self._adjust(task[1])
            except Exception as e:
                print("failed", e)
            HeartbeatInstance().unlock()

    def _run_sequence(self, sequence):
        prev_value = self.current_value
        for item in sequence:
            timestamp, value = item
            while time.time() < timestamp:
                time.sleep(0.0002)
            if value == -1:
                self._set(prev_value)
            else:
                self._set(value)

    def _set(self, value):
        if value <   0: value =   0
        if value > 100: value = 100
        if value < 1: # relative to current value
            value = self.current_value * value
        self.current_value = value

        if self.use_gpio is True:
            v = int(round(value / (100 / 15), 0))
            GPIO.output(self.gpio_pins[0], v & 0x1 != 0)
            GPIO.output(self.gpio_pins[1], v & 0x2 != 0)
            GPIO.output(self.gpio_pins[2], v & 0x4 != 0)
            GPIO.output(self.gpio_pins[3], v & 0x8 != 0)

        else:
            for channel in range(16):
                value_percent_channel = self.light_segment_adjustments[channel] * value
                self._set_with_offsets(channel, value_percent_channel)

    def _set_with_offsets(self, channel, value_percent):
        value_channel = (value_percent / 100) * 4095
        if value_channel == 0:
            self._set_pwm(channel, 4095, 0)
        elif value_channel >= 4095:
            self._set_pwm(channel, 0, 4095)
        else:
            offset = channel_offsets[channel] * 256
            on = offset - (value_channel / 2)
            off = on + value_channel
            if on < 0:
                on = 4096 - abs(on)
            if off > 4095:
                off = off - 4096
            on = int(round(on))
            off = int(round(off))
            self._set_pwm(channel, on, off)

    def _set_pwm(self, channel, on, off):
        if self.current_pwm_values[channel][0] != on or  self.current_pwm_values[channel][1] != off:
            self.current_pwm_values[channel] = [on, off]
            self.pwm.set_pwm(channel, on, off)

    def _adjust(self, values):
        self.light_segment_adjustments = values
        self._set(self.current_value)

    def _screensaver_step(self):
        self._screensaver_values_full.append(self._screensaver_values_full[0])
        del self._screensaver_values_full[0]
        for i in range(16):
            index = int(i * self._screensaver_steps_per_col)
            value = self._screensaver_values_full[index]
            channel_value = value * self.current_value
            self._set_with_offsets(i, channel_value)


class LightAPI():
    def __init__(self):
        self.light = Light()
        route("/light/set/<value>")(self.set)
        route("/light/adjust/<values>")(self.set)
        route("/light/sequence/<sequence>")(self.sequence)

    # 1..100 # absolut light value in percent
    # 0..0.9999 # relative to current value
    def set(self, value):
        self.light.set(float(value))

    def adjust(self, values):
        values = [float(v) for v in values.split(";")]
        self.light.adjust(values)

    def sequence(self,sequence):
        sequence = sequence.split(";")
        sequence = [item.split(":") for item in sequence]
        sequence = [[float(item[0]), float(item[1])] for item in sequence]
        now = time.time()
        for item in sequence:
            ts, value = item
            if ts - 20 > now:
                print("shot ts out of range", ts)
                return
            if ts < now - 5:
                print("shot in past, ignore", ts)
                return
        self.light.sequence(sequence)

    def screensaver(self):
        self.light.enable_screensaver()
