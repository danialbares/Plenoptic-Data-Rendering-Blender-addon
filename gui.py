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
############################################################################
#  This file is part of the 4D Light Field Benchmark.                      #
#                                                                          #
#  This work is licensed under the Creative Commons                        #
#  Attribution-NonCommercial-ShareAlike 4.0 International License.         #
#  To view a copy of this license,                                         #
#  visit http://creativecommons.org/licenses/by-nc-sa/4.0/.                #
#                                                                          #
#  Authors: Katrin Honauer & Ole Johannsen                                 #
#  Contact: contact@lightfield-analysis.net                                #
#  Website: www.lightfield-analysis.net                                    #
#                                                                          #
#  This add-on is based upon work of Maximilian Diebold                    #
#                                                                          #
#  The 4D Light Field Benchmark was jointly created by the University of   #
#  Konstanz and the HCI at Heidelberg University. If you use any part of   #
#  the benchmark, please cite our paper "A dataset and evaluation          #
#  methodology for depth estimation on 4D light fields". Thanks!           #
#                                                                          #
#  @inproceedings{honauer2016benchmark,                                    #
#    title={A dataset and evaluation methodology for depth estimation on   #
#           4D light fields},                                              #
#    author={Honauer, Katrin and Johannsen, Ole and Kondermann, Daniel     #
#            and Goldluecke, Bastian},                                     #
#    booktitle={Asian Conference on Computer Vision},                      #
#    year={2016},                                                          #
#    organization={Springer}                                               #
#    }                                                                     #
#                                                                          #
############################################################################

import bpy
from bpy.props import *

class VIEW3D_PT_camera_setup(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_label = "Camera Set Up"
    bl_category = "Plenoptic Data Rendering"

    def draw(self, context):
        LF = bpy.context.scene.LF
        layout = self.layout
        
        box = layout.box()
        col = box.column(align=False)
        col.operator("scene.create_lightfield", text="Add Camera Grid", icon="ADD")
        col.operator("scene.delete_lightfield", text="Delete Camera Grid", icon="REMOVE")
        
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Number of cameras & position")
        row = box.row()
        col = box.column(align=True)       
        row.prop(LF, "num_cams_x", text="X:")
        row.prop(LF, "num_cams_y", text="Y: ")
        col.prop(LF, "baseline_mm")
        col = box.column(align=True)
        if LF.show_one_camera == False:
            col.operator("scene.hide_cameras", text="Show only center camera", icon="HAND")
        else:
            col.operator("scene.show_cameras", text="Show all cameras", icon="HAND")
        
        box = layout.box()
        box.label(text="Camera parameters")
        col = box.column(align=True)
        col.prop(LF, "focus_dist")
        col.prop(LF, "fstop")
        col.prop(LF, "focal_length")
        col.prop(LF, "sensor_size")
        
        box.label(text="Resolution [px]")
        row = box.row()
        col = box.column(align=True) 
        row.prop(LF, "x_res")
        row.prop(LF, "y_res")
    
        box = layout.box()
        box.label(text="Disparity preview")
        col = box.column(align=True)
        col.prop(LF, "frustum_min_disp")
        col.prop(LF, "frustum_max_disp")
        frustum_name = bpy.context.scene.LF.get_frustum_name()
        if bpy.data.objects[frustum_name].hide_viewport == True:
            col.operator("scene.show_frustum", text="Show Frustum", icon="HAND")
        else:
            col.operator("scene.hide_frustum", text="Hide Frustum", icon="HAND")
 
        box = layout.box()
        box.label(text="Save settings")
        col = box.column(align=True)
        col.prop(LF, "depth_map_scale")
        col.prop(LF, "sequence_start")
        col.prop(LF, "sequence_end")
        col.prop(LF, "sequence_steps")



class VIEW3D_PT_render_setup(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_label = "Rendering"
    bl_category = "Plenoptic Data Rendering"

    def draw(self, context):
        LF = bpy.context.scene.LF
        layout = self.layout
        
        box = layout.box()
        col = box.column(align=True)
        col.prop(LF, "tgt_dir")
        
        box = layout.box()
        box.label(text="Light Field")
        col = box.column(align=True)
        col.label(text="Save images as:")
        row = box.row(align=True)
        col = box.column(align=True)
        row.prop(LF, "save_lenslet_image", text="Lenslet")
        row.prop(LF, "save_sidebyside_image", text="Side-by-side")
        
        col.label(text="Save depth and disparity maps as:")
        row = box.row(align=True)
        col = box.column(align=True)
        row.prop(LF, "save_depth_as_png", text="PNG")
        row.prop(LF, "save_depth_as_pfm", text="PFM")
          
        row = box.row(align=True)
        col.prop(LF, "save_depth_for_all_views")     
        col.prop(LF, "save_object_id_maps_for_all_views")
        col = box.column(align=True)
        col.prop(LF, "focus_separation")
        col.prop(LF, "focus_steps")
        focus_planes_name = bpy.context.scene.LF.get_focus_planes_name()
        if bpy.data.objects[focus_planes_name].hide_viewport == True:
            col.operator("scene.show_focus_planes", text="Show focus range", icon="HAND")
        else:
            col.operator("scene.hide_focus_planes", text="Hide focus range", icon="HAND")
        col = box.column(align=True)
        col.label(text="Render Light Field as:")
        col.operator("scene.render_lightfield", text="Multiple views", icon="OUTLINER_DATA_CAMERA")
        col = box.column(align=True)
        col.operator("scene.render_focus_stack", text="Focus stack", icon="NODE_COMPOSITING")

        box = layout.box()
        box.label(text="Point Cloud")
        col = box.column(align=True)
        col.prop(LF, "point_cloud_name")
        col = box.column(align=True)
        col.label(text="Render Point Cloud:")
        col.operator("scene.render_pointcloud", text="From generated views", icon="OUTLINER_OB_POINTCLOUD")
        col = box.column(align=True)
        col.operator("export_mesh.ply", text="Directly from Blender", icon="OUTLINER_OB_POINTCLOUD")



class VIEW3D_PT_scene_settings(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_label = "Scene Settings"
    bl_category = "Plenoptic Data Rendering"

    def draw(self, context):
        LF = bpy.context.scene.LF
        layout = self.layout
        
        box = layout.box()
        box.label(text="Information")
        col = box.column(align=False)
        col.prop(LF, "scene")
        col.prop(LF, "date")
        col.prop(LF, "authors")

        box = layout.box()
        box.label(text="Save/load settings")
        col = box.column(align=False)
        col.prop(LF, "path_config_file")
        col.operator("scene.load_lightfield", text="Load config file", icon="SCENE_DATA")
        col.operator("scene.save_lightfield", text="Save config file", icon="SCENE_DATA")
          

classes = (
    VIEW3D_PT_camera_setup,
    VIEW3D_PT_render_setup,
    VIEW3D_PT_scene_settings,
    
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
