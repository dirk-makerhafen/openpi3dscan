import time
from multiprocessing.pool import ThreadPool
from app.devices.devices import DevicesInstance
from .task import Task


class Task_ColorCalibrate(Task):
    def __init__(self):
        super().__init__()
        self.name = "ColorCalibrate"
        self.light_segment_adjustments = [0.95] * 16

    def run(self):
        cameras = DevicesInstance().cameras.list()
        lc = len(cameras)
        if lc == 0:
            return

        self.light_segment_adjustments = [0.95] * 16

        with ThreadPool(self.nr_of_threads) as p:
            print(p.map(lambda device: device.light.adjust(self.light_segment_adjustments), DevicesInstance().lights.list()))
            print(p.map(lambda device: device.light.set(100), DevicesInstance().lights.list()))
            print(p.map(lambda device: device.projector.disable(), DevicesInstance().projectors.list()))
            print(p.map(lambda device: device.camera.whitebalance(), cameras))

        time.sleep(2)

        for step in range(10):
            print("Step", step)

            with ThreadPool(self.nr_of_threads) as p:
                print(p.map(lambda device: device.camera.settings.get_avg_rgb(), cameras))

            # Calculate light Adjustments
            light_changed = self._calulate_light_adjustment()

            # Calculate rgb averages
            avg_r = sum([c.avg_rgb[0] for c in cameras]) / lc
            avg_g = sum([c.avg_rgb[1] for c in cameras]) / lc
            avg_b = sum([c.avg_rgb[2] for c in cameras]) / lc

            # Update devices
            with ThreadPool(self.nr_of_threads) as p:
                results_light = p.map(lambda device: device.light.adjust(self.light_segment_adjustments), DevicesInstance().lights.list())
                results_color = p.map(lambda device: device.camera.settings.adjust_color(avg_r, avg_g, avg_b)    , cameras)

            print("results_light", results_light)
            print("results_color", results_color)

            if True not in results_color and light_changed is False:
                break

    def _calulate_light_adjustment(self):
        light_segment_values = []
        light_changed = False

        for segment in range(0, 16):
            next_segment = segment + 1 if segment != 15 else  0
            prev_segment = segment - 1 if segment !=  0 else 15
            cameras  = DevicesInstance().get_cameras_by_segment(segment)
            cameras += DevicesInstance().get_cameras_by_segment(next_segment)
            cameras += DevicesInstance().get_cameras_by_segment(prev_segment)
            avg_light = sum([sum(c.camera.settings.avg_rgb) / 3 for c in cameras]) / len(cameras)
            light_segment_values.append(avg_light)

        global_avg_light = sum(light_segment_values) / len(light_segment_values)

        for segment in range(0, 16):
            diff = light_segment_values[segment] - global_avg_light
            if abs(diff) > 1:  # segment is to light or to dark
                self.light_segment_adjustments[segment] *= 1 - (diff / 150)
                light_changed = True
            if self.light_segment_adjustments[segment] > 1:
                self.light_segment_adjustments[segment] = 1

        print("light_segment_values", light_segment_values)
        print("self.light_segment_adjustments", self.light_segment_adjustments)

        return light_changed

