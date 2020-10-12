import bpy
import imp
from bpy.app.handlers import persistent


from bpy.types import( 
    PropertyGroup,
    Panel,
    Operator,
    UIList,
    AddonPreferences
    )

from bpy.props import(
    FloatProperty,
    PointerProperty,
    CollectionProperty,
    EnumProperty,
    BoolProperty,
    StringProperty,
    IntProperty
    )

from .. import utils
from . import cmd
from . import setup_ik
from . import edit
from . import renamer
from . import duplicator
from . import constraint
from . import arp

imp.reload(utils)
imp.reload(cmd)
imp.reload(setup_ik)
imp.reload(edit)
imp.reload(renamer)
imp.reload(duplicator)
imp.reload(constraint)
imp.reload(arp)


AXIS = (('X','X','X'), ('Y','Y','Y'), ('Z','Z','Z'), ('-X','-X','-X'), ('-Y','-Y','-Y'), ('-Z','-Z','-Z'))

RIGSHAPEPATH = "E:\data\googledrive\lib\model/rig.blend"

#---------------------------------------------------------------------------------------
#アーマチュアを拾ってリグコントロールに使う
#
#---------------------------------------------------------------------------------------
#
#ボーンを選択順で拾うためのハンドラ <<　ボーンを選択順で拾う必要がなくなった
#エディットモードだと更新されないので、選択順をとるならポーズモードでとるしかない
#ツールの基本的な処理は、ポーズモードならallbonesで処理、エディットモードなら現在の選択をcontextから取得して処理する
#---------------------------------------------------------------------------------------

@persistent
def cyarigtools_handler(scene):
    return
    props = bpy.context.scene.cyarigtools_props
    amt = utils.getActiveObj()
    if amt == None:
        props.armature_name = ''
        return
    elif amt.type != 'ARMATURE':
        props.armature_name = ''
        return

    props.armature_name = amt.name

    selected = utils.get_selected_bones()
    #ボーンが何も選択されていなければリストをクリアする
    if selected == []:
        props.allbones.clear()

    else:
        if utils.current_mode() == 'POSE':
            act_bone = bpy.context.active_pose_bone.name
        elif utils.current_mode() == 'EDIT':
            act_bone = bpy.context.active_bone.name
            

        index_notExists = []
        #すでに選択されているものをアクティブにした場合、リストにあるものを削除して最後に追加する
        for i , bone in enumerate(props.allbones):
            if act_bone == bone.name:
                index_notExists.append(i)
            
        props.allbones.add().name = act_bone

        #選択されていなければリストから外す removeはインデックスで指定        
        for i , bone in enumerate(props.allbones):
            if not bone.name in [x.name for x in selected]:
                index_notExists.append(i)

        for index in reversed(index_notExists):
             props.allbones.remove(index)


#---------------------------------------------------------------------------------------
#Props
#---------------------------------------------------------------------------------------        
class CYARIGTOOLS_Props_OA(PropertyGroup):
    handler_through : BoolProperty(default = False)

    allbones : CollectionProperty(type=PropertyGroup)
    rigshape_scale : FloatProperty( name = "scale", min=0.01,default=1.0, update = cmd.rigshape_change_scale )
    setupik_lr : EnumProperty(items= (('l', 'l', 'L'),('r', 'r', 'R')))
    setupik_number : IntProperty(name="count", default=2)
    ploc_number : IntProperty(name="count", default=2)
    setup_chain_baseame : StringProperty( name = 'name' )
    parent_polevector : BoolProperty()

    #コンストレイン関連
    const_influence : FloatProperty( name = "influence", min=0.00 , max=1.0, default=1.0, update= edit.constraint_showhide )
    const_showhide : BoolProperty( name = 'mute', update = edit.constraint_change_influence )

    #リグのコントロール
    armature_name : StringProperty( name = 'armature' )

    axismethod : EnumProperty(items= (('new', 'new', 'new'),('old', 'old', 'old')))

    for r in cmd.RIGARRAY:
        for p in cmd.PROPARRAY[r]:
            for lr in ('l' , 'r'):
                prop_val = '%s_%s_%s' % (r,p,lr)
                exec('%s : FloatProperty(  name = \"%s\",min=0.0 , max=1.0, default=1.0 , update = cmd.rig_change_ctr )' % ( prop_val ,lr ) )


    axis_forward : EnumProperty(items = AXIS , name = 'forward',default = '-Z' )
    axis_up : EnumProperty(items = AXIS , name = 'up' ,default = 'Y')



#---------------------------------------------------------------------------------------
#UI
#---------------------------------------------------------------------------------------
class CYARIGTOOLS_PT_ui(utils.panel):
    bl_label = "Rig Tools"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        props = bpy.context.scene.cyarigtools_props        

        col = self.layout.column(align=False)
        col.operator("cyarigtools.rigsetuptools",icon = 'OBJECT_DATA')
        col.operator("cyarigtools.edittools",icon = 'OBJECT_DATA')
        col.operator("cyarigtools.renamer",icon = 'OBJECT_DATA')
        col.operator("cyarigtools.duplicator",icon = 'OBJECT_DATA')
        col.operator("cyarigtools.constrainttools",icon = 'OBJECT_DATA')
        col.operator("cyarigtools.rigcontrolpanel",icon = 'OBJECT_DATA')
        col.operator("cyarigtools.arptools",icon = 'OBJECT_DATA')


