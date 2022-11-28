from pyhtmlgui import PyHtmlView

from app_windows.files.shotsDropboxDownload import ShotsDropboxDownloadInstance

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
                            <div class="col-md-10">
                                <strong class="mb-0">Access token</strong>
                                <p class="text-muted mb-0">Access token for Dropbox synchronisation</p>
                            </div>
                            <div class="col-md-2">
                                <input class="form-control" id="dropbox_token" value="{{pyview.subject.token}}" type="text" onchange='pyview.subject.set_token($("#dropbox_token").val())'\>
                            </div>
                        </div>
                    </div>  
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-10">
                                <strong class="mb-0">Sync</strong>
                                <p class="text-muted mb-0">Next synchronisation in {{pyview.subject.get_next_sync_minutes()}} Minutes</p>
                            </div>
                            <div class="col-md-2">
                                <button onclick="pyview.run()">Sync now</button<
                            </div>
                        </div>
                    </div>                                  
                </div>
            </div>   
        </div>
    </div>    
    '''
    def run(self):
        ShotsDropboxDownloadInstance().sync()

