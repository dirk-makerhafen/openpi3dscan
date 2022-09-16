import json
import time

from app.files.shots import ShotsInstance


class Camera:
    def __init__(self, device):
        self.device = device
        self.settings = CameraSettings(self)
        self.shots = CameraShots(self)
        self.reihe = 1  # 1-7 top-bottom
        self.segment = 1  # 1-16
        self.busy_until = 0  # lock actions on device if benchmark or shot is active

    def preview(self, resolution=(640, 480)):
        self.device.wait_locked()
        try:
            result = self.device.api_request("/camera/preview/%s,%s/img.jpg" % (resolution[0], resolution[1]), timeout=20, max_tries=1).content
        except:
            return None
        return result

    def whitebalance(self):
        self.device.task_queue.put(self._whitebalance)

    def _whitebalance(self):
        result = self.device.api_request("/camera/calibrate/whitebalance")
        if result is not None:
            self.device.lock(7)
            time.sleep(9)
            self.settings.receive()


class CameraSettings:
    def __init__(self, camera : Camera):
        self.camera = camera
        self.iso = 100
        self.shutter_speed = 0
        self.exposure_speed = 0
        self.analog_gain = 0
        self.digital_gain = 0
        self.exposure_mode = "backlight"
        self.meter_mode = "backlit"
        self.awb_mode = "auto"
        self.awb_gains = [0, 0]
        self.avg_rgb = [-1, -1, -1]
        self.bounding_box = [-1, -1, -1, -1]
        self.quality = "speed"
        self.locked = False  # lock settings so heartbeat does not overwrite them for now

    def set_quality(self, quality):
        self.camera.device.task_queue.put([self._set_quality, quality])

    def _set_quality(self, quality):
        try:
            self.quality = self.camera.device.api_request("/camera/settings/quality/%s" % quality).text
        except Exception as e:
            print("failed to set quality", e)
        self.camera.device.notify_observers()

    def set_iso(self, new_iso):
        self.camera.device.task_queue.put([self._set_iso, new_iso])

    def _set_iso(self, new_iso):
        try:
            self.iso = int(self.camera.device.api_request("/camera/settings/iso/%s" % new_iso).text)
        except Exception as e:
            print("failed to set iso", e)
        self.camera.device.notify_observers()

    def set_exposure_mode(self, exposure_mode):
        self.camera.device.task_queue.put([self._set_exposure_mode, exposure_mode])

    def _set_exposure_mode(self, exposure_mode):
        try:
            self.exposure_mode = self.camera.device.api_request("/camera/settings/exposure_mode/%s" % exposure_mode).text
        except Exception as e:
            print("failed to set exposure_mode", e)
        self.camera.device.notify_observers()

    def set_meter_mode(self, meter_mode):
        self.camera.device.task_queue.put([self._set_meter_mode, meter_mode])

    def _set_meter_mode(self, meter_mode):
        try:
            self.meter_mode = self.camera.device.api_request("/camera/settings/meter_mode/%s" % meter_mode).text
        except Exception as e:
            print("failed to set meter_mode", e)
        self.camera.device.notify_observers()

    def set_awb_mode(self, awb_mode):
        self.camera.device.task_queue.put([self._set_awb_mode, awb_mode])

    def _set_awb_mode(self, awb_mode):
        try:
            self.awb_mode = self.camera.device.api_request("/camera/settings/awb_mode/%s" % awb_mode).text
        except Exception as e:
            print("failed to set awb_mode", e)
        self.camera.device.notify_observers()

    def set_shutter_speed(self, new_shutter_speed):
        self.camera.device.task_queue.put([self._set_shutter_speed, new_shutter_speed])

    def _set_shutter_speed(self, new_shutter_speed):
        for i in range(3):
            if self.camera.device.api_request("/camera/settings/shutter_speed/%s" % new_shutter_speed) is None:
                print("failed to set shutter_speed")
                break
            time.sleep(1)
            self.get_shutter_speed()
            if abs(self.shutter_speed - new_shutter_speed) < 100: # set successfull
                break
            print("must repeat set_shutter_speed")
        self.camera.device.notify_observers()

    def set_awb_gains(self, new_gains):
        self.camera.device.task_queue.put([self._set_awb_gains, new_gains])

    def _set_awb_gains(self, new_gains):
        new_gains_str = ";".join(["%s" % g for g in new_gains])
        for i in range(3):
            if self.camera.device.api_request("/camera/settings/awb_gains/%s" % new_gains_str) is None:
                print("failed to set awb_gains")
                break
            time.sleep(1)
            self.get_awb_gains()
            if abs(self.awb_gains[0] - new_gains[0]) < 0.03 and abs(self.awb_gains[1] - new_gains[1]) < 0.03: # set successfull
                break
            print("must repeat aws gain set")

        self.camera.device.notify_observers()

    def get_awb_gains(self):
        try:
            self.awb_gains = json.loads(self.camera.device.api_request("/camera/settings/awb_gains").text)
        except Exception as e:
            print("failed to get awb_gains", e)
        self.camera.device.notify_observers()
        return self.awb_gains

    def get_shutter_speed(self):
        try:
            self.shutter_speed = int(self.camera.device.api_request("/camera/settings/shutter_speed").text)
        except Exception as e:
            print("failed to get shutter_speed", e)
        self.camera.device.notify_observers()
        return self.shutter_speed

    def get_exposure_speed(self):
        try:
            self.exposure_speed = int(self.camera.device.api_request("/camera/settings/exposure_speed").text)
        except Exception as e:
            print("failed to get exposure_speed", e)
        self.camera.device.notify_observers()
        return self.exposure_speed

    def adjust_color(self, avg_r, avg_g, avg_b):
        self.camera.device.task_queue.put([self._adjust_color, avg_r, avg_g, avg_b])

    def _adjust_color(self, avg_r, avg_g, avg_b):
        diff_r = self.avg_rgb[0] - avg_r
        diff_g = self.avg_rgb[1] - avg_g
        diff_b = self.avg_rgb[2] - avg_b
        changed = False
        if diff_r > 1 and (diff_g > 1 or diff_b > 1):
            self.set_shutter_speed(self.shutter_speed - (abs(diff_r) * 500))
            changed = True
        elif diff_r < -1 and (diff_g < -1 or diff_b < -1):
            self.set_shutter_speed(self.shutter_speed + (abs(diff_r) * 500))
            changed = True
        else:
            new_gains = self.awb_gains[0:]
            if diff_g > 1:
                new_gains[0] = new_gains[0] - (abs(diff_g) / 15)
            elif diff_g < -1:
                new_gains[0] = new_gains[0] + (abs(diff_g) / 15)
            if diff_b > 1:
                new_gains[1] = new_gains[1] - (abs(diff_b) / 15)
            elif diff_b < -1:
                new_gains[1] = new_gains[1] + (abs(diff_b) / 15)
            if new_gains != self.awb_gains:
                self.set_awb_gains(new_gains)
                changed = True
        return changed

    def get_avg_rgb(self):
        result = self.camera.device.api_request("/camera/calibrate/get_avg_rgb")
        print(result)
        try:
            result = json.loads(result.text)
            self.avg_rgb = result[0]
            self.bounding_box = result[1]
        except Exception as e:
            print(e)
            self.bounding_box = [-1, -1, -1, -1]
            self.avg_rgb = [-1, -1, -1]
        print(result)
        return result

    def receive(self):
        try:
            results = json.loads(self.camera.device.api_request("/camera/settings/get").text)
        except Exception as e:
            print(e)
            return
        self.iso = results["iso"]
        self.shutter_speed = results["shutter_speed"]
        self.awb_gains = results["awb_gains"]
        self.camera.device.notify_observers()


