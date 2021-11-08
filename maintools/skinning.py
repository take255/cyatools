import bpy
import bmesh
import imp
import re
import math
import mathutils
import csv

from . import utils
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
    #props = bpy.context.scene.cyatools_oa

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
    #If a bone already binded , ignore it .
    #Ignore bone under rig_root.
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
                #if Isrigbone(b):
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
    for obj in utils.selected():
        utils.act(obj)
        for group in obj.vertex_groups:
            bpy.context.object.vertex_groups.remove(group)



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
            #選択モデルをアクティブに
            #objects.active =obj
            utils.act(obj)

            msh = obj.data
            vtxCount = len(msh.vertices)#頂点数

            #頂点数でループ
            for i in range(vtxCount):
                for group in obj.vertex_groups:
                    if group.name not in result:
                        group.add( [i], 0, 'REPLACE' )

            #obj.select = True
            utils.select(obj,True)



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
                weights_transfer_v2()

        else:
            weights_transfer_v2()


#バインドされていなかったらバインドする
def weights_transfer_v2():
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
                        # for i,v in enumerate(mesh.vertices):
                        #     if v.select:
                        #         vg.remove( [i] )


            #bpy.ops.object.mode_set(mode = 'EDIT')
            #bpy.ops.mesh.select_mode(type="VERT")
            #bpy.ops.mesh.select_all(action = 'DESELECT')
            bpy.ops.object.mode_set(mode = 'OBJECT')

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

    for i in range(bonesize):
        index_inv[i] = namedic[ nameflip[i] ]

    size = len(mesh.vertices)
    kd = mathutils.kdtree.KDTree(size)

    #rside_indices = [i for i,v in enumerate(mesh.vertices) if v.co.x < -0.0001]

    #lside_pos = [[i,(-v.co.x , v.co.y , v.co.z )] for i,v in enumerate(mesh.vertices) if v.co.x < -0.0001]

    props = bpy.context.scene.cyatools_oa
    print(props.weightmirror_dir)
    if props.weightmirror_dir == 'L>R':
        opposit_pos = [[i,(-v.co.x , v.co.y , v.co.z )] for i,v in enumerate(mesh.vertices) if v.co.x < -0.0001]
    elif props.weightmirror_dir == 'R>L':
        opposit_pos = [[i,(-v.co.x , v.co.y , v.co.z )] for i,v in enumerate(mesh.vertices) if v.co.x > 0.0001]



    # print('rside>' ,rside_indices)
    # print('lsidepos>')
    # for p in lside_pos:
    #     print(p)


    for i, v in enumerate(mesh.vertices):
        kd.insert(v.co, i)

    kd.balance()

    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')

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
#選択されている頂点のウェイトをすべて削除
#---------------------------------------------------------------------------------------
def remove_weight_selectedVTX():
    bpy.ops.object.mode_set(mode = 'OBJECT')
    obj = bpy.context.active_object

    #頂点の情報
    msh = obj.data
    vtxCount = str(len(msh.vertices))#頂点数
    for v in msh.vertices:
        if v.select:
            for vge in v.groups:
                vge.weight = 0


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
def export_vertexgroup_list():
    obj = bpy.context.object
    result = []
    for group in obj.vertex_groups:
        result.append([group.name,])
        print(group.name)


    print(result)
    with open('e:/tmp/vertexgroup.csv', 'w' , newline = "") as f:
        writer = csv.writer(f)
        writer.writerows(result)


#---------------------------------------------------------------------------------------
#csvファイルを元にウェイトを転送する
#---------------------------------------------------------------------------------------
def transfer_with_csvtable(path):

    #'E:/data/OneDrive/projects/_model/Others/Gmod/mametya/table/transfer01.csv'
    dic = {}
    with open( path ) as f:
        reader = csv.reader(f)
        for row in reader:

            if row[0] != row[1]:#転送元と先が一緒だったら無視する
                dic[row[0]] = row[1]

    for obj in utils.selected():
        boneArray = []
        for group in obj.vertex_groups:
            boneArray.append(group.name)

        size = len(boneArray)
        #頂点の情報
        msh = obj.data
        vtxCount = str(len(msh.vertices))#頂点数

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

