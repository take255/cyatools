import bpy
import bmesh
from mathutils import ( Matrix , Vector ,kdtree ,Euler)
from math import radians

import imp


from . import utils
imp.reload(utils)


#---------------------------------------------------------------------------------------
#コンポーネント表示のアップデート
#---------------------------------------------------------------------------------------
def vertex_size(self,context):
    view3d = bpy.context.preferences.themes[0].view_3d
    props = bpy.context.scene.cyatools_oa
    view3d.vertex_size = props.vertex_size

def facedot_size(self,context):
    view3d = bpy.context.preferences.themes[0].view_3d
    props = bpy.context.scene.cyatools_oa
    view3d.facedot_size = props.facedot_size

def outline_width(self,context):
    view3d = bpy.context.preferences.themes[0].view_3d
    props = bpy.context.scene.cyatools_oa
    view3d.outline_width = props.outline_width

def origin_size(self,context):
    view3d = bpy.context.preferences.themes[0].view_3d
    props = bpy.context.scene.cyatools_oa
    view3d.object_origin_size = props.origin_size


#---------------------------------------------------------------------------------------
#片側メッシュ削除
#---------------------------------------------------------------------------------------
def del_half_x():
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='DESELECT')#全選択解除してからの
    bpy.ops.mesh.select_all(action='TOGGLE')#全選択

    bpy.ops.mesh.bisect(plane_co=(0, 0, 0), plane_no=(1, 0, 0), use_fill=False, clear_inner=True)
    bpy.ops.object.editmode_toggle()

def select_linked_faces():
    currentmode = utils.current_mode()

    bpy.ops.object.mode_set(mode = 'EDIT')
    obj = bpy.context.edit_object
    me = obj.data

    bm = bmesh.from_edit_mesh(me)

    count = -1
    while(count != 0):
        selected = [f for f in bm.faces if f.select]
        count = len(selected)
        for f in selected:
            for edge in f.edges:
                linked = edge.link_faces
                for face in linked:
                    face.select = True

        count = len([f for f in bm.faces if f.select]) - count

    bmesh.update_edit_mesh(me, True)
    bpy.ops.object.mode_set(mode = currentmode )

#---------------------------------------------------------------------------------------
#reset pivot by selected face normal
#---------------------------------------------------------------------------------------
def pivot_by_facenormal_():

    utils.mode_o()
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True, properties=True)

    utils.mode_e()

    obj = bpy.context.edit_object
    me = obj.data
    bm = bmesh.from_edit_mesh(me)

    upvector = Vector((0,0,1.0))
    upvector_x = Vector((-1.0,0,0))

    for f in bm.faces:
        if f.select:
            pos = f.calc_center_bounds()
            normal = f.normal
            for d in dir(f):
                print(d)

            #法線が(0,0,1)なら別処理
            d = normal.dot(upvector)

            if d > 0.99 or d < -0.99:
                xaxis = normal.cross(upvector_x)
                yaxis = xaxis.cross(normal)
            else:
                xaxis = normal.cross(upvector)
                yaxis = xaxis.cross(normal)

            normal.normalize()
            xaxis.normalize()
            yaxis.normalize()

            x = [x for x in xaxis] +[0.0]
            y = [x for x in yaxis] +[0.0]
            z = [x for x in normal] +[0.0]
            p = [x for x in pos] +[0.0]

            m0 = Matrix([xaxis,yaxis,normal])
            m0.transpose()

            matrix = Matrix([x , y , z , p])
            matrix.transpose()


    utils.mode_o()

    #empty_p = create_locator(obj.name , matrix)

    #親子付けする前に逆変換しておいて親子付け時の変形を打ち消す
    mat_loc = Matrix.Translation([-x for x in pos])
    obj.matrix_world = m0.inverted().to_4x4() @ mat_loc

    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True, properties=True)

    obj.matrix_world = Matrix.Translation(pos) @ m0.to_4x4()
    #obj.parent = empty_p

