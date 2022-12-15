import glob
import os
import random

from app_windows.realityCapture.genericTask import GenericTask

XMP_TEMPLATE_full = '''
<x:xmpmeta xmlns:x="adobe:ns:meta/">
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description xcr:Version="3" xcr:PosePrior="initial" xcr:Coordinates="absolute"
       xcr:DistortionModel="brown3" xcr:FocalLength35mm="%(FocalLength35mm)s"
       xcr:Skew="0" xcr:AspectRatio="1" xcr:PrincipalPointU="%(PrincipalPointU)s"
       xcr:PrincipalPointV="%(PrincipalPointV)s" xcr:CalibrationPrior="initial"
       xcr:CalibrationGroup="%(Group)s" xcr:DistortionGroup="%(Group)s" xcr:InTexturing="%(InTexturing)s"
       xcr:InMeshing="%(InMeshing)s" xmlns:xcr="http://www.capturingreality.com/ns/xcr/1.1#">
      <xcr:Rotation>%(Rotation)s</xcr:Rotation>
      <xcr:Position>%(Position)s</xcr:Position>
      <xcr:DistortionCoeficients>%(DistortionCoeficients)s</xcr:DistortionCoeficients>
    </rdf:Description>
  </rdf:RDF>
</x:xmpmeta>
'''
XMP_TEMPLATE = '''
<x:xmpmeta xmlns:x="adobe:ns:meta/">
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description xcr:Version="3" xcr:Coordinates="absolute" xcr:DistortionModel="brown3" 
            xcr:FocalLength35mm="%(FocalLength35mm)s"
            xcr:PrincipalPointU="%(PrincipalPointU)s"
            xcr:PrincipalPointV="%(PrincipalPointV)s" 
            xcr:PosePrior="initial"
            xcr:CalibrationPrior="%(CalibrationPrior)s"
            xcr:CalibrationGroup="%(Group)s" 
            xcr:DistortionGroup="%(Group)s" 
            xmlns:xcr="http://www.capturingreality.com/ns/xcr/1.1#">
            <xcr:DistortionCoeficients>%(DistortionCoeficients)s</xcr:DistortionCoeficients>
            <xcr:Rotation>%(Rotation)s</xcr:Rotation>
            <xcr:Position>%(Position)s</xcr:Position>
        </rdf:Description>
</rdf:RDF>
</x:xmpmeta>
'''

