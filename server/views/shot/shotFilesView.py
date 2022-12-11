import os
import time

from pyhtmlgui import PyHtmlView, ObservableListView, ObservableList

from views.shot.shotDropboxUploadView import DropboxUploadView


class DropboxSharingView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="row">
            <div class="col-md-12" style="border-top:1px solid gray;font-weight:bold;;padding-top:10px;padding-bottom:10px;">Sharing</div>
                {% if pyview.dropboxSharingView is None % }
                    <div class="col-md-12">
                        <table style="width:100%;text-align:center">
                            <thead>
                                <tr>
                                    <th style="text-align:center">Type</th>
                                    <th style="text-align:center">Name</th>
                                    <th style="text-align:center">Expire in Weeks</th>
                                    <th style="text-align:center">Compress</th>
                                    <th style="text-align:center">Action</th>
                                </tr>
                            </thead>
                            <tr style="border-top: 1px solid lightgray;    line-height: 3em;">
                                <td style="padding-left: 5px;padding-right: 5px;">
                                    <select style="" class="form-control" name="filetype" id="link_type">
                                        <option value="single">This shot</option>
                                        <option value="group">Group of shots</option>         
                                    </select>
                                </td>
                                <td> <input id="name" value="remote folder name" />  </td>
                                <td> <input id="exire_in_weeks" value="23"/>  </td>
                                <td> <input id="compress" {% if pyview.settingsInstance.realityCaptureSettings.default_lit == true %}checked{% endif %} type="checkbox"/>  </td>
                                <td> <button class="form-control btn btn-success" style="margin-right:5px" onclick='pyview.parent.create_model($("#filetype").val(), $("#reconstruction_quality").val(), $("#quality").val(), $("#create_mesh_from").val(), $("#create_textures")[0].checked, $("#lit_unlit")[0].checked);'> Create Link </button></td>
                            </tr>
                        </table>
                    </div>
                {% else %}
                    <div class="col-md-6">url</div>
                    <div class="col-md-3">expire in</div>
                    <div class="col-md-3">delete</div>
                    <div class="col-md-12">
                        
                    </div>
                {% endif %}
            
        </div>






