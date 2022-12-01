from pyhtmlgui import PyHtmlView


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
                        <div class="col-md-9">
                            <strong class="mb-0">Firmware image</strong>
                            <p class="text-muted mb-0">Select firmware image to install to new SD-Cards</p>
                        </div>
                        <div class="col-md-3">
                            <div class="custom-control custom-switch">
                                <select  class="form-control btnfw" name="image" id="image"  onchange='pyview.subject.set_image($("#image").val())'>
                                    {% for image in pyview.subject.image_files %}
                                        <option value="{{image}}" {% if pyview.subject.current_image == image   %}selected{%endif%}>{{image}}</option>
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
                                            <td> {{image}} </td>
                                            <td> <button class="btn btn-warning" style="margin-right:5px" onclick='pyview.subject.delete_image({{image}});'> Delete </button> </td>
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
