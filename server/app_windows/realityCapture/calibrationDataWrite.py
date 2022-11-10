from app_windows.realityCapture.genericTask import GenericTask

class CalibrationDataWrite(GenericTask):
    def __init__(self, rc_job):
        super().__init__(rc_job)

    def run(self):
        self.set_status("active")
        self.rc_job.calibrationData.delete_xmp_files()
        cnt = self.rc_job.calibrationData.write_xmp_files()
        self.log.append("%s images precalibrated" % cnt)
        self.set_status("success")