import bpy
import bmesh
import imp
import re
import math
import mathutils
import csv
import pickle
from pathlib import Path

from . import apply
from . import utils

imp.reload(apply)
imp.reload(utils)

#選択したモデルのアーマチュアモディファイヤを全面に出す
def bone_xray(self,context):
    for ob in utils.selected():
        print(ob.name)
        for m in ob.modifiers:
            if m.type == 'ARMATURE':
                amt = m.object
                print(amt)
                #ob.show_x_ray = not ob.show_x_ray
                amt.show_in_front = not amt.show_in_front


##スキンバインド
def bind():
    props = bpy.context.scene.cyatools_oa
    doSkinBind(props.bind_auto_bool)


def doSkinBind(bind_auto):

    selected = utils.selected()

    obArray = []
    for ob in selected:
        if ob.type == 'ARMATURE':
            amt = ob

    for ob in selected:
        if ob != amt:
            obArray.append(ob)
            utils.activeObj(ob)
            m = ob.modifiers.new("Armature", type='ARMATURE')
            m.object = amt

    #頂点グループ追加
    vtxgrp = set()
    for ob in obArray:
        vtxgrp.clear()
        for group in ob.vertex_groups:
            vtxgrp.add(group.name)

        utils.activeObj(amt)
        utils.mode_e()
        bpy.ops.armature.select_all(action='DESELECT')

        for b in amt.data.edit_bones:
            if not b.name in vtxgrp:

                if b.use_deform == True:
                    b.select = True
                    ob.vertex_groups.new(name = b.name)


    #自動ウェイト振り
    #バインドするためレイヤを全表示する必要がある。表示レイヤを取っておき表示してバインドしたあと元の状態に戻す。

    utils.mode_o()
    if bind_auto:
        utils.act(amt)

        disp = []
        for i in range(32):
            disp.append(bpy.context.object.data.layers[i])
            bpy.context.object.data.layers[i] = True

        for ob in obArray:
            utils.mode_o()
            utils.act(ob)
            bpy.ops.object.mode_set(mode = 'WEIGHT_PAINT')
            bpy.ops.paint.weight_from_bones(type='AUTOMATIC')

        utils.mode_o()
        utils.act(amt)
        for i in range(32):
            bpy.context.object.data.layers[i] = disp[i]




#Deformボーンを除外
def Isrigbone(bone):
    root = 'rig_root'
    parent = bone.parent

    result = True

    if bone.name == root:
        result = False

    elif parent == None:
        result = True

    elif parent.name == root:
        result = False

    else:
        result = Isrigbone(parent)

    return result


#rig_rootを除外
def Isrigbone_(bone):
    root = 'rig_root'
    parent = bone.parent

    result = True

    if bone.name == root:
        result = False

    elif parent == None:
        result = True

    elif parent.name == root:
        result = False

    else:
        result = Isrigbone(parent)

    return result


def asssign_maxweight():
    selected = bpy.context.selected_objects
    obj = selected[1]

    result =[]
    for bone in bpy.context.selected_bones:
        print( bone.name )
        result.append(bone.name)


    bpy.ops.object.mode_set(mode = 'OBJECT')
    objects = bpy.context.scene.objects

    #アーマチュアをエディットモードのままにしておくと選択がおかしくなるのでいったん全選択解除
    bpy.ops.object.select_all(action='DESELECT')

    for obj in selected:
        if obj.type != 'ARMATURE':

            #選択モデルをアクティブに
            objects.active =obj

            msh = obj.data
            vtxCount = len(msh.vertices)#頂点数

            #頂点数でループ
            #一致するバーテックスグループの名前を検索し、100%ウェイトを与える。
            for i in range(vtxCount):
                for group in obj.vertex_groups:
                    if group.name  in result:
                        group.add( [i], 1.0, 'REPLACE' )


#---------------------------------------------------------------------------------------
#選択骨をインフルエンス追加
#---------------------------------------------------------------------------------------
def add_influence_bone():
    selected = utils.selected()
    obj = selected[1]

    result =[]
    for bone in utils.get_selected_bones():
        print( bone.name )
        result.append( bone.name )

    utils.mode_o()
    utils.deselectAll()

    for obj in selected:
        if obj.type != 'ARMATURE':

            utils.activeObj(obj)
            msh = obj.data

            #頂点グループを追加
            for group in result:
                bpy.context.object.vertex_groups.new(name = group)


#---------------------------------------------------------------------------------------
#自動でインフルエンス追加
#---------------------------------------------------------------------------------------
def add_influence_bone_auto():
    selected = utils.selected()

    for ob in selected:

        boneset =[]
        current_grp = []


        for group in ob.vertex_groups:
            current_grp.append(group.name)


        for mod in ob.modifiers:
            if mod.type == 'ARMATURE':
                amt = mod.object
                print( amt.name )

        #アーマチュア内の骨をリストアップしてセットに格納
        utils.act(amt)
        utils.mode_e()
        for b in amt.data.edit_bones:
            boneset.append(b.name)

        utils.mode_o()
        utils.activeObj(ob)

        for b in boneset:
            if b not in current_grp:
                bpy.context.object.vertex_groups.new(name = b)
                print(b)

#---------------------------------------------------------------------------------------
#他のモデルからインフルエンスコピー
#---------------------------------------------------------------------------------------
def copy_influence_bone():
    selected = utils.selected()
    act = utils.getActiveObj()

    bones = []
    for vg in act.vertex_groups :
        bones.append( vg.name )
        #print( vg.name )

    for ob in selected:
        if ob != act:
            utils.activeObj( ob )
            msh = ob.data

            for b in bones :
                bpy.context.object.vertex_groups.new(name = b )
                print( vg.name )



