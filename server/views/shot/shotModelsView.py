from pyhtmlgui import PyHtmlView, ObservableList, ObservableListView

from app.settings.settings import SettingsInstance


class ModelPreviewFileItemView(PyHtmlView):
    DOM_ELEMENT = "tr"
    TEMPLATE_STR = '''
    <td> {{pyview.subject.create_mesh_from}} </td>
    <td> {{pyview.subject.create_textures}}  </td>
    <td>
        {% if pyview.subject.status == "ready" %} 
            <button class="btn btn-sm" style="line-height: 1em;padding-top: 2px;padding-bottom: 2px;margin-bottom:2px;"  onclick="pyview.select_model()">show</button>
        {% else %}
            {{pyview.subject.status}}
        {% endif %}
    </td>
    '''

    @property
    def DOM_ELEMENT_EXTRAS(self):
        s = 'style="line-height: 1.5em;'
        if self.parent.parent.selected_model == self.subject:
            s += 'background-color: #3e8f3e55;'
        s += '"'
        return s

    def select_model(self):
        self.parent.parent.select_model(self.subject)


class ShotModelsView(PyHtmlView):
    DOM_ELEMENT_EXTRAS = ''
    TEMPLATE_STR = ''' 
    <div class="modelfiles">
        <div class="row"></div>
        <div class="row"></div>
        <div class="row">
            <table style="width:100%;text-align:center">
             <thead>
              <tr>
                <td style="text-align:center">Mesh </td>
                <td style="text-align:center">Texture</td>
                <td style="text-align:center">Action</td>
              </tr>
              </thead>
              
              {{pyview.filesListView.render()}}
              
              <tr style="border-top: 1px solid lightgray; line-height: 3em;">
                    <td>
                        <select name="m_create_mesh_from" id="m_create_mesh_from">
                          <option value="projection" {% if pyview.settings.realityCaptureSettings.default_create_mesh_from == "projection" %}selected{% endif %}>Projection</option>
                          <option value="normal"     {% if pyview.settings.realityCaptureSettings.default_create_mesh_from == "normal"     %}selected{% endif %}>Normal</option>
                          <option value="all"        {% if pyview.settings.realityCaptureSettings.default_create_mesh_from == "all"        %}selected{% endif %}>All Images</option>
                        </select>   
                    </td>
                    <td>
                        <input id="m_create_textures" {% if pyview.settings.realityCaptureSettings.default_create_textures == true %}checked{% endif %}  type="checkbox"/>
                    </td>
                    <td>
                        <button class="btn btn-sm " style="line-height: 1em;    padding-top: 2px;padding-bottom: 2px; margin-bottom: 5px;" onclick='pyview.create_model($("#m_create_mesh_from").val(), $("#m_create_textures")[0].checked);'> Create Model </button>
                    </td>
                </tr>    
            </table>
        </div>
    </div>
    {% if pyview.selected_model != None %}
        <model-viewer  
            src="{{pyview.get_model_url()}}"
            orientation="0deg -90deg 90deg" 
            ar ar-modes="webxr scene-viewer quick-look"  
            seamless-poster 
            shadow-intensity="1" 
            camera-controls 
            enable-pan
            style="width:100%;height:100%"
        >
            <div id="button-load" slot="poster">
                <div style="width:100%;text-align:center;font-size:3em;padding-top: 20%;color:#aaa">
                    loading model
                </div>
            </div>
        </model-viewer>
    {% else %}
        <div style="width:100%;text-align:center;font-size:3em;padding-top: 20%;color:#aaa">
            {% if pyview.has_preview_models %}
                 no model selected 
            {% else %}
                 no model previews found
            {% endif %}         
        </div>
    {% endif %}
    '''

    def __init__(self, subject, parent):
        super().__init__(subject, parent)
        self.current_shot = None
        self.current_models = ObservableList()
        self.selected_model = None
        self.settings = SettingsInstance()
        self.filesListView = ObservableListView(self.current_models, self, item_class=ModelPreviewFileItemView, dom_element="tbody", filter_function=lambda x: x.subject.filetype != "glb")

    def create_model(self, create_mesh_from, create_textures):
        self.parent.create_model(
            filetype="glb",
            reconstruction_quality=SettingsInstance().realityCaptureSettings.default_reconstruction_quality,
            quality="low",
            create_mesh_from=create_mesh_from,
            create_textures=create_textures)

    @property
    def has_preview_models(self):
        return len([m for m in self.current_models if m.filetype == "glb" and m.status == "ready"]) > 0

    def get_model_url(self):
        f = self.selected_model.filename.replace(".zip", "").replace(" ", "_")
        return "/shots/%s/download/%s/%s" % (self.current_shot.shot_id, self.selected_model.model_id, f)

    def select_model(self, model):
        if self.selected_model != model:
            self.selected_model = model
            if self.is_visible:
                self.update()

    def render(self):
        self._update_current_shot()
        return super(ShotModelsView, self).render()

    def update(self) -> None:
        self._update_current_shot()
        return super(ShotModelsView, self).update()

    def _update_current_shot(self):
        if self.current_shot != self.parent.current_shot:
            self.current_shot = self.parent.current_shot
            self.selected_model = None
            if self.current_shot is not None:
                self.current_models = self.parent.current_shot.models
            else:
                self.current_models = ObservableList()
            self.filesListView = ObservableListView(self.current_models, self, item_class=ModelPreviewFileItemView, dom_element="tbody", filter_function=lambda x: x.subject.filetype != "glb")

            models = [m for m in self.current_models if m.filetype == "glb" and m.status == "ready"]
            if len(models) > 0:
                self.selected_model = models[0]
