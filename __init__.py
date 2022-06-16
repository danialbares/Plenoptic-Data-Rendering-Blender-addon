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

bl_info = {
    'name': 'Plenoptic Data Renderer',
    'author': 'Ole Johannsen, Katrin Honauer, Daniel Albares',
    'description': 'Blender add-on to render multiple plenoptic modalities',
    'version': (1, 1, 0),
    'blender': (2, 80, 0),
    'api': 36103,
    'location': 'View3D > Tool Shelf > 4D Light Field Renderer',
    'url': 'https://github.com/danialbares/Plenoptic-Data-Rendering-Blender-addon',
    'category': 'Render'
}

if "bpy" in locals():
    import imp 
    imp.reload(gui)
    imp.reload(lightfield_simulator)
    imp.reload(updates)
    imp.reload(import_export)
    imp.reload(preferences)
    imp.reload(pointcloud_simulator)
else:
    from . import gui, lightfield_simulator, updates, import_export, preferences, pointcloud_simulator
    
import bpy
from bpy.props import *

import datetime
import os, sys

from . import gui
from . import lightfield_simulator
from . import pointcloud_simulator
from . import import_export
from . import preferences
from .preferences import *
from .pointcloud_simulator import *


# Class for the global variables
class PlenopticAddon:
    
    # Path to the addon directory
    path = bpy.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    tmp_path = bpy.path.abspath(path + "/tmp/")
    libpath = bpy.path.abspath(path + "/lib/")
    
    python_dependencies = [
                            ('pynng', 'pynng', ''),
                            ('cv2', 'opencv-python', ''),
                            ('PIL', 'Pillow', ''),
                            ]
                            

    # Append the add-on's path to Blender's python path
    sys.path.insert(0, libpath)
    sys.path.insert(0, path)
    
    # Method that checks if a specific module is installed in the lib directory
    @classmethod
    def is_installed(self, module, found=False):
        
        import importlib.machinery
        import sys

        # Extract information of the module
        module_name, install_name, install_version = module

        # Try to find the module in the "lib" directory
        module_spec = (importlib.machinery.PathFinder().find_spec(module_name, [self.libpath]))
        if module_spec:
            return True
        else:
            return False
    
    
    # Method that checks if all dependencies can be found in the "lib" directory
    @classmethod
    def check_dependencies(self, found=False):

        # Boolean to return if all the dependencies are found
        found_all = True

        # Checks if the modules are installed
        for module in self.python_dependencies:
            if not self.is_installed(module, found):
                found_all = False

        return found_all
    
    
    
