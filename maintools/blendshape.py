#import numpy as np
import bpy
import bmesh
from mathutils import ( Vector , Matrix , Quaternion )
import math
import imp

from . import utils
imp.reload(utils)


#クオータニオンにを回転角ウェイトをかける
#クオータニオンを返す
def quat_weight(q , weight):
    axis_angle = q.to_axis_angle()
    axis = axis_angle[0]
    angle = axis_angle[1] * weight #角度を出しウェイトを掛ける
    return Quaternion(axis , angle)


class Bone:
    quatanion = Quaternion()
    parent_number = 0

    initmatrix = Matrix()
    matrix = Matrix()
    location = Vector()

    parent = ''

    def __init__(self , name):
        self.name = name

    #クオータニオンの回転をワールドに変換する
    def conv_quat_axis(self):
        axis_angle = self.quatanion.to_axis_angle()
        axis = axis_angle[0]
        angle = axis_angle[1]
        self.initmatrix
        axis_conv = self.initmatrix @ axis
        self.quatanion = Quaternion(axis_conv , angle)


class Vtx:
    """頂点出力のためのクラス"""

    co = ''
    #weight = []
    class Weight:
        """ウェイトの構造体"""
        value = 0
        name = ''


    def __init__(self):
        self.weight = []

    def getWeight(self,index,weight,boneArray):
        w = self.Weight()
        w.value = weight
        w.name =  boneArray[index]
        self.weight.append(w)


    def normalize_weight(self):
        sum = 0
        for w in self.weight:
            sum += w.value

        for w in self.weight:
            w.value = w.value/sum




  #親のクオータニオンにもウェイトを掛ける必要ある？
  #子供のほうから順にかけていかなければならない。結果がよくないのは親から順にかけられているから
    def calc_quat(self , val , BoneArray):
        #ウェイトをボーンの階層順にソートする。parent_numberを含むリストを作成して、それをキーにしてソート
        bonelist = []
        for w in self.weight:
            bonelist.append([ BoneArray[w.name].parent_number , w])

        bonelist.sort(key=lambda x:x[0])

        for w in reversed([ x[1] for x in bonelist ] ):
            parent = BoneArray[w.name].parent
            v = val - BoneArray[w.name].location #回転軸を原点以外に移動 位置にウェイトは掛けなくてよい

            q0 = quat_weight( BoneArray[ w.name ].quatanion , w.value ) #ボーンの逆クオータニオン
            q1 = quat_weight( BoneArray[ parent ].quatanion , w.value ) #親の逆クオータニオン

            #クオータニオンに戻し頂点座標にかける。位置をもとに戻す。最後に親の逆クオータニオンをかける。
            val =  q1 @ ( ( q0 @ v + BoneArray[w.name].location ) - BoneArray[parent].location ) + BoneArray[parent].location
        return  val


    def calc_mat(self , val , BoneArray):
        vec = Vector()
        for w in self.weight:
            #vec +=  BoneArray[BoneArray[w.name].parent].matrix @ BoneArray[w.name].matrix @ ( val - BoneArray[w.name].location ) * w.value  + BoneArray[w.name].location * w.value
            if w.name == 'Bone.001':
                #vec +=   BoneArray[BoneArray[w.name].parent].matrix @ ( BoneArray[w.name].matrix @ ( val - BoneArray[w.name].location ) * w.value  + BoneArray[w.name].location * w.value )
                vec +=   ( BoneArray[w.name].matrix @ ( val - BoneArray[w.name].location ) * w.value  + BoneArray[w.name].location * w.value )

            else:
                vec +=     ( val - BoneArray[w.name].location ) * w.value  + BoneArray[w.name].location * w.value

        print(vec)
        return vec


    #ウェイト割合とマトリックスをかけて足していくことで初期姿勢に戻していく
    def calc_mat__(self , val , boneMatrixArray , initmatrixarray ,boneLocationArray):
        vec = Vector()
        for w in self.weight:
            vec +=  boneMatrixArray[w.name] @ ( val - boneLocationArray[w.name] ) * w.value  + boneLocationArray[w.name] * w.value

        return vec





