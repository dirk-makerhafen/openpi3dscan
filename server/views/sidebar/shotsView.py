from pyhtmlgui import PyHtmlView, ObservableListView


class ShotsView(ObservableListView):
    DOM_ELEMENT_CLASS = "ShotsView row"
    TEMPLATE_STR = '''
        {% for item in pyview.get_items() %}
            {{ item.render()}}
        {% endfor %}

    '''

    def __init__(self, subject, parent, **kwargs):
        super().__init__(subject, parent, item_class=ShotsItemView, sort_key=lambda x: x.subject.shot_id, sort_reverse=True, **kwargs)
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

        self.selected_shot = self.parent.subject.shots_remote.get(shot_id)
        if self.is_visible:
            [c.update() for c in self._children if c.subject.shot_id == shot_id]

        if self.selected_shot is not None:
            self.parent.show_shot(self.selected_shot)

    def search(self, value):
        self.filter_function = lambda x: x.subject.name.lower().find(value.lower()) == -1
        self.update()


class ShotsItemView(PyHtmlView):
    DOM_ELEMENT_CLASS = "ShotsItemView col-md-12"
    TEMPLATE_STR = '''
    <div class="row {% if pyview.parent.selected_shot.shot_id == pyview.subject.shot_id %} selected {% endif %}" onclick='pyview.parent.select_shot("{{pyview.subject.shot_id}}");'>
        <div class="col-md-12">
            <div class="name"> 
                {{pyview.subject.name}} {{pyview.subject.status}}
            </div>
            <div class="info"> 
                {{pyview.subject.nr_of_devices}},{{pyview.subject.nr_of_files}},{{pyview.subject.nr_of_models}}{% if pyview.subject.nr_of_models_waiting > 0 or pyview.subject.nr_of_models_failed > 0 %}({% if pyview.subject.nr_of_models_waiting > 0%}{{pyview.subject.nr_of_models_waiting}}{% endif %}{% if pyview.subject.nr_of_models_waiting > 0 and pyview.subject.nr_of_models_failed > 0 %},{% endif %}{% if pyview.subject.nr_of_models_failed > 0%}{{pyview.subject.nr_of_models_failed}}!{% endif %}){% endif %} 
            </div>  
        </div>  
    </div>
    '''