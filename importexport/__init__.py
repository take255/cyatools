import bpy
import imp
from pathlib import Path

from bpy.types import(
    PropertyGroup,
    Panel,
    Operator,
    UIList,
    AddonPreferences
    )

from bpy.props import(
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty
    )

from .. import utils
from . import cmd

imp.reload(utils)
imp.reload(cmd)

PATH = 'E:/data/blender_ref/pickle/'
MODEL_NAME = 'model.dat'
BONE_NAME = 'bonedata.dat'
AXIS = (('X','X','X'), ('Y','Y','Y'), ('Z','Z','Z'), ('-X','-X','-X'), ('-Y','-Y','-Y'), ('-Z','-Z','-Z'))
WORLD = (('Blender','Blender','Blender'), ('Maya','Maya','Maya'))

def fullpath(path,filename):
    if path[-1] != '/':
        path += '/'
    return path + filename

def modelname():
    prefs = bpy.context.preferences.addons[__name__].preferences
    return fullpath(prefs.path,prefs.model_name)

def bonename():
    prefs = bpy.context.preferences.addons[__name__].preferences
    return fullpath(prefs.path,prefs.bone_name)

def weightname():
    #prefs = bpy.context.preferences.addons[__name__].preferences
    path = bpy.context.preferences.addons['cyatools'].preferences.importexport
    return path

def animname():
    prefs = bpy.context.preferences.addons[__name__].preferences
    return fullpath(prefs.path,'test.anim')

#---------------------------------------------------------------------------------------
#Props
#---------------------------------------------------------------------------------------
class CYAIMPORTEXPORT_Props_OA(PropertyGroup):
    #option
    upvector : EnumProperty(items = WORLD , name = 'bone upvector',default = 'Blender' )
    add_tipbones : BoolProperty(name="add tip bones" ,  default = False)

    #FBX option
    scale : FloatProperty(name="scale",min=0.001,default=1.0)
    export_option : EnumProperty(items= (('sel', 'sel', '選択されたもの'),('eachsel', 'eachsel', 'Export selection to each file'),('col', 'col', 'colコレクション')))
    export_mode : EnumProperty(items= (('def', 'def', 'Default'),('ue', 'ue', 'ForUnrealEngine'),('md', 'md', 'ForMarverousDesigner')))
    fbx_path : StringProperty(name = "path")
    axis_forward : EnumProperty(items = AXIS , name = 'forward',default = '-Y' )
    axis_up : EnumProperty(items = AXIS , name = 'up' ,default = 'Z')

    temp_unitscale_enable : BoolProperty(name="enable" ,  default = False)
    temp_unitscale : FloatProperty(name="unit scale",min=0.001,default=1.0)
    export_frame : IntProperty(name="frame" , default= 0 )


#---------------------------------------------------------------------------------------
#UI Preference
#---------------------------------------------------------------------------------------
class CYAIMPORTEXPORT_MT_addonpreferences(AddonPreferences):
    bl_idname = __name__

    path : StringProperty(default = PATH)
    model_name : StringProperty(default = MODEL_NAME)
    bone_name : StringProperty(default = BONE_NAME)

    def draw(self, context):
        layout = self.layout
        layout.label(text='File Path & File Name')
        col = layout.column()
        col.prop(self, 'path',text = 'path', expand=True)

        row = col.row()
        row.prop(self, 'model_name',text = 'model name', expand=True)
        row.prop(self, 'bone_name',text = 'bone name', expand=True)


#---------------------------------------------------------------------------------------
#UI
#---------------------------------------------------------------------------------------
class CYAIMPORTEXPORT_PT_ui(utils.panel):
    bl_label = "Import Export"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        props = bpy.context.scene.cyaimportexport_props

        col = self.layout.column()
        self.row = col.row()
        self.ui( "mesh" , "cyaimportexport.mesh_export" , "cyaimportexport.mesh_import" )
        self.ui( "weight" , "cyaimportexport.weight_export" , "cyaimportexport.weight_import" )
        self.ui( "bone" , "cyaimportexport.bone_export" , "cyaimportexport.bone_import")
        self.ui( "anim" , "cyaimportexport.anim_export" , "cyaimportexport.anim_import")


        box = col.box()
        box.label(text="Export Settings")
        box.prop(props, 'upvector', icon='BLENDER' )
        box.prop(props, 'add_tipbones')



        box = col.box()
        box.label(text="FBX")

        row = box.row()
        row.operator( 'cyaimportexport.export_format' , text = 'Export FBX' , icon = 'FILE_TICK').mode = 'fbx'
        row.operator( 'cyaimportexport.export_format' , text = 'Export OBJ' , icon = 'FILE_TICK').mode = 'obj'

        row = box.row()
        row.prop(props,"export_option", expand=True)
        row.prop(props,"export_mode", expand=True)

        row = box.row()
        row.prop(props,"fbx_path")
        row.operator( 'cyaimportexport.filebrowse' , icon = 'FILE_FOLDER' ,text = "")


        box = col.box()
        box.label(text="Temporary Unit Scale")
        row = box.row()
        row.prop(props, 'temp_unitscale_enable')
        row.prop(props, 'temp_unitscale', icon='BLENDER')


        row0 = col.row()
        box = row0.box()
        box.label(text="Export Frame Number")
        row = box.row()
        row.prop(props, 'export_frame')

        row0 = col.row()
        box = row0.box()
        box.label(text="Scale")
        col1=box.column()
        col1.prop(props, 'scale', icon='BLENDER', toggle=True)

        row = col1.row()
        row.prop(props, 'axis_forward', icon='BLENDER' )
        row.prop(props, 'axis_up', icon='BLENDER')


        row0 = col.row()
        box = row0.box()
        box.operator( 'cyaimportexport.rot90')



    def ui(self , name , oncmd ,offcmd ):
        box = self.row.box()
        box.label( text = name )

        row = box.row(align=True)
        row.operator( oncmd , icon = 'FILE_TICK')
        row.operator( offcmd, icon = 'FILEBROWSER')


