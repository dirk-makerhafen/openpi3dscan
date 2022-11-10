import math
import os

from app_windows.realityCapture.genericTask import GenericTask


class Markers(GenericTask):
    def __init__(self, rc_job, distances):
        super().__init__(rc_job)
        self.distances = distances
        self.available_markers = []

    def run(self):
        markers_csv = self.get_path("%s_markers.csv")
        force_reload = self.status != "idle"
        if len(self.distances) == 0:
            self.log.append("Not distances loaded, not detecting markers")
            self.set_status("success")
            return

        self.set_status("active")

        if force_reload is True and os.path.exists(markers_csv):
            self.log.append("Removing cached markers")
            os.remove(markers_csv)

        if os.path.exists(markers_csv):
            self._load_markers_csv(markers_csv)
            self.log.append("%s of %s Markers loaded from cache" % (len(self.available_markers), len(self.distances)))
            if len(self.available_markers) >= math.floor(len(self.distances) / 10.0):
                self.set_status("success")
                return
            self.log.append("less than 10% of markers loaded, must run detection")

        cmd = self._get_cmd_start()
        cmd += self._get_cmd_new_scene()
        cmd += '-detectMarkers "%s" ' %  self.get_path("DetectMarkersParams.xml")
        cmd += '-getLicense "%s" ' % self.rc_job.pin
        cmd += '-exportControlPointsMeasurements "%s" ' % markers_csv
        cmd += '-quit '
        self._run_command(cmd, "load_markers")

        self._load_markers_csv(markers_csv)
        self.log.append("%s of %s Markers detected" % (len(self.available_markers),  len(self.distances)))

        if len(self.available_markers) < math.floor(len(self.distances)/10.0):
            self.log.append("less than 10% of markers detected, failed")
            self.set_status("failed")
        else:
            self.set_status("success")

    def _load_markers_csv(self, markers_csv):
        markers = set()
        if os.path.exists(markers_csv):
            with open(markers_csv, "r") as f:
                for line in f.read().split("\n"):
                    if line.startswith("#") or len(line) < 10:
                        continue
                    markers.add(line.split(",")[1].strip())
        self.available_markers = list(markers)