class CalibrationData(GenericTask):
    def __init__(self, rc_job, initial_data):
        super().__init__(rc_job)
        self.data = initial_data
        self.xmp_exclude = []
        self.written_files = {}

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

    def update_from_xmp(self):
        cnt = 0

        cam_data = self._read_xmp_files()
        self.delete_xmp_files()
        first_time_calibration = len(self.data) == 0
        for data in cam_data:
            if data["FocalLength35mm"] > 37 or data["FocalLength35mm"] < 33:
                #print("No adding", data )
                continue
            if data["cam_id"] not in self.xmp_exclude:
                self.add_data(data["segment"], data["row"], "FocalLength35mm", data["FocalLength35mm"])
                self.add_data(data["segment"], data["row"], "PrincipalPointU", data["PrincipalPointU"])
                self.add_data(data["segment"], data["row"], "PrincipalPointV", data["PrincipalPointV"])
                self.add_data(data["segment"], data["row"], "DistortionCoeficients", data["DistortionCoeficients"])
            if "Rotation" in data:
                self.add_data(data["segment"], data["row"], "Rotation", data["Rotation"])
            if "Position" in data:
                self.add_data(data["segment"], data["row"], "Position", data["Position"])
            cnt += 1
        if first_time_calibration is True:
            positions = [data["Position"] for data in cam_data if "Position" in data]
            c_x = (max([x[0] for x in positions]) + min([x[0] for x in positions])) / 2
            c_y = (max([x[1] for x in positions]) + min([x[1] for x in positions])) / 2
            c_z = (max([x[2] for x in positions]) + min([x[2] for x in positions])) / 2
            center_align = [c_x, c_y, c_z - (self.rc_job.box_dimensions[2] / 2)]
            print("new center data", center_align)
            self.center(center_align)
        return cnt

    def write_xmp_files(self):
        self.xmp_exclude = []
        cnt = 0
        self.written_files = {}
        for cam_id in self.get_camera_ids():
            segment, row = cam_id.split("-")
            group_id = ( int(segment) * 100 ) + int(row)
            if self.count(segment, row, "FocalLength35mm") == 0:
               continue

            CalibrationPrior = "initial"
            if self.count(segment, row, "FocalLength35mm") > 20 and random.random() > 0.10: # 10% chance to adjust focus even if we already have enough data
                CalibrationPrior = "locked"
                self.xmp_exclude.append(cam_id)

            try:
                s = XMP_TEMPLATE % {
                    "FocalLength35mm"       :                             self.get(segment, row, "FocalLength35mm"),
                    "PrincipalPointU"       :                             self.get(segment, row, "PrincipalPointU"),
                    "PrincipalPointV"       :                             self.get(segment, row, "PrincipalPointV"),
                    "DistortionCoeficients" : " ".join(["%s" % x for x in self.get(segment, row, "DistortionCoeficients")] ),
                    "Rotation"              : " ".join(["%s" % x for x in self.get(segment, row, "Rotation")] ),
                    "Position"              : " ".join(["%s" % x for x in self.get(segment, row, "Position")] ),
                    "Group"                 : group_id,
                    "CalibrationPrior"      : CalibrationPrior,
                }
                for mode in ["normal", "projection"]:
                    xmp_path = os.path.join(self.rc_job.workingdir, "images", mode, "seg%s-cam%s-%s.xmp" % (segment, row, mode[0]))
                    img_path = xmp_path.replace(".xmp", ".jpg")
                    if os.path.exists(img_path):
                        cnt += 1
                        with open(xmp_path, "w") as f:
                            f.write(s)
                        self.written_files["seg%s-cam%s-%s.xmp" % (segment, row, mode[0])] = os.path.getmtime(xmp_path)
            except:
                pass
        return cnt

    def _read_xmp_files(self):
        camera_data = []
        for xmp_path in glob.glob(os.path.join(self.rc_job.workingdir, "images", "*", "*.xmp")):
            img_path = xmp_path.replace(".xmp",".jpg")
            if not os.path.exists(img_path):
                continue
            fname = os.path.split(xmp_path)[1]
            if fname in self.written_files and self.written_files[fname] == os.path.getmtime(xmp_path): # file did not change
                continue

            data = open(xmp_path, "r").read()
            try:
                cam_data = {
                    "segment"              : fname.split("-")[0].replace("seg","").strip(),
                    "row"                  : fname.split("-")[1].replace("cam","").strip(),
                    "mode"                 : fname.split('-')[2].strip(),
                    "FocalLength35mm"      : float(data.split("FocalLength35mm=")[1].split('"')[1]),
                    "PrincipalPointU"      : float(data.split("PrincipalPointU=")[1].split('"')[1]),
                    "PrincipalPointV"      : float(data.split("PrincipalPointV=")[1].split('"')[1]),
                    "DistortionCoeficients": [float(x) for x in data.split("DistortionCoeficients>")[1].split('<')[0].split(" ")],
                    "CalibrationPrior"     : data.split("CalibrationPrior=")[1].split('"')[1],
                } 
                cam_data["cam_id"] = "%s-%s" % (cam_data["segment"], cam_data["row"])
            except Exception as e:
                print("Failed to load", xmp_path ,e)
                continue
            try:
                cam_data["Rotation"]= [float(x) for x in data.split("Rotation>")[1].split('<')[0].split(" ")]
            except Exception as e:
                pass
            try:
                cam_data["Position"] = [float(x) for x in data.split("Position>")[1].split('<')[0].split(" ")]
            except Exception as e:
                try:
                    cam_data["Position"] = [float(x) for x in data.split("Position=")[1].split('"')[1].split(" ")]
                except Exception as e:
                    pass

            camera_data.append(cam_data)
        return camera_data

    def delete_xmp_files(self):
        for path in glob.glob(os.path.join(self.rc_job.workingdir, "images", "*","*.xmp")):
            os.remove(path)
