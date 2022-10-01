from pyhtmlgui import Observable
import os, glob


class XMPData(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.rc_proj_file = parent.get_filepath("realityCapture.rcproj")
        self.xmp_data = []

    def run(self):
        self._run_rc()
        self._read_xmp_files()
        return len(self.xmp_data) > 50

    def _run_rc(self):
        cmd = self.parent.get_cmd_start()
        cmd += '-load "%s" ' % (self.rc_proj_file)
        cmd += '-exportXMP "%s\\tmp\\xmp_settings.xml" ' % self.parent.source_folder
        cmd += '-quit '
        self.parent.run_command(cmd, "export_xmp")

    def _read_xmp_files(self):
        self.xmp_data  = []
        for path in glob.glob(os.path.join(self.parent.images_path, "*", "*.xmp")):
            img_path = path.replace(".xmp", ".jpg")
            if not os.path.exists(img_path):
                continue
            data = open(path, "r").read()
            try:
                cam_data = {
                    "segment": path.split('\\')[-1].split("-")[0].replace("seg", "").strip(),
                    "row": path.split('\\')[-1].split("-")[1].replace("cam", "").strip(),
                    "mode": path.split('\\')[-1].split('-')[2].strip(),
                    "FocalLength35mm": float(data.split("FocalLength35mm=")[1].split('"')[1]),
                    "PrincipalPointU": float(data.split("PrincipalPointU=")[1].split('"')[1]),
                    "PrincipalPointV": float(data.split("PrincipalPointV=")[1].split('"')[1]),
                    "DistortionCoeficients": [float(x) for x in data.split("DistortionCoeficients>")[1].split('<')[0].split(" ")],
                    "CalibrationPrior": data.split("CalibrationPrior=")[1].split('"')[1],
                }
                cam_data["cam_id"] = "%s-%s" % (cam_data["segment"], cam_data["row"])
            except Exception as e:
                print("Failed to load", path, e)
                continue
            try:
                cam_data["Rotation"] = [float(x) for x in data.split("Rotation>")[1].split('<')[0].split(" ")]
            except Exception as e:
                pass
            try:
                cam_data["Position"] = [float(x) for x in data.split("Position>")[1].split('<')[0].split(" ")]
            except Exception as e:
                try:
                    cam_data["Position"] = [float(x) for x in data.split("Position=")[1].split('"')[1].split(" ")]
                except Exception as e:
                    pass

            self.xmp_data.append(cam_data)


    def clear(self):
        for path in glob.glob(os.path.join(self.parent.images_path, "*", "*.xmp")):
            os.remove(path)
        self.xmp_data = []