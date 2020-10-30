

import bpy
import imp
# import math
from mathutils import ( Vector , Matrix )

from .. import utils
from . import arpbone
from . import constraint
from . import setup_ik

imp.reload(utils)
imp.reload(arpbone)
imp.reload(constraint)
imp.reload(setup_ik)


bconv={
'pelvis':'spine',
'spine_01':'spine.001',
'spine_02':'spine.002',
'spine_03':'spine.003',

'spine_03':'spine.004',
'spine_03':'spine.003',

'thigh_l':'thigh.L',
'thigh_r':'thigh.R',
'calf_l':'shin.L',
'calf_r':'shin.R',
'foot_l':'foot.L',
'foot_r':'foot.R',
'ball_l':'toe.L',
'ball_r':'toe.R',
}

#先端のボーン。向きをＸ軸方向に合わせる
tip =[
'toe.L',
'toe.R',
]


def move_layer(bone_name,number,amt):
    #まずは移動先をアクティブにする
    amt.data.layers[number] = True

    #レイヤをすべてアクティブではない状態にする
    for i in range(32):
        bpy.context.object.data.layers[number] = False
        bpy.context.object.data.bones[bone_name].layers[i] = False    

    bpy.context.object.data.bones[bone_name].layers[number] = True

#---------------------------------------------------------------------
#ARPとMixamoをコンストレインする
#Mixamo,ARPの順で選択する
#---------------------------------------------------------------------
def const(rig):

    if rig == 'ue4':
        bonedic =  arpbone.ue4
        root = 'pelvis'
    if rig == 'mixamo':
        bonedic =  arpbone.mixamo
        root = 'mixamorig:Hips'


    selected = utils.selected()
    arp = utils.getActiveObj()
    selected.remove(arp)
    tgt = selected[0]

    #ボーン軸向きがおかしくなるのでミラーをオフにしておく
    bpy.context.object.data.use_mirror_x = False

    
    #tgtをアクティブにしてボーンを取得
    #ボーンの位置を取得する

    utils.act(tgt)
    utils.mode_p()
    bonelist = []

    d_swap = {v: k for k, v in bonedic.items()}

    #コンストレインを全削除
    for bone in tgt.pose.bones:
        for const in bone.constraints:
            bone.constraints.remove( const )

    allbonename = [b.name for b in tgt.pose.bones]
    for bname in bonedic.values():
        if bname in allbonename:
            b = tgt.pose.bones[bname]
            p = d_swap[bname]
            m = Matrix(b.matrix)
            head = Vector(b.head)
            tail = Vector(b.tail)
            # roll = b.roll
            bonelist.append([b.name,m,head,tail,p])


    # for b in bonelist:
    #     print(b)
    #arpの骨にtgtの骨を追加
    utils.mode_o()
    utils.act(arp)
    utils.mode_e()
    
    
    bpy.context.object.data.layers[30] = True
    
    #ボーンが存在していたら削除
    bpy.ops.armature.select_all(action='DESELECT')
    constbones = [x.name for x in arp.data.edit_bones]
    for l in bonelist:
        if l[0] in constbones:
            arp.data.edit_bones[l[0]].select = True
            #b.select = True
    
    bpy.ops.armature.delete()


    #ボーン生成
    for l in bonelist:
        b = arp.data.edit_bones.new(l[0])
        
        b.head = l[2]
        b.tail = l[3]
        b.matrix = l[1]

        b.parent = arp.data.edit_bones[l[4]]

        #print(l)


    #コンストレイン
    utils.mode_o()
    utils.act(tgt)
    utils.mode_p()
    for bname in bonedic.values():
        constraint.do_const_2amt(tgt,arp,'COPY_ROTATION',bname,bname,'WORLD',(True,True,True) , (False,False,False))

    #Hipsだけトランスもコンストレイン
    #bname = 'mixamorig:Hips'
    constraint.do_const_2amt(tgt,arp,'COPY_LOCATION',root,root,'WORLD',(True,True,True) , (False,False,False))

    #レイヤ３０に移動
    utils.mode_o()
    utils.act(arp)
    utils.mode_p()
    
    for l in bonedic.values():
        setup_ik.move_layer(l,30)


def const_(rig):
    if rig == 'ue4':
        bonedic =  arpbone.ue4
        root = 'pelvis'
    if rig == 'mixamo':
        bonedic =  arpbone.mixamo
        root = 'mixamorig:Hips'


    selected = utils.selected()
    arp = utils.getActiveObj()
    selected.remove(arp)
    tgt = selected[0]


    print(arp)
    print(tgt)
    
    #tgtをアクティブにしてボーンを取得
    #ボーンの位置を取得する

    utils.act(tgt)
    utils.mode_e()
    bonelist = []

    d_swap = {v: k for k, v in bonedic.items()}

    allbonename = [b.name for b in tgt.data.edit_bones]
    for bname in bonedic.values():
        if bname in allbonename:
            b = tgt.data.edit_bones[bname]
            p = d_swap[bname]
            head = Vector(b.head)
            tail = Vector(b.tail)
            roll = b.roll
            bonelist.append([b.name,head,tail,roll,p])

    #arpの骨にtgtの骨を追加
    utils.mode_o()
    utils.act(arp)
    utils.mode_e()

    
    bpy.context.object.data.layers[30] = True
    for l in bonelist:
        b = arp.data.edit_bones.new(l[0])
        b.head = l[1]
        b.tail = l[2]
        b.roll = l[3]

        b.parent = arp.data.edit_bones[l[4]]

        print(l)

    #コンストレイン
    utils.mode_o()
    utils.act(tgt)
    utils.mode_p()
    for bname in bonedic.values():
        constraint.do_const_2amt(tgt,arp,'COPY_ROTATION',bname,bname,'WORLD',(True,True,True) , (False,False,False))

    #Hipsだけトランスもコンストレイン
    #bname = 'mixamorig:Hips'
    constraint.do_const_2amt(tgt,arp,'COPY_LOCATION',root,root,'WORLD',(True,True,True) , (False,False,False))

    #レイヤ３０に移動
    utils.mode_o()
    utils.act(arp)
    utils.mode_p()
    
    for l in bonedic.values():
        setup_ik.move_layer(l,30)


