from pyhtmlgui import PyHtmlView


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
                            <div class="col-md-5">
                                <strong class="mb-0">USB-Disks</strong>
                                <p class="text-muted mb-0">List of connected USB Disks</p>
                            </div>
                            <div class="col-md-5">
                                <table style="width:100%;text-align:center">
                                    <thead>
                                        <tr>
                                            <th style="text-align:center">Name</th>
                                            <th style="text-align:center">Status</th>
                                            <th style="text-align:center">Disk Size</th>
                                            <th style="text-align:center">Disk Free</th>
                                            <th style="text-align:center">Primary</th>
                                            <th style="text-align:center">Action</th>
                                        </tr>
                                    </thead>                                
                                    {% for disk in pyview.subject.disks %}
                                        <tr style="border-top: 1px solid lightgray;   line-height: 3em;">
                                            <td>{{disk.label}}</td>
                                            <td>{{disk.status}}</td>
                                            <td>{{disk.disk_total}}</td>
                                            <td>{{disk.disk_free}}</td>
                                            <td>{{disk.is_primary}}</td>
                                            <td>
                                                {% if disk.status == "Active" %}
                                                    <button class="btn btnfw" onclick="pyview.subject.load()">Eject</button>
                                                {% elif  disk.status == "" %} 
                                                    <button class="btn btnfw" onclick="pyview.subject.load()">Activate</button>
                                                {% endif %}  
                                                <button class="btn btnfw" onclick="pyview.set_as_primary()">Set as Primary</button>
                                            </td>
                                        </tr>
                                    {% endfor %}
                                </table>   
                            </div>
                            <div class="col-md-2" style="text-align:center">
                                {% if pyview.subject.status == "idle" %}
                                    <button class="btn btnfw" onclick="pyview.subject.load()">Reload</button>
                                {% else %}
                                    <p> {{pyview.subject.status }} </p>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                </div>
            </div>   
        </div>
    </div>   
    '''
