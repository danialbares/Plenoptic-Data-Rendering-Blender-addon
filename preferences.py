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
from .__init__ import *


class ADDON_OT_install_dependencies(bpy.types.Operator):
    bl_idname = "addon.install_dependencies"
    bl_label = "Install missing dependencies"
    bl_description = "Install all Python dependencies required by this add-on to the add-on directory."
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):

        # Check if dependencies are missing
        if not PlenopticAddon.check_dependencies():

            import platform, subprocess
            import datetime

            # Path to python
            python_path = bpy.path.abspath(sys.executable)

            # Install the dependencies to the add-on's lib path
            for module in PlenopticAddon.python_dependencies:
                if not PlenopticAddon.is_installed(module):
                    
                    #subprocess.call([python_path, '-m', 'pip', 'install', '--upgrade', module[1], '--target', PlenopticAddon.libpath, '--no-cache'], stdout=logfile)
                    subprocess.call([python_path, '-m', 'pip', 'install', '--upgrade', module[1], '--target', PlenopticAddon.libpath, '--no-cache'])


        return {'FINISHED'}


class ADDON_PT_install_dependencies(bpy.types.AddonPreferences):
    bl_idname = __package__
    
    def draw(self, context):

        # Notify the user and provide an option to install the needed dependencies
        layout = self.layout
        
        # Button for the installation
        if not PlenopticAddon.check_dependencies():
            layout.alert = True
            row = layout.row()
            row.alignment = 'EXPAND'
            row.scale_y = 0.5
            row.label(text="Some of the Python modules needed for the add-on execution are missing.")
            row = layout.row(align=True)
            row = layout.row()
            row.alignment = 'EXPAND'
            row.scale_y = 0.5
            row.label(text="Please install them before using it. Thanks & enjoy!")
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.operator("addon.install_dependencies", icon='PLUS')

        else:
            layout.alert = False
            row = layout.row()
            row.label(text="All required Python modules were correctly installed :)", icon='INFO')



classes = (
    ADDON_OT_install_dependencies,
    ADDON_PT_install_dependencies,
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


