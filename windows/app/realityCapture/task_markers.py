from pyhtmlgui import Observable
import os

class Subtask_Markers(Observable):
    def __init__(self, parent, markers, distances):
        super().__init__()
        self.parent = parent
        self.markers = markers
        self.distances = distances
        self.markers_csv = parent.get_workfiles_path("markers.cvs")
        self.available_markers = []

    def run(self):
        self._load_markers_csv()
        while len(self.available_markers) < 10:
            self._run_rc()
            self._load_markers_csv()
            if len(self.available_markers) < 10:
                self.clear()
                print("No markers ask continue, break?")
                result = False
                if result == True:
                    break
        print("%s markers loaded" % len(self.available_markers))


    def get_available_distances(self):
        for index1, marker1 in enumerate(self.available_markers):
            for marker2 in [self.available_markers[index2] for index2 in range(index1 + 1, len(self.available_markers))]:
                if marker1 not in self.distances:
                    continue
                if marker2 not in self.distances[marker1]:
                    continue
                yield [marker1, marker2, self.distances[marker1][marker2]]

    def _run_rc(self):
        cmd = self.parent.get_cmd_start()
        cmd += self.parent.get_cmd_new_scene()
        cmd += '-detectMarkers "%s\\tmp\\DetectMarkersParams.xml" ' % self.parent.source_path
        cmd += '-getLicense "%s" ' % self.parent.pin
        cmd += '-exportControlPointsMeasurements "%s" ' % ( self.markers_csv)
        cmd += '-quit '
        self.parent.run_command(cmd, "load_markers")

    def _load_markers_csv(self):
        markers = set()
        if os.path.exists(self.markers_csv):
            with open(self.markers_csv, "r") as f:
                for line in f.read().split("\n"):
                    if line.startswith("#") or len(line) < 10:
                        continue
                    markers.add(line.split(",")[1].strip())
        self.available_markers = list(markers)

    def clear(self):
        if os.path.exists(self.markers_csv):
            os.remove(self.markers_csv)
        self.available_markers = []