#---------------------------------------------------------------------------------------
#アーマチュア以外のモディファイヤをapply
#---------------------------------------------------------------------------------------
def apply_without_armature_modifiers():
    sel = bpy.context.selected_objects
    scene_obj = bpy.context.scene.objects
    for ob in sel:
        scene_obj.active = ob

        for i, mod in enumerate(ob.modifiers):
            if mod.type != 'ARMATURE':
                print(mod.name)
                bpy.ops.object.modifier_apply(modifier=mod.name)


def delete_all_vtxgrp():
    objects = utils.selected()
    for obj in utils.selected():
        utils.act(obj)
        for group in obj.vertex_groups:
            bpy.context.object.vertex_groups.remove(group)

    for obj in objects:
        utils.select(obj,True)


def delete_notexist_vtxgrp():
    sel = bpy.context.selected_objects
    scene_obj = bpy.context.scene.objects
    for obj in sel:
        boneset = set()
        for i, mod in enumerate(obj.modifiers):
            if mod.type == 'ARMATURE':
                amt = mod.object
                utils.activeObj(amt)
                bpy.ops.object.mode_set(mode='EDIT')

                #アーマチュア内の骨をリストアップしてセットに格納
                for b in amt.data.edit_bones:
                    boneset.add(b.name)

        #頂点グループを走査してボーンのセットに含まれているかどうか調査
        bpy.ops.object.mode_set(mode='OBJECT')
        utils.activeObj(obj)
        for group in obj.vertex_groups:
            if (group.name in boneset) == False:
                bpy.context.object.vertex_groups.remove(group)

    # result = []
    # #jntが含まれていなければ削除対象
    # for group in obj.vertex_groups:
    #     if group.name.find("jnt") == -1:
    #         result.append(group)

    # for group in result:
    #     print(group.name)
    #     bpy.context.object.vertex_groups.remove(group)
def delete_with_word():
    props = bpy.context.scene.cyatools_oa
    name = props.vertexgrp_string

    obj = bpy.context.object
    me = obj.data
    result = []
    #jntが含まれていなければ削除対象
    for group in obj.vertex_groups:
        if group.name.find(name) == -1:
            result.append(group)

    for group in result:
        print(group.name)
        bpy.context.object.vertex_groups.remove(group)



#---------------------------------------------------------------------------------------
#
#ウェイト削除
#
#---------------------------------------------------------------------------------------

#------------------------------
#全ウェイト削除
#------------------------------
def delete_allweights():
    obj=bpy.context.active_object

    # boneArray = []
    # for group in obj.vertex_groups:
    #     boneArray.append(group.name)

    #頂点の情報
    msh = obj.data
    #vtxCount = str(len(msh.vertices))#頂点数
    for v in msh.vertices:
        for vge in v.groups:
            vge.weight = 0

#------------------------------
#選択されているボーン以外のウェイト以外を削除
#------------------------------
def delete_unselectedweights():
    selected = bpy.context.selected_objects
    print( selected[1].name)
    result =set()

    #選択されたボーンを取得
    for bone in bpy.context.selected_bones:
        print( bone.name)
        result.add(bone.name)

    bpy.ops.object.mode_set(mode = 'OBJECT')

    objects = bpy.context.scene.objects

    #アーマチュアをエディットモードのままにしておくと選択がおかしくなるのでいったん全選択解除
    bpy.ops.object.select_all(action='DESELECT')

    # objArray = []
    for obj in selected:
        if obj.type != 'ARMATURE':
            utils.act(obj)
            msh = obj.data
            vtxCount = len(msh.vertices)#頂点数

            #頂点数でループ
            for i in range(vtxCount):
                for group in obj.vertex_groups:
                    if group.name not in result:
                        group.add( [i], 0, 'REPLACE' )

            utils.select(obj,True)


#------------------------------
#選択頂点の部分から選択した骨のウェイトを削除する
#モデルの頂点を選択、除外したいアーマチュアの骨を選択して実行
#------------------------------
def remove_weights_selectedbone():
    selected = bpy.context.selected_objects
    result =set()

    #選択されたボーンを取得
    for bone in bpy.context.selected_bones:
        result.add(bone.name)

    bpy.ops.object.mode_set(mode = 'OBJECT')

    objects = bpy.context.scene.objects

    #アーマチュアをエディットモードのままにしておくと選択がおかしくなるのでいったん全選択解除
    bpy.ops.object.select_all(action='DESELECT')

    # objArray = []
    for obj in selected:
        if obj.type != 'ARMATURE':
            utils.act(obj)
            mesh = obj.data
            #vtxCount = len(msh.vertices)#頂点数

            for i,v in enumerate(mesh.vertices):
                if v.select:
                    for group in obj.vertex_groups:
                        if group.name in result:
                            group.add( [i], 0, 'REPLACE' )

            utils.select(obj,True)


#---------------------------------------------------------------------------------------
#ウェイトのクリンナップ
#---------------------------------------------------------------------------------------
#weight_cleanup

#------------------------------
#選択されている頂点のウェイトをすべて削除
#------------------------------
def remove_weight_selectedVTX():
    bpy.ops.object.mode_set(mode = 'OBJECT')
    obj = bpy.context.active_object

    #頂点の情報
    msh = obj.data
    for v in msh.vertices:
        if v.select:
            for vge in v.groups:
                vge.weight = 0



#---------------------------------------------------------------------------------------
#ウェイトの転送
#選択頂点のウェイト転送は、転送先の頂点をあらかじめ選択しておく仕様
#---------------------------------------------------------------------------------------
def weights_transfer(mode):
    props = bpy.context.scene.cyatools_oa

    if mode == 'v1':
        bpy.ops.object.data_transfer(
            use_create=True,
            vert_mapping='NEAREST',
            data_type='VGROUP_WEIGHTS',
            layers_select_src='ALL',
            layers_select_dst='NAME',
            mix_mode='REPLACE')

    elif mode == 'v2':
        if props.batch_weight_transfer_bool:
            suffix = props.batch_weight_transfer_string
            selected = utils.selected()
            utils.deselectAll()

            for ob in selected:
                sourcename = ob.name + suffix
                utils.actByName(sourcename)
                utils.select(ob,True)
                #weights_transfer_v2()
                wt = WeightTransfer()
                wt.do_transfer()

        else:
            #weights_transfer_v2()
            wt = WeightTransfer()
            wt.do_transfer()


