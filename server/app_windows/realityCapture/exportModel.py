import os, shutil
from pygltflib import GLTF2, TextureInfo
from app_windows.realityCapture.genericTask import GenericTask
import sys, os
import numpy as np
import trimesh
import platform
import shutil

scad_script = '''
    text=text;
    date=date;
    length= length;
    width = 7 + ( length * 4.5);
    difference(){
        union (){
        cube ([width, 13 ,0.7], center = true);
        translate([-(width/2)+7,  3, 0]) linear_extrude(height = 0.9) text(date, halign = "left", valign = "center", size = 5, font = "Arial Black");
        translate([-(width/2)+7, -3, 0]) linear_extrude(height = 0.9) text(text, halign = "left", valign = "center", size = 5, font = "Arial Black");
        }
        translate([-width/2+4,0,-2]) cylinder(6,2.2,2.2);  
    }
'''


_search_path = os.environ.get("PATH", "")
# add additional search locations on windows
if platform.system() == "Windows":
    # split existing path by delimiter
    _search_path = [i for i in _search_path.split(";") if len(i) > 0]
    _search_path.append(os.path.normpath(r"C:\Program Files\OpenSCAD"))
    _search_path.append(os.path.normpath(r"C:\Program Files (x86)\OpenSCAD"))
    _search_path = ";".join(_search_path)
# add mac-specific search locations
if platform.system() == "Darwin":
    _search_path = [i for i in _search_path.split(":") if len(i) > 0]
    _search_path.append("/Applications/OpenSCAD.app/Contents/MacOS")
    _search_path = ":".join(_search_path)
# try to find the SCAD executable by name
openscad_path = shutil.which("openscad", path=_search_path)
if openscad_path is None:
    openscad_path = shutil.which("OpenSCAD", path=_search_path)



