from pyhtmlgui import PyHtmlView, ObservableListView


#from views.realityCapture.rc_markersView import RC_MarkersView


class StepView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="list-group-item">
        <div class="row align-items-center">
            <div class="col-md-10">
                <strong class="mb-0"> STEP NAME </strong>
                <p class="text-muted mb-0"><input type="textfield"></input></p>
                <p class="text-muted mb-0">log</p>
            </div>
            <div class="col-md-2">
                <div class="custom-control custom-switch">
                <button onclick="">Run</button>
                </div>
            </div>
        </div>
    </div> 
    '''
class ProcessingTaskView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="main">
    <div class="SystemRestart">
        <div class="row justify-content-center" style="width:100%">
        <div class="col-md-12">
            <div class="list-group mb-5 shadow">
                <div class="list-group-item">
                    <div class="row align-items-center">
                        <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Reality Capture Job</div>
                    </div>
                </div>
                
        
            </div>
        </div>   
        
            <div class="list-group-item">
        <div class="row align-items-center">
            <div class="col-md-10">
                <strong class="mb-0"> Status</strong>
                <p class="text-muted mb-0">log</p>
            </div>
            <div class="col-md-2">
                <div class="custom-control custom-switch">Downloading
                </div>
            </div>
        </div>
    </div> 
        
        </div>
    
            <div class="row justify-content-center" style="width:100%">
                <div class="col-md-12">
                    <div class="list-group mb-5 shadow">
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Job steps</div>
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
        self.steps =  ObservableListView(subject.steps, self,StepView)
        #self.rc_markersView = RC_MarkersView(subject.rc_markers, self)

class ProcessingView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="main">
    <div class="SystemRestart">
            <div class="row justify-content-center" style="width:100%">
                <div class="col-md-12">
                    <div class="list-group mb-5 shadow">
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Reality Capture Job</div>
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