class WeightTransfer:

    def __init__(self):
        props = bpy.context.scene.cyatools_oa
        self.num_sample = props.weight_transfer_samplevtx
        self.selected_only = props.weight_transfer_selected_vtx
        self.keep_org = props.weight_transfer_keep_original
        self.weight_array = []


    #バインドされていなかったらバインドする
    def do_transfer(self):
        props = bpy.context.scene.cyatools_oa
        bpy.ops.object.mode_set(mode = 'OBJECT')

        obj_source = bpy.context.active_object
        mesh = obj_source.data

        #コピー元のkdTreeを作成
        size = len(mesh.vertices)
        self.kd = mathutils.kdtree.KDTree(size)
        for i, v in enumerate(mesh.vertices):
            self.kd.insert(v.co, i)
        self.kd.balance()


        amt = False
        #ソースオブジェクトにバインドされている骨を調べる
        for mod in obj_source.modifiers:
            if mod.type == 'ARMATURE':
                amt = mod.object

        #コピー元にアーマチュアモディファイヤが無ければ実行しない
        if not amt:
            return


        #ボーン名とインデックスの変換テーブル作成
        #ソースオブジェクトにバインドされている骨の一覧を取得
        self.bonename2index = {}
        bonearray = []
        for i,vg in enumerate( obj_source.vertex_groups ):
            self.bonename2index[vg.name] = i
            bonearray.append(vg.name)



        for v in mesh.vertices:
            grp =[]
            for vge in v.groups:
                grp.append([vge.group, vge.weight])
            self.weight_array.append(grp)

        for obj in utils.selected():

            if obj != obj_source:
                mesh = obj.data

                #自動バインド
                #アーマチュアモディファイヤがあるかどうか調べる。無ければ追加する。

                #頂点グループの削除
                utils.act(obj)
                # for group in obj.vertex_groups:
                #     bpy.context.object.vertex_groups.remove(group)


                ExistsAmt = False

                for mod in obj.modifiers:
                    if mod.type == 'ARMATURE':
                        ExistsAmt = True
                        mod.object = amt

                if not ExistsAmt:
                    m = obj.modifiers.new("Armature", type='ARMATURE')
                    m.object = amt


                for b in bonearray:
                    if(b not in [x.name for x in obj.vertex_groups ]):
                        obj.vertex_groups.new(name = b)


                #ボーン名からインデックスからインデックスの変換テーブル作成
                self.index2index = {}

                #選択頂点のインデックスを事前に取得
                indexarray = []

                self.delete_weights( obj , range( len(mesh.vertices))) #ウェイトの削除)
                # if self.selected_only:
                #     for v in mesh.vertices:
                #         if v.select:
                #             indexarray.append(v.index)

                #     self.delete_weights( obj , indexarray )#ウェイトの削除

                # else:
                #     self.delete_weights( obj , range( len(mesh.vertices))) #ウェイトの削除)


                bpy.ops.object.mode_set(mode = 'OBJECT')


                #選択された頂点だけ処理するかどうかで処理を分ける
                if not self.selected_only:
                    for i,v in enumerate(mesh.vertices):
                        self.calc_weight(i,obj,v)
                else:
                    for i,v in enumerate(mesh.vertices):
                        if v.select:
                            self.calc_weight(i,obj,v)



    def delete_weights(self , obj ,targetvtx ):
        for i,vg in enumerate(obj.vertex_groups):
            if vg.name in self.bonename2index:
                self.index2index[ self.bonename2index[vg.name] ] = i

            # if not self.keep_org:#元のウェイトを削除しないでコピー実行
            #     vg.remove( targetvtx )


    def calc_weight( self, i ,obj  , v):
        result = self.kd.find_n( v.co , self.num_sample )

        for vg in obj.vertex_groups:
            vg.remove([i])

        #距離情報から割合を出す 近い方がウェイトが大きいので逆数にする
        #距離が０のときはウェイトを全振りする

        #xに０が無いか調査

        # is_overlapping = False
        # for i,x in enumerate(result):
        #     if x[2] == 0:
        #         weight_ratio = [ result[i][1] , 1 ]
        #         is_overlapping = True
        #         break


        #距離０があるかどうか調べる。あったら100%割り振る
        if 0 in [x[2] for x in result]:
            idx = [x[2] for x in result].index(0)
            weight_ratio = [ [ result[idx][1] , 1.0 ] ]

        else:
            sum_weight = sum([1/x[2] for x in result] ) #result[0][2] + result[1][2]
            weight_ratio = [ [ x[1] , 1/x[2]/sum_weight ] for x in result ]#インデックスと距離に応じた割合 近い方がよりウェイトが大きい




        for wr in weight_ratio:

            index = wr[0]
            ratio = wr[1]

            for w in self.weight_array[index]:#コピー元とコピー先のボーンのインデックスの整合性を合わせている
                if w[0] in self.index2index:
                    target_index = self.index2index[w[0]]
                    vg = obj.vertex_groups[ target_index ]
                    #vg.remove([i])

                    #頂点インデックス、ウェイト値
                    #print( target_index , w[1]*ratio )
                    vg.add( [i], w[1]*ratio , 'ADD' )#




