from pyhtmlgui import PyHtmlView


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
                        <div class="col-md-10"> 
                            <strong class="mb-0">Startup Delay</strong>
                            <p class="text-muted mb-0">Delay between clicking and actually taking the images. Default: 3 Seconds</p>
                         </div>
                        <div class="col-md-2" style="text-align:center"> 
                            <input id="startup_delay_{{pyview.uid}}" value={{pyview.subject.startup_delay}} onchange='pyview.subject.set_startup_delay($("#startup_delay_{{pyview.uid}}").val())' type="number" min="2" max="10" />
                        </div>
                    </div>
                </div>
                <div class="list-group-item">
                    <div class="row align-items-center">
                        <div class="col-md-10"> 
                            <strong class="mb-0">Second Image Delay</strong>
                            <p class="text-muted mb-0">Delay between first and second image, in steps of 110ms. Default: 0</p>
                         </div>
                        <div class="col-md-2" style="text-align:center"> 
                            <input id="image_delay_{{pyview.uid}}" value={{pyview.subject.image_delay}} onchange='pyview.subject.set_image_delay($("#image_delay_{{pyview.uid}}").val())' type="number"  min="0" max="10"/>
                        </div>
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

