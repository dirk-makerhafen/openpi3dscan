import os
from pyhtmlgui import PyHtmlView, ObservableListView, ObservableList



class ShotFilesModelFilesView(PyHtmlView):
    TEMPLATE_STR = '''
    
    <div class="ModelFiles">
        <div class="row justify-content-center" style="width:100%">
            <div class="col-md-12">
                <div class="list-group mb-5 shadow">
                    <div class="list-group-item">
                        <div class="row align-items-center" style="border-bottom: 1px solid lightgray;">
                            <div class="col-md-8 h3" >
                                Model Files
                            </div>
                            {% if pyview.settingsInstance.realityCaptureSettings.settingsDefaultModelSets.default_models | length != 0 %}
                                <div class="col-md-2"">
                                    <select style="margin-top:10px" class="form-control" name="set_name" id="set_name">
                                        {% for set_name in pyview.settingsInstance.realityCaptureSettings.settingsDefaultModelSets.get_set_names() %}
                                            <option value="{{set_name}}">{{set_name}}</option>
                                        {% endfor %}
                                    </select>
                                </div>
                                <div class="col-md-2">
                                    <button class="btn btn-success btnfw" style="margin-right:5px;margin-top:10px" onclick='pyview.parent.subject.create_models_from_set($("#set_name").val());'> Create Models </button>
                                </div>
                            {% endif %}    
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-1 h5" style="text-align:center;font-weight:bold">Type</div>
                            <div class="col-md-1 h5" style="text-align:center;font-weight:bold;width:11.1%">Reconstruction Quality</div>
                            <div class="col-md-1 h5" style="text-align:center;font-weight:bold;width:11.1%">Export Quality</div>
                            <div class="col-md-1 h5" style="text-align:center;font-weight:bold;width:11.1%">Mesh from</div>
                            <div class="col-md-1 h5" style="text-align:center;font-weight:bold">Textures</div>
                            <div class="col-md-1 h5" style="text-align:center;font-weight:bold">Lit</div>
                            <div class="col-md-3 h5" style="text-align:center;font-weight:bold">File</div>
                            <div class="col-md-2 h5" style="text-align:center;font-weight:bold">Action</div>
                        </div>
                        {{pyview.filesListView.render()}}     
                        <div class="row" style="margin-top:10px">    
                            <div class="col-md-1" style="text-align:center">
                                <select style="" class="form-control" name="filetype" id="filetype" onchange='var v=$("#filetype").val();
                                   if(v=="holobox"){ 
                                        $("#dh").text("High, 60 Fps");
                                        $("#dm").text("Normal, 48 Fps");
                                        $("#dl").text("Low, 24 Fps");
                                   }else{
                                     if(v=="webp"||v=="gif"){ 
                                        $("#dh").text("High, 720x1280");
                                        $("#dm").text("Normal, 576x1024");
                                        $("#dl").text("Low, 450x800");
                                     }else{
                                        $("#dh").text("High, 4M");
                                        $("#dm").text("Normal, 1M");
                                        $("#dl").text("Low, 500K");
                                     }
                                   };
                                   if(v=="glb"||v=="gif"||v=="webp"||v=="holobox"){ $("#lit_unlit").prop("disabled", false); }else{ $("#lit_unlit").prop("disabled", true);$("#lit_unlit")[0].checked = true; }'>
                                    <option value="obj">OBJ</option>
                                    <option value="stl">STL</option>
                                    <option value="3mf">3MF</option>
                                    <option value="glb">GLB</option>
                                    <option value="fbx">FBX</option>
                                    <option value="rcproj">RCPROJ</option>
                                    <option value="gif">GIF</option>
                                    <option value="webp">WebP</option>
                                    <option value="holobox">Holobox Video</option>
                                </select>
                            </div>
                            <div class="col-md-1" style="text-align:center;width:11.1%">
                                <select style="" class="form-control" name="reconstruction_quality" id="reconstruction_quality">
                                    <option value="high"   {% if pyview.settingsInstance.realityCaptureSettings.default_reconstruction_quality == "high"    %}selected{% endif %} >High</option>
                                    <option value="normal" {% if pyview.settingsInstance.realityCaptureSettings.default_reconstruction_quality == "normal"  %}selected{% endif %}>Normal</option>
                                    <option value="preview"{% if pyview.settingsInstance.realityCaptureSettings.default_reconstruction_quality == "preview" %}selected{% endif %} >Preview</option>
                                </select>   
                            </div>
                            <div class="col-md-1" style="text-align:center;width:11.1%">
                                <select style="" class="form-control" name="quality" id="quality">
                                    <option id="dh" value="high"  {% if pyview.settingsInstance.realityCaptureSettings.default_export_quality == "high"   %}selected{% endif %}>High, 4M</option>
                                    <option id="dm" value="normal"{% if pyview.settingsInstance.realityCaptureSettings.default_export_quality == "normal" %}selected{% endif %}>Normal, 1M</option>
                                    <option id="dl" value="low"   {% if pyview.settingsInstance.realityCaptureSettings.default_export_quality == "low"    %}selected{% endif %}>Low, 500K</option>
                                </select>  
                            </div>
                            <div class="col-md-1" style="text-align:center;width:11.1%">
                                <select style="" class="form-control" name="create_mesh_from" id="create_mesh_from">
                                    <option value="projection" {% if pyview.settingsInstance.realityCaptureSettings.default_create_mesh_from == "projection" %}selected{% endif %}>Projection</option>
                                    <option value="normal"     {% if pyview.settingsInstance.realityCaptureSettings.default_create_mesh_from == "normal"     %}selected{% endif %}>Normal</option>
                                    <option value="all"        {% if pyview.settingsInstance.realityCaptureSettings.default_create_mesh_from == "all"        %}selected{% endif %}>All Images</option>
                                </select>   
                            </div>
                            <div class="col-md-1" style="text-align:center">
                                <input id="create_textures" {% if pyview.settingsInstance.realityCaptureSettings.default_create_textures == true %}checked{% endif %} type="checkbox"/>
                            </div>
                            <div class="col-md-1" style="text-align:center">
                                <input id="lit_unlit" {% if pyview.settingsInstance.realityCaptureSettings.default_lit == true %}checked{% endif %} type="checkbox"/>
                            </div>
                            <div class="col-md-3" style="text-align:center">
                         
                            </div>
                            
                            <div class="col-md-2" style="text-align:center">
                                <button class="btn btn-success btnfw" style="margin-right:5px" onclick='pyview.parent.subject.create_model($("#filetype").val(), $("#reconstruction_quality").val(), $("#quality").val(), $("#create_mesh_from").val(), $("#create_textures")[0].checked, $("#lit_unlit")[0].checked);'> Create Model </button>
                            </div>
                        </div>
                    </div>
                                      
                </div>
            </div>   
        </div>
    </div>
    '''

    def __init__(self, subject, parent, settingsInstance, **kwargs):
        super().__init__(subject, parent, **kwargs)
        self.settingsInstance = settingsInstance
        self.filesListView = ObservableListView(self.subject, self, item_class=ModelFileItemView, filter_function=lambda x:x.subject.is_custom_upload==True)


