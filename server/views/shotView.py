from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.app import App
import os
from pyhtmlgui import PyHtmlView
from views.shot.shotFilesView import ShotFilesView
from views.shot.shotModelsView import ShotModelsView
from views.shot.shotComentsView import ShotCommentsView
from views.imageCarousel.imageCarouselStatic import ImageCarouselStatic
from app.files.shots import ShotsInstance


class ShotView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="main" style="overflow-y:hidden;">
        <div class="topMenu row">
            {% if pyview.current_shot._deleted != True %}
                <div class="col-md-3 topMenuItem">
                    <input id="_name_input" value="{{pyview.current_shot.name}}" onchange='pyview.current_shot.set_name($("#_name_input").val())' style="width:100%;line-height: 1.5em;font-size: 1.1em;" placeholder="NAME" type="text"/>
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
                <div id="files_btn" class="col-md-1 topMenuItem" onclick='pyview.toggle_files();'>
                    Files
                </div>
                {% if pyview.show_path == True %}
                    <div class="{% if pyview.settingsInstance.realityCaptureSettings.allow_rc_automation == True %}col-md-3{% else %}col-md-4{% endif %} topMenuItem"> <a href="#" onclick="pyview.open_in_explorer()">{{pyview.current_shot.path}}</a>  </div>
                {% else %}
                    <div class="{% if pyview.settingsInstance.realityCaptureSettings.allow_rc_automation == True %}col-md-3{% else %}col-md-4{% endif %} topMenuItem"> &nbsp; </div>
                {% endif %}
                
                <div class="col-md-1 topMenuItem">
                    {% if pyview.can_sync == True %}
                        <button class="btn" style="margin-right:5px" onclick='pyview.sync_remote();'> Sync </button>
                    {% else %}
                        <select class="form-control" style="display: initial;" id="available_locations"  onchange='pyview.set_location($("#available_locations").val())' >
                            {% if pyview.current_shot.meta_location == "" %}
                                <option value="" selected>- SELECT A LOCATION -</option>
                            {% endif  %}
                            {% for location in pyview.available_locations() %}
                                <option value="{{location}}" {% if location==pyview.current_shot.meta_location %}selected{% endif %}>{{location}}</option>
                            {% endfor %}      
                        </select>
                    {% endif %}
                </div>
                <div class="col-md-1 topMenuItem" style="border-right: 0px;">
                    <button class="btn btn-warning" style="margin-right:5px" onclick='$("#confirm_delete").show();'> Delete </button>
                    <div id="confirm_delete" class="confirm_delete" style="display:none;z-index:999;position:fixed;left:40%;top:10%;width:40%;background-color:white;padding: 10px;padding-botton:20px;border: 5px solid #f33;">
                        <div class="row">
                            <div class="col-md-12" style="font-weight:bold;padding-bottom:10px;text-align:center">
                                Delete Shot '{{pyview.current_shot.name}}' ? 
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
            {% if pyview.current_shot._deleted != True %}
                {{ pyview.current_view.render() }}
            {% else %}
                <div style="width:100%;text-align:center;font-size:3em;padding-top: 20%;color:#aaa">
                    <b>{{pyview.current_shot.name}}</b> <br>
                    has been removed      
                </div>
            {% endif %}
        </div>
        {% if pyview.current_shot._deleted != True %}
            {{ pyview.comments.render() }}
            {{ pyview.shotFiles.render() }}
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

    def __init__(self, subject: App, parent, settingsInstance):
        super().__init__(subject, parent)
        self.imageCarousel = ImageCarouselStatic(self.subject, self)
        self.shotModels = ShotModelsView(self.subject, self, settingsInstance)
        self.comments = ShotCommentsView(self.subject, self)
        self.shotFiles = ShotFilesView(self.subject, self,settingsInstance)
        self.current_shot = None
        self.current_view = self.imageCarousel
        self.can_sync = True
        self.show_path = False
        self.settingsInstance = settingsInstance

    def open_in_explorer(self):
        if self.current_shot is not None:
            os.startfile( self.current_shot.path)

    def show_shot(self, shot):
        if self.current_shot != shot:
            self.current_shot = shot
            self.current_view = self.imageCarousel
            if self.is_visible:
                self.update()

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
        self.shotFiles.hide()
        self.comments.toggle()

    def toggle_files(self):
        self.comments.hide()
        self.shotFiles.toggle()

    def delete_shot(self):
        ShotsInstance().delete(self.current_shot)
        self.current_shot._deleted = True
        if self.is_visible:
            self.update()

    def rename(self, value):
        self.current_shot.set_name(value)

    def sync_remote(self):
        self.current_shot.sync_remote()

    def set_location(self, location):
        raise NotImplementedError()

    def create_model(self, filetype="obj", reconstruction_quality="high", quality="high", create_mesh_from="projection", create_textures=False, lit=True):
        if create_textures is None:
            create_textures = False
        self.current_shot.create_model(filetype=filetype, reconstruction_quality=reconstruction_quality, quality=quality, create_mesh_from=create_mesh_from, create_textures=create_textures, lit=lit)

    def switch_type(self):
        self.imageCarousel.switch_type()

    def available_locations(self):
        raise NotImplementedError()
