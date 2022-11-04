import json
import os

import requests
from app_windows.realityCapture.genericTask import GenericTask


class Upload(GenericTask):
    def __init__(self, rc_job):
        super().__init__(rc_job)

    def upload_model(self, model_path):
        self.set_status("active")
        with open(model_path, 'rb') as f:
            print("Uploading model: %s" % model_path)
            try:
                requests.post("http://%s/shots/%s/upload/%s" % (self.rc_job.source_ip, self.rc_job.shot_id, self.rc_job.model_id), files={'upload_file': f})
                print("Upload finished")
            except:
                print("failed to reach server while uploading")
                self.process_failed(self.rc_job.shot_id, self.rc_job.model_id)

    def upload_calibration_data(self, data):
        print("Uploading calibration")
        try:
            requests.post("http://%s/upload_calibration" % (self.rc_job.source_ip), json={"data": json.dumps(data)})
            print("Upload finished")
        except:
            print("failed to reach server while uploading")
