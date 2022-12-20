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
<div class="" style=" padding-top: 50px;">
    
    <div class="Images">
        <div class="row justify-content-center" style="width:100%">
            <div class="col-md-12">
                <div class="list-group mb-5 shadow">
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Images</div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
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
                                <div class="col-md-1" style="line-height:3em"> 
                                    {% if pyview.subject.publishing_status == "can_unpublish" %}
                                        <button class="btn btnfw" onclick='pyview.unpublish_images()' > Unpublish </button>
                                    {% elif pyview.subject.publishing_status == "can_publish"  %}
                                        <button class="btn btnfw" onclick='pyview.publish_images()' > Publish </button>
                                    {% elif pyview.subject.publishing_status == "state_changing" %}
                                        <p style="text-align:center">processing</p>
                                    {% endif %}
                                </div>
                            {% endif %}
                        </div>
                    </div>
                                      
                </div>
            </div>   
        </div>
    </div>


    {% if pyview.settingsInstance.realityCaptureSettings.allow_rc_automation == True %}
        {{ pyview.modelFilesView.render() }}
    {% endif %}
    {{ pyview.dropboxPublicFolderView.render() }}
</div>
    '''

    def __init__(self, subject, parent, settingsInstance, **kwargs):
        super().__init__(subject, parent, **kwargs)
        self.settingsInstance = settingsInstance
        self.modelFilesView = ShotFilesModelFilesView(self.subject.models, self, settingsInstance)

        if hasattr(self.subject, "dropboxUpload"):
            self.dropboxUploadView = DropboxUploadView(self.subject.dropboxUpload, self)
        else:
            self.dropboxUploadView = None
        self.dropboxPublicFolderView = DropboxPublicFolderView(self.subject.dropboxPublicFolder, self)

    def open_images_in_explorer(self):
        os.startfile( self.subject.images_path)

    def publish_images(self):
        self.subject.dropboxPublicFolder.add_images()
    def unpublish_images(self):
        self.subject.dropboxPublicFolder.remove_images()
