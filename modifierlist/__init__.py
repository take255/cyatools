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
from bpy.types import ( PropertyGroup , Panel , Operator ,UIList)
from bpy.app.handlers import persistent
import imp

from bpy.props import(
    PointerProperty,
    IntProperty,
    BoolProperty,
    StringProperty,
    CollectionProperty
    )

from .. import utils
from . import cmd

imp.reload(utils)
imp.reload(cmd)


try:
    bpy.utils.unregister_class(CYAMODIFIERLIST_Props_item)
except:
    pass


CurrentObj = ''
#Modcount = 0

@persistent
def cyamodifierlist_handler(scene):

    props = bpy.context.scene.cyamodifierlist_props
    global CurrentObj
    #global Modcount

    if utils.selected() == []:
        props.handler_through = False
        CurrentObj = ''
        cmd.clear()
        return

    act = utils.getActiveObj()

    #print('handler',props.handler_through)
    if props.handler_through:
        return

    if act == None:
        return


    #選択が変更されたときだけリロード。
    if CurrentObj != act.name:
        print('selection changed')
        cmd.reload()
        CurrentObj = act.name


    #モディファイヤの数に変更があればリロード
    mod_count = len(act.modifiers)
    if props.mod_count != mod_count:
        cmd.reload()
        props.mod_count = mod_count


def cyamodifierlist_handler_(scene):
    props = bpy.context.scene.cyamodifierlist_props
    ui_list = bpy.context.window_manager.cyamodifierlist_list
    act = utils.getActiveObj()

    if props.handler_through:
        return

    if act == None:
        return

    mod_count = len(act.modifiers)

    #選択が変わったときにリロード
    #モディファイヤの数を保持しておく。モディファイヤ数が変わったらリロード
    if props.currentobj != act.name:
        cmd.reload()
        props.currentobj = act.name
        props.mod_count = mod_count
    else:
        if props.mod_count != mod_count:
            cmd.reload()
            props.mod_count = len(act.modifiers)


class CYAMODIFIERLIST_Props_OA(PropertyGroup):
    handler_through : BoolProperty(default = False)
    currentobj : StringProperty(maxlen=63)
    mod_count : IntProperty()


#---------------------------------------------------------------------------------------
#modifierList
#---------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------
#リスト内のアイテムの見た目を指定
#---------------------------------------------------------------------------------------
class CYAMODIFIERLIST_UL_uilist(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            #item.nameが表示される
            layout.prop(item, "bool_val", text = "")
            layout.prop(item, "name", text="", emboss=False, icon_value=icon)

            #layout.label(item.name, icon_value='BONE_DATA')

        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


#---------------------------------------------------------------------------------------
#リスト名 , list_id can be ””　，item_ptr ,item , index_pointer ,active_index
#active_indexをui_list.active_indexで取得できる
#---------------------------------------------------------------------------------------
class CYAMODIFIERLIST_PT_ui(utils.panel):
    bl_label = "Modifier List"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self , width=400)

    def draw(self, context):
        layout=self.layout
        row = layout.row()

        col = row.column()
        ui_list = context.window_manager.cyamodifierlist_list

        col.template_list("CYAMODIFIERLIST_UL_uilist", "", ui_list, "itemlist", ui_list, "active_index", rows=8)
        col = row.column(align=True)

        col.operator("cyamodifierlist.modifierlist_apply", icon='MODIFIER_ON')
        col.operator("cyamodifierlist.modifierlist_apply_checked", icon='CHECKBOX_HLT')
        col.operator("cyamodifierlist.modifierlist_remove", icon='TRASH')
        col.operator("cyamodifierlist.modifierlist_move_item", icon=utils.icon['UP']).dir = 'TOP'
        col.operator("cyamodifierlist.modifierlist_move_item", icon='TRIA_UP').dir = 'UP'
        col.operator("cyamodifierlist.modifierlist_move_item", icon='TRIA_DOWN').dir = 'DOWN'
        col.operator("cyamodifierlist.modifierlist_move_item", icon=utils.icon['DOWN']).dir = 'BOTTOM'


