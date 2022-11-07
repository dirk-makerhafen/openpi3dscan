from pyhtmlgui import PyHtmlView, ObservableListView

class logView(PyHtmlView):
    TEMPLATE_STR = '''
        {{pyview.subject}}
    '''
class RealityCaptureView(PyHtmlView):
    TEMPLATE_STR = '''
    
            <div class="row justify-content-center" style="width:100%">
                <div class="col-md-12">
                    <div class="list-group mb-5 shadow">
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-11 h3" style="border-bottom: 1px solid lightgray;">{{pyview.subject.shot_name}}, {{pyview.subject.filetype}}</div>
                                <div class="col-md-1 h3" style="border-bottom: 1px solid lightgray;">{{pyview.subject.status}}</div>
                            </div>
                        </div>
                        <div class="list-group-item">
                            <div class="row align-items-center" style="border-bottom: 1px solid lightgray;">
                                <div class="col-md-3" style="font-size: 1.2em;font-weight:bold">Filetype:</div>
                                <div class="col-md-1">{{pyview.subject.filetype}}</div>
                                <div class="col-md-3" style="font-size: 1.2em;font-weight:bold">Reconstruction quality:</div>
                                <div class="col-md-1">{{pyview.subject.reconstruction_quality}}</div>
                                <div class="col-md-3 " style="font-size: 1.2em;font-weight:bold">Export quality:</div>
                                <div class="col-md-1">{{pyview.subject.export_quality}}</div>
                            </div>
                            <div class="row align-items-center" style="border-bottom: 1px solid lightgray;">
                                <div class="col-md-3 " style="font-size: 1.2em;font-weight:bold">Create mesh from:</div>
                                <div class="col-md-1">{{pyview.subject.create_mesh_from}}</div>
                                <div class="col-md-3 " style="font-size: 1.2em;font-weight:bold">Create textures:</div>
                                <div class="col-md-1">{{pyview.subject.create_textures}}</div>
                                <div class="col-md-3 " style="font-size: 1.2em;font-weight:bold">Lit:</div>
                                <div class="col-md-1">{{pyview.subject.lit}}</div>
                            </div>
                            
                        </div>
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-10 h3" style="border-bottom: 1px solid lightgray;">Processing Steps</div>
                                <div class="col-md-2 h3" style="border-bottom: 1px solid lightgray;">button?</div>
                            </div>
                        </div>
                        {{pyview.prepareFolderView.render()}}
                        {% if pyview.downloadView %}
                            {{ pyview.downloadView.render() }}
                        {% endif %}
                        {{pyview.verifyImagesView.render()}}
                        {{pyview.calibrationDataWriteView.render()}}
                        {{pyview.markersView.render()}}
                        {{pyview.alignmentView.render()}}
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
        self.alignmentView = AlignmentView(subject.alignment, self)
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


class GenericTaskView(PyHtmlView):
    def __init__(self, subject, parent, **kwargs):
        super().__init__(subject, parent, **kwargs)
        self.logView = ObservableListView(subject.log, self, LogItemView)

class LogItemView(PyHtmlView):
    TEMPLATE_STR = '''{{pyview.subject.value}}'''

class PrepareFolderView(GenericTaskView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-1" style="text-align:center">{{pyview.subject.status}}</div>
                <div class="col-md-2">
                    <p>Prepare folders</p>
                </div>
                <div class="col-md-7">{{pyview.logView.render()}}</div>
                <div class="col-md-2"></div>
            </div>
        </div>
    '''
class DownloadView(GenericTaskView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-1" style="text-align:center">{{pyview.subject.status}}</div>
                <div class="col-md-2">
                    <p>Download</p>
                </div>
                <div class="col-md-7">{{pyview.logView.render()}}</div>
                <div class="col-md-2"></div>
            </div>
        </div>
    '''
class VerifyImagesView(GenericTaskView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-1" style="text-align:center">{{pyview.subject.status}}</div>
                <div class="col-md-2">
                    <p>Verify images</p>
                </div>
                <div class="col-md-7">{{pyview.logView.render()}}</div>
                <div class="col-md-2"></div>
            </div>
        </div>
    '''
class MarkersView(GenericTaskView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-1" style="text-align:center">{{pyview.subject.status}}</div>
                <div class="col-md-2">
                    <p>Detect markers</p>
                </div>
                <div class="col-md-7">{{pyview.logView.render()}}</div>
                <div class="col-md-2"></div>
            </div>
        </div>
    '''
class AlignmentView(GenericTaskView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-1" style="text-align:center">{{pyview.subject.status}}</div>
                <div class="col-md-2">
                    <p>Align images</p>
                </div>
                <div class="col-md-7">{{pyview.logView.render()}}</div>
                <div class="col-md-2"></div>
            </div>
        </div> 
    '''
class RawModelView(GenericTaskView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-1" style="text-align:center">{{pyview.subject.status}}</div>
                <div class="col-md-2">
                    <p>Create raw model</p>
                </div>
                <div class="col-md-7">{{pyview.logView.render()}}</div>
                <div class="col-md-2"></div>
            </div>
        </div>
    '''
class ExportmodelView(GenericTaskView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-1" style="text-align:center">{{pyview.subject.status}}</div>
                <div class="col-md-2">
                    <p>Create export model</p>
                </div>
                <div class="col-md-7">{{pyview.logView.render()}}</div>
                <div class="col-md-2"></div>
            </div>
        </div>
    '''
class AnimationView(GenericTaskView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">    
                <div class="col-md-1" style="text-align:center">{{pyview.subject.status}}</div>
                <div class="col-md-2">
                    <p>Create animation</p>
                </div>
                <div class="col-md-7">{{pyview.logView.render()}}</div>
                <div class="col-md-2"></div>
            </div>
        </div>
    '''
class ResultsArchiveView(GenericTaskView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-1" style="text-align:center">{{pyview.subject.status}}</div>
                <div class="col-md-2">
                    <p>Create result archive</p>
                </div>
                <div class="col-md-7">{{pyview.logView.render()}}</div>
                <div class="col-md-2"></div>
            </div>
        </div>
    '''
class UploadView(GenericTaskView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-1" style="text-align:center">{{pyview.subject.status}}</div>
                <div class="col-md-2">
                    <p>Upload results</p>
                </div>
                <div class="col-md-7">{{pyview.logView.render()}}</div>
                <div class="col-md-2"></div>
            </div>
        </div>
    '''

class CalibrationDataWriteView(GenericTaskView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-1" style="text-align:center">{{pyview.subject.status}}</div>
                <div class="col-md-2">
                    <p>Write calibration data</p>
                </div>
                <div class="col-md-7">{{pyview.logView.render()}}</div>
                <div class="col-md-2"></div>
            </div>
        </div>
    '''


class CalibrationDataUpdateView(GenericTaskView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-1" style="text-align:center">{{pyview.subject.status}}</div>
                <div class="col-md-2">
                    <p>Update calibration data</p>
                </div>
                <div class="col-md-7">{{pyview.logView.render()}}</div>
                <div class="col-md-2"></div>
            </div>
        </div>
    '''
