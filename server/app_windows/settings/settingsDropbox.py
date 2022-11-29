import time
from app.settings.settingsDropbox import SettingsDropbox


class SettingsDropbox(SettingsDropbox):
    def __init__(self, parent):
        super().__init__(parent)
        self.next_sync_time = time.time()

    def set_next_sync_time(self, new_next_sync_time):
        if self.next_sync_time != new_next_sync_time:
            self.next_sync_time = new_next_sync_time
            self.notify_observers()

    def get_next_sync_minutes(self):
        return int((self.next_sync_time - time.time()) / 60)

    def set_sync_now(self):
        self.set_next_sync_time( time.time())
        from app_windows.files.shotsDropboxDownload import ShotsDropboxDownloadInstance
        ShotsDropboxDownloadInstance().sync()
