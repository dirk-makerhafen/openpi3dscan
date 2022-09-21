from __future__ import annotations
from typing import TYPE_CHECKING
from pyhtmlgui import PyHtmlView

from app.tasks.task_CameraBalance import TaskCameraBalanceInstance

if TYPE_CHECKING:
    from app.app import App
    from views.appView import AppView
from views.imageCarousel.imageCarouselLive import ImageCarouselLive
from app.devices.devices import DevicesInstance
from app.tasks.tasks import TasksInstance
from app.tasks.task_CreateShot import TaskCreateShotInstance


class TaskShutterBalanceTopView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="col-md-2 topMenuItem">
        {% if pyview.subject.status == "idle" %} 
            <button class="btn btn-success" onclick='pyview.run();'> Shutterbalance </button>
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
    <div class="col-md-2 topMenuItem">
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


class TaskCameraBalanceTopView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="col-md-2 topMenuItem" style="border-right: 0px;">
        {% if pyview.subject.status == "idle" %} 
            <button class="btn" onclick='pyview.run();'> Balance </button>
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
            <button id="create_shot_btn" class="btn btn-success" style="margin-right:5px; width: 80%;" onclick='pyview.create_shot( $("#_name_input").val());' style="color:#484"> TAKE SHOT  </button>
        {% else %}
             <div style="
                    position: fixed;
                    left: 0px;
                    top: 0px;
                    width: 100%;
                    background-color: #bbb9;
                    color: #fff;
                    height: 100%;
                    font-size: 8em;
                    padding-top: 20%;
                    z-index: 999;
            "> 
                {% if pyview.subject.status == "preparing"  %} Warmup {% endif %}
                {% if pyview.subject.status == "waiting"    %} Shot in {{pyview.subject.shot_count_down}}  {% endif %}
                {% if pyview.subject.status == "shot"       %} SHOT {% endif %}
                {% if pyview.subject.status == "processing" %} Processing {{pyview.subject.processed_percent}}% {% endif %}                
            </div>
        {% endif %}
    </div>
    <script>
        document.onkeydown = function (e) {
            if ( e.keyCode ==  27 ){    // start or play
                {% if pyview.subject.status == "idle" %} 
                    pyview.create_shot( $("#_name_input").val();
                {% endif %}
            };
        };
    </script>
    '''

    def __init__(self, subject, parent):
        super().__init__(subject, parent)
        self._name_input = ""

    def create_shot(self, _name_input):
        self._name_input = _name_input
        self.subject.run(_name_input, self.parent.shot_quality)


class LiveView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="main" style="overflow-y:hidden;" >
        <div class="topMenu row" style="height:50px">
            {{ pyview.create_shot_view.render() }}
            <div class="col-md-4 topMenuItem">&nbsp;</div>
            <div class="col-md-2 topMenuItem">
                <p id="light_value" style="line-height: 15px;margin: 0px;margin-top:5px;text-align: center;">Light ({{pyview.get_light()}}%)</p>
                <input onchange="pyview.set_light(this.value)" oninput="document.getElementById('light_value').innerHTML = 'Light ('+this.value+'%)' " type="range" min="0" max="100" value="{{pyview.get_light()}}" style="min-height:30px;">
            </div>
            {{ pyview.camerabalance_view.render() }}
        </div>
        <div style="overflow-y:scroll;height:calc(100% - 35px);">
             {{ pyview.imageCarousel.render() }}
        </div>
    </div>   
    '''

    def __init__(self, subject: App, parent):
        super().__init__(subject, parent)
        self.imageCarousel = ImageCarouselLive(self.subject, self)
        self._name_input = ""
        self.shot_quality = "speed"
        self.create_shot_view = TaskCreateShotView(TaskCreateShotInstance(), self)
        #self.whitebalance_view = TaskWhitebalanceTopView(TaskWhitebalanceInstance(), self)
        #self.shutterbalance_view = TaskShutterBalanceTopView(TaskShutterBalanceInstance(), self)
        self.camerabalance_view = TaskCameraBalanceTopView(TaskCameraBalanceInstance(), self)
        self._tasks = TasksInstance()

    def whitebalance(self):
        TasksInstance().whitebalance()

    def color_calibrate(self):
        TasksInstance().color_calibrate()

    def set_light(self, value):
        DevicesInstance().lights.set(value)

    def get_light(self):
        return DevicesInstance().lights.value

    def switch_type(self):
        self.imageCarousel.switch_type()
        projection_active = self.imageCarousel.image_type == "projection"
        DevicesInstance().projectors.set(projection_active)

