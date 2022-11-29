import os
import re

import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect
from pyhtmlgui import Observable
APP_KEY = "cnjh44n7t8bdsc7"

class SettingsDropbox(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.save = parent.save
        self.enabled = False
        self.token = ""
        self.refresh_token = ""
        self.authorize_url = None
        self.auth_flow = None

    def to_dict(self):
        return {
            "enabled": self.enabled,
            "token": self.token,
            "refresh_token": self.refresh_token,
        }

    def from_dict(self, data):
        self.token = data["token"]
        self.enabled = data["enabled"]
        self.refresh_token = data["refresh_token"]

    def set_token(self, new_token):
        if self.token != new_token:
            self.token = new_token
            self.finish_authflow()
            self.save()
            self.notify_observers()

    def set_enabled(self, new_enabled):
        if self.enabled != new_enabled:
            self.enabled = new_enabled
            self.save()
            self.notify_observers()

    def set_refresh_token(self, new_refresh_token):
        if self.refresh_token != new_refresh_token:
            self.refresh_token = new_refresh_token
            self.save()
            self.notify_observers()

    def start_authflow(self):
        self.refresh_token = ""
        self.auth_flow = DropboxOAuth2FlowNoRedirect(APP_KEY, use_pkce=True, token_access_type='offline')
        self.authorize_url = self.auth_flow.start()
        self.notify_observers()

    def finish_authflow(self):
        self.refresh_token = ""
        self.authorize_url = None
        self.notify_observers()
        try:
            oauth_result = self.auth_flow.finish(self.token)
            with dropbox.Dropbox(oauth2_refresh_token=oauth_result.refresh_token, app_key=APP_KEY) as dbx:
                dbx.users_get_current_account()
                print("Successfully set up client!")
                self.refresh_token = oauth_result.refresh_token
        except Exception as e:
            print('Error: %s' % (e,))
            return
        finally:
            self.auth_flow = None
        self.notify_observers()

    def check_auth(self):
        self.auth_flow = "not_none"
        self.notify_observers()
        try:
            with dropbox.Dropbox(oauth2_refresh_token=self.refresh_token, app_key=APP_KEY) as dbx:
                dbx.users_get_current_account()
                print("Successfully set up client!")
        except Exception as e:
            print('Error: %s' % (e,))
            self.refresh_token = ""
            return
        finally:
            self.auth_flow = None
            self.notify_observers()