#バインドされていなかったらバインドする
def weights_transfer_v2_():
    props = bpy.context.scene.cyatools_oa
    bpy.ops.object.mode_set(mode = 'OBJECT')

    obj_source = bpy.context.active_object
    mesh = obj_source.data
    size = len(mesh.vertices)

    amt = False
    #ソースオブジェクトにバインドされている骨を調べる
    for mod in obj_source.modifiers:
        if mod.type == 'ARMATURE':
            amt = mod.object



    #コピー元にアーマチュアモディファイヤが無ければ実行しない
    if not amt:
        return


    #ボーン名とインデックスの変換テーブル作成
    #ソースオブジェクトにバインドされている骨の一覧を取得
    bonename2index = {}
    bonearray = []
    for i,vg in enumerate( obj_source.vertex_groups ):
        bonename2index[vg.name] = i
        bonearray.append(vg.name)

    #コピー元のkdTreeを作成
    kd = mathutils.kdtree.KDTree(size)
    for i, v in enumerate(mesh.vertices):
        kd.insert(v.co, i)
    kd.balance()

    weight_array = []

    for v in mesh.vertices:
        grp =[]
        for vge in v.groups:
            grp.append([vge.group, vge.weight])
        weight_array.append(grp)


    for obj in utils.selected():

        if obj != obj_source:
            mesh = obj.data

            #自動バインド
            #アーマチュアモディファイヤがあるかどうか調べる。無ければ追加する。
            ExistsAmt = False
            for mod in obj.modifiers:
                if mod.type == 'ARMATURE':
                    ExistsAmt = True

            if not ExistsAmt:
                m = obj.modifiers.new("Armature", type='ARMATURE')
                m.object = amt

                for b in bonearray:
                    obj.vertex_groups.new(name = b)


            #remove all vertex weight.
            #ボーン名からインデックスからインデックスの変換テーブル作成
            index2index = {}


            #選択頂点のインデックスを事前に取得
            indexarray = []

            if props.weight_transfer_selected_vtx:
                for v in mesh.vertices:
                    if v.select:
                        indexarray.append(v.index)



            for i,vg in enumerate(obj.vertex_groups):
                if vg.name in bonename2index:
                    index2index[ bonename2index[vg.name] ] = i

                if not props.weight_transfer_keep_original:#元のウェイトを削除しないでコピー実行

                    if not props.weight_transfer_selected_vtx:
                        vg.remove( range( len(mesh.vertices) ) )

                    else:#選択頂点だけコピーの場合は選択されている頂点のウェイトだけ削除
                        vg.remove( indexarray )

            bpy.ops.object.mode_set(mode = 'OBJECT')

            #選択された頂点だけ処理するかどうか　
            if not props.weight_transfer_selected_vtx:

                for i,v in enumerate(mesh.vertices):
                    co, index, dist = kd.find( v.co )

                    for w in weight_array[index]:
                        if w[0] in index2index:
                            vg = obj.vertex_groups[ index2index[w[0]] ]
                            #頂点インデックス、ウェイト値
                            vg.add( [i], w[1] , 'REPLACE' )

            else:

                for i,v in enumerate(mesh.vertices):
                    if v.select:
                        co, index, dist = kd.find( v.co )

                        for w in weight_array[index]:
                            if w[0] in index2index:
                                vg = obj.vertex_groups[ index2index[w[0]] ]
                                #頂点インデックス、ウェイト値
                                vg.add( [i], w[1] , 'REPLACE' )

#---------------------------------------------------------------------------------------
#ウェイトのミラー
#---------------------------------------------------------------------------------------
#SMALL = 0.01
#SMALL = 0.1

signR = 'R_'
signL = 'L_'

signdic = { 'R_':'L_' , 'L_':'R_' , '_l':'_r' , '_r':'_l' , 'Left':'Right' , 'Right':'Left' , '_L':'_R' , '_R':'_L' }

sign_prefix = { 'R_':'L_' , 'L_':'R_' , 'Left':'Right' , 'Right':'Left' }
sign_suffix = { '_l':'_r' , '_r':'_l' , '_L':'_R' , '_R':'_L' }
sign_facerig={'.L':'.R','.R':'.L'}
sign_vroid={'R':'L','L':'R'}


def nameFlip_(name):
    strlen=len(name)
    if(strlen<1):
        return name

    for sign in signdic:
        if(name.find( sign ) != -1):
            return name.replace( sign , signdic[sign] )
    return name


def nameFlip(name):
    strlen=len(name)
    if(strlen<1):
        return name

    props = bpy.context.scene.cyatools_oa

    if(props.weightmirror_vroidmode):#_L_ _R_でミラーリング
        buf = name.split('_')
        for sign in sign_vroid:
            if sign in buf:
                new = name.replace('_%s_' % sign, '_%s_' % sign_vroid[sign])
                return new
    else:
        #prefixを調べる
        for sign in sign_prefix:
            if name[ : len(sign) ] == sign:
                new = sign_prefix[sign] + name[ len(sign): ]
                return new

        #suffixを調べる
        for sign in sign_suffix:
            if name[ -len(sign) : ] == sign:
                new = name[:-len(sign)] + sign_suffix[sign]
                return new

        for sign in sign_facerig:
            if name.find(sign)!=-1:
                new = name.replace(sign,sign_facerig[sign])
                return new

    return name


def calDistance(v1,v2):
    vx=v1.x-v2.x
    vy=v1.y-v2.y
    vz=v1.z-v2.z
    return math.sqrt(vx*vx+vy*vy+vz*vz)

def getTgt(v,array , SMALL):
    vcp=v.co.copy()
    vcp.x*=-1
    array.remove(v)
    ret=None
    for tv in array:
        dist=calDistance(vcp,tv.co)
        if(dist<SMALL):
            ret=tv
            array.remove(tv)
            break
    return ret

def weights_mirror(mode):
    if mode == 'v1':
        weights_mirror_v1()
    elif mode == 'v2':
        weights_mirror_v2()

