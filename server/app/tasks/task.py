from pyhtmlgui import Observable


class Task(Observable):
    def __init__(self):
        super().__init__()
        self.nr_of_threads = 20
        self.name = ""
