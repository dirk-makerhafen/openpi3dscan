import math
import os
import time
import webbrowser

from pyhtmlgui import PyHtmlView, ObservableListView, ObservableList

from views.shot.shotDropboxUploadView import DropboxUploadView


class DropboxSharingItemView(PyHtmlView):
    DOM_ELEMENT = "div"
    DOM_ELEMENT_CLASS = "row"
    DOM_ELEMENT_EXTRAS = 'style="line-height: 3em;"'
    TEMPLATE_STR = '''
        <div class="col-md-2"> </div>
        <div class="col-md-3" style="margin-top: 1px;text-align:center"> {{pyview.subject.name}} </div>
        <div class="col-md-5 mytooltip" style="margin-top: 1px;text-align:center;text-overflow: ellipsis;overflow: hidden;white-space: nowrap;"> 
            <span class="tooltiptext">copied to clipboard</span>
            <a id="url_{{pyview.uid}}" href="{{ pyview.subject.url}}" ondblclick='{% if pyview.parent.parent.parent.parent.show_path == True %} pyview.open_in_browser() {% else %} window.open("{{ pyview.subject.url}}", "_blank").focus(); {% endif %}' onclick='copy_to_clipboard(event, document.getElementById("url_{{pyview.uid}}"))'>
               {{pyview.subject.url}}                                  
            </a> 
        </div>
        <div class="col-md-1" style="margin-top: 1px;text-align:center"> 
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
    def open_in_browser(self):
        webbrowser.open(self.subject.url)


class DropboxPublicFolderView(PyHtmlView):
    TEMPLATE_STR = '''
        <script>
            function copy_to_clipboard(e, element) {
                e = e || window.event;
                e.preventDefault();
                navigator.clipboard.writeText(element.href);
                element.parentElement.classList.add("tooltip_visible");
                setTimeout(function(){
                  element.parentElement.classList.remove("tooltip_visible");
                }, 1500);
            }
        </script>
        <div class="DropboxPublicFolder">
            <div class="row justify-content-center" style="width:100%">
                <div class="col-md-12">
                    <div class="list-group mb-5 shadow">
                        <div class="list-group-item">
                            <div class="row align-items-center"  style="border-bottom: 1px solid lightgray;">
                                <div class="col-md-12 h3">Dropbox Public Folder</div>
                            </div>
                        </div>
                        <div class="list-group-item">
                            {% if pyview.subject.status == "new" %}
                                <div class="row align-items-center">
                                    <div class="row" style="">
                                        <div class="col-md-5 h5"></div>
                                        <div class="col-md-3" style="font-weight:bold;text-align:center">Folder Name</div>
                                        <div class="col-md-2" style="font-weight:bold;text-align:center">Expire in</div>
                                        <!----<div class="col-md-1" style="font-weight:bold;text-align:center">Compress </div>---!>
                                        <div class="col-md-2" style="font-weight:bold;text-align:center">Action</div> 
                                    </div>  
                                    <div class="row"> 
                                      <div class="col-md-5"></div>
                                      <div class="col-md-3" style="text-align:center">
                                        <input id="link_name" value="{{ pyview.subject.parent_shot.name }}" style="width:100%" class="form-control" type="text" />
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
                                      <!--- <div class="col-md-1" style="text-align:center">
                                        <input type="checkbox" style="margin-top:5px" id="compress_link" name="compress" checked> 
                                      </div>---!>
                                      <div class="col-md-2" style="text-align:center"> 
                                        <button class=" btn btn-success btnfw" style="" onclick='pyview.subject.create_link($("#link_name").val(), $("#expire_in").val(), true);' > Create Folder </button>
                                      </div>
                                    </div>  
                                </div>
                             {% else %}
                               <div class="row" style="line-height:3em">
                                    <div class="col-md-2 h5" style="font-weight: bold;"></div>
                                    {% if pyview.subject.status == "creating" %}
                                         <div class="col-md-10" style="margin-top:1px;text-align:center"> Creating folder and link.. </div>
                                    {% elif pyview.subject.status == "deleting" %}
                                        <div class="col-md-10" style="margin-top:1px;text-align:center"> Deleting folder.. </div>
                                    {% else %}
                                        <div class="col-md-3" style="margin-top:1px;text-align:center"> {{ pyview.subject.name }}</div>
                                        <div class="col-md-4 mytooltip" style="margin-top:1px;text-align:center;text-overflow: ellipsis;overflow: hidden;white-space: nowrap;"> 
                                            <span class="tooltiptext">copied to clipboard</span>
                                            <a id="url_{{pyview.uid}}" href="{{ pyview.subject.url}}" ondblclick='{% if pyview.parent.parent.show_path == True %} pyview.open_in_browser() {% else %} window.open("{{ pyview.subject.url}}", "_blank").focus(); {% endif %}' onclick='copy_to_clipboard(event, document.getElementById("url_{{pyview.uid}}"))'>
                                                {{ pyview.subject.url}}                                        
                                            </a> 
                                        </div>
                                        <div class="col-md-2" style="margin-top:1px;text-align:center"> Expire in: {{ pyview._get_expire_time() }} </div>
                                        <div class="col-md-1" style="margin-top:0px">
                                        <button class=" btn btnfw" {% if pyview.subject.can_delete == False %}disabled{% endif %} onclick='pyview.subject.delete()'>Delete</button> </div> 
                                    {% endif  %}
                                </div> 
                                

                            
                            {% endif %}
                        </div>              
                    </div>
                </div>   
            </div>
        </div>
    
    {% if pyview.subject.status != "new" %}
        <div class="DropboxPublicFolderItems">
            <div class="row justify-content-center" style="width:100%">
                <div class="col-md-12">
                    <div class="list-group mb-5 shadow">
                        <div class="list-group-item">
                            <div class="row align-items-center" style="border-bottom: 1px solid lightgray;">
                                <div class="col-md-12 h3" style="">Public Files</div>
                            </div>
                        </div>
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="row" style="">
                                    <div class="col-md-2 h5" style="font-weight: bold;"> </div>
                                    <div class="col-md-3 h5" style="font-weight: bold;text-align:center"> Name</div>
                                    <div class="col-md-5 h5" style="font-weight: bold;text-align:center"> Link</div>
                                    <div class="col-md-1 h5" style="font-weight: bold;text-align:center"> Status </div>
                                    <div class="col-md-1 h5" style="font-weight: bold;text-align:center"> Action </div>
                                </div>    
                                {{pyview.uploadsView.render()}}    
                            </div>
                        </div>
                                          
                    </div>
                </div>   
            </div>
        </div>
    {% endif %}

    '''

    def __init__(self, subject, parent, **kwargs):
        super().__init__(subject, parent, **kwargs)
        self.uploadsView = ObservableListView(self.subject.uploads, self, item_class=DropboxSharingItemView)

    def open_in_browser(self):
        webbrowser.open(self.subject.url)

    def _get_expire_time(self):
        seconds = self.subject.expire_time - time.time()
        minutes = int(math.ceil(seconds / 60 ))
        if minutes < 10:
            return "a few minutes"
        hours = int(math.ceil(seconds / 60 / 60 ))
        if hours < 2:
            return "%s minutes" % minutes
        days = int(math.ceil(seconds / 60 / 60 / 24 ))
        if days < 2:
            return "%s hours" % hours
        weeks = int(math.ceil(seconds / 60 / 60 / 24 / 7))
        if weeks < 5:
            return "%s days" % days
        month = int(math.ceil(seconds / 60 / 60 / 24 / 30.416))
        if month < 5:
            return "%s weeks" % weeks
        return "%s month" % month
