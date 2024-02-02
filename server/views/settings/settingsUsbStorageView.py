from pyhtmlgui import PyHtmlView,ObservableListView


class UsbDiskView(PyHtmlView):
    TEMPLATE_STR = '''
        <tr style="border-top: 1px solid lightgray;   line-height: 3em;">
        <td>{{pyview.subject.label}}</td>
        <td>{{pyview.subject.status}}</td>
        <td>{{pyview.subject.disk_free}} / {{pyview.subject.disk_total}}</td>
        <td>{{pyview.subject.shots_loaded}} / {{pyview.subject.shots_available}}</td>
        <td>{{pyview.subject.oldest_shot}} / {{pyview.subject.newest_shot}}</td>
        <td>{{pyview.subject.is_primary}}</td>
        <td>
            {% if pyview.subject.status == "Active" %}
                <button style="width:50%" class="btn btnfw" onclick="pyview.subject.unload()">Eject</button>
            {% elif  pyview.subject.status == "" %} 
                <button style="width:50%"  class="btn btnfw" onclick="pyview.subject.load()">Activate</button>
            {% endif %}  
            {% if pyview.subject.is_primary == false %}
                <button style="width:50%" class="btn btnfw" onclick="pyview.subject.set_as_primary()">Set as Primary</button>
            {% endif %}  
        </td>
        </tr>
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
                            <div class="col-md-3">
                                <strong class="mb-0">USB-Disks</strong>
                                <p class="text-muted mb-0">List of connected USB Disks</p>
                                {% if pyview.subject.status == "idle" %}
                                    <button class="btn btnfw" onclick="pyview.subject.load()">Reload</button>
                                {% else %}
                                    <p>{{pyview.subject.status }}</p>
                                {% endif %}
                            </div>
                            <div class="col-md-9">
                                <table style="width:100%;text-align:center">
                                    <thead>
                                        <tr>
                                            <th style="text-align:center">Name</th>
                                            <th style="text-align:center">Status</th>
                                            <th style="text-align:center">Disk Free / Size</th>
                                            <th style="text-align:center">Shots Loaded / Avail</th>
                                            <th style="text-align:center">Shots From / To</th>
                                            <th style="text-align:center">Primary</th>
                                            <th style="text-align:center">Action</th>
                                        </tr>
                                    </thead>                                
                                    {{ pyview.disks.render() }}
                                </table>   
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
        self.disks = ObservableListView(subject=subject.disks, parent=self, item_class=UsbDiskView, dom_element="tbody")
