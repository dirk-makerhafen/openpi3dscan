from pyhtmlgui import PyHtmlView


class HostnameSettingsView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="Hostname">
        <div class="row justify-content-center" style="width:100%">
            <div class="col-md-12">
                <div class="list-group mb-5 shadow">
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Server hostname</div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-10">
                                <strong class="mb-0">Hostname</strong>
                                <p class="text-muted mb-0">Server will be reachable at <a href="http://{{pyview.subject.hostname}}.local">http://{{pyview.subject.hostname}}.local</a></p>
                            </div>
                            <div class="col-md-2">
                                <input  class="form-control" id="hostname" value="{{pyview.subject.hostname}}" type="text"/>
                            </div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-10">
                                <strong class="mb-0">Save Changes</strong>
                                <p class="text-muted mb-0">Reboot to apply changes after saving!</p>
                            </div>
                            <div class="col-md-2">
                               <button class="btn " style="margin-right:5px" onclick='pyview.subject.set_hostname($("#hostname").val());'> Change hostname </button>
                            </div>
                        </div>
                    </div>    
                </div>
            </div>   
        </div>
    </div>    
    '''