#---------------------------------------------------------------------------------------
#リグセットアップツール
#---------------------------------------------------------------------------------------
class CYARIGTOOLS_MT_rigcontrolpanel(bpy.types.Operator):
    bl_idname = "cyarigtools.rigcontrolpanel"
    bl_label = "rig control panel"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        props = bpy.context.scene.cyarigtools_props
        amt = utils.getActiveObj()
        if amt == None:
            props.armature_name = ''
            return
        elif amt.type != 'ARMATURE':
            props.armature_name = ''
            return

        props.armature_name = amt.name

        for part in ('arm', 'leg'):
            for lr in ('l', 'r'):
                name = 'ctr.%s.%s' % (part , lr)

                if name in [b.name for b in amt.pose.bones]:
                    bone = amt.pose.bones[name]
                    val = bone.get('ikfk_%s' % lr )
                    if val != None:
                        exec('props.%s_ikfk_%s = val' % ( part , lr ))


        return context.window_manager.invoke_props_dialog(self , width=400)

    def draw(self, context):
        props = bpy.context.scene.cyarigtools_props        

        col = self.layout.column(align=False)

        box = col.box()

        box.prop(props, "armature_name")
        row = box.row()
        row.operator("cyarigtools.posetool_copy_matrix",icon = 'OBJECT_DATA')
        row.operator("cyarigtools.posetool_paste_matrix",icon = 'OBJECT_DATA')

        row  = col.column()

        box = row.box()
        row = box.row()

        for r in cmd.RIGARRAY:
            box1 = row.box()
            box1.label(text = r )

            for p in cmd.PROPARRAY[ r ]:
                box2 = box1.box()
                box2.label(text = p )

                for lr in ('l' , 'r'):
                    propname = "%s_%s_%s"  % (r , p , lr)
                    col = box2.column()
                    row1 = col.row()
                    row1.prop(props, propname )

                    cmd1 = row1.operator("cyarigtools.modify_rig_control_panel",icon = 'TRIA_DOWN')
                    cmd1.rig = r
                    cmd1.lr = lr
                    cmd1.propname = p
                    cmd1.value = 0.0

                    cmd1 = row1.operator("cyarigtools.modify_rig_control_panel",icon = 'TRIA_UP')
                    cmd1.rig = r
                    cmd1.lr = lr
                    cmd1.propname = p
                    cmd1.value = 100.0

                    cmd1 = row1.operator("cyarigtools.modify_rig_control_panel_key",icon = 'REC')
                    cmd1.rig = r
                    cmd1.lr = lr
                    cmd1.propname = p


def rig_ui_( props , row , parts , lr ):
    box1 = row.box()
    box1.label(text = '%s' % parts )

    box2 = box1.box()
    box2.label(text = 'ikfk')

    col = box2.column()
    row = col.row()
    row.prop(props, "%s_ikfk_%s"  % (parts , 'l') )
    row.operator("cyarigtools.rigctr_arm",icon = 'OBJECT_DATA')
    row.operator("cyarigtools.rigctr_arm",icon = 'OBJECT_DATA')

    col = box2.column()
    row = col.row()
    row.prop(props, "%s_ikfk_%s"  % (parts , 'r') )
    row.operator("cyarigtools.rigctr_arm",icon = 'OBJECT_DATA')
    row.operator("cyarigtools.rigctr_arm",icon = 'OBJECT_DATA')


    box2 = box1.box()
    box2.label(text = 'stretch')

    col = box2.column()
    row = col.row()
    row.prop(props, "%s_stretch_%s"  % (parts , 'l') )
    row.operator("cyarigtools.rigctr_arm",icon = 'OBJECT_DATA')
    row.operator("cyarigtools.rigctr_arm",icon = 'OBJECT_DATA')

    col = box2.column()
    row = col.row()
    row.prop(props, "%s_stretch_%s"  % (parts , 'r') )
    row.operator("cyarigtools.rigctr_arm",icon = 'OBJECT_DATA')
    row.operator("cyarigtools.rigctr_arm",icon = 'OBJECT_DATA')

