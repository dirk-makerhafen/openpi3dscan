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
                                <div class="col-md-6">
                                    <strong class="mb-0">USB-Disks</strong>
                                    <p class="text-muted mb-0">List of connected USB Disks</p>
                                </div>
                                <div class="col-md-1">
                                {% if pyview.subject.status == "idle" %}
                                    <button class="btn" onclick="pyview.subject.load()">Reload</button>
                                {% else %}
                                    {{pyview.subject.status }}
                                {% endif %}

                                </div>
                                <div class="col-md-5">
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
                                                <td>{{disk.label}}</td>
                                                <td>{{disk.fstype}}</td>
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
