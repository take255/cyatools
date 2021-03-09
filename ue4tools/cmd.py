import bpy
import imp
import re

from .. import utils
imp.reload(utils)


def unitscale(value):
    bpy.context.scene.unit_settings.scale_length = value


# def adjust_arp(mode):
#     pass


# def export_anim():
#     fullpath = bpy.data.filepath
#     buf = fullpath.split('\\')
#     animname = buf[-1].split('.')[0]
    

#     export_cmd('anim',animname)


def export(mode):
    props = bpy.context.scene.cyaue4tools_props 
    name = ''

    act = utils.getActiveObj()
    currentMode = utils.current_mode()

    if mode == 'anim':
        #リンクされたファイル名からキャラ名を抜き出す
        #アニメションシーンなら　CH_Mmob01.blend , RIG_Mmob01.blend　の２つのファイルを取得できるはず
        #プレフィックスと.blendを削除したものをキャラ名とする
        lib = bpy.data.libraries
        if len(lib) == 0:
            msg = 'シーンにキャラクターがリンクされていません'
            bpy.ops.cyatools.messagebox('INVOKE_DEFAULT', message = msg)            
            return
        else:
            buf =  re.split('[_.]',lib[0].name)
            charname = buf[1]



        utils.mode_o()
        utils.deselectAll()
        #コレクション00_Model~に含まれているモデルを対象にする
        #コレクション名：00_Anim_male01_run01　＞　ファイル名：an_male01_run01.fbx
        for c in bpy.data.collections:
            #print(c.name,c.name.find('00_Model'))
            if c.name.find('00_Anim_') != -1:
                name = 'AN_%s_%s' % (charname , c.name.replace('00_Anim_',''))
                for ob in bpy.context.scene.objects: 
                    cols = [x.name for x in ob.users_collection]
                    print(ob.name,cols,c in cols)
                    if c.name in cols: 
                        utils.select(ob,True)
                        utils.activeObj(ob)

                export_core( mode , name )

        utils.act(act)
        utils.mode(currentMode)


    elif mode == 'model':
        #コレクション00_Model~に含まれているモデルを対象にする
        for c in bpy.data.collections:
            print(c.name,c.name.find('00_Model'))
            if c.name.find('00_Model_') != -1:
                utils.deselectAll()
                name = c.name.replace('00_Model_','CH_')
                for ob in bpy.context.scene.objects: 
                    cols = [x.name for x in ob.users_collection]
                    print(ob.name,cols,c in cols)
                    if c.name in cols: 
                        utils.select(ob,True)
                        utils.activeObj(ob)

                export_core( mode , name )

def export_core( mode , name ):
    props = bpy.context.scene.cyaue4tools_props 

    outpath = '%s\%s.fbx' % ( props.filepath , name )
    print(outpath)

    #スケールを0.01に強制
    unitscale = bpy.context.scene.unit_settings.scale_length
    bpy.context.scene.unit_settings.scale_length = 0.01

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
            add_leaf_bones = False,

            #bake animation
            bake_anim = True,
            bake_anim_use_all_bones = True,
            bake_anim_use_nla_strips = False,
            bake_anim_use_all_actions = False,
            bake_anim_force_startend_keying = True,
            #bake_anim_step = 0.1
            bake_anim_simplify_factor = 0.0
            )

    if mode == 'model':
        scale = 1.0
        axis_forward = '-Z'
        axis_up = 'Y'
        object_types = {'MESH','ARMATURE'} 

        bpy.ops.export_scene.fbx(
            filepath=outpath ,
            use_selection = True ,
            global_scale = scale ,
            axis_forward = axis_forward ,
            axis_up = axis_up,
            object_types = object_types,

            primary_bone_axis = 'Y',
            secondary_bone_axis = 'X',
            add_leaf_bones = False,

            #bake animation
            bake_anim = False,
            bake_anim_use_all_bones = True,
            bake_anim_use_nla_strips = False,
            bake_anim_use_all_actions = False,
            bake_anim_force_startend_keying = True
            )

    #ユニットスケールをもとに戻す
    bpy.context.scene.unit_settings.scale_length = unitscale


    msg = '出力完了しました ' + outpath
    bpy.ops.cyatools.messagebox('INVOKE_DEFAULT', message = msg)            

