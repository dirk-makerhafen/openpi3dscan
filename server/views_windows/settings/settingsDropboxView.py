from pyhtmlgui import PyHtmlView

from app_windows.files.shotsDropboxDownload import ShotsDropboxDownloadInstance
import webbrowser

import time

from pyhtmlgui import PyHtmlView

class DropboxDownloadView(PyHtmlView):
    TEMPLATE_STR = '''
        {% if pyview.subject.status == "idle" %}
            <div class="col-md-3">
                {% if pyview.subject.last_success != None %}
                    <p class="h5">Last synchronized {{pyview.get_last_success()}} ago</p>
                {% endif %}
                {% if pyview.subject.last_failed != None %}
                    <p class="h5">Failed to synchronized {{pyview.get_last_failed()}} ago</p>
                {% endif %}
            </div>
            <div class="col-md-1">
                <button class="btn btnfw" onclick="pyview.run()">Sync Now</button>
            </div>
        {% else %}
            <div class="col-md-4">
                <p class="h5">Synchronizing Dropbox</p>
                {% if pyview.subject.current_download_shotid != "" %}
                    <p class="h5"> {{pyview.subject.current_download_shotid}}, {{pyview.subject.current_progress}}% finished</p>
                {% endif %}
            </div>
        {% endif %}
    
    '''
    def get_last_success(self):
        seconds = time.time() - self.subject.last_success
        return self._convert_time(seconds)

    def get_last_failed(self):
        seconds = time.time() - self.subject.last_failed
        return self._convert_time(seconds)

    def _convert_time(self, seconds):
        minutes = int(seconds / 60 )
        if minutes < 2:
            return "%s seconds" % int(seconds)
        hours = int(seconds / 60 / 60 )
        if hours < 2:
            return "%s minutes" % minutes
        days = int(seconds / 60 / 60 / 24 )
        if days < 2:
            return "%s hours" % hours
        weeks = int(seconds / 60 / 60 / 24 / 7)
        if weeks < 5:
            return "%s days" % days
        return "%s weeks" % weeks

    def run(self):
        ShotsDropboxDownloadInstance().sync()



class SettingsDropboxView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="Dropbox">
        <div class="row justify-content-center" style="width:100%">
            <div class="col-md-12">
                <div class="list-group mb-5 shadow">
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Remote Synchronisation</div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-11">
                                <strong class="mb-0">Enable synchronisation of remote locations via Dropbox.</strong>
                                <p class="text-muted mb-0"> </p>
                            </div>
                            <div class="col-md-1" style="text-align:center">
                                <div class="custom-control custom-switch">
                                    <input id="dropbox_enabled"  type="checkbox" {% if pyview.subject.enabled == True %}checked{% endif %} onchange='pyview.subject.set_enabled($("#dropbox_enabled").prop("checked") === true)'>                                 
                                </div>
                            </div>         
                        </div>
                    </div>  
                    {% if pyview.subject.enabled == True %}
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-8">
                                    <strong class="mb-0">Dropbox authorisation</strong>
                                     {% if pyview.subject.authorize_url != None %}
                                         <p class="text-muted mb-0">
                                            <a onclick="pyview.open_authlink()" href="#">CLICK HERE TO GET AUTHORISATION TOKEN</a>
                                        </p>
                                     {% else %}
                                        <p class="text-muted mb-0">Authorize Dropbox access for this app</p>
                                     {% endif %}
                                </div>
                                {% if pyview.subject.authorize_url != None %}
                                     <div class="col-md-3">
                                         <input class="form-control" id="dropbox_token" type="text" >
                                     </div>
                                     <div class="col-md-1">
                                        <button class="btn btnfw btn-success" onclick='pyview.subject.set_token($("#dropbox_token").val())'>Authorize</button>
                                     </div>
                                {% else %}
                                    {% if pyview.subject.token != "" and pyview.subject.auth_flow != None %}
                                         <div class="col-md-3">
                                             <p class="h5" style="color:#aaaa00">Authorising</p>
                                         </div>
                                    {% else %}
                                        {% if pyview.subject.refresh_token != "" and pyview.subject.token != "" %}
                                            <div class="col-md-2">
                                                 <p class="h5" style="color:#00aa00">Authorisation successfull</p>
                                             </div>
                                             <div class="col-md-1">
                                                <button class="btn btn-warning btnfw"  onclick='pyview.subject.start_authflow()'>Reset</button>
                                             </div>
                                             <div class="col-md-1">
                                                <button class="btn btnfw"  onclick='pyview.subject.check_auth()'>Check</button>
                                             </div>
                                        {% else %}
                                            <div class="col-md-3">
                                                 <p class="h5" style="color:#aa0000">Authorisation failed</p>
                                            </div>
                                            <div class="col-md-1">
                                                <button class="btn btnfw"  onclick='pyview.subject.start_authflow()'>Renew</button>
                                            </div>
                                        {% endif %}
                                    {% endif %}
                                {% endif %}      
                            </div>
                        </div>   
                        {% if pyview.subject.is_authorized() %}
                            <div class="list-group-item">
                                <div class="row align-items-center">
                                    <div class="col-md-8">
                                        <strong class="mb-0">Download</strong>
                                        {% if pyview.shotsDropboxDownloadInstance.status == "idle" %}
                                            <p class="text-muted mb-0">Next automatic download in {{pyview.subject.get_next_sync_minutes()}} Minutes</p>
                                        {% else %} 
                                            <p class="text-muted mb-0">Automatic download active</p>
                                        {% endif %} 
                                    </div>
                                    {{pyview.dropboxDownloadView.render()}}
                                </div>
                            </div>   
                        {% endif %}                               
                    {% endif %}                               
                </div>
            </div>   
        </div>
    </div>          
    '''
    def __init__(self, subject, parent):
        super().__init__(subject, parent)
        self.shotsDropboxDownloadInstance = ShotsDropboxDownloadInstance()
        self.dropboxDownloadView = DropboxDownloadView(self.shotsDropboxDownloadInstance, self)
        self.add_observable(self.shotsDropboxDownloadInstance)

    def open_authlink(self):
        if self.subject.authorize_url != None:
            webbrowser.open(self.subject.authorize_url)

