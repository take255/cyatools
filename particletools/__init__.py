import bpy
#from bpy.types import ( PropertyGroup , Panel , Operator ,UIList)
from bpy.types import ( PropertyGroup , Panel , Operator , UIList )
import imp
from bpy.app.handlers import persistent

from bpy.props import(
    PointerProperty,
    IntProperty,
    BoolProperty,
    StringProperty,
    CollectionProperty,
    FloatProperty,
    # EnumProperty
    )

from . import utils
from . import cmd

imp.reload(utils)
imp.reload(cmd)

bl_info = {
"name": "cya_particletools",
"author": "kisecyakeshi",
"version": (0, 1),
"blender": (2, 80, 0),
"description": "cya_particletools",
"category": "Object"}


try: 
    bpy.utils.unregister_class(CYAPARTICLETOOLS_Props_item)
except:
    pass


#Handler_through = False
CurrentObj = ''
CurrentProp = 0
CurrentList = 0

#---------------------------------------------------------------------------------------
#オブジェクトを選択したときにパーティクルセッティングをリストに追加
#パーティクルプロパティとリストで同期をとる
#選択をグローバルにとっておき比較
#---------------------------------------------------------------------------------------
@persistent
def cyaparticletools_handler(scene):
    #global Handler_through

    global CurrentObj
    global CurrentProp
    global CurrentList#ツールのリストインデックス


    if utils.selected() == []:
        print('aaa')
        CurrentObj = ''
        cmd.clear()
        return

    act = utils.getActiveObj()
    
    #print(CurrentObj , act.name)
    #isnotHair = False
    if act == None:
        return 

    elif cmd.check_not_ps():#パーティクルシステムがないなら先に進まない
        CurrentObj = act.name
        cmd.clear()
        return

    #選択が変更されたときだけリロード。
    if CurrentObj != act.name:
        print('selection changed')
        cmd.reload()    


    #リストを選択したときとパーティクルシステムを選択したときの処理
    props = bpy.context.scene.cyaparticletools_oa

    ps = act.particle_systems
    index_prop = ps.active_index #PSのプロパティ
    index_list = cmd.active_ps_index() #ツールのリスト

    index = None
    if CurrentList != index_list:
        ps.active_index = index = index_list
    elif CurrentProp != index_prop:
        index = index_prop
        cmd.active_index_set( index_prop )


    #インデックスに変更があった場合、いろいろアップデート
    if index != None:
        CurrentProp = CurrentList = index   
    #表示オンオフ
    #cmd.disp()


    if act.name == CurrentObj:
        return
    else:
        CurrentObj = act.name


    # ui_list = bpy.context.window_manager.cyaparticletools_list
    # itemlist = ui_list.itemlist

    # cmd.clear()
    # particle_systems = act.particle_systems
    # for p in particle_systems:
    #     item = itemlist.add()
    #     item.name = p.name

        
        #bpy.data.particles[p.settings.name].shape = props.shape

    # for ob in utils.selected():
    #     item = itemlist.add()
    #     item.name = CurrentObj
        #ui_list.active_index = len(itemlist) - 1


    #props = bpy.context.scene.cyaobjectlist_props

    # #インデックスが変わったときだけ選択
    # if len(itemlist) > 0:
    #     index = ui_list.active_index
    #     if props.currentindex != index:
    #         props.currentindex = index#先に実行しておかないとdeselectでhandlerがループしてしまう
    #         bpy.ops.object.select_all(action='DESELECT')
    #         utils.selectByName(itemlist[index].name,True)




class CYAPARTICLETOOLS_Props_OA(PropertyGroup):
    collection_name : StringProperty(name="Collection", maxlen=63 )
    allcollections : CollectionProperty(type=PropertyGroup) 

#---------------------------------------------------------------------------------------
    #Particle Attribhte
