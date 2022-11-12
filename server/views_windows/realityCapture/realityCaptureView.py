from pyhtmlgui import PyHtmlView, ObservableListView

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
                                <div class="col-md-2 h3" style="border-bottom: 1px solid lightgray;"></div>
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
        self.prepareFolderView = GenericTaskView(subject.prepareFolder, self, "Prepare folders")
        if subject.download is not None:
            self.downloadView = GenericTaskView(subject.download, self, "Download")
        self.verifyImagesView = GenericTaskView(subject.verifyImages, self, "Verify images")
        self.calibrationDataWriteView = GenericTaskView(subject.calibrationDataWrite, self, "Write calibration data")
        self.markersView = GenericTaskView(subject.markers, self, "Detect markers")
        self.alignmentView = GenericTaskView(subject.alignment, self, "Align images")
        self.calibrationDataUpdateView = GenericTaskView(subject.calibrationDataUpdate, self, "Update calibration data")
        self.rawmodelView = GenericTaskView(subject.rawmodel, self, "Create raw model")
        self.exportmodelView = GenericTaskView(subject.exportmodel, self, "Create export model")
        if subject.animation is not None:
            self.animationView = GenericTaskView(subject.animation, self, "Create animation")
            self.resultsArchiveView = None
        else:
            self.resultsArchiveView = GenericTaskView(subject.resultsArchive, self, "Create result archive")
            self.animationView = None
        if subject.upload is not None:
            self.uploadView = GenericTaskView(subject.upload, self, "Upload results")
        else:
            self.uploadView = None


class GenericTaskView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-1" style="text-align:center">{{pyview.subject.status}}</div>
                <div class="col-md-2">
                    <p>{{pyview.name}}</p>
                </div>
                <div class="col-md-9">{{pyview.logView.render()}}</div>
            </div>
        </div>
    '''
    def __init__(self, subject, parent, name, **kwargs):
        super().__init__(subject, parent, **kwargs)
        self.name = name
        self.logView = ObservableListView(subject.log, self, LogItemView)

class LogItemView(PyHtmlView):
    TEMPLATE_STR = '''{{pyview.subject.value}}'''

