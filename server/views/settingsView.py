from pyhtmlgui import PyHtmlView

from app.tasks.task_ShutterBalance import TaskShutterBalanceInstance
from app.tasks.task_UpdateServer import TaskUpdateServerInstance
from app.tasks.task_Whitebalance import TaskWhitebalanceInstance


class WirelessSettingsView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="Wireless">
            <div class="row justify-content-center" style="width:100%">
                <div class="col-md-12">
                    <div class="list-group mb-5 shadow">
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Wireless Network</div>
                            </div>
                        </div>
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-10">
                                    <strong class="mb-0">Name</strong>
                                    <p class="text-muted mb-0">Wireless network name</p>
                                </div>
                                <div class="col-auto">
                                    <input id="wireless_ssid" value="{{pyview.subject.ssid}}" type="text"/>
                                </div>
                            </div>
                        </div>
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-10">
                                    <strong class="mb-0">Password</strong>
                                    <p class="text-muted mb-0">Wireless network password</p>
                                </div>
                                <div class="col-auto">
                                    <input id="wireless_password" value="{{pyview.subject.password}}" type="text"/>
                                </div>
                            </div>
                        </div>
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-10">
                                    <strong class="mb-0">Save Changes</strong>
                                    <p class="text-muted mb-0">Apply new wlan settings</p>
                                </div>
                                <div class="col-auto">
                                   <button class="btn " style="margin-right:5px" onclick='pyview.subject.apply($("#wireless_ssid").val(), $("#wireless_password").val());'> Apply Changes </button>
                                </div>
                            </div>
                        </div>    
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-8">
                                    <strong class="mb-0">Status</strong>
                                    <p class="text-muted mb-0">Wireless network status</p>
                                </div>
                                <div class="col-md-2">
                                   <button class="btn " style="margin-right:5px" onclick='pyview.subject.get_connection_status();'> Get Status </button>
                                </div>
                                <div class="col-md-2">
                                    {% if pyview.subject.status == "not_connected" %}NOT Connected{% endif %}
                                    {% if pyview.subject.status == "connecting" %}Connecting, please wait..{% endif %}
                                    {% if pyview.subject.status == "configure" %}Configuring network..{% endif %}
                                    {% if pyview.subject.status == "connected" %}Connected<br>IP: {{pyview.subject.ip}}{% endif %}
                                    {% if pyview.subject.status == "checking" %}Checking Status{% endif %}
                                </div>
                            </div>
                        </div>                                  
                    </div>
                </div>   
            </div>
        </div>    
    '''

class TaskShutterBalanceView(PyHtmlView):
    TEMPLATE_STR = '''
        {% if pyview.subject.status == "idle" %} 
            <button class="btn" onclick='pyview.subject.run();'> Balance </button>
        {% else %}
            <p class="btn">Balancing</p>
        {% endif %}
    '''

class TaskWhitebalanceView(PyHtmlView):
    TEMPLATE_STR = '''
        {% if pyview.subject.status == "idle" %} 
            <button class="btn" onclick='pyview.subject.run();'> Balance </button>
        {% else %}
            <p class="btn">Balancing</p>
        {% endif %}
    '''

class TaskUpdateServerView(PyHtmlView):
    TEMPLATE_STR = '''
        {% if pyview.subject.status == "idle" %} 
            <button class="btn" onclick='pyview.subject.run();'> Update Server </button>
        {% else %}
            <p class="btn">{{pyview.subject.status}}</p>
        {% endif %}
    '''

class UsbStorageView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="Storage">
            <div class="row justify-content-center" style="width:100%">
                <div class="col-md-12">
                    <div class="list-group mb-5 shadow">
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Storage</div>
                            </div>
                        </div>
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-6">
                                    <strong class="mb-0">USB-Disks</strong>
                                    <p class="text-muted mb-0">List of connected USB Disks</p>
                                </div>
                                <div class="col-md-6">
                                   <table style="width:100%;text-align:center">
                                    <thead>
                                        <tr>
                                            <th style="text-align:center">Name</th>
                                            <th style="text-align:center">Type</th>
                                            <th style="text-align:center">Disk Size</th>
                                            <th style="text-align:center">Disk Free</th>
                                        </tr>
                                    </thead>                                
                                        {% for disk in pyview.subject.disks %}
                                            <tr style="border-top: 1px solid lightgray;   line-height: 3em;">
                                                <td>{{disk.LABEL}}</td>
                                                <td>{{disk.FSTYPE}}</td>
                                                <td>{{disk.disk_total}}</td>
                                                <td>{{disk.disk_free}}</td>
                                            </tr>
                                        {% endfor %}
                                    </table>   
                                </div>
                            </div>
                        </div>
                    </div>
                </div>   
            </div>
        </div>   
    '''

