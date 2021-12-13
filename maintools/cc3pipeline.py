import bpy
import bmesh

import imp
import os
from pathlib import Path
import pickle


#from mathutils import ( Matrix)

from . import utils
from ..rigtools import edit
from . import skinning


imp.reload(utils)


#新規マテリアルを作成して、そこにイメージを集める
#シェーダーノード一覧
#https://docs.blender.org/api/blender2.8/bpy.types.html
def collect_textures():

    for ob in utils.selected():

        image_array = []

        for mat in ob.data.materials:
            print('------------------------------------')
            print(mat.name)
            nodes = mat.node_tree.nodes
            for node in nodes:
                #Node = nodes.get("Image Texture")
                if node.type == 'TEX_IMAGE':
                    img = node.image


                    for d in dir(img):
                        print(d)

                    image_array.append(img)


        newmat = bpy.data.materials.new(name='ImageCollected' )


        newmat.use_nodes = True
        nodes = newmat.node_tree.nodes
        mat_links = newmat.node_tree.links
        # a new material node tree already has a diffuse and material output node
        # output = mat_nodes['Material Output']
        # diffuse = mat_nodes['Diffuse BSDF']

        #nodes = newmat.node_tree.nodes
        #nodes.new(type='ShaderNodeOutputMaterial')
        for i,img in enumerate(image_array):
            tex = nodes.new(type='ShaderNodeTexImage')
            tex.image = img
            img.colorspace_settings.name = 'sRGB' #カラースペースをsRGBに強制
            tex.location.x = 100*i
            tex.location.y = 800

        # newmat
        # nodes.new(type='ShaderNodeOutputMaterial')
            # Node = nodes.get("Principled BSDF")
            # color = Node.inputs["Base Color"].default_value[:]
            # print(color)



#選択したイメージテクスチャノードの画像を保存
def save_textures(exportdir):
    path = Path( exportdir )

    mat = bpy.context.active_object.active_material

    nodes = mat.node_tree.nodes
    for node in nodes:
        if node.select:
            nodes.active = node
            if node.type == 'TEX_IMAGE':

                img = node.image
                new_path = str( Path(path) / Path(img.name) )
                root, ext = os.path.splitext(new_path)

                if ext.lower() != '.png':
                    new_path += '.png'

                img.filepath_raw = new_path
                img.file_format = 'PNG'
                img.save()


#選択したイメージテクスチャノードの画像を保存
#要素ごとにフォルダ分けする
def save_textures_():

    subpathes = ( 'Diffuse','Normal' )
    rootpath = Path("e:/tmp/b")

    target_dir = {}
    for path in subpathes:

        dst_dir = rootpath / Path(path)
        target_dir[path] = dst_dir
        os.makedirs(str(dst_dir), exist_ok=True )

    mat = bpy.context.active_object.active_material

    nodes = mat.node_tree.nodes
    for node in nodes:
        if node.select:
            if node.type == 'TEX_IMAGE':

                img = node.image

                for path in subpathes:
                    if img.name.find(path) != -1:

                        new_path = str( target_dir[path] / Path(img.name) )
                        root, ext = os.path.splitext(new_path)

                        if ext.lower() != '.png':
                            new_path += '.png'

                        img.filepath_raw = new_path
                        img.file_format = 'PNG'
                        img.save()


#選択したモデルのポリゴン数を見て分類する
PARTS = {
    14046:'CC_Base_Body',
    640:'CC_Base_Eye',
    296:'CC_Base_Tongue',
    2421:'CC_Base_Teeth',
}

def saveload_uv_quick(mode):

    path = Path(bpy.context.preferences.addons['cyatools'].preferences.lib_path)

    if  path.exists():
        for obj in utils.selected():

            utils.act(obj)
            polygons = obj.data.polygons

            uvfilepath =path /  Path(PARTS[len(polygons)])
            saveload_uv( mode , str(uvfilepath) )


def saveload_uv( mode , path ):

    if mode == 'save':
        obj = utils.getActiveObj()

        # msh = obj.data
        # vertices = obj.data.vertices
        polygons = obj.data.polygons

        #ポリゴンの情報
        polygonArray = []
        UVarray = []

        for face in polygons:
            polygonArray.append(face.vertices)

            #UVの情報
            uv_data = []
            for loop_idx in face.loop_indices:
                uv_coords = obj.data.uv_layers.active.data[loop_idx].uv
                uv_data.append([uv_coords.x,uv_coords.y])
            UVarray.append(uv_data)


        #拡張子はpklにする
        filename = Path(path)
        #if filename.suffix != 'pkl':
        new_filename= filename.with_suffix('.pkl')
        print(new_filename)
        f = open( new_filename, 'wb' )
        pickle.dump( UVarray, f ,protocol=0)
        f.close()



    elif mode == 'load':

        #filename = r'E:\tmp\b\uv.pkl'
        filename= Path(path).with_suffix('.pkl')
        f = open(  filename  ,'rb')
        uvdata = pickle.load( f )
        f.close()

        obj = utils.getActiveObj()
        polygons = obj.data.polygons

        #UVの生成

        for i,face in enumerate(polygons):
            for loop_idx,uv in zip(face.loop_indices,uvdata[i]):
                uv_coords = obj.data.uv_layers.active.data[loop_idx].uv
                uv_coords.x = uv[0]
                uv_coords.y = uv[1]


#CC3ボーンのリネーム　rigtools/edit
#ファイル　E:\data\OneDrive\projects\_lib\Blender\CC3_bonename_exchange.csv
def rename_bone():
    path = Path(bpy.context.preferences.addons['cyatools'].preferences.lib_path) / Path('CC3_bonename_exchange.csv')
    edit.rename_bone_with_csv(path)

#頂点グループ転送
def transfer_vtx_grp():
    path = Path(bpy.context.preferences.addons['cyatools'].preferences.lib_path) / Path('CC3_vtxgrp_transfer.csv')
    skinning.transfer_with_csvtable(path)


#バインドポーズを読み込む
def append_bindpose():
    amt = utils.getActiveObj()

    file_path = Path(r"E:\data\OneDrive\projects\_lib\Blender\cc3root.blend")
    inner_path =Path( 'Action')
    pose_name = Path('PoseLib')

    bpy.ops.wm.append(
        filepath = str( file_path /  inner_path / pose_name ),
        directory =  str( file_path /  inner_path ),
        filename= str( pose_name )
        )

    #ポーズの割り当て　最後に追加されたものをポーズに設定する
    utils.act(amt)
    amt.pose_library = bpy.data.actions[-1]
    #amt.pose_library.pose_markers.active_index = 0
    utils.mode_p()
    bpy.ops.poselib.apply_pose(pose_index = 0)
    utils.mode_o()