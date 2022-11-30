import time
from app.settings.settingsDropbox import SettingsDropbox

class SettingsDropboxWindows(SettingsDropbox):
    def __init__(self, parent):
        super().__init__(parent)
        self.next_sync_time = time.time() + 600

    def set_next_sync_time(self, new_next_sync_time):
        if self.next_sync_time != new_next_sync_time:
            self.next_sync_time = new_next_sync_time
            self.notify_observers()

    def get_next_sync_minutes(self):
        return max(0, int(round((self.next_sync_time - time.time()) / 60)))

    def set_sync_now(self):
        self.set_next_sync_time( time.time() + 1800)
        from app_windows.files.shotsDropboxDownload import ShotsDropboxDownloadInstance
        ShotsDropboxDownloadInstance().sync()

    def set_enabled(self, new_enabled):
        if self.enabled != new_enabled:
            self.enabled = new_enabled
            if self.enabled is True:
                self.next_sync_time  = time.time() + 600
            self.save()
            self.notify_observers()

    def _on_authflow_successfull(self):
        if self.enabled is True:
            self.next_sync_time = time.time() + 600
            self.notify_observers()