#---------------------------------------------------------------------------------------
#ブレンドシェイプを元に姿勢に戻す
#ウェイトは振られた状態、アーマチュアモディファイヤはオフにしておく。姿勢はポーズを付けた状態にしておく
#現在の姿勢のインバースをかけて元の姿勢に戻す

#ワールドマトリクスなので親のマトリックスは必要なし
#初期マトリックスが必要
#インバートを掛けたあと初期マトリックスをかける

#ローカルのインバートを掛ける際、原点以外の軸を中心に変換する必要がある
#やり方は頂点座標(vector)からボーンポーズの座標をひく
#---------------------------------------------------------------------------------------


def invert():
    scn = bpy.context.scene.objects
    BoneArray = {}
    BoneArray['init'] = Bone('init')

    #アーマチャーを取得
    for obj in bpy.context.selected_objects:
        if obj.type == 'ARMATURE':
            amt = obj


    utils.activeObj(amt)

    for bone in amt.pose.bones:
        q = Quaternion(bone.rotation_quaternion)
        q.invert()

        BoneArray[bone.name] = Bone(bone.name)
        BoneArray[bone.name].quatanion = q

        m_world = Matrix(bone.matrix)
        BoneArray[bone.name].location = Vector((m_world[0][3] , m_world[1][3] , m_world[2][3]) )


        BoneArray[bone.name].parent_number = len(bone.parent_recursive)



        if bone.parent != None:
            BoneArray[bone.name].parent = bone.parent.name
        else:
            BoneArray[bone.name].parent = 'init'


    #初期マトリックス
    utils.mode_e()
    for bone in amt.data.edit_bones:
        BoneArray[bone.name].initmatrix = Matrix(bone.matrix).to_3x3()

    utils.mode_o()

    for b in BoneArray.values():
        b.conv_quat_axis()

    for obj in bpy.context.selected_objects:
        if obj.type != 'ARMATURE':
            mesh = obj.data
            bm = bmesh.new()
            bm.from_mesh(mesh)

            boneArray = []
            for group in obj.vertex_groups:
                    boneArray.append(group.name)

            #ウェイト値を取得
            vtxarray = []
            for v in mesh.vertices:
                    vtx = Vtx()
                    for vge in v.groups:
                        if vge.weight > 0.00001:#ウェイト値０は除外
                            vtx.getWeight(vge.group, vge.weight ,boneArray) #boneArrayから骨名を割り出して格納
                    vtx.normalize_weight() #ウェイトをノーマライズする
                    vtxarray.append(vtx)


            #obj = bpy.context.object
            #シェイプのインデックス
            #shapekeysList = len(obj.data.shape_keys.key_blocks)
            spIndex = obj.active_shape_key_index

            print(spIndex)
            key = bm.verts.layers.shape.keys()[spIndex]

            val = bm.verts.layers.shape.get(key)
            #sk=mesh.shape_keys.key_blocks[key]

            for v,vtx in zip(bm.verts,vtxarray):
                delta = v[val] - v.co
                v[val] = vtx.calc_quat( v[val] , BoneArray)

            #ブレンドシェイプキーの操作
            # for key in bm.verts.layers.shape.keys():
            #     val = bm.verts.layers.shape.get(key)
            #     #print("%s = %s" % (key,val) )
            #     sk=mesh.shape_keys.key_blocks[key]
            #     #print("v=%f, f=%f" % ( sk.value, sk.frame))
            #     #print(vtxarray)

            #     for v,vtx in zip(bm.verts,vtxarray):
            #         delta = v[val] - v.co
            #         # if (delta.length > 0):
            #         #     print ( "v[%d]+%s" % ( i,delta) )
            #         #v[val] = vtx.calc_mat( v[val] , boneMatrixArray ,initmatrixarray ,boneLocationArray)
            #         v[val] = vtx.calc_quat( v[val] , BoneArray)
            #         #v[val] = m @ v[val]*0.5 + v[val] * 0.5

            bm.to_mesh(obj.data)


VARRAY = []
VARRAY_DIC = {}