class FirmwareSettingsView(PyHtmlView):
    DOM_ELEMENT_CLASS = "FirmwareSettingsView"
    TEMPLATE_STR = '''
        <div class="row justify-content-center" style="width: 100%">
            <div class="col-md-12">
                <div class="list-group mb-5 shadow">
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Legacy Firmware</div>
                        </div>
                    </div>
                    
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-10">
                                <strong class="mb-0">Firmware image</strong>
                                <p class="text-muted mb-0">Select firmware image to install to new SD-Cards</p>
                            </div>
                            <div class="col-auto">
                                <div class="custom-control custom-switch">
                                    <select name="image" id="image"  onchange='pyview.subject.set_image($("#image").val())'>
                                        {% for image in pyview.subject.image_files %}
                                            <option value="image" {% if pyview.subject.current_image == image   %}selected{%endif%}>{{image}}</option>
                                        {% endfor %}
                                    </select> 
                                    <span class="custom-control-label"></span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <strong class="mb-0">Available images</strong>
                                <p class="text-muted mb-0">List of available firmware images</p>
                            </div>

                            <div class="col-md-4">
                                <div class="custom-control custom-switch">
                                    <table style="width:100%;text-align:center">
                                        {% for image in pyview.subject.image_files %}
                                            <tr style="border-top: 1px solid lightgray;   line-height: 3em;">
                                                <td>{{image}}</td>
                                                <td>
                                                    <button class="btn btn-warning" style="margin-right:5px" onclick='pyview.subject.delete_image({{image}});'> Delete </button>
                                                </td>
                                            </tr>
                                        {% endfor %}
                                    </table>                 
                                    <span class="custom-control-label"></span>
                                </div>
                            </div>
                        </div>
                    </div>
 
                </div>
            </div>   
        </div>

    '''

    def __init__(self, subject, parent):
        super().__init__(subject, parent)

