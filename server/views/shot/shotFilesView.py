from pyhtmlgui import PyHtmlView, ObservableListView, ObservableList

from app.settings.settings import SettingsInstance


class ShotFilesView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="row" style="margin-bottom: 10px;">
        <div class="col-md-11" style="font-weight:bold;padding-bottom:10px;">Images</div>
        <div class="col-md-1" style="font-weight:bold;cursor: pointer" onclick='pyview.hide()'>
            <a style="text-align: right;float: right;color: gray;"> Close </a>
        </div>
        <div class="col-md-12">
            <a class="btn" href="/shots/{{pyview.parent.current_shot.shot_id}}.zip"><i class="fa fa-download" aria-hidden="true"></i> {{pyview.parent.current_shot.get_clean_shotname()}}.zip </a>
        </div>
    </div>
    <div class="row">
        <div class="col-md-12" style="border-top:1px solid gray;font-weight:bold;;padding-top:10px;padding-bottom:10px;">Model Files</div>
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
                    <td>
                        <select name="filetype" id="filetype">
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
                    <td>
                        <select name="reconstruction_quality" id="reconstruction_quality">
                            <option value="high"   {% if pyview.settings.realityCaptureSettings.default_reconstruction_quality == "high"    %}selected{% endif %} >High</option>
                            <option value="normal" {% if pyview.settings.realityCaptureSettings.default_reconstruction_quality == "normal"  %}selected{% endif %}>Normal</option>
                            <option value="preview"{% if pyview.settings.realityCaptureSettings.default_reconstruction_quality == "preview" %}selected{% endif %} >Preview</option>
                        </select>                            
                    </td>
                    <td>
                        <select name="quality" id="quality">
                            <option value="high"  {% if pyview.settings.realityCaptureSettings.default_export_quality == "high"   %}selected{% endif %}>High (4M)</option>
                            <option value="normal"{% if pyview.settings.realityCaptureSettings.default_export_quality == "normal" %}selected{% endif %}>Normal (1M)</option>
                            <option value="low"   {% if pyview.settings.realityCaptureSettings.default_export_quality == "low"    %}selected{% endif %}>Low (500K)</option>
                        </select>                            
                    </td>
                    <td>
                        <select name="create_mesh_from" id="create_mesh_from">
                            <option value="projection" {% if pyview.settings.realityCaptureSettings.default_create_mesh_from == "projection" %}selected{% endif %}>Projection</option>
                            <option value="normal"     {% if pyview.settings.realityCaptureSettings.default_create_mesh_from == "normal"     %}selected{% endif %}>Normal</option>
                            <option value="all"        {% if pyview.settings.realityCaptureSettings.default_create_mesh_from == "all"        %}selected{% endif %}>All Images</option>
                        </select>   
                    </td>
                    <td> <input id="create_textures" {% if pyview.settings.realityCaptureSettings.default_create_textures == true %}checked{% endif %} type="checkbox"/> </td>
                    <td> <input id="lit_unlit" {% if pyview.settings.realityCaptureSettings.default_lit == true %}checked{% endif %} type="checkbox"/>  </td>
                    <td> <button class="btn btn-success" style="margin-right:5px" onclick='pyview.parent.create_model($("#filetype").val(), $("#reconstruction_quality").val(), $("#quality").val(), $("#create_mesh_from").val(), $("#create_textures")[0].checked, $("#lit_unlit")[0].checked);'> Create Model </button></td>
                </tr>
            </table>
        </div>
    </div>
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

    def __init__(self, subject, parent, **kwargs):
        super().__init__(subject, parent, **kwargs)
        self.is_hidden = True
        self.current_models_list = ObservableList()
        self.current_shot = None
        self.settings = SettingsInstance()
        self.filesListView = ObservableListView(self.current_models_list, self, item_class=ModelFileItemView, dom_element="tbody")

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
            else:
                self.current_models_list = ObservableList()
            self.filesListView = ObservableListView(self.current_models_list, self, item_class=ModelFileItemView, dom_element="tbody")


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
                <a href="/shots/{{pyview.subject.parentShot.shot_id}}/download/{{pyview.subject.model_id}}">{{pyview.subject.filename}}  </a>({{pyview.subject.filesize}} MB)
            {% else %}
                {{pyview.subject.status}}
            {% endif %}
        </td>
        <td><button class="btn" onclick='pyview.subject.delete()'> Delete</button></td>
    '''