#選択された頂点をバッファに保持する
#エディットモードのままだと適用されないことに注意
def copy_pos():
    global VARRAY
    VARRAY.clear()

    global VARRAY_DIC
    VARRAY_DIC.clear()

    obj = bpy.context.active_object
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)

    bpy.ops.object.mode_set(mode = 'OBJECT')
    #選択された頂点インデックスを取得
    #indexarray = []
    indexarray = [i for i,v in enumerate(mesh.vertices) if v.select ]
    # for i,v in enumerate(mesh.vertices):
    #     if v.select:
    #         VARRAY.append([v,v.co])
    #         print(v.co)

    # print(indexarray)
    # return
    #ブレンドシェイプ
    spIndex = obj.active_shape_key_index

    key = bm.verts.layers.shape.keys()[spIndex]
    val = bm.verts.layers.shape.get(key)


    #選択された頂点インデックスは別に取得
    for i,v in enumerate(bm.verts):
        if i in indexarray:

            pos = Vector((v[val][0],v[val][1],v[val][2]))
            VARRAY.append([i,pos])
            VARRAY_DIC[i] = pos
            #print([i,pos])
    #print(VARRAY_DIC)


#シェイプのインデックスが０の時は別処理
def paste_pos():
    global VARRAY
    global VARRAY_DIC

    obj = bpy.context.active_object
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)

    spIndex = obj.active_shape_key_index
    key = bm.verts.layers.shape.keys()[spIndex]
    val = bm.verts.layers.shape.get(key)

    bpy.ops.object.mode_set(mode = 'OBJECT')

    # if spIndex > 0:
    print(len(bm.verts))
    for i,v in enumerate(bm.verts):
        if i in VARRAY_DIC:
            v[val] = VARRAY_DIC[i]
            print(val,i)
        #print(v[val],v1[1])
        #if i == v1[0]:
        #v[val] = v1[1]

    bm.to_mesh(obj.data)
    mesh.update()

    # else:
    #     for i,v in enumerate(mesh.vertices):
    #         if i in VARRAY_DIC:
    #             print(VARRAY_DIC[i])
    #             v.co = VARRAY_DIC[i]


VARRAY_DOWNSTREAM = []
#選択されたブレンドシェイプより下流のブレンドシェイプを保持しておく
#選択中のは含まないので注意
#エディットモードのままだと適用されないことに注意
#配列　[index ,[ [index , Vector ] , [index , Vector ] ] ]
def keep_downstream():
    global VARRAY_DOWNSTREAM
    VARRAY_DOWNSTREAM.clear()

    obj = bpy.context.active_object
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)


    bpy.ops.object.mode_set(mode = 'OBJECT')
    max = len(bm.verts.layers.shape.keys())
    spIndex = obj.active_shape_key_index + 1

    #print(spIndex)
    VARRAY_DOWNSTREAM.append( spIndex  )

    varray_all = []
    for index in range( spIndex  , max ):

        key = bm.verts.layers.shape.keys()[index]
        val = bm.verts.layers.shape.get(key)

        varray = []

        for i,v in enumerate(bm.verts):
            pos = Vector((v[val][0],v[val][1],v[val][2]))
            varray.append([i,pos])
            print([i,pos])
        varray_all.append( varray )

    VARRAY_DOWNSTREAM.append( varray_all )


def restore_downstream():
    global VARRAY_DOWNSTREAM

    obj = bpy.context.active_object
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)

    bpy.ops.object.mode_set(mode = 'OBJECT')


    #spIndex = obj.active_shape_key_index
    spIndex = VARRAY_DOWNSTREAM[0]


    #for i, index in enumerate(range( spIndex + 1 , max )):
    for i, array in enumerate( VARRAY_DOWNSTREAM[1] ):

        index = spIndex + i
        key = bm.verts.layers.shape.keys()[index]
        val = bm.verts.layers.shape.get(key)

        for v,v1 in zip(bm.verts,array):
            print(v[val],v1[1])
            v[val] = v1[1]


    bm.to_mesh(obj.data)
    mesh.update()


#ブレンドシェイプのキーを全削除
def remove_all_keys():
    for ob in utils.selected():
        utils.act(ob)
        bpy.ops.object.shape_key_remove(all=True)


#シェイプキークリア
def shape_key_clear():
    for ob in utils.selected():
        utils.act(ob)
        bpy.ops.object.shape_key_clear()


