import bpy
import imp
from mathutils import ( Vector , Matrix )

from . import utils

imp.reload(utils)


#モデルと骨を選択して実行
#骨はポーズモードに入って各プロポーションを修正する
def assign():
    props = bpy.context.scene.cyarigtools_props  
    root = props.root_scale
    spine = props.spine_scale
    clavicle = props.clavicle_scale
    hand = props.hand_scale


    for ob in utils.selected():
        
        ob.scale = Vector((root,root,root))
        if ob.type == 'ARMATURE':
            amt = ob

    utils.act(amt)
    utils.mode_p()
    

    amt.pose.bones['spine_01'].scale = Vector((spine,spine,spine))
    amt.pose.bones['clavicle_l'].scale = Vector((clavicle,clavicle,clavicle))
    amt.pose.bones['clavicle_r'].scale = Vector((clavicle,clavicle,clavicle))
    amt.pose.bones['hand_l'].scale = Vector((hand,hand,hand))
    amt.pose.bones['hand_r'].scale = Vector((hand,hand,hand))

    utils.mode_o()

    
#トランスフォーム、骨のポーズ、アーマチュアモディファイヤのアプライ
#バインドしなおすを追加したい
def apply():
    utils.mode_o()

    for ob in utils.selected():
        utils.act(ob)
        bpy.ops.object.transform_apply( location = True , rotation=True , scale=True )

        if ob.type == 'ARMATURE':
            amt = ob
        else:
            for mod in ob.modifiers:
                if mod.type == 'ARMATURE':
                    bpy.ops.object.modifier_apply(modifier=mod.name)


    utils.act(amt)
    utils.mode_p()
    bpy.ops.pose.armature_apply(selected=False)

    utils.mode_o()
    #ここ以降バインドしなおすを追加する



def get():
    props = bpy.context.scene.cyarigtools_props  
    utils.mode_o()
    amt = False
    for ob in utils.selected():
        utils.act(ob)
        if ob.type == 'ARMATURE':
            amt = ob

    if not amt:
        return

    utils.act(amt)
    props.root_scale = amt.scale.x

    utils.mode_p()
    props.spine_scale = amt.pose.bones['spine_01'].scale.x
    props.clavicle_scale = amt.pose.bones['clavicle_l'].scale.x
    props.hand_scale = amt.pose.bones['hand_l'].scale.x
    utils.mode_o()



