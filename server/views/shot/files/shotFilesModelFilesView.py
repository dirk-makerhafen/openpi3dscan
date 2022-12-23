import os
from pyhtmlgui import PyHtmlView, ObservableListView, ObservableList



class ShotFilesModelFilesView(PyHtmlView):
    TEMPLATE_STR = '''
    
    <div class="ModelFiles">
        <div class="row justify-content-center" style="width:100%">
            <div class="col-md-12">
                <div class="list-group mb-5 shadow">
                    <div class="list-group-item">
                        <div class="row align-items-center" style="border-bottom: 1px solid lightgray;">
                            <div class="col-md-8 h3" >
                                Model Files
                            </div>
                            {% if pyview.settingsInstance.realityCaptureSettings.settingsDefaultModelSets.default_models | length != 0 %}
                                <div class="col-md-2"">
                                    <select style="margin-top:10px" class="form-control" name="set_name" id="set_name">
                                        {% for set_name in pyview.settingsInstance.realityCaptureSettings.settingsDefaultModelSets.get_set_names() %}
                                            <option value="{{set_name}}">{{set_name}}</option>
                                        {% endfor %}
                                    </select>
                                </div>
                                <div class="col-md-2">
                                    <button class="btn btn-success btnfw" style="margin-right:5px;margin-top:10px" onclick='pyview.parent.subject.create_models_from_set($("#set_name").val());'> Create Models </button>
                                </div>
                            {% endif %}    
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-1 h5" style="text-align:center;font-weight:bold">Type</div>
                            <div class="col-md-1 h5" style="text-align:center;font-weight:bold;width:11.1%">Reconstruction Quality</div>
                            <div class="col-md-1 h5" style="text-align:center;font-weight:bold;width:11.1%">Export Quality</div>
                            <div class="col-md-1 h5" style="text-align:center;font-weight:bold;width:11.1%">Mesh from</div>
                            <div class="col-md-1 h5" style="text-align:center;font-weight:bold">Textures</div>
                            <div class="col-md-1 h5" style="text-align:center;font-weight:bold">Lit</div>
                            <div class="col-md-3 h5" style="text-align:center;font-weight:bold">File</div>
                            <div class="col-md-2 h5" style="text-align:center;font-weight:bold">Action</div>
                        </div>
                        {{pyview.filesListView.render()}}     
                        <div class="row" style="margin-top:10px">    
                            <div class="col-md-1" style="text-align:center">
                                <select style="" class="form-control" name="filetype" id="filetype" onchange='var v=$("#filetype").val();if(v=="glb"||v=="gif"||v=="webp"){ $("#lit_unlit").prop("disabled", false); }else{ $("#lit_unlit").prop("disabled", true);$("#lit_unlit")[0].checked = true; }'>
                                    <option value="obj">OBJ</option>
                                    <option value="stl">STL</option>
                                    <option value="3mf">3MF</option>
                                    <option value="glb">GLB</option>
                                    <option value="fbx">FBX</option>
                                    <option value="rcproj">RCPROJ</option>
                                    <option value="gif">GIF</option>
                                    <option value="webp">WebP</option>
                                </select>
                            </div>
                            <div class="col-md-1" style="text-align:center;width:11.1%">
                                <select style="" class="form-control" name="reconstruction_quality" id="reconstruction_quality">
                                    <option value="high"   {% if pyview.settingsInstance.realityCaptureSettings.default_reconstruction_quality == "high"    %}selected{% endif %} >High</option>
                                    <option value="normal" {% if pyview.settingsInstance.realityCaptureSettings.default_reconstruction_quality == "normal"  %}selected{% endif %}>Normal</option>
                                    <option value="preview"{% if pyview.settingsInstance.realityCaptureSettings.default_reconstruction_quality == "preview" %}selected{% endif %} >Preview</option>
                                </select>   
                            </div>
                            <div class="col-md-1" style="text-align:center;width:11.1%">
                                <select style="" class="form-control" name="quality" id="quality">
                                    <option value="high"  {% if pyview.settingsInstance.realityCaptureSettings.default_export_quality == "high"   %}selected{% endif %}>High (4M)</option>
                                    <option value="normal"{% if pyview.settingsInstance.realityCaptureSettings.default_export_quality == "normal" %}selected{% endif %}>Normal (1M)</option>
                                    <option value="low"   {% if pyview.settingsInstance.realityCaptureSettings.default_export_quality == "low"    %}selected{% endif %}>Low (500K)</option>
                                </select>  
                            </div>
                            <div class="col-md-1" style="text-align:center;width:11.1%">
                                <select style="" class="form-control" name="create_mesh_from" id="create_mesh_from">
                                    <option value="projection" {% if pyview.settingsInstance.realityCaptureSettings.default_create_mesh_from == "projection" %}selected{% endif %}>Projection</option>
                                    <option value="normal"     {% if pyview.settingsInstance.realityCaptureSettings.default_create_mesh_from == "normal"     %}selected{% endif %}>Normal</option>
                                    <option value="all"        {% if pyview.settingsInstance.realityCaptureSettings.default_create_mesh_from == "all"        %}selected{% endif %}>All Images</option>
                                </select>   
                            </div>
                            <div class="col-md-1" style="text-align:center">
                                <input id="create_textures" {% if pyview.settingsInstance.realityCaptureSettings.default_create_textures == true %}checked{% endif %} type="checkbox"/>
                            </div>
                            <div class="col-md-1" style="text-align:center">
                                <input id="lit_unlit" {% if pyview.settingsInstance.realityCaptureSettings.default_lit == true %}checked{% endif %} type="checkbox"/>
                            </div>
                            <div class="col-md-3" style="text-align:center"></div>
                            <div class="col-md-2" style="text-align:center">
                                <button class="btn btn-success btnfw" style="margin-right:5px" onclick='pyview.parent.subject.create_model($("#filetype").val(), $("#reconstruction_quality").val(), $("#quality").val(), $("#create_mesh_from").val(), $("#create_textures")[0].checked, $("#lit_unlit")[0].checked);'> Create Model </button>
                            </div>
                        </div>
                    </div>
                                      
                </div>
            </div>   
        </div>
    </div>
    
        

    
    '''

    def __init__(self, subject, parent, settingsInstance, **kwargs):
        super().__init__(subject, parent, **kwargs)
        self.settingsInstance = settingsInstance
        self.filesListView = ObservableListView(self.subject, self, item_class=ModelFileItemView)


