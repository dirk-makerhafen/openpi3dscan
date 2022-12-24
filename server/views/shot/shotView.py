import os
from views.images.imageStaticView import ImagesStaticView
from views.shot.files.shotFilesView import ShotFilesView
from pyhtmlgui import PyHtmlView
from views.shot.shotModelsView import ShotModelsView
from views.shot.shotComentsView import ShotCommentsView

class ShotView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="main" style="overflow-y:hidden;">
        <div class="topMenu row">
            {% if pyview.subject._deleted != True %}
                <div class="col-md-3 topMenuItem">
                    <input id="_name_input" value="{{pyview.subject.name}}" onchange='pyview.subject.set_name($("#_name_input").val())' style="width:100%;line-height: 1.5em;font-size: 1.1em;" placeholder="NAME" type="text"/>
                </div>
                <div class="col-md-1 topMenuItem {% if pyview.current_view == pyview.imageCarousel%}selected{%endif%}" onclick='pyview.show_shot_2d();'>
                   Images
                </div>
                {% if pyview.settingsInstance.realityCaptureSettings.allow_rc_automation == True %}
                    <div class="col-md-1 topMenuItem {% if pyview.current_view == pyview.shotModels   %}selected{%endif%}" onclick='pyview.show_shot_3d();'>
                        3D Models 
                    </div>
                {% endif %}
                <div id="comments_btn" class="col-md-1 topMenuItem" onclick='pyview.toggle_comments();'>
                    Comments
                </div>
                <div id="files_btn" class="col-md-1 topMenuItem {% if pyview.current_view == pyview.shotFiles   %}selected{%endif%}" onclick='pyview.show_files();'>
                    Files
                </div>        
                {% if pyview.show_path == True %}
                    <div class="{% if pyview.settingsInstance.realityCaptureSettings.allow_rc_automation == True %}col-md-3{% else %}col-md-4{% endif %} topMenuItem"> <a href="#" onclick="pyview.open_in_explorer()">{{pyview.subject.path}}</a>  </div>
                {% else %}
                    <div class="{% if pyview.settingsInstance.realityCaptureSettings.allow_rc_automation == True %}col-md-3{% else %}col-md-4{% endif %} topMenuItem"> &nbsp; </div>
                {% endif %}
                
                <div class="col-md-1 topMenuItem">
                    {% if pyview.can_sync == True %}
                        <button class="btn" style="margin-right:5px" onclick='pyview.sync_remote();'> Sync </button>
                    {% else %}
                        <select class="form-control" style="display: initial;" id="available_locations"  onchange='pyview.set_location($("#available_locations").val())' >
                            {% if pyview.subject.meta_location == "" %}
                                <option value="" selected>- SELECT A LOCATION -</option>
                            {% endif  %}
                            {% for location in pyview.available_locations() %}
                                <option value="{{location}}" {% if location==pyview.subject.meta_location %}selected{% endif %}>{{location}}</option>
                            {% endfor %}      
                        </select>
                    {% endif %}
                </div>
                <div class="col-md-1 topMenuItem" style="border-right: 0px;">
                    <button class="btn btn-warning" style="margin-right:5px" onclick='$("#confirm_delete").show();'> Delete </button>
                    <div id="confirm_delete" class="confirm_delete" style="display:none;z-index:999;position:fixed;left:40%;top:10%;width:40%;background-color:white;padding: 10px;padding-botton:20px;border: 5px solid #f33;">
                        <div class="row">
                            <div class="col-md-12" style="font-weight:bold;padding-bottom:10px;text-align:center">
                                Delete Shot '{{pyview.subject.name}}' ? 
                            </div>
                            <div class="col-md-6" style="font-weight:bold;">
                                <button class="btn btn-danger" onclick='pyview.delete_shot();$("#confirm_delete").hide();'>DELETE</button>
                            </div>
                            <div class="col-md-6" style="font-weight:bold;">
                                <button class="btn btn-success"  onclick='$("#confirm_delete").hide();'>Cancel</button>
                            </div>
                        </div>
                    </div>                    
                </div>
            {% endif %}
        </div>
        <div style="overflow-y:scroll;height:calc(100% - 0{% if pyview.current_view == pyview.imageCarousel %}35{%endif%}px);">
            {% if pyview.subject._deleted != True %}
                {{ pyview.current_view.render() }}
            {% else %}
                <div style="width:100%;text-align:center;font-size:3em;padding-top: 20%;color:#aaa">
                    <b>{{pyview.subject.name}}</b> <br>
                    has been removed      
                </div>
            {% endif %}
        </div>
        {% if pyview.subject._deleted != True %}
            {{ pyview.comments.render() }}
        {% endif %}
        <script>
            document.onkeydown = function (e) {
                if ( e.keyCode ==  33 ||  e.keyCode ==  34){ 
                    e.preventDefault();
                };
                if ( e.keyCode ==  33 ||  e.keyCode ==  37){    // pageup or  left
                    pyview.imageCarousel.rotate_cw();
                };
                if ( e.keyCode ==  34 ||  e.keyCode ==  39){    // pagedown or  right
                    pyview.imageCarousel.rotate_ccw();
                };
            };
        </script>
        
    </div>   
    '''



    def __init__(self, subject, parent, settingsInstance, shotsInstance):
        self._on_subject_updated = None
        super().__init__(subject, parent)
        self.imageCarousel = ImagesStaticView(self.subject, self)
        self.shotModels = ShotModelsView(self.subject, self, settingsInstance)
        self.comments = ShotCommentsView(self.subject.comment, self)
        self.shotFiles = ShotFilesView(self.subject, self,settingsInstance)
        self.current_view = self.imageCarousel
        self.can_sync = True
        self.show_path = False
        self.settingsInstance = settingsInstance
        self.shotsInstance = shotsInstance

    def open_in_explorer(self):
        if self.subject is not None:
            os.startfile( self.subject.path)

    def show_shot_2d(self):
        if self.current_view != self.imageCarousel:
            self.current_view = self.imageCarousel
            if self.is_visible:
                self.update()

    def show_shot_3d(self):
        if self.current_view != self.shotModels:
            self.current_view = self.shotModels
            if self.is_visible:
                self.update()

    def toggle_comments(self):
        self.comments.toggle()

    def show_files(self):
        if self.current_view != self.shotFiles:
            self.current_view = self.shotFiles
            if self.is_visible:
                self.update()

    def delete_shot(self):
        self.shotsInstance.delete(self.subject)
        self.subject._deleted = True
        if self.is_visible:
            self.update()

    def rename(self, value):
        self.subject.set_name(value)

    def sync_remote(self):
        self.subject.sync_remote()

    def set_location(self, location):
        raise NotImplementedError()

    def create_model(self, filetype="obj", reconstruction_quality="high", quality="high", create_mesh_from="projection", create_textures=False, lit=True):
        if create_textures is None:
            create_textures = False
        self.subject.create_model(filetype=filetype, reconstruction_quality=reconstruction_quality, quality=quality, create_mesh_from=create_mesh_from, create_textures=create_textures, lit=lit)

    def create_models_from_set(self, set_name ):
        self.subject.create_models_from_set(set_name)


    def switch_type(self):
        self.imageCarousel.switch_type()

    def available_locations(self):
        raise NotImplementedError()
