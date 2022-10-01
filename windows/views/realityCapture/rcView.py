from pyhtmlgui import PyHtmlView
from .rc_alignmentsView import RC_AlignmentsView
from .rc_exportView import RC_ExportView
from .rc_markersView import RC_MarkersView
from .rc_reconstructionView import RC_ReconstructionView
from .data_calibrationView import CalibrationDataView

class RCView(PyHtmlView):
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
                
                    {{ pyview.rc_markersView.render()        }}
                    {{ pyview.calibrationdataView.render()   }}
                    {{ pyview.rc_alignmentsView.render()     }}
                    {{ pyview.rc_reconstructionView.render() }}
                    {{ pyview.rc_exportView.render()         }}
                
                </div>
            </div>   
        </div>
    </div>    
    '''

    def __init__(self, subject, parent, **kwargs):
        super().__init__(subject, parent, **kwargs)
        self.rc_markersView = RC_MarkersView(subject.rc_markers, self)
        self.calibrationdataView = CalibrationDataView(subject.calibrationdata, self)
        self.rc_alignmentsView = RC_AlignmentsView(subject.rc_alignments, self)
        self.rc_reconstructionView = RC_ReconstructionView(subject.rc_reconstruction, self)
        self.rc_exportView = RC_ExportView(subject.rc_export, self)
