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
import imp
import csv
import os

from bpy.props import(
    PointerProperty,
    IntProperty,
    BoolProperty,
    StringProperty,
    CollectionProperty,
    FloatProperty,
    EnumProperty
    )

from .. import utils
from . import modifier
from . import apply
from . import curve
from . import scene
from . import constraint
from . import locator
from . import rename
from . import skinning
from . import transform
from . import modeling
from . import etc
from . import blendshape
from . import scenesetup
from . import facemap

imp.reload(utils)
imp.reload(modifier)
imp.reload(apply)
imp.reload(curve)
imp.reload(scene)
imp.reload(constraint)
imp.reload(locator)
imp.reload(rename)
imp.reload(skinning)
imp.reload(transform)
imp.reload(modeling)
imp.reload(etc)
imp.reload(blendshape)
imp.reload(scenesetup)
imp.reload(facemap)


MOB_OFFSET_PATH = 'D:/Prj/B01/Assets/Characters/Common/Data/Mob_Offset.csv'

MOB_TYPE = []
MOB_TYPE_DATA = []
if(os.path.exists(MOB_OFFSET_PATH)):
    with open(MOB_OFFSET_PATH, encoding='utf8', newline='') as f:
        csvreader = csv.reader(f)
        for row in csvreader:

            item = [row[0],row[0],""]
            MOB_TYPE.append([row[0],row[0],""])
            MOB_TYPE_DATA.append([row[0],row[1]])



#シーンを追加したとき、それぞれのシーンにあるシーンリストを更新してあげる必要がある
def go_scene(self,context):
    props = bpy.context.scene.cyatools_oa
    scene = props.scene_name
    bpy.context.window.scene = bpy.data.scenes[scene]
    count = len(bpy.data.scenes)

    #シーンを変更したので、propsを読み直し
    props = bpy.context.scene.cyatools_oa
    if props.scene_name != scene:
        props.scene_name = scene

    #シーンを追加した場合、シーンのコレクションプロパティとの差が生じてしまっているので修正
    if len(props.allscene) != count:
        props.allscene.clear()
        for scn in bpy.data.scenes:
            props.allscene.add().name = scn.name

    if len(props.target_allscene) != count:
        props.target_allscene.clear()
        for scn in bpy.data.scenes:
            props.target_allscene.add().name = scn.name



class CYATOOLS_Props_OA(PropertyGroup):
    #アプライオプション
    deleteparticle_apply : BoolProperty(name="delete particle" ,  default = False)
    keephair_apply : BoolProperty(name="keep hair" ,  default = False)
    keeparmature_apply : BoolProperty(name="keep armature" ,  default = False)
    merge_apply : BoolProperty(name="all" ,  default = True)
    merge_by_material : BoolProperty(name="material" ,  default = True)
    create_collection : BoolProperty(name="create collection" ,  default = False)
    add_suffix : BoolProperty(name="add suffix" ,  default = True)
    only_directly_below : BoolProperty(name="only directly below" ,  default = False)
    keep_transform : BoolProperty(name="keep transform" ,  default = False)

    apply_frame : IntProperty(name="apply_frame")


    #シーン名
    scene_name : StringProperty(name="Scene", maxlen=63 ,update = go_scene)
    allscene : CollectionProperty(type=PropertyGroup)

    target_scene_name : StringProperty(name="Target", maxlen=63 ,update = go_scene)
    target_allscene : CollectionProperty(type=PropertyGroup)

    new_scene_name : StringProperty(name="new scene", maxlen=63)


    displayed_obj : StringProperty(name="Target", maxlen=63)
    displayed_allobjs : CollectionProperty(type=PropertyGroup)

    displayed_collection : StringProperty(name="Coll", maxlen=63)
    displayed_allcollections : CollectionProperty(type=PropertyGroup)

    #モデリングツール
    mirror_mode : EnumProperty(items=(
        ('normal', 'normal', ''),
        ('const', 'const', ''),
        ('rot', 'rot', '')))

    vertex_size : IntProperty(name="vtx size" ,update = modeling.vertex_size,min=1,max = 32)
    facedot_size : IntProperty(name="facedot size" ,update = modeling.facedot_size,min=1,max = 10)
    outline_width : IntProperty(name="outline width" ,update = modeling.outline_width,min=1,max = 5)
    origin_size : IntProperty(name="origin size" ,update = modeling.origin_size,min=4,max = 10)
    uv_index : IntProperty(name="mapindex" ,update = etc.change_uv_index,min=0,max = 10)

    #モディファイヤ関連
    mod_init : BoolProperty(default = True)
    modifier_type : EnumProperty(items = modifier.TYPE , name = '' )

    solidify_thickness : FloatProperty(name = "Solidify_thick",precision = 4, update=modifier.apply)
    shrinkwrap_offset : FloatProperty(name = "wrap_ofset", precision = 4, update=modifier.apply)
    bevel_width : FloatProperty(name = "Bevel_width",update=modifier.apply)
    array_count : IntProperty(name = "Array_num",update=modifier.apply)

    array_offset_x : FloatProperty(name = "x", update=modifier.apply)
    array_offset_y : FloatProperty(name = "y",  update=modifier.apply)
    array_offset_z : FloatProperty(name = "z",  update=modifier.apply)

    #コンストレイン関連
    const_type : EnumProperty(items = constraint.TYPE , name = '' )

    #リネームツール関連
    rename_start_num : IntProperty( name = "start",min=1,default=1 )
    rename_string : StringProperty(name = "word")
    from_string : StringProperty(name = "from")
    to_string : StringProperty(name = "to")

    #スキン関連
    bone_xray_bool : BoolProperty( name = "bone_xray",update=skinning.bone_xray)
    vertexgrp_string : StringProperty(name = "word")
    weight_margin : FloatProperty(name = "margin", default=0.01 )

    batch_weight_transfer_bool : BoolProperty(name="batch" ,  default = False)
    weight_transfer_keep_original : BoolProperty(name="keep original" ,  default = False)
    weight_transfer_selected_vtx : BoolProperty(name="selected vtx" ,  default = False)
    weight_transfer_samplevtx : IntProperty(name = "sample", default=3 )

    bind_auto_bool : BoolProperty(name="auto" ,  default = True)
    batch_weight_transfer_string : StringProperty(name = "suffix")
    threshold_selectweight : FloatProperty(name = "threshold", default=0.9 )

    weight_import_clear : BoolProperty(name="weight import clear" ,  default = False)


    mobproecss_index : IntProperty( name = "number", min=1, max=10, default=1 )

    #ミラーウェイト関連
    weightmirror_dir : EnumProperty(items=(
        ('L>R', 'L>R', ''),
        ('R>L', 'R>L', '')),
        default = 'L>R'
        )
    weightmirror_selected_vtx : BoolProperty(name="selected vtx" ,  default = False)
    weightmirror_vroidmode : BoolProperty(name="vroid" ,  default = False)

    skin_filepath : StringProperty(name = "path")

    #モブのウェイト
    import_mob_weight_sex : EnumProperty(items=(
        ('Male', 'Male', ''),
        ('Female', 'Female', '')),
        default = 'Male'
        )



    #マテリアル関連
    material_index : IntProperty( name = "number", min=0, max=10, default=1 )

    #カーブツール
    with_bevel : BoolProperty(name="with bevel" ,  default = True)
    curve_liner : BoolProperty(name="liner" ,  default = False)

    #シーンセットアップツール
    proxy_with_skinbinding : BoolProperty(name="skinbind" ,  default = False)
    proxy_hide_source : BoolProperty(name="hide" ,  default = True)
    newcollection_name1 : StringProperty(name = "char name")
    newcollection_name2 : StringProperty(name = "categoty")
    newcollection_name3 : StringProperty(name = "parts name")


    mob_offset : StringProperty(name="mob_offset", maxlen=63 )
    mob_offset_all : CollectionProperty(type=PropertyGroup)

    #アニメーション
    mob_sex : EnumProperty(items=(
        ('M', 'M', ''),
        ('F', 'F', ''),
        ))
    mob_body_number : IntProperty(name = "body")
    mob_extruct_frame : IntProperty(name = "end frame")
    mob_extructall_startframe : IntProperty(name = "start")




    #mob_offset : EnumProperty(items = MOB_TYPE , name = '' )

#---------------------------------------------------------------------------------------
#UI
#---------------------------------------------------------------------------------------
class CYATOOLS_PT_toolPanel(utils.panel):
    bl_label ='Main Tools'
    def draw(self, context):
        self.layout.operator("cyatools.apply", icon='EVENT_A')
        self.layout.operator("cyatools.modifier_tools", icon='MODIFIER')
        self.layout.operator("cyatools.cya_modeling_tools", icon='MESH_CUBE')
        self.layout.operator("cyatools.curvetools", icon='CURVE_DATA')
        self.layout.operator("cyatools.rename", icon='SYNTAX_OFF')
        self.layout.operator("cyatools.skinningtools", icon='MOD_SKIN')
        self.layout.operator("cyatools.blendshape_tools", icon='MOD_SKIN')
        self.layout.operator("cyatools.scenesetuptools", icon='SCENE_DATA')
        self.layout.operator("cyatools.facemaptools", icon='SCENE_DATA')

#---------------------------------------------------------------------------------------
#Modeling Tools
#---------------------------------------------------------------------------------------
class CYATOOLS_MT_modeling_tools(Operator):
    bl_idname = "cyatools.cya_modeling_tools"
    bl_label = "modeling"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        return{'FINISHED'}

    def invoke(self, context, event):
        view3d = bpy.context.preferences.themes[0].view_3d
        props = bpy.context.scene.cyatools_oa
        props.vertex_size = view3d.vertex_size
        props.facedot_size = view3d.facedot_size
        props.outline_width = view3d.outline_width
        props.origin_size = view3d.object_origin_size

        return context.window_manager.invoke_props_dialog(self ,width = 600)

    def draw(self, context):
        props = bpy.context.scene.cyatools_oa
        layout=self.layout
        row = layout.split(factor = 0.6, align = False)

        col = row.column()
        box2 = col.box()
        box2.label( text = 'locator' )
        row0 = box2.row()
        row0.operator( "cyatools.replace_locator" , icon = 'OUTLINER_DATA_EMPTY')
        row0.operator( "cyatools.replace_locator_facenormal" , icon = 'NORMALS_FACE')

        row0 = box2.row()
        row0.operator( "cyatools.group" , icon = 'GROUP')
        row0.operator( "cyatools.locator_tobone" , icon = 'CONSTRAINT_BONE')

        row0 = box2.row()
        row0.operator( "cyatools.locator_tobone_keep" , icon = 'CONSTRAINT_BONE')

        #トランスフォーム
        box3 = col.box()
        box3.label( text = 'transform' )
        box3.operator( "cyatools.trasnform_apply_x" , icon = 'AXIS_SIDE')
        box3.operator( "cyatools.trasnform_reset_cursor_rot" , icon = 'CON_ROTLIKE')
        box3.operator( "cyatools.modeling_pivot_by_facenormal" , icon = 'NORMALS_FACE')
        box3.operator( "cyatools.trasnform_invert_bonetransform" , icon = 'NORMALS_FACE')

        box5 = col.box()
        box5.label( text = 'modeling' )
        box5.operator( "cyatools.modeling_del_half_x" , icon = 'MOD_TRIANGULATE')
        box5.operator( "cyatools.modeling_select_linked_faces" , icon = 'SNAP_FACE')
        box5.operator( "cyatools.modeling_mirror_l_to_r" , icon = 'MOD_MIRROR')
        box5.operator( "cyatools.modeling_separate_face" , icon = 'CONSTRAINT_BONE')


        #頂点コピー
        box5 = col.box()
        box5.label( text = 'vertex copy' )

        row5 = box5.row()
        row5.label( text = 'vertex' )
        row5.operator( "cyatools.modeling_copy_vertex_pos" , icon = 'SNAP_VERTEX',text='copy sel').mode = 0
        row5.operator( "cyatools.modeling_copy_vertex_pos" , icon = 'SNAP_VOLUME',text='copy all').mode = 1

        row5.operator( "cyatools.modeling_copy_vertex_pos" , icon = 'PASTEDOWN',text='paste').mode = 2