def weights_mirror_v1():
    props = bpy.context.scene.cyatools_oa
    SMALL = props.weight_margin
    index2name={}
    nameflip={}

    obj=bpy.context.active_object
    if(obj.type!='MESH'):
        return

    mesh=obj.data
    for vg in obj.vertex_groups:
        index2name[vg.index]=vg.name
        nameflip[vg.name] = nameFlip(vg.name)
        targets = mesh.vertices.values()

    for v in mesh.vertices:
        if(v.co.x>SMALL):
            tgt = getTgt(v,targets , SMALL)
            if(tgt==None):
                print("no")
                continue
            for vg in obj.vertex_groups:
                vg.remove([tgt.index])
            vgs=v.groups
            for vge in vgs:
                tvg=obj.vertex_groups[nameflip[index2name[vge.group]]]
                tvg.add([tgt.index],vge.weight,'REPLACE')





def weights_mirror_v2():
    bpy.ops.object.mode_set(mode = 'OBJECT')
    obj = bpy.context.active_object
    mesh = obj.data

    index2name={}
    nameflip={}
    index_inv={}
    namedic={}
    bonesize = len(obj.vertex_groups)
    for vg in obj.vertex_groups:
        index2name[vg.index]=vg.name
        nameflip[vg.index] = nameFlip(vg.name)
        namedic[vg.name] = vg.index
        print(vg.name)

    for i in range(bonesize):
        index_inv[i] = namedic[ nameflip[i] ]

    size = len(mesh.vertices)
    kd = mathutils.kdtree.KDTree(size)

    #rside_indices = [i for i,v in enumerate(mesh.vertices) if v.co.x < -0.0001]

    #lside_pos = [[i,(-v.co.x , v.co.y , v.co.z )] for i,v in enumerate(mesh.vertices) if v.co.x < -0.0001]

    props = bpy.context.scene.cyatools_oa

    #選択された頂点だけ処理するかどうか　
    if props.weightmirror_selected_vtx:
        if props.weightmirror_dir == 'L>R':
            opposit_pos = [[i,(-v.co.x , v.co.y , v.co.z )] for i,v in enumerate(mesh.vertices) if v.co.x < -0.0001 and v.select]
        elif props.weightmirror_dir == 'R>L':
            opposit_pos = [[i,(-v.co.x , v.co.y , v.co.z )] for i,v in enumerate(mesh.vertices) if v.co.x > 0.0001 and v.select]


    else:
        if props.weightmirror_dir == 'L>R':
            opposit_pos = [[i,(-v.co.x , v.co.y , v.co.z )] for i,v in enumerate(mesh.vertices) if v.co.x < -0.0001]
        elif props.weightmirror_dir == 'R>L':
            opposit_pos = [[i,(-v.co.x , v.co.y , v.co.z )] for i,v in enumerate(mesh.vertices) if v.co.x > 0.0001]




    for i, v in enumerate(mesh.vertices):
        kd.insert(v.co, i)

    kd.balance()

    # bpy.ops.object.mode_set(mode = 'EDIT')
    # bpy.ops.mesh.select_mode(type="VERT")
    # bpy.ops.mesh.select_all(action = 'DESELECT')
    # bpy.ops.object.mode_set(mode = 'OBJECT')

    for p in opposit_pos:
        #中心付近の頂点で近接を探索したときに自分自身のインデックスがかえってくる
        #そのまま処理すると、その頂点のウェイトが消失する
        #対策としてそういう場合は処理をスキップしてエラーを防ぐ
        co, index, dist = kd.find( p[1] )
        #print(index,co,p[0] != index)

        if p[0] != index:#自分自身のインデックスが帰ってきたらスキップ
            for vg in obj.vertex_groups:
                vg.remove([p[0]])

            v = obj.data.vertices[index]
            mirror_weight = [(index2name[index_inv[vge.group]], vge.weight) for vge in v.groups]

            for w in mirror_weight:
                vg = obj.vertex_groups[ w[0] ]
                #頂点インデックス、ウェイト値
                vg.add( [p[0]], w[1] , 'REPLACE' )



def weights_mirror_v2_():

    obj = bpy.context.object
    #co_find = context.scene.cursor.location @ obj.matrix_world.inverted()

    mesh = obj.data
    size = len(mesh.vertices)
    kd = mathutils.kdtree.KDTree(size)

    #select right side vertices.
    rside_indices = [i for i,v in enumerate(mesh.vertices) if v.co.x < 0]
    lside_pos = [[i,(- v.co.x , v.co.y , v.co.z )] for i,v in enumerate(mesh.vertices) if v.co.x < 0]

    # selectedVtxIndex = set([v.index for v in obj.data.vertices if v.select])
    # print(selectedVtxIndex)

    print(lside_pos)

    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')


    print(rside_indices)
    utils.mode_e()
    for i in rside_indices:
        print(mesh.vertices[i].select)
        mesh.vertices[i].select = True
        mesh.vertices[i].co.x = mesh.vertices[i].co.x + 1


    bpy.ops.object.mode_set(mode = 'EDIT')

    return
    for i, v in enumerate(mesh.vertices):
        kd.insert(v.co, i)

    kd.balance()

    return
    # Find the closest point to the center
    co_find = (0.0, 0.0, 0.0)
    co, index, dist = kd.find(co_find)
    print("Close to center:", co, index, dist)


    # Find the closest 10 points to the 3d cursor
    print("Close 10 points")
    for (co, index, dist) in kd.find_n(co_find, 10):
        print("    ", co, index, dist)


    # Find points within a radius of the 3d cursor
    print("Close points within 0.5 distance")
    co_find = context.scene.cursor.location
    for (co, index, dist) in kd.find_range(co_find, 0.5):
        print("    ", co, index, dist)



