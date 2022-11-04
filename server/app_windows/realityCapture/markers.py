import os

from app_windows.realityCapture.genericTask import GenericTask


class Markers(GenericTask):
    def __init__(self, rc_job):
        super().__init__(rc_job)
        self.available_markers = []

    def load(self):
        markers_csv = self.rc_job.get_path("%s_markers.csv")
        force_reload = self.status != "idle"
        self.set_status("active")

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

        if len(self.available_markers) < 2:
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
        print("%s markers loaded" % len(self.available_markers))
