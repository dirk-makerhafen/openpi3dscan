from pyhtmlgui import PyHtmlView

class SettingsDropboxView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="Dropbox">
        <div class="row justify-content-center" style="width:100%">
            <div class="col-md-12">
                <div class="list-group mb-5 shadow">
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Dropbox</div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-11">
                                <strong class="mb-0">Location synchronisation</strong>
                                <p class="text-muted mb-0"> Enable sending images to main location.</p>
                            </div>
                            <div class="col-md-1">
                                <div class="custom-control custom-switch" style="text-align:center">
                                    <input id="dropbox_enabled"  type="checkbox" {% if pyview.subject.enabled == True %}checked{% endif %} onchange='pyview.subject.set_enabled($("#dropbox_enabled").prop("checked") === true)'>                                 
                                </div>
                            </div>         
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-11">
                                <strong class="mb-0">Public Sharing</strong>
                                <p class="text-muted mb-0"> Allow public data sharing via dropbox links</p>
                            </div>
                            <div class="col-md-1">
                                <div class="custom-control custom-switch" style="text-align:center">
                                    <input id="dropbox_enable_public"  type="checkbox" {% if pyview.subject.enable_public == True %}checked{% endif %} onchange='pyview.subject.set_enable_public($("#dropbox_enable_public").prop("checked") === true)'>                                 
                                </div>
                            </div>         
                        </div>
                    </div>    
                    {% if pyview.subject.enabled == True or pyview.subject.enable_public == True  %}
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
                    {% endif %}                          
                </div>
            </div>   
        </div>
    </div>    
    '''

