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
                    </div>
                </div>   
            </div>
        </div>
    '''