def pivot_by_facenormal():

    utils.mode_o()
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True, properties=True)

    utils.mode_e()

    obj = bpy.context.edit_object
    me = obj.data
    bm = bmesh.from_edit_mesh(me)

    upvector = Vector((0,0,1.0))
    upvector_x = Vector((-1.0,0,0))

    for f in bm.faces:
        if f.select:
            pos = f.calc_center_bounds()
            normal = f.normal
            xaxis = f.calc_tangent_edge()
            yaxis = xaxis.cross(normal)

            normal.normalize()
            xaxis.normalize()
            yaxis.normalize()

            x = [x for x in xaxis] +[0.0]
            y = [x for x in yaxis] +[0.0]
            z = [x for x in normal] +[0.0]
            p = [x for x in pos] +[0.0]

            m0 = Matrix([xaxis,yaxis,normal])
            m0.transpose()

            matrix = Matrix([x , y , z , p])
            matrix.transpose()


    utils.mode_o()

    #empty_p = create_locator(obj.name , matrix)

    #親子付けする前に逆変換しておいて親子付け時の変形を打ち消す
    mat_loc = Matrix.Translation([-x for x in pos])
    obj.matrix_world = m0.inverted().to_4x4() @ mat_loc

    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True, properties=True)

    obj.matrix_world = Matrix.Translation(pos) @ m0.to_4x4()
    #obj.parent = empty_p


#頂点位置の左から右へのミラーコピー
#選択した頂点をコピーする
def mirror_l_to_r():
    bpy.ops.object.mode_set(mode = 'OBJECT')
    obj = bpy.context.active_object
    mesh = obj.data

    size = len(mesh.vertices)
    kd = kdtree.KDTree(size)

    #rside_indices = [i for i,v in enumerate(mesh.vertices) if v.co.x < 0 and v.select]
    lside_pos = [[i,(-v.co.x , v.co.y , v.co.z )] for i,v in enumerate(mesh.vertices) if v.co.x < 0  and v.select ]


    for i, v in enumerate(mesh.vertices):
        kd.insert(v.co, i)

    kd.balance()

    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')

    for p in lside_pos:
        co, index, dist = kd.find( p[1] )
        print("Close to center:",p[0],':', co, index, dist)
        obj.data.vertices[p[0]].co = (-co.x,co.y,co.z)


    bpy.ops.object.mode_set(mode = 'EDIT')




def mirror_l_to_r_back():
    bpy.ops.object.mode_set(mode = 'OBJECT')
    obj = bpy.context.active_object
    mesh = obj.data

    size = len(mesh.vertices)
    kd = kdtree.KDTree(size)

    rside_indices = [i for i,v in enumerate(mesh.vertices) if v.co.x < 0]
    lside_pos = [[i,(-v.co.x , v.co.y , v.co.z )] for i,v in enumerate(mesh.vertices) if v.co.x < 0]

    # selectedVtxIndex = set([v.index for v in obj.data.vertices if v.select])
    # print(selectedVtxIndex)

    print(lside_pos)
    for i, v in enumerate(mesh.vertices):
        kd.insert(v.co, i)

    kd.balance()

    #co_find = (0.0, 0.0, 0.0)

    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')

    for p in lside_pos:
        co, index, dist = kd.find( p[1] )
        print("Close to center:",p[0],':', co, index, dist)
        obj.data.vertices[p[0]].co = (-co.x,co.y,co.z)


    # for i in rside_indices:
    #     mesh.vertices[i].select = True
        #obj.data.vertices[i].co.x = 2.0
    bpy.ops.object.mode_set(mode = 'EDIT')


#---------------------------------------------------------------------------------------
#選択された頂点をバッファに保持する
#エディットモードのままだと適用されないことに注意
#---------------------------------------------------------------------------------------

#VARRAY = []
VARRAY_DIC = {}

#頂点コピー
def copy_vertex_pos():
    #global VARRAY
    #VARRAY.clear()
    global VARRAY_DIC
    VARRAY_DIC.clear()


    #bpy.ops.object.mode_set(mode = 'OBJECT')
    obj = bpy.context.active_object
    mesh = obj.data

    bpy.ops.object.mode_set(mode = 'OBJECT')
    print('----------------------')
    for i,v in enumerate(mesh.vertices):
        #print(v.select)
        if v.select:
            #pos = Vector((v[val][0],v[val][1],v[val][2]))
            VARRAY_DIC[i] = Vector((v.co[0],v.co[1],v.co[2]))
            #VARRAY.append(v.co)
            #print(v.co)


