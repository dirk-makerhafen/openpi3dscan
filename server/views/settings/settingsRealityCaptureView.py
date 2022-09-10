from pyhtmlgui import PyHtmlView


class RealityCaptureView(PyHtmlView):
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
                                <strong class="mb-0">RealityCapture Automation Software</strong>
                                <p class="text-muted mb-0">Software package to automate RealityCapture. Download, unzip, run <b>start.bat</b> </p>
                            </div>
                            <div class="col-auto">
                                <div class="custom-control custom-switch">
                                    <a href="/windows_pack.zip">DOWNLOAD</a>
                                    <span class="custom-control-label"></span>
                                </div>
                            </div>
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
                                    <input id="rc_pin" type="text" value="{{pyview.subject.pin}}" onchange='pyview.subject.set_pin($("#rc_pin").val())'>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <strong class="mb-0">Marker Distances</strong>
                                <p class="text-muted mb-0"> Distances of markers for RealityCapture reconstruction scaling</p>
                            </div>
                            <div class="col-md-4">
                                <div class="custom-control custom-switch">
                                    <textarea rows=8 id="marker_distances_{{pyview.uid}}"  style="white-space: pre-wrap;width:100%" onchange='pyview.subject.set_markers($("#marker_distances_{{pyview.uid}}").val())'>{{pyview.subject.markers}}</textarea>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <strong class="mb-0">Reconstruction region</strong>
                                <p class="text-muted mb-0">Size of RealityCapture reconstruction region</p>
                            </div>
                            <div class="col-md-2">
                                <div class="custom-control custom-switch">
                                    <p>Diameter</p> 
                                    <input id="region_diameter" type="number" step="0.01" value="{{pyview.subject.diameter}}" onchange='pyview.subject.set_diameter($("#region_diameter").val())'>
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="custom-control custom-switch">
                                    <p>Height</p>
                                    <input id="region_height" type="number" step="0.01" value="{{pyview.subject.height}}" onchange='pyview.subject.set_height($("#region_height").val())'>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>   
        </div>
    </div>
    '''