#---------------------------------------------------------------------------------------
#リグセットアップツール
#---------------------------------------------------------------------------------------
class CYARIGTOOLS_MT_rigsetuptools(bpy.types.Operator):
    bl_idname = "cyarigtools.rigsetuptools"
    bl_label = "rig setup"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        props = bpy.context.scene.cyarigtools_props        

        col_root = self.layout.column(align=False)
        box = col_root.box()
        box.prop(props,'axismethod')

        row = col_root.row(align=False)
        box = row.box()

        box.label(text = 'rigshape')
        box.operator("cyarigtools.rigshape_selector",icon = 'OBJECT_DATA')
        box.operator("cyarigtools.rigshape_revert",icon = 'BONE_DATA')
        box.prop(props, "rigshape_scale", icon='BLENDER', toggle=True)
        box.operator("cyarigtools.rigshape_append")
        box.operator("cyarigtools.make_the_same_size")
    

        col = row.column()

        box = col.box()
        box.label(text = 'rig')
        box.prop(props,'setup_chain_baseame')
        row1 = box.row()
        row1.operator("cyarigtools.setupik_customrig",text = 'ik').mode = 'ik'
        row1.prop(props, "parent_polevector")

        row1 = box.row()
        row1.operator("cyarigtools.setupik_customrig",text = 'knee').mode = 'knee'
        row1.operator("cyarigtools.setupik_customrig",text = 'transform').mode = 'transform'

        row1 = box.row()
        row1.operator("cyarigtools.setupik_customrig",text = 'ploc').mode = 'ploc'
        row1.prop(props, "ploc_number")


        box.operator("cyarigtools.setupik_setup_rig_chain")


        box = col.box()
        box.label(text = 'setup ik')
        row1 = box.row()
        row1.operator("cyarigtools.setupik_ik").mode = 1
        row1.prop(props, "setupik_number")

        box.operator("cyarigtools.setupik_polevector")
        box.operator("cyarigtools.setupik_spline_ik")
        box.operator("cyarigtools.setupik_hook")


        box = col.box()
        box.label(text = 'setup for UE')
        box.operator("cyarigtools.setupik_ue")


        box = row.box()
        box.label(text = 'body')
        box.operator("cyarigtools.setupik_rig_arm")
        box.operator("cyarigtools.setupik_rig_leg")
        box.operator("cyarigtools.setupik_rig_spine")
        box.operator("cyarigtools.setupik_rig_spine_v2")
        box.operator("cyarigtools.setupik_rig_spine_v3")
        box.operator("cyarigtools.setupik_rig_neck")
        box.operator("cyarigtools.setupik_rig_neck_v2")
        box.operator("cyarigtools.setupik_rig_finger")
        box.prop(props, "setupik_lr", expand=True)


#---------------------------------------------------------------------------------------
#エディットツール
#---------------------------------------------------------------------------------------
class CYARIGTOOLS_MT_edittools(bpy.types.Operator):
    bl_idname = "cyarigtools.edittools"
    bl_label = "edit"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        props = bpy.context.scene.cyarigtools_props        
        props.handler_through = False
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        props = bpy.context.scene.cyarigtools_props        

        col_root = self.layout.column(align=False)
        box = col_root.box()
        box.prop(props,'axismethod')

        row = col_root.split(factor = 0.4, align = False)

        #上部左
        col = row.box()
        box = col.box()
        box.label(text = 'length')
        box.operator("cyarigtools.edit_length_uniform")
        box.operator("cyarigtools.edit_length_half")

        box = col.box()
        box.label(text = 'modify')
        box.operator("cyarigtools.edit_genarate_symmetry")
        box.operator("cyarigtools.edit_connect_chain")


        box = col.box()
        box.label(text = 'generate')
        box.operator("cyarigtools.edit_genarate_bone_from2")

        box = col.box()
        box.label(text = 'constraint')
        box.prop(props,"const_influence")
        box.prop(props,"const_showhide")

        box1 = box.box()
        box1.label(text = 'delete')
        row1 = box1.row()
        row1.operator("cyarigtools.edit_constraint_cleanup")
        row1.operator("cyarigtools.edit_constraint_empty_cleanup")

        #上部中央
        box = row.box()
        col1 = box.column()
        row1 = col1.row()
        box1 = row1.box()
        box1.label(text = 'align')
        box1.operator("cyarigtools.edit_align_position")
        box1.operator("cyarigtools.edit_align_direction")
        box1.operator("cyarigtools.edit_align_along")
        box1.operator("cyarigtools.edit_align_near_axis")

        box1 = row1.box()
        box1.label(text = 'align plane')
        box1.operator("cyarigtools.edit_align_2axis_plane")
        box1.operator("cyarigtools.edit_align_on_plane")
        box1.operator("cyarigtools.edit_align_at_flontview")

        box = col1.box()
        box.label(text = 'direction')
        col = box.column()

        box1 = col.box()
        box1.label(text = 'roll')

        row = box1.row()
        for x in ( '90d' , '-90d' , '180d'):
            row.operator("cyarigtools.edit_roll_degree" ,text = x ).op = x

        box1 = col.box()
        box1.label(text = 'axis swap')

        row = box1.row()
        for x in ( 'x' , 'y' , 'z' ,'invert'):
            row.operator("cyarigtools.edit_axis_swap" ,text = x ).op = x


        row = col.row()
        row.operator("cyarigtools.edit_adjust_roll")
        row.operator("cyarigtools.edit_align_roll_global")

        #Add bone at the selected objects
        # First, select some objects ,select bone in the end.
        box3 = col1.box()
        box3.label( text = 'bone and object' )
        row = box3.row()
        row.operator( "cyarigtools.locator_add_bone")
        row.operator( "cyarigtools.locator_snap_bone_at_obj")

        row1 = box3.row()
        row1.prop(props, 'axis_forward',text = 'fwd')
        row1.prop(props, 'axis_up')

        # box = col_root.box()
        # box.label(text = 'other commands')
        # row = box.row()
        # row.operator("cyarigtools.edit_connect_chain")
        # row.operator("cyarigtools.edit_delete_rig")