#頂点ペースト
def paste_vertex_pos():
    # global VARRAY
    global VARRAY_DIC
    #VARRAY_DIC.clear()


    print(VARRAY_DIC)
    obj = bpy.context.active_object
    mesh = obj.data
    bpy.ops.object.mode_set(mode = 'OBJECT')

    for i,v in enumerate(mesh.vertices):
        if i in VARRAY_DIC:
            #print("aaaaa",i,VARRAY_DIC[i])
            v.co = VARRAY_DIC[i]
            #v.co = Vector((1,1,1))


    # for v,v1 in zip(mesh.vertices,VARRAY):
    # #for v in VARRAY:
    #     v.co = v1
    #     # vtx = mesh.vertices[v[0]]
    #     # print(vtx)
    #     print(v.co)





#---------------------------------------------------------------------------------------
#選択された頂点をバッファに保持する
#エディットモードのままだと適用されないことに注意
#---------------------------------------------------------------------------------------
def copy_bshape_pos():
    global VARRAY
    VARRAY.clear()

    obj = bpy.context.active_object
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)

    spIndex = obj.active_shape_key_index
    key = bm.verts.layers.shape.keys()[spIndex]
    val = bm.verts.layers.shape.get(key)

    bpy.ops.object.mode_set(mode = 'OBJECT')

    print('----------------------')

    #選択された頂点インデックスは別に取得
    for i,v in enumerate(bm.verts):
        pos = Vector((v[val][0],v[val][1],v[val][2]))
        VARRAY.append([i,pos])
        print([i,pos])


def paste_bshape_pos():
    global VARRAY

    obj = bpy.context.active_object
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)


    spIndex = obj.active_shape_key_index
    key = bm.verts.layers.shape.keys()[spIndex]
    val = bm.verts.layers.shape.get(key)

    bpy.ops.object.mode_set(mode = 'OBJECT')


    for v,v1 in zip(bm.verts,VARRAY):
        print(v[val],v1[1])
        v[val] = v1[1]
    bm.to_mesh(obj.data)
    mesh.update()


#自動スムーズをONにして角度を１８０度にする
def normal_180deg():
    for ob in utils.selected():
        ob.data.use_auto_smooth = True
        ob.data.auto_smooth_angle = 180


#---------------------------------------------------------------------------------------
#ロケータを配置して分離したいフェースを選択　実行するとフェースが複製されロケータの位置が原点になって配置される
#---------------------------------------------------------------------------------------
def separate_face():
    objects = set([ob.name for ob in utils.selected()])
    bpy.ops.mesh.duplicate_move()
    bpy.ops.mesh.separate(type='SELECTED')

    utils.mode_o()

    dupulicated = []
    for ob in utils.selected():
        if ob.name not in objects:
            dupulicated.append(ob)
            print(ob.name)

    bpy.ops.object.select_all(action='DESELECT')

    utils.act(dupulicated[0])
    for ob in dupulicated:
        utils.select(ob,True)

    bpy.ops.object.join()


#---------------------------------------------------------------------------------------
#欠損を生成する
# 頂点グループに名前をつけて自動でカット
# . で区切る
# 先頭 MISSINGPARTS
# 基準にする骨名
# 出力するメッシュ名
# MISSINGPARTS.lowerarm_l.model_leftarm

#オートマージをオフにする必要あり
#モディファイヤの削除
#回転をかける
#---------------------------------------------------------------------------------------
class Missingparts:
    def __init__(self,vg , index ):
        buf = vg.split('.')
        self.vg = vg
        self.bone = buf[1]
        self.mesh = buf[2]
        self.index = index