#        row5.operator( "cyatools.modeling_paste_vertex_pos" , icon = 'PASTEDOWN')

        row6 = box5.row()
        row6.label( text = 'blend' )
        row6.operator( "cyatools.modeling_copy_vertex_pos_blendshape" , icon = 'SNAP_VERTEX',text='copy sel').mode = 0
        row6.operator( "cyatools.modeling_copy_vertex_pos_blendshape" , icon = 'SNAP_VOLUME',text='copy all').mode = 1
        row6.operator( "cyatools.modeling_copy_vertex_pos_blendshape" , icon = 'PASTEDOWN',text='paste').mode = 2
        #row6.operator( "cyatools.modeling_paste_vertex_pos_blendshape" , icon = 'MOD_MIRROR')

        row6 = box5.row()
        row6.operator( "cyatools.modeling_copy_vertex_pos_paste_to_blendshape" , icon = 'PASTEDOWN')
        #row6.operator( "cyatools.modeling_paste_vertex_pos_blendshape" , icon = 'PASTEDOWN').mode = 2



        #material UV
        box5 = col.box()
        box5.label( text = 'material UV' )
        box5.operator( "cyatools.material_reload_texture", icon = 'TEXTURE')
        box5.operator( "cyatools.material_remove_submaterial", icon = 'NODE_MATERIAL')

        row5 = box5.row()
        row5.operator( "cyatools.material_add_uv")
        row5.prop(props, 'uv_index' , expand=True)
        row5.operator('cyatools.remove_uv_index' , icon = 'TRASH')


        #instacne
        col = row.column()
        box3 = col.box()
        box3.label( text = 'instance' )
        box3.operator( "cyatools.instance_select_collection" , icon = 'RESTRICT_SELECT_OFF')
        box3.operator( "cyatools.instance_instancer" , icon = 'DUPLICATE')
        box3.operator( "cyatools.instance_substantial" , icon = 'MOD_SUBSURF')
        box3.operator( "cyatools.instance_replace" , icon = 'LIBRARY_DATA_OVERRIDE')

        box4 = col.box()
        box4.label( text = 'rot90deg' )
        row = box4.row()
        row.operator( "cyatools.transform_rot90deg" , text = 'x').axis = 'x'
        row.operator( "cyatools.transform_rot90deg" , text = 'y').axis = 'y'
        row.operator( "cyatools.transform_rot90deg" , text = 'z').axis = 'z'

        box4 = col.box()
        box4.label( text = 'swap axis' )
        row = box4.row()
        row.operator( "cyatools.swap_axis" , text = 'x').axis = 'x'
        row.operator( "cyatools.swap_axis" , text = 'y').axis = 'y'
        row.operator( "cyatools.swap_axis" , text = 'z').axis = 'z'


        box4 = col.box()
        box4.label( text = ' mirror instance' )
        col1 = box4.column()
        row = col1.row()
        row.operator( "cyatools.instance_mirror" , text = 'x' ).op = 'x'
        row.operator( "cyatools.instance_mirror" , text = 'y' ).op = 'y'
        row.operator( "cyatools.instance_mirror" , text = 'z' ).op = 'z'
        row = col1.row()
        row.prop(props, 'mirror_mode' , expand=True)

        box4 = col.box()
        box4.label( text = 'component size' )
        box4.prop(props, 'vertex_size' , expand=True)
        box4.prop(props, 'facedot_size' , expand=True)
        box4.prop(props, 'outline_width' , expand=True)
        box4.prop(props, 'origin_size' , expand=True)

        box4 = col.box()
        box4.label( text = 'normal' )
        col1 = box4.column()
        row = col1.row()
        row.operator( "cyatools.modeling_normal_180deg")
        row.operator( "cyatools.modeling_normal_clear")

        box4 = col.box()
        box4.label( text = 'special' )
        #col1 = box4.column()
        #row = col1.row()
        box4.operator( "cyatools.modeling_extract_missingparts")
        box4.operator( "cyatools.modeling_extract_missingparts2")


class CYATOOLS_MT_modifier_tools(Operator):
    bl_idname = "cyatools.modifier_tools"
    bl_label = "modifier / constraint"

    def execute(self, context):
        return{'FINISHED'}

    def invoke(self, context, event):
        #アクティブオブジェクトのコンストレインの状態を取得
        modifier.get_param()
        return context.window_manager.invoke_props_dialog(self , width=400)

    def draw(self, context):
        props = bpy.context.scene.cyatools_oa
        layout=self.layout

        box = layout.box()
        box.label( text = 'simplemodifier' , icon = 'MODIFIER')
        row = box.row()
        row.operator( "cyatools.modifier_simple" ,text = 'Mirror', icon = 'MOD_MIRROR').mode = 0

        box = layout.box()
        box.label( text = 'modifier edit' , icon = 'MODIFIER')

        row = box.row()
        box1 = row.box()
        box1.label( text = 'Select'  , icon='RESTRICT_SELECT_ON')

        box1.operator( "cyatools.selectmodifiercurve" , icon = 'RESTRICT_SELECT_OFF')
        box1.operator( "cyatools.selectmodifierboolean" , icon = 'RESTRICT_SELECT_OFF')
        box1.operator( "cyatools.modifier_send_to" , icon = 'OUTLINER_OB_GROUP_INSTANCE')


        box2 = row.box()
        box2.label( text = 'modify'  , icon='MODIFIER_OFF')

        box2.prop(props, "solidify_thickness")
        box2.prop(props, "shrinkwrap_offset" )
        box2.prop(props, "bevel_width")

        box3 = row.box()
        box3.label( text = 'array modify'  , icon='MOD_ARRAY')

        box3.prop(props, "array_count")
        box3.prop(props, "array_offset_x" )
        box3.prop(props, "array_offset_y" )
        box3.prop(props, "array_offset_z" )


        #row = layout.row()
        row = layout.split(factor = 0.5, align = False)
        box = row.box()
        box.label( text = 'modifier (assign/apply/show/hide)' )
        box.prop(props, "modifier_type" , icon='RESTRICT_VIEW_OFF')

        row1 = box.row()
        row1.alignment = 'RIGHT'
        row1.operator( "cyatools.modifier_asign" , icon = 'VIEW_PAN')
        row1.operator( "cyatools.modifier_apply" , icon = 'CHECKBOX_HLT')
        row1.operator( "cyatools.modifier_show" , icon = 'HIDE_OFF')
        row1.operator( "cyatools.modifier_hide" , icon = 'HIDE_ON')
        row1.operator( "cyatools.modifier_remove" , icon = 'TRASH')

        col = box.column()
        row1 = col.row()
        row1.operator( "cyatools.modifier_apply_all" ,text = 'apply all', icon = 'PROP_ON').mode = 0
        row1.operator( "cyatools.modifier_apply_all" ,text = 'delete all', icon = 'CANCEL').mode = 1

        box = row.box()
        box.label( text = 'constraint (assign)' )
        box.prop(props, "const_type" , icon='RESTRICT_VIEW_OFF')
        row1 = box.row()
        row1.alignment = 'RIGHT'

        mode = (
        ('assign','VIEW_PAN'),
        ('apply','CHECKBOX_HLT'),
        ('show','HIDE_OFF'),
        ('hide','HIDE_ON'),
        ('remove','TRASH'),
        )

        for m in mode:
            row1.operator( "cyatools.constraint_asign" , icon = m[1]).mode = m[0]

        col = box.column()
        row1 = col.row()
        for i,m in enumerate((('apply','PROP_ON'),('delate','CANCEL'))):
            row1.operator( "cyatools.constraint_apply_all" ,text = m[0] + ' all', icon = m[1] ).mode = i



