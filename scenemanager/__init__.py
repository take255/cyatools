import bpy
from bpy.types import ( PropertyGroup ,Operator, UIList)
import imp
import subprocess
from bpy.app.handlers import persistent


from bpy.props import(
    PointerProperty,
    IntProperty,
    StringProperty,
    CollectionProperty,
    BoolProperty,
    EnumProperty,
    )

from .. import utils
from . import cmd

imp.reload(utils)
imp.reload(cmd)


#---------------------------------------------------------------------------------------
#シーンが開かれたときと保存した時、自動でリロードする
#---------------------------------------------------------------------------------------
@persistent
def cyascenemanager_handler(dummy):
    #print("Load Handler:", bpy.data.filepath)
    cmd.setproject()


#---------------------------------------------------------------------------------------
#
#---------------------------------------------------------------------------------------
class CYASCENEMANAGER_Props_OA(PropertyGroup):
    #copy_target : EnumProperty(items= (('svn', 'svn', 'SVN'),('work', 'work', 'work'),('backup', 'backup', 'Backup'),('onedrive', 'onedrive', 'onedrive')  ))
    copy_target : EnumProperty(items= (('svn', '', '','EVENT_S',0),('work', '', '','EVENT_W',1),('backup', '', '','EVENT_B',2),('onedrive', '', '','EVENT_O',3)  ))
    switch_path : EnumProperty(items= (('svn', '', '','EVENT_S',0),('work', '', '','EVENT_W',1),('backup', '', '','EVENT_B',2),('onedrive', '', '','EVENT_O',3)),update = cmd.switch_path)
    #copy_target : EnumProperty(items= (('svn', 'svn', '','EVENT_S'),('work', 'work', '','EVENT_S'),('backup', 'backup', '','EVENT_S'),('onedrive', 'onedrive', '','EVENT_S')  ))
    #switch_path : EnumProperty(items= (('svn', 'svn', 'SVN'),('work', 'work', 'work'),('backup', 'backup', 'Backup'),('onedrive', 'onedrive', 'onedrive')  ))

    svn_root : StringProperty(name="svn root",  default=r'D:\Prj\B01\Assets' )
    work_root : StringProperty(name="work root", default= r'E:\data\project\YKS')
    backup_root : StringProperty(name="backup root", default= r'E:\data\project\YKSBuckup')
    onedrive_root : StringProperty(name="onedrive root", default= r'E:\data\OneDrive\projects\YKS')

    svn_dir : StringProperty(name="svn dir")
    work_dir : StringProperty(name="work dir")
    backup_dir : StringProperty(name="backup dir")
    onedrive_dir : StringProperty(name="onedrive dir")

    current_root :StringProperty(name="current root")
    relative_path :StringProperty(name="relative_path")


    #UI用プロパティ
    current_dir : StringProperty(name = "")
    selected_file : StringProperty(name = "")
    add_work : BoolProperty(default=False)


    #full_path :StringProperty(name="path")


