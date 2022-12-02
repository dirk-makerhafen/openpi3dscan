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
                                    <div class="col-md-6 h4"  style="margin-top:16px;" >Task failed, make sure you have enough credits available</div>
                                    <div class="col-md-1" >
                                        <button class="btn btnfw" onclick="pyview.subject.set_status('continue')"  style="margin-top:14px;">Continue</button>
                                    </div> 
                                    <div class="col-md-1" >
                                        <button class="btn btnfw" onclick="pyview.subject.set_status('repeat')"  style="margin-top:14px;">Repeat</button><br>
                                    </div> 
                                {% else %}
                                    <div class="col-md-4" >  &nbsp; </div>
                                    <div class="col-md-2 h3" style="margin-top:16px;" > {{ pyview.subject.status }} </div>
                                    <div class="col-md-2 " >
                                        {% if pyview.subject.status == "processing" or pyview.subject.status == "idle" %}
                                            <button class="btn btnfw" onclick="pyview.subject.pause()"  style="margin-top:14px;">Pause</button>
                                        {% endif %}
                                        {% if pyview.subject.status == "paused" %}
                                            <button class="btn btnfw" onclick="pyview.subject.unpause()"  style="margin-top:14px;">Continue</button>
                                        {% endif %}                                    
                                    </div>
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
