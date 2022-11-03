import os

from pyhtmlgui import Observable


class Markers(Observable):
    def __init__(self, rc_job):
        super().__init__()
        self.rc_job = rc_job
        self.available_markers = []
        self.status = "idle"

    def set_status(self, new_status):
        if self.status == new_status:
            return
        self.status = new_status
        self.notify_observers()

    def load(self, force_reload=False):
        markers_csv = self.rc_job.get_path("%s_markers.csv")
        if force_reload is True and os.path.exists(markers_csv):
            os.remove(markers_csv)

        if os.path.exists(markers_csv):
            self._load_markers_csv(markers_csv)

        if len(self.available_markers) < 2 or force_reload is True:
            cmd = self.rc_job._get_cmd_start()
            cmd += self.rc_job._get_cmd_new_scene()
            cmd += '-detectMarkers "%s" ' %  self.rc_job.get_path("DetectMarkersParams.xml")
            cmd += '-getLicense "%s" ' % self.rc_job.pin
            cmd += '-exportControlPointsMeasurements "%s" ' % markers_csv
            cmd += '-quit '
            self.rc_job._run_command(cmd, "load_markers")
            self._load_markers_csv(markers_csv)

    def _load_markers_csv(self, markers_csv):
        markers = set()
        if os.path.exists(markers_csv):
            with open(markers_csv, "r") as f:
                for line in f.read().split("\n"):
                    if line.startswith("#") or len(line) < 10:
                        continue
                    markers.add(line.split(",")[1].strip())
        self.available_markers = list(markers)
        print("%s markers loaded" % len(self.available_markers))
