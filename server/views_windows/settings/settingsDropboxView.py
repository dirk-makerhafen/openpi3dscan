from pyhtmlgui import PyHtmlView

from app_windows.files.shotsDropboxDownload import ShotsDropboxDownloadInstance

import time

from pyhtmlgui import PyHtmlView

class DropboxDownloadView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="col-md-2">
        {% if pyview.subject.status == "idle" %}
            {% if pyview.subject.last_success != None %}
                <p>Last synchronized {{pyview.get_last_success()}} ago</p>
            {% endif %}
            {% if pyview.subject.last_failed != None %}
                <p>Failed to synchronized {{pyview.get_last_failed()}} ago</p>
            {% endif %}
        {% else %}
            <p>Downloading {{pyview.subject.current_download_shotid}}, {{pyview.subject.current_progress}}% done</p>
            {% if pyview.subject.current_download_file != "" %}
                <p>Current File: {{pyview.subject.current_download_file}}</p>
            {% else %}
                <p>&nbsp;</p>
            {% endif %}
        {% endif %}
    </div>
    <div class="col-md-2">
        <button class="btn" onclick="pyview.run()">Sync now</button<
    </div>
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
                            <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Location Synchronisation</div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-11">
                                <strong class="mb-0">Enable synchronisation</strong>
                                <p class="text-muted mb-0"> </p>
                            </div>
                            <div class="col-md-1">
                                <div class="custom-control custom-switch">
                                    <input id="dropbox_enabled"  type="checkbox" {% if pyview.subject.enabled == True %}checked{% endif %} onchange='pyview.subject.set_enabled($("#dropbox_enabled").prop("checked") === true)'>                                 
                                </div>
                            </div>         
                        </div>
                    </div>  
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <strong class="mb-0">Dropbox authorisation</strong>
                                 {% if pyview.subject.authorize_url != None %}
                                     <p class="text-muted mb-0">
                                        <a target="blanc" href="{{pyview.subject.authorize_url}}">CLICK HERE TO GET AUTHORISATION TOKEN</a>
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
                                    <button class="btn" onclick='pyview.subject.set_token($("#dropbox_token").val())'>authorize</button>
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
                                         <div class="col-md-2">
                                            <button class="btn"  onclick='pyview.subject.check_auth()'>check</button>
                                            <button class="btn btn-warning"  onclick='pyview.subject.start_authflow()'>reset</button>
                                         </div>
                                    {% else %}
                                        <div class="col-md-3">
                                             <p class="h5" style="color:#aa0000">Authorisation failed</p>
                                        </div>
                                        <div class="col-md-1">
                                            <button class="btn"  onclick='pyview.subject.start_authflow()'>reset</button>
                                        </div>
                                    {% endif %}
                                {% endif %}
                            {% endif %}
                            
                        </div>
                    </div>   
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-10">
                                <strong class="mb-0">Sync</strong>
                                <p class="text-muted mb-0">Next synchronisation in {{pyview.subject.get_next_sync_minutes()}} Minutes</p>
                            </div>
                           
                                {{pyview.dropboxDownloadView.render()}}
                            
                        </div>
                    </div>                                  
                </div>
            </div>   
        </div>
    </div>    
    '''
    def __init__(self, subject, parent):
        super().__init__(subject, parent)
        self.dropboxDownloadView = DropboxDownloadView(ShotsDropboxDownloadInstance(), self)

