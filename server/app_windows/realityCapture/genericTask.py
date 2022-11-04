from pyhtmlgui import Observable


class GenericTask(Observable):
    def __init__(self, rc_job):
        super().__init__()
        self.rc_job = rc_job
        self.status = "idle"

    def set_status(self, new_status):
        if self.status == new_status:
            return
        self.status = new_status
        self.notify_observers()