class CYATOOLS_MT_curvetools(Operator):
    bl_idname = "cyatools.curvetools"
    bl_label = "curve"

    def execute(self, context):
        return{'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self,width = 400)

    def draw(self, context):
        props = bpy.context.scene.cyatools_oa
        layout=self.layout
        row = layout.split(factor = 0.4, align = False)

        box1 = row.box()
        box1.label( text = 'create liner' )
        row1 = box1.row()

        for x in ( 'x' , 'y' , 'z' ):
            row1.operator( "cyatools.curve_create_liner" ,text = x).dir = x
        box1.prop( props,"with_bevel")
        box1.prop( props,"curve_liner")

        box2 = row.box()
        box2.label( text = 'bevel assign' )
        box2.operator( "cyatools.curve_assign_bevel" , icon = 'RESTRICT_SELECT_OFF')
        box2.operator( "cyatools.curve_assign_circle_bevel" , icon = 'CURVE_NCIRCLE')
        box2.operator( "cyatools.curve_assign_liner_bevel" , icon = 'IPO_LINEAR')

        box2 = row.box()
        box2.label( text = 'taper assign' )
        box2.operator( "cyatools.curve_assign_taper_selected" , icon = 'RESTRICT_SELECT_OFF')
        box2.operator( "cyatools.curve_assign_taper" , icon = 'CURVE_BEZCURVE')

        box3 = row.box()
        box3.label( text = 'select' )
        box3.operator( "cyatools.curve_select_bevel" , icon = 'MOD_BEVEL')


class CYATOOLS_MT_object_applier(Operator):
    bl_idname = "cyatools.apply"
    bl_label = "Object Applier"

    def invoke(self, context, event):
        scene.set_current()
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        return{'FINISHED'}


    def draw(self, context):
        props = bpy.context.scene.cyatools_oa
        layout = self.layout

        box = layout.box()
        row = box.row()
        row.prop_search(props, "scene_name", props, "allscene", icon='SCENE_DATA')
        row.operator("cyatools.new_scene" , icon = 'DUPLICATE')

        box = layout.box()
        box.prop_search(props, "target_scene_name", props, "target_allscene", icon='SCENE_DATA')
        row = box.row()
        row.label( text = 'apply' )
        row.operator("cyatools.apply_model" , icon='OBJECT_DATAMODE' )
        row.operator("cyatools.apply_collection" , icon='GROUP' )
        row.operator("cyatools.apply_collection_instance" , icon='GROUP' )
        row.operator("cyatools.apply_particle_instance", icon='PARTICLES' )

        row = box.row()
        row.label( text = 'move' )
        row.operator("cyatools.move_model" , icon = 'OBJECT_DATAMODE').mode = True
        row.operator("cyatools.move_collection" , icon = 'GROUP').mode = True

        row = box.row()
        row.label( text = 'copy' )
        row.operator("cyatools.move_model" , icon = 'OBJECT_DATAMODE').mode = False
        row.operator("cyatools.move_collection" , icon = 'GROUP').mode = False

        box = layout.box()
        box.label(text = 'collection maintenance')
        row = box.row()
        row.operator("cyatools.collection_sort" , icon = 'DUPLICATE')
        row.operator("cyatools.remove_empty_collection" , icon = 'DUPLICATE')


        box = layout.box()
        box.label(text = 'options')

        box.prop(props, "apply_frame")

        box1 = box.box()
        box1.label(text = 'merge')
        col = box1.column()
        row = col.row()
        row.prop(props, "merge_apply")
        row.prop(props, "merge_by_material")
        row = col.row()
        row.prop(props, "only_directly_below")

        row = box.row()
        row.prop(props, "keeparmature_apply")
        row.prop(props, "keephair_apply")

        row = box.row()
        row.prop(props, "create_collection")
        row.prop(props, "deleteparticle_apply")

        row = box.row()
        row.prop(props, "add_suffix")
        row.prop(props, "keep_transform")


#---------------------------------------------------------------------------------------
#スキン関連ツール
#---------------------------------------------------------------------------------------
class CYATOOLS_MT_skinningtools(Operator):
    bl_idname = "cyatools.skinningtools"
    bl_label = "skinning"

    def execute(self, context):
        return{'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 400)

    def draw(self, context):
        props = bpy.context.scene.cyatools_oa
        layout=self.layout

        row = layout.row(align=False)
        col = row.column()

        box = col.box()
        box.label(text = 'influence')
        row1 = box.row()
        row1.operator("cyatools.skinning_bind" , icon = 'OUTLINER_DATA_ARMATURE')
        row1.prop(props, "bind_auto_bool")

        row1 = box.row()
        row1.operator("cyatools.skinning_add_influence_bone"  , icon = 'BONE_DATA')
        row1.operator("cyatools.skinning_copy_influence_bone" , icon = 'COMMUNITY')

        row1 = box.row()
        row1.operator("cyatools.skinning_add_influence_bone_auto" , icon = 'COMMUNITY')


        box = col.box()
        box.label(text = 'copy weight')
        col1 = box.column()

        row1 = col1.row()
        row1.operator("cyatools.skinning_weights_transfer" , icon = 'COMMUNITY').mode = 'v2'
        row1.prop(props, "batch_weight_transfer_bool")


        col1.prop(props,'batch_weight_transfer_string')
        col1.prop(props, "weight_transfer_selected_vtx")
        col1.prop(props, "weight_transfer_keep_original")
        col1.prop(props, "weight_transfer_samplevtx")


        box = col.box()
        box.label(text = 'mirror weight')
        col1 = box.column()
        row1 = col1.row()
        row1.operator("cyatools.skinning_weights_mirror",text = 'mirror'  , icon = 'MOD_MIRROR').mode = 'v2'

        row1 = col1.row()
        row1.prop(props, 'weightmirror_dir' , expand=True)
        col1.prop(props, "weightmirror_selected_vtx")
        col1.prop(props, "weightmirror_vroidmode")

        box = col.box()
        box.label(text = 'mob')
        col1 = box.column()
        row1 = col1.row()
        row1.operator("cyatools.skinning_mob_process01",text = 'process01' )
        row1.prop(props, 'mobproecss_index' , expand=True)


        #CSVを使ったウェイト編集ツール
        box = layout.box()
        box.label(text = 'vetex group edit with csv')
        col1 = box.column()
        row1 = col1.row()
        row1.operator("cyatools.skinning_rename_with_csvtable")
        row1.operator("cyatools.skinning_export_vertexgroup_list")
        row1.operator("cyatools.skinning_transfer_with_csvtable")

        row2 = col1.row()
        row2.prop(props,"skin_filepath")
        col = row.column()
        box = col.box()
        box.label(text = 'delete vtx group')

        row = box.row()
        row.alignment = 'EXPAND'
        row.operator("cyatools.skinning_apply_without_armature_modifiers" , icon = 'MODIFIER')#!!!

        row = box.row()
        row.alignment = 'EXPAND'
        row.operator("cyatools.skinning_delete_all_vtxgrp")
        row.operator("cyatools.skinning_delete_notexist_vtxgrp")

        row = box.row()
        row.alignment = 'EXPAND'
        row.operator("cyatools.skinning_delete_unselected_vtxgroup" , icon = 'RESTRICT_SELECT_OFF')

        box = box.box()
        box.label(text = 'Delete vtx grp with word')
        box.operator("cyatools.skinning_delete_with_word")
        box.prop(props, "vertexgrp_string", icon='FONT_DATA', toggle=True)


        box = col.box()
        box.label(text = 'delete weight')

        row = box.row()
        row.alignment = 'EXPAND'
        row.operator("cyatools.skinning_delete_allweights")
        row.operator("cyatools.skinning_delete_unselectedweights")

        row = box.row()
        row.alignment = 'EXPAND'
        row.operator("cyatools.skinning_remove_weight_selectedvtx")
        row.operator("cyatools.skinning_remove_weights_selectedbone")

        box = col.box()
        box.label(text = 'Modify')
        col1=box.column()
        row = col1.row()
        row.operator("cyatools.skinning_selectgrp"  , icon = 'MOD_MIRROR')
        row.operator("cyatools.skinning_weighthummer"  , icon = 'MOD_MIRROR')

        row = col1.row()
        row.prop(props, 'threshold_selectweight' , expand=True)

        # row = col1.row()
        # row.operator("cyatools.skinning_weight_cleanup"  , icon = 'MOD_MIRROR')


        box = col.box()
        box.label(text = 'importexport')

        col1 = box.column()
        row = col1.row()
        row.operator("cyatools.skinning_weight_export"  , icon = 'MOD_MIRROR')
        row.operator("cyatools.skinning_weight_import"  , icon = 'MOD_MIRROR')

        row = col1.row()
        row.prop(props, 'weight_import_clear' , expand=True)

        box.label(text = 'mob')
        row = box.row()
        row.operator("cyatools.skinning_mob_import_faceit"  , icon = 'MOD_MIRROR')
        row.operator("cyatools.skinning_mob_import_faceitrig"  , icon = 'MOD_MIRROR')
        row.operator("cyatools.skinning_mob_import_ingame"  , icon = 'MOD_MIRROR')

        row = box.row()
        row.prop(props, 'import_mob_weight_sex' , expand=True)

        #row.operator("cyatools.skinning_weight_export   "  , icon = 'MOD_MIRROR')


#---------------------------------------------------------------------------------------
#リネームツール
#リネームとオブジェクト選択に関するツール群
#---------------------------------------------------------------------------------------
class CYATOOLS_MT_rename(Operator):
    bl_idname = "cyatools.rename"
    bl_label = "rename"

    def execute(self, context):
        return{'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self , width = 400 )

    def draw(self, context):
        props = bpy.context.scene.cyatools_oa
        layout=self.layout

        col_root = layout.column()
        split = col_root.split(factor = 0.5, align = False)
        box = split.box()
        box.label(text="rename select")

        col = box.column()
        col.prop(props, "rename_string")

        row1 = col.row()
        row1.alignment = 'LEFT'
        row1.operator("cyatools.rename_select" , icon = 'VIEW_PAN')
        row1.operator("cyatools.rename_dropper" , icon = 'EYEDROPPER')
        row1.operator("cyatools.rename_common_renumber" , icon = 'LINENUMBERS_ON')
        row1.prop(props, "rename_start_num")

        split1 = col.split(factor = 0.5, align = False)
        split1.operator("cyatools.rename_by_rule")

        row2 =split1.row()
        row2.operator("cyatools.rename_add" , text = 'Prefix').op = 'PREFIX'
        row2.operator("cyatools.rename_add", text = 'Suffix').op = 'SUFFIX'

        box = split.box()
        col = box.column()
        col.operator("cyatools.rename_replace")
        col.prop(props, "from_string")
        col.prop(props, "to_string")

        box = col_root.box()
        row = box.row()

        box1 = row.box()
        box1.label(text="replace")
        col = box1.column()
        for s in ('high>low' , 'low>high' , '.>_' , 'delete_number'):
            col.operator("cyatools.rename_replace_defined", text = s).op = s

        box1 = row.box()
        box1.label(text="shape name")
        col = box1.column()
        for s in ('object','maya'):
            col.operator("cyatools.rename_mesh", text = s).op = s

        box1 = row.box()
        box1.label(text="add")
        col = box1.column()
        for s in ('org',):
            col.operator("cyatools.rename_add_defined", text = s).op = s

#---------------------------------------------------------------------------------------
#アニメーションツール
#---------------------------------------------------------------------------------------
class CYATOOLS_MT_blendshape_tools(Operator):
    bl_idname = "cyatools.blendshape_tools"
    bl_label = "animation"

    def execute(self, context):
        return{'FINISHED'}

    def invoke(self, context, event):
        #return context.window_manager.invoke_props_dialog(self)
        return context.window_manager.invoke_props_dialog(self, width = 400)

    def draw(self, context):
        props = bpy.context.scene.cyatools_oa
        layout=self.layout


        box = layout.box()
        box.label( text = 'blendshape key edit' , icon = 'MODIFIER')

        row = box.row()
        row.operator( "cyatools.blendshape_insert_all_keys" , icon = 'MOD_MIRROR')
        row.operator( "cyatools.blendshape_shape_key_clear" , icon = 'MOD_MIRROR')


        row = box.row()
        row.operator( "cyatools.blendshape_copy_action")
        row.operator( "cyatools.blendshape_push_down")

        row = box.row()
        row.operator( "cyatools.blendshape_shepekey_mute" ,text = 'Mute').mode = True
        row.operator( "cyatools.blendshape_shepekey_mute" ,text = 'UnMute').mode = False


        box = layout.box()
        box.label( text = 'blendshape key remove' , icon = 'MODIFIER')
        row = box.row()
        row.operator( "cyatools.blendshape_remove_shapekey_unmuted" , icon = 'MOD_MIRROR')
        row.operator( "cyatools.blendshape_remove_shapekey_numbered" , icon = 'MOD_MIRROR')

        row = box.row()
        row.operator( "cyatools.blendshape_remove_all_keys" , icon = 'MOD_MIRROR')





        box = layout.box()
        box.label( text = 'blendshape vtx copy paste' , icon = 'MODIFIER')
        col0 = box.column()
        col0.operator( "cyatools.blendshape_save_vtxpos_delta" , icon = 'MOD_MIRROR')

        row = col0.row()
        #row.operator( "cyatools.blendshape_copy_vertex_pos" , icon = 'MOD_MIRROR')
        #row.operator( "cyatools.blendshape_paste_vertex_pos" , icon = 'MOD_MIRROR')

        row.label( text = 'Import Shape',icon = "RADIOBUT_ON")
        row.operator( "cyatools.blendshape_import_vtxpos_delta" ,text = 'Mesh').mode = 0
        row.operator( "cyatools.blendshape_import_vtxpos_delta" ,text = 'BlendShape').mode = 1

        row = col0.row()
        row.label( text = 'In Game',icon = "RADIOBUT_ON")
        row.operator( "cyatools.blendshape_setup_mob_face").mode = 0
        row.operator( "cyatools.blendshape_setup_mob_face2",text = 'import M').mode = 0
        row.operator( "cyatools.blendshape_setup_mob_face2",text = 'import F').mode = 2


        row = col0.row()
        row.label( text = 'CS',icon = "RADIOBUT_ON")
        row.operator( "cyatools.blendshape_setup_mob_face").mode = 1
        row.operator( "cyatools.blendshape_setup_mob_face2",text = 'import M').mode = 1
        row.operator( "cyatools.blendshape_setup_mob_face2",text = 'import F').mode = 3




        box.label( text = 'restore' , icon = 'MODIFIER')
        row = box.row()
        row.operator( "cyatools.blendshape_keep_pos" , icon = 'MOD_MIRROR')
        row.operator( "cyatools.blendshape_restore_pos" , icon = 'MOD_MIRROR')


        box = layout.box()
        box.label( text = 'Mob facial' , icon = 'MODIFIER')
        row = box.row()
        row.operator( "cyatools.blendshape_mob_facial_cleanup" , icon = 'MOD_MIRROR')


        #モブバリエーション
        box = layout.box()
        box.label( text = 'Mob Variation' , icon = 'MODIFIER')
        col=box.column()
        row = col.row()
        row.operator( "cyatools.blendshape_mob_extruct" , text = 'extruct').mode=0
        row.operator( "cyatools.blendshape_mob_extruct" , text = 'extruct(+mouth open)').mode=1


        row = col.row()
        row.operator( "cyatools.blendshape_mob_extruct_all" , icon = 'MOD_MIRROR')
        row.prop(props, 'mob_extructall_startframe' , expand=True)

        #row = col.row()
        box1 = col.box()
        row =box1.row()
        row.operator( "cyatools.blendshape_mob_extruct_face")

        col=box1.column()
        row = col.row()
        row.prop(props, 'mob_sex' , expand=True)
        row.prop(props, 'mob_body_number' , expand=True)

        col=box.column()
        row = col.row()
        row.operator( "cyatools.blendshape_mob_extruct_frame")
        row.prop(props, 'mob_extruct_frame' , expand=True)




        box = layout.box()
        box.label( text = 'Remove Transform Key' , icon = 'MODIFIER')
        row = box.row()
        row.operator( "cyatools.anim_remove_transform_key" ,text = "location").mode = "location"
        row.operator( "cyatools.anim_remove_transform_key" ,text = "rotation").mode = "rotation"
        row.operator( "cyatools.anim_remove_transform_key" ,text = "scale").mode = "scale"



#---------------------------------------------------------------------------------------
#シーンセットアップツール
#---------------------------------------------------------------------------------------
class CYATOOLS_MT_scenesetuptools(Operator):
    bl_idname = "cyatools.scenesetuptools"
    bl_label = "scene setup tools"
    #mob_type = []

    def execute(self, context):
        return{'FINISHED'}

    def invoke(self, context, event):
        #ウインドウを開くタイミングでモブデータを読み込む
        scenesetup.MOB_TYPE_DATA.clear()
        props = bpy.context.scene.cyatools_oa
        props.mob_offset_all.clear()

        with open(MOB_OFFSET_PATH, encoding='utf8', newline='') as f:
            csvreader = csv.reader(f)
            for row in csvreader:
                props.mob_offset_all.add().name = row[0]
                scenesetup.MOB_TYPE_DATA[row[0]] = row[1]


        return context.window_manager.invoke_props_dialog(self, width = 400)

    def draw(self, context):
        props = bpy.context.scene.cyatools_oa
        layout=self.layout

        box = layout.box()
        box.operator( "cyatools.scenesetup_makeproxy" , icon = 'LINKED')
        box.prop(props, 'proxy_with_skinbinding' , expand=True)
        box.prop(props, 'proxy_hide_source' , expand=True)

        box = layout.box()
        box.operator( "cyatools.scenesetup_rename_collection_model" , icon = 'SYNTAX_OFF')

        box = layout.box()
        box.label( text = 'Create Collection' , icon = 'MODIFIER')

        box.prop(props, 'newcollection_name1' , expand=True)
        box.prop(props, 'newcollection_name2' , expand=True)
        box.prop(props, 'newcollection_name3' , expand=True)

        row = box.row()
        row.operator( "cyatools.scenesetup_create_new_collection" , icon = 'SYNTAX_OFF')
        row.operator( "cyatools.scenesetup_pick_collection_name" , icon = 'SYNTAX_OFF')
        row.operator( "cyatools.scenesetup_create_skin_parts" , icon = 'SYNTAX_OFF')

        box = layout.box()
        box.label( text = 'Save Collection State' , icon = 'MODIFIER')
        box.operator( "cyatools.scenesetup_save_collection_state" , icon = 'SYNTAX_OFF')


        box = layout.box()
        box.label( text = 'Render State' , icon = 'MODIFIER')
        box.operator( "cyatools.scenesetup_match_render_to_view" , icon = 'SYNTAX_OFF')


        box = layout.box()
        box.label( text = 'MobSetup' , icon = 'MODIFIER')
        row = box.row()
        row.prop_search(props, "mob_offset", props, "mob_offset_all", icon='SCENE_DATA')
        row.operator("cyatools.scenesetup_mob_offset" , text = 'offset').mode = 0
        row.operator("cyatools.scenesetup_mob_offset" , text = '-offset').mode = 1

        row = box.row()
        row.operator("cyatools.scenesetup_mob_modify_vtxgrp" , icon = 'DUPLICATE')


#---------------------------------------------------------------------------------------
#フェイスマップツール
#---------------------------------------------------------------------------------------
class CYATOOLS_MT_facemaptools(Operator):
    bl_idname = "cyatools.facemaptools"
    bl_label = "facemap tools"

    def execute(self, context):
        return{'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 400)

    def draw(self, context):
        layout=self.layout
        box = layout.box()
        box.operator( "cyatools.facemap_select_backside" , icon = 'LINKED')



#--------------------------------------------------------------------------------------
#Operator
#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------
#Curve Tool
#---------------------------------------------------------------------------------------

class CYATOOLS_OT_curve_assign_bevel(Operator):
        """カーブにベベルをアサイン\nカーブ、ベベルカーブの順に選択して実行"""
        bl_idname = "cyatools.curve_assign_bevel"
        bl_label = "select"

        def execute(self, context):
            curve.assign_bevel()
            return {'FINISHED'}

class CYATOOLS_OT_curve_assign_circle_bevel(Operator):
        """カーブに円のベベルをアサイン"""
        bl_idname = "cyatools.curve_assign_circle_bevel"
        bl_label = "circle"

        def execute(self, context):
            curve.assign_circle_bevel()
            return {'FINISHED'}

class CYATOOLS_OT_curve_assign_liner_bevel(Operator):
        """カーブに直線のベベルをアサイン"""
        bl_idname = "cyatools.curve_assign_liner_bevel"
        bl_label = "liner"

        def execute(self, context):
            curve.assign_liner_bevel()
            return {'FINISHED'}

class CYATOOLS_OT_curve_assign_taper_selected(Operator):
        """カーブにテーパーをアサイン
カーブ、テーパーカーブの順に選択して実行"""
        bl_idname = "cyatools.curve_assign_taper_selected"
        bl_label = "select"

        def execute(self, context):
            curve.assign_taper_selected()
            return {'FINISHED'}

class CYATOOLS_OT_curve_assign_taper(Operator):
        """カーブにテーパーをアサイン
カーブ、テーパーカーブの順に選択して実行"""
        bl_idname = "cyatools.curve_assign_taper"
        bl_label = "curve"

        def execute(self, context):
            curve.assign_taper()
            return {'FINISHED'}


class CYATOOLS_OT_curve_create_liner(Operator):
        """カーブ作成
with bebelをOnにするとサークルでベベルする
linerをOnにするとカーブがPolyLineになる"""
        bl_idname = "cyatools.curve_create_liner"
        bl_label = "add liner"
        dir : StringProperty()
        def execute(self, context):
            curve.create_liner(self.dir)
            return {'FINISHED'}

class CYATOOLS_OT_curve_select_bevel(Operator):
        """選択カーブのベベルを選択"""
        bl_idname = "cyatools.curve_select_bevel"
        bl_label = "bevel"

        def execute(self, context):
            curve.select_bevel()
            return {'FINISHED'}


#---------------------------------------------------------------------------------------
#Locator
#---------------------------------------------------------------------------------------

class CYATOOLS_OT_replace_locator(Operator):
    """モデルに位置にロケータを配置してコンストレインする。モデルのトランスフォームは初期値にする。"""
    bl_idname = "cyatools.replace_locator"
    bl_label = "to locator"

    def execute(self, context):
        locator.replace()
        return {'FINISHED'}

class CYATOOLS_OT_replace_locator_facenormal(Operator):
    """モデルに位置にロケータを配置してコンストレインする。モデルのトランスフォームは初期値にする。"""
    bl_idname = "cyatools.replace_locator_facenormal"
    bl_label = "face normal"

    def execute(self, context):
        locator.replace_facenormal()
        return {'FINISHED'}

class CYATOOLS_OT_group(Operator):
    """ロケータで選択モデルをまとめる"""
    bl_idname = "cyatools.group"
    bl_label = "group"

    def execute(self, context):
        locator.group()
        return {'FINISHED'}

class CYATOOLS_OT_locator_tobone(Operator):
    """ボーンにロケータを挟んでコンストする\nモデルを選択し、コンストしたいアーマチュアボーンを選択して実行する"""
    bl_idname = "cyatools.locator_tobone"
    bl_label = "to Bone"

    def execute(self, context):
        locator.tobone()
        return {'FINISHED'}

class CYATOOLS_OT_locator_tobone_keep(Operator):
    """オフセットを保ちつつボーンにロケータを挟んでコンストする
    モデルを選択し、コンストしたいアーマチュアボーンを選択して実行する"""
    bl_idname = "cyatools.locator_tobone_keep"
    bl_label = "to Bone keep ofsset"

    def execute(self, context):
        locator.tobone_keep()
        return {'FINISHED'}

class CYATOOLS_OT_modeling_separate_face(Operator):
    """選択されたフェースが複製され１メッシュになる"""
    bl_idname = "cyatools.modeling_separate_face"
    bl_label = "separate face"

    def execute(self, context):
        locator.separate_face()
        return {'FINISHED'}


#---------------------------------------------------------------------------------------
#Instance
#---------------------------------------------------------------------------------------
class CYATOOLS_OT_instance_select_collection(Operator):
    """コレクションインスタンスから元のコレクションを選択する"""
    bl_idname = "cyatools.instance_select_collection"
    bl_label = "select source"
    def execute(self, context):
        locator.instance_select_collection()
        return {'FINISHED'}

class CYATOOLS_OT_instance_instancer(Operator):
    """選択したオブジェクトがメンバーのコレクションをインスタンス化"""
    bl_idname = "cyatools.instance_instancer"
    bl_label = "instancer"
    def execute(self, context):
        locator.instancer()
        return {'FINISHED'}

class CYATOOLS_OT_instance_substantial(Operator):
    """コレクションインスタンスを実体化させる"""
    bl_idname = "cyatools.instance_substantial"
    bl_label = "substantial"
    def execute(self, context):
        locator.instance_substantial()
        return {'FINISHED'}

class CYATOOLS_OT_instance_replace(Operator):
    """選択物をアクティブなものに差し替える"""
    bl_idname = "cyatools.instance_replace"
    bl_label = "replace"
    def execute(self, context):
        locator.instance_replace()
        return {'FINISHED'}


#---------------------------------------------------------------------------------------
#ObjectApplier
#---------------------------------------------------------------------------------------
def target_exist():
    props = bpy.context.scene.cyatools_oa
    target = props.target_scene_name
    if target != '':
        return True
    else:
        return False

APPLY_TARGET_ERROR = 'ターゲットシーンが選択されていない'

#選択モデルをリスト選択されたシーンに移動
class CYATOOLS_OT_move_model(Operator):
    """選択したモデルをリスト選択されたシーンに移動する"""
    bl_idname = "cyatools.move_model"
    bl_label = "model"
    mode : BoolProperty(default = True)

    def execute(self, context):
        if target_exist():
            apply.move_object_to_other_scene(self.mode)
        else:
            self.report({'ERROR'}, APPLY_TARGET_ERROR)
        return {'FINISHED'}



#選択コレクションをリスト選択されたシーンに移動
class CYATOOLS_OT_move_collection(Operator):
    """選択コレクションをリスト選択されたシーンに移動"""
    bl_idname = "cyatools.move_collection"
    bl_label = "collection"
    mode : BoolProperty(default = True)
    def execute(self, context):
        if target_exist():
            apply.move_collection_to_other_scene(self.mode)
        else:
            self.report({'ERROR'}, APPLY_TARGET_ERROR)
        return {'FINISHED'}

#空のコレクションを削除
class CYATOOLS_OT_remove_empty_collection(Operator):
    """空のコレクションを削除"""
    bl_idname = "cyatools.remove_empty_collection"
    bl_label = "remove empty"
    def execute(self, context):
        apply.remove_empty_collection()
        return {'FINISHED'}

class CYATOOLS_OT_collection_sort(Operator):
    """コレクションのソート"""
    bl_idname = "cyatools.collection_sort"
    bl_label = "sort"
    def execute(self, context):
        apply.collection_sort()
        return {'FINISHED'}


#選択したコレクションに含まれたモデルを対象に
#出力名にコレクション名を付ける
#末尾にorgcを付ける
class CYATOOLS_OT_apply_collection(Operator):
    """選択したコレクション以下のモデルが対象\nコレクションのモデルはジョインされる\n名前はコレクション名+orgcとする"""
    bl_idname = "cyatools.apply_collection"
    bl_label = "col"
    def execute(self, context):
        if target_exist():
            apply.apply_collection()
        else:
            self.report({'ERROR'}, APPLY_TARGET_ERROR)
        return {'FINISHED'}

class CYATOOLS_OT_apply_collection_instance(Operator):
    """選択したコレクションインスタンスが対象"""
    bl_idname = "cyatools.apply_collection_instance"
    bl_label = "colins"
    def execute(self, context):
        if target_exist():
            apply.apply_collection_instance()
        else:
            self.report({'ERROR'}, APPLY_TARGET_ERROR)
        return {'FINISHED'}


#Newシーンのパネルを開く
class CYATOOLS_MT_new_scene(Operator):
    """新しいFixScnを生成する"""
    bl_idname = "cyatools.new_scene"
    bl_label = ""

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        props = bpy.context.scene.cyatools_oa
        row = self.layout.row(align=False)
        row.prop(props, "new_scene_name", icon='BLENDER', toggle=True)

    def execute(self, context):
        props = bpy.context.scene.cyatools_oa

        scene_name = props.new_scene_name
        if bpy.data.scenes.get(scene_name) is not None:
            return {'FINISHED'}

        bpy.ops.scene.new(type='EMPTY')
        bpy.context.scene.name = scene_name
        scene.set_current()

        return {'FINISHED'}

#パーティクルインスタンスのApply
class CYATOOLS_OT_apply_particle_instance(Operator):
    """パーティクルインスタンスを実体化して1つのモデルに集約"""
    bl_idname = "cyatools.apply_particle_instance"
    bl_label = "particle to model"

    def execute(self, context):
        apply.particle_instance()
        return {'FINISHED'}

#モデル名に_orgをつけてそれを作業用のモデルとする。
class CYATOOLS_OT_apply_model(Operator):
    """名前の末尾にorgがついたモデルが対象\nモディファイアフリーズ＞_orgを削除したモデルを複製＞選択シーンににリンク"""
    bl_idname = "cyatools.apply_model"
    bl_label = "org"

    def execute(self, context):
        apply.model_org()
        return {'FINISHED'}



#---------------------------------------------------------------------------------------
#Modifier
#---------------------------------------------------------------------------------------

#二つのノードを選択してモディファイヤアサインと同時にターゲットを割り当てる
#ターゲットモデルをアクティブとするので　モディファイヤをアサインしたいモデルをまず選択、最後にターゲットを選択する
class CYATOOLS_OT_modifier_asign(Operator):
    """モディファイヤをアサインする"""
    bl_idname = "cyatools.modifier_asign"
    bl_label = ""

    def execute(self, context):
        modifier.assign()
        return {'FINISHED'}

class CYATOOLS_OT_modifier_show(Operator):
    """モディファイヤを表示する"""
    bl_idname = "cyatools.modifier_show"
    bl_label = ""

    def execute(self, context):
        modifier.show(True)
        return {'FINISHED'}

class CYATOOLS_OT_modifier_hide(Operator):
    """モディファイヤを表示する"""
    bl_idname = "cyatools.modifier_hide"
    bl_label = ""

    def execute(self, context):
        modifier.show(False)
        return {'FINISHED'}

class CYATOOLS_OT_modifier_apply(Operator):
    """モディファイヤを適用する"""
    bl_idname = "cyatools.modifier_apply"
    bl_label = ""

    def execute(self, context):
        modifier.apply_mod()
        return {'FINISHED'}

class CYATOOLS_OT_modifier_remove(Operator):
    """delete the modifier of selected type"""
    bl_idname = "cyatools.modifier_remove"
    bl_label = ""

    def execute(self, context):
        modifier.delete_mod()
        return {'FINISHED'}

class CYATOOLS_OT_modifier_simple(Operator):
    """簡易モディファイヤ実行"""
    bl_idname = "cyatools.modifier_simple"
    bl_label = ""
    mode : IntProperty()

    def execute(self, context):
        modifier.simple(self.mode)
        return {'FINISHED'}


#選択したモデルのモディファイヤカーブのカーブ選択。
class CYATOOLS_OT_modifier_select_curve(Operator):
    """選択したモデルのモディファイヤカーブのカーブ選択"""
    bl_idname = "cyatools.selectmodifiercurve"
    bl_label = "Curve"
    def execute(self, context):
        modifier.select('CURVE')
        return {'FINISHED'}

class CYATOOLS_OT_modifier_select_boolean(Operator):
    """選択したモデルのブーリアン選択"""
    bl_idname = "cyatools.selectmodifierboolean"
    bl_label = "Boolean"
    def execute(self, context):
        modifier.select('BOOLEAN')
        return {'FINISHED'}

class CYATOOLS_OT_modifier_send_to(Operator):
    """選択したモデルのモディファイヤ関連オブジェクトをコレクションに集める"""
    bl_idname = "cyatools.modifier_send_to"
    bl_label = "gather into collection"
    def execute(self, context):
        modifier.send_to()
        return {'FINISHED'}

class CYATOOLS_OT_modifier_apply_all(Operator):
    """Apply all modifiers."""
    bl_idname = "cyatools.modifier_apply_all"
    bl_label = ""
    mode : IntProperty()
    def execute(self, context):
        modifier.apply_all(self.mode)
        return {'FINISHED'}


#---------------------------------------------------------------------------------------
#Constraint
#---------------------------------------------------------------------------------------
class CYATOOLS_OT_constraint_asign(Operator):
    """メニューで選択したタイプのみ適用する
1:複数選択し、アクティブなもので他のものをコンストレインする
2: 適用　3:表示　4:非表示　5:削除
"""
    bl_idname = "cyatools.constraint_asign"
    bl_label = ""
    mode : StringProperty()
    def execute(self, context):
        constraint.assign(self.mode)
        return {'FINISHED'}

class CYATOOLS_OT_constraint_apply_all(Operator):
    """Apply all modifiers."""
    bl_idname = "cyatools.constraint_apply_all"
    bl_label = ""
    mode : IntProperty()
    def execute(self, context):
        constraint.apply_all(self.mode)
        return {'FINISHED'}


#---------------------------------------------------------------------------------------
#transform
#---------------------------------------------------------------------------------------
class CYATOOLS_OT_swap_axis(Operator):
    """軸をスワップする"""
    bl_idname = "cyatools.swap_axis"
    bl_label = ""
    axis : StringProperty()
    def execute(self, context):
        locator.swap_axis(self.axis)
        return {'FINISHED'}


class CYATOOLS_OT_transform_rot90deg(Operator):
    """90度モデルを回転させる"""
    bl_idname = "cyatools.transform_rot90deg"
    bl_label = ""
    axis : StringProperty()
    def execute(self, context):
        transform.rot90deg(self.axis)
        return {'FINISHED'}


#オブジェクトをX軸ミラーコンストレインする
class CYATOOLS_OT_instance_mirror(Operator):
    """インスタンスをミラーする
normal : 反転したインスタンスを作成
const : トランスフォームに反転高速する
rot : スケールを用いず回転で反転する"""
    bl_idname = "cyatools.instance_mirror"
    bl_label = "constraint mirror"
    op : StringProperty(default='x')
    def execute(self, context):
        locator.mirror(self.op)
        return {'FINISHED'}


#オブジェクトをX軸だけapply
class CYATOOLS_OT_trasnform_apply_x(Operator):
    """X軸だけapply"""
    bl_idname = "cyatools.trasnform_apply_x"
    bl_label = "apply x"
    op : StringProperty(default='x')
    def execute(self, context):
        transform.apply_x(self.op)
        return {'FINISHED'}

#カーソルの回転をリセット
class CYATOOLS_OT_trasnform_reset_cursor_rot(Operator):
    """Reset cursor rotation"""
    bl_idname = "cyatools.trasnform_reset_cursor_rot"
    bl_label = "reset cursor rot"
    def execute(self, context):
        transform.reset_cursor_rot()
        return {'FINISHED'}

#選択した骨でモデルを逆変換
class CYATOOLS_OT_trasnform_invert_bonetransform(Operator):
    """モデルとアーマチュアの骨を選択して、骨の逆変換をかける"""
    bl_idname = "cyatools.trasnform_invert_bonetransform"
    bl_label = "invert bone transform"
    def execute(self, context):
        transform.invert_bonetransform()
        return {'FINISHED'}


#---------------------------------------------------------------------------------------
#modering
#---------------------------------------------------------------------------------------
#モデルの-Xを削除
class CYATOOLS_OT_modeling_del_half_x(Operator):
    """モデルの-X側を削除"""
    bl_idname = "cyatools.modeling_del_half_x"
    bl_label = "del half x"
    def execute(self, context):
        modeling.del_half_x()
        return {'FINISHED'}

class CYATOOLS_OT_modeling_mirror_l_to_r(Operator):
    """mirror geometry from left side to right side. """
    bl_idname = "cyatools.modeling_mirror_l_to_r"
    bl_label = "mirror vtx"
    def execute(self, context):
        modeling.mirror_l_to_r()
        return {'FINISHED'}

class CYATOOLS_OT_modeling_select_linked_faces(Operator):
    """モデルの-X側を削除"""
    bl_idname = "cyatools.modeling_select_linked_faces"
    bl_label = "select linked faces"
    def execute(self, context):
        modeling.select_linked_faces()
        return {'FINISHED'}

class CYATOOLS_OT_modeling_pivot_by_facenormal(Operator):
    """Asign the model rotate pivot selected face normal"""
    bl_idname = "cyatools.modeling_pivot_by_facenormal"
    bl_label = "pivot_by_facenormal"
    def execute(self, context):
        modeling.pivot_by_facenormal()
        return {'FINISHED'}


class CYATOOLS_OT_modeling_copy_vertex_pos(Operator):
    """選択した頂点の位置をコピー"""
    bl_idname = "cyatools.modeling_copy_vertex_pos"
    bl_label = ""
    mode : IntProperty()

    def execute(self, context):
        modeling.copy_vertex_pos(self.mode)
        return {'FINISHED'}

# class CYATOOLS_OT_modeling_paste_vertex_pos(Operator):
#     """選択した頂点の位置をコピー"""
#     bl_idname = "cyatools.modeling_paste_vertex_pos"
#     bl_label = "paste vtx"
#     def execute(self, context):
#         modeling.paste_vertex_pos()
#         return {'FINISHED'}


class CYATOOLS_OT_modeling_copy_vertex_pos_blendshape(Operator):
    """ブレンドシェイプからに頂点の位置をコピー"""
    bl_idname = "cyatools.modeling_copy_vertex_pos_blendshape"
    bl_label = ""
    mode : IntProperty()

    def execute(self, context):
        modeling.copy_vertex_pos_blendshape(self.mode)
        return {'FINISHED'}


class CYATOOLS_OT_modeling_copy_vertex_pos_paste_to_blendshape(Operator):
    """他モデルから頂点をコピーして、選択中のブレンドシェイプにペーストする
    ブレンドシェイプのモデルをアクティブに"""
    bl_idname = "cyatools.modeling_copy_vertex_pos_paste_to_blendshape"
    bl_label = "copy vtx to blendshape"

    def execute(self, context):
        modeling.copy_vertex_pos_paste_to_blendshape()
        return {'FINISHED'}


# class CYATOOLS_OT_modeling_paste_vertex_pos_blendshape(Operator):
#     """ブレンドシェイプに頂点の位置をペースト"""
#     bl_idname = "cyatools.modeling_paste_vertex_pos_blendshape"
#     bl_label = "paste vtx blend"
#     def execute(self, context):
#         modeling.paste_vertex_pos_blendshape()
#         return {'FINISHED'}


class CYATOOLS_OT_modeling_normal_180deg(Operator):
    """自動スムーズにして角度を180度に設定"""
    bl_idname = "cyatools.modeling_normal_180deg"
    bl_label = "auto smooth 180deg"
    def execute(self, context):
        modeling.normal_180deg()
        return {'FINISHED'}

class CYATOOLS_OT_modeling_normal_clear(Operator):
    """自動スムーズにして角度を180度に設定"""
    bl_idname = "cyatools.modeling_normal_clear"
    bl_label = "normal clear"
    def execute(self, context):
        modeling.normal_clear()
        return {'FINISHED'}


class CYATOOLS_OT_modeling_extract_missingparts(Operator):
    """欠損を生成する 頂点グループに名前をつけて自動でカット
    . で区切る
    先頭 MISSINGPARTS
    基準にする骨名
    出力するメッシュ名
    例：MISSINGPARTS.lowerarm_l.model_leftarm
    """
    bl_idname = "cyatools.modeling_extract_missingparts"
    bl_label = "extract missingparts"
    def execute(self, context):
        modeling.extract_missingparts()
        return {'FINISHED'}

#ボックスを使ったモデルのカット
class CYATOOLS_OT_modeling_extract_missingparts2(Operator):
    """欠損を生成する 01_MISSING_PARTS_CUTTER　というコレクションにカッターモデルを入れて実行
    カッターモデル名に情報を入れる　. で区切る
    CUTTER.基準にする骨名.出力するメッシュ名
    例：CUTTER.lowerarm_l.model_leftarm
    """
    bl_idname = "cyatools.modeling_extract_missingparts2"
    bl_label = "extract missingparts2"
    def execute(self, context):
        modeling.extract_missingparts2()
        return {'FINISHED'}

#---------------------------------------------------------------------------------------
#アニメーション
#---------------------------------------------------------------------------------------
class CYATOOLS_OT_anim_remove_transform_key(Operator):
    """トランスフォームのキーを削除"""
    bl_idname = "cyatools.anim_remove_transform_key"
    bl_label = ""
    mode : StringProperty()
    def execute(self, context):
        blendshape.remove_transform_key(self.mode)
        return {'FINISHED'}


#---------------------------------------------------------------------------------------
#ブレンドシェイプ
#---------------------------------------------------------------------------------------
# class CYATOOLS_OT_blendshape_copy_vertex_pos(Operator):
#     """選択した頂点の位置をコピー"""
#     bl_idname = "cyatools.blendshape_copy_vertex_pos"
#     bl_label = "copy vtx"
#     def execute(self, context):
#         blendshape.copy_pos()
#         return {'FINISHED'}

# class CYATOOLS_OT_blendshape_paste_vertex_pos(Operator):
#     """選択した頂点の位置をコピー"""
#     bl_idname = "cyatools.blendshape_paste_vertex_pos"
#     bl_label = "paste vtx"
#     def execute(self, context):
#         blendshape.paste_pos()
#         return {'FINISHED'}


# class CYATOOLS_OT_blendshape_save_vtxpos_delta(Operator):
#     """頂点の位置の差分を取得して保存する"""
#     bl_idname = "cyatools.blendshape_save_vtxpos_delta"
#     bl_label = "save vtxpos delta"
#     def execute(self, context):
#         blendshape.save_vtxpos_delta()
#         return {'FINISHED'}

class CYATOOLS_OT_blendshape_save_vtxpos_delta(Operator):
    """頂点の位置の差分を取得して保存する
    変形後、変形前の順に選択して選択して実行(変形前をアクティブ)
    """
    bl_idname = "cyatools.blendshape_save_vtxpos_delta"
    bl_label = "save vtxpos delta"

    filepath : bpy.props.StringProperty(subtype="FILE_PATH")
    filename : StringProperty()
    directory : StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        blendshape.save_vtxpos_delta(self.filepath)
        #skinning.weight_export(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class CYATOOLS_MT_blendshape_import_vtxpos_delta(Operator):
    bl_idname = "cyatools.blendshape_import_vtxpos_delta"
    bl_label = ""

    filepath : bpy.props.StringProperty(subtype="FILE_PATH")
    filename : StringProperty()
    directory : StringProperty(subtype="FILE_PATH")
    mode : IntProperty()

    def execute(self, context):
        blendshape.import_vtxpos_delta(self.filepath,self.mode)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class CYATOOLS_OT_blendshape_setup_mob_face(Operator):
    """インゲームのタ－ゲット用シェイプキーの作成"""
    bl_idname = "cyatools.blendshape_setup_mob_face"
    bl_label = "setup"
    mode : IntProperty()

    def execute(self, context):
        blendshape.setup_mob_face(self.mode)
        return {'FINISHED'}

class CYATOOLS_OT_blendshape_setup_mob_face2(Operator):
    """モブのインゲームフェイシャルターゲットをインポート
    E:/data/project/YKS/Characters/Data/Mob/FacialData/"""
    bl_idname = "cyatools.blendshape_setup_mob_face2"
    bl_label = "import target"
    mode : IntProperty()

    def execute(self, context):
        blendshape.setup_mob_face2(self.mode)
        return {'FINISHED'}


class CYATOOLS_OT_blendshape_keep_pos(Operator):
    """選択したブレンドシェイプから下のものを保持する"""
    bl_idname = "cyatools.blendshape_keep_pos"
    bl_label = "keep"
    def execute(self, context):
        blendshape.keep_downstream()
        return {'FINISHED'}

class CYATOOLS_OT_blendshape_restore_pos(Operator):
    """選択したブレンドシェイプの下のものを復帰する"""
    bl_idname = "cyatools.blendshape_restore_pos"
    bl_label = "restore"
    def execute(self, context):
        blendshape.restore_downstream()
        return {'FINISHED'}

class CYATOOLS_OT_blendshape_remove_all_keys(Operator):
    """選択したモデルのブレンドシェイプキーを全削除"""
    bl_idname = "cyatools.blendshape_remove_all_keys"
    bl_label = "delete all keys"
    def execute(self, context):
        blendshape.remove_all_keys()
        return {'FINISHED'}

class CYATOOLS_OT_blendshape_insert_all_keys(Operator):
    """現在のフレームにキーを挿入"""
    bl_idname = "cyatools.blendshape_insert_all_keys"
    bl_label = "insert all keys"
    def execute(self, context):
        blendshape.insert_all_keys()
        return {'FINISHED'}

class CYATOOLS_OT_blendshape_remove_shapekey_unmuted(Operator):
    """ミュートされていないキーを削除"""
    bl_idname = "cyatools.blendshape_remove_shapekey_unmuted"
    bl_label = "remove unmuted"
    def execute(self, context):
        blendshape.remove_shapekey_unmuted()
        return {'FINISHED'}

class CYATOOLS_OT_blendshape_remove_shapekey_numbered(Operator):
    """末尾に番号が入ったキーを削除"""
    bl_idname = "cyatools.blendshape_remove_shapekey_numbered"
    bl_label = "remove numbered"
    def execute(self, context):
        blendshape.remove_shapekey_numbered()
        return {'FINISHED'}


class CYATOOLS_OT_blendshape_shape_key_clear(Operator):
    """シェイプキーをクリアする(削除はしない)"""
    bl_idname = "cyatools.blendshape_shape_key_clear"
    bl_label = "shape key clear"
    def execute(self, context):
        blendshape.shape_key_clear()
        return {'FINISHED'}


class CYATOOLS_OT_blendshape_copy_action(Operator):
    """シェイプキーの編集アクションをコピーする
    複数選択して、アクティブなものを他のものにコピー"""
    bl_idname = "cyatools.blendshape_copy_action"
    bl_label = "copy shepe key action"
    def execute(self, context):
        blendshape.copy_action()
        return {'FINISHED'}

class CYATOOLS_OT_blendshape_push_down(Operator):
    """フェイシャル"アニメーションをプッシュダウンする"""
    bl_idname = "cyatools.blendshape_push_down"
    bl_label = "push down"
    def execute(self, context):
        blendshape.push_down()
        return {'FINISHED'}

class CYATOOLS_OT_blendshape_shepekey_mute(Operator):
    """シェイプキーのミュート、アンミュート"""
    bl_idname = "cyatools.blendshape_shepekey_mute"
    bl_label = ""
    mode : BoolProperty()
    def execute(self, context):
        blendshape.shepekey_mute(self.mode)
        return {'FINISHED'}

#モブのブレンドシェイプのクリンナップ
class CYATOOLS_OT_blendshape_mob_facial_cleanup(Operator):
    """モブのブレンドシェイプのクリンナップ
    Faceitで作成して４つのモブ用フェイシャルターゲットを作成したら実行する
    余分なターゲットを削除して、ターゲット名を修正する
    """
    bl_idname = "cyatools.blendshape_mob_facial_cleanup"
    bl_label = "mob facial cleanup"
    def execute(self, context):
        blendshape.mob_facial_cleanup()
        return {'FINISHED'}

#モブバリエーションの抽出
class CYATOOLS_OT_blendshape_mob_extruct(Operator):
    """モブのブレンドシェイプのクリンナップ
    Faceitで作成して４つのモブ用フェイシャルターゲットを作成したら実行する
    余分なターゲットを削除して、ターゲット名を修正する
    """
    bl_idname = "cyatools.blendshape_mob_extruct"
    bl_label = ""
    mode : IntProperty()
    def execute(self, context):
        blendshape.mob_extruct0(self.mode)
        return {'FINISHED'}

#モブバリエーションの一括抽出
class CYATOOLS_OT_blendshape_mob_extruct_all(Operator):
    """モブのブレンドシェイプのクリンナップ
    Faceitで作成して４つのモブ用フェイシャルターゲットを作成したら実行する
    余分なターゲットを削除して、ターゲット名を修正する
    """
    bl_idname = "cyatools.blendshape_mob_extruct_all"
    bl_label = "extruct all"
    def execute(self, context):
        blendshape.mob_extruct_all()
        return {'FINISHED'}

#モブ顔バリエーションの一括抽出
class CYATOOLS_OT_blendshape_mob_extruct_face(Operator):
    """モブのブレンドシェイプのクリンナップ
    Faceitで作成して４つのモブ用フェイシャルターゲットを作成したら実行する
    余分なターゲットを削除して、ターゲット名を修正する
    """
    bl_idname = "cyatools.blendshape_mob_extruct_face"
    bl_label = "extruct face"
    def execute(self, context):
        blendshape.mob_extruct_face()
        return {'FINISHED'}

#モブ顔バリエーションの一括抽出
class CYATOOLS_OT_blendshape_mob_extruct_frame(Operator):
    """モブのブレンドシェイプのクリンナップ
    Faceitで作成して４つのモブ用フェイシャルターゲットを作成したら実行する
    余分なターゲットを削除して、ターゲット名を修正する
    """
    bl_idname = "cyatools.blendshape_mob_extruct_frame"
    bl_label = "extruct frame"
    def execute(self, context):
        blendshape.mob_extruct_frame()
        return {'FINISHED'}

#---------------------------------------------------------------------------------------
#material
#---------------------------------------------------------------------------------------
#reload texture
class CYATOOLS_OT_material_reload_texture(Operator):
    """reload all textures"""
    bl_idname = "cyatools.material_reload_texture"
    bl_label = "reload texture"
    def execute(self, context):
        etc.material_reload_texture()
        return {'FINISHED'}

#サブマテリアルの削除
class CYATOOLS_OT_material_remove_submaterial(Operator):
    """reload sub materials"""
    bl_idname = "cyatools.material_remove_submaterial"
    bl_label = "remove sub materials"
    def execute(self, context):
        etc.material_remove_submaterial()
        return {'FINISHED'}

#UVを追加
class CYATOOLS_OT_material_add_uv(Operator):
    """UVを追加する"""
    bl_idname = "cyatools.material_add_uv"
    bl_label = "add UV"
    def execute(self, context):
        etc.material_add_uv()
        return {'FINISHED'}

#アクティブUVを削除
class CYATOOLS_OT_remove_uv_index(Operator):
    """UVを追加する"""
    bl_idname = "cyatools.remove_uv_index"
    bl_label = ""
    def execute(self, context):
        etc.remove_uv_index()
        return {'FINISHED'}


#---------------------------------------------------------------------------------------
#スキニングツール
#---------------------------------------------------------------------------------------
class CYATOOLS_OT_skinning_add_influence_bone(Operator):
    """インフルエンスジョイント(vertexGroup)を追加:\nまずモデルを選択する。次にアーマチュアを選択してエディットモードに入りジョイントを選択する。"""
    bl_idname = "cyatools.skinning_add_influence_bone"
    bl_label = "add inf"
    def execute(self, context):
        skinning.add_influence_bone()
        return {'FINISHED'}


class CYATOOLS_OT_skinning_add_influence_bone_auto(Operator):
    """アーマチュアモディファイヤにアサインされている骨を自動で頂点グループに加える"""
    bl_idname = "cyatools.skinning_add_influence_bone_auto"
    bl_label = "add inf auto"
    def execute(self, context):
        skinning.add_influence_bone_auto()
        return {'FINISHED'}


class CYATOOLS_OT_skinning_copy_influence_bone(Operator):
    """まず、コピー先のモデル最後にコピー元のモデルを選択して実行する"""
    bl_idname = "cyatools.skinning_copy_influence_bone"
    bl_label = "copy inf"
    def execute(self, context):
        skinning.copy_influence_bone()
        return {'FINISHED'}


class CYATOOLS_OT_skinning_bind(Operator):
    """Armature Modifierを追加する
モデルとArmatureを選択して実行する"""
    bl_idname = "cyatools.skinning_bind"
    bl_label = "bind"
    def execute(self, context):
        skinning.bind()
        return {'FINISHED'}

class CYATOOLS_OT_skinning_weights_mirror(Operator):
    """ウェイトのミラーコピー
X+側から X-側へウェイトをコピーする
    """
    bl_idname = "cyatools.skinning_weights_mirror"
    bl_label = "mirror"
    mode : StringProperty()
    def execute(self, context):
        skinning.weights_mirror(self.mode)
        return {'FINISHED'}

class CYATOOLS_OT_skinning_assign_maxweights(Operator):
    """選択ボーンに100%ウェイトを振る
まずモデルを選択する。次にアーマチュアを選択してエディットモードに入りジョイントを選択する。"""
    bl_idname = "cyatools.skinning_assign_maxweights"
    bl_label = "100%"
    def execute(self, context):
        skinning.assign_maxweights()
        return {'FINISHED'}

class CYATOOLS_OT_skinning_weights_transfer(Operator):
    """複数モデルのウェイト転送
コピー先を複数選択し、最後にコピー元のモデルを選択して実行
batchにチェックを入れると、文字列をsuffixとしたモデルを
コピー元として転送する(ex:model_back > model)
"""

    bl_idname = "cyatools.skinning_weights_transfer"
    bl_label = "transfer"
    mode : StringProperty()
    def execute(self, context):
        skinning.weights_transfer(self.mode)
        return {'FINISHED'}


class CYATOOLS_OT_skinning_apply_without_armature_modifiers(Operator):
    """アーマチュア以外のモディファイヤをApplyする。"""
    bl_idname = "cyatools.skinning_apply_without_armature_modifiers"
    bl_label = "apply without armature"
    def execute(self, context):
        skinning.apply_without_armature_modifiers()
        return {'FINISHED'}

class CYATOOLS_OT_skinning_delete_allweights(Operator):
    """すべての頂点グループのウェイトを０にする"""
    bl_idname = "cyatools.skinning_delete_allweights"
    bl_label = "all"
    def execute(self, context):
        skinning.delete_allweights()
        return {'FINISHED'}

class CYATOOLS_OT_skinning_delete_unselectedweights(Operator):
    """選択されているのボーン以外のウェイトを０にする
まずモデルを選択し、次にアーマチュアを選択
エディットモードに入りボーンを選択して実行"""
    bl_idname = "cyatools.skinning_delete_unselectedweights"
    bl_label = "unselected"
    def execute(self, context):
        skinning.delete_unselectedweights()
        return {'FINISHED'}

class CYATOOLS_OT_skinning_remove_weight_selectedVTX(Operator):
    """選択されている頂点のウェイト値を０にする"""
    bl_idname = "cyatools.skinning_remove_weight_selectedvtx"
    bl_label = "removeSelectedVTX"
    def execute(self, context):
        skinning.remove_weight_selectedVTX()
        return {'FINISHED'}

class CYATOOLS_OT_skinning_remove_weights_selectedbone(Operator):
    """選択されている頂点から選択されている骨のウェイト値を０にする"""
    bl_idname = "cyatools.skinning_remove_weights_selectedbone"
    bl_label = "removeSelectedBone"
    def execute(self, context):
        skinning.remove_weights_selectedbone()
        return {'FINISHED'}


class CYATOOLS_OT_skinning_delete_with_word(Operator):
    """指定された文字列が含まれていないバーテックスグループを削除する"""
    bl_idname = "cyatools.skinning_delete_with_word"
    bl_label = "Keep groups including words "

    def execute(self, context):
        skinning.delete_with_word()
        return {'FINISHED'}

class CYATOOLS_OT_skinning_delete_not_exist_vtxgrp(Operator):
    """存在していない頂点グループ"""
    bl_idname = "cyatools.skinning_delete_notexist_vtxgrp"
    bl_label = "delete not exist"

    def execute(self, context):
        skinning.delete_notexist_vtxgrp()
        return {'FINISHED'}

class CYATOOLS_OT_skinning_delete_unselected_vtxgroup(Operator):
    """Allow you to remove unselected bone's vtx group.\n First select model,next select armature and enter edit mode.\n So select not excluded bones."""
    bl_idname = "cyatools.skinning_delete_unselected_vtxgroup"
    bl_label = "unselected"
    def execute(self, context):
        skinning.delete_unselected_vtxgroup()
        return {'FINISHED'}

class CYATOOLS_OT_skinning_delete_all_vtxgrp(Operator):
    """現在アサインされているバーテックスグループをすべて削除する"""
    bl_idname = "cyatools.skinning_delete_all_vtxgrp"
    bl_label = "delete all vtx grp"
    def execute(self, context):
        skinning.delete_all_vtxgrp()
        return {'FINISHED'}

class CYATOOLS_OT_skinning_selectgrp(Operator):
    """選択した頂点グループを閾値以上のウェイトの頂点を選択
    複数のメッシュが選択されているときは、頂点グループ名を元に複数選択する"""
    bl_idname = "cyatools.skinning_selectgrp"
    bl_label = "select "
    def execute(self, context):
        skinning.selectgrp()
        return {'FINISHED'}

class CYATOOLS_OT_sskinning_weighthummer(Operator):
    """閾値以下のウェイトを0にする"""
    bl_idname = "cyatools.skinning_weighthummer"
    bl_label = "hummer"
    def execute(self, context):
        skinning.hummer()
        return {'FINISHED'}

# class CYATOOLS_OT_skinning_weight_cleanup(Operator):
#     """ウェイトのクリンナップ
#     スムーズなどで入った変なウェイトをカットする
#     1.クリンナップしたいモデルの頂点を選択
#     2.残したいアーマチュアの骨を選択
#     3.実行"""
#     bl_idname = "cyatools.skinning_weight_cleanup"
#     bl_label = "clean up"
#     def execute(self, context):
#         skinning.weight_cleanup()
#         return {'FINISHED'}



#モブ処理01
class CYATOOLS_OT_skinning_mob_process01(Operator):
    """モブ処理１"""
    bl_idname = "cyatools.skinning_mob_process01"
    bl_label = "process01"
    def execute(self, context):
        skinning.mob_process()
        return {'FINISHED'}

#---------------------------------------------------------------------------------------
#SKin FileBrowser
#---------------------------------------------------------------------------------------
class CYATOOLS_MT_skinning_rename_with_csvtable(Operator):
    bl_idname = "cyatools.skinning_rename_with_csvtable"
    bl_label = "rename vtx grp"

    filepath : bpy.props.StringProperty(subtype="FILE_PATH")
    filename : StringProperty()
    directory : StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        skinning.rename_with_csvtable(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class CYATOOLS_MT_skinning_transfer_with_csvtable(Operator):
    """csvの変換テーブルを使ってウェイトを転送"""
    bl_idname = "cyatools.skinning_transfer_with_csvtable"
    bl_label = "transfer "

    filepath : bpy.props.StringProperty(subtype="FILE_PATH")
    filename : StringProperty()
    directory : StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        skinning.transfer_with_csvtable(self.filepath)
        return {'FINISHED'}



class CYATOOLS_OT_skinning_export_vertexgroup_list(Operator):
    """頂点グループのリストを出力"""
    bl_idname = "cyatools.skinning_export_vertexgroup_list"
    bl_label = "export vertex group"

    filepath : bpy.props.StringProperty(subtype="FILE_PATH")
    filename : StringProperty()
    directory : StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        skinning.export_vertexgroup_list(self.filepath)
        return {'FINISHED'}

#---------------------------------------------------------------------------------------
#ウェイト　インポート　エクスポート
#---------------------------------------------------------------------------------------
class CYATOOLS_MT_skinning_weight_export(Operator):
    bl_idname = "cyatools.skinning_weight_export"
    bl_label = "export"

    filepath : bpy.props.StringProperty(subtype="FILE_PATH")
    filename : StringProperty()
    directory : StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        skinning.weight_export(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class CYATOOLS_MT_skinning_weight_import(Operator):
    bl_idname = "cyatools.skinning_weight_import"
    bl_label = "import"

    filepath : bpy.props.StringProperty(subtype="FILE_PATH")
    filename : StringProperty()
    directory : StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        skinning.weight_import (self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#ウェイトインポート　モブ用
class CYATOOLS_OT_skinning_mob_import_faceit(Operator):
    """faceitのウェイトを読み込む"""
    bl_idname = "cyatools.skinning_mob_import_faceit"
    bl_label = "faceit"
    def execute(self, context):
        skinning.mob_import_faceit()
        return {'FINISHED'}

class CYATOOLS_OT_skinning_mob_import_faceitrig(Operator):
    """faceitのウェイトを読み込む"""
    bl_idname = "cyatools.skinning_mob_import_faceitrig"
    bl_label = "faceitrig"
    def execute(self, context):
        skinning.mob_import_faceitrig()
        return {'FINISHED'}


class CYATOOLS_OT_skinning_mob_import_ingame(Operator):
    """インゲームのウェイトを読み込む"""
    bl_idname = "cyatools.skinning_mob_import_ingame"
    bl_label = "ingame"
    def execute(self, context):
        skinning.mob_import_ingame()
        return {'FINISHED'}


#---------------------------------------------------------------------------------------
#Rename
#---------------------------------------------------------------------------------------

class CYATOOLS_OT_rename_continuous_renumber(Operator):
    """入力した文字列の末尾に連番を振るリネーム"""
    bl_idname = "cyatools.rename_common_renumber"
    bl_label = ""
    def execute(self, context):
        rename.continuous_renumber()
        return {'FINISHED'}

class CYATOOLS_OT_rename_by_rule(Operator):
    """複数選択、アクティブなノード名のネーミングルールに従ってリネームする
アクティブノードがmodel_01なら、他のモデル名に
model_02,model_03と連番でリネームする"""
    bl_idname = "cyatools.rename_by_rule"
    bl_label = "follow active"
    def execute(self, context):
        rename.by_rule()
        return {'FINISHED'}

#プレフィックスとサフィックスの追加
class CYATOOLS_OT_rename_add(Operator):
    """プレフィクスを追加する。番号は振らない。"""
    bl_idname = "cyatools.rename_add"
    bl_label = ""
    op : StringProperty()
    def execute(self, context):
        rename.add(self.op)
        return {'FINISHED'}

class CYATOOLS_OT_rename_replace(Operator):
    """fromの文字列をtoに置き換える"""
    bl_idname = "cyatools.rename_replace"
    bl_label = "replace"
    def execute(self, context):
        rename.replace()
        return {'FINISHED'}

class CYATOOLS_OT_rename_replace_defined(Operator):
    bl_idname = "cyatools.rename_replace_defined"
    bl_label = "名前の一部を差し替える"
    op : StringProperty()
    def execute(self, context):
        rename.replace_defined(self.op)
        return {'FINISHED'}

class CYATOOLS_OT_rename_mesh(Operator):
    """mesh : メッシュの名前をオブジェクト名に合わせる
maya : メッシュ名をオブジェクト名に合わせ、末尾にShapeをつける"""
    bl_idname = "cyatools.rename_mesh"
    bl_label = ""
    op : StringProperty()
    def execute(self, context):
        rename.mesh(self.op)
        return {'FINISHED'}

class CYATOOLS_OT_rename_add_defined(Operator):
    bl_idname = "cyatools.rename_add_defined"
    bl_label = "名前の末尾にボタンの文字を追加"
    op : StringProperty()
    def execute(self, context):
        rename.add_defined(self.op)
        return {'FINISHED'}

class CYATOOLS_OT_rename_select(Operator):
    """名前フィールドのワードで選択する"""
    bl_idname = "cyatools.rename_select"
    bl_label = ""
    def execute(self, context):
        rename.select()
        return {'FINISHED'}

#アクティブなオブジェクトの名前をフィールドに入力する
class CYATOOLS_OT_rename_dropper(Operator):
    """アクティブなオブジェクトの名前をフィールドに入力する"""
    bl_idname = "cyatools.rename_dropper"
    bl_label = ""
    def execute(self, context):
        rename.dropper()
        return {'FINISHED'}


#---------------------------------------------------------------------------------------
#
#Scene Setup Tools
#
#---------------------------------------------------------------------------------------

class CYATOOLS_OT_scenesetup_makeproxy(Operator):
    """キャラを自動でプロキシモデルに"""
    bl_idname = "cyatools.scenesetup_makeproxy"
    bl_label = "Make Proxy"
    def execute(self, context):
        scenesetup.make_proxy()
        return {'FINISHED'}

class CYATOOLS_OT_scenesetup_rename_collection_model(Operator):
    """コレクションに合わせてモデル名をリネームする"""
    bl_idname = "cyatools.scenesetup_rename_collection_model"
    bl_label = "Rename To Match Collections"
    def execute(self, context):
        scenesetup.rename_collection_model()
        return {'FINISHED'}


class CYATOOLS_OT_scenesetup_create_new_collection(Operator):
    """新規コレクション追加　自動連番機能つき"""
    bl_idname = "cyatools.scenesetup_create_new_collection"
    bl_label = "Create"
    def execute(self, context):
        scenesetup.create_new_collection()
        return {'FINISHED'}

class CYATOOLS_OT_scenesetup_create_skin_parts(Operator):
    """Skin Partsの基本コレクションの作成"""
    bl_idname = "cyatools.scenesetup_create_skin_parts"
    bl_label = "Create"
    def execute(self, context):
        scenesetup.create_new_skin_parts()
        return {'FINISHED'}


class CYATOOLS_OT_scenesetup_pick_collection_name(Operator):
    """コレクションの名前をピックする"""
    bl_idname = "cyatools.scenesetup_pick_collection_name"
    bl_label = "Pick Collection Name"
    def execute(self, context):
        scenesetup.pick_collection_name()
        return {'FINISHED'}


class CYATOOLS_OT_scenesetup_save_collection_state(Operator):
    """コレクションの表示情報をJsonで保存する"""
    bl_idname = "cyatools.scenesetup_save_collection_state"
    bl_label = "Save Collection State"
    def execute(self, context):
        scenesetup.save_collection_state()
        return {'FINISHED'}


class CYATOOLS_OT_scenesetup_match_render_to_view(Operator):
    """レンダリングを表示状態に一致させる"""
    bl_idname = "cyatools.scenesetup_match_render_to_view"
    bl_label = "Match render state to view"
    def execute(self, context):
        scenesetup.match_render_to_view()
        return {'FINISHED'}


class CYATOOLS_OT_scenesetup_mob_offset(Operator):
    """モブの位置オフセットの設定"""
    bl_idname = "cyatools.scenesetup_mob_offset"
    bl_label = ""
    mode : IntProperty()

    def execute(self, context):
        scenesetup.mob_offset(self.mode)
        return {'FINISHED'}


class CYATOOLS_OT_scenesetup_mob_modify_vtxgrp(Operator):
    """モブの頂点グループをゲーム用に修正"""
    bl_idname = "cyatools.scenesetup_mob_modify_vtxgrp"
    bl_label = "mob modify vtxgrp"
    def execute(self, context):
        scenesetup.mob_modify_vtxgrp()
        return {'FINISHED'}

#---------------------------------------------------------------------------------------
#
#Facemap Tools
#
#---------------------------------------------------------------------------------------

class CYATOOLS_OT_facemap_select_backside(Operator):
    """Backsideというフェイスマップを選する択"""
    bl_idname = "cyatools.facemap_select_backside"
    bl_label = "Select Backside"
    def execute(self, context):
        facemap.select_backside()
        return {'FINISHED'}


#---------------------------------------------------------------------------------------
#ここから下のリネームツール、未対応
#---------------------------------------------------------------------------------------
class Rename_del_suffix(Operator):
    """アンダーバーで区切られたサフィックスを削除する"""
    bl_idname = "object.rename_del_suffix"
    bl_label = "suffixを削除"

    def execute(self, context):
        for ob in bpy.context.selected_objects:
            buf = ob.name.split('_')
            new = ob.name.replace('_'+buf[-1],'')
            print(ob.data.name)
            ob.name = new
            ob.data.name = new#メッシュの名前もついでに変更する
        return {'FINISHED'}


class Rename_Del_Suffix_number(Operator):
    """ノード名の末尾の.数字を削除"""
    bl_idname = "object.rename_del_suffix_number"
    bl_label = "ノード名の末尾の.数字を削除"

    def execute(self, context):
        for ob in bpy.context.selected_objects:
            buf = ob.name.split(".")
            #末尾が数字か調べる
            if buf[-1].isdigit():
                ob.name = ob.name[:-(len(buf[-1])+1)]
        return {'FINISHED'}

#前提条件として、orgは先頭の要素ではない、orgの前に必ず数字がついてる
class Renumber_Pre_Org(Operator):
    """orgの前の番号をスタート番号から順番に番号を振りなおす"""
    bl_idname = "object.renumber_pre_org"
    bl_label = "orgの前の番号を振りなおす"

    def execute(self, context):
        num = bpy.context.scene.nico2_rename_start_number
        for ob in bpy.context.selected_objects:
            buf = ob.name.split("_")

            #org.001みたいになっている場合も考慮する必要あり

            for i,b in enumerate(buf):
                if b.find('org') != -1:
                    index = i - 1

            buf[index] = '%02d' % num
            num += 1

            newname = ''
            for b in buf:
                newname += b + '_'

            ob.name = newname[:-1] #最後の _ を削除している
        return {'FINISHED'}



classes = (
    CYATOOLS_Props_OA,

    # UI Panel
    CYATOOLS_PT_toolPanel,
    CYATOOLS_MT_modeling_tools,
    CYATOOLS_MT_blendshape_tools,

    CYATOOLS_MT_modifier_tools,
    CYATOOLS_MT_object_applier,
    CYATOOLS_MT_curvetools,
    CYATOOLS_MT_scenesetuptools,
    CYATOOLS_MT_facemaptools,
    CYATOOLS_OT_curve_create_liner,
    CYATOOLS_OT_curve_assign_bevel,
    CYATOOLS_OT_curve_assign_circle_bevel,
    CYATOOLS_OT_curve_assign_liner_bevel,
    CYATOOLS_OT_curve_select_bevel,
    CYATOOLS_OT_curve_assign_taper_selected,
    CYATOOLS_OT_curve_assign_taper,


    # helper
    CYATOOLS_OT_replace_locator,
    CYATOOLS_OT_replace_locator_facenormal,
    CYATOOLS_OT_group,
    CYATOOLS_OT_collection_sort,
    CYATOOLS_OT_locator_tobone,
    CYATOOLS_OT_locator_tobone_keep,
    CYATOOLS_OT_modeling_separate_face,


    #モデリング
    CYATOOLS_OT_modeling_del_half_x,
    CYATOOLS_OT_modeling_pivot_by_facenormal,
    CYATOOLS_OT_modeling_select_linked_faces,
    CYATOOLS_OT_modeling_mirror_l_to_r,
    CYATOOLS_OT_modeling_copy_vertex_pos,
    #CYATOOLS_OT_modeling_paste_vertex_pos,
    #CYATOOLS_OT_modeling_paste_vertex_pos_blendshape,
    CYATOOLS_OT_modeling_copy_vertex_pos_blendshape,
    CYATOOLS_OT_modeling_copy_vertex_pos_paste_to_blendshape,


    CYATOOLS_OT_modeling_normal_180deg,
    CYATOOLS_OT_modeling_normal_clear,
    CYATOOLS_OT_modeling_extract_missingparts,
    CYATOOLS_OT_modeling_extract_missingparts2,

    # transform
    CYATOOLS_OT_swap_axis,
    CYATOOLS_OT_trasnform_apply_x,
    CYATOOLS_OT_trasnform_reset_cursor_rot,
    CYATOOLS_OT_trasnform_invert_bonetransform,
    CYATOOLS_OT_transform_rot90deg,


    # instance
    CYATOOLS_OT_instance_select_collection,
    CYATOOLS_OT_instance_instancer,
    CYATOOLS_OT_instance_substantial,
    CYATOOLS_OT_instance_replace,

    # modifier
    CYATOOLS_OT_modifier_asign,
    CYATOOLS_OT_modifier_show,
    CYATOOLS_OT_modifier_hide,
    CYATOOLS_OT_modifier_apply,
    CYATOOLS_OT_modifier_select_curve,
    CYATOOLS_OT_modifier_select_boolean,
    CYATOOLS_OT_modifier_send_to,
    CYATOOLS_OT_modifier_apply_all,
    CYATOOLS_OT_modifier_remove,

    CYATOOLS_OT_modifier_simple,

    # constraint
    CYATOOLS_OT_constraint_asign,
    CYATOOLS_OT_instance_mirror,
    CYATOOLS_OT_constraint_apply_all,

    # object applier
    CYATOOLS_MT_new_scene,
    CYATOOLS_OT_move_model,
    CYATOOLS_OT_apply_collection,
    CYATOOLS_OT_apply_collection_instance,
    CYATOOLS_OT_remove_empty_collection,
    CYATOOLS_OT_apply_particle_instance,
    CYATOOLS_OT_apply_model,
    CYATOOLS_OT_move_collection,

    #リネーム
    CYATOOLS_MT_rename,
    CYATOOLS_OT_rename_continuous_renumber,
    CYATOOLS_OT_rename_by_rule,
    CYATOOLS_OT_rename_add,
    CYATOOLS_OT_rename_replace,
    CYATOOLS_OT_rename_replace_defined,
    CYATOOLS_OT_rename_mesh,
    CYATOOLS_OT_rename_add_defined,
    CYATOOLS_OT_rename_select,
    CYATOOLS_OT_rename_dropper,


    #スキニング
    CYATOOLS_MT_skinningtools,
    CYATOOLS_OT_skinning_add_influence_bone,
    CYATOOLS_OT_skinning_add_influence_bone_auto,
    CYATOOLS_OT_skinning_copy_influence_bone,
    CYATOOLS_OT_skinning_bind,
    CYATOOLS_OT_skinning_weights_mirror,
    CYATOOLS_OT_skinning_assign_maxweights,
    CYATOOLS_OT_skinning_weights_transfer,
    CYATOOLS_OT_skinning_apply_without_armature_modifiers,
    CYATOOLS_OT_skinning_delete_allweights,
    CYATOOLS_OT_skinning_delete_unselectedweights,
    CYATOOLS_OT_skinning_remove_weight_selectedVTX,
    CYATOOLS_OT_skinning_remove_weights_selectedbone,

    CYATOOLS_OT_skinning_delete_with_word,
    CYATOOLS_OT_skinning_delete_not_exist_vtxgrp,
    CYATOOLS_OT_skinning_delete_all_vtxgrp,
    CYATOOLS_OT_skinning_delete_unselected_vtxgroup,
    CYATOOLS_OT_sskinning_weighthummer,

    CYATOOLS_MT_skinning_rename_with_csvtable,
    CYATOOLS_OT_skinning_export_vertexgroup_list,
    CYATOOLS_MT_skinning_transfer_with_csvtable,
    CYATOOLS_OT_skinning_selectgrp,
    #CYATOOLS_OT_skinning_weight_cleanup,

    CYATOOLS_MT_skinning_weight_export,
    CYATOOLS_MT_skinning_weight_import,
    CYATOOLS_OT_skinning_mob_import_faceit,
    CYATOOLS_OT_skinning_mob_import_faceitrig,
    CYATOOLS_OT_skinning_mob_import_ingame,
    CYATOOLS_OT_skinning_mob_process01,

    #マテリアル
    CYATOOLS_OT_material_reload_texture,
    CYATOOLS_OT_material_remove_submaterial,
    CYATOOLS_OT_material_add_uv,
    CYATOOLS_OT_remove_uv_index,

    #アニメーション
    CYATOOLS_OT_anim_remove_transform_key,

    #ブレンドシェイプ
    #CYATOOLS_OT_blendshape_copy_vertex_pos,
    #CYATOOLS_OT_blendshape_paste_vertex_pos,
    CYATOOLS_OT_blendshape_save_vtxpos_delta,
    CYATOOLS_MT_blendshape_import_vtxpos_delta,
    CYATOOLS_OT_blendshape_setup_mob_face,
    CYATOOLS_OT_blendshape_setup_mob_face2,

    CYATOOLS_OT_blendshape_keep_pos,
    CYATOOLS_OT_blendshape_restore_pos,
    CYATOOLS_OT_blendshape_remove_all_keys,
    CYATOOLS_OT_blendshape_insert_all_keys,
    CYATOOLS_OT_blendshape_shape_key_clear,
    CYATOOLS_OT_blendshape_copy_action,
    CYATOOLS_OT_blendshape_push_down,
    CYATOOLS_OT_blendshape_shepekey_mute,
    CYATOOLS_OT_blendshape_remove_shapekey_unmuted,
    CYATOOLS_OT_blendshape_remove_shapekey_numbered,
    CYATOOLS_OT_blendshape_mob_facial_cleanup,
    CYATOOLS_OT_blendshape_mob_extruct,
    CYATOOLS_OT_blendshape_mob_extruct_all,
    CYATOOLS_OT_blendshape_mob_extruct_face,
    CYATOOLS_OT_blendshape_mob_extruct_frame,


    #シーンセットアップ
    CYATOOLS_OT_scenesetup_makeproxy,
    CYATOOLS_OT_scenesetup_rename_collection_model,
    CYATOOLS_OT_scenesetup_create_new_collection,
    CYATOOLS_OT_scenesetup_pick_collection_name,
    CYATOOLS_OT_scenesetup_save_collection_state,
    CYATOOLS_OT_scenesetup_create_skin_parts,
    CYATOOLS_OT_scenesetup_match_render_to_view,
    CYATOOLS_OT_scenesetup_mob_offset,
    CYATOOLS_OT_scenesetup_mob_modify_vtxgrp,

    #フェースマップツール
    CYATOOLS_OT_facemap_select_backside,


)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.cyatools_oa = PointerProperty(type=CYATOOLS_Props_OA)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.cyatools_oa