from pyhtmlgui import PyHtmlView


class LockSettingsView(PyHtmlView):
    DOM_ELEMENT_CLASS = "LockSettings"
    TEMPLATE_STR = '''
    <div class="row justify-content-center" style="width: 100%">
        <div class="col-md-12">
            <div class="list-group mb-5 shadow">
                <div class="list-group-item">
                    <div class="row align-items-center">
                        <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Lock Settings</div>
                    </div>
                </div>

                <div class="list-group-item">
                    {% if pyview.subject.locked == True%}
                        <div class="row align-items-center">
                            <div class="col-md-10">
                                <strong class="mb-0">Unlock</strong>
                                <p class="text-muted mb-0">System settings are password protected, enter password to unlock </p>
                            </div>
                            <div class="col-md-1">
                                <div class="custom-control custom-switch">
                                     <input  class="form-control" id="password" placeholder="password" type="text"/>
                                </div>
                            </div>
                            <div class="col-md-1">
                                <div class="custom-control custom-switch">
                                     <button class="btn btnfw btn-success" onclick='pyview.subject.unlock($("#password").val())'>Unlock</button>
                                </div>
                            </div>
                        </div>
                    {% else %}
                        <div class="row align-items-center">
                            <div class="col-md-10">
                                <strong class="mb-0">Lock</strong>
                                <p class="text-muted mb-0">System settings can be password protected, enter password to prevent unauthorized changes </p>
                            </div>
                            <div class="col-md-1">
                                <div class="custom-control custom-switch">
                                     <input  class="form-control" id="password" placeholder="password" type="text"/>
                                </div>
                            </div>
                            <div class="col-md-1">
                                <div class="custom-control custom-switch">
                                     <button class="btn btnfw btn-success" onclick='pyview.subject.lock($("#password").val())'>Lock</button>
                                </div>
                            </div>
                        </div>      
                    {% endif %}
                </div>

            </div>
        </div>
    </div>
    '''

    def __init__(self, subject, parent):
        super().__init__(subject, parent)
