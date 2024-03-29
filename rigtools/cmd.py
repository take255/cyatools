import numpy as np
import bpy
from bpy.props import FloatProperty

from mathutils import Vector
from mathutils import Matrix
import pickle
import imp

from .. import utils
imp.reload(utils)

#RIGSHAPEPATH = "E:\data\googledrive\lib\model/rig.blend"

#---------------------------------------------------------------------------------------
#リグシェイプ
#---------------------------------------------------------------------------------------
def rigshape_change_scale(self,context):
    props = bpy.context.scene.cyarigtools_props

    utils.mode_p()
    for bone in utils.get_selected_bones():
        bone.custom_shape_scale = props.rigshape_scale/bone.length

def rigshape_revert():
    utils.mode_p()
    #bpy.ops.object.mode_set(mode = 'POSE')
    for bone in utils.get_selected_bones():
        bone.custom_shape = None


def rigshape_append():
    current_scene_name = bpy.context.scene.name
    filepath = bpy.utils.user_resource('SCRIPTS','addons') + '/cyatools/rigtools/rig.blend'
    #RigShape_Scn 無ければ作成する
    scene = 'RigShape_Scn'
    if bpy.data.scenes.get(scene) is None:
        bpy.ops.scene.new(type='EMPTY')
        bpy.context.scene.name = scene

    utils.sceneActive(scene)

    #append object from .blend file
    with bpy.data.libraries.load(filepath) as (data_from, data_to):
        data_to.objects = data_from.objects

    #link object to current scene
    for obj in data_to.objects:
        print(obj.name)
        if obj is not None:
            utils.sceneLink(obj)

    utils.sceneActive(current_scene_name)

# make rig shepe size the same. It makes active bone  basis.
def make_the_same_size():
    selected = utils.bone.get_selected_bones()
    act = utils.bone.get_active_bone()

    basesize = act.length * act.custom_shape_scale
    for b in selected:
        b.custom_shape_scale = basesize/b.length
        #print(b.length)


#---------------------------------------------------------------------------------------
#Change rig control value
#---------------------------------------------------------------------------------------
RIGARRAY = ('arm','leg')
PROPARRAY = {
    # 'arm': ('ikfk','stretch'),
    # 'leg': ('ikfk','stretch')
    'arm': ('ikfk','clav','hand','stretch'),
    'leg': ('ikfk','foot','stretch')

}

def rig_change_ctr(self,context):
    amt = bpy.context.object
    props = bpy.context.scene.cyarigtools_props

    for r in RIGARRAY:
        for p in PROPARRAY[r]:
            for lr in ('l' , 'r'):

                ctr = 'ctr.%s.%s' % ( r , lr )

                #if ctr in [o.name for o in bpy.data.objects]:
                if ctr in [b.name for b in amt.pose.bones]:
                    prop ='%s.%s' % (p,lr)
                    prop_val = '%s_%s_%s' % (r,p,lr)
                    #print(ctr , prop , prop_val)
                    exec('amt.pose.bones[\'%s\'][\'%s\'] = props.%s' % ( ctr , prop , prop_val ) ) #amt.pose.bones[ctr.arm.l]['ikfk.l'] = props.arm_ikfk_l'
                    exec('amt.pose.bones[\'%s\'].matrix = amt.pose.bones[\'%s\'].matrix' % (ctr,ctr))  # There is a need to update matrix.

    bpy.context.view_layer.update()


def modify_rig_control_panel( rig , lr , propname , value ):
    amt = bpy.context.object
    props = bpy.context.scene.cyarigtools_props

    ctr = 'ctr.%s.%s' % ( rig , lr )

    if ctr in [b.name for b in amt.pose.bones]:
        prop = '%s.%s' % ( propname , lr )
        prop_val = '%s_%s_%s' % ( rig , propname , lr )
        print( ctr , prop , prop_val )
        exec('props.%s = %f' % ( prop_val ,value ) ) #amt.pose.bones[ctr.arm.l]['ikfk.l'] = props.arm_ikfk_l'
        exec('amt.pose.bones[\'%s\'][\'%s\'] = %f ' % ( ctr , prop , value ) ) #amt.pose.bones[ctr.arm.l]['ikfk.l'] = props.arm_ikfk_l'


def modify_rig_control_panel_key( rig , lr , propname ):
    amt = bpy.context.object
    #props = bpy.context.scene.cyarigtools_props

    ctr = 'ctr.%s.%s' % ( rig , lr )
    prop = '%s.%s' % ( propname , lr )

    bone = amt.pose.bones[ ctr ]
    bone.keyframe_insert(data_path='["%s"]' % prop)

    bpy.context.view_layer.update()

#---------------------------------------------------------------------------------------
#matrix copy paste
#---------------------------------------------------------------------------------------
BONE_MATRIX = []
BONE_MATRIX_DIC = {}

def copy_matrix():
    amt = bpy.context.object
    global BONE_MATRIX_DIC
    BONE_MATRIX_DIC.clear()
    utils.mode_p()

    for bone in utils.get_selected_bones():
        BONE_MATRIX_DIC[bone.name] = Matrix(bone.matrix)
        #m = Matrix(bone.matrix)
        #pos =(m[0][3] , m[1][3] , m[2][3]  )
        #bonematrixarray[bone.name] = [Matrix(bone.matrix) , pos]


def paste_matrix():
    for bone in bpy.context.selected_pose_bones:
        bone.matrix = BONE_MATRIX_DIC[bone.name]

    # for b in BONE_MATRIX_DIC:
    #     print(b)


#---------------------------------------------------------------------------------------
#matrix copy pose
#ルート階層から順に適用していく必要がある
#階層でソートするには
#---------------------------------------------------------------------------------------

def pose_copy_pasete(mode):

    amt = bpy.context.object
    global BONE_MATRIX_DIC

    utils.mode_p()

    if mode == "copy":
        BONE_MATRIX_DIC.clear()

        for bone in utils.get_selected_bones():
            BONE_MATRIX_DIC[bone.name] = Matrix(bone.matrix)
            #m = Matrix(bone.matrix)
            #pos =(m[0][3] , m[1][3] , m[2][3]  )
            #bonematrixarray[bone.name] = [Matrix(bone.matrix) , pos]



    else:
        array = []
        for bone in bpy.context.selected_pose_bones:

            num = get_parent_loop( bone , 0 )
            print(bone.name,num)

            array.append([num,bone.name])
            #bone.matrix = BONE_MATRIX_DIC[bone.name]

        array.sort()

        for a in array:
            bone = amt.pose.bones[a[1]]
            print(bone.name, a , bone.name in BONE_MATRIX_DIC)

            if bone.name in BONE_MATRIX_DIC:
                bone.matrix = BONE_MATRIX_DIC[bone.name]
    # for b in BONE_MATRIX_DIC:
    #     print(b)

def get_parent_loop(bone,num):
    p = bone.parent
    num += 1
    if p != None:
        num = get_parent_loop( p , num )

    return num