# Global properties for the script, Mainly for UI
class LFPropertyGroup(bpy.types.PropertyGroup):
    
    
    # camera parameters
    focal_length: FloatProperty(
        name='Focal length [mm]',
        default=100,
        min=0,
        max=1000,
        description='Focal length of cameras [mm]',
        update=updates.update_lightfield
    )
    x_res: IntProperty(
        name='X:',
        default=512,
        min=1,
        max=10000,
        description='Image resolution in x direction [px]',
        update=updates.update_lightfield
    )
    y_res: IntProperty(
        name='Y:',
        default=512,
        min=1,
        max=10000,
        description='Image resolution in y direction [px]',
        update=updates.update_lightfield
    )
    sensor_size: FloatProperty(
        name='Sensor size [mm]',
        default=35,
        min=1,
        max=1000,
        description='Sensor chip size in [mm]',
        update=updates.update_lightfield
    )
    fstop: FloatProperty(
        name='f-Stop',
        default=1,
        min=0,
        max=300,
        description='Amount of focus. The lower, the blurrier',
        update=updates.update_lightfield
    )
    show_one_camera: BoolProperty(
        name='Show a view with only one camera',
        default=False,
        description='Whether to show one camera or all of them.'
    )
    

    # Light field parameters
    num_cams_x: IntProperty(
        name='Number of cameras X',
        default=3,
        min=1,
        max=2000,
        description='Number of cameras in x direction',
        update=updates.update_number_of_cameras
    )
    num_cams_y: IntProperty(
        name='Number of cameras Y',
        default=3,
        min=1,
        max=2000,
        description='Number of cameras in y direction',
        update=updates.update_number_of_cameras
    )
    baseline_mm: FloatProperty(
        name='Baseline [mm]',
        default=50.0,
        min=0.01,
        max=15000,
        description='Distance between each pair of cameras in array in [mm]',
        update=updates.update_baseline
    )
    focus_dist: FloatProperty(
        name='Focus distance [m]',
        default=8,
        min=0,
        max=10000,
        description='Distance where cameras are focused [m]',
        update=updates.update_lightfield
    )
    focus_separation: FloatProperty(
        name='Focus separation [m]',
        default=5,
        min=0,
        max=1000,
        description='Focus separation between stack captures [m]',
        update=updates.update_lightfield
    )
    focus_steps: IntProperty(
        name='Focus steps',
        default=5,
        min=0,
        max=50,
        description='Number of captures for the focus stack generation',
        update=updates.update_lightfield
    )
    depth_map_scale: FloatProperty(
        name='Depth Map Scale',
        default=10.0,
        description='Factor for the high resolution depth map export'
    )
    save_depth_for_all_views: BoolProperty(
        name='Save depth maps for all views',
        default=False,
        description='Whether to save disp/depth maps for all views or only for center view'
    )
    save_object_id_maps_for_all_views: BoolProperty(
        name='Save object id maps for all views',
        default=False,
        description='Whether to save object id maps for all views or only for center view'
    )
    save_depth_as_png: BoolProperty(
        name='Save depth and disparity maps as png',
        default=False,
        description='Whether to save disp/depth maps as png or not'
    )
    save_depth_as_pfm: BoolProperty(
        name='Save depth and disparity maps as pfm',
        default=False,
        description='Whether to save disp/depth maps as pfm or not'
    )
    save_lenslet_image: BoolProperty(
        name='Save lightfield as a lenslet image',
        default=False,
        description='Save all of the rendered perspectives as a lenslet image'
    )
    save_sidebyside_image: BoolProperty(
        name='Save lightfield as a side-by-side image',
        default=False,
        description='Save a side-by-side image with the center perspective and the disparity map'
    )
    sequence_start: IntProperty(
        name='Start frame',
        default=0,
        description='The frame in the timeline where to start recording the LF movie'
    )
    sequence_end: IntProperty(
        name='End frame',
        default=0,
        description='The frame in the timeline where to stop recording the LF movie'
    )
    sequence_steps: IntProperty(
        name='Frame steps',
        default=1,
        min=1,
        max=20,
        description='Step length from one to the next frame, i.e. to downsample the movie'
    )
    
    
    # File IO
    tgt_dir: StringProperty(
        name='',
        subtype='FILE_PATH',
        default=updates.get_default_target_directory(),
        description='Target directory for blender output',
        update=updates.update_target_directory
    )
    path_config_file: StringProperty(
        name='',
        subtype='FILE_PATH',
        default=updates.get_default_path_config_file(),
        description='File path for light field config file',
        update=updates.update_path_config_file
    )

    # Meta information
    min_disp: FloatProperty(
        name='min_disp[px]',
        default=-2.0,
        min=-20.0,
        max=20.0,
        description='Min disparity of the scene in [px]',
    )
    max_disp: FloatProperty(
        name='max_disp[px]',
        default=2.0,
        min=-20.0,
        max=20.0,
        description='Max disparity the scene in [px]',
    )
    frustum_min_disp: FloatProperty(
        name='Frustum Min Disparity [px]',
        default=-2.0,
        min=-20.0,
        max=20.0,
        description='Min disparity of frustum in [px]',
        update=updates.update_lightfield
    )
    frustum_max_disp: FloatProperty(
        name='Frustum Max Disparity [px]',
        default=2.0,
        min=-20.0,
        max=20.0,
        description='Max disparity of frustum in [px]',
        update=updates.update_lightfield
    )    
    authors: StringProperty(
        name='',
        default='Daniel Albares',
        description='Author(s) of the scene'
    )
    category: StringProperty(
        name='',
        default='test',
        description='Scene category, e.g. test, training, stratified'
    )
    scene: StringProperty(
        name='',
        default='Scene_00',
        description='Name of the scene'
    )
    contact: StringProperty(
        name='',
        default='contact@lightfield-analysis.net',
        description='Contact information'
    )
    date: StringProperty(
        name='',
        default=str(datetime.date.today()),
        description='Creation date'
    )
    version: StringProperty(
        name='',
        default="v0",
        description='Version of the scene'
    )
    point_cloud_name: StringProperty(
        name='',
        default='PointCloud0',
        description='Name of the ply file to be saved'
    )

    # Private variables to manage internal computations, no access from GUI interface
    baseline_x_m: FloatProperty(
        name='BaselineX',
        default=0.05,
    )
    baseline_y_m: FloatProperty(
        name='BaselineY',
        default=0.05,
    )
    cycles_seed: IntProperty(
        default=-1
    )
    setup_number: IntProperty(
        default=0
    )
    num_cams_x_hidden: IntProperty(
        default=0
    )
    num_cams_y_hidden: IntProperty(
        default=0
    )
    center_cam_x: FloatProperty(
        name='x',
        default=0.0,
        description='X position of center camera',
    )
    center_cam_y: FloatProperty(
        name='y',
        default=0.0,
        description='Y position of center camera',
    )
    center_cam_z: FloatProperty(
        name='z',
        default=0.0,
        description='Z position of center camera',
    )
    center_cam_rot_x: FloatProperty(
        name='x',
        default=3.141592654 / 2.0,  
        description='Rotation of the center camera around the x axis',
    )
    center_cam_rot_y: FloatProperty(
        name='y',
        default=0.0,
        description='Rotation of the center camera around the y axis',
    )
    center_cam_rot_z: FloatProperty(
        name='z',
        default=-3.141592654 / 2.0,
        description='Rotation of the center camera around the z axis',
    )
    num_blades: FloatProperty(
        name='Blade Number',
        default=8,
        min=0,
        max=10000,
        description='Number of blades in aperture for polygonal bukeh (at least 3)',
        update=updates.update_lightfield
    )
    rotation: FloatProperty(
        name='Rotation [°]',
        default=8,
        min=0,
        max=10000,
        description='Rotation of blades in aperture [°]',
        update=updates.update_lightfield
    )


    @staticmethod
    def get_lightfield_cameras():
        cameras = []
        for obj in bpy.data.objects:
            if obj.type == 'CAMERA' and obj.name.startswith("LF"):
                cameras.append(obj)
        return cameras

    def get_center_camera(self):
        camera_name = self.get_camera_name((self.num_cams_y - 1) / 2, (self.num_cams_x - 1) / 2)
        try:
            camera = bpy.data.objects[camera_name]
        except KeyError:
            print("Could not find center camera: %s" % camera_name)
            return None

        return camera

    def get_frustum(self):
        return bpy.data.objects[self.get_frustum_name()]
    
    def get_focus_planes(self):
        return bpy.data.objects[self.get_focus_planes_name()]

    # scene object names
    def get_frustum_name(self):
        return "LF%s_Frustum" % self.setup_number
    
    def get_focus_planes_name(self):
        return "LF%s_Focus_planes" % self.setup_number

    def get_camera_name(self, i, j):
        return "LF%s_Cam%3.3i" % (self.setup_number, i*self.num_cams_x+j)

    def get_lightfield_name(self):
        return "LF%s" % self.setup_number

    @staticmethod
    def is_valid_directory(tgt_dir):
        if not os.path.isdir(bpy.path.abspath(tgt_dir)):
            print("Could not find directory: '%s'. Trying to create it..." % tgt_dir)
            try:
                os.makedirs(tgt_dir)
            except:
                print("Could not create directory: '%s'" % tgt_dir)
                return False
        return True
   
               
                  
classes = (
    LFPropertyGroup,
    
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    import_export.register();
    lightfield_simulator.register();
    gui.register();
    preferences.register();
    pointcloud_simulator.register();

    bpy.types.Scene.LF = bpy.props.PointerProperty(type=LFPropertyGroup)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    import_export.unregister();
    lightfield_simulator.unregister();
    gui.unregister();
    preferences.unregister();
    pointcloud_simulator.unregister();
    

if __name__ == "__main__":
    register()