#---------------------------------------------------------------------------------------
    
    #Hair Shape
    shape : FloatProperty(name = "shape",precision = 4, update=cmd.apply_shape)
    root_radius :  FloatProperty(name = "root_radius",precision = 4, update=cmd.apply_root_radius)
    tip_radius :  FloatProperty(name = "tip_radius",precision = 4, update=cmd.apply_tip_radius)
    radius_scale :  FloatProperty(name = "radius_scale",precision = 4, update=cmd.apply_radius_scale)

    #display
    render_step :  IntProperty(name = "render_step" , update=cmd.apply_render_step)
    display_step :  IntProperty(name = "display_step" , update=cmd.apply_display_step)
    use_hair_bspline :  BoolProperty(name = "use_hair_bspline" , update=cmd.apply_use_hair_bspline)


    edit_display_step :  IntProperty(name = "edit_display_step" , update=cmd.apply_edit_render_step)
    #bpy.context.scene.tool_settings.particle_edit.display_step = 6

#---------------------------------------------------------------------------------------
#リスト内のアイテムの見た目を指定
#---------------------------------------------------------------------------------------
class CYAPARTICLETOOLS_UL_uilist(UIList):
    

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            #item.nameが表示される
            #item.iconname = 'GROUP'
            layout.prop(item, "disp", text = "" , icon = item.iconname)
            layout.prop(item, "check", text = "")
            #layout.operator("cyaparticletools.particle_effector_collection_assign" , icon = 'GROUP').mode = True
            layout.prop(item, "name", text="", emboss=False, icon_value=icon)
            #layout.prop(item, "check", text="", emboss=False, icon_value=icon)
            

        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)



class CYAPARTICLETOOLS_PT_particletools(utils.panel):
    bl_label = "Particle Tools"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        return{'FINISHED'}

    def draw(self, context):
        props = bpy.context.scene.cyaparticletools_oa
        layout = self.layout

        layout.operator("cyaparticletools.create_particle_setting" , icon = 'GROUP')
        layout.operator("cyaparticletools.edit_attribute" , icon = 'GROUP')
        layout.operator("cyaparticletools.copy_particle_settings" , icon = 'GROUP')

        row = layout.row()
        row.operator("cyaparticletools.showhide_all" , text = "show all").mode = True
        row.operator("cyaparticletools.showhide_all" ,  text = "hide all").mode = False

        row = layout.row()
        row.operator("cyaparticletools.showhide_check" , text = "show check").mode = True
        row.operator("cyaparticletools.showhide_check" ,  text = "hide check").mode = False



        ui_list = context.window_manager.cyaparticletools_list
        box = layout.box()
        box.label(text = 'particle settings')

        col = box.column()
        col.template_list("CYAPARTICLETOOLS_UL_uilist", "", ui_list, "itemlist", ui_list, "active_index", rows=8)




class CYAPARTICLETOOLS_MT_edit_attribute(Operator):
    bl_idname = "cyaparticletools.edit_attribute"
    bl_label = "edit_attribute"

    def invoke(self, context, event):
        #cmd.set_collection()
        cmd.isBanApply = True
        cmd.set_attribute()
        cmd.isBanApply = False

        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        return{'FINISHED'}

    def draw(self, context):
        props = bpy.context.scene.cyaparticletools_oa
        layout = self.layout

        row = layout.row()

        box = row.box()
        box.label(text = 'Hair Shape')
        box.prop(props, "shape" , icon='RESTRICT_VIEW_OFF')
        box.prop(props, "root_radius" , icon='RESTRICT_VIEW_OFF')
        box.prop(props, "tip_radius" , icon='RESTRICT_VIEW_OFF')
        box.prop(props, "radius_scale" , icon='RESTRICT_VIEW_OFF')

        box = row.box()
        box.label(text = 'Display')
        box.prop(props, "edit_display_step" , icon='RESTRICT_VIEW_OFF')
        box.prop(props, "render_step" , icon='RESTRICT_VIEW_OFF')
        box.prop(props, "display_step" , icon='RESTRICT_VIEW_OFF')
        box.prop(props, "use_hair_bspline" , icon='RESTRICT_VIEW_OFF')
        

        box = layout.box()
        box.label(text = 'effect collection')
        row = box.row()
        row.prop_search(props, "collection_name", props, "allcollections", icon='SCENE_DATA')
        row.operator("cyaparticletools.particle_effector_collection_assign" , icon = 'GROUP').mode = True
        row.operator("cyaparticletools.particle_effector_collection_assign" , icon = 'X').mode = False