# Use this tool when made objects instance.
def mirror_transfer():
    for obj in utils.selected():
        boneArray = []
        targetbone = []

        for group in obj.vertex_groups:
            boneArray.append(group.name)

        for i,bone in enumerate( boneArray ):
            exist = False
            for sign in signdic:
                if(bone.find( sign ) != -1):
                    index = boneArray.index(bone.replace( sign , signdic[sign] ))
                    targetbone.append(boneArray[index])
                    exist = True
                    #return name.replace( sign , signdic[sign] )
            if not exist:
                #bonedic[ i ] = i
                targetbone.append(bone)


            # if bone.find('L_') != -1:
            #     index = boneArray.index(bone.replace('L_','R_'))
            #     targetbone.append(boneArray[index])
            # elif bone.find('R_') != -1:
            #     index = boneArray.index(bone.replace('R_','L_'))
            #     targetbone.append(boneArray[index])

            # else:
            #     bonedic[ i ] = i
            #     targetbone.append(bone)

        # #頂点の情報
        msh = obj.data

        vtxarray = []
        for v in msh.vertices:
            grparray  = []
            for vge in v.groups:
                if vge.weight > 0.00001:#ウェイト値０は除外
                    index = vge.group
                    grparray.append([ targetbone[index] , vge.weight ] )
                    vge.weight = 0.0
            vtxarray.append(grparray)


        for i,point in enumerate( vtxarray ):
            for w in point:
                vg = obj.vertex_groups[w[0]]
                vg.add( [i], float(w[1]), 'REPLACE' )




#---------------------------------------------------------------------------------------
#CSV変換テーブルを使って頂点グループをリネーム
#---------------------------------------------------------------------------------------
def rename_with_csvtable(path):
    # props = bpy.context.scene.cyatools_oa
    # path = props.skin_filepath

    #辞書として読み込む
    dic = {}
    #with open('E:/data/OneDrive/projects/_model/Others/Gmod/mametya/table/exchange01.csv') as f:
    with open( path ) as f:
        reader = csv.reader(f)
        for row in reader:
            dic[row[0]] = row[1]
            print(row)

    obj = bpy.context.object

    #辞書に含まれていたらリネームする
    for group in obj.vertex_groups:
        if group.name in dic:
            group.name = dic[group.name]


#---------------------------------------------------------------------------------------
#頂点グループのリストを出力
#---------------------------------------------------------------------------------------
def export_vertexgroup_list(path):
    obj = bpy.context.object
    result = []
    for group in obj.vertex_groups:
        result.append([group.name,])
        print(group.name)


    print(result)
    with open(path, 'w' , newline = "") as f:
        writer = csv.writer(f)
        writer.writerows(result)


#---------------------------------------------------------------------------------------
#csvファイルを元にウェイトを転送する
#転送先の骨がバインドされていなければ追加する
#---------------------------------------------------------------------------------------
def transfer_with_csvtable(path):

    dic = {}
    target_vtxgrp =set()#不足分の骨がないか調べるための配列

    with open( path ) as f:

        reader = csv.reader(f)
        for row in reader:
            if row[0] != row[1]:#転送元と先が一緒だったら無視する
                dic[row[0]] = row[1]
                target_vtxgrp.add(row[1])

    for obj in utils.selected():
        boneArray = []
        for group in obj.vertex_groups:
            boneArray.append(group.name)

        #バインドされていない頂点グループがあったら追加する
        diff = target_vtxgrp.difference(set(boneArray))
        print('diff',diff)
        for b in diff:
            boneArray.append(b)
            obj.vertex_groups.new(name = b)


        #頂点の情報
        msh = obj.data
        #vtxCount = str(len(msh.vertices))#頂点数

        for i,v in enumerate(msh.vertices):
            #いったんweightarrayに頂点の全部のウェイトを格納
            weightarray = [0.0 ]*len(boneArray)
            for vge in v.groups:
                weightarray[vge.group] = vge.weight

                #転送元のウェイトをクリア
                if boneArray[vge.group] in dic:
                    vge.weight = 0


            #転送元のウェイト値を転送先のウェイトに足す
            for bone in boneArray:
                if bone in dic:
                    idx0 = boneArray.index(bone)
                    idx1 = boneArray.index(dic[bone])

                    weightarray[idx1] += weightarray[idx0]
                    weightarray[idx0] = 0.0

            new_weights = [[i,x] for i,x in enumerate(weightarray) if x > 0.0001]

            #ウェイト値が０ではないものを抜き出し、ウェイトを追加する
            for w in new_weights:
                vg = obj.vertex_groups[w[0]]
                vg.add( [i], w[1], 'REPLACE' )


#---------------------------------------------------------------------------------------
#頂点グループリストで選択したもので、閾値以上のウェイトが振られている頂点を選択
#複数選択したオブジェクトに対応
#---------------------------------------------------------------------------------------
def selectgrp():
    props = bpy.context.scene.cyatools_oa
    threshold = props.threshold_selectweight

    #選択されている頂点グループの名前を調べる
    act  = utils.getActiveObj()
    index = act.vertex_groups.active_index
    bone = act.vertex_groups[index]
    bname = bone.name


    selected = utils.selected()

    for obj in selected:
        bones = [b.name for b in obj.vertex_groups]
        if bname in bones:
            utils.mode_o()
            utils.act(obj)
            index = bones.index(bname)
            print(index)

            msh = obj.data

            indexarray = set()
            for v in msh.vertices:
                for vge in v.groups:
                    if vge.group == index :
                        if vge.weight > threshold:
                            indexarray.add(v.index)

            utils.mode_e()

            bm = bmesh.from_edit_mesh(msh)
            for v in bm.verts:
                v.select = False


            for v in bm.verts:
                if v.index in indexarray:
                    v.select = True


            bm.select_mode |= {'VERT'}
            bm.select_flush_mode()

            bmesh.update_edit_mesh(msh)


    utils.mode_o()
    for obj in selected:
        utils.select(obj,True)
    utils.mode_e()



