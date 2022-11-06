from pyhtmlgui import PyHtmlView, ObservableListView


class SettingsCacheView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="Cache">
        <div class="row justify-content-center" style="width:100%">
            <div class="col-md-12">
                <div class="list-group mb-5 shadow">
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Cache</div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <strong class="mb-0">Directory</strong>
                                <p class="text-muted mb-0">Cache directory</p>
                            </div>
                            <div class="col-md-4">
                            
                            </div>
                        </div>
                    </div>
                     <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <strong class="mb-0">Size</strong>
                                <p class="text-muted mb-0">Cache last x tasks</p>
                            </div>
                            <div class="col-md-4">
                            
                            </div>
                        </div>
                    </div>                 
                </div>
            </div>   
        </div>
    </div>
    '''
    def __init__(self, subject, parent, **kwargs):
        super().__init__(subject, parent, **kwargs)