class ShotFilesCustomModelFilesView(PyHtmlView):
    TEMPLATE_STR = '''
<style>

.box__dragndrop,
.box__uploading,
.box__success,
.box__error {
  display: none;
}
.box {
    width: 100%;
    height: 60px;
}
.box.has-advanced-upload {
  background-color: white;
}
.box.has-advanced-upload .box__dragndrop {
  display: inline;
}
.box.is-dragover {
  background-color: #f0fff0;
}
.box.is-uploading .box__input {
  visibility: block;
}
.box.is-uploading .box__uploading {
  display: block;
}


</style>
    <div class="CustomModelFiles">
    

    
        <div class="row justify-content-center" style="width:100%">
            <div class="col-md-12">
                <div class="list-group mb-5 shadow">
                    <div class="list-group-item">
                        <div class="row align-items-center" style="border-bottom: 1px solid lightgray;">
                            <form id="form" class="box" method="post" action="/shots/{{pyview.parent.subject.shot_id}}/upload_custom" enctype="multipart/form-data">
                              <div class="col-md-7  h3">
                                Custom Files
                              </div>
                              <div class="box__input col-md-3" style="">
                                <input style="display:none" class="box__file" type="file" name="files[]" id="file" data-multiple-caption="{count} files selected" multiple />
                                <label style="line-height: 50px;height: 50px;" for="file">
                                    <strong style="color:#337ab7">Choose a file</strong><span class="box__dragndrop"> or drag it here</span>.
                                </label>
                                <div class="box__uploading">Uploading…</div>
                                <div class="box__success">Done!</div>
                                <div class="box__error">Error! <span></span>.</div>
                              </div>
                              <div class="col-md-2">
                                <button id="btn_upload" disabled class="btn btn-success btnfw" style="margin-top:10px"> Upload File</button>
                              </div>
                            </form>
                            
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-1 h5" style="text-align:center;font-weight:bold">Type</div>
                            <div class="col-md-1 h5" style="text-align:center;font-weight:bold;width:11.1%">Reconstruction Quality</div>
                            <div class="col-md-1 h5" style="text-align:center;font-weight:bold;width:11.1%">Export Quality</div>
                            <div class="col-md-1 h5" style="text-align:center;font-weight:bold;width:11.1%">Mesh from</div>
                            <div class="col-md-1 h5" style="text-align:center;font-weight:bold">Textures</div>
                            <div class="col-md-1 h5" style="text-align:center;font-weight:bold">Lit</div>
                            <div class="col-md-3 h5" style="text-align:center;font-weight:bold">File</div>
                            <div class="col-md-2 h5" style="text-align:center;font-weight:bold">Action</div>
                        </div>
                        {{pyview.filesListView.render()}}     
                        <div class="row" style="margin-top:10px">    
                            <script>
                                var existing_files = [{% for item in pyview.subject %}{%if item.is_custom_upload%}"{{item.filename}}",{%endif%}{% endfor %}""];

                                var isAdvancedUpload = function() {
                                  var div = document.createElement('div');
                                  return (('draggable' in div) || ('ondragstart' in div && 'ondrop' in div)) && 'FormData' in window && 'FileReader' in window;
                                }();
                            
                                var $form = $('.box');
                                if (isAdvancedUpload) {
                                  $form.addClass('has-advanced-upload');
                                }


                                if (isAdvancedUpload) {
                                  var $input    = $form.find('input[type="file"]');
                                  var $label    = $form.find('label')
                                    
                                  var droppedFiles = false;
                                
                                  $form.on('drag dragstart dragend dragover dragenter dragleave drop', function(e) {
                                    e.preventDefault();
                                    e.stopPropagation();
                                  })
                                  .on('dragover dragenter', function() {
                                    $form.addClass('is-dragover');
                                  })
                                  .on('dragleave dragend drop', function() {
                                    $form.removeClass('is-dragover');
                                  })
                                  .on('drop', function(e) {
                                    droppedFiles = e.originalEvent.dataTransfer.files;
                                    $label.text(droppedFiles.length > 1 ? ($input.attr('data-multiple-caption') || '').replace( '{count}', droppedFiles.length ) : droppedFiles[ 0 ].name);
                                    console.log(droppedFiles);
                                    $("#btn_upload").prop('disabled', false);
                                  });
                                  
                                  $input.on('change', function(e) {
                                     droppedFiles = e.target.files;
                                     $label.text(droppedFiles.length > 1 ? ($input.attr('data-multiple-caption') || '').replace( '{count}', droppedFiles.length ) : droppedFiles[ 0 ].name);
                                     
                                     $("#btn_upload").prop('disabled', false);
                                     for (let i = 0; i < droppedFiles.length; i++) {
                                        if(existing_files.includes(droppedFiles[i].name)){
                                            console.log("exists: " + droppedFiles[i] );
                                        }
                                     }
                                  });
                                
                                }


                                $form.on('submit', function(e) {
                                    e.preventDefault();
                                  if ($form.hasClass('is-uploading')) return false;
                                
                                  $form.addClass('is-uploading').removeClass('is-error');
                                
                                  if (isAdvancedUpload) {
                                      
                                    
                                      var ajaxData = new FormData($form.get(0));
                                    console.log();
                                   
                                    ajaxData.delete( $input.attr('name') );
                                      if (droppedFiles) {
                                      console.log("yep");
                                        $.each( droppedFiles, function(i, file) {
                                            console.log("here23" + i + file.name);
                                            if(!existing_files.includes(file.name)){
                                               console.log("append" + file);
                                                ajaxData.append( $input.attr('name'), file );
                                            }
                                        });
                                      }
                                 
                                 
                                 
                                 
                                      $.ajax({
                                        url: $form.attr('action'),
                                        type: $form.attr('method'),
                                        data: ajaxData,
                                        dataType: 'json',
                                        cache: false,
                                        contentType: false,
                                        processData: false,
                                        complete: function() {
                                          $form.removeClass('is-uploading');
                                           console.log("complete");
                                           document.getElementById("form").reset();
                                           $label.html('<strong style="color:#337ab7">Choose a file</strong><span class="box__dragndrop"> or drag it here</span>.');
                                      
                                        },
                                        success: function(data) {
                                           console.log("success");
                                          $form.addClass( data.success == true ? 'is-success' : 'is-error' );
                                          if (!data.success) $errorMsg.text(data.error);
                                        },
                                        error: function() {
                                          console.log("error");
                                          // Log the error, show an alert, whatever works for you
                                        }
                                      });
                                  } else {
                                    // ajax for legacy browsers
                                  }
                                });
                            </script>
                            
                        </div>
                    </div>
                </div>
            </div>   
        </div>
    </div>




    '''

    def __init__(self, subject, parent, settingsInstance, **kwargs):
        super().__init__(subject, parent, **kwargs)
        self.settingsInstance = settingsInstance
        self.filesListView = ObservableListView(self.subject, self, item_class=ModelFileItemView, filter_function=lambda x:x.subject.is_custom_upload==False)


