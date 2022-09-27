import random

from pyhtmlgui import Observable
import os, glob

from app.realityCapture.configfiles import XMP_TEMPLATE


class CalibrationData(Observable):
    def __init__(self, parent, initialData ):
        super().__init__()
        self.data = initialData
        self.parent = parent
        for cam_id in self.get_camera_ids():
            segment, row = cam_id.split("-")
            count = self.count(segment, row, "FocalLength35mm")
            if count == 0:
                continue
            CalibrationPrior = "initial"
            if count > 20 and random.random() > 0.10:  # 10% chance to adjust focus even if we already have enough data
                CalibrationPrior = "locked"
            self.data[cam_id]["CalibrationPrior"] = CalibrationPrior


    def reset(self):
        self.data = {}

    def reset_positions(self):
        for key in self.data:
            if "Position" in self.data[key]:
                del self.data[key]["Position"]
            if "Rotation" in self.data[key]:
                del self.data[key]["Rotation"]

    def center(self,center_align):
        x,y,z = center_align
        for key in self.data:
            if "Position" in self.data[key]:
                for index, pos in enumerate(self.data[key]["Position"]):
                    pos = [pos[0] - x, pos[1] - y, pos[2] - z, ]
                    self.data[key]["Position"][index] = pos

    def get_camera_ids(self):
        return ["%s" % key for key in self.data.keys()]

    def get(self, segment, row, key):
        cam_id = "%s-%s" % (segment, row)
        data = self.data[cam_id][key]
        if type(data[0]) == list:
            return [ sum( t[i] for t in data) / len(data) for i in range(0,len(data[0])) ]
        else:
            return sum(data) / len(data)

    def count(self, segment, row, key):
        cam_id = "%s-%s" % (segment, row)
        try:
            return len(self.data[cam_id][key])
        except:
            return 0

    def add_data(self, segment, row, key, data):
        cam_id = "%s-%s" % ( segment, row )
        if cam_id not in self.data:
            self.data[cam_id] = {}
        if key not in self.data[cam_id]:
            self.data[cam_id][key] = []
        self.data[cam_id][key].append(data)
        self.data[cam_id][key] = self.data[cam_id][key][-30:]

    def write_as_xmp(self):
        self.xmp_exclude = []
        for cam_id in self.get_camera_ids():
            segment, row = cam_id.split("-")
            group_id = (int(segment) * 100) + int(row)
            if self.count(segment, row, "FocalLength35mm") == 0:
                continue

            try:
                s = XMP_TEMPLATE % {
                    "FocalLength35mm": self.get(segment, row, "FocalLength35mm"),
                    "PrincipalPointU": self.get(segment, row, "PrincipalPointU"),
                    "PrincipalPointV": self.get(segment, row, "PrincipalPointV"),
                    "DistortionCoeficients": " ".join( ["%s" % x for x in self.get(segment, row, "DistortionCoeficients")]),
                    "Rotation": " ".join(["%s" % x for x in self.get(segment, row, "Rotation")]),
                    "Position": " ".join(["%s" % x for x in self.get(segment, row, "Position")]),
                    "Group": group_id,
                    "CalibrationPrior": self.data[cam_id]["CalibrationPrior"],
                }
                for mode in ["normal", "projection"]:
                    xmp_path = os.path.join(self.parent.images_path, mode, "seg%s-cam%s-%s.xmp" % (segment, row, mode[0]))
                    img_path = xmp_path.replace(".xmp", ".jpg")
                    if os.path.exists(img_path):
                        with open(xmp_path, "w") as f:
                            f.write(s)
            except:
                pass


    def add_from_xmp(self, xmp_data):
        first_time_calibration = len(self.data) == 0
        for data in xmp_data:
            if data["FocalLength35mm"] > 37 or data["FocalLength35mm"] < 33:
                # print("No adding", data )
                continue
            if data["cam_id"] not in self.xmp_exclude:
                self.add_data(data["segment"], data["row"], "FocalLength35mm", data["FocalLength35mm"])
                self.add_data(data["segment"], data["row"], "PrincipalPointU", data["PrincipalPointU"])
                self.add_data(data["segment"], data["row"], "PrincipalPointV", data["PrincipalPointV"])
                self.add_data(data["segment"], data["row"], "DistortionCoeficients",
                                         data["DistortionCoeficients"])
            if "Rotation" in data:
                self.add_data(data["segment"], data["row"], "Rotation", data["Rotation"])
            if "Position" in data:
                self.add_data(data["segment"], data["row"], "Position", data["Position"])

        if first_time_calibration is True:
            positions = [data["Position"] for data in xmp_data if "Position" in data]
            c_x = (max([x[0] for x in positions]) + min([x[0] for x in positions])) / 2
            c_y = (max([x[1] for x in positions]) + min([x[1] for x in positions])) / 2
            c_z = (max([x[2] for x in positions]) + min([x[2] for x in positions])) / 2
            center_align = [c_x, c_y, c_z - (BOX_DIMENSIONS[2] / 2)]
            print("new center data", center_align)
            self.center(center_align)

