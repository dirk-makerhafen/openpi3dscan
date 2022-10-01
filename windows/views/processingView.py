from pyhtmlgui import PyHtmlView

from views.realityCapture.rc_markersView import RC_MarkersView


class SettingsView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="main">
        <div class="RealityCapture">
            <div class="row justify-content-center" style="width:100%">
                <div class="col-md-12">
                    <div class="list-group mb-5 shadow">
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">RealityCapture</div>
                            </div>
                        </div>
                        
                                                     
                    </div>
                </div>   
            </div>
        </div>
    </div> 

    '''

    def __init__(self, subject, parent):
        super().__init__(subject, parent)
        self.rc_markersView = RC_MarkersView(subject.rc_markers, self)
