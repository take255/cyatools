#import numpy as np
import bpy
import bmesh
from mathutils import ( Vector , Matrix , Quaternion )
import math
import imp
import pickle

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


# VARRAY = []
# VARRAY_DIC = {}

# #選択された頂点をバッファに保持する
# #エディットモードのままだと適用されないことに注意
# def copy_pos():
#     global VARRAY
#     VARRAY.clear()

#     global VARRAY_DIC
#     VARRAY_DIC.clear()

#     obj = bpy.context.active_object
#     mesh = obj.data
#     bm = bmesh.new()
#     bm.from_mesh(mesh)

#     bpy.ops.object.mode_set(mode = 'OBJECT')
#     #選択された頂点インデックスを取得
#     indexarray = [i for i,v in enumerate(mesh.vertices) if v.select ]
#     spIndex = obj.active_shape_key_index

#     key = bm.verts.layers.shape.keys()[spIndex]
#     val = bm.verts.layers.shape.get(key)


#     #選択された頂点インデックスは別に取得
#     for i,v in enumerate(bm.verts):
#         if i in indexarray:

#             pos = Vector((v[val][0],v[val][1],v[val][2]))
#             VARRAY.append([i,pos])
#             VARRAY_DIC[i] = pos


# #シェイプのインデックスが０の時は別処理
# def paste_pos():
#     global VARRAY
#     global VARRAY_DIC

#     obj = bpy.context.active_object
#     mesh = obj.data
#     bm = bmesh.new()
#     bm.from_mesh(mesh)

#     spIndex = obj.active_shape_key_index
#     key = bm.verts.layers.shape.keys()[spIndex]
#     val = bm.verts.layers.shape.get(key)

#     bpy.ops.object.mode_set(mode = 'OBJECT')


#     print(len(bm.verts))
#     for i,v in enumerate(bm.verts):
#         if i in VARRAY_DIC:
#             v[val] = VARRAY_DIC[i]
#             print(val,i)

#     bm.to_mesh(obj.data)
#     mesh.update()



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
#ブレンドシェイプが１つもなければエラーになるのでスルーするようにする
def remove_all_keys():
    for ob in utils.selected():
        utils.act(ob)

        if ob.data.shape_keys != None:
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


#---------------------------------------------------------------------------------------
#末尾に数値がついたシェイプを削除
#---------------------------------------------------------------------------------------
def remove_shapekey_numbered():
    for ob in utils.selected():
        utils.act(ob)
        shape_keys = ob.data.shape_keys.key_blocks

        for i, shape_key in reversed(list(enumerate(shape_keys))):

            # 消したくないシェイプキーは除外する
            # Bufのサイズが２なら数字付きとする
            buf = shape_key.name.split('.')
            if len(buf)>1:
                print(shape_key.name)
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


#---------------------------------------------------------------------------------------
#モブのシェイプ抜き出し
#モデル複製＞現状シェイプ生成＞いらないシェイプ削除
#名前にフレーム番号を割り振る
#
#未対応
#
#---------------------------------------------------------------------------------------
MOBDIC={
10:"M_01",
20:"M_02",
30:"M_03",
40:"M_04",
50:"M_05",
60:"M_06",
70:"M_07",
110:"F_01",
120:"F_02",
130:"F_03",
140:"F_04",
150:"F_05",
160:"F_06",
170:"F_07"
}

MOBDIC_Body={
0:"01",
200:"02",
400:"03",
600:"04",
800:"05",
1000:"06",
1200:"07",
}

MOBDIC_FACE={
10:"01",
20:"02",
30:"03",
40:"04",
50:"05",
60:"06",
70:"07",
80:"08",
90:"09",
100:"10",
110:"11",
120:"12",
130:"13",
140:"14",
150:"15",
160:"16"
}

def mob_extruct0():
    frame = bpy.context.scene.frame_current
    mob_extruct(frame)

def mob_extruct(frame):

    #frame = bpy.context.scene.frame_current

    source = utils.getActiveObj()

    if frame in MOBDIC:
        newname = "Mob_" + MOBDIC[frame]
    else:
        newname = f"{ source.name }_{frame}"

    bpy.ops.object.duplicate(linked=False)
    bpy.ops.object.shape_key_add(from_mix=True)

    ob = utils.getActiveObj()
    ob.name = newname
    # シェイプキーのリストを取得する
    shape_keys = ob.data.shape_keys.key_blocks

    # シェイプキーのリストを逆順に舐める
    #生成された最後のシェイプだけ残す
    max = len(shape_keys)-2

    for i in range(max, -1, -1):
        print(i)
        bpy.context.active_object.active_shape_key_index = i
        bpy.ops.object.shape_key_remove()


    #最後に複製したシェイプの削除
    bpy.context.active_object.active_shape_key_index = 0
    bpy.ops.object.shape_key_remove()

