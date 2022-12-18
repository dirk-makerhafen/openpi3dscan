import os
import time

from pyhtmlgui import PyHtmlView, ObservableListView, ObservableList

from views.shot.files.shotFilesModelFilesView import ShotFilesModelFilesView
from views.shot.files.shotFilesPublicSharingView import DropboxPublicFolderView
from views.shot.shotDropboxUploadView import DropboxUploadView

class ShotFilesImagesView(PyHtmlView):
    TEMPLATE_STR = '''
    
    '''


class ShotFilesView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="row" style="margin-bottom: 10px;">
        <div class="col-md-11" style="font-weight:bold;padding-bottom:10px;">Images</div>
        <div class="col-md-1" style="font-weight:bold;cursor: pointer" onclick='pyview.hide()'>
            <a style="text-align: right;float: right;color: gray;"> Close </a>
        </div>
        <div class="col-md-6" style="padding-left:20px">
            <p class="h5"><a href="/shots/{{pyview.subject.shot_id}}.zip"><i class="fa fa-download" aria-hidden="true"></i> {{pyview.subject.get_clean_shotname()}}.zip </a> </p>
            {% if pyview.parent.show_path == True %}
                <p class="h5"><a href="#" onclick="pyview.open_images_in_explorer()">{{pyview.subject.images_path}}</a></p>
            {% endif %}
        </div>
        {% if pyview.settingsInstance.settingsDropbox.refresh_token != "" and pyview.dropboxUploadView != None %}
            {{ pyview.dropboxUploadView.render() }}
        {% else %}
             <div class="col-md-5"> </div>
        {% endif %}
        {% if  pyview.settingsInstance.settingsDropbox.refresh_token != "" and pyview.subject.dropboxPublicFolder.status != "new" %}
            <div class="col-md-1">
                {% if pyview.subject.dropboxPublicFolder.share_images == True %}
                    <button class="btn " onclick='pyview.unpublish_images()' > Unpublish </button>
                {% else %}
                    <button class="btn " onclick='pyview.publish_images()' > Publish </button>
                {% endif %}
            </div>
        {% endif %}
    </div>
    {% if pyview.settingsInstance.realityCaptureSettings.allow_rc_automation == True %}
        {{ pyview.modelFilesView.render() }}
    {% endif %}
    {{ pyview.dropboxPublicFolderView.render() }}
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
        self.modelFilesView = ShotFilesModelFilesView(self.subject.models, self, settingsInstance)

        if hasattr(self.subject, "dropboxUpload"):
            self.dropboxUploadView = DropboxUploadView(self.subject.dropboxUpload, self)
        else:
            self.dropboxUploadView = None
        self.dropboxPublicFolderView = DropboxPublicFolderView(self.subject.dropboxPublicFolder, self)

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

    def open_images_in_explorer(self):
        os.startfile( self.subject.images_path)

    def publish_images(self):
        self.subject.dropboxPublicFolder.add_images()
    def unpublish_images(self):
        self.subject.dropboxPublicFolder.remove_images()