def extract_missingparts():
    threshold = 0.9
    partsarray = []
    #頂点グループからMISSINGPARTSが付いたものを選択
    act  = utils.getActiveObj()
    #index = act.vertex_groups.active_index
    for i,b in enumerate(act.vertex_groups):
        vg = b.name
        buf = vg.split('.')
        if buf[0] == 'MISSINGPARTS':
            partsarray.append( Missingparts( vg , i ) )


    #print(partsarray[0].bone,partsarray[0].mesh)
    selected = utils.selected()


    #抽出したい頂点グループごとに処理する
    for mp in partsarray:

        #---------------------------------------------------------------------------------------
        #頂点グループの頂点を選択
        #---------------------------------------------------------------------------------------
        for obj in selected:
            bones = [b.name for b in obj.vertex_groups]
            if mp.vg in bones:
                utils.mode_o()
                utils.act(obj)
                index = bones.index(mp.vg)
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

        #---------------------------------------------------------------------------------------
        #面を分割して別モデルにする
        #---------------------------------------------------------------------------------------
        objects = set([ob.name for ob in utils.selected()])
        bpy.ops.mesh.duplicate_move()
        bpy.ops.mesh.separate(type='SELECTED')

        utils.mode_o()

        dupulicated = []
        for ob in utils.selected():
            if ob.name not in objects:
                dupulicated.append(ob)
                print(ob.name)

        bpy.ops.object.select_all(action='DESELECT')

        utils.act(dupulicated[0])
        for ob in dupulicated:
            utils.select(ob,True)

        bpy.ops.object.join()
        act = utils.getActiveObj()
        act.name = mp.mesh


        #---------------------------------------------------------------------------------------
        #骨の逆行列で原点に持ってくる
        #アマチュアモディファイヤから骨を検索して行列を取得
        #---------------------------------------------------------------------------------------

        for mod in act.modifiers:
            if mod.type == 'ARMATURE':
                amt = mod.object

        utils.act(amt)
        utils.mode_p()

        #bone  = utils.bone.get_active_bone()
        bone = amt.pose.bones[mp.bone]
        matrix = Matrix(bone.matrix)
        matrix.invert()
        #mat_loc = Matrix.Translation(Vector(bone.head))

        act.matrix_world = matrix @ Matrix(act.matrix_world)


#---------------------------------------------------------------------------------------
#欠損を生成する ボックスを使ったバージョン
# 01_MISSING_PARTS_CUTTER　というコレクションにカッターモデルを入れて実行
# カッターモデル名に情報を入れる　. で区切る
# CUTTER.基準にする骨名.出力するメッシュ名
# 例：CUTTER.lowerarm_l.model_leftarm

#オートマージをオフにする必要あり
#モディファイヤの削除
#回転をかける
#---------------------------------------------------------------------------------------
class Missingparts2:
    def __init__(self,ob ):
        buf = ob.name.split('.')
        self.ob = ob
        self.bone = buf[1]
        self.mesh = buf[2]

def extract_missingparts2():

    #01_MISSING_PARTS_CUTTERコレクション内のモデルを検索
    cutterarray = []
    for c in bpy.data.collections:
        if c.name.find('01_MISSING_PARTS_CUTTER') != -1:

            for ob in bpy.context.scene.objects:
                cols = [x.name for x in ob.users_collection]
                if c.name in cols:
                    #cutterarray.append(ob)
                    cutterarray.append(Missingparts2(ob))

    #モデル複製
    #selected = [x.name for x in utils.selected()]
    selected = utils.selected()

    for cutter in cutterarray:
        utils.deselectAll()
        utils.act(selected[0])
        for ob in selected:
            utils.select(ob,True)
            #utils.selectByName(ob,True)

        bpy.ops.object.duplicate_move()

        for ob in utils.selected():
            m = ob.modifiers.new("Boolean", type='BOOLEAN')
            m.object = cutter.ob
            m.operation = 'INTERSECT'


        bpy.ops.object.join()
        act = utils.getActiveObj()
        #---------------------------------------------------------------------------------------
        #骨の逆行列で原点に持ってくる
        #アマチュアモディファイヤから骨を検索して行列を取得
        #---------------------------------------------------------------------------------------

        for mod in act.modifiers:
            if mod.type == 'ARMATURE':
                amt = mod.object

        utils.act(amt)
        utils.mode_p()

        print(cutter.bone)
        bone = amt.pose.bones[cutter.bone]
        matrix = Matrix(bone.matrix)
        matrix.invert()

        print(matrix)

        utils.mode_o()
        utils.act(act)

        #モディファイヤのアプライ
        for mod in act.modifiers:
            bpy.ops.object.modifier_apply( modifier = mod.name )

        act.matrix_world = matrix @ Matrix(act.matrix_world)

        # R0 = Euler((0,0,radians(90))).to_matrix().to_4x4()
        # R1 = Euler((radians(-90),0,0)).to_matrix().to_4x4()
        # act.matrix_world = R1 @ R0 @ act.matrix_world

        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True, properties=True)