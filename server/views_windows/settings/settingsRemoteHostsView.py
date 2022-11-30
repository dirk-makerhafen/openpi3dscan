from pyhtmlgui import PyHtmlView, ObservableListView


class SettingsRemoteHostsView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="RemoteHosts">
        <div class="row justify-content-center" style="width:100%">
            <div class="col-md-12">
                <div class="list-group mb-5 shadow">
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Local Scanner</div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <strong class="mb-0">Hosts</strong>
                                <p class="text-muted mb-0">Directly receive tasks from scanner in same network</p>
                            </div>
                            <div class="col-md-4">
                            <table class="table">
                                {% for host in  pyview.subject.hosts %}
                                    <tr>
                                        <td><p class="h5" style="margin-left: 5px;">{{host}}</p></td>
                                        <td><button class="btn btnfw" onclick='pyview.subject.remove_host("{{host}}")'>Remove</button></td>
                                    </tr>
                                {% endfor %}
                                <tr>
                                <td> <input  class="form-control" placeholder="myscanner.local" id="newhost" type="text"></input></td>
                                <td> <button class="btn btnfw" onclick='pyview.subject.add_host($("#newhost").val())'>Add</button> </td>   
                                </tr>
                            </table>
                            </div>
                        </div>
                    </div>
                                      
                </div>
            </div>   
        </div>
    </div>
    '''
    def __init__(self, subject, parent, **kwargs):
        super().__init__(subject, parent, **kwargs)


