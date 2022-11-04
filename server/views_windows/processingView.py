from pyhtmlgui import PyHtmlView, ObservableListView

from views_windows.realityCapture.realityCaptureView import RealityCaptureView


class ProcessingView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="main">
        <div class="RealityCapture">
            <div class="row justify-content-center" style="width:100%">
                <div class="col-md-12">
                    <div class="list-group mb-5 shadow">
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-10 h3" style="border-bottom: 1px solid lightgray;">RealityCapture Processing</div>
                                <div class="col-md-2 h3" style="border-bottom: 1px solid lightgray;">{{pyview.subject.status}}</div>
                            </div>
                        </div>
                    </div>
                </div>   
            </div>
            {{ pyview.tasks.render() }}   
        </div>
    </div>
    
    '''

    def __init__(self, subject, parent):
        super().__init__(subject, parent)
        self.tasks = ObservableListView(subject.rc_tasks, self, RealityCaptureView)
