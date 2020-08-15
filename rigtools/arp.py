

import bpy
import imp
# import math
from mathutils import ( Vector , Matrix )

from .. import utils
from . import arpbone
from . import constraint

imp.reload(utils)
imp.reload(arpbone)
imp.reload(constraint)


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

# def const_ue4():
#     const(arpbone.ue4,'pelvis')


# def const_mixamo():
#     const(arpbone.mixamo,'mixamorig:Hips')
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
