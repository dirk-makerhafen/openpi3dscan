from pyhtmlgui import Observable

class CardReaderPartition(Observable):
    def __init__(self, card, partition_name, size, fstype):
        super().__init__()
        self.card = card
        self.partition_name = partition_name
        self.size = size
        self.fstype = fstype
        self.mount_dir = None