#全種類のモブを抽出
def mob_extruct_all():
    props = bpy.context.scene.cyatools_oa
    source = utils.getActiveObj()

    start = props.mob_extructall_startframe
    for f in MOBDIC:
        bpy.context.scene.frame_set(start+f )
        print(f)
        utils.act(source)
        mob_extruct(f)



def mob_extruct1(newname):

    source = utils.getActiveObj()

    bpy.ops.object.duplicate(linked=False)
    bpy.ops.object.shape_key_add(from_mix=True)

    ob = utils.getActiveObj()
    ob.name = newname
    # シェイプキーのリストを取得する
    shape_keys = ob.data.shape_keys.key_blocks

    # シェイプキーのリストを逆順に舐める
    #生成された最後のシェイプだけ残す
    max = len(shape_keys)-2

    for i in range(max, -1, -1):
        bpy.context.active_object.active_shape_key_index = i
        bpy.ops.object.shape_key_remove()


    #最後に複製したシェイプの削除
    bpy.context.active_object.active_shape_key_index = 0
    bpy.ops.object.shape_key_remove()




#顔バリエーションモデル出力
def mob_extruct_face():
    source = utils.getActiveObj()
    props = bpy.context.scene.cyatools_oa


    #for f0 in MOBDIC_Body:
    for f1 in MOBDIC_FACE:
        #num= f0+f1
        num= 200*(props.mob_body_number-1) +f1

        bpy.context.scene.frame_set( num )
        #frame = bpy.context.scene.frame_current

        newname = "Mob_%s_%02d_0%s" % (props.mob_sex , props.mob_body_number , MOBDIC_FACE[f1] )
        print(newname)

        utils.act(source)
        mob_extruct1(newname)


#終了フレームを指定してブレンドシェイプを抽出
def mob_extruct_frame():
    source = utils.getActiveObj()
    props = bpy.context.scene.cyatools_oa

    for f1 in range(props.mob_extruct_frame):
        #num= f0+f1

        bpy.context.scene.frame_set( f1+1 )
        #frame = bpy.context.scene.frame_current

        newname = "Mob_%02d" % (f1+1)
        print(newname)

        utils.act(source)
        mob_extruct1(newname)


#全種類のモブを抽出
def mob_extruct_():
    source = utils.getActiveObj()

    for f in MOBDIC:
        bpy.context.scene.frame_set( f )
        print(f)
        utils.act(source)
        mob_extruct()

#キーの削除
def remove_transform_key(mode):
    print(mode)

    for ob in utils.selected():
        ad = ob.animation_data

        if ad:
            action = ad.action

            remove_types = ["location", "scale", "rotation"]
            # select all that have datapath above
            # fcurves = [fc for fc in action.fcurves
            #         for type in remove_types
            #         if fc.data_path.startswith(type)
            #         ]
            fcurves = [fc for fc in action.fcurves if fc.data_path.startswith(mode) ]
            # remove fcurves
            while(fcurves):
                fc = fcurves.pop()
                action.fcurves.remove(fc)



#
#
def save_vtxpos_delta(filename):
    VARRAY=[]
    #bpy.ops.object.mode_set(mode = 'OBJECT')
    print(filename)

    selected = utils.selected()
    act = bpy.context.active_object
    mesh = act.data

    bpy.ops.object.mode_set(mode = 'OBJECT')

    for i,v in enumerate(mesh.vertices):
        #if v.select:
        VARRAY.append(Vector((v.co[0],v.co[1],v.co[2])))


    export_data=[]
    for ob in selected:
        if(ob != act):
            mesh = ob.data
            for v,vt in zip(mesh.vertices,VARRAY):
                vec = Vector((v.co[0],v.co[1],v.co[2]))-vt
                export_data.append([vec[0],vec[1],vec[2]])
                print(vec)


    f = open( filename, 'wb' )
    pickle.dump( export_data, f ,protocol=0)
    f.close()


def import_vtxpos_delta(filename):
    f = open(  filename  ,'rb')
    dat = pickle.load( f )
    f.close()

    for d in dat:
        print(d)


    obj = bpy.context.active_object
    mesh = obj.data
    bpy.ops.object.mode_set(mode = 'OBJECT')

    for v,vt in zip(mesh.vertices,dat):
        #pos = Vector((v.co[0],v.co[1],v.co[2]))
        v.co = v.co+Vector((vt[0],vt[1],vt[2]))




#シェイプのインデックスが０の時は別処理
# def paste_pos():
#     global VARRAY
#     global VARRAY_DIC

#     obj = bpy.context.active_object
#     mesh = obj.data
#     bm = bmesh.new()
#     bm.from_mesh(mesh)

#     spIndex = obj.active_shape_key_index
#     key = bm.verts.layers.shape.keys()[spIndex]
#     val = bm.verts.layers.shape.get(key)

#     bpy.ops.object.mode_set(mode = 'OBJECT')


#     print(len(bm.verts))
#     for i,v in enumerate(bm.verts):
#         if i in VARRAY_DIC:
#             v[val] = VARRAY_DIC[i]
#             print(val,i)

#     bm.to_mesh(obj.data)
#     mesh.update()