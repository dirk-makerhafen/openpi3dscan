from pyhtmlgui import PyHtmlView


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
                                     <input class="form-control" id="dropbox_token" value="{{pyview.subject.token}}" type="text" >
                                 </div>
                                 <div class="col-md-1">
                                    <button class="btn" onclick='pyview.subject.set_token($("#dropbox_token").val())'>authorize</button>
                                 </div>
                            {% else %}
                                {% if pyview.subject.refresh_token != "" and pyview.subject.token != "" %}
                                    <div class="col-md-3">
                                         <p class="h5" style="color:#00ff0066">Authorisation successfull</p>
                                     </div>
                                     <div class="col-md-1">
                                        <button class="btn"  onclick='pyview.subject.check_auth()'>check</button>
                                        <button class="btn btn-warning"  onclick='pyview.subject.start_authflow()'>reset</button>
                                     </div>
                                {% else %}
                                    {% if pyview.subject.refresh_token == "" and pyview.subject.token != ""  and pyview.subject.auth_flow != None %}
                                         <div class="col-md-3">
                                             <p class="h5" style="color:#ffff0066">Authorising</p>
                                         </div>
                                    {% else %}
                                        <div class="col-md-3">
                                             <p class="h5" style="color:#ff000066">Authorisation failed</p>
                                         </div>
                                         <div class="col-md-1">
                                            <button class="btn"  onclick='pyview.subject.start_authflow()'>reset</button>
                                         </div>
                                    {% endif %}
                                {% endif %}
                            
                            {% endif %}
                            
                        </div>
                    </div>                              
                </div>
            </div>   
        </div>
    </div>    
    '''

