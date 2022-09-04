from pyhtmlgui import PyHtmlView, ObservableDictView


class CardReaderSlotView(PyHtmlView):
    DOM_ELEMENT_CLASS = "CardReaderSlotView col-md-12"
    TEMPLATE_STR = '''
        {% if pyview.subject.sdcard is none %}
            <div class="row" style="font-weight:bold;  ont-size: 1.1em;padding-top: 5px;padding-bottom: 5px">
                <div class="col-md-12"> 
                    No card
                </div>
            </div>
        {% else %}
            <div class="row" style="font-weight:bold;  font-size: 1.1em;padding-top: 5px;padding-bottom: 5px">
                <div class="col-md-4"> SD-Card </div>
                <div class="col-md-3"> {{ pyview.subject.sdcard.size }}GB </div>
                <div class="col-md-4"> {{ pyview.subject.status }} </div>
            </div>
            <div class="row">
                <div class="col-md-3"> 
                    <select {% if pyview.subject.status != "idle" %}disabled{% endif %}  id="{{pyview.uid}}_group" name="" >
                        <option {% if pyview.subject.sdcard.info_group == "camera" %}selected{% endif %} value="camera"> Camera </option>
                        <option {% if pyview.subject.sdcard.info_group == "projector" %}selected{% endif %} value="projector"> Projector </option>
                        <option {% if pyview.subject.sdcard.info_group == "light" %}selected{% endif %} value="light"> Light </option>
                    </select>
                </div>
                <div class="col-md-4"> <input {% if pyview.subject.status != "idle" %}disabled{% endif %}  id="{{pyview.uid}}_id"  style="width:100%" value="{{pyview.subject.sdcard.info_id}}"></input></div>
                <div class="col-md-5"> <input {% if pyview.subject.status != "idle" %}disabled{% endif %}  id="{{pyview.uid}}_name"  style="width:100%" value="{{pyview.subject.sdcard.info_name}}"></input></div>
                <div class="col-md-12" style="padding-top:10px;padding-bottom:10px"> 
                    <button {% if pyview.subject.status != "idle" %}disabled{% endif %} class="btn-small" style="width:49%" onclick='pyview.write_image(document.getElementById("{{pyview.uid}}_group").value, document.getElementById("{{pyview.uid}}_id").value, document.getElementById("{{pyview.uid}}_name").value);'>Write</button>
                    <button {% if pyview.subject.status != "idle" %}disabled{% endif %} class="btn-small" style="width:49%" onclick='pyview.update_card(document.getElementById("{{pyview.uid}}_group").value, document.getElementById("{{pyview.uid}}_id").value, document.getElementById("{{pyview.uid}}_name").value);'>Update</button>
                </div>
            </div>
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
    DOM_ELEMENT_CLASS = "CardReaderView row"
    TEMPLATE_STR = '''
        <div class="col-md-12">
            <div class="row" style="font-size:1.1em">
                <div class="col-md-10">
                    {% if pyview.subject.cardReaderSlots | length == 0 %}
                        <p style="color:red">No reader connected<p>
                    {% else %}
                        <p style="color:green">Cardreader connected<p>
                    {% endif %}
                </div>
                <div class="col-md-2">
                    {% if pyview.subject.status == "idle" %}
                        <i class="fa-solid fa-arrows-rotate" onclick="pyview.subject.reload_task()"></i>
                    {% else %}
                        <i class="fa-solid fa-arrows-rotate" style="color:gray"></i>
                    {% endif %}
                </div>
            </div>
            {{pyview.slotsView.render()}}
        </div>
    '''
    def __init__(self, subject, parent, **kwargs):
        super().__init__(subject, parent, **kwargs)
        self.slotsView = ObservableDictView(subject.cardReaderSlots, self, item_class=CardReaderSlotView)
        self.slotsView.DOM_ELEMENT_CLASS = "ObservableDictView row"