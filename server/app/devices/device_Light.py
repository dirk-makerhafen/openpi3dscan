class Light:
    def __init__(self, device):
        self.device = device

    def adjust(self, values):
        self.device.task_queue.put([self._adjust, values])

    def _adjust(self, values):
        self.device.wait_locked()
        values = ";".join(["%s" % v for v in values])
        self.device.api_request("/light/adjust/%s" % values)

    def set(self, value):
        self.device.task_queue.put([self._set, value])

    def _set(self, value):
        self.device.wait_locked()
        self.device.api_request("/light/set/%s" % value)

    def sequence(self, sequence):
        self.device.task_queue.put([self._sequence, sequence])

    def _sequence(self, sequence):
        sequence = ";".join(["%s:%s" % (s[0], s[1]) for s in sequence])
        self.device.lock(6)
        self.device.api_request("/light/sequence/%s" % sequence)
