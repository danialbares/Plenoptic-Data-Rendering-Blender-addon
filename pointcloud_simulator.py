############################################################################
#  This work, "Plenoptic Data Rendering", is a derivative of "4D Light     #
#  Field Benchmark" by Katrin Honauer & Ole Johannsen used under           #
#  Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International #
#  License (http://creativecommons.org/licenses/by-nc-sa/4.0/)             #
#                              and                                         #
#  "Stanford PLY Format" by Bruce Merry & Campbell Barton used under       #
#  GNU General Public License version 3.0 (GPLv3)                          #
#  (https://www.gnu.org/licenses/gpl-3.0.html) / Desaturated from original #
#                                                                          #
#  "Plenoptic Data Rendering" is licensed under GPLv3                      #
#  (https://www.gnu.org/licenses/gpl-3.0.html) by Daniel Albares Martin    #
#                                                                          #
############################################################################

import bpy
from bpy.props import *
import sys, os, json

import os
import random
import shutil
import pathlib
import numpy as np
import glob
import cv2

from math import *
from mathutils import *


class OBJECT_OT_render_pointcloud(bpy.types.Operator):
    """render point cloud"""
    bl_idname = "scene.render_pointcloud"
    bl_label = """Render Point Cloud"""
    bl_options = {'REGISTER'}

    def execute(self, context):
        
        import cv2
        # INITIALIZE ATTRIBUTES
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        
        LF = bpy.context.scene.LF
        
        # Image attributes
        self.rgb_list = []
        self.depth_list = []
        self.depth_list_pfm = []
        self.num_points = LF.x_res * LF.y_res
        self.point_cloud_name = LF.point_cloud_name
        
        #if LF.sequence_start == LF.sequence_end:
            #bpy.context.scene.frame_current = LF.sequence_start
            
        # Sort images in path. Read them and append them to the list of images
        sorted_rgb = sorted(glob.glob(LF.tgt_dir + "/input_Cam*.png"))
        sorted_depth = sorted(glob.glob(LF.tgt_dir + "/gt_disp_lowres*.png"))
        sorted_depth_pfm = sorted(glob.glob(LF.tgt_dir + "/gt_disp_lowres*.pfm"))
        
        # Check if PNG disparity maps exist. If not, check if PFM disparity maps exist
        if len(sorted_depth) and len(sorted_rgb) > 0:
            
            for filename in sorted_rgb:
                img = cv2.imread(filename)
                self.rgb_list.append(img)
                
            for filename in sorted_depth:
                img = cv2.imread(filename)
                self.depth_list.append(img)
                
            self.renderPointCloud(LF, LF.tgt_dir)
        
        elif len(sorted_depth_pfm) and len(sorted_rgb) > 0:
            
            for filename in sorted_rgb:
                img = cv2.imread(filename)
                self.rgb_list.append(img)
                
            for filename in sorted_depth_pfm:
                img = self.read_pfm(filename)
                self.depth_list_pfm.append(img)
                
            self.renderPointCloud(LF, LF.tgt_dir)
        
        else:
            "Display message to render light field first to generate views and depth maps"
            
        
        return {'FINISHED'} 
    
    
    def renderPointCloud(self, LF, tgt_dir):
        """""""""""""""""""""""""""""""""""""""""""""""""""""""""
        Render Point Cloud of the scene
        """""""""""""""""""""""""""""""""""""""""""""""""""""""""
        LF = bpy.context.scene.LF
        
        # Create new empty points array
        points = np.zeros((LF.x_res * LF.y_res, 3), np.float32)
        color = np.zeros((LF.x_res * LF.y_res, 3), np.int)
        
        # For loop to set the depth and color values
        c = 0
        idx = 0
        for i in range(0, LF.x_res):
            for j in range(0, LF.y_res):
                points[c, 0] = j
                points[c, 1] = i
                im_rgb = self.rgb_list[idx]
                # In case it is using RGB disparity map
                if len(self.depth_list) > 0:
                    im_depth = self.depth_list[idx]
                    points[c, 2] = im_depth[i, j, 0]
                # In case it is using PFM disparity map
                elif len(self.depth_list_pfm) > 0:
                    MIN = 0
                    MAX = 512
                    im_depth = self.depth_list_pfm[idx]
                    value = im_depth[i,j]
                    points[c, 2] = self.range_adjust(MAX, LF.max_disp, LF.min_disp, value)
                color[c] = im_rgb[i, j]
                c += 1
        
        self.exportPlyFile(LF, LF.tgt_dir, points, color)
        
                        
    def exportPlyFile(self, LF, tgt_dir, points, color):
        """""""""""""""""""""""""""""""""""""""""""""""""""""""""
        Export ply file with the point cloud mesh
        """""""""""""""""""""""""""""""""""""""""""""""""""""""""
        LF = bpy.context.scene.LF
        
        # Path to export ply file
        filename = str(LF.point_cloud_name)
        path = tgt_dir + "/" + filename + ".ply"
        
        with open(path, 'w', encoding='ascii') as ply_file:
            # Write headers
            headers = ["ply\n",
                       "format ascii 1.0\n",
                       "element face 0\n",
                       "property list uchar int vertex_indices\n",
                       "element vertex %d\n" % self.num_points,
                       "property float x\n",
                       "property float y\n",
                       "property float z\n",
                       "property uchar diffuse_red\n",
                       "property uchar diffuse_green\n",
                       "property uchar diffuse_blue\n",
                       "end_header\n"]

            for header in headers:
                ply_file.write(header)

            # Write point position and color
            for pt_idx in range(0, self.num_points):
                pt_pos = points[pt_idx]
                pt_color = color[pt_idx]
                ply_file.write("%f %f %f %d %d %d\n" % (pt_pos[1], pt_pos[0], pt_pos[2], int(pt_color[2]), int(pt_color[1]), int(pt_color[0])))


    def read_pfm(self, filename):
        """""""""""""""""""""""""""""""""""""""""""""""""""""""""
        Read pfm file to generate Point Cloud from it
        """""""""""""""""""""""""""""""""""""""""""""""""""""""""
        from pathlib import Path
        import struct
        
        with Path(filename).open('rb') as pfm_file:
            line1, line2, line3 = (pfm_file.readline().decode('latin-1').strip() for _ in range(3))
            assert line1 in ('PF', 'Pf')

            channels = 3 if "PF" in line1 else 1
            width, height = (int(s) for s in line2.split())
            scale_endianess = float(line3)
            bigendian = scale_endianess > 0
            scale = abs(scale_endianess)

            buffer = pfm_file.read()
            samples = width * height * channels
            assert len(buffer) == samples * 4

            fmt = f'{"<>"[bigendian]}{samples}f'
            decoded = struct.unpack(fmt, buffer)
            shape = (height, width, 3) if channels == 3 else (height, width)
            return np.flipud(np.reshape(decoded, shape)) * scale
        
    def range_adjust(self, max, disp_max, disp_min, value):
        ans = max * (value - disp_min) / (disp_max - disp_min)
        return ans


        
