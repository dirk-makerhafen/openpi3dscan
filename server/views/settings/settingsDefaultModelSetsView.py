from pyhtmlgui import PyHtmlView

class SettingsDefaultModelSetsView(PyHtmlView):
    TEMPLATE_STR = '''

        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-12">
                    <strong class="mb-0">One Click File Sets</strong>
                    <p class="text-muted mb-0"> Create sets of model so you can created mutiple models with one click </p>
                </div>
                <div class="col-md-12">
                <table style="width:100%;text-align:center">
                    <thead>
                        <tr>
                        <th style="text-align:center">Name</th>
                        <th style="text-align:center">Type</th>
                        <th style="text-align:center">Reconstruction Quality</th>
                        <th style="text-align:center">Export Quality</th>
                        <th style="text-align:center">Mesh from</th>
                        <th style="text-align:center">Textures</th>
                        <th style="text-align:center">Lit</th>
                        <th style="text-align:center">Action</th>
                        </tr>
                    </thead>
                    
                    {% for default_model in pyview.subject.default_models %}
                        <tr>
                            <td>{{default_model.name}} </td>
                            <td>{{default_model.filetype}} </td>
                            <td>{{default_model.reconstruction_quality}}</td>
                            <td>{{default_model.quality}}</td>
                            <td>{{default_model.create_mesh_from}}</td>
                            <td>{{default_model.create_textures}}</td>
                            <td>{{default_model.lit}}</td>
                            <td><button class="btn" onclick='default_model.delete()'> Remove</button></td>
                        </tr>
                    {% endfor %}
                                        
                    <tr style="border-top: 1px solid lightgray;    line-height: 3em;">
                        <td> 
                          <input id="set_name" placefolder="Set Name" />  
                        </td>
                        <td style="padding-left: 5px;padding-right: 5px;">
                            <select style="" class="form-control" name="filetype" id="filetype" onchange='var v=$("#filetype").val();if(v=="glb"||v=="gif"||v=="webp"){ $("#lit_unlit").prop("disabled", False); }else{ $("#lit_unlit").prop("disabled", True);$("#lit_unlit")[0].checked = True; }'>
                                <option value="obj">OBJ</option>
                                <option value="stl">STL</option>
                                <option value="3mf">3MF</option>
                                <option value="glb">GLB</option>
                                <option value="fbx">FBX</option>
                                <option value="rcproj">RCPROJ</option>
                                <option value="gif">GIF</option>
                                <option value="webp">WebP</option>
                            </select>
                        </td>
                        <td style="padding-left: 5px;padding-right: 5px;">
                            <select style="" class="form-control" name="reconstruction_quality" id="reconstruction_quality">
                                <option value="high"   >High</option>
                                <option value="normal" >Normal</option>
                                <option value="preview">Preview</option>
                            </select>                            
                        </td>
                        <td style="padding-left: 5px;padding-right: 5px;">
                            <select style="" class="form-control" name="quality" id="quality">
                                <option value="high" >High (4M)</option>
                                <option value="normal">Normal (1M)</option>
                                <option value="low"   >Low (500K)</option>
                            </select>                            
                        </td>
                        <td style="padding-left: 5px;padding-right: 5px;">
                            <select style="" class="form-control" name="create_mesh_from" id="create_mesh_from">
                                <option value="projection" >Projection</option>
                                <option value="normal"     >Normal</option>
                                <option value="all"        >All Images</option>
                            </select>   
                        </td>
                        <td> <input id="create_textures" type="checkbox"/> </td>
                        <td> <input id="lit_unlit" type="checkbox"/>  </td>
                        
                        <td> <button class="form-control btn btn-success" style="margin-right:5px" onclick='pyview.parent.addDefaultModel($("#set_name").val(), $("#filetype").val(), $("#reconstruction_quality").val(), $("#quality").val(), $("#create_mesh_from").val(), $("#create_textures")[0].checked, $("#lit_unlit")[0].checked);'> Add Model </button></td>
                    </tr>
                </table>
                    
                    
                </div>
            </div>
        </div>
 
    '''
    def __init__(self, subject, parent, **kwargs):
        super().__init__(subject, parent, **kwargs)