class ModelPublishingView(PyHtmlView):
    DOM_ELEMENT = "dummy"
    TEMPLATE_STR = '''
        {% if pyview.subject.value == "state_changing" %}
            <div class="col-md-2" style="text-align:center;margin-top:1px">processing</div>
        {% else %}
            <div class="col-md-1" style="text-align:center">
                {% if pyview.subject.value == "can_unpublish" %}
                     <button class="btn btnfw" onclick='pyview.unpublish_model()' > Unpublish</button>
                {% elif pyview.subject.value == "can_publish" %}
                    <button class="btn btnfw" onclick='pyview.publish_model()' > Publish</button> 
                {% elif pyview.subject.value == "no_publish" %}

                {% endif %}
            </div>
            <div class="col-md-1" style="text-align:center">
                <button class="btn btnfw " onclick='pyview.parent.subject.delete()'> Delete</button>
            </div>
        {% endif %} 
    '''
    def publish_model(self):
        self.parent.subject.parentShot.dropboxPublicFolder.add_model(self.parent.subject)
    def unpublish_model(self):
        self.parent.subject.parentShot.dropboxPublicFolder.remove_model(self.parent.subject)

class ModelFileItemView(PyHtmlView):
    DOM_ELEMENT = "div"
    DOM_ELEMENT_CLASS = 'row'
    DOM_ELEMENT_EXTRAS = 'style="line-height: 3em;"'
    TEMPLATE_STR = '''
        <div class="col-md-1" style="text-align:center;margin-top:1px"> {{pyview.subject.filetype}}  </div>
        <div class="col-md-1" style="text-align:center;width:11.1%;margin-top:1px"> {{pyview.subject.reconstruction_quality}} </div>
        <div class="col-md-1" style="text-align:center;width:11.1%;margin-top:1px"> {{pyview.subject.quality}} </div>
        <div class="col-md-1" style="text-align:center;width:11.1%;margin-top:1px"> {{pyview.subject.create_mesh_from}} </div>
        <div class="col-md-1" style="text-align:center;margin-top:1px"> {{pyview.subject.create_textures}} </div>
        <div class="col-md-1" style="text-align:center;margin-top:1px"> {{pyview.subject.lit}} </div>
        <div class="col-md-3" style="text-align:center;margin-top:1px">
            {% if pyview.subject.status == "ready" %} 
                 {% if pyview.parent.parent.parent.parent.show_path == True %}
                    <a style="white-space: nowrap;" href="#" onclick="pyview.open_in_explorer()">{{pyview.subject.filename}}</a> ({{pyview.subject.filesize}}&nbsp;MB)
                {% else %}
                    <a style="white-space: nowrap;" href="/shots/{{pyview.subject.parentShot.shot_id}}/download/{{pyview.subject.model_id}}">{{pyview.subject.filename}}</a> ({{pyview.subject.filesize}}&nbsp;MB)
                {% endif %}
            {% else %}
                {{pyview.subject.status}}
            {% endif %}    
        </div>
        {% if  pyview.parent.parent.settingsInstance.settingsDropbox.refresh_token != "" and pyview.subject.parentShot.dropboxPublicFolder.status != "new" %}
            {{ pyview.modelPulishingView.render() }}
        {% else %}
            <div class="col-md-1"></div>
            <div class="col-md-1 " style="text-align:center">
                <button class="btn btnfw" onclick='pyview.subject.delete()'> Delete</button>
            </div>
        {% endif %}
    '''

    def __init__(self, subject, parent, **kwargs):
        super().__init__(subject, parent, **kwargs)
        self.modelPublishingView = ModelPublishingView(self.subject.publishing_status, self)

    def open_in_explorer(self):
        p = self.subject.get_path()
        if os.path.isdir(p) is False:
            p = self.subject.path
        os.startfile(p)

