import bpy
import imp
import re
import math
import mathutils

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
    if props.bind_auto_bool:
        utils.act(amt)

        disp = []
        for i in range(32):
            disp.append(bpy.context.object.data.layers[i])
            bpy.context.object.data.layers[i] = True
                            
        for ob in obArray:
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

    return 


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



#アーマチュア以外のモディファイヤをapply
def apply_not_armature_modifiers():
    sel = bpy.context.selected_objects
    scene_obj = bpy.context.scene.objects
    for ob in sel:
        scene_obj.active = ob

        for i, mod in enumerate(ob.modifiers):
            if mod.type != 'ARMATURE':
                print(mod.name)
                bpy.ops.object.modifier_apply(modifier=mod.name)



def delete_all_vtxgrp():
    obj = bpy.context.object
    me = obj.data
    result = []
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
def delete_by_word():
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

    boneArray = []
    for group in obj.vertex_groups:
        boneArray.append(group.name)

    #頂点の情報
    msh = obj.data
    vtxCount = str(len(msh.vertices))#頂点数
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



def weights_transfer_v2():
    bpy.ops.object.mode_set(mode = 'OBJECT')

    obj_source = bpy.context.active_object
    mesh = obj_source.data
    size = len(mesh.vertices)

    #ボーン名とインデックスの変換テーブル作成
    bonename2index = {}
    for i,vg in enumerate( obj_source.vertex_groups ):
        bonename2index[vg.name] = i
        
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

            #remove all vertex weight.
            #ボーン名からインデックスからインデックスの変換テーブル作成
            index2index = {}
            for i,vg in enumerate(obj.vertex_groups):
                if vg.name in bonename2index:
                    index2index[ bonename2index[vg.name] ] = i
                vg.remove( range( len(mesh.vertices) ) )
                #print(bonename2index[vg.name],i)

            bpy.ops.object.mode_set(mode = 'EDIT') 
            bpy.ops.mesh.select_mode(type="VERT")
            bpy.ops.mesh.select_all(action = 'DESELECT')
            bpy.ops.object.mode_set(mode = 'OBJECT')

            for i,v in enumerate(mesh.vertices):
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

signdic = { 'R_':'L_' , 'L_':'R_' , '_l':'_r' , '_r':'_l' , 'Left':'Right' , 'Right':'Left' }

sign_prefix = { 'R_':'L_' , 'L_':'R_' , 'Left':'Right' , 'Right':'Left' }
sign_suffix = { '_l':'_r' , '_r':'_l'}


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
        #print(targets)
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
        print(nameflip[i])
        index_inv[i] = namedic[ nameflip[i] ]

    size = len(mesh.vertices)
    kd = mathutils.kdtree.KDTree(size)

    rside_indices = [i for i,v in enumerate(mesh.vertices) if v.co.x < -0.0001]

    lside_pos = [[i,(-v.co.x , v.co.y , v.co.z )] for i,v in enumerate(mesh.vertices) if v.co.x < -0.0001]

    for i, v in enumerate(mesh.vertices):
        kd.insert(v.co, i)

    kd.balance()

    bpy.ops.object.mode_set(mode = 'EDIT') 
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')

    for p in lside_pos:
        for vg in obj.vertex_groups:
            vg.remove([p[0]])

        co, index, dist = kd.find( p[1] )
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
   #ボーン名
    bonearray = set()

    for obj in utils.selected():
        # objname = obj.name
        boneArray = []
        # bonedic = {}
        #targetarray = []
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
                


