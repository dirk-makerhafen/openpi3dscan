import time

from pyhtmlgui import Observable
import os

class RC_Markers(Observable):
    def __init__(self, parent, markers, distances):
        super().__init__()
        self.parent = parent
        self.markers = markers
        self.distances = distances
        self.markers_csv = parent.get_workfiles_path("markers.cvs")
        self.available_markers = []
        self.status = "idle" # failed_ask_abort, repeat, success, failed
        self.parent.addlog(["markers", 'Marker detection initialized with %s known markers and %s distances' % (len(self.markers), len(self.distances))])

    def run(self):
        self._load_markers_csv()

        if len(self.available_markers) >= 10:
            self.parent.addlog(["markers", '%s markers loaded from cached "%s"' % (len(self.available_markers), self.markers_csv)])
            return True

        while len(self.available_markers) < 10:
            self._run_rc()
            self._load_markers_csv()
            if len(self.available_markers) >= 10:
                self.parent.addlog( ["markers", '%s markers loaded from "%s"' % (len(self.available_markers), self.markers_csv)])
                return True
            else:
                self.parent.addlog( ["markers", 'Marker detection failed, %s markers found in "%s", expecting at least 10' % (len(self.available_markers), self.markers_csv)])
                self.set_status("failed_ask_abort")
                while self.status == "failed_ask_abort":
                    time.sleep(1)
                self.clear()
                if self.status != "repeat":
                    break
                self.parent.addlog(["markers", 'Repeating marker detection'])

        self.clear()
        return False

    def set_status(self, status):
        if self.status != status:
            self.status = status
            self.notify_observers()

    def get_available_distances(self):
        for index1, marker1 in enumerate(self.available_markers):
            for marker2 in [self.available_markers[index2] for index2 in range(index1 + 1, len(self.available_markers))]:
                if marker1 not in self.distances:
                    continue
                if marker2 not in self.distances[marker1]:
                    continue
                yield [marker1, marker2, self.distances[marker1][marker2]]

    def _run_rc(self):
        self.parent.addlog(["markers", 'Starting marker detection'])
        cmd = self.parent.get_cmd_start()
        cmd += self.parent.get_cmd_new_scene()
        cmd += '-detectMarkers "%s\\tmp\\DetectMarkersParams.xml" ' % self.parent.source_path
        cmd += '-getLicense "%s" ' % self.parent.pin
        cmd += '-exportControlPointsMeasurements "%s" ' % ( self.markers_csv)
        cmd += '-quit '
        self.parent.addlog(["markers", 'Command: %s' % cmd])
        self.parent.run_command(cmd, "load_markers")

    def _load_markers_csv(self):
        markers = set()
        if os.path.exists(self.markers_csv):
            self.parent.addlog(["markers", 'Loading markers from "%s"' % self.markers_csv])
            with open(self.markers_csv, "r") as f:
                for line in f.read().split("\n"):
                    if line.startswith("#") or len(line) < 10:
                        continue
                    markers.add(line.split(",")[1].strip())
        else:
            self.parent.addlog(["markers", 'No markers file exists at "%s"' % self.markers_csv])
        self.available_markers = list(markers)

    def clear(self):
        self.parent.addlog(["markers", 'Clearing marker detection'])
        if os.path.exists(self.markers_csv):
            os.remove(self.markers_csv)
        self.available_markers = []
