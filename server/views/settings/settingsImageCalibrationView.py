from pyhtmlgui import PyHtmlView

from app.settings.settings import SettingsInstance
from app.tasks.task_CameraBalance import TaskCameraBalanceInstance
from app.tasks.task_ShutterBalance import TaskShutterBalanceInstance
from app.tasks.task_Whitebalance import TaskWhitebalanceInstance



class TaskCameraBalanceView(PyHtmlView):
    TEMPLATE_STR = '''
        {% if pyview.subject.status == "idle" %} 
            <button class="btn btnfw" onclick='pyview.subject.run();'> Calibrate now </button>
        {% else %}
            <p class="btn" style="color:green">Calibrating</p>
        {% endif %}
    '''



class TaskShutterBalanceView(PyHtmlView):
    TEMPLATE_STR = '''
        {% if pyview.subject.status == "idle" %} 
            <button class="btn" onclick='pyview.subject.run();'> Calibrate </button>
        {% else %}
            <p class="btn" style="color:green">Calibrating</p>
        {% endif %}
    '''


class TaskWhitebalanceView(PyHtmlView):
    TEMPLATE_STR = '''
        {% if pyview.subject.status == "idle" %} 
            <button class="btn" onclick='pyview.subject.run();'> Calibrate </button>
        {% else %}
            <p class="btn" style="color:green">Calibrating</p>
        {% endif %}
    '''


class CameraImageCalibationView(PyHtmlView):
    DOM_ELEMENT_CLASS = "CameraSettingsView"
    TEMPLATE_STR = '''
    <div class="row justify-content-center" style="width: 100%">
        <div class="col-md-12">
            <div class="list-group mb-5 shadow">
                <div class="list-group-item">
                    <div class="row align-items-center">
                        <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Image calibration</div>
                    </div>
                </div>
                <div class="list-group-item" style="display:none">
                    <div class="row align-items-center">
                        <div class="col-md-8">
                            <strong class="mb-0">Shutter speed (0=Auto)</strong>
                            <p class="text-muted mb-0">Set Shutter speed for cameras, or click <i>Calibrate</i> to select automatically.</p>
                        </div>
                        <div class="col-md-2">{{pyview.shutterbalance_view.render()}}</div>
                        <div class="col-md-2">
                            <div class="custom-control custom-switch">
                                <input ca="width:100%" id="shutter_speed" type=number value="{{pyview.subject.shutter_speed}}" onchange='pyview.subject._set_shutter_speed($("#shutter_speed").val())'>
                                <span class="custom-control-label"></span>
                            </div>
                        </div>
                    </div>
                </div> 
                <div class="list-group-item" style="display:none">
                    <div class="row align-items-center">
                        <div class="col-md-8">
                            <strong class="mb-0">Whitebalance gains</strong>
                            <p class="text-muted mb-0">Set whitebalance gains for cameras, or click <i>Calibrate</i> to select automatically.</p>
                        </div>
                        <div class="col-md-2">{{pyview.whitebalance_view.render()}}</div>
                        <div class="col-md-1">
                            <div class="custom-control custom-switch">
                                <p style="color:red" >red</p>
                                <input style="width:100%" id="awb_gain_red" type="number" step="0.01" value="{{pyview.subject.awb_gains[0]}}" onchange='pyview._set_awb_gain_red($("#awb_gain_red").val())'>
                            </div>
                        </div>
                        <div class="col-md-1">
                            <div class="custom-control custom-switch">
                                <p style="color:blue">blue</p>
                                <input style="width:100%" id="awb_gain_blue" type="number" step="0.01" value="{{pyview.subject.awb_gains[1]}}" onchange='pyview._set_awb_gain_blue($("#awb_gain_blue").val())'>
                            </div>
                        </div>
                    </div>
                </div>   
                <div class="list-group-item">
                    <div class="row align-items-center">
                        <div class="col-md-10">
                            <strong class="mb-0">Auto calibrate</strong>
                            <p class="text-muted mb-0">Automatically set shutter speed and whitebalance gains.</p>
                        </div>
                        <div class="col-md-2">{{pyview.camerabalance_view.render()}}</div>
                    </div>
                </div>  
                <div class="list-group-item">
                    <div class="row align-items-center">
                        <div class="col-md-10">
                            <strong class="mb-0">Adjust shutter speed</strong>
                            <p class="text-muted mb-0">Adjust automatically calibrated shutter speeds up or down</p>
                        </div>
                        <div class="col-md-2">
                            <p id="ssa_value" style="line-height: 15px;margin: 0px;margin-top:5px;text-align: center;">{{pyview.subject.shutter_speed_adjustment}}%, avg {{pyview.subject.average_shutter_speed}}ms</p>
                            <input onchange="pyview.subject._set_shutter_speed_adjustment(this.value)" oninput="document.getElementById('ssa_value').innerHTML = ''+this.value+'%' " type="range" min="-100" max="100" value="{{pyview.subject.shutter_speed_adjustment}}" style="min-height:30px;">
                        </div>
                    </div>
                </div>  
                <div class="list-group-item">
                    <div class="row align-items-center">
                        <div class="col-md-12">
                            <table id="calibrationtable" class="table">
                                <thead>
                                    <tr>
                                        <th></th>
                                        {% for i in range(pyview.settings_scanner.segments) %}
                                            <th>SEG{{loop.index}}</th>
                                        {% endfor %}
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>Shutter, calibrated</td>
                                        {% for per_segment_shutter_speed in pyview.subject.per_segment_shutter_speeds %}
                                            <td> {{ per_segment_shutter_speed }} </td>
                                        {% endfor %}
                                    </tr>
                                    <tr>
                                        <td>Shutter, adjusted</td>
                                        {% for per_segment_shutter_speed in pyview.subject.adjusted_shutter_speeds %}
                                            <td> {{ per_segment_shutter_speed }} </td>
                                        {% endfor %}
                                    </tr>
                                    <tr>
                                        <td>Red</td>
                                        {% for per_segment_awb_gains_red in pyview.subject.per_segment_awb_gains %}
                                            <td> {{ per_segment_awb_gains_red[0] }} </td>
                                        {% endfor %}
                                    </tr>
                                    <tr>
                                        <td>Blue</td>
                                        {% for per_segment_awb_gains_blue in pyview.subject.per_segment_awb_gains %}
                                            <td> {{ per_segment_awb_gains_blue[1] }} </td>
                                        {% endfor %}
                                    </tr>
                                </tbody>
                            </table>  
                        </div>    
                    </div>
                </div>                   
            </div>
        </div>
    </div>
    '''

    def __init__(self, subject, parent):
        super().__init__(subject, parent)
        self.whitebalance_view = TaskWhitebalanceView(TaskWhitebalanceInstance(), self)
        self.shutterbalance_view = TaskShutterBalanceView(TaskShutterBalanceInstance(), self)
        self.camerabalance_view = TaskCameraBalanceView(TaskCameraBalanceInstance(), self)
        self.settings_scanner = SettingsInstance().settingsScanner

    def _set_awb_gain_red(self, value):
        gains = self.subject.awb_gains
        gains[0] = float(value)
        self.subject.awb_gains = gains

    def _set_awb_gain_blue(self, value):
        gains = self.subject.awb_gains
        gains[1] = float(value)
        self.subject.awb_gains = gains