class ExportModel(GenericTask):
    def __init__(self, rc_job):
        super().__init__(rc_job)
        self.export_model_path = os.path.join(self.rc_job.workingdir, self.rc_job.export_foldername,self.rc_job.export_filename)

        if self.rc_job.filetype != "rcproj":
            self.output_model_path = os.path.join(self.rc_job.workingdir, self.rc_job.export_foldername, self.rc_job.export_filename.replace(" ","_" if self.rc_job.filetype not in ["3mf","stl", "stl_printready" ] else " "))


    def run(self):
        force_reload = self.status != "idle"
        self.set_status("active")
        if force_reload is True and os.path.exists(self.output_model_path):
            self.log.append("Removing cached export file")
            os.remove(self.output_model_path)

        if os.path.exists(self.output_model_path):
            if self.rc_job.compress_results is False and self.rc_job.filetype != "rcproj":
                self.rc_job.result_path = os.path.join(self.rc_job.workingdir, self.rc_job.export_foldername)
            self.log.append("Using from cache")
            self.set_status("success")
            return

        cmd = self._get_cmd_start()
        cmd += '-load "%s\\%s.rcproj" deleteAutosave ' % (self.rc_job.workingdir, self.rc_job.realityCapture_filename)
        cmd += '-selectComponent "MAIN" '
        cmd += '-selectModel "RAW" '
        if self.rc_job.export_quality == "high" or self.rc_job.filetype == "holobox":
            cmd += '-simplify 4000000 '
        elif self.rc_job.export_quality == "normal" or self.rc_job.filetype in ["gif", "webp"]:
            cmd += '-simplify 1000000 '
        elif self.rc_job.export_quality == "low":
            cmd += '-simplify 500000 '
        cmd += '-cleanModel '
        cmd += '-closeHoles '
        if self.rc_job.create_textures is True and self.rc_job.filetype not in ["stl", "stl_printready"]:
            cmd += '-calculateTexture '
            #cmd += '-calculateVertexColors '
        cmd += '-renameSelectedModel "EXPORT" '
        if self.rc_job.filetype == "rcproj":
            cmd += '-save "%s" ' % self.export_model_path
        else:
            cmd += '-exportModel "EXPORT" "%s" ' % self.export_model_path

        cmd += '-quit '
        self._run_command(cmd, "create_export_model")

        if not os.path.exists(self.output_model_path):
            self.log.append("Export model not created, %s not found." % self.output_model_path)
            self.set_status("failed")
            return

        if self.rc_job.fileextension == "glb" and self.rc_job.lit is False and self.rc_job.create_textures is True:
            glbf = GLTF2().load(self.output_model_path)
            glbf.materials[0].pbrMetallicRoughness.baseColorFactor = [0, 0, 0, 1]
            glbf.materials[0].emissiveFactor = [1, 1, 1]
            glbf.materials[0].emissiveTexture = TextureInfo(index=0)
            glbf.save(self.output_model_path)

        if self.rc_job.filetype == "stl_printready":
            self.add_plate(self.output_model_path)

        if not os.path.exists(self.output_model_path):
            self.log.append("Print preparation failed, %s not found." % self.output_model_path)
            self.set_status("failed")
            return

        if self.rc_job.compress_results is False and self.rc_job.filetype != "rcproj":
            self.rc_job.result_path = os.path.join(self.rc_job.workingdir, self.rc_job.export_foldername)

        if os.path.exists("%s.rcInfo" % self.output_model_path):
            os.remove("%s.rcInfo" % self.output_model_path)
        self.log.append("Export model created")
        self.set_status("success")



    def capfirst(self, s):
        return s[:1].upper() + s[1:]

    def create_plate(self, input_file):
        output_file = input_file.replace(".stl", "_TAG.stl")
        fname = input_file.split("/")[-1]
        day = fname.split(" ",2)[0].split(".")[2]
        month = fname.split(" ",2)[0].split(".")[1]
        date = fname.split(" ",2)[1]
        name = self.capfirst("_".join(fname.split(" ",2)[2].split("_")[:-1])).replace(" ","")
        date = "%s.%s %s" % ( day, month, date)
        length = max([len(name), len(date)])
        os.system('%s -o "%s" nameplate.scad -D \'text="%s"\'  -D \'date="%s"\' -D \'length=%s\' 2>/dev/null' % (openscad_path,  output_file, name, date, length))
        return output_file

    def extract_vertexes(self, mesh, lower_limit = 0.05, upper_limit = 0.3):
        z_min = mesh.bounds[0][2]
        z_max = mesh.bounds[1][2]
        total_height = z_max - z_min
        lower_limit = z_min + total_height * lower_limit
        upper_limit = z_min + total_height * upper_limit
        return mesh.vertices[(mesh.vertices[:, 2] <= upper_limit) & (mesh.vertices[:, 2] >= lower_limit)]

    def center_model(self, mesh):
        valid_vertices = self.extract_vertexes(mesh)
        if valid_vertices.size > 0:
            valid_min = np.min(valid_vertices, axis=0)
            valid_max = np.max(valid_vertices, axis=0)
            valid_center = (valid_min + valid_max) / 2
        else:
            valid_center = [0, 0, 0]  # Fallback to origin if no vertices meet the criteria
        mesh.apply_translation([-valid_center[0], -valid_center[1], 0])
        mesh.apply_translation([0, 0,-mesh.bounds[0][2]]) #     # Translate the mesh so that its lowest point is at Z=0

    def cut_mesh(self, mesh, lower_limit, upper_limit):
        box_height = upper_limit - lower_limit
        ground_plane_center = [0, 0, lower_limit + box_height/2]
        ground_plane_mesh = trimesh.creation.box(extents=[200, 200, box_height], transform=trimesh.transformations.translation_matrix(ground_plane_center))
        return mesh.difference(ground_plane_mesh, engine='scad')

    def rotate(self, original_mesh):
        z_max = original_mesh.bounds[1][2]
        mesh = self.cut_mesh(original_mesh, -10, z_max / 20)  # use only lower part to rotation estimation
        mesh = self.cut_mesh(mesh, z_max / 5, z_max)

        smallest_dim = 999999
        smallest_angle = 0
        center = mesh.centroid

        back_angle = 25     #rotate back x deg for better range
        mesh.apply_transform(trimesh.transformations.rotation_matrix(np.deg2rad(-back_angle), [0, 0, 1], center))

        angle_step = 2
        angle = np.deg2rad(angle_step)
        for i in range(int(160/angle)):
            mesh.apply_transform(trimesh.transformations.rotation_matrix(angle, [0, 0, 1], center))
            y_dim = mesh.bounds[1][1] - mesh.bounds[0][1]  # Max Y - Min Y
            if y_dim < smallest_dim:
                smallest_dim = y_dim
                smallest_angle = i*angle_step
        original_mesh.apply_transform(trimesh.transformations.rotation_matrix( np.deg2rad(smallest_angle-back_angle), [0, 0, 1], center))

    def add_plate(self, input_file):
        self.log.append("Preparing printer ready stl")
        nameplate_scad_script = os.path.join(self.rc_job.workingdir, "nameplate.scad")
        with open(nameplate_scad_script, "w") as f:
            f.write(scad_script)
        model_mesh = trimesh.load(input_file)  # load model

        model_mesh.apply_scale(100)   # scale to mm 1:10 model

        model_mesh = self.cut_mesh(model_mesh, -10, 0.3) # cut ground plane
        components = model_mesh.split(only_watertight=False)  # extract largest component
        model_mesh = max(components, key=lambda x: x.volume)

        self.center_model(model_mesh)
        self.rotate(model_mesh)
        self.center_model(model_mesh)

        z_dim = model_mesh.bounds[1][2] - model_mesh.bounds[0][2]  # Max X - Min X
        if z_dim > 60:
            backward_angle = 25  # tilt model backwards for better printing
            model_mesh.apply_transform(trimesh.transformations.rotation_matrix(np.deg2rad(-backward_angle), [1, 0, 0], model_mesh.centroid))
            model_mesh.apply_translation([0, 0, -model_mesh.bounds[0][2]])  # # Translate the mesh so that its lowest point is at Z=0
        else:
            print(" Model too small, %s mm high, not tilting" % int(z_dim))

        plate_file = self.create_plate(input_file)  # create plate
        plate_mesh = trimesh.load(plate_file)  # load plate model
        self.center_model(plate_mesh)  # center plate

        offset = np.array([0, (np.min(model_mesh.bounds[:, 1]) - np.max(plate_mesh.bounds[:, 1])) - 5, 0])  # move plate
        plate_mesh.apply_translation(offset)

        combined_mesh = trimesh.util.concatenate([model_mesh, plate_mesh])
        combined_mesh.export(input_file)

        os.remove(nameplate_scad_script)
        os.remove(plate_file)


