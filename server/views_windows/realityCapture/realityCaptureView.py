from pyhtmlgui import PyHtmlView, ObservableListView

class logView(PyHtmlView):
    TEMPLATE_STR = '''
        {{pyview.subject}}
    '''
class RealityCaptureView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="main">
        <div class="RealityCapture">
            <div class="row justify-content-center" style="width:100%">
                <div class="col-md-12">
                    <div class="list-group mb-5 shadow">
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-10 h3" style="border-bottom: 1px solid lightgray;">RealityCapture</div>
                                <div class="col-md-2 h3" style="border-bottom: 1px solid lightgray;">{{pyview.subject.status}}</div>
                            </div>
                        </div>
                    </div>
                </div>   
            </div>
            
        </div>
        <div class="TAsks">
            <div class="row justify-content-center" style="width:100%">
                <div class="col-md-12">
                    <div class="list-group mb-5 shadow">
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-10 h3" style="border-bottom: 1px solid lightgray;">Task shot_id</div>
                                <div class="col-md-2 h3" style="border-bottom: 1px solid lightgray;">{{pyview.subject.status}}</div>
                            </div>
                        </div>

                        
                        {{pyview.prepareFolderView.render()}}
                        {% if pyview.downloadView %}
                            {{ pyview.downloadView.render() }}
                        {% endif %}
                        {{pyview.verifyImagesView.render()}}
                        {{pyview.calibrationDataWriteView.render()}}
                        {{pyview.markersView.render()}}
                        {{pyview.alignmentsView.render()}}
                        {{pyview.calibrationDataUpdateView.render()}}
                        {{pyview.rawmodelView.render()}}
                        {{pyview.exportmodelView.render()}}
                        {% if pyview.animation %}
                            {{ pyview.animation.render() }}
                        {% endif %}
                        {% if pyview.resultsArchiveView %}
                            {{ pyview.resultsArchiveView.render() }}
                        {% endif %}
                        {% if pyview.uploadView %}
                            {{ pyview.uploadView.render() }}
                        {% endif %}


                    </div>
                </div>   
                
            </div>
            
        </div>  


    </div>
    '''
    def __init__(self, subject, parent, **kwargs):
        super().__init__(subject, parent, **kwargs)
        #self.foo = ObservableListView(self.subject.log, self, logView)
        self.prepareFolderView = PrepareFolderView(subject.prepareFolder, self)
        if subject.download is not None:
            self.downloadView = DownloadView(subject.download, self)
        self.verifyImagesView = VerifyImagesView(subject.verifyImages, self)
        self.calibrationDataWriteView = CalibrationDataWriteView(subject.calibrationDataWrite, self)
        self.markersView = MarkersView(subject.markers, self)
        self.alignmentsView = AlignmentsView(subject.alignments, self)
        self.calibrationDataUpdateView = CalibrationDataUpdateView(subject.calibrationDataUpdate, self)
        self.rawmodelView = RawModelView(subject.rawmodel, self)
        self.exportmodelView = ExportmodelView(subject.exportmodel, self)
        if subject.animation is not None:
            self.animationView = AnimationView(subject.animation, self)
            self.resultsArchiveView = None
        else:
            self.resultsArchiveView = ResultsArchiveView(subject.resultsArchive, self)
            self.animationView = None
        if subject.upload is not None:
            self.uploadView = UploadView(subject.upload, self)
        else:
            self.upload = None

class PrepareFolderView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-3">
                    <p>prepare</p>
                </div>
                <div class="col-md-2"></div>
                <div class="col-md-2">idle</div>
            </div>
        </div>
    '''
class DownloadView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-3">
                    <p>downoad</p>
                </div>
                <div class="col-md-2"></div>
                <div class="col-md-2">idle</div>
            </div>
        </div>
    '''
class VerifyImagesView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-3">
                    <p>verifyImages</p>
                </div>
                <div class="col-md-2">
                    5 images_cleaned 
                </div>
                <div class="col-md-2">
                    Idle
                </div>
            </div>
        </div>
    '''
class MarkersView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-3">
                    <p>markers</p>
                </div>
                <div class="col-md-2">23 markers detected</div>
                <div class="col-md-2">idle</div>
            </div>
        </div>
    '''
class AlignmentsView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-3">
                    <p>alignment</p>
                </div>
                <div class="col-md-2">
                    23 cameras aligned
                </div>
                <div class="col-md-2">idle</div>
            </div>
        </div> 
    '''
class RawModelView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-3">
                    <p>rawmodel</p>
                </div>
                <div class="col-md-2"></div>
                <div class="col-md-2">idle</div>
            </div>
        </div>
    '''
class ExportmodelView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-3">
                    <p>exportmodel</p>
                </div>
                <div class="col-md-2"></div>
            </div>
        </div>
    '''
class AnimationView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-3">
                    <p>animate</p>
                </div>
                <div class="col-md-2"></div>
                <div class="col-md-2">idle</div>
            </div>
        </div>
    '''
class ResultsArchiveView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-3">
                    <p>result</p>
                </div>
                <div class="col-md-2"></div>
                <div class="col-md-2">idle</div>
            </div>
        </div>
    '''
class UploadView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-3">
                    <p>upload</p>
                </div>
                <div class="col-md-2"></div>
                <div class="col-md-2">idle</div>
            </div>
        </div>
    '''

class CalibrationDataWriteView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-3">
                    <p>calibrationDataWrite</p>
                </div>
                <div class="col-md-2"></div>
                <div class="col-md-2">idle</div>
            </div>
        </div>
    '''
class CalibrationDataUpdateView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-3">
                    <p>calibrationDataupdate</p>
                </div>
                <div class="col-md-2"></div>
                <div class="col-md-2">idle</div>
            </div>
        </div>
    '''
