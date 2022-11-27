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
                                <div class="col-md-4 h3" >RealityCapture Automation Tasks</div>
                                {% if pyview.subject.status == "failed" %}
                                    <div class="col-md-6 h4" >Task failed, make sure you have enough credits available</div>
                                    <div class="col-md-2" >
                                        <button class="btn btn-success" onclick="pyview.subject.set_status('repeat')">Repeat Task</button><br>
                                        <button class="btn btn-warning" onclick="pyview.subject.set_status('continue')" style="margin-top:3px;">Fail task and Continue</button>
                                    </div> 
                                {% else %}
                                    <div class="col-md-6" >&nbsp;</div>
                                    <div class="col-md-2 h3" >{{pyview.subject.status}}</div>
                                {% endif %}
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
