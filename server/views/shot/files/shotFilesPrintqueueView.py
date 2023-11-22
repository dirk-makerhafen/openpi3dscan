import math
import os
import time
import webbrowser

from pyhtmlgui import PyHtmlView, ObservableListView, ObservableList

from views.shot.shotDropboxUploadView import DropboxUploadView



class ShotFilesPrintqueueItemView(PyHtmlView):
    DOM_ELEMENT = "div"
    DOM_ELEMENT_CLASS = 'row'
    DOM_ELEMENT_EXTRAS = 'style="line-height: 3em;"'
    TEMPLATE_STR = '''

        
    '''

    def __init__(self, subject, parent, **kwargs):
        super().__init__(subject, parent, **kwargs)


class ShotFilesPrintqueueView(PyHtmlView):
    TEMPLATE_STR = '''
    
    <div class="ShotFilesPrintqueueView">
        <div class="row justify-content-center" style="width:100%">
            <div class="col-md-12">
                <div class="list-group mb-5 shadow">
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Print Queue</div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-5 h5" style="text-align:center;font-weight:bold;">File</div>
                            <div class="col-md-1 h5" style="text-align:center;font-weight:bold;">Color</div>
                            <div class="col-md-1 h5" style="text-align:center;font-weight:bold;">Printer</div>
                            <div class="col-md-1 h5" style="text-align:center;font-weight:bold;">Created</div>
                            <div class="col-md-1 h5" style="text-align:center;font-weight:bold;">Changed</div>
                            <div class="col-md-1 h5" style="text-align:center;font-weight:bold;">Status</div>
                            <div class="col-md-2 h5" style="text-align:center;font-weight:bold">Actions</div>
                        </div>
                       {% for item in pyview.subject.printqueue %}
                            <div class="col-md-5" style="text-align:center;margin-top:1px;white-space: nowrap;"> {{item.model.filename}}  </div>
                            <div class="col-md-1" style="text-align:center;margin-top:1px"> {{item.color}} </div>
                            <div class="col-md-1" style="text-align:center;margin-top:1px"> {{item.printer}} </div>
                            <div class="col-md-1" style="text-align:center;margin-top:1px"> {{item.created}} </div>
                            <div class="col-md-1" style="text-align:center;margin-top:1px"> {{item.last_changed}} </div>                                                              
                            <div class="col-md-1" style="text-align:center;margin-top:1px"> {{item.status}} </div>                                                              
                            <div class="col-md-2" style="text-align:center;margin-top:1px">
                                {% if item.status == "waiting" %} 
                                    <button class="btn">printing</button>    
                                    <button class="btn">remove</button>    
                                {% endif %}
                                {% if item.status == "printing" %}
                                    <button class="btn">success</button>    
                                    <button class="btn">failed</button>    
                                {% endif %}
                                {% if item.status == "failed" %}
                                    <button class="btn">retry</button>    
                                    <button class="btn">remove</button>    
                                {% endif %}
                                {% if item.status == "printed" %}
                                    <button class="btn">remove</button>    
                                {% endif %}
                                
                            </div>                                                              
                       {% endfor %}
                    </div>              
                </div>
            </div>   
        </div>
    </div>
      

    '''

    def __init__(self, subject, parent, **kwargs):
        super().__init__(subject, parent, **kwargs)

