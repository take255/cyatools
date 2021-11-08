import bpy
import imp

from mathutils import ( Matrix , Vector ,Euler)
from math import radians

from . import utils
imp.reload(utils)

def apply_x(axis):
    selected = utils.selected()
    utils.deselectAll()

    for ob in selected:
        utils.act(ob)
        loc = Vector(ob.location)
        ob.location = (loc[0],0,0)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True, properties=True)
        ob.location = (0,loc[1],loc[2])

def reset_cursor_rot():
    bpy.context.scene.cursor.rotation_euler = (0,0,0)


#選択したボーンでトランスフォームする　選択した骨がワールドに合うように逆変換する
def invert_bonetransform():
    amt = False
    objects = []
    for ob in utils.selected():
        if ob.type == 'ARMATURE':
            amt = ob
        else:
            objects.append(ob)


    if not amt:
        return

    bone  = utils.bone.get_active_bone()
    matrix = Matrix(bone.matrix)
    matrix.invert()
    mat_loc = Matrix.Translation(Vector(bone.head))


    for ob in objects:
        m = matrix @ Matrix(ob.matrix_world)
        ob.matrix_world = m

def rot90deg(axis):
    x = radians(90)

    if axis == 'x':
        r = (x, 0, 0)
    elif axis == 'y':
        r = (0, x, 0)
    elif axis == 'z':
        r = (0, 0, x)

    R = Euler(r).to_matrix().to_4x4()

    for ob in utils.selected():
        #ob.matrix_world = ob.matrix_world @ R
        ob.matrix_world = R @ ob.matrix_world