#実装されてない
def extracter():
    print(arpbone.bonedic)


#メタリグをアクティブにして選択
def fit_metarig():
    metarig = utils.getActiveObj()#
    print(metarig.name)

    selected = utils.selected()
    utils.deselectAll()

    for r in selected:
        if r != metarig:
            utils.mode_o()
            utils.act(r)

            print(r.name)
            utils.mode_e()

            m_array = {}
            for bone in r.data.edit_bones:
                matrix = bone.matrix
                if bone.name in bconv:

                    # matrix = bone.matrix
                    # #matrix = bone.matrix.to_3x3()
                    # matrix.transpose()

                    # x =  -matrix[2]
                    # y =  matrix[0]
                    # z = -matrix[1]


                    head = Vector(bone.head)
                    # m = Matrix((x,y,z,matrix[3]))
                    # m.transpose()
                    # #matrix = m.to_4x4()

                    m_array[ bconv[bone.name] ] = head
                    print(bone.name,bone.matrix )
    

            utils.mode_o()
            utils.act(metarig)
            utils.mode_e()

            for bone in metarig.data.edit_bones:
                if bone.name in m_array:
                    print('>>',bone.name)
                    bone.head = m_array[bone.name]
                    #bone.head = m_array[bone.name][0]
                    #print(bone.name,bone.matrix )

def check_transform():
    loc = bpy.context.object.location
    
#---------------------------------------------------------------------
# UE4,MIXAMOのボーン位置にARPリファレンスボーンを合わせる
# UE4,またはMIXAMOのアーマチュアを選択し、最後にARPリファレンスボーンを選択して実行する
#リグがアプライされていなければ注意を出す
#---------------------------------------------------------------------
def adjust_arp(mode):
    if mode == 'ue4':
        bonedic =  arpbone.ue4_ref
        root = 'pelvis'
    if mode == 'mixamo':
        bonedic =  arpbone.mixamo_
        root = 'mixamorig:Hips'

    #ARPリグのトランスフォームフリーズ
    #act = utils.getActiveObj()
    #bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    init_matrix = Matrix()
    selected = utils.selected()
    #notFreezed = False

    #フリーズされていなければ処理を中断
    for ob in selected:
        if ob.matrix_world != init_matrix:
            msg = 'トランスフォームがフリーズされていません。'
            bpy.ops.cyatools.messagebox('INVOKE_DEFAULT', message = msg)
            return

    arp = utils.getActiveObj()
    arp.data.use_mirror_x = False #角度がおかしくなるのでミラーオプションを切る。多分 r>lの順に処理すれば切らなくても大丈夫

    selected.remove(arp)
    tgt = selected[0]

    print(arp)
    print(tgt)
    
    #tgtをアクティブにしてボーンを取得
    #ボーンの位置を取得する
    #ターゲットのトランスフォームフリーズ
    utils.act(tgt)
    #bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    utils.mode_p()
    bonelist = []

    #d_swap = {v: k for k, v in bonedic.items()}

    #コンストレインを全削除
    for bone in tgt.pose.bones:
        for const in bone.constraints:
            bone.constraints.remove( const )

    allbonename = [b.name for b in tgt.pose.bones]
    for bname in bonedic:
        print(bname,bname in allbonename)
        if bname in allbonename:
            b = tgt.pose.bones[bname]

            # buf = bonedic[bname].split('.')
            # name = '%s_ref.%s' % (buf[0],buf[1])
            name = bonedic[bname]

            head = Vector(b.head)
            tail = Vector(b.tail)
            #roll =b.roll
            m = Matrix(b.matrix)

            bonelist.append( [ name , head , tail , m ] )

    #arpの骨にtgtの骨を追加
    utils.mode_o()
    utils.act(arp)
    utils.mode_e()

    
    for l in bonelist:
        if l[0] in arp.data.edit_bones:
            b = arp.data.edit_bones[l[0]]
            b.head = l[1]
            b.tail = l[2]
            b.matrix = l[3]

            print(l)


    msg = '処理完了'
    bpy.ops.cyatools.messagebox('INVOKE_DEFAULT', message = msg)


def disable_ikstretch():
    amt = utils.getActiveObj()
    utils.mode_p()
    for b in amt.pose.bones:
        for const in b.constraints:
            if const.type == 'IK':
                const.use_stretch = False



    msg = '処理完了 すべてのikStretchを無効化しました'
    bpy.ops.cyatools.messagebox('INVOKE_DEFAULT', message = msg)
