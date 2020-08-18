import bpy
import imp

from .. import utils
imp.reload(utils)


def unitscale(value):
    bpy.context.scene.unit_settings.scale_length = value


# def adjust_arp(mode):
#     pass


def export_anim():
    fullpath = bpy.data.filepath
    buf = fullpath.split('\\')
    animname = buf[-1].split('.')[0]
    

    export_cmd('anim',animname)


def export_cmd(mode,name):
    props = bpy.context.scene.cyaue4tools_props 
    outpath = '%s\%s.fbx' % ( props.filepath , name )
    print(outpath)

    # forward = props.axis_forward
    # up = props.axis_up

    if mode == 'anim':
        scale = 1.0
        axis_forward = '-Z'
        axis_up = 'Y'
        object_types = {'ARMATURE',} 

        bpy.ops.export_scene.fbx(
            filepath=outpath ,
            use_selection = True ,
            global_scale = scale ,
            axis_forward = axis_forward ,
            axis_up = axis_up,
            object_types = object_types,

            primary_bone_axis = 'Y',
            secondary_bone_axis = 'X',

            #bake animation
            bake_anim = True,
            bake_anim_use_all_bones = True,
            bake_anim_use_nla_strips = False,
            bake_anim_use_all_actions = False,
            bake_anim_force_startend_keying = True
            )


    # elif props.export_mode == 'ue':
    #     print(outpath)
    #     if mode == 'fbx':
    #         bpy.ops.export_scene.fbx(
    #             filepath=outpath ,
    #             use_selection = True ,
    #             global_scale = props.scale ,
    #             axis_forward = props.axis_forward ,
    #             axis_up = props.axis_up,
    #             mesh_smooth_type = 'FACE',#Added for UE
    #             add_leaf_bones  = False , #Added for UE
    #             use_armature_deform_only  = True #Added for UE
    #             )

    #     elif mode == 'obj':
    #         bpy.ops.export_scene.obj(
    #             filepath=outpath ,
    #             use_selection = True ,
    #             global_scale = props.scale ,
    #             axis_forward = props.axis_forward ,
    #             axis_up = props.axis_up
    #             )


    # if mode == 'fbx':
    #     bpy.ops.export_scene.fbx(filepath=outpath ,global_scale = props.scale , bake_anim_step=2.0 , bake_anim_simplify_factor=0.0 , use_selection = True)
        