class CYAIMPORTEXPORT_MT_filebrowse(Operator):
    bl_idname = "cyaimportexport.filebrowse"
    bl_label = "Folder"

    filepath : bpy.props.StringProperty(subtype="FILE_PATH")
    filename : StringProperty()
    directory : StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        #print(self.filepath)
        print((self.filepath, self.filename, self.directory))
        props = bpy.context.scene.cyaimportexport_props
        props.fbx_path = self.directory
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}



class CYAIMPORTEXPORT_mesh_export(Operator):
    """メッシュ情報をエクスポート"""
    bl_idname = "cyaimportexport.mesh_export"
    bl_label = ""
    def execute(self, context):
        cmd.mesh_export( modelname() )
        return {'FINISHED'}

class CYAIMPORTEXPORT_mesh_import(Operator):
    """メッシュ情報をインポート"""
    bl_idname = "cyaimportexport.mesh_import"
    bl_label = ""
    def execute(self, context):
        cmd.mesh_import( modelname() )
        return {'FINISHED'}

class CYAIMPORTEXPORT_weight_export(Operator):
    """ウェイト情報をエクスポート"""
    bl_idname = "cyaimportexport.weight_export"
    bl_label = ""
    def execute(self, context):
        cmd.weight_export(weightname())
        return {'FINISHED'}

class CYAIMPORTEXPORT_weight_import(Operator):
    """ウェイト情報をインポート"""
    bl_idname = "cyaimportexport.weight_import"
    bl_label = ""
    def execute(self, context):
        cmd.weight_import(weightname())
        return {'FINISHED'}

class CYAIMPORTEXPORT_bone_export(Operator):
    """ボーン情報をエクスポート"""
    bl_idname = "cyaimportexport.bone_export"
    bl_label = ""
    def execute(self, context):
        cmd.bone_export( bonename() )
        return {'FINISHED'}

class CYAIMPORTEXPORT_bone_import(Operator):
    """ボーン情報をインポート"""
    bl_idname = "cyaimportexport.bone_import"
    bl_label = ""
    def execute(self, context):
        cmd.bone_import( bonename() )
        return {'FINISHED'}

class CYAIMPORTEXPORT_anim_export(Operator):
    """アニメーション情報をエクスポート"""
    bl_idname = "cyaimportexport.anim_export"
    bl_label = ""
    def execute(self, context):
        cmd.anim_export(animname())
        return {'FINISHED'}

class CYAIMPORTEXPORT_anim_import(Operator):
    """アニメーション情報をインポート"""
    bl_idname = "cyaimportexport.anim_import"
    bl_label = ""
    def execute(self, context):
        cmd.anim_import(animname())
        return {'FINISHED'}


#FBX
class CYAIMPORTEXPORT_export_format(Operator):
    """選択されているモデルのFBX出力"""
    bl_idname = "cyaimportexport.export_format"
    bl_label = ""
    mode : StringProperty(default='fbx')

    def execute(self, context):
        cmd.export_format(self.mode)
        return {'FINISHED'}

# #OBJ
# class CYAIMPORTEXPORT_export_obj(Operator):
#     """選択されているモデルのOBJ出力"""
#     bl_idname = "cyaimportexport.export_obj"
#     bl_label = "Export OBJ"
#     def execute(self, context):
#         cmd.export_obj()
#         return {'FINISHED'}


#FBX
class CYAIMPORTEXPORT_rot90(Operator):
    """X軸に90度回転を入れる
    Unityなどで90度入ってしまうのを回避する
    """
    bl_idname = "cyaimportexport.rot90"
    bl_label = "rot90"

    def execute(self, context):
        cmd.rot90()
        return {'FINISHED'}


classes = (
    CYAIMPORTEXPORT_Props_OA,
    CYAIMPORTEXPORT_PT_ui,
    CYAIMPORTEXPORT_MT_addonpreferences,

    CYAIMPORTEXPORT_mesh_export,
    CYAIMPORTEXPORT_mesh_import,
    CYAIMPORTEXPORT_weight_export,
    CYAIMPORTEXPORT_weight_import,
    CYAIMPORTEXPORT_bone_export,
    CYAIMPORTEXPORT_bone_import,
    CYAIMPORTEXPORT_anim_export,
    CYAIMPORTEXPORT_anim_import,


    CYAIMPORTEXPORT_export_format,
    CYAIMPORTEXPORT_MT_filebrowse,

    CYAIMPORTEXPORT_rot90

)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.cyaimportexport_props = PointerProperty(type=CYAIMPORTEXPORT_Props_OA)



def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.cyaimportexport_props