#---------------------------------------------------------------------------------------
#
#---------------------------------------------------------------------------------------
class CYASCENEMANAGER_UL_uilist(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:


            layout.prop(item, "bool_val", text = "")



            #ファイルタイプによってアイコンを変える
            if item.filetype == 'blend':
                ic = 'FILE_BLEND'
                mode = 'blend'

            elif item.filetype == 'image':
                ic = 'FILE_IMAGE'
                mode = 'blend'

            elif item.filetype == 'dir':
                ic = 'FILE_FOLDER'
                mode = 'dir'
            else:
                ic = 'FILE_BLANK'
                mode = 'file'


            l = layout.operator( "cyascenemanager.dir",text="", icon=ic, emboss=False)
            l.mode = mode
            l.name = item.name


            layout.prop(item, "name", text="", emboss=False, icon_value=icon)

        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

#---------------------------------------------------------------------------------------
#
#---------------------------------------------------------------------------------------
class CYASCENEMANAGER_PT_scenemanager(utils.panel):
    bl_label = "Scene Manager"

    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        ui_list = context.window_manager.cyascenemanager_list
        prop = bpy.context.scene.cyascenemanager_oa

        layout=self.layout

        row = layout.row(align=False)
        col = row.column()

        box = col.box()
        row = box.row()
        row.operator("cyascenemanager.go_up_dir", text = '' , icon= 'FILE_PARENT')
        row.operator("cyascenemanager.open_file", icon = 'FILE')
        #row.operator("cyascenemanager.save_file", icon = 'FILE_NEW')
        row.operator("cyascenemanager.open_explorer", text = '' , icon= 'FILE_FOLDER')
        row.operator("cyascenemanager.reload" , icon  ='FILE_REFRESH' )

        # row.operator("cyascenemanager.switch_work", icon = 'EVENT_S').mode = 'svn'
        # row.operator("cyascenemanager.switch_work", icon = 'EVENT_W').mode = 'work'
        # row.operator("cyascenemanager.switch_work", icon = 'EVENT_B').mode = 'backup'
        # row.operator("cyascenemanager.switch_work", icon = 'EVENT_O').mode = 'onedrive'

        row.prop(prop,"switch_path", expand=True)





        col = box.column()
        #row = col.row()
        col.prop(prop,"current_dir")

        col.template_list("CYASCENEMANAGER_UL_uilist", "", ui_list, "itemlist", ui_list, "active_index", rows=8)

        row = col.row()
        row.prop(prop,"selected_file")
        row.operator("cyascenemanager.save_file", icon = 'FILE_NEW')


        box = col.box()
        box.label(text="Copy Move")
        col = box.column()
        row = col.row()
        row.prop(prop,"copy_target", expand=True)

        row = col.row()
        row.operator("cyascenemanager.move", text = 'copy').mode = 'copy'
        row.operator("cyascenemanager.move", text = 'move').mode = 'move'
        #row.operator("cyascenemanager.move_otherdir", text = 'move')
        row.operator("cyascenemanager.save_as_work" , icon = 'COPYDOWN')

        row = col.row()
        row.operator("cyascenemanager.load_textures" )

        row.prop(prop,"add_work" )
        #row.operator("cyascenemanager.save_onedrive" )



class CYASCENEMANAGER_Props_item(PropertyGroup):
    name : StringProperty()
    bool_val : BoolProperty()
    filetype : StringProperty()

bpy.utils.register_class(CYASCENEMANAGER_Props_item)


#---------------------------------------------------------------------------------------
class CYASCENEMANAGER_Props_list(PropertyGroup):
    active_index : IntProperty( update = cmd.selection_changed )
    itemlist : CollectionProperty(type=CYASCENEMANAGER_Props_item)#アイテムプロパティの型を収めることができるリストを生成


#---------------------------------------------------------------------------------------
#
#---------------------------------------------------------------------------------------
class CYASCENEMANAGER_OT_save_as_work(Operator):
    """現在ひらいているシーンをバックアップする"""
    bl_idname = "cyascenemanager.save_as_work"
    bl_label = ""

    def execute(self, context):
        cmd.save_backup()
        return {'FINISHED'}

class CYASCENEMANAGER_OT_load_textures(Operator):
    bl_idname = "cyascenemanager.load_textures"
    bl_label = "load_textures"
    def execute(self, context):
        print("sssss")
        cmd.load_textures()
        return {'FINISHED'}

class CYASCENEMANAGER_OT_move(Operator):
    bl_idname = "cyascenemanager.move"
    bl_label = "move"
    mode : StringProperty()

    def execute(self, context):
        cmd.move(self.mode)
        return {'FINISHED'}


# class CYASCENEMANAGER_OT_move_otherdir(Operator):
#     bl_idname = "cyascenemanager.move_otherdir"
#     bl_label = ""
#     mode : StringProperty()

#     def execute(self, context):
#         print("sssss")
#         print(self.mode)
#         cmd.move_otherdir(self.mode)
#         return {'FINISHED'}

# class CYASCENEMANAGER_OT_switch_work(Operator):
#     """パスチェンジ"""
#     bl_idname = "cyascenemanager.switch_work"
#     bl_label = ""
#     mode : StringProperty()

    # def execute(self, context):
    #     cmd.switch_work(self.mode)
    #     return {'FINISHED'}


class CYASCENEMANAGER_OT_open_file(Operator):
    bl_idname = "cyascenemanager.open_file"
    bl_label = ""

    def execute(self, context):
        cmd.open_file()
        return {'FINISHED'}

class CYASCENEMANAGER_OT_save_file(Operator):
    bl_idname = "cyascenemanager.save_file"
    bl_label = ""

    def execute(self, context):
        cmd.save_file()
        return {'FINISHED'}


# class CYASCENEMANAGER_OT_save_onedrive(Operator):
#     bl_idname = "cyascenemanager.save_onedrive"
#     bl_label = ""

#     def execute(self, context):
#         cmd.save_onedrive()
#         return {'FINISHED'}


#---------------------------------------------------------------------------------------
#
#ディレクトリ操作
#
#---------------------------------------------------------------------------------------

class CYASCENEMANAGER_OT_reload(Operator):
    """リロード"""
    bl_idname = "cyascenemanager.reload"
    bl_label = ""

    def execute(self, context):
        cmd.setproject()
        return {'FINISHED'}


#１階層上に上る
class CYASCENEMANAGER_OT_go_up_dir(Operator):
    bl_idname = "cyascenemanager.go_up_dir"
    bl_label = ""

    def execute(self, context):
        cmd.go_up_dir()
        return {'FINISHED'}


#ディレクトリかファイルか
class CYASCENEMANAGER_OT_dir(Operator):
    bl_idname = "cyascenemanager.dir"
    bl_label = ""
    mode : StringProperty()
    name : StringProperty()

    def execute(self, context):
        cmd.go_down_dir(self.mode,self.name)
        return {'FINISHED'}


class CYASCENEMANAGER_OT_blend(Operator):
    bl_idname = "cyascenemanager.blend"
    bl_label = ""


class CYASCENEMANAGER_OT_open_explorer(Operator):
    bl_idname = "cyascenemanager.open_explorer"
    bl_label = ""

    def execute(self, context):
        prop = bpy.context.scene.cyascenemanager_oa
        subprocess.Popen(["explorer", prop.current_dir ], shell=True)
        return {'FINISHED'}






# class CYASCENEMANAGER_OT_convert_vertex_color(Operator):
#     """シェーダーはPrincipled BSDFにすること"""
#     bl_idname = "CYASCENEMANAGER.convert_vertex_color"
#     bl_label = "convert vtxcolor"
#     def execute(self, context):
#         cmd.convert_vertex_color()
#         return {'FINISHED'}

# class CYASCENEMANAGER_OT_pick_vertex_color(Operator):
#     """ First, select polugon face (not vertex) and execute this command."""
#     bl_idname = "CYASCENEMANAGER.pick_vertex_color"
#     bl_label = ""
#     mode : IntProperty()
#     def execute(self, context):
#         cmd.pick_vertex_color(self.mode)
#         return {'FINISHED'}






classes = (
    CYASCENEMANAGER_Props_OA,
    CYASCENEMANAGER_UL_uilist,
    CYASCENEMANAGER_Props_list,
    CYASCENEMANAGER_PT_scenemanager,
    CYASCENEMANAGER_OT_save_as_work,
    CYASCENEMANAGER_OT_reload,
    CYASCENEMANAGER_OT_move,
    #CYASCENEMANAGER_OT_switch_work,
    #CYASCENEMANAGER_OT_switch_backup,
    CYASCENEMANAGER_OT_open_file,
    CYASCENEMANAGER_OT_save_file,
    #CYASCENEMANAGER_OT_save_onedrive,

    CYASCENEMANAGER_OT_dir,
    CYASCENEMANAGER_OT_blend,
    CYASCENEMANAGER_OT_go_up_dir,
    CYASCENEMANAGER_OT_open_explorer,

    CYASCENEMANAGER_OT_load_textures

#     CYASCENEMANAGER_PT_materialtools,
#     CYASCENEMANAGER_OT_assign_vertex_color,
#     CYASCENEMANAGER_OT_convert_vertex_color,
#     CYASCENEMANAGER_OT_pick_vertex_color
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.cyascenemanager_oa = PointerProperty(type=CYASCENEMANAGER_Props_OA)
    bpy.types.WindowManager.cyascenemanager_list = PointerProperty(type=CYASCENEMANAGER_Props_list)

    bpy.app.handlers.load_post.append(cyascenemanager_handler)
    bpy.app.handlers.save_post.append(cyascenemanager_handler)



def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.cyascenemanager_oa
    del bpy.types.WindowManager.cyascenemanager_list

    bpy.app.handlers.depsgraph_update_pre.remove(cyascenemanager_handler)
    bpy.app.handlers.depsgraph_update_pre.remove(cyascenemanager_handler)


