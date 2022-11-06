import json
import os

import requests
from app_windows.realityCapture.genericTask import GenericTask


class Upload(GenericTask):
    def __init__(self, rc_job):
        super().__init__(rc_job)

    def run(self):
        self.set_status("active")
        with open(self.rc_job.result_file, 'rb') as f:
            self.log.append("Upload model to %s" % self.rc_job.source_ip)
            try:
                requests.post("http://%s/shots/%s/upload/%s" % (self.rc_job.source_ip, self.rc_job.shot_id, self.rc_job.model_id), files={'upload_file': f})
                self.set_status("success")
            except:
                self.log.append("Upload failed")
                self.set_status("failed")
                return

        self.log.append("Upload calibration data to %s" % self.rc_job.source_ip)
        try:
            requests.post("http://%s/upload_calibration" % (self.rc_job.source_ip), json={"data": json.dumps(self.rc_job.calibrationData.data)})
        except:
            self.log.append("Failed to upload calibration data")
            self.set_status("failed")
            return
        self.set_status("success")