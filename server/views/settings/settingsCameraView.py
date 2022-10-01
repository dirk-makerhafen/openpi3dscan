from pyhtmlgui import PyHtmlView

from app.settings.settings import SettingsInstance
from app.tasks.task_CameraBalance import TaskCameraBalanceInstance
from app.tasks.task_ShutterBalance import TaskShutterBalanceInstance
from app.tasks.task_Whitebalance import TaskWhitebalanceInstance



class TaskCameraBalanceView(PyHtmlView):
    TEMPLATE_STR = '''
        {% if pyview.subject.status == "idle" %} 
            <button class="btn" onclick='pyview.subject.run();'> Calibrate all </button>
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


class CameraSettingsView(PyHtmlView):
    DOM_ELEMENT_CLASS = "CameraSettingsView"
    TEMPLATE_STR = '''
    <div class="row justify-content-center" style="width: 100%">
        <div class="col-md-12">
            <div class="list-group mb-5 shadow">
                <div class="list-group-item">
                    <div class="row align-items-center">
                        <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Camera Settings</div>
                    </div>
                </div>

                <div class="list-group-item">
                    <div class="row align-items-center">
                        <div class="col-md-10">
                            <strong class="mb-0">ISO</strong>
                            <p class="text-muted mb-0">Select the apparent ISO setting of the cameras. Default: 100</p>
                        </div>
                        <div class="col-auto">
                            <div class="custom-control custom-switch">
                                <select name="iso" id="iso"  onchange='pyview.subject._set_iso($("#iso").val())'>
                                    <option value="0"   {% if pyview.subject.iso == 0   %}selected{%endif%}>Auto</option>
                                    <option value="100" {% if pyview.subject.iso == 100 %}selected{%endif%}>100</option>
                                    <option value="200" {% if pyview.subject.iso == 200 %}selected{%endif%}>100</option>
                                    <option value="320" {% if pyview.subject.iso == 320 %}selected{%endif%}>320</option>
                                    <option value="400" {% if pyview.subject.iso == 400 %}selected{%endif%}>400</option>
                                    <option value="500" {% if pyview.subject.iso == 500 %}selected{%endif%}>500</option>
                                    <option value="640" {% if pyview.subject.iso == 640 %}selected{%endif%}>640</option>
                                    <option value="800" {% if pyview.subject.iso == 800 %}selected{%endif%}>800</option>
                                </select>  
                                <span class="custom-control-label"></span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="list-group-item">
                    <div class="row align-items-center">
                        <div class="col-md-10">
                            <strong class="mb-0">Exposure mode </strong>
                            <p class="text-muted mb-0">Sets the exposure mode of the camera. Default: Backlight</p>
                        </div>
                        <div class="col-auto">
                            <div class="custom-control custom-switch">
                                <select name="exposure_mode" id="exposure_mode" onchange='pyview.subject._set_exposure_mode($("#exposure_mode").val())'>
                                  <option value='off'          {% if pyview.subject.exposure_mode == 'off'          %}selected{%endif%}>OFF</option>
                                  <option value='auto'         {% if pyview.subject.exposure_mode == 'auto'         %}selected{%endif%}>Auto</option>
                                  <option value='night'        {% if pyview.subject.exposure_mode == 'night'        %}selected{%endif%}>Night</option>
                                  <option value='nightpreview' {% if pyview.subject.exposure_mode == 'nightpreview' %}selected{%endif%}>Nightpreview</option>
                                  <option value='backlight'    {% if pyview.subject.exposure_mode == 'backlight'    %}selected{%endif%}>Backlight</option>
                                  <option value='spotlight'    {% if pyview.subject.exposure_mode == 'spotlight'    %}selected{%endif%}>Spotlight</option>
                                  <option value='sports'       {% if pyview.subject.exposure_mode == 'sports'       %}selected{%endif%}>Sports</option>
                                  <option value='snow'         {% if pyview.subject.exposure_mode == 'snow'         %}selected{%endif%}>Snow</option>
                                  <option value='beach'        {% if pyview.subject.exposure_mode == 'beach'        %}selected{%endif%}>Beach</option>
                                  <option value='verylong'     {% if pyview.subject.exposure_mode == 'verylong'     %}selected{%endif%}>Verylong</option>
                                  <option value='fixedfps'     {% if pyview.subject.exposure_mode == 'fixedfps'     %}selected{%endif%}>Fixedfps</option>
                                  <option value='antishake'    {% if pyview.subject.exposure_mode == 'antishake'    %}selected{%endif%}>Antishake</option>
                                  <option value='fireworks'    {% if pyview.subject.exposure_mode == 'fireworks'    %}selected{%endif%}>Fireworks</option>
                                </select>
                                <span class="custom-control-label"></span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="list-group-item">
                    <div class="row align-items-center">
                        <div class="col-md-10">
                            <strong class="mb-0">Meter mode</strong>
                            <p class="text-muted mb-0">
                                Adjusts the cameras metering mode. All modes set up two regions: a center region, and an outer region. The 'backlit' mode has the largest central region (30% ), while 'spot' has the smallest
                                . Default is "Spot"
                            </p>
                        </div>
                        <div class="col-auto">
                            <div class="custom-control custom-switch">
                                <select name="meter_mode" id="meter_mode" onchange='pyview.subject._set_meter_mode($("#meter_mode").val())'>
                                  <option value='average'{% if pyview.subject.meter_mode == 'average' %}selected{%endif%}>Average</option>
                                  <option value='spot'   {% if pyview.subject.meter_mode == 'spot'    %}selected{%endif%}>Spot (10%)</option>
                                  <option value='backlit'{% if pyview.subject.meter_mode == 'backlit' %}selected{%endif%}>Backlit (30%)</option>
                                  <option value='matrix' {% if pyview.subject.meter_mode == 'matrix'  %}selected{%endif%}>Matrix</option>
                                </select>
                                <span class="custom-control-label"></span>
                            </div>
                        </div>
                    </div>
                </div> 

                <div class="list-group-item">
                    <div class="row align-items-center">
                        <div class="col-md-10">
                            <strong class="mb-0">AWB mode</strong>
                            <p class="text-muted mb-0">Sets the auto-white-balance mode of the camera. Default: Auto</p>
                        </div>
                        <div class="col-auto">
                            <div class="custom-control custom-switch">
                                <select name="awb_mode" id="awb_mode"  onchange='pyview.subject._set_awb_mode($("#awb_mode").val())'>
                                  <option value='auto'        {% if pyview.subject.awb_mode == 'auto'        %}selected{%endif%}>Auto</option>
                                  <option value='off'         {% if pyview.subject.awb_mode == 'off'         %}selected{%endif%}>Off</option>
                                  <option value='sunlight'    {% if pyview.subject.awb_mode == 'sunlight'    %}selected{%endif%}>Sunlight</option>
                                  <option value='cloudy'      {% if pyview.subject.awb_mode == 'cloudy'      %}selected{%endif%}>Cloudy</option>
                                  <option value='shade'       {% if pyview.subject.awb_mode == 'shade'       %}selected{%endif%}>Shade</option>
                                  <option value='tungsten'    {% if pyview.subject.awb_mode == 'tungsten'    %}selected{%endif%}>Tungsten</option>
                                  <option value='fluorescent' {% if pyview.subject.awb_mode == 'fluorescent' %}selected{%endif%}>Fluorescent</option>
                                  <option value='incandescent'{% if pyview.subject.awb_mode == 'incandescent'%}selected{%endif%}>Incandescent</option>
                                  <option value='flash'       {% if pyview.subject.awb_mode == 'flash'       %}selected{%endif%}>Flash</option>
                                  <option value='horizon'     {% if pyview.subject.awb_mode == 'horizon'     %}selected{%endif%}>Horizon</option>
                                </select>
                                <span class="custom-control-label"></span>
                            </div>
                        </div>
                    </div>
                </div> 

            </div>
        </div>
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
                                <input style="width:100%" id="shutter_speed" type=number value="{{pyview.subject.shutter_speed}}" onchange='pyview.subject._set_shutter_speed($("#shutter_speed").val())'>
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
                                        <td>Shutter</td>
                                        {% for i in range(pyview.settings_scanner.segments) %}
                                            <td> {{ pyview.subject.per_segment_shutter_speeds[i] }} </td>
                                        {% endfor %}
                                        
                                    </tr>
                                    <tr>
                                        <td>Red</td>
                                        {% for i in range(pyview.settings_scanner.segments) %}
                                            <td> {{ pyview.subject.per_segment_awb_gains[i][0] }} </td>
                                        {% endfor %}
                                    </tr>
                                    <tr>
                                        <td>Blue</td>
                                        {% for i in range(pyview.settings_scanner.segments) %}
                                            <td> {{ pyview.subject.per_segment_awb_gains[i][1] }} </td>
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