class SequenceSettingsView(PyHtmlView):
    DOM_ELEMENT_CLASS = " SequenceSettingsView"
    TEMPLATE_STR = '''
        <div class="row justify-content-center" style="width:100%">
            <div class="col-md-12">
                <div class="list-group mb-5 shadow">
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Image Capture Settings</div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-8"> 
                                <strong class="mb-0">Image</strong>
                                <p class="text-muted mb-0">Two images are generated at any shot</p>
                             </div>
                            <div class="col-md-2" style="text-align:center"> First Shot </div>
                            <div class="col-md-2" style="text-align:center"> Second Shot </div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <strong class="mb-0">Enable Projection</strong>
                                <p class="text-muted mb-0">Enable projectors for this image</p>
                            </div>
                            <div class="col-md-2" style="text-align:center">
                                <div class="custom-control custom-switch">   
                                    <input id="projection_image1_{{pyview.uid}}"  type="checkbox" {% if pyview.subject.image1.projection == True %}checked{% endif %} onclick='pyview.subject.image1._set_projection($("#projection_image1_{{pyview.uid}}").prop("checked") === true)'>
                                    <span class="custom-control-label"></span>
                                </div>
                            </div>
                            <div class="col-md-2" style="text-align:center">
                                <div class="custom-control custom-switch">   
                                    <input id="projection_image2_{{pyview.uid}}"  type="checkbox" {% if pyview.subject.image2.projection == True %}checked{% endif %} onclick='pyview.subject.image2._set_projection($("#projection_image2_{{pyview.uid}}").prop("checked") === true)'>                                 
                                    <span class="custom-control-label"></span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <strong class="mb-0">Light</strong>
                                <p class="text-muted mb-0">Adjust lighting for this shot. Values from 1 to 100 set Light to 1-100% of max light. Values from 0-1 set light relative to current value. Set to -1 for last value set in live view</p>
                            </div>
                            <div class="col-md-2" style="text-align:center">
                                <div class="custom-control custom-switch">
                                   <input id="light_image1_{{pyview.uid}}" value="{{pyview.subject.image1.light}}" onchange='pyview.subject.image1._set_light($("#light_image1_{{pyview.uid}}").val())' type="number"/>
                                    <span class="custom-control-label"></span>
                                </div>
                            </div>
                            <div class="col-md-2" style="text-align:center">
                                <div class="custom-control custom-switch">
                                   <input id="light_image2_{{pyview.uid}}" value="{{pyview.subject.image2.light}}" onchange='pyview.subject.image2._set_light($("#light_image2_{{pyview.uid}}").val())' type="number"/>
                                    <span class="custom-control-label"></span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <strong class="mb-0">Timing</strong>
                                <p class="text-muted mb-0">Switching offset in ms for light and projection</p>
                            </div>
                            <div class="col-md-2" style="text-align:center">
                                <div class="custom-control custom-switch">
                                    <input id="offset_image1_{{pyview.uid}}" value="{{pyview.subject.image1.offset}}" onchange='pyview.subject.image1._set_offset($("#offset_image1_{{pyview.uid}}").val())' type="number"/>
                                    <span class="custom-control-label"></span>
                                </div>
                            </div>
                            <div class="col-md-2" style="text-align:center">
                                <div class="custom-control custom-switch">
                                    <input id="offset_image2_{{pyview.uid}}" value="{{pyview.subject.image2.offset}}" onchange='pyview.subject.image2._set_offset($("#offset_image2_{{pyview.uid}}").val())' type="number"/>
                                    <span class="custom-control-label"></span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>   
        </div>
   
    '''

    def __init__(self, subject, parent):
        super().__init__(subject, parent)

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
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <strong class="mb-0">Shutter speed (0=Auto)</strong>
                                <p class="text-muted mb-0">Set Shutter speed for cameras, or select balance to select automatically.</p>
                            </div>
                            <div class="col-md-2">{{pyview.shutterbalance_view.render()}}</div>
                            <div class="col-md-2">
                                <div class="custom-control custom-switch">
                                    <input id="shutter_speed" type=number value="{{pyview.subject.shutter_speed}}" onchange='pyview.subject._set_shutter_speed($("#shutter_speed").val())'>
                                    <span class="custom-control-label"></span>
                                </div>
                            </div>
                        </div>
                    </div> 
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <strong class="mb-0">Whitebalance gains</strong>
                                <p class="text-muted mb-0">Set whitebalance gains for cameras, or select balance to select automatically.</p>
                            </div>
                            <div class="col-md-2">{{pyview.whitebalance_view.render()}}</div>
                            <div class="col-md-2">
                                <div class="custom-control custom-switch">
                                    <input id="awb_gain_red" type=number value="{{pyview.subject.awb_gains[0]}}" onchange='pyview._set_awb_gain_red($("#awb_gain_red").val())'>
                                    <lable class="custom-control-label" style="color:red" for="awb_gain_red">red</lable>
                                    <input id="awb_gain_blue" type=number value="{{pyview.subject.awb_gains[1]}}" onchange='pyview._set_awb_gain_blue($("#awb_gain_blue").val())'>
                                    <lable class="custom-control-label" style="color:blue" for="awb_gain_blue">blue</lable>
                                </div>
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

    def _set_awb_gain_red(self, value):
        gains = self.subject.awb_gains
        gains[0] = float(value)
        self.subject.awb_gains = gains

    def _set_awb_gain_blue(self, value):
        gains = self.subject.awb_gains
        gains[1] = float(value)
        self.subject.awb_gains = gains

