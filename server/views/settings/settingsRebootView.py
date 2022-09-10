from pyhtmlgui import PyHtmlView


class RebootShutdownView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="SystemRestart">
        <div class="row justify-content-center" style="width:100%">
            <div class="col-md-12">
                <div class="list-group mb-5 shadow">
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Shutdown/Reboot Server</div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-10">
                                <strong class="mb-0">Reboot</strong>
                                <p class="text-muted mb-0">Reboot server, this will take 2-3 minutes</p>
                            </div>
                            <div class="col-auto">
                                {% if pyview.subject.status == "active"%}
                                    <button class="btn " style="margin-right:5px" onclick='pyview.subject.reboot()'> Reboot </button>
                                {% else %}
                                    <p>{{pyview.subject.status}} active</p>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-10">
                                <strong class="mb-0">Shutdown</strong>
                                <p class="text-muted mb-0">Shutdown Server</p>
                            </div>
                            <div class="col-auto">
                                {% if pyview.subject.status == "active" %}
                                    <button class="btn " style="margin-right:5px" onclick='pyview.subject.shutdown();'> Shutdown </button>
                                 {% else %}
                                    <p>{{pyview.subject.status}} active</p>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                </div>
            </div>   
        </div>
    </div>    
'''