#---------------------------------------------------------------------------------------
#リストのアイテムに他の情報を埋め込みたい場合はプロパティを追加できるのでいろいろ追加してみよう。
#ここでレジストしないと不具合がでる。register()に含めたいところだが。
#TestCollectionPropertyのitemListの型として指定する必要があるので後でレジストできない
#---------------------------------------------------------------------------------------

class CYAMODIFIERLIST_Props_item(PropertyGroup):
    name : StringProperty(get=cmd.get_item, set=cmd.set_item)
    bool_val : BoolProperty( update = cmd.showhide )

bpy.utils.register_class(CYAMODIFIERLIST_Props_item)


#---------------------------------------------------------------------------------------
#アイテムのリストクラス
#複数のアイテムをリストに持ち、リストにアイテムを加えたり、選択したリストを取得したりする。
#このクラス自体はuiをもっているわけではないので、現在リストで選択されているインデックスを取得する必要がある。
#
#col.template_list("Modifierlist_group_list", "", ui_list, "itemlist", ui_list, "active_index", rows=3)
#template_listで選択されたアイテムのインデックスをactive_indexに渡すため、上のように指定する必要がある。

#CollectionPropertyへの追加方法例
# item = self.list.add()
# item.name = bone.name
# item.int_val = 10
#---------------------------------------------------------------------------------------
class CYAMODIFIERLIST_Props_list(PropertyGroup):
    active_index : IntProperty()
    itemlist : CollectionProperty(type=CYAMODIFIERLIST_Props_item)#アイテムプロパティの型を収めることができるリストを生成



class CYAMODIFIERLIST_OT_move_item(Operator):
    """アイテムの移動"""
    bl_idname = "cyamodifierlist.modifierlist_move_item"
    bl_label = ""
    dir : StringProperty(default='UP')

    def execute(self, context):
        cmd.move(self.dir)
        return {'FINISHED'}

class CYAMODIFIERLIST_OT_apply(Operator):
    """選択をapply"""
    bl_idname = "cyamodifierlist.modifierlist_apply"
    bl_label = ""

    def execute(self, context):
        cmd.apply()
        return {'FINISHED'}

class CYAMODIFIERLIST_OT_apply_checked(Operator):
    """チェックされたものをapply"""
    bl_idname = "cyamodifierlist.modifierlist_apply_checked"
    bl_label = ""

    def execute(self, context):
        cmd.apply_checked()
        return {'FINISHED'}

class CYAMODIFIERLIST_OT_remove(Operator):
    """チェックされたものを削除"""
    bl_idname = "cyamodifierlist.modifierlist_remove"
    bl_label = ""

    def execute(self, context):
        cmd.remove()
        return {'FINISHED'}


classes = (
    CYAMODIFIERLIST_Props_OA,
    CYAMODIFIERLIST_PT_ui,

    CYAMODIFIERLIST_Props_list,
    CYAMODIFIERLIST_UL_uilist,
    CYAMODIFIERLIST_OT_move_item,
    CYAMODIFIERLIST_OT_apply,
    CYAMODIFIERLIST_OT_apply_checked,
    CYAMODIFIERLIST_OT_remove
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.cyamodifierlist_props = PointerProperty(type=CYAMODIFIERLIST_Props_OA)
    bpy.types.WindowManager.cyamodifierlist_list = PointerProperty(type=CYAMODIFIERLIST_Props_list)

    bpy.app.handlers.depsgraph_update_pre.append(cyamodifierlist_handler)
    bpy.app.handlers.undo_post.append(cyamodifierlist_handler)
    bpy.app.handlers.redo_post.append(cyamodifierlist_handler)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.cyamodifierlist_props
    del bpy.types.WindowManager.cyamodifierlist_list

    bpy.app.handlers.depsgraph_update_pre.remove(cyamodifierlist_handler)
    bpy.app.handlers.undo_post.remove(cyamodifierlist_handler)
    bpy.app.handlers.redo_post.remove(cyamodifierlist_handler)