'''

class ShotFilesView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="row" style="margin-bottom: 10px;">
        <div class="col-md-11" style="font-weight:bold;padding-bottom:10px;">Images</div>
        <div class="col-md-1" style="font-weight:bold;cursor: pointer" onclick='pyview.hide()'>
            <a style="text-align: right;float: right;color: gray;"> Close </a>
        </div>
        <div class="col-md-7" style="padding-left:20px">
            <p class="h5"><a href="/shots/{{pyview.parent.current_shot.shot_id}}.zip"><i class="fa fa-download" aria-hidden="true"></i> {{pyview.parent.current_shot.get_clean_shotname()}}.zip </a> </p>
            {% if pyview.parent.show_path == True %}
                <p class="h5"><a href="#" onclick="pyview.open_images_in_explorer()">{{pyview.current_shot.images_path}}</a></p>
            {% endif %}
        </div>
        {% if pyview.settingsInstance.settingsDropbox.refresh_token != "" and pyview.dropboxUploadView != None %}
            {{ pyview.dropboxUploadView.render() }}
        {% endif %}
    </div>
    {% if pyview.settingsInstance.realityCaptureSettings.allow_rc_automation == True %}
        <div class="row">
            <div class="col-md-8" style="border-top:1px solid gray;font-weight:bold;;padding-top:10px;padding-bottom:10px;">Model Files</div>
            {% if pyview.settingsInstance.realityCaptureSettings.settingsDefaultModelSets.default_models | length != 0 %}
                <div class="col-md-2" style="border-top:1px solid gray;font-weight:bold;;padding-top:10px;padding-bottom:10px;">
                    <select style="" class="form-control" name="set_name" id="set_name">
                        {% for set_name in pyview.settingsInstance.realityCaptureSettings.settingsDefaultModelSets.get_set_names() %}
                            <option value="{{set_name}}">{{set_name}}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-2" style="border-top:1px solid gray;font-weight:bold;;padding-top:10px;padding-bottom:10px;">
                    <button class="form-control btn btn-success" style="margin-right:5px" onclick='pyview.parent.create_models_from_set($("#set_name").val());'> Create Models </button>
                </div>
            {% endif %}
            <div class="col-md-12">
                <table style="width:100%;text-align:center">
                    <thead>
                        <tr>
                        <th style="text-align:center">Type</th>
                        <th style="text-align:center">Reconstruction Quality</th>
                        <th style="text-align:center">Export Quality</th>
                        <th style="text-align:center">Mesh from</th>
                        <th style="text-align:center">Textures</th>
                        <th style="text-align:center">Lit</th>
                        <th style="text-align:center">File</th>
                        <th style="text-align:center">Action</th>
                        </tr>
                    </thead>
                    {{pyview.filesListView.render()}}
                    <tr style="border-top: 1px solid lightgray;    line-height: 3em;">
                        <td style="padding-left: 5px;padding-right: 5px;">
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
                        </td>
                        <td style="padding-left: 5px;padding-right: 5px;">
                            <select style="" class="form-control" name="reconstruction_quality" id="reconstruction_quality">
                                <option value="high"   {% if pyview.settingsInstance.realityCaptureSettings.default_reconstruction_quality == "high"    %}selected{% endif %} >High</option>
                                <option value="normal" {% if pyview.settingsInstance.realityCaptureSettings.default_reconstruction_quality == "normal"  %}selected{% endif %}>Normal</option>
                                <option value="preview"{% if pyview.settingsInstance.realityCaptureSettings.default_reconstruction_quality == "preview" %}selected{% endif %} >Preview</option>
                            </select>                            
                        </td>
                        <td style="padding-left: 5px;padding-right: 5px;">
                            <select style="" class="form-control" name="quality" id="quality">
                                <option value="high"  {% if pyview.settingsInstance.realityCaptureSettings.default_export_quality == "high"   %}selected{% endif %}>High (4M)</option>
                                <option value="normal"{% if pyview.settingsInstance.realityCaptureSettings.default_export_quality == "normal" %}selected{% endif %}>Normal (1M)</option>
                                <option value="low"   {% if pyview.settingsInstance.realityCaptureSettings.default_export_quality == "low"    %}selected{% endif %}>Low (500K)</option>
                            </select>                            
                        </td>
                        <td style="padding-left: 5px;padding-right: 5px;">
                            <select style="" class="form-control" name="create_mesh_from" id="create_mesh_from">
                                <option value="projection" {% if pyview.settingsInstance.realityCaptureSettings.default_create_mesh_from == "projection" %}selected{% endif %}>Projection</option>
                                <option value="normal"     {% if pyview.settingsInstance.realityCaptureSettings.default_create_mesh_from == "normal"     %}selected{% endif %}>Normal</option>
                                <option value="all"        {% if pyview.settingsInstance.realityCaptureSettings.default_create_mesh_from == "all"        %}selected{% endif %}>All Images</option>
                            </select>   
                        </td>
                        <td> <input id="create_textures" {% if pyview.settingsInstance.realityCaptureSettings.default_create_textures == true %}checked{% endif %} type="checkbox"/> </td>
                        <td> <input id="lit_unlit" {% if pyview.settingsInstance.realityCaptureSettings.default_lit == true %}checked{% endif %} type="checkbox"/>  </td>
                        <td> &nbsp;  </td>
                        <td> <button class="form-control btn btn-success" style="margin-right:5px" onclick='pyview.parent.create_model($("#filetype").val(), $("#reconstruction_quality").val(), $("#quality").val(), $("#create_mesh_from").val(), $("#create_textures")[0].checked, $("#lit_unlit")[0].checked);'> Create Model </button></td>
                    </tr>
                </table>
            </div>
        </div>
    {% endif %}
    <script>
        {% if pyview.is_hidden %}
            $('#files_btn').removeClass('selected');
        {% else %}
            $('#files_btn').addClass('selected');
        {% endif %}
    </script>
    '''

    @property
    def DOM_ELEMENT_EXTRAS(self):
        return 'style="display:none;"' if self.is_hidden is True else ""

    def __init__(self, subject, parent, settingsInstance, **kwargs):
        super().__init__(subject, parent, **kwargs)
        self.settingsInstance = settingsInstance
        self.is_hidden = True
        self.current_models_list = ObservableList()
        self.current_shot = None
        self.filesListView = ObservableListView(self.current_models_list, self, item_class=ModelFileItemView, dom_element="tbody")
        self.dropboxUploadView = None
        self.dropboxSharingView = None

    def show(self):
        if self.is_hidden is True and self.is_visible:
            self.is_hidden = False
            self.update()

    def hide(self):
        if self.is_hidden is False and self.is_visible:
            self.is_hidden = True
            self.update()

    def toggle(self):
        self.is_hidden = not self.is_hidden
        if self.is_visible:
            self.update()

    def render(self):
        self._update_current_shot()
        return super(ShotFilesView, self).render()

    def update(self) -> None:
        self._update_current_shot()
        return super(ShotFilesView, self).update()

    def _update_current_shot(self):
        if self.current_shot != self.parent.current_shot:
            self.current_shot = self.parent.current_shot
            if self.current_shot is not None:
                self.current_models_list = self.parent.current_shot.models

                if self.dropboxUploadView is not None:
                    self.dropboxUploadView.delete(remove_from_dom=False)
                if hasattr(self.current_shot, "dropboxUpload"):
                    self.dropboxUploadView = DropboxUploadView(self.current_shot.dropboxUpload, self)
            else:
                self.current_models_list = ObservableList()
            self.filesListView = ObservableListView(self.current_models_list, self, item_class=ModelFileItemView, dom_element="tbody")

    def open_images_in_explorer(self):
        if self.current_shot is not None:
            os.startfile( self.current_shot.images_path)


class ModelFileItemView(PyHtmlView):
    DOM_ELEMENT = "tr"
    DOM_ELEMENT_EXTRAS = 'style="line-height: 3em;"'
    TEMPLATE_STR = '''
        <td>{{pyview.subject.filetype}} </td>
        <td>{{pyview.subject.reconstruction_quality}}</td>
        <td>{{pyview.subject.quality}}</td>
        <td>{{pyview.subject.create_mesh_from}}</td>
        <td>{{pyview.subject.create_textures}}</td>
        <td>{{pyview.subject.lit}}</td>
        <td>
            {% if pyview.subject.status == "ready" %} 
                 {% if pyview.parent.parent.parent.show_path == True %}
                    <a href="#" onclick="pyview.open_in_explorer()">{{pyview.subject.filename}} </a> ({{pyview.subject.filesize}} MB)
                {% else %}
                    <a href="/shots/{{pyview.subject.parentShot.shot_id}}/download/{{pyview.subject.model_id}}">{{pyview.subject.filename}} </a> ({{pyview.subject.filesize}} MB)
                {% endif %}
            {% else %}
                {{pyview.subject.status}}
            {% endif %}
        </td>
        <td><button class="btn" onclick='pyview.subject.delete()'> Delete</button></td>
    '''

    def open_in_explorer(self):
        p = self.subject.get_path()
        if os.path.isdir(p) is False:
            p = self.subject.path
        os.startfile(p)

