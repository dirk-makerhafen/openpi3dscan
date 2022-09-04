from __future__ import annotations
from typing import TYPE_CHECKING

from pyhtmlgui import PyHtmlView

if TYPE_CHECKING:
    from app.app import App
    from views.appView import AppView
from views.imageCarousel.imageCarouselLive import ImageCarouselLive
from app.devices.devices import DevicesInstance
from app.tasks.tasks import TasksInstance

from app.tasks.task_CreateShot import TaskCreateShotInstance
from app.tasks.task_Whitebalance import TaskWhitebalanceInstance
from app.tasks.task_ShutterBalance import TaskShutterBalanceInstance


class TaskShutterBalanceTopView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="col-md-2 topMenuItem" >
            {% if pyview.subject.status == "idle" %} 
                <button class="btn btn-success" onclick='pyview.run();'> ShutterBalance </button>
            {% else %}
                Balancing
            {% endif %}
        </div>
    '''

    def __init__(self, subject, parent):
        super().__init__(subject, parent)

    def run(self):
        self.subject.run()

class TaskWhitebalanceTopView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="col-md-2 topMenuItem" >
            {% if pyview.subject.status == "idle" %} 
                <button class="btn btn-success" onclick='pyview.run();'> Whitebalance </button>
            {% else %}
                Balancing
            {% endif %}
        </div>
    '''

    def __init__(self, subject, parent):
        super().__init__(subject, parent)

    def run(self):
        self.subject.run()


class TaskCreateShotView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="col-md-2 topMenuItem">
            <input {% if pyview.subject.status != "idle" %}disabled{% endif %} id="_name_input" value="{{pyview._name_input}}" style="width: 100%;line-height: 1.5em;font-size: 1.3em;" placeholder="NAME" type="text"/>
        </div>
        <div class="col-md-2 topMenuItem" >
            {% if pyview.subject.status == "idle" %} 
                <button class="btn btn-success" style="margin-right:5px" onclick='pyview.create_shot( $("#_name_input").val());' style="color:#484"> TAKE SHOT  </button>
            {% else %}
                {% if pyview.subject.status == "preparing"  %} Warmup {% endif %}
                {% if pyview.subject.status == "waiting"    %} Shot in {{pyview.subject.shot_count_down}}{% endif %}
                {% if pyview.subject.status == "shot"       %} SHOT {% endif %}
                {% if pyview.subject.status == "processing" %} Processing {{pyview.subject.processed_percent}}% {% endif %}
            {% endif %}
        </div>
    '''

    def __init__(self, subject, parent):
        super().__init__(subject, parent)
        self._name_input = ""

    def create_shot(self, _name_input):
        self._name_input = _name_input
        self.subject.run(_name_input, self.parent.shot_quality)


class LiveView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="main">
        <div class="topMenu row" style="height:50px">
            {{ pyview.create_shot_view.render() }}

            <div class="col-md-2 topMenuItem">
                <p id="light_value" style="line-height: 15px;margin: 0px;margin-top:5px;text-align: center;">Light ({{pyview.get_light()}}%)</p>
                <input onchange="pyview.set_light(this.value)" oninput="document.getElementById('light_value').innerHTML = 'Light ('+this.value+'%)' " type="range" min="0" max="100" value="{{pyview.get_light()}}" style="min-height:30px;">
            </div>
            <div class="col-md-1 topMenuItem">&nbsp;
            </div>
            
            {{ pyview.shutterbalance_view.render() }}
            {{ pyview.whitebalance_view.render() }}
            
        </div>
        <div style="overflow-y:scroll;height:calc(100% - 35px);">
             {{ pyview.imageCarousel.render() }}
        </div>
    </div>   
    '''


    def __init__(self, subject: App, parent: AppView):
        super().__init__(subject, parent)
        self.imageCarousel = ImageCarouselLive(self.subject, self)
        self._name_input = ""
        self.shot_quality = "speed"
        self.create_shot_view = TaskCreateShotView(TaskCreateShotInstance(), self)
        self.whitebalance_view = TaskWhitebalanceTopView(TaskWhitebalanceInstance(), self)
        self.shutterbalance_view = TaskShutterBalanceTopView(TaskShutterBalanceInstance(), self)
        self._tasks = TasksInstance()

    def whitebalance(self):
        TasksInstance().whitebalance()

    def color_calibrate(self):
        TasksInstance().color_calibrate()

    def set_light(self, value):
        DevicesInstance().lights.set(value)

    def get_light(self):
        return  DevicesInstance().lights.value

    def switch_type(self):
        self.imageCarousel.switch_type()
        projection_active = self.imageCarousel.image_type == "projection"
        DevicesInstance().projectors.set(projection_active)

