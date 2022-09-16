from pyhtmlgui import PyHtmlView


class SettingsScannerView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="SystemRestart">
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
                                <strong class="mb-0">Segments</strong>
                                <p class="text-muted mb-0">Number of segments installed</p>
                            </div>
                            <div class="col-auto">
                                <input id="scanner_segments" type="number" min=2 max=24 value="{{pyview.subject.segments}}" onchange='pyview.subject.set_segments($("#scanner_segments").val())'>
                            </div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-10">
                                <strong class="mb-0">Cameras</strong>
                                <p class="text-muted mb-0">Number of cameras per segment</p>
                            </div>
                            <div class="col-auto">
                                <input id="scanner_cameras_per_segment" type="number" min=1 max=24 value="{{pyview.subject.cameras_per_segment}}" onchange='pyview.subject.set_cameras_per_segment($("#scanner_cameras_per_segment").val())'>
                            </div>
                        </div>
                    </div>
                </div>
            </div>   
        </div>
    </div>    
'''

