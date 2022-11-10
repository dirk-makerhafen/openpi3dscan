from app_windows.realityCapture.genericTask import GenericTask

class CalibrationDataUpdate(GenericTask):
    def __init__(self, rc_job):
        super().__init__(rc_job)

    def run(self):
        self.set_status("active")
        if self.rc_job.alignment.alignments_were_recreated is False:
            self.log.append("Alignments from cache, not updating calibrations")
            self.set_status("success")
            return

        cnt = self.rc_job.calibrationData.update_from_xmp()
        self.log.append("%s calibrations updated" % cnt)
        self.set_status("success")