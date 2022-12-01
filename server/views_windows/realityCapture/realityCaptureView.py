from pyhtmlgui import PyHtmlView, ObservableListView

class RealityCaptureView(PyHtmlView):
    TEMPLATE_STR = '''
            <div class="row justify-content-center" style="width:100%">
                <div class="col-md-12">
                    <div class="list-group mb-5 shadow">
                        <div class="list-group-item" style="padding-bottom:0px"> 
                            <div class="row align-items-center">
                                <div class="col-md-11 h3" style="border-bottom: 1px solid lightgray;margin-top:10px;margin-bottom:2px">
                                    <b>{{pyview.subject.shot_name}}</b>
                                </div>
                                <div class="col-md-1 h3" style="border-bottom: 1px solid lightgray;margin-top:10px;margin-bottom:2px">{{pyview.subject.status}}</div>
                            </div>
                        </div>
                        <div class="list-group-item" style="padding-bottom:10px">
                            <div class="row align-items-center" style="border-bottom: 1px solid lightgray;">
                                <div class="col-md-2 " style="font-size: 1.3em"><b style="font-size:0.8em">File:</b> {{pyview.subject.filetype}}</div>
                                <div class="col-md-2 " style="font-size: 1.3em"><b style="font-size:0.8em">Mesh:</b> {{pyview.subject.create_mesh_from}}</div>
                                <div class="col-md-2 " style="font-size: 1.3em"><b style="font-size:0.8em">Reconstruction:</b> {{pyview.subject.reconstruction_quality}}</div>
                                <div class="col-md-2 " style="font-size: 1.3em"><b style="font-size:0.8em">Export:</b> {{pyview.subject.export_quality}}</div>                                
                                <div class="col-md-2 " style="font-size: 1.3em"><b style="font-size:0.8em">Textures:</b> {{pyview.subject.create_textures}}</div>
                                <div class="col-md-2 " style="font-size: 1.3em"><b style="font-size:0.8em">Lit:</b> {{pyview.subject.lit}}</div>                                
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
                        {% if pyview.animationView %}
                            {{ pyview.animationView.render() }}
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
        self.prepareFolderView         = GenericTaskView(subject.prepareFolder, self, "Prepare folders")
        if subject.download is not None:
            self.downloadView          = GenericTaskView(subject.download, self, "Download")

        self.verifyImagesView          = GenericTaskView(subject.verifyImages, self, "Verify images")
        self.calibrationDataWriteView  = GenericTaskView(subject.calibrationDataWrite, self, "Write calibration data")
        self.markersView               = GenericTaskView(subject.markers, self, "Detect markers")
        self.alignmentView             = GenericTaskView(subject.alignment, self, "Align images")
        self.calibrationDataUpdateView = GenericTaskView(subject.calibrationDataUpdate, self, "Update calibration data")
        self.rawmodelView              = GenericTaskView(subject.rawmodel, self, "Reconstruction")
        self.exportmodelView           = GenericTaskView(subject.exportmodel, self, "Create export model")
        self.rcprojExportView = None
        self.animationView = None
        self.resultsArchiveView = None
        self.uploadView = None

        if subject.rcprojExport is not None:
            self.rcprojExportView      = GenericTaskView(subject.rcprojExport, self, "Create rcproj export")
        if subject.animation is not None:
            self.animationView         = GenericTaskView(subject.animation, self, "Create animation")
        if subject.resultsArchive is not None:
            self.resultsArchiveView    = GenericTaskView(subject.resultsArchive, self, "Compress results")
        if subject.upload is not None:
            self.uploadView            = GenericTaskView(subject.upload, self, "Upload results")



class GenericTaskView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="list-group-item" style="padding: 0.1rem 2.25rem;">
            <div class="row align-items-center">
                <div class="col-md-1" style="text-align:center;background-color:
                {% if pyview.subject.status == "idle" %}#fff{% endif %}
                {% if pyview.subject.status == "active" %}#ffff0066{% endif %}
                {% if pyview.subject.status == "success" %}#00ff0066{% endif %}
                {% if pyview.subject.status == "failed" %}#ff000066{% endif %}
                ">{{pyview.subject.status}}</div>
                <div class="col-md-2">{{pyview.name}}</div>
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