#---------------------------------------------------------------------------------------
#リグシェイプUI : シーンからリグシェイプを検索してポップアップに登録
#---------------------------------------------------------------------------------------
class CYARIGTOOLS_PT_rigshape_selector(bpy.types.Operator):
    """選択した骨をリストのシェイプに置き換える"""
    bl_idname = "cyarigtools.rigshape_selector"
    bl_label = "replace"
    bl_options = {'REGISTER', 'UNDO'}

    prop : bpy.props.StringProperty(name="RigShape", maxlen=63)
    rigshapes : bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    def execute(self, context):
        utils.mode_p()
        for bone in bpy.context.selected_pose_bones:
            obj = bpy.data.objects[self.prop]
            bone.custom_shape = obj

        utils.mode_e()
        for bone in bpy.context.selected_bones:
            bone.show_wire = True

        utils.mode_p()
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop_search(self, "prop", self, "rigshapes", icon='MESH_DATA')

    def invoke(self, context, event):
        self.rigshapes.clear()
        for obj in bpy.data.objects:
            if obj.name.find('rig.shape.') != -1:
                self.rigshapes.add().name = obj.name
        return context.window_manager.invoke_props_dialog(self)


        #col.operator("cyarigtools.arppanel",icon = 'OBJECT_DATA')

#---------------------------------------------------------------------------------------
#Rigify Toos UI
#---------------------------------------------------------------------------------------
class CYARIGTOOLS_MT_arptools(bpy.types.Operator):
    """Auto Rig Pro用ツール"""
    bl_idname = "cyarigtools.arptools"
    bl_label = "ARP Tools"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.operator("cyarigtools.arp_extracter")
        box.operator("cyarigtools.arp_connect")
        box.operator("cyarigtools.arp_disable_ikstretch")

        box = layout.box()
        box.label(text="Constraint")
        row = box.row()
        row.operator("cyarigtools.arp_const",text = 'ue4').rig = 'ue4'
        row.operator("cyarigtools.arp_const",text = 'mixamo').rig = 'mixamo'


        box = layout.box()
        box.label(text="Adjust ARP")
        row = box.row()
        row.operator( 'cyarigtools.adjust_arp',text = "UE4").mode = 'ue4'
        row.operator( 'cyarigtools.adjust_arp',text = "MIXAMO").mode = 'mixamo'




#---------------------------------------------------------------------------------------
# Operator
#---------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------
# Rig Shape
#---------------------------------------------------------------------------------------
#リグシェイプを通常のボーンに戻す
class CYARIGTOOLS_OT_rigshape_revert(bpy.types.Operator):
    """リグシェイプを通常のボーンに戻す"""
    bl_idname = "cyarigtools.rigshape_revert"
    bl_label = "revert"
    def execute(self, context):
        cmd.rigshape_revert()
        return {'FINISHED'}

#リグシェイプをRigShape_Scnに入れる
class CYARIGTOOLS_OT_rigshape_append(bpy.types.Operator):
    """リグシェイプをシーンにアペンドする"""
    bl_idname = "cyarigtools.rigshape_append"
    bl_label = "append"
    def execute(self, context):
        #prefs = bpy.context.preferences.addons[__name__].preferences
        cmd.rigshape_append()
        return {'FINISHED'}

#Make selected rig shape the same size. The active is the size basis.
class CYARIGTOOLS_OT_make_the_same_size(bpy.types.Operator):
    """Make selected rig shape the same size. The active is the size basis."""
    bl_idname = "cyarigtools.make_the_same_size"
    bl_label = "same size"
    def execute(self, context):
        cmd.make_the_same_size()
        return {'FINISHED'}


#---------------------------------------------------------------------------------------
# setup custom rig
#---------------------------------------------------------------------------------------
class CYARIGTOOLS_OT_setupik_customrig(bpy.types.Operator):
    """Allow you to set up custom rigs.
    ik:
    Add ik controller and pole vector.
    First ,select 2 joint bones, and execute this command.
    
    knee:
    Add knee bone and constraint knee to leg bone.
    First ,select 2 joint bones, and execute this command.

    transform:
    Add simple transform constraint node.
    First ,select a single bone, and execute this command.

    ploc:
    Add procedural rotation node.
    First ,select a single bone, and decide procedural bone number.
    next exeute this command."""

    bl_idname = "cyarigtools.setupik_customrig"
    bl_label = ""
    mode : StringProperty()
    def execute(self, context):
        setup_ik.customrig(self.mode)
        return {'FINISHED'}

#---------------------------------------------------------------------------------------
# setup ik
#---------------------------------------------------------------------------------------
class CYARIGTOOLS_OT_setupik_ik(bpy.types.Operator):
    """IKのセットアップ。ＩＫの先端とコントローラの順にリストに加えて実行する。"""
    bl_idname = "cyarigtools.setupik_ik"
    bl_label = "ik"
    mode : IntProperty()
    def execute(self, context):
        setup_ik.ik(self.mode)
        return {'FINISHED'}

class CYARIGTOOLS_OT_setupik_polevector(bpy.types.Operator):
    """ポールベクターのセットアップ\n根本、先の順に選択する"""
    bl_idname = "cyarigtools.setupik_polevector"
    bl_label = "pole vec"
    def execute(self, context):
        setup_ik.polevector()
        return {'FINISHED'}

