from pyhtmlgui import PyHtmlView


class SettingsLocationsView(PyHtmlView):
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
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-10">
                                <strong class="mb-0">Location</strong>
                                <p class="text-muted mb-0">Unique scanner location name</p>
                            </div>
                            <div class="col-md-2">
                                <div class="custom-control custom-switch">
                                </div>
                            </div>
                        </div>
                    </div> 
                    {% for locations in pyview.subject.locations %}            
                        {{ location }}               
                    {% endfor %}                               
                </div>
            </div>   
        </div>
    </div>    
'''