class CameraShots:
    def __init__(self, camera : Camera):
        self.camera = camera
        self.shotlist = []

    def create(self, remote_shot, sequence, shot_quality, projection_first):
        self.camera.device.task_queue.put([self._create, remote_shot, sequence, shot_quality, projection_first])

    def delete(self, shot_id):
        self.camera.device.task_queue.put([self._delete, shot_id])

    def refresh_list(self):
        self.camera.device.task_queue.put([self._refresh_list])

    def _delete(self, shot_id):
        self.camera.device.api_request("/camera/shots/delete/%s" % shot_id, max_time=10)
        if shot_id in self.shotlist:
            self.shotlist.remove(shot_id)
        return True

    def _create(self, remote_shot, sequence, shot_quality, projection_first):
        sequence_str = ";".join(["%s" % s for s in sequence])
        self.camera.device.lock(6)  # + self.image_processing_time
        url = "/camera/shots/create/%s/%s/%s/%s" % (remote_shot.shot_id, sequence_str, shot_quality, projection_first)
        result = self.camera.device.api_request(url, max_time=5)
        if result is not None:
            sleeptime = sequence[-1] - time.time()
            if sleeptime > 0 and sleeptime < 10:
                time.sleep(sleeptime + 1)
            self.shotlist.append(remote_shot.shot_id)
            remote_shot.add_device(self.camera.device)
        return True

    # image_mode = normal | preview, image_type = normal | projection
    def download(self, shot_id, image_type, image_mode, return_image=True):
        # "/shot/<shot_id>/<image_mode>/<image_type>.jpg
        self.camera.device.wait_locked()
        self.camera.device.lock(10)
        try:
            r = self.camera.device.api_request("/camera/shots/get/%s/%s/%s.jpg" % (shot_id, image_mode, image_type), max_tries=1)
            data = r.content
        except:
            return None
        finally:
            self.camera.device.unlock()
        if len(data) < 10000:
            return None
        ShotsInstance().get(shot_id).add_image(image_type, image_mode, self.camera.device.device_id, data)
        if return_image is False:
            return None
        return data

    def _refresh_list(self):
        self.camera.device.wait_locked()
        shotlist = self.camera.device.api_request("/camera/shots/list", timeout=20, max_time=25, max_tries=2)
        if shotlist is not None:
            try:
                self.shotlist = json.loads(shotlist.text)
                ShotsInstance().sync_shotlist(self.shotlist, self.camera.device)
            except:
                pass
