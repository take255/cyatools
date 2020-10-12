import bpy
import bmesh
from mathutils import ( Matrix , Vector ,kdtree)

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


def mirror_l_to_r():
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
