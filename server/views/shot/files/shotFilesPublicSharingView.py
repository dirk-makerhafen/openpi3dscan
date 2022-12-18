import os
import time

from pyhtmlgui import PyHtmlView, ObservableListView, ObservableList

from views.shot.shotDropboxUploadView import DropboxUploadView


class DropboxSharingItemView(PyHtmlView):
    DOM_ELEMENT = "div"
    DOM_ELEMENT_CLASS = "row"
    TEMPLATE_STR = '''
        <div class="col-md-3"> </div>
        <div class="col-md-3" style="margin-top: 10px;text-align:center"> {{pyview.subject.name}} </div>
        <div class="col-md-4" style="margin-top: 10px;text-align:center"> <a href="#">{{pyview.subject.url}}</a> </div>
        <div class="col-md-1" style="margin-top: 10px;text-align:center"> 
            {% if pyview.subject.status == "uploading" %}
                Uploading,&nbsp;{{ pyview.subject.progress }}%
            {% else %}
                {{pyview.subject.status}} 
            {% endif %}
        </div>
        <div class="col-md-1"> 
            {% if pyview.subject.status != "uploading" and pyview.subject.status != "deleting" %}
                <button class="btn btnfw" onclick="pyview.subject.delete()">Remove</button>     
            {% endif %}    
        </div>
    '''


class DropboxPublicFolderView(PyHtmlView):
    TEMPLATE_STR = '''
            {% if pyview.subject.status != "new" %}
                <div class="row" style="border-top:1px solid gray;margin-top:20px;padding-bottom:10px;padding-top: 10px;">
                    <div class="col-md-3 h5" style="font-weight: bold;">Dropbox Public Folder</div>
                    {% if pyview.subject.status == "creating" %}
                         <div class="col-md-9" style="margin-top:10px;text-align:center"> creating folder and link.. </div>
                    {% else %}
                        <div class="col-md-3" style="margin-top:10px"> {{ pyview.subject.name }} </div>
                        <div class="col-md-4" style="margin-top:10px"> <a href="{{ pyview.subject.url }}">{{ pyview.subject.url}}</a> </div>
                        <div class="col-md-1" style="margin-top:10px"> Expire in:{{ pyview.subject.expire_in }} </div>
                        <div class="col-md-1" style="margin-top:0px"><button class=" btn btnfw" onclick='pyview.subject.delete()'>Delete</button> </div> 
                    {% endif  %}

                </div> 
            {% else %}
                <div class="row" style="border-top:1px solid gray;margin-top:20px;padding-top: 10px;">
                    <div class="col-md-4 h5" style="font-weight: bold;">Dropbox Public Folder</div>
                    <div class="col-md-3" style="font-weight:bold;text-align:center">Folder Name</div>
                    <div class="col-md-2" style="font-weight:bold;text-align:center">Expire in</div>
                    <div class="col-md-1" style="font-weight:bold;text-align:center">Compress </div>
                    <div class="col-md-2" style="font-weight:bold;text-align:center">Action</div> 
                </div>  
                <div class="row"> 
                  <div class="col-md-4"></div>
                  <div class="col-md-3" style="text-align:center">
                    <input id="link_name" value="{{ pyview.subject.parent_shot.name }} " style="width:100%" class="form-control" type="text" />
                  </div>
                  <div class="col-md-2" style="text-align:center">
                    <select style="text-align:center" class="form-control" name="expire_in" id="expire_in">
                        <option value="1">1 Week</option>
                        <option value="2">2 Weeks</option>
                        <option value="3">3 Weeks</option>
                        <option value="4">1 Month</option>
                        <option value="12">3 Month</option>
                        <option value="24">6 Month</option>
                    </select>
                  </div>
                  <div class="col-md-1" style="text-align:center">
                    <input type="checkbox" style="margin-top:5px" id="compress_link" name="compress" checked> 
                  </div>
                  <div class="col-md-2" style="text-align:center"> 
                    <button class=" btn btn-success btnfw" style="" onclick='pyview.subject.create_link($("#link_name").val(), $("#expire_in").val(), $("#compress_link")[0].checked);' > Create Folder </button>
                  </div>
                </div>  


            {% endif %}
                <div class="row" style="border-top:1px solid gray;margin-top:10px;padding-bottom:10px;padding-top: 10px;">
                    <div class="col-md-3 h5" style="font-weight: bold;">Public Files</div>
                    <div class="col-md-3 h5" style="font-weight: bold;text-align:center">  Name</div>
                    <div class="col-md-4 h5" style="font-weight: bold;text-align:center"> Link</div>
                    <div class="col-md-1 h5" style="font-weight: bold;text-align:center"> Status </div>
                    <div class="col-md-1 h5" style="font-weight: bold;text-align:center"> Action </div>
                </div>    
                {{pyview.uploadsView.render()}}    


    '''

    def __init__(self, subject, parent, **kwargs):
        super().__init__(subject, parent, **kwargs)
        self.uploadsView = ObservableListView(self.subject.uploads, self, item_class=DropboxSharingItemView)

