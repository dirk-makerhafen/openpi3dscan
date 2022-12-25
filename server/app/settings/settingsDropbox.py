import os
import re
import time

import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect
from pyhtmlgui import Observable

class SettingsDropbox(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.save = parent.save
        self.enabled = False
        self.enable_public = False
        self.token = ""
        self.refresh_token = ""
        self.authorize_url = None
        self.auth_flow = None
        self.app_key = "laqa1f9bjza8viz"

    def to_dict(self):
        return {
            "enabled": self.enabled,
            "enable_public": self.enable_public,
            "token": self.token,
            "refresh_token": self.refresh_token,
        }

    def from_dict(self, data):
        self.token = data["token"]
        self.enabled = data["enabled"]
        self.enable_public = data["enable_public"]
        self.refresh_token = data["refresh_token"]

    def set_token(self, new_token):
        if self.token != new_token:
            self.token = new_token
            self.finish_authflow()
            self.save()
            self.notify_observers()

    def set_enable_public(self, new_enable_public):
        if self.enable_public != new_enable_public:
            self.enable_public = new_enable_public
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
        self.auth_flow = DropboxOAuth2FlowNoRedirect(self.app_key, use_pkce=True, token_access_type='offline')
        self.authorize_url = self.auth_flow.start()
        self.set_refresh_token("")

    def finish_authflow(self):
        self.refresh_token = ""
        self.authorize_url = None
        self.notify_observers()
        try:
            oauth_result = self.auth_flow.finish(self.token)
            with dropbox.Dropbox(oauth2_refresh_token=oauth_result.refresh_token, app_key=self.app_key) as dbx:
                dbx.users_get_current_account()
                self.refresh_token = oauth_result.refresh_token
            self._on_authflow_successfull()
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
            with dropbox.Dropbox(oauth2_refresh_token=self.refresh_token, app_key=self.app_key) as dbx:
                dbx.users_get_current_account()
        except Exception as e:
            print('Error: %s' % (e,))
            self.refresh_token = ""
            return
        finally:
            self.auth_flow = None
            self.notify_observers()

    def is_authorized(self):
        return self.refresh_token != "" and self.auth_flow == None

    def _on_authflow_successfull(self):
        pass