#リスト用
class CYAPARTICLETOOLS_Props_item(PropertyGroup):
    name : StringProperty()
    check : BoolProperty()
    disp : BoolProperty( update=cmd.disp )
    iconname : StringProperty(default = 'RESTRICT_VIEW_OFF')
    idx : IntProperty()
    mod : StringProperty()
    
bpy.utils.register_class(CYAPARTICLETOOLS_Props_item)

class CYAPARTICLETOOLS_Props_list(PropertyGroup):
    active_index : IntProperty()
    itemlist : CollectionProperty(type=CYAPARTICLETOOLS_Props_item)#アイテムプロパティの型を収めることができるリストを生成


#---------------------------------------------------------------------------------------
#パーティクルツール
#---------------------------------------------------------------------------------------
class CYAPARTICLETOOLS_OT_particle_effector_collection_assign(Operator):
    """パーティクルのエフェクトコレクションを設定する"""
    bl_idname = "cyaparticletools.particle_effector_collection_assign"
    bl_label = ""
    mode : BoolProperty()
    def execute(self, context):
        cmd.effector_collection_assign(self.mode)
        return {'FINISHED'}

class CYAPARTICLETOOLS_OT_create_particle_setting(Operator):
    """新しい髪の毛のパーティクルセッティングを生成"""
    bl_idname = "cyaparticletools.create_particle_setting"
    bl_label = "create"
    def execute(self, context):
        cmd.create_particle_setting()
        return {'FINISHED'}

class CYAPARTICLETOOLS_OT_copy_particle_settings(Operator):
    """チェックを付けたもののパーティクルセッティングをアクティブのものと同じにする"""
    bl_idname = "cyaparticletools.copy_particle_settings"
    bl_label = "copy"
    def execute(self, context):
        cmd.copy_particle_settings()
        return {'FINISHED'}

# class CYAPARTICLETOOLS_OT_sort_particle_sistem(Operator):
#     """パーティクルシステムの名前でのソート"""
#     bl_idname = "cyaparticletools.sort_particle_sistem"
#     bl_label = "sort by name"
#     def execute(self, context):
#         cmd.sort_particle_sistem()
#         return {'FINISHED'}

class CYAPARTICLETOOLS_OT_showhide_all(Operator):
    """パーティクルシステムの表示、非表示"""
    bl_idname = "cyaparticletools.showhide_all"
    bl_label = ""
    mode : BoolProperty()
    def execute(self, context):
        cmd.showhide_all(self.mode)
        return {'FINISHED'}


class CYAPARTICLETOOLS_OT_showhide_check(Operator):
    """チェックを付けたパーティクルシステムの表示、非表示"""
    bl_idname = "cyaparticletools.showhide_check"
    bl_label = ""
    mode : BoolProperty()
    def execute(self, context):
        cmd.showhide_check(self.mode)
        return {'FINISHED'}


classes = (
    CYAPARTICLETOOLS_Props_OA,
    CYAPARTICLETOOLS_PT_particletools,
    CYAPARTICLETOOLS_MT_edit_attribute,
    CYAPARTICLETOOLS_Props_list,

    #リスト
    CYAPARTICLETOOLS_UL_uilist,
    CYAPARTICLETOOLS_OT_particle_effector_collection_assign,

    CYAPARTICLETOOLS_OT_create_particle_setting,
    CYAPARTICLETOOLS_OT_copy_particle_settings,
    #CYAPARTICLETOOLS_OT_sort_particle_sistem,
    CYAPARTICLETOOLS_OT_showhide_all,
    CYAPARTICLETOOLS_OT_showhide_check,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.cyaparticletools_oa = PointerProperty(type = CYAPARTICLETOOLS_Props_OA )
    bpy.types.WindowManager.cyaparticletools_list = PointerProperty(type = CYAPARTICLETOOLS_Props_list )
    bpy.app.handlers.depsgraph_update_pre.append(cyaparticletools_handler)



def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.cyaparticletools_oa
    del bpy.types.WindowManager.cyaparticletools_list
    bpy.app.handlers.depsgraph_update_pre.remove(cyaparticletools_handler)
