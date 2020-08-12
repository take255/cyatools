

import bpy
import imp
# import math
from mathutils import ( Vector , Matrix )

from .. import utils
from . import arpbone

imp.reload(utils)
imp.reload(arpbone)


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


def duplicator():
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