def weight_export(filename):
    #ボーン名
    bonearray = set()

    for obj in utils.selected():

        objname = obj.name
        boneArray = []
        for group in obj.vertex_groups:
            boneArray.append(group.name)

        #print(boneArray)
        size = len(boneArray)
        #頂点の情報
        msh = obj.data
        #vtxCount = str(len(msh.vertices))#頂点数

        export_data = []
        for v in msh.vertices:
            vtx = Vtx()
            for vge in v.groups:
                if vge.weight > 0.00001 and vge.group < size :#ウェイト値０は除外 and prevent index out of range
                    vtx.getWeight(vge.group, vge.weight ,boneArray) #boneArrayから骨名を割り出して格納
            #vtx.normalize_weight() #ウェイトをノーマライズする

            for bone in [x.name for x in vtx.weight]:
                bonearray.add(bone)

            export_data.append(vtx.export())
        export_data.insert(0,list(bonearray))

        #filename = path + objname + '.wgt'
        #print(export_data[0])
        export_pcl( filename ,  export_data )



        bpy.ops.object.mode_set(mode='OBJECT')


def weight_import(filename):
    props = bpy.context.scene.cyatools_oa

    mode = True
    if utils.current_mode() == 'OBJECT':
        mode = False

    for obj in bpy.context.selected_objects:

        #filename = '%s%s.wgt' % (path ,obj.name)

        #選択された頂点のインデックスのセットをつくり、ウェイトを描き戻すときにチェックする
        #インデックスは０から始まる
        selectedVtx = [v for v in obj.data.vertices if v.select]
        selectedVtxIndex = set([v.index for v in obj.data.vertices if v.select])


        vtxgrp = set()

        for group in obj.vertex_groups:
            vtxgrp.add(group.name)


        #ウェイト値のクリア

        if not props.weight_import_clear:
            if mode:
                for v in selectedVtx:
                    for i, g in enumerate(v.groups):
                        v.groups[i].weight=0
            else:
                for v in obj.data.vertices:
                    for i, g in enumerate(v.groups):
                        v.groups[i].weight=0

        #ウェイト値読み込む
        if mode:#edit mode
            for i,point in enumerate(import_pcl()):
                if i in selectedVtxIndex:
                    for w in point.findall('weight'):
                        vg = obj.vertex_groups[w[0]]
                        vg.add( [i], float(w[1]), 'REPLACE' )

        else:#object mode
            dat = import_pcl(filename)

            bonearray = dat.pop(0)#頂点グループ一覧

            for b in bonearray:
                if b not in vtxgrp:
                    obj.vertex_groups.new(name = b)

            for i,point in enumerate(dat):

                result = []
                for w in point:
                    vg = obj.vertex_groups[w[0]]
                    vg.add( [i], float(w[1]), 'REPLACE' )
                    result.append([w[0],w[1]])




#---------------------------------------------------------------------------------------
#pickle
#---------------------------------------------------------------------------------------
def import_pcl(filename):
    f = open(  filename  ,'rb')
    dat = pickle.load( f )
    f.close()
    return dat

def export_pcl(filename , export_data):
    f = open( filename, 'wb' )
    pickle.dump( export_data, f ,protocol=0)
    f.close()

#---------------------------------------------------------------------------------------
#vertex format
#---------------------------------------------------------------------------------------
class Vtx:
    """頂点出力のためのクラス"""
    co = ''

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
            #w.value = str(w.value/sum)
            w.value = w.value/sum

    def export(self):
        return [[w.name , w.value] for w in self.weight]

#---------------------------------------------------------------------------------------
#小さいウェイトの削除
#---------------------------------------------------------------------------------------
def hummer():
    props = bpy.context.scene.cyatools_oa
    threshold = props.threshold_selectweight
    act = utils.getActiveObj()
    mesh = act.data

    utils.mode_o()
    for v in [x for x in mesh.vertices if x.select]:
        print(v.index)
        for vge in v.groups:
            print(vge.group, vge.weight)
            if( vge.weight < threshold ):
                vg = act.vertex_groups[vge.group]
                vg.add( [v.index], 0.0 , 'REPLACE' )


Parts ={"Body","Eyes","Tangue","Teeth","FemaleBody","Sandal","BodyNoFinger","FemaleBodyNoFinger",
        "Base","Eye","LowerGum","Tongue","UpperGum","Zsandal"
        }


def mob_import_faceit():
    mob_import_main("faceit")

#---------------------------------------------
def mob_import_faceitrig():
    mob_import_main("faceitrig")


#---------------------------------------------
def mob_import_ingame():
    mob_import_main("ingame")


def mob_import_main(mode):
    props = bpy.context.scene.cyatools_oa


    for obj in bpy.context.selected_objects:

        #buf = obj.name.split("_")
        buf = re.split('[_.]', obj.name)
        print(buf)

        path=""
        for p in Parts:
            if(p in buf):
                print(p)
                if(p == "Base"):#Baseの時は個別処理
                    s = props.import_mob_weight_sex
                    if(s=="Male"):
                        p += "_M"

                    elif(s=="Female"):
                        p += "_F"


                path = Path(bpy.context.preferences.addons['cyatools'].preferences.lib_path) / Path(f'Mob/weight/{mode}_{p}.wgt')

        print(path)

        if(path!=""):
            mob_weight_import(obj,path)






def mob_weight_import(obj,path):
    vtxgrp = set()

    for group in obj.vertex_groups:
        vtxgrp.add(group.name)

    #ウェイト値のクリア
    for v in obj.data.vertices:
        for i, g in enumerate(v.groups):
            v.groups[i].weight=0

    #ウェイト値読み込む
    dat = import_pcl(path)

    bonearray = dat.pop(0)#頂点グループ一覧

    for b in bonearray:
        if b not in vtxgrp:
            obj.vertex_groups.new(name = b)

    for i,point in enumerate(dat):

        result = []
        for w in point:
            vg = obj.vertex_groups[w[0]]
            vg.add( [i], float(w[1]), 'REPLACE' )
            result.append([w[0],w[1]])


def mob_process():
    props = bpy.context.scene.cyatools_oa

    if(props.mobproecss_index==1):
        mob_process01()
    elif(props.mobproecss_index==2):
        mob_process02()
    elif(props.mobproecss_index==3):
        mob_process03()


