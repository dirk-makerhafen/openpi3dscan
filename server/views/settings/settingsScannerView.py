from pyhtmlgui import PyHtmlView


class SettingsScannerView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="SettingsScanner">
        <div class="row justify-content-center" style="width:100%">
            <div class="col-md-12">
                <div class="list-group mb-5 shadow">
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Hardware Setup</div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-10">
                                <strong class="mb-0">Location</strong>
                                <p class="text-muted mb-0">Unique scanner location name</p>
                            </div>
                            <div class="col-md-2">
                                <div class="custom-control custom-switch">
                                    <input  class="form-control" style="width:100%;text-align:center" id="scanner_location" type="text" value="{{pyview.subject.location}}" onchange='pyview.subject.set_location($("#scanner_location").val())'>
                                </div>
                            </div>
                        </div>
                    </div> 
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-11">
                                <strong class="mb-0">Segments</strong>
                                <p class="text-muted mb-0">Number of segments installed</p>
                            </div>
                            <div class="col-md-1">
                                <div class="custom-control custom-switch">
                                    <input class="form-control" style="width:100%;text-align:center" id="scanner_segments" type="number" min=2 max=24 value="{{pyview.subject.segments}}" onchange='pyview.subject.set_segments($("#scanner_segments").val())'>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-11">
                                <strong class="mb-0">Cameras</strong>
                                <p class="text-muted mb-0">Number of cameras per segment</p>
                            </div>
                            <div class="col-md-1">
                                <div class="custom-control custom-switch">
                                    <input class="form-control" style="width:100%;text-align:center" id="scanner_cameras_per_segment" type="number" min=1 max=24 value="{{pyview.subject.cameras_per_segment}}" onchange='pyview.subject.set_cameras_per_segment($("#scanner_cameras_per_segment").val())'>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-11">
                                <strong class="mb-0">Rotation</strong>
                                <p class="text-muted mb-0">Default camera rotation. You must update cameras for this change to take place!</p>
                            </div>
                            <div class="col-md-1">
                                <div class="custom-control custom-switch">
                                    <select class="form-control" name="camera_rotation" id="camera_rotation"  onchange='pyview.subject.set_camera_rotation($("#camera_rotation").val())'>
                                        <option value=0   {% if pyview.subject.camera_rotation == 0   %}selected{%endif%}>   0 </option>
                                        <option value=90  {% if pyview.subject.camera_rotation == 90  %}selected{%endif%}>  90 </option>
                                        <option value=180 {% if pyview.subject.camera_rotation == 180 %}selected{%endif%}> 180 </option>
                                        <option value=270 {% if pyview.subject.camera_rotation == 270 %}selected{%endif%}> 270 </option>
                                    </select>  
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-11">
                                <strong class="mb-0">Camera position numbering</strong>
                                <p class="text-muted mb-0">Position of first camera</p>
                            </div>
                            <div class="col-md-1">
                                <div class="custom-control custom-switch">
                                    <select class="form-control" name="camera_one_position" id="camera_one_position"  onchange='pyview.subject.set_camera_one_position($("#camera_one_position").val())'>
                                        <option value="top"    {% if pyview.subject.camera_one_position == "top"    %} selected {%endif%}> Top </option>
                                        <option value="bottom" {% if pyview.subject.camera_one_position == "bottom" %} selected {%endif%}> Bottom </option>
                                    </select>  
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-11">
                                <strong class="mb-0">Camera numbering</strong>
                                <p class="text-muted mb-0">First camera number (0 or 1)</p>
                            </div>
                            <div class="col-md-1">
                                <div class="custom-control custom-switch">
                                    <input class="form-control" style="width:100%;text-align:center" id="first_camera_number" type="number" min=0 max=1 value="{{pyview.subject.first_camera_number}}" onchange='pyview.subject.set_first_camera_number($("#first_camera_number").val())'>
                                </div>
                            </div>
                        </div>
                    </div>            
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-10">
                                <strong class="mb-0">Flipped cameras</strong>
                                <p class="text-muted mb-0">In case some cameras are upsite down, add their names as a comma separated list. eg: SEG1-CAM2,SEG23-CAM4. Device must be updated after changes.</p>
                            </div>
                            <div class="col-md-2">
                                <div class="custom-control custom-switch">
                                    <input class="form-control" style="width:100%;text-align:center" id="scanner_flipped_cameras" type="text" value="{{pyview.subject.flipped_cameras}}" onchange='pyview.subject.set_flipped_cameras($("#scanner_flipped_cameras").val())'>
                                </div>
                            </div>
                        </div>
                    </div>                                   
                </div>
            </div>   
        </div>
    </div>    
'''