class CYARIGTOOLS_OT_setupik_spline_ik(bpy.types.Operator):
    """リストに根本から先端までのボーンを入力する。\nコントローラは自動で生成される。\n先頭のボーンを選択しておくこと。\nベジェカーブが生成されるのでそれでコントロールする。"""
    bl_idname = "cyarigtools.setupik_spline_ik"
    bl_label = "spline ik"  
    def execute(self, context):
        setup_ik.spline_ik()
        return {'FINISHED'}

class CYARIGTOOLS_OT_setupik_hook(bpy.types.Operator):
    """カーブとアーマチュアを選択して実行\nコントローラは自動で生成される"""
    bl_idname = "cyarigtools.setupik_hook"
    bl_label = "hook"
    def execute(self, context):
        setup_ik.hook()
        return {'FINISHED'}

class CYARIGTOOLS_OT_setupik_rig_arm(bpy.types.Operator):
    """腕のリグの自動設定\n鎖骨、上腕、前腕、手の順でリストに並べる"""
    bl_idname = "cyarigtools.setupik_rig_arm"
    bl_label = "arm"
    def execute(self, context):
        setup_ik.setup_rig_arm()
        return {'FINISHED'}

class CYARIGTOOLS_OT_setupik_rig_leg(bpy.types.Operator):
    """脚足のリグの自動設定\n腰、太もも、すね、足、つま先の順でリストに並べる"""
    bl_idname = "cyarigtools.setupik_rig_leg"
    bl_label = "leg"
    def execute(self, context):
        setup_ik.setupik_rig_leg()
        return {'FINISHED'}

class CYARIGTOOLS_OT_setupik_rig_spine(bpy.types.Operator):
    """背骨のリグの自動設定\n腰から胸までの骨を順番にリストに登録して実行"""
    bl_idname = "cyarigtools.setupik_rig_spine"
    bl_label = "spine"
    def execute(self, context):
        setup_ik.setup_rig_spine()
        return {'FINISHED'}

class CYARIGTOOLS_OT_setupik_rig_spine_v2(bpy.types.Operator):
    """背骨のリグの自動設定\n腰から胸までの骨を順番にリストに登録して実行"""
    bl_idname = "cyarigtools.setupik_rig_spine_v2"
    bl_label = "spine v2"
    def execute(self, context):
        setup_ik.setup_rig_spine_v2()
        return {'FINISHED'}

class CYARIGTOOLS_OT_setupik_rig_spine_v3(bpy.types.Operator):
    """背骨のリグの自動設定\n腰から胸までの骨を順番にリストに登録して実行"""
    bl_idname = "cyarigtools.setupik_rig_spine_v3"
    bl_label = "spine v3"
    def execute(self, context):
        setup_ik.setup_rig_spine_v3()
        return {'FINISHED'}

class CYARIGTOOLS_OT_setupik_rig_neck(bpy.types.Operator):
    """首骨のリグの自動設定\n胸の骨、首、頭までの骨を順番にリストに登録して実行"""    
    bl_idname = "cyarigtools.setupik_rig_neck"
    bl_label = "neck"
    def execute(self, context):
        setup_ik.setup_rig_neck()
        return {'FINISHED'}

class CYARIGTOOLS_OT_setupik_rig_neck_v2(bpy.types.Operator):
    """首骨のリグの自動設定:
        胸の骨、首、頭までの骨を順番にリストに登録して実行"""    

    bl_idname = "cyarigtools.setupik_rig_neck_v2"
    bl_label = "neck v2"
    def execute(self, context):
        setup_ik.setup_rig_neck_v2()
        return {'FINISHED'}

class CYARIGTOOLS_OT_setupik_rig_finger(bpy.types.Operator):
    """指のリグの自動設定:
    指のルートボーンを選択して実行する。
    ボーンのフォーマットはindex_01_lで最初と最後の要素を使う。
    できあがるコントローラ名は ctr.index.lとなる。
    tweakノードはctr.tweak.index_01.lとなる。"""    

    bl_idname = "cyarigtools.setupik_rig_finger"
    bl_label = "finger"
    def execute(self, context):
        setup_ik.setup_rig_finger()
        return {'FINISHED'}


class CYARIGTOOLS_OT_setupik_setup_rig_chain(bpy.types.Operator):
    """setup Unreal Engine Rig"""    
    bl_idname = "cyarigtools.setupik_setup_rig_chain"
    bl_label = "assign chain rig"
    def execute(self, context):
        setup_ik.setup_rig_chain()
        return {'FINISHED'}


#setup Unreal Engine Rig
class CYARIGTOOLS_OT_setupik_ue(bpy.types.Operator):
    """setup Unreal Engine Rig"""    
    bl_idname = "cyarigtools.setupik_ue"
    bl_label = "create ue rig"
    def execute(self, context):
        setup_ik.setup_ue()
        return {'FINISHED'}




#---------------------------------------------------------------------------------------
# edit tool
#---------------------------------------------------------------------------------------
class CYARIGTOOLS_OT_edit_length_uniform(bpy.types.Operator):
    """ボーンの長さをそろえる。\n最後に選択されたボーンに他のを合わせる"""
    bl_idname = "cyarigtools.edit_length_uniform"
    bl_label = "uniform"

    def execute(self, context):
        edit.length_uniform()
        return {'FINISHED'}


