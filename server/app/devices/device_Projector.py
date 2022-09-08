class Projector:
    def __init__(self, device):
        self.device = device

    def enable(self):
        self.device.task_queue.put(self._enable)

    def _enable(self):
        self.device.wait_locked()
        self.device.api_request("/projector/enable")

    def disable(self):
        self.device.task_queue.put(self._disable)

    def _disable(self):
        self.device.wait_locked()
        self.device.api_request("/projector/disable")

    def sequence(self, sequence):
        self.device.task_queue.put([self._sequence, sequence])

    def _sequence(self, sequence):
        sequence = ";".join(["%s:%s" % (s[0], s[1]) for s in sequence])
        self.device.lock(6)
        result = self.device.api_request("/projector/sequence/%s" % sequence)
        print("sequence started on %s" % self.device.ip, result)
