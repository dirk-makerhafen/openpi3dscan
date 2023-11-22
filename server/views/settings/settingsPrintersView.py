from pyhtmlgui import PyHtmlView


class PrinterSettingsView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="Printers">
        <div class="row justify-content-center" style="width:100%">
            <div class="col-md-12">
                <div class="list-group mb-5 shadow">
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">3D Printer Management</div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-11">
                                <strong class="mb-0">Enable</strong>
                                <p class="text-muted mb-0">Enable printer management</p>
                            </div>
                            <div class="col-md-1">
                                <div class="custom-control custom-switch">
                                    <input id="enabled_printers"  type="checkbox" {% if pyview.subject.enabled == True %}checked{% endif %} onclick='pyview.subject.set_enabled($("#enabled_printers").prop("checked") === true)'>                                 
                                </div>
                            </div>         
                        </div>
                    </div> 
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <strong class="mb-0">Printers</strong>
                                <p class="text-muted mb-0"> List of available Printers</p>
                            </div>
                            <div class="col-md-4">
                                <div class="custom-control custom-switch">
                                    <textarea class="form-control" rows=8 id="printers_{{pyview.uid}}"  style="white-space: pre-wrap;width:100%" onchange='pyview.subject.set_printers($("#printers_{{pyview.uid}}").val())'>{{pyview.subject.printers}}</textarea>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <strong class="mb-0">Colors</strong>
                                <p class="text-muted mb-0"> List of available colors for printing</p>
                            </div>
                            <div class="col-md-4">
                                <div class="custom-control custom-switch">
                                    <textarea class="form-control" rows=8 id="colors_{{pyview.uid}}"  style="white-space: pre-wrap;width:100%" onchange='pyview.subject.set_colors($("#colors_{{pyview.uid}}").val())'>{{pyview.subject.colors}}</textarea>
                                </div>
                            </div>
                        </div>
                    </div>
                                        
                    
                </div>
            </div>   
        </div>
    </div>    
    '''
