# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.types import( 
    AddonPreferences
    #PropertyGroup , Panel , Operator ,UIList
    )
import imp

from bpy.props import(
    StringProperty,

    )

from . import maintools
from . import modifierlist
from . import rigtools
from . import importexport
from . import objectlist
from . import idmaptools
from . import ue4tools
# from . import particletools

imp.reload(maintools)
imp.reload(modifierlist)
imp.reload(rigtools)
imp.reload(importexport)
imp.reload(objectlist)
imp.reload(idmaptools)
imp.reload(ue4tools)
# imp.reload(particletools)

bl_info = {
"name": "cyatools",
"author": "Takehito Tsuchiya",
"version": (0, 3),
"blender": (2, 80, 3),
"description": "cyatools",
"category": "Object"}

RIGSHAPEPATH = "E:\data\googledrive\lib\model/rig.blend"

#---------------------------------------------------------------------------------------
#UI Preference
#---------------------------------------------------------------------------------------
class CYATOOLS_MT_addonpreferences(AddonPreferences):
    bl_idname = __name__
 
    shape_path : StringProperty(default = RIGSHAPEPATH )

    def draw(self, context):
        layout = self.layout
        layout.label(text='Rig Shape Path')
        col = layout.column()
        col.prop(self, 'shape_path',text = 'shape_path', expand=True)

#メッセージダイアログ
#スペース区切りで改行する
class CYATOOLS_MT_messagebox(bpy.types.Operator):
    bl_idname = "cyatools.messagebox"
    bl_label = ""
 
    message : bpy.props.StringProperty(
        name = "message",
        description = "message",
        default = ''
    )
 
    def execute(self, context):
        self.report({'INFO'}, self.message)
        print(self.message)
        return {'FINISHED'}
 
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 400)
 
    def draw(self, context):
        buf = self.message.split(' ')
        for s in buf:
            self.layout.label(text = s)
        #self.layout.label("")


classes = (
    CYATOOLS_MT_addonpreferences,
    CYATOOLS_MT_messagebox
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    maintools.register()
    modifierlist.register()
    rigtools.register()
    importexport.register()
    objectlist.register()
    idmaptools.register()
    ue4tools.register()

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    maintools.unregister()
    modifierlist.unregister()
    rigtools.unregister()
    importexport.unregister()
    objectlist.unregister()
    idmaptools.unregister()
    ue4tools.unregister()