class CYARIGTOOLS_OT_edit_length_half(bpy.types.Operator):
    """選択されたボーンの長さを半分にする"""
    bl_idname = "cyarigtools.edit_length_half"
    bl_label = "half"
    def execute(self, context):
        edit.length_half()
        return {'FINISHED'}

class CYARIGTOOLS_OT_edit_genarate_bone_from2(bpy.types.Operator):
    """最初に選択したボーンの根本から、最後に選択したボーンの先端までのボーンを生成する"""
    bl_idname = "cyarigtools.edit_genarate_bone_from2"
    bl_label = "new from 2bone"
    def execute(self, context):
        edit.genarate_bone_from2()
        return {'FINISHED'}

#複製ではない
class CYARIGTOOLS_OT_edit_genarate_symmetry(bpy.types.Operator):
    """ネーミングルールでミラーリングする。エディットモードでコピー元のボーンを選択して実行する。"""
    bl_idname = "cyarigtools.edit_genarate_symmetry"
    bl_label = "symmetry"
    def execute(self, context):
        edit.genarate_symmetry()
        return {'FINISHED'}

class CYARIGTOOLS_OT_edit_align_position(bpy.types.Operator):
    """アクティブなジョイントの位置に、それ以外のジョイントの位置を合わせる。"""
    bl_idname = "cyarigtools.edit_align_position"
    bl_label = "position"
    def execute(self, context):
        edit.align_position()
        return {'FINISHED'}

class CYARIGTOOLS_OT_edit_align_direction(bpy.types.Operator):
    """アクティブなジョイントの向きに、それ以外のジョイントの向きを合わせる。"""
    bl_idname = "cyarigtools.edit_align_direction"
    bl_label = "direction"
    def execute(self, context):
        edit.align_direction()
        return {'FINISHED'}

class CYARIGTOOLS_OT_edit_align_along(bpy.types.Operator):
    """リストの最初のボーン上に以降のボーンを並べる"""
    bl_idname = "cyarigtools.edit_align_along"
    bl_label = "along"
    def execute(self, context):
        edit.align_along()
        return {'FINISHED'}

class CYARIGTOOLS_OT_edit_aling_near_axis(bpy.types.Operator):
    """近いグローバルび軸にボーンを向ける。\nボーンを選択して実行する。"""
    bl_idname = "cyarigtools.edit_align_near_axis"
    bl_label = "near axis"
    def execute(self, context):
        edit.align_near_axis()
        return {'FINISHED'}

class CYARIGTOOLS_OT_edit_align_2axis_plane(bpy.types.Operator):
    """２ボーンの平面を出して軸向きを合わせる"""
    bl_idname = "cyarigtools.edit_align_2axis_plane"
    bl_label = "2axis plane"
    def execute(self, context):
        edit.along_2axis_plane()
        return {'FINISHED'}

class CYARIGTOOLS_OT_edit_align_on_plane(bpy.types.Operator):
    """リストの1番目と２番目の基準平面にそれ以下のボーンをそろえる。"""
    bl_idname = "cyarigtools.edit_align_on_plane"
    bl_label = "on plane"
    def execute(self, context):
        edit.align_on_plane()
        return {'FINISHED'}

class CYARIGTOOLS_OT_edit_align_at_flontview(bpy.types.Operator):
    """正面から見たときにジョイントが直線に並ぶようにそろえる\nポーズモードで選択すること"""
    bl_idname = "cyarigtools.edit_align_at_flontview"
    bl_label = "frontview"
    def execute(self, context):
        edit.align_at_flontview()
        return {'FINISHED'}

class CYARIGTOOLS_OT_edit_adjust_roll(bpy.types.Operator):
    """リストから選択したものとその下のボーンでロール値を調整。\nいっぺんにすべてのボーンのロール修正ができないので２本ずつおこなう。"""
    bl_idname = "cyarigtools.edit_adjust_roll"
    bl_label = "adjust"
    def execute(self, context):
        edit.adjust_roll()
        return {'FINISHED'}

class CYARIGTOOLS_OT_edit_roll_degree(bpy.types.Operator):
    """ロールを90°回転させる。"""
    bl_idname = "cyarigtools.edit_roll_degree"
    bl_label = ""
    op : StringProperty()
    def execute(self, context):
        edit.roll_degree(self.op)
        return {'FINISHED'}

class CYARIGTOOLS_OT_edit_align_roll_global(bpy.types.Operator):
    """グローバル軸にX,Z軸向きをそろえる"""
    bl_idname = "cyarigtools.edit_align_roll_global"
    bl_label = "align global"
    def execute(self, context):
        edit.align_roll_global
        return {'FINISHED'}

class CYARIGTOOLS_OT_edit_axis_swap(bpy.types.Operator):
    """ロールを90°回転させる。"""
    bl_idname = "cyarigtools.edit_axis_swap"
    bl_label = ""
    op : StringProperty()
    def execute(self, context):
        edit.axis_swap(self.op)
        return {'FINISHED'}

#---------------------------------------------------------------------------------------
# rig control panel
#---------------------------------------------------------------------------------------
class CYARIGTOOLS_OT_rigctr_arm(bpy.types.Operator):
    """リグ"""
    bl_idname = "cyarigtools.rigctr_arm"
    bl_label = ""
    def execute(self, context):
        edit.align_roll_global
        return {'FINISHED'}