class ModelPublishingView(PyHtmlView):
    DOM_ELEMENT = "dummy"
    TEMPLATE_STR = '''
        {% if pyview.subject.value == "state_changing" %}
            <div class="col-md-2" style="text-align:center;margin-top:1px">processing</div>
        {% else %}
            <div class="col-md-1" style="text-align:center">
                {% if pyview.subject.value == "can_unpublish" %}
                     <button class="btn btnfw" onclick='pyview.unpublish_model()' > Unpublish</button>
                {% elif pyview.subject.value == "can_publish" %}
                    <button class="btn btnfw" onclick='pyview.publish_model()' > Publish</button> 
                {% elif pyview.subject.value == "no_publish" %}

                {% endif %}
            </div>
            <div class="col-md-1" style="text-align:center">
                <button class="btn btnfw " onclick='pyview.parent.subject.delete()'> Delete</button>
            </div>
        {% endif %} 
    '''
    def publish_model(self):
        self.parent.subject.parentShot.dropboxPublicFolder.add_model(self.parent.subject)
    def unpublish_model(self):
        self.parent.subject.parentShot.dropboxPublicFolder.remove_model(self.parent.subject)

class ModelFileItemView(PyHtmlView):
    DOM_ELEMENT = "div"
    DOM_ELEMENT_CLASS = 'row'
    DOM_ELEMENT_EXTRAS = 'style="line-height: 3em;"'
    TEMPLATE_STR = '''
        <div class="col-md-1" style="text-align:center;margin-top:1px"> {{pyview.subject.filetype}}  </div>
        <div class="col-md-1" style="text-align:center;width:11.1%;margin-top:1px"> {{pyview.subject.reconstruction_quality}} </div>
        <div class="col-md-1" style="text-align:center;width:11.1%;margin-top:1px"> {{pyview.subject.quality}} </div>
        <div class="col-md-1" style="text-align:center;width:11.1%;margin-top:1px"> {{pyview.subject.create_mesh_from}} </div>
        <div class="col-md-1" style="text-align:center;margin-top:1px"> {{pyview.subject.create_textures}} </div>
        <div class="col-md-1" style="text-align:center;margin-top:1px"> {{pyview.subject.lit}} </div>
        <div class="col-md-3" style="text-align:center;margin-top:1px;white-space: nowrap;">
            {% if pyview.subject.status == "ready" %} 
                 {% if pyview.parent.parent.parent.parent.show_path == True %}
                    <a style="white-space: nowrap;" href="#" onclick="pyview.open_in_explorer()">{{pyview.subject.filename}}</a> ({{pyview.subject.filesize}}&nbsp;MB)
                {% else %}
                    <a style="white-space: nowrap;" href="/shots/{{pyview.subject.parentShot.shot_id}}/download/{{pyview.subject.model_id}}">{{pyview.subject.filename}}</a> ({{pyview.subject.filesize}}&nbsp;MB)
                {% endif %}
            {% else %}
                {{pyview.subject.status}}
            {% endif %}    
        </div>
        {% if  pyview.parent.parent.settingsInstance.settingsDropbox.is_authorized() == True and pyview.parent.parent.settingsInstance.settingsDropbox.enable_public == True and pyview.subject.parentShot.dropboxPublicFolder.status != "new" %}
            {{ pyview.modelPublishingView.render() }}
        {% else %}
            <div class="col-md-1"></div>
            <div class="col-md-1 " style="text-align:center">
                <button class="btn btnfw" onclick='pyview.subject.delete()'> Delete</button>
            </div>
        {% endif %}
    '''

    def __init__(self, subject, parent, **kwargs):
        super().__init__(subject, parent, **kwargs)
        self.modelPublishingView = ModelPublishingView(self.subject.publishing_status, self)

    def open_in_explorer(self):
        p = self.subject.get_path()
        if os.path.isdir(p) is False:
            p = self.subject.path
        os.startfile(p)

