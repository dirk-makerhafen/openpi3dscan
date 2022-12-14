from pyhtmlgui import PyHtmlView


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
                                <p class="text-muted mb-0">Wireless network name. Use <i>name;address</i> if you need to force a specific AP address</p>
                            </div>
                            <div class="col-md-2">
                                <input class="form-control" id="wireless_ssid" value="{{pyview.subject.ssid}}" type="text"/>
                            </div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-10">
                                <strong class="mb-0">Password</strong>
                                <p class="text-muted mb-0">Wireless network password</p>
                            </div>
                            <div class="col-md-2">
                                <input class="form-control" id="wireless_password" value="{{pyview.subject.password}}" type="text"/>
                            </div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-10">
                                <strong class="mb-0">Save changes</strong>
                                <p class="text-muted mb-0">Apply new wlan settings</p>
                            </div>
                            <div class="col-md-2">
                               <button class="btn btnfw" onclick='pyview.subject.apply($("#wireless_ssid").val(), $("#wireless_password").val());'> Apply Changes </button>
                            </div>
                        </div>
                    </div>    
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <strong class="mb-0">Status</strong>
                                <p class="text-muted mb-0">Wireless network status</p>
                            </div>
                            
                            <div class="col-md-2 h5" style="text-align:center">
                                {% if pyview.subject.status == "not_connected" %}NOT Connected{% endif %}
                                {% if pyview.subject.status == "connecting" %}Connecting, please wait..{% endif %}
                                {% if pyview.subject.status == "configure" %}Configuring network..{% endif %}
                                {% if pyview.subject.status == "connected" %}Connected<br>IP: {{pyview.subject.ip}}{% endif %}
                                {% if pyview.subject.status == "checking" %}Checking Status{% endif %}
                            </div>
                            <div class="col-md-2">
                                {% if pyview.subject.status == "checking" or pyview.subject.status == "configure" or pyview.subject.status == "connecting" %}
                                    <button class="btn btnfw" disabled style="margin-right:5px" > Working </button>
                                {% else %}
                                    <button class="btn btnfw " style="margin-right:5px" onclick='pyview.subject.get_connection_status();'> Get Status </button>
                                {% endif %}
                            </div>
                        </div>
                    </div>   
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-5">
                                <strong class="mb-0">Wireless scan</strong>
                                <p class="text-muted mb-0">Search for available wireless networks.</p>
                            </div>
                            <div class="col-md-5">
                                <div class="custom-control custom-switch">
                                    {% if pyview.subject.wireless_networks|length > 0 %}
                                        <table style="width:100%;text-align:center;margin-top:10px">
                                            <thead>
                                            <tr>
                                                <td>Name</td>
                                                <td>Address</td>
                                                <td>Frequency</td>
                                                <td>Channel</td>
                                                <td>Signal</td>
                                            </tr>
                                            </thead>
                                            {% for wireless_network in pyview.subject.wireless_networks %}
                                                <tr style="border-top: 1px solid lightgray;   line-height: 3em;">
                                                    <td> {{wireless_network.ssid}} </td>
                                                    <td> {{wireless_network.bssid}} </td>
                                                    <td> {{wireless_network.frequency}} </td>
                                                    <td> {{wireless_network.channel}} </td>
                                                    <td> {{wireless_network.signal}}% </td>
                                                </tr>
                                            {% endfor %}
                                        </table> 
                                    {% endif %}                
                                </div>
                            </div>
                            <div class="col-md-2">
                                {% if pyview.subject.scan_worker == None %}
                                    <button class="btn btnfw" style="margin-right:5px" onclick='pyview.subject.scan();'> Scan </button>
                                    {% if  pyview.subject.wireless_networks|length > 0 %}
                                        <button class="btn btnfw" style="margin-right:5px;margin-top:5px" onclick='pyview.subject.clear();'> Clear </button>
                                    {% endif %}
                                {% else %}
                                    <button class="btn btnfw" disabled style="margin-right:5px" > Scanning </button>
                                {% endif %}
                            </div>
                        </div>
                    </div>                               
                </div>
            </div>   
        </div>
    </div>    
    '''

