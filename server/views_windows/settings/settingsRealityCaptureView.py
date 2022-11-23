from pyhtmlgui import PyHtmlView


class SettingsRealityCaptureView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="RealityCapture">
        <div class="row justify-content-center" style="width:100%">
            <div class="col-md-12">
                <div class="list-group mb-5 shadow">
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">RealityCapture</div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-10">
                                <strong class="mb-0">Pin</strong>
                                <p class="text-muted mb-0">Setup RealityCapture pin at <a target="blanc" href="https://www.capturingreality.com/my.pin">https://www.capturingreality.com/my.pin</a></p>
                            </div>
                            <div class="col-md-2">
                                <div class="custom-control custom-switch">
                                    <input class="form-control" id="rc_pin" type="text" value="{{pyview.subject.pin}}" onchange='pyview.subject.set_pin($("#rc_pin").val())'>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-10">
                                <strong class="mb-0">Activation Token</strong>
                                <p class="text-muted mb-0">Get RealityCapture activation token at <a target="blanc" href="https://www.capturingreality.com/my.activation#PPI">https://www.capturingreality.com/my.activation#PPI</a></p>
                            </div>
                            <div class="col-md-2">
                                <div class="custom-control custom-switch">
                                    <input class="form-control" id="rc_token" type="text" value="{{pyview.subject.token}}" onchange='pyview.subject.set_token($("#rc_token").val())'>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-10">
                                <strong class="mb-0">Reconstruction quality</strong>
                                <p class="text-muted mb-0">Default reconstruction quality for RealityCapture </p>
                            </div>
                            <div class="col-md-2">
                                <div class="custom-control custom-switch">
                                     <select class="form-control" name="default_reconstruction_quality" id="default_reconstruction_quality"  onchange='pyview.subject.set_default_reconstruction_quality($("#default_reconstruction_quality").val())'>
                                        <option value="preview" {% if pyview.subject.default_reconstruction_quality == "preview"%}selected{%endif%}>Preview</option>
                                        <option value="normal"  {% if pyview.subject.default_reconstruction_quality == "normal" %}selected{%endif%}>Normal</option>
                                        <option value="high"    {% if pyview.subject.default_reconstruction_quality == "high"    %}selected{%endif%}>High</option>
                                    </select>  
                                </div>
                            </div>
                            
                        </div>
                    </div>                                 
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-10">
                                <strong class="mb-0">Export quality</strong>
                                <p class="text-muted mb-0">Default export quality for RealityCapture. </p>
                            </div>
                            <div class="col-md-2">
                                <div class="custom-control custom-switch">
                                     <select class="form-control" name="default_export_quality" id="default_export_quality"  onchange='pyview.subject.set_default_export_quality($("#default_export_quality").val())'>
                                        <option value="low"    {% if pyview.subject.default_export_quality == "low"    %}selected{%endif%}>Low (500k)</option>
                                        <option value="normal" {% if pyview.subject.default_export_quality == "normal" %}selected{%endif%}>Normal (1M)</option>
                                        <option value="high"   {% if pyview.subject.default_export_quality == "high"    %}selected{%endif%}>High (4M)</option>
                                    </select>  
                                </div>
                            </div>
                            
                        </div>
                    </div>    
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-10">
                                <strong class="mb-0">Mesh from</strong>
                                <p class="text-muted mb-0">Default for images for mesh creation </p>
                            </div>
                            <div class="col-md-2">
                                <div class="custom-control custom-switch">
                                     <select class="form-control" name="default_create_mesh_from" id="default_create_mesh_from"  onchange='pyview.subject.set_default_create_mesh_from($("#default_create_mesh_from").val())'>
                                        <option value="normal"     {% if pyview.subject.default_create_mesh_from == "normal"     %}selected{%endif%}>Normal</option>
                                        <option value="projection" {% if pyview.subject.default_create_mesh_from == "projection" %}selected{%endif%}>Projection</option>
                                        <option value="all"        {% if pyview.subject.default_create_mesh_from == "all"         %}selected{%endif%}>All</option>
                                    </select>  
                                </div>
                            </div>
                            
                        </div>
                    </div>        
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-11">
                                <strong class="mb-0">Texture</strong>
                                <p class="text-muted mb-0">Create textures by default. </p>
                            </div>
                            <div class="col-md-1">
                                <div class="custom-control custom-switch">
                                    <input class="form-check-input" id="default_create_textures"  type="checkbox" {% if pyview.subject.default_create_textures == True %}checked{% endif %} onclick='pyview.subject.set_default_create_textures($("#default_create_textures").prop("checked") === true)'>                                 
                                </div>
                            </div>         
                        </div>
                    </div>  
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-11">
                                <strong class="mb-0">Lit / Unlit</strong>
                                <p class="text-muted mb-0">GLB, GIF and WEBP default lit. </p>
                            </div>
                            <div class="col-md-1">
                                <div class="custom-control custom-switch">
                                    <input class="form-check-input" id="default_lit"  type="checkbox" {% if pyview.subject.default_lit == True %}checked{% endif %} onclick='pyview.subject.set_default_lit($("#default_lit").prop("checked") === true)'>                                 
                                </div>
                            </div>         
                        </div>
                    </div> 
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-11">
                                <strong class="mb-0">Hide RealityCapture</strong>
                                <p class="text-muted mb-0">Don't show RealityCapture window during processing</p>
                            </div>
                            <div class="col-md-1">
                                <div class="custom-control custom-switch">
                                    <input class="form-check-input" id="hide_realitycapture"  type="checkbox" {% if pyview.subject.hide_realitycapture == True %}checked{% endif %} onclick='pyview.subject.set_hide_realitycapture($("#hide_realitycapture").prop("checked") === true)'>                                 
                                </div>
                            </div>         
                        </div>
                    </div>                        
                </div>
            </div>   
        </div>
    </div>
    '''

