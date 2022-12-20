from pyhtmlgui import PyHtmlView, ObservableListView


class SidebarShotsView(ObservableListView):
    DOM_ELEMENT_CLASS = "ShotsView row"
    TEMPLATE_STR = '''
    {% for item in pyview.get_items() %}
        {{ item.render()}}
    {% endfor %}
    '''

    def __init__(self, subject, parent, settingsInstance, **kwargs):
        super().__init__(subject, parent, item_class=ShotsItemView, sort_key=lambda x: x.subject.shot_id, sort_reverse=True, **kwargs)
        self.settingsInstance = settingsInstance
        self.selected_shot = None

    def select_shot(self, shot_id):
        if self.selected_shot is None and shot_id is None:
            return
        if self.selected_shot is not None and self.selected_shot.shot_id == shot_id:  # no changes
            return

        if self.selected_shot is not None:  # unselect current shot
            currently_selected_shot_id = self.selected_shot.shot_id
            self.selected_shot = None
            if self.is_visible:
                [c.update() for c in self._children if c.subject.shot_id == currently_selected_shot_id]

        if shot_id is None:
            return

        self.selected_shot = self.parent.subject.shots.get(shot_id)
        if self.is_visible:
            [c.update() for c in self._children if c.subject.shot_id == shot_id]

        if self.selected_shot is not None:
            self.parent.show_shot(self.selected_shot)

    def search(self, value):
        self.filter_function = lambda x: True in [ (x.subject.name.lower().find(sv) == -1 and x.subject.meta_location.lower().find(sv) == -1 and x.subject.shot_id.lower().find(sv.replace(":","")) == -1) for sv in value.lower().split(" ")]
        self.update()


class SidebarDropboxUploadView(PyHtmlView):
    DOM_ELEMENT = "dummy"
    TEMPLATE_STR = ''',{{pyview.subject.current_progress}}%'''

class ShotsItemView(PyHtmlView):
    DOM_ELEMENT_CLASS = "ShotsItemView col-md-12"
    TEMPLATE_STR = '''
    <div class="row {% if pyview.parent.selected_shot.shot_id == pyview.subject.shot_id %} selected {% endif %}" onclick='pyview.parent.select_shot("{{pyview.subject.shot_id}}");'>
        <div class="col-md-12">
            <div class="name"> 
               {% if pyview.subject.devices == None %}{{pyview.subject.meta_location}},{% endif %} {{pyview.subject.name}} {{pyview.subject.status}}
            </div>
            <div class="info"> 
                {% if pyview.subject.devices != None %}{{pyview.subject.nr_of_devices}},{% endif %}{{pyview.subject.nr_of_files}}{% if pyview.parent.settingsInstance.realityCaptureSettings.allow_rc_automation == True %},{{pyview.subject.nr_of_models}}{% if pyview.subject.nr_of_models_waiting_or_processing > 0 or pyview.subject.nr_of_models_failed > 0 %}({% if pyview.subject.nr_of_models_waiting_or_processing > 0%}{{pyview.subject.nr_of_models_waiting_or_processing}}{% endif %}{% if pyview.subject.nr_of_models_waiting_or_processing > 0 and pyview.subject.nr_of_models_failed > 0 %},{% endif %}{% if pyview.subject.nr_of_models_failed > 0%}{{pyview.subject.nr_of_models_failed}}!{% endif %}){% endif %}{% endif %}{% if pyview.dropboxUploadView != None %}{{pyview.dropboxUploadView.render()}}{% endif %} 
            </div>  
        </div>  
    </div>
    '''
    def __init__(self, subject, parent):
        super().__init__(subject, parent)
        self.dropboxUploadView = None

    def update(self):
        if hasattr(self.subject, "dropboxUpload"):
            if self.subject.dropboxUpload.status != "uploading":
                if self.dropboxUploadView is not None:
                    self.dropboxUploadView.delete(remove_from_dom = False)
                    self.dropboxUploadView = None
            else:
                if self.dropboxUploadView is None:
                    self.dropboxUploadView = SidebarDropboxUploadView(self.subject.dropboxUpload, self)
        super().update()