#Mob_Model_CS Mob_Model以下のサンダル以外のモデルを削除
#PoseModel以下のモデルを複製
# レイヤー移動、アーマチュアモディファイヤのアプライ、頂点グループ削除、faceitウェイトインポート
#PoseModelレイヤ非表示

def mob_process01():

    #Mob_Model_CS Mob_Model以下のサンダル以外のモデルを削除
    utils.deselectAll()
    for ob in bpy.data.objects:
        col = [c.name for c in ob.users_collection]

        if('Mob_Model_CS' in col or 'Mob_Model' in col):
            if(ob.name != 'Sandal'):
                utils.select(ob,True)
    bpy.ops.object.delete()


    #poseModelのモデルをFasceit用に複製
    utils.deselectAll()
    objs=[]
    for ob in bpy.data.objects:
        col = [c.name for c in ob.users_collection]
        if('PoseModel' in col):
            if(ob.name != 'Sandal'):
                utils.select(ob,True)



    for ob in utils.selected():
        utils.act(ob)
        bpy.ops.object.duplicate(linked=False)
        objs.append(utils.getActiveObj())

    #１０フレーム目でモディファイヤアプライ
    bpy.context.scene.frame_set( 10 )

    for ob in objs:
        utils.activeObj(ob)
        for mod in ob.modifiers:
            if "ARMATURE" == mod.type:
                bpy.ops.object.modifier_apply( modifier = mod.name )


    for ob in objs:
        utils.select(ob,True)

    delete_all_vtxgrp()
    mob_import_faceit()


    #コレクション移動
    for c in bpy.data.collections:
        if c.name.find('Mob_Model_CS') != -1:
            for ob in objs:
                c.objects.link(ob)

        if c.name.find('PoseModel') != -1:
            for ob in objs:
                c.objects.unlink(ob)

    #PoseModelのハイド
    layer = bpy.context.window.view_layer.layer_collection
    show_collection_by_name(layer,'PoseModel',True)

#--------------------------------------------------------------------
#Process02
#Faceitでインゲーム用のフェイシャルをセットアップしたらこれを実行する
#Eye Bodyを複製して CSじゃないコレクションに移動　コレクションを非表示にする
def mob_process02():
    pattern = re.compile(r'Base|Eye')
    objs=[]
    objs0=[]
    for ob in bpy.data.objects:
        if(bool(pattern.search(ob.name))):
            if('Mob_Model_CS' in [c.name for c in ob.users_collection]):
                #utils.act(ob)
                objs0.append(ob)
                #bpy.ops.object.duplicate(linked=False)
                #objs.append(utils.getActiveObj())

    for ob in objs0:
        utils.act(ob)
        bpy.ops.object.duplicate(linked=False)
        objs.append(utils.getActiveObj())



    #コレクション移動
    for c in bpy.data.collections:
        if c.name=='Mob_Model':
            for ob in objs:
                c.objects.link(ob)

        if c.name=='Mob_Model_CS':
            for ob in objs:
                c.objects.unlink(ob)


    #Mob_Modelのハイド
    layer = bpy.context.window.view_layer.layer_collection
    show_collection_by_name(layer,'Mob_Model',True)



#--------------------------------------------------------------------
#Process03
#Faceitでフェイシャルを設定し終わったら実行。ゲームモデルを生成する
#--------------------------------------------------------------------
def mob_process03():
    #インゲームウェイトの読み込み
    utils.deselectAll()
    for ob in bpy.data.objects:
        col = [c.name for c in ob.users_collection]

        if('Mob_Model_CS' in col or 'Mob_Model' in col):
            utils.select(ob,True)

    delete_all_vtxgrp()
    mob_import_ingame()


    #モデルを一体化する
    layer = bpy.context.window.view_layer.layer_collection
    pattern = re.compile(r'00_Model_Mob')
    pattern0 = re.compile(r'CS$')
    pattern1 = re.compile(r'^(?!.*(CS)).+$')


    for i,model_col in enumerate(('Mob_Model','Mob_Model_CS')):
        utils.deselectAll()
        active_collection_by_name(layer,model_col)
        ob = apply.apply_collection()

        m = ob.modifiers.new("Armature", type='ARMATURE')
        m.object = bpy.data.objects["root"]

        #コレクション移動
        for collection in bpy.data.collections:
            if(i==1 and bool(pattern.search(collection.name)) and bool(pattern0.search(collection.name))):
                col=collection.name

            if(i==0 and bool(pattern.search(collection.name)) and bool(pattern1.search(collection.name))):
                col=collection.name

        for c in bpy.data.collections:
            if c.name==col:
                c.objects.link(ob)


        #ルートからアンリンク
        bpy.context.scene.collection.objects.unlink(ob)





def mob_process03_():
    pattern = re.compile(r'Body|Eyes|Tangue|Teeth')
    objs=[]

    utils.deselectAll()
    for ob in bpy.data.objects:
        if(bool(pattern.search(ob.name))):
            l=[c.name for c in ob.users_collection]
            if('Mob_Model_CS' in l or 'Mob_Model' in l):
                objs.append(ob)

    for ob in objs:
        utils.select(ob,True)

    delete_all_vtxgrp()
    mob_import_ingame()


#Process03
#Faceitのウェイトを削除してインゲームのウェイトをコピー

#Process04
#アプライ済のモデルをコレクションに移動してrootにバインドする


#---------------------------------------------------------------------------------------
#ビューレイヤーを名前で表示状態切替
#---------------------------------------------------------------------------------------
def show_collection_by_name(layer ,name , state):
    props = bpy.context.scene.cyatools_oa
    children = layer.children

    if children != None:
        for ly in children:
            if name == ly.name:
                ly.hide_viewport = state

            show_collection_by_name(ly , name , state)

def active_collection_by_name(layer ,name):
    props = bpy.context.scene.cyatools_oa
    children = layer.children

    if children != None:
        for ly in children:
            if name == ly.name:
                bpy.context.view_layer.active_layer_collection = ly

            active_collection_by_name(ly , name)