#---------------------------------------------------------------------------------------
#シェイプキーのアニメーションコピペ
#シェイプキーがなければエラーになる
#---------------------------------------------------------------------------------------
def copy_action():
    bpy.ops.object.mode_set(mode = 'OBJECT')

    obj_source = bpy.context.active_object
    action = obj_source.data.shape_keys.animation_data.action.name


    for ob in utils.selected():
        ob.data.shape_keys.animation_data.action = bpy.data.actions[action]


#---------------------------------------------------------------------------------------
#NLAエディタでアニメーションをプッシュダウンする
#---------------------------------------------------------------------------------------
def push_down():
    for obj in utils.selected():
        if obj.data.shape_keys.animation_data is not None:
            action = obj.data.shape_keys.animation_data.action
            if action is not None:
                track = obj.data.shape_keys.animation_data.nla_tracks.new()
                track.strips.new(action.name, action.frame_range[0], action)
                obj.data.shape_keys.animation_data.action = None


#---------------------------------------------------------------------------------------
#シェイプキーのNLAのミュート、アンミュート
#---------------------------------------------------------------------------------------
def shepekey_mute(mute):
    for obj in utils.selected():
        for j in obj.data.shape_keys.animation_data.nla_tracks:
            j.mute = mute

#---------------------------------------------------------------------------------------
#シェイプキーを挿入
#---------------------------------------------------------------------------------------
def insert_all_keys():
    frame = bpy.context.scene.frame_current

    for ob in utils.selected():
        for kb in ob.data.shape_keys.key_blocks:
            print(kb)
            kb.keyframe_insert(data_path='value', frame= frame )


#---------------------------------------------------------------------------------------
#ミュートされていないシェイプキーを削除する
#---------------------------------------------------------------------------------------
def remove_shapekey_unmuted():

    for ob in utils.selected():
        utils.act(ob)
        # シェイプキーのリストを取得する
        shape_keys = ob.data.shape_keys.key_blocks

        # シェイプキーのリストを逆順に舐める
        # （先頭から消すとインデックスがずれるので後ろから消す）
        for i, shape_key in reversed(list(enumerate(shape_keys))):
            # 消したくないシェイプキーは除外する
            #if shape_key.name != "Basis" or shape_key.mute == False:
            print(shape_key.mute)
            if shape_key.mute == False:
                # シェイプキーを選択して、削除
                bpy.context.active_object.active_shape_key_index = i
                bpy.ops.object.shape_key_remove()


    # for sk in bpy.data.shape_keys:
    #     sk.value = 0
    #     sk.keyframe_insert(data_path='value', frame= 1 )

    # for ob in utils.selected():
    #     for shapekey in ob.data.shape_keys:
    #         # rename / translate shape key names by changing shapekey.name
    #         for keyblock in shapekey.key_blocks:
    #                 print(keyblock.value)

    #         return
        # rename / translate block key names by changing keyblock.name

#    for obj in utils.selected():
#         if obj.data.shape_keys is not None:
#             print(obj.data.shape_keys )
    # bpy.context.object.data.shape_keys.key_blocks ["Key 1"]
    # keyframe_insert（data_path = 'value'、frame = 1）


#---------------------------------------------------------------------------------------
#モブのフェイシャルターゲットのクリンナップ
#シェイプキーは先頭の４つ残しで削除
#---------------------------------------------------------------------------------------
def mob_facial_cleanup():

    namearray = (
    'Basis',
    'CloseEyes',
    'Damage',
    'Fear',
    'Anger',
    )

    for ob in utils.selected():
        utils.act(ob)
        # シェイプキーのリストを取得する
        shape_keys = ob.data.shape_keys.key_blocks

        # シェイプキーのリストを逆順に舐める
        # （先頭から消すとインデックスがずれるので後ろから消す）
        for i, shape_key in reversed(list(enumerate(shape_keys))):

            bpy.context.active_object.active_shape_key_index = i
            bpy.ops.object.shape_key_remove()

            if i == 5:
                break

        #ブレンドシェイプのリネーム
        for shape_key , name in zip(shape_keys,namearray):
            shape_key.name = name

