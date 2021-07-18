import bpy
import imp

from bpy.types import( 
    PropertyGroup,
    # Panel,
    Operator,
    # UIList,
    # AddonPreferences
    )

from bpy.props import(
    FloatProperty,
    PointerProperty,
    StringProperty,
    IntProperty,
    # EnumProperty,
    # BoolProperty
    )

from .. import utils
from . import cmd

imp.reload(utils)
imp.reload(cmd)

#---------------------------------------------------------------------------------------
#Props
#---------------------------------------------------------------------------------------
class CYAUE4TOOLS_Props_OA(PropertyGroup):
    filepath : StringProperty(name = "path")



#---------------------------------------------------------------------------------------
#UI
#---------------------------------------------------------------------------------------
class CYAUE4TOOLS_PT_ui(utils.panel):
    bl_label = "UE4 Tools"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        props = bpy.context.scene.cyaue4tools_props        


        col = self.layout.column(align=False)
        box = col.box()
        box.label(text="Unit Scale")

        box.prop( bpy.context.scene.unit_settings ,"scale_length")

        row = box.row()
        for val in (0.01,1.0,10.0,100.0):
            row.operator( 'cyaue4tools.unitscale',text = str(val) ).value = val
        # row.operator( 'cyaue4tools.unitscale',text = "1.0").mode = 1
        # row.operator( 'cyaue4tools.unitscale',text = "100").mode = 2


        box = col.box()
        box.label(text="Export")

        for mode in ('model','anim','anim_linked','facial'):
            box.operator("cyaue4tools.export" , text = mode ).mode = mode

        row = box.row()
        row.prop(props,"filepath")
        row.operator( 'cyaue4tools.filebrowse' , icon = 'FILE_FOLDER' ,text = "")

        # box = col.box()
        # box.label(text="Adjust ARP")
        # row = box.row()
        # row.operator( 'cyaue4tools.adjust_arp',text = "UE4").mode = 'UE4'
        # row.operator( 'cyaue4tools.adjust_arp',text = "MIXAMO").mode = 'MIXAMO'




#---------------------------------------------------------------------------------------
#FileBrowser
#---------------------------------------------------------------------------------------
class CYAUE4TOOLS_MT_filebrowse(Operator):
    bl_idname = "cyaue4tools.filebrowse"
    bl_label = "Folder"

    filepath : bpy.props.StringProperty(subtype="FILE_PATH")
    filename : StringProperty()
    directory : StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        print((self.filepath, self.filename, self.directory))
        props = bpy.context.scene.cyaue4tools_props        
        props.filepath = self.directory
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#---------------------------------------------------------------------------------------
#Unit Scale
#---------------------------------------------------------------------------------------
class CYAUE4TOOLS_OT_unitscale(bpy.types.Operator):
    """ユニットスケールの変更"""
    bl_idname = "cyaue4tools.unitscale"
    bl_label = ""
    value : FloatProperty()
    def execute(self, context):
        cmd.unitscale(self.value)
        return {'FINISHED'}


# #---------------------------------------------------------------------------------------
# #Adjust ARP
# #---------------------------------------------------------------------------------------
# class CYAUE4TOOLS_OT_adjust_arp(bpy.types.Operator):
#     """UE4,MIXAMOのボーン位置にARPリファレンスボーンを合わせる
#     UE4,またはMIXAMOのアーマチュアを選択し、最後にARPリファレンスボーンを選択して実行する"""
#     bl_idname = "cyaue4tools.adjust_arp"
#     bl_label = ""
#     mode : StringProperty()
#     def execute(self, context):
#         cmd.adjust_arp(self.mode)
#         return {'FINISHED'}


#---------------------------------------------------------------------------------------
#Export
#---------------------------------------------------------------------------------------

#モデルとアニメーションでコレクション＞FBXのリネームが統一されていないのがちょっと問題。
#ModelをCharaに、武器をWeaponにするか？

class CYAUE4TOOLS_OT_export(bpy.types.Operator):
    """FBXファイル出力
命名規則
モデル:00_Model~
アニメーション:00_Anim~
00_Model_CH_Mmob01であればCH_Mmob01.fbxというファイルを出力する。
"""

    bl_idname = "cyaue4tools.export"
    bl_label = "anim export"
    mode : StringProperty()
    def execute(self, context):
        cmd.export(self.mode)
        return {'FINISHED'}


classes = (
    CYAUE4TOOLS_Props_OA,
    CYAUE4TOOLS_PT_ui,
    CYAUE4TOOLS_MT_filebrowse,
    CYAUE4TOOLS_OT_export,
    CYAUE4TOOLS_OT_unitscale,
    #CYAUE4TOOLS_OT_adjust_arp
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.cyaue4tools_props = PointerProperty(type=CYAUE4TOOLS_Props_OA)


def unregister():    
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.cyaue4tools_props

