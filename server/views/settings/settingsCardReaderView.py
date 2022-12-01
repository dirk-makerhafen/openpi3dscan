from pyhtmlgui import ObservableDictView, PyHtmlView


class CardReaderSlotView(PyHtmlView):
    DOM_ELEMENT = "tr"
    TEMPLATE_STR = '''
     {% if pyview.subject.sdcard is not none %}
        <td> {{ pyview.subject.sdcard.size }}GB </td>
        <td {% if pyview.subject.status != "idle" %}style="color:green"{% endif %}> {{ pyview.subject.status }} </td>
        <td>                    
            <select {% if pyview.subject.status != "idle" %}disabled{% endif %}  id="{{pyview.uid}}_group" name="" >
                    <option {% if pyview.subject.sdcard.info_group == "camera" %}selected{% endif %} value="camera"> Camera </option>
                    <option {% if pyview.subject.sdcard.info_group == "projector" %}selected{% endif %} value="projector"> Projector </option>
                    <option {% if pyview.subject.sdcard.info_group == "light" %}selected{% endif %} value="light"> Light </option>
            </select> 
        </td>
        <td> <input placeholder="101" {% if pyview.subject.status != "idle" %}disabled{% endif %}  id="{{pyview.uid}}_id" value="{{pyview.subject.sdcard.info_id}}"></input></td>
        <td> <input placeholder="SEG1-CAM1" {% if pyview.subject.status != "idle" %}disabled{% endif %}  id="{{pyview.uid}}_name"  value="{{pyview.subject.sdcard.info_name}}"></input></td>
        <td>     
            <button {% if pyview.subject.status != "idle" %}disabled{% endif %} class="btn-small"  onclick='pyview.write_image(document.getElementById("{{pyview.uid}}_group").value, document.getElementById("{{pyview.uid}}_id").value, document.getElementById("{{pyview.uid}}_name").value);'>Write Image</button>
            <button {% if pyview.subject.status != "idle" %}disabled{% endif %} class="btn-small"  onclick='pyview.update_card(document.getElementById("{{pyview.uid}}_group").value, document.getElementById("{{pyview.uid}}_id").value, document.getElementById("{{pyview.uid}}_name").value);'>Update Card</button>
        </td>            
    {% else %}
        <td>No Card inserted</td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
    {% endif %}            
    '''

    def __init__(self, subject, parent, **kwargs):
        super().__init__(subject, parent, **kwargs)

    def write_image(self, group, dev_id, name):
        print("write image", group, dev_id, name)
        self.subject.write_image_task(group, dev_id, name)

    def update_card(self, group, dev_id, name):
        print("update_card", group, dev_id, name)
        self.subject.update_card_task(group, dev_id, name)


class CardReaderView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="Cardreader">
            <div class="row justify-content-center" style="width:100%">
                <div class="col-md-12">
                    <div class="list-group mb-5 shadow">
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Card Reader</div>
                            </div>
                        </div>
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-10">
                                    <strong class="mb-0">
                                        {% if pyview.subject.cardReaderSlots | length == 0 %}
                                            <p style="color:red">No reader connected<p>
                                        {% else %}
                                            <p style="color:green">Cardreader connected<p>
                                        {% endif %}
                                    </strong>
                                    <p class="text-muted mb-0">
                                        {% if pyview.subject.status != "idle" %}{{pyview.subject.status}}{%endif%}&nbsp;
                                     </p>
                                </div>
                                <div class="col-md-2">
                                   <button class="btn btnfw" {% if pyview.subject.status != "idle" %}disabled{%endif%}style="margin-right:5px" onclick='pyview.subject.reload_task();'> Reload </button>
                                </div>
                            </div>
                        </div>
                        <div class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-2">
                                    <strong class="mb-0">Cardreader Slots</strong>
                                </div>
                                <div class="col-md-10">
                                   <table style="width:100%;text-align:center">
                                        <thead>
                                            <tr>
                                                <th style="text-align:center">Size</th>
                                                <th style="text-align:center">Status</th>
                                                <th style="text-align:center">Type</th>
                                                <th style="text-align:center">ID</th>
                                                <th style="text-align:center">NAME</th>
                                                <th style="text-align:center">Action</th>
                                            </tr>
                                        </thead>    
                                        {{pyview.slotsView.render()}}                            
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
        self.slotsView = ObservableDictView(subject.cardReaderSlots, self, item_class=CardReaderSlotView)
        self.slotsView.DOM_ELEMENT = "tbody"

