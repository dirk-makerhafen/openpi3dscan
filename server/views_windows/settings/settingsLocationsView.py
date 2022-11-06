from pyhtmlgui import PyHtmlView, ObservableListView


class SettingsLocationView(PyHtmlView):
    DOM_ELEMENT = "tr"
    TEMPLATE_STR = '''    
    <td> <input id="location_{{pyview.uid}}" type="text" value="{{pyview.subject.location}}" onchange='pyview.subject.set_location($("#location_{{pyview.uid}}").val())'> </td>
    <td> <input id="segments_{{pyview.uid}}" type="number" min=2 max=128 step=1 value="{{pyview.subject.segments}}" onchange='pyview.subject.set_segments($("#segments_{{pyview.uid}}").val())'> </td>
    <td> <input id="cameras_per_segment_{{pyview.uid}}" type="number" min=2 max=128 step=1 value="{{pyview.subject.cameras_per_segment}}" onchange='pyview.subject.set_cameras_per_segment($("#cameras_per_segment_{{pyview.uid}}").val())'> </td>
    <td> 
        <select id="camera_rotation_{{pyview.uid}}"  onchange='pyview.subject.set_camera_rotation($("#camera_rotation_{{pyview.uid}}").val())'>
            <option value=0   {% if pyview.subject.camera_rotation == 0   %}selected{%endif%}>   0 </option>
            <option value=90  {% if pyview.subject.camera_rotation == 90  %}selected{%endif%}>  90 </option>
            <option value=180 {% if pyview.subject.camera_rotation == 180 %}selected{%endif%}> 180 </option>
            <option value=270 {% if pyview.subject.camera_rotation == 270 %}selected{%endif%}> 270 </option>
        </select>  
     </td>
    <td> 
        <select id="camera_one_position_{{pyview.uid}}"  onchange='pyview.subject.set_camera_one_position($("#camera_one_position_{{pyview.uid}}").val())'>
            <option value="top"    {% if pyview.subject.camera_one_position == "top"    %} selected {%endif%}> Top </option>
            <option value="bottom" {% if pyview.subject.camera_one_position == "bottom" %} selected {%endif%}> Bottom </option>
        </select>  
     </td>
    <td> 
        <textarea rows=8 id="marker_distances_{{pyview.uid}}"  style="white-space: pre-wrap;width:100%" onchange='pyview.subject.set_markers($("#marker_distances_{{pyview.uid}}").val())'>{{pyview.subject.markers}}</textarea>
     </td>
    <td>
        <input  style="width:100%;text-align:center" id="region_diameter_{{pyview.uid}}" type="number" step="0.01" value="{{pyview.subject.diameter}}" onchange='pyview.subject.set_diameter($("#region_diameter_{{pyview.uid}}").val())'>
    </td>
    <td> <input  style="width:100%;text-align:center" id="region_height_{{pyview.uid}}" type="number" step="0.01" value="{{pyview.subject.height}}" onchange='pyview.subject.set_height($("#region_height_{{pyview.uid}}").val())'></td>
    
    '''


class SettingsLocationsView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="SystemRestart">
        <div class="row justify-content-center" style="width:100%">
            <div class="col-md-12">
                <div class="list-group mb-5 shadow">
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Hardware Setup</div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-10">
                                <strong class="mb-0">Location</strong>
                                <p class="text-muted mb-0">Unique scanner location name</p>
                            </div>
                            <div class="col-md-2">
                                <div class="custom-control custom-switch">
                                <button onclick="pyview.subject.new_location()">New Location</button>
                                </div>
                            </div>
                        </div>
                    </div> 
                     <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-12">
                                <table id="devicetable" class="table">
                                    <thead>
                                        <tr>
                                            <th>Location</th>
                                            <th>Segments</th>
                                            <th>Cameras/Seg</th>
                                            <th>Rotation</th>
                                            <th>Cam1 Pos</th>
                                            <th>Markers</th>
                                            <th>Diameter</th>
                                            <th>Height</th>
                                        </tr>
                                    </thead>
                                   {{ pyview.locations.render() }}  
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
        self.locations = ObservableListView(subject=subject.locations, parent=self, item_class=SettingsLocationView, dom_element="tbody")