class RealityCaptureView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="RealityCapture">
            <div class="row justify-content-center" style="width:100%">
                <div class="col-md-12">
                    <div class="list-group mb-5 shadow">
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">RealityCapture</div>
                            </div>
                        </div>
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-10">
                                    <strong class="mb-0">RealityCapture Automation Software</strong>
                                    <p class="text-muted mb-0">Software package to automate RealityCapture. Download, unzip, run process.exe </p>
                                </div>
                                <div class="col-auto">
                                    <div class="custom-control custom-switch">
                                        <a href="/windows_pack.zip">DOWNLOAD</a>
                                        <span class="custom-control-label"></span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>   
            </div>
        </div>
    '''

class RebootShutdownView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="SystemRestart">
            <div class="row justify-content-center" style="width:100%">
                <div class="col-md-12">
                    <div class="list-group mb-5 shadow">
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Shutdown/Reboot Server</div>
                            </div>
                        </div>
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-10">
                                    <strong class="mb-0">Reboot</strong>
                                    <p class="text-muted mb-0">Reboot server, this will take 1-2 minutes</p>
                                </div>
                                <div class="col-auto">
                                    {% if pyview.subject.status == "active"%}
                                        <button class="btn " style="margin-right:5px" onclick='pyview.subject.reboot()'> Reboot </button>
                                    {% else %}
                                        <p>{{pyview.subject.status}} active</p>
                                    {% endif %}
                                </div>
                            </div>
                        </div>
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-10">
                                    <strong class="mb-0">Shutdown</strong>
                                    <p class="text-muted mb-0">Shutdown Server</p>
                                </div>
                                <div class="col-auto">
                                    {% if pyview.subject.status == "active" %}
                                        <button class="btn " style="margin-right:5px" onclick='pyview.subject.shutdown();'> Shutdown </button>
                                     {% else %}
                                        <p>{{pyview.subject.status}} active</p>
                                    {% endif %}
                                </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>   
            </div>
        </div>    

   
    '''


class SettingsView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="main">
    
        {{pyview.cameraSettingsView.render()}}
    
        {{pyview.sequenceSettingsSpeedView.render()}}  
    
        {{pyview.firmwareSettingsView.render()}}  
          
        {{pyview.wirelessSettingsView.render()}}  
        
        {{pyview.realityCaptureView.render()}}  
        
        {{pyview.usbStorageView.render()}}  
          
        <div class="System">
            <div class="row justify-content-center" style="width:100%">
                <div class="col-md-12">
                    <div class="list-group mb-5 shadow">
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Openpi3dscan</div>
                            </div>
                        </div>
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-10">
                                    <strong class="mb-0">Version</strong>
                                    <p class="text-muted mb-0">Current server version</p>
                                </div>
                                <div class="col-auto">
                                    {{pyview.subject.settings.VERSION}}
                                </div>
                            </div>
                        </div>
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-10">
                                    <strong class="mb-0">Online Updates</strong>
                                    <p class="text-muted mb-0">Check for updates and install if available. Server will reboot after updates are installed.</p>
                                </div>
                                <div class="col-auto">
                                    {{pyview.updateServerView.render()}}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>   
            </div>
        </div>    

        {{pyview.rebootShutdownView.render()}}  

 
    </div> 
    
    '''

    def __init__(self, subject, parent):
        super().__init__(subject, parent)

        self.sequenceSettingsSpeedView = SequenceSettingsView(self.subject.settings.sequenceSettingsSpeed, self)
        self.cameraSettingsView = CameraSettingsView(self.subject.settings.cameraSettings, self)
        self.firmwareSettingsView = FirmwareSettingsView(self.subject.settings.firmwareSettings, self)
        self.wirelessSettingsView = WirelessSettingsView(self.subject.settings.wirelessSettings, self)
        self.updateServerView = TaskUpdateServerView(TaskUpdateServerInstance(), self)
        self.realityCaptureView = RealityCaptureView(self.subject, self)
        self.usbStorageView = UsbStorageView(self.subject.usbDisks, self)
        self.rebootShutdownView = RebootShutdownView(self.subject, self)