class CYARIGTOOLS_OT_modify_rig_control_panel(bpy.types.Operator):
    """modify rig control panel value"""
    bl_idname = "cyarigtools.modify_rig_control_panel"
    bl_label = ""
    rig : StringProperty()
    lr : StringProperty()
    propname : StringProperty()
    value : FloatProperty()
    def execute(self, context):
        cmd.modify_rig_control_panel( self.rig , self.lr , self.propname , self.value )
        return {'FINISHED'}

class CYARIGTOOLS_OT_modify_rig_control_panel_key(bpy.types.Operator):
    """keying rig custom property"""
    bl_idname = "cyarigtools.modify_rig_control_panel_key"
    bl_label = ""
    rig : StringProperty()
    lr : StringProperty()
    propname : StringProperty()
    def execute(self, context):
        cmd.modify_rig_control_panel_key( self.rig , self.lr , self.propname)
        return {'FINISHED'}

#pose tool : matrix copy paste
class CYARIGTOOLS_OT_posetool_copy_matrix(bpy.types.Operator):
    """keying rig custom property"""
    bl_idname = "cyarigtools.posetool_copy_matrix"
    bl_label = "copy"
    def execute(self, context):
        cmd.copy_matrix()
        return {'FINISHED'}

class CYARIGTOOLS_OT_posetool_paste_matrix(bpy.types.Operator):
    """keying rig custom property"""
    bl_idname = "cyarigtools.posetool_paste_matrix"
    bl_label = "paste"
    def execute(self, context):
        cmd.paste_matrix()
        return {'FINISHED'}


#---------------------------------------------------------------------------------------
# constraint tool
#---------------------------------------------------------------------------------------
class CYARIGTOOLS_OT_edit_constraint_cleanup(bpy.types.Operator):
    """選択された複数ボーンのコンストレインをすべて削除する"""
    bl_idname = "cyarigtools.edit_constraint_cleanup"
    bl_label = "all"
    def execute(self, context):
        edit.constraint_cleanup()
        return {'FINISHED'}

class CYARIGTOOLS_OT_edit_constraint_cleanup_empty(bpy.types.Operator):
    """選択された複数ボーンの空のコンストレインを削除する"""
    bl_idname = "cyarigtools.edit_constraint_empty_cleanup"
    bl_label = "empty"
    def execute(self, context):
        edit.constraint_cleanup_empty()
        return {'FINISHED'}

#---------------------------------------------------------------------------------------
# arp tools
#---------------------------------------------------------------------------------------
class CYARIGTOOLS_OT_arp_connect(bpy.types.Operator):
    """名前リストにしたがってボーンをコンストレインで接続"""
    bl_idname = "cyarigtools.arp_connect"
    bl_label = "connect"
    def execute(self, context):
        arp.connect()
        return {'FINISHED'}


class CYARIGTOOLS_OT_arp_extracter(bpy.types.Operator):
    """キャラのボーンを複製する"""
    bl_idname = "cyarigtools.arp_extracter"
    bl_label = "extract"
    def execute(self, context):
        arp.extracter()
        return {'FINISHED'}

class CYARIGTOOLS_OT_arp_const(bpy.types.Operator):
    """ARPリグでボーンをコンストレインする。
    ue4もしくはmixamoのリグを選択し,次にARPの順に選択して実行。"""
    bl_idname = "cyarigtools.arp_const"
    bl_label = ""
    rig : StringProperty()

    def execute(self, context):
        arp.const(self.rig)
        return {'FINISHED'}

class CYARIGTOOLS_OT_adjust_arp(bpy.types.Operator):
    """UE4,MIXAMOのボーン位置にARPリファレンスボーンを合わせる
    UE4,またはMIXAMOのアーマチュアを選択し、最後にARPリファレンスボーンを選択して実行する"""
    bl_idname = "cyarigtools.adjust_arp"
    bl_label = ""
    mode : StringProperty()
    def execute(self, context):
        arp.adjust_arp(self.mode)
        return {'FINISHED'}

class CYARIGTOOLS_OT_arp_disable_ikstretch(bpy.types.Operator):
    """選択したアーマチュアのすべてのik stretchを無効化します。"""
    bl_idname = "cyarigtools.arp_disable_ikstretch"
    bl_label = "disable ikstretch"
    def execute(self, context):
        arp.disable_ikstretch()
        return {'FINISHED'}

#---------------------------------------------------------------------------------------
#Add bone
#---------------------------------------------------------------------------------------

# Add bone at the selected objects
class CYARIGTOOLS_OT_locator_add_bone(Operator):
    """選択したモデルの位置にボーンを生成
複数のモデルを選択後、アーマチュアをアクティブにして実行"""
    bl_idname = "cyarigtools.locator_add_bone"
    bl_label = "add bone at obj"
    def execute(self, context):
        edit.add_bone()
        return {'FINISHED'}

