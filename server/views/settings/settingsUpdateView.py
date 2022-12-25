from pyhtmlgui import PyHtmlView
from app.tasks.task_UpdateServer import TaskUpdateServerInstance

class TaskUpdateServerView(PyHtmlView):
    TEMPLATE_STR = '''
    {% if pyview.subject.status == "idle" %} 
        <button class="btn btnfw" onclick='pyview.subject.run();'> Update Server </button>
    {% else %}
        <p style="color:green" class="h5">{{pyview.subject.status}}</p>
    {% endif %}
    '''

class SettingsUpdateView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="row justify-content-center" style="width:100%">
            <div class="col-md-12">
                <div class="list-group mb-5 shadow">
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Version</div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-10">
                                <strong class="mb-0">Version</strong>
                                <p class="text-muted mb-0">Current server version</p>
                            </div>
                            <div class="col-md-2" style="text-align:center">
                                <p class="h5">{{pyview.subject.VERSION}}</p>
                            </div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-10">
                                <strong class="mb-0">Online Updates</strong>
                                <p class="text-muted mb-0">Check for updates and install if available. Server will reboot after updates are installed.</p>
                            </div>
                            <div class="col-md-2" style="text-align:center">
                                {{pyview.updateServerView.render()}}
                            </div>
                        </div>
                    </div>
                </div>
            </div>   
        </div>
    '''

    def __init__(self, subject, parent):
        super().__init__(subject, parent)
        self.updateServerView = TaskUpdateServerView(TaskUpdateServerInstance(), self)
