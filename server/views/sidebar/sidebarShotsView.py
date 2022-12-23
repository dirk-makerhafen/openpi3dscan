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
    TEMPLATE_STR = ''',{{pyview.subject.progress}}%'''

class NrOfDevicesView(PyHtmlView):
    DOM_ELEMENT = "dummy"
    TEMPLATE_STR = '''{{pyview.subject | length }},'''

class NrOfFilesView(PyHtmlView):
    DOM_ELEMENT = "dummy"
    TEMPLATE_STR = '''{{pyview.subject.value }}'''

class ModelsStatsView(PyHtmlView):
    DOM_ELEMENT = "dummy"
    TEMPLATE_STR = '''
    ,{{pyview.subject.models|length}}{% if pyview.subject.waiting_or_processing|length > 0 or pyview.subject.failed|length > 0 %}({% if pyview.subject.waiting_or_processing|length > 0%}{{pyview.subject.waiting_or_processing|length}}{% endif %}{% if pyview.subject.waiting_or_processing|length > 0 and pyview.subject.failed|length > 0 %},{% endif %}{% if pyview.subject.failed|length > 0%}{{pyview.subject.failed|length}}!{% endif %}){% endif %}
    '''

class ShotsItemView(PyHtmlView):
    DOM_ELEMENT_CLASS = "ShotsItemView col-md-12"
    TEMPLATE_STR = '''
    <div class="row {% if pyview.parent.selected_shot.shot_id == pyview.subject.shot_id %} selected {% endif %}" onclick='pyview.parent.select_shot("{{pyview.subject.shot_id}}");'>
        <div class="col-md-12">
            <div class="name"> 
               {% if pyview.subject.devices == None %}{{pyview.subject.meta_location}},{% endif %} {{pyview.subject.name}} {{pyview.subject.status}}
            </div>
            <div class="info"> 
                {% if pyview.nrOfDevicesView != None %}{{pyview.nrOfDevicesView.render()}}{% endif %}{{pyview.nrOfFilesView.render()}}{% if pyview.parent.settingsInstance.realityCaptureSettings.allow_rc_automation == True %}{{pyview.modelsStatsView.render()}}{% endif %}{% if pyview.dropboxUploadView != None %}{{pyview.dropboxUploadView.render()}}{% endif %} 
            </div>  
        </div>  
    </div>
    '''
    def __init__(self, subject, parent):
        super().__init__(subject, parent)
        self.nrOfDevicesView = None
        self.dropboxUploadView = None
        self.nrOfFilesView = NrOfFilesView(self.subject.nr_of_files, self)
        self.modelsStatsView = ModelsStatsView(self.subject.model, self)
        if self.subject.devices is not None:
            self.nrOfDevicesView = NrOfDevicesView(self.subject.devices, self)

    def update(self):
        if hasattr(self.subject, "dropboxUpload"):
            if self.subject.dropboxUpload.status != "uploading":
                if self.dropboxUploadView is not None:
                    self.dropboxUploadView.delete(remove_from_dom = False)
                    self.dropboxUploadView = None
            else:
                if self.dropboxUploadView is None:
                    self.dropboxUploadView = SidebarDropboxUploadView(self.subject.dropboxUpload, self)
        if self.is_visible:
            super().update()