class CYARIGTOOLS_OT_locator_snap_bone_at_obj(Operator):
    """オブジェクトの位置にボーンをスナップ
モデルを選択後、アーマチュアを選択しエディットモードに入る
ボーンを選択して実行するとオブジェクトの位置にボーンが吸着する"""
    bl_idname = "cyarigtools.locator_snap_bone_at_obj"
    bl_label = "snap bone"
    def execute(self, context):
        edit.snap_bone_at_obj()
        return {'FINISHED'}


#---------------------------------------------------------------------------------------
# other tools
#---------------------------------------------------------------------------------------
class CYARIGTOOLS_OT_edit_connect_chain(bpy.types.Operator):
    """First,select some bones, then execute this command."""
    bl_idname = "cyarigtools.edit_connect_chain"
    bl_label = "connect chain"
    def execute(self, context):
        edit.connect_chain()
        return {'FINISHED'}

class CYARIGTOOLS_OT_edit_delete_rig(bpy.types.Operator):
    """Delete automaticaly root_rig and it's children ."""
    bl_idname = "cyarigtools.edit_delete_rig"
    bl_label = "delete rig"
    def execute(self, context):
        edit.delete_rig()
        return {'FINISHED'}


classes = (
    CYARIGTOOLS_Props_OA,
    CYARIGTOOLS_PT_ui,
    #CYARIGTOOLS_MT_addonpreferences,

    CYARIGTOOLS_MT_rigsetuptools,
    CYARIGTOOLS_MT_edittools,
    CYARIGTOOLS_MT_rigcontrolpanel,

    #RigShape-Related
    CYARIGTOOLS_PT_rigshape_selector,
    CYARIGTOOLS_OT_rigshape_revert,
    CYARIGTOOLS_OT_rigshape_append,
    CYARIGTOOLS_OT_make_the_same_size,
    
    #setup ik rig
    CYARIGTOOLS_OT_setupik_ik,
    CYARIGTOOLS_OT_setupik_polevector,
    CYARIGTOOLS_OT_setupik_spline_ik,
    CYARIGTOOLS_OT_setupik_hook,

    CYARIGTOOLS_OT_setupik_rig_arm,
    CYARIGTOOLS_OT_setupik_rig_leg,
    CYARIGTOOLS_OT_setupik_rig_spine,
    CYARIGTOOLS_OT_setupik_rig_spine_v2,
    CYARIGTOOLS_OT_setupik_rig_spine_v3,
    CYARIGTOOLS_OT_setupik_rig_neck,
    CYARIGTOOLS_OT_setupik_rig_neck_v2,
    CYARIGTOOLS_OT_setupik_setup_rig_chain,
    CYARIGTOOLS_OT_setupik_rig_finger,

    CYARIGTOOLS_OT_setupik_ue,
    CYARIGTOOLS_OT_setupik_customrig,

    #edit
    CYARIGTOOLS_OT_edit_length_uniform,
    CYARIGTOOLS_OT_edit_length_half,
    CYARIGTOOLS_OT_edit_genarate_bone_from2,
    CYARIGTOOLS_OT_edit_genarate_symmetry,

    CYARIGTOOLS_OT_edit_align_position,
    CYARIGTOOLS_OT_edit_align_direction,
    CYARIGTOOLS_OT_edit_align_along,
    CYARIGTOOLS_OT_edit_aling_near_axis,
    CYARIGTOOLS_OT_edit_align_2axis_plane,
    CYARIGTOOLS_OT_edit_align_on_plane,
    CYARIGTOOLS_OT_edit_align_at_flontview,
    CYARIGTOOLS_OT_edit_adjust_roll,
    CYARIGTOOLS_OT_edit_roll_degree,
    CYARIGTOOLS_OT_edit_align_roll_global,
    CYARIGTOOLS_OT_edit_axis_swap,
    CYARIGTOOLS_OT_locator_add_bone,
    CYARIGTOOLS_OT_locator_snap_bone_at_obj,


    #other tools
    CYARIGTOOLS_OT_edit_connect_chain,
    CYARIGTOOLS_OT_edit_delete_rig,

    #constraint
    CYARIGTOOLS_OT_edit_constraint_cleanup,
    CYARIGTOOLS_OT_edit_constraint_cleanup_empty,

    #rig control panel
    CYARIGTOOLS_OT_rigctr_arm,
    CYARIGTOOLS_OT_modify_rig_control_panel,
    CYARIGTOOLS_OT_modify_rig_control_panel_key,
    CYARIGTOOLS_OT_posetool_copy_matrix,
    CYARIGTOOLS_OT_posetool_paste_matrix,

    #ARP Tools
    CYARIGTOOLS_MT_arptools,
    CYARIGTOOLS_OT_arp_connect,
    CYARIGTOOLS_OT_arp_extracter,
    CYARIGTOOLS_OT_arp_const,
    CYARIGTOOLS_OT_adjust_arp,
    CYARIGTOOLS_OT_arp_disable_ikstretch
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.cyarigtools_props = PointerProperty(type=CYARIGTOOLS_Props_OA)
    bpy.app.handlers.depsgraph_update_post.append(cyarigtools_handler)

    renamer.register()
    duplicator.register()
    constraint.register()


def unregister():
    
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.cyarigtools_props
    bpy.app.handlers.depsgraph_update_post.remove(cyarigtools_handler)

    renamer.unregister()
    duplicator.unregister()
    constraint.unregister()