from bpy.props import (
    CollectionProperty,
    StringProperty,
    BoolProperty,
    FloatProperty,
)
from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper,
    axis_conversion,
    orientation_helper,
)        


@orientation_helper(axis_forward='Y', axis_up='Z')
class OBJECT_OT_EXPORT_PLY(bpy.types.Operator, ExportHelper):
    bl_idname = "export_mesh.ply"
    bl_label = "Export PLY"
    bl_description = "Export as a Stanford PLY with normals, vertex colors and texture coordinates"

    filename_ext = ".ply"
    filter_glob: StringProperty(default="*.ply", options={'HIDDEN'})

    use_ascii: BoolProperty(
        name="ASCII",
        description="Export using ASCII file format, otherwise use binary",
    )
    use_selection: BoolProperty(
        name="Selection Only",
        description="Export selected objects only",
        default=False,
    )
    use_mesh_modifiers: BoolProperty(
        name="Apply Modifiers",
        description="Apply Modifiers to the exported mesh",
        default=True,
    )
    use_normals: BoolProperty(
        name="Normals",
        description=(
            "Export Normals for smooth and hard shaded faces "
            "(hard shaded faces will be exported as individual faces)"
        ),
        default=True,
    )
    use_uv_coords: BoolProperty(
        name="UVs",
        description="Export the active UV layer",
        default=True,
    )
    use_colors: BoolProperty(
        name="Vertex Colors",
        description="Export the active vertex color layer",
        default=True,
    )
    global_scale: FloatProperty(
        name="Scale",
        min=0.01,
        max=1000.0,
        default=1.0,
    )

    def execute(self, context):
        from mathutils import Matrix

        context.window.cursor_set('WAIT')

        keywords = self.as_keywords(
            ignore=(
                "axis_forward",
                "axis_up",
                "global_scale",
                "check_existing",
                "filter_glob",
            )
        )
        global_matrix = axis_conversion(
            to_forward=self.axis_forward,
            to_up=self.axis_up,
        ).to_4x4() @ Matrix.Scale(self.global_scale, 4)
        keywords["global_matrix"] = global_matrix

        self.save(context, **keywords)

        context.window.cursor_set('DEFAULT')

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        sfile = context.space_data
        operator = sfile.active_operator

        col = layout.column(heading="Format")
        col.prop(operator, "use_ascii")
        
        
    def _write_binary(self, fw, ply_verts, ply_faces, mesh_verts):
        from struct import pack
        for index, normal, uv_coords, color in ply_verts:
            fw(pack("<3f", *mesh_verts[index].co))
            if normal is not None:
                fw(pack("<3f", *normal))
            if uv_coords is not None:
                fw(pack("<2f", *uv_coords))
            if color is not None:
                fw(pack("<4B", *color))


    def _write_ascii(self, fw, ply_verts, ply_faces, mesh_verts):

        for index, normal, uv_coords, color in ply_verts:
            fw(b"%.6f %.6f %.6f" % mesh_verts[index].co[:])
            if normal is not None:
                fw(b" %.6f %.6f %.6f" % normal)
            if uv_coords is not None:
                fw(b" %.6f %.6f" % uv_coords)
            if color is not None:
                fw(b" %u %u %u %u" % color)
            fw(b"\n")

    def save_mesh(self, filepath, mesh, use_ascii, use_normals, use_uv_coords, use_colors):
        import bpy

        def rvec3d(v):
            return round(v[0], 6), round(v[1], 6), round(v[2], 6)

        def rvec2d(v):
            return round(v[0], 6), round(v[1], 6)

        if use_uv_coords and mesh.uv_layers:
            active_uv_layer = mesh.uv_layers.active.data
        else:
            use_uv_coords = False

        if use_colors and mesh.vertex_colors:
            active_col_layer = mesh.vertex_colors.active.data
        else:
            use_colors = False

        # in case
        color = uvcoord = uvcoord_key = normal = normal_key = None

        mesh_verts = mesh.vertices
        # vdict = {} # (index, normal, uv) -> new index
        vdict = [{} for i in range(len(mesh_verts))]
        ply_verts = []
        ply_faces = [[] for f in range(len(mesh.polygons))]
        vert_count = 0

        for i, f in enumerate(mesh.polygons):

            if use_normals:
                smooth = f.use_smooth
                if not smooth:
                    normal = f.normal[:]
                    normal_key = rvec3d(normal)

            if use_uv_coords:
                uv = [
                    active_uv_layer[l].uv[:]
                    for l in range(f.loop_start, f.loop_start + f.loop_total)
                ]
            if use_colors:
                col = [
                    active_col_layer[l].color[:]
                    for l in range(f.loop_start, f.loop_start + f.loop_total)
                ]

            pf = ply_faces[i]
            for j, vidx in enumerate(f.vertices):
                v = mesh_verts[vidx]

                if use_normals and smooth:
                    normal = v.normal[:]
                    normal_key = rvec3d(normal)

                if use_uv_coords:
                    uvcoord = uv[j][0], uv[j][1]
                    uvcoord_key = rvec2d(uvcoord)

                if use_colors:
                    color = col[j]
                    color = (
                        int(color[0] * 255.0),
                        int(color[1] * 255.0),
                        int(color[2] * 255.0),
                        int(color[3] * 255.0),
                    )
                key = normal_key, uvcoord_key, color

                vdict_local = vdict[vidx]
                pf_vidx = vdict_local.get(key)  # Will be None initially

                if pf_vidx is None:  # Same as vdict_local.has_key(key)
                    pf_vidx = vdict_local[key] = vert_count
                    ply_verts.append((vidx, normal, uvcoord, color))
                    vert_count += 1

                pf.append(pf_vidx)

        with open(filepath, "wb") as file:
            fw = file.write
            file_format = b"ascii" if use_ascii else b"binary_little_endian"

            # Header
            # ---------------------------

            fw(b"ply\n")
            fw(b"format %s 1.0\n" % file_format)
            fw(b"comment Created by Blender %s - www.blender.org\n" % bpy.app.version_string.encode("utf-8"))

            fw(b"element vertex %d\n" % len(ply_verts))
            fw(
                b"property float x\n"
                b"property float y\n"
                b"property float z\n"
            )
            if use_normals:
                fw(
                    b"property float nx\n"
                    b"property float ny\n"
                    b"property float nz\n"
                )
            if use_uv_coords:
                fw(
                    b"property float s\n"
                    b"property float t\n"
                )
            if use_colors:
                fw(
                    b"property uchar red\n"
                    b"property uchar green\n"
                    b"property uchar blue\n"
                    b"property uchar alpha\n"
                )

            fw(b"element face %d\n" % len(mesh.polygons))
            fw(b"property list uchar uint vertex_indices\n")
            fw(b"end_header\n")

            # Geometry
            # ---------------------------

            if use_ascii:
                self._write_ascii(fw, ply_verts, ply_faces, mesh_verts)
            else:
                self._write_binary(fw, ply_verts, ply_faces, mesh_verts)


    def save(self, 
        context,
        filepath="",
        use_ascii=False,
        use_selection=False,
        use_mesh_modifiers=True,
        use_normals=True,
        use_uv_coords=True,
        use_colors=True,
        global_matrix=None,
    ):
        import time
        import bpy
        import bmesh

        t = time.time()

        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')

        if use_selection:
            obs = context.selected_objects
        else:
            obs = context.scene.objects

        depsgraph = context.evaluated_depsgraph_get()
        bm = bmesh.new()

        for ob in obs:
            if use_mesh_modifiers:
                ob_eval = ob.evaluated_get(depsgraph)
            else:
                ob_eval = ob

            try:
                me = ob_eval.to_mesh()
            except RuntimeError:
                continue

            me.transform(ob.matrix_world)
            bm.from_mesh(me)
            ob_eval.to_mesh_clear()

        mesh =  bpy.data.meshes.new("TMP PLY EXPORT")
        bm.to_mesh(mesh)
        bm.free()

        if global_matrix is not None:
            mesh.transform(global_matrix)

        if use_normals:
            mesh.calc_normals()

        self.save_mesh(
            filepath,
            mesh,
            use_ascii,
            use_normals,
            use_uv_coords,
            use_colors,
        )

        bpy.data.meshes.remove(mesh)

        t_delta = time.time() - t
        print(f"Export completed {filepath!r} in {t_delta:.3f}")


classes = (
    OBJECT_OT_render_pointcloud,
    OBJECT_OT_EXPORT_PLY,
    
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

if __name__ == "__main__":
    register()





