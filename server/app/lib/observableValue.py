from pyhtmlgui import Observable


class ObservableValue(Observable):
    def __init__(self, value):
        super().__init__()
        self._value = value
    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, value):
        self.set(value)
    def set(self, value):
        if value != self._value:
            self._value = value
            self.notify_observers()