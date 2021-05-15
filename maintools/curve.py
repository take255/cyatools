import bpy
from mathutils import Vector

from . import utils


#def create_with_bevel(dir):
#直線カーブを作る
#with bevelがOnなら、ベベル込みのカーブを作成する
#ベベルはcurve_collenctionに格納される￥
def create_liner(dir):
    props = bpy.context.scene.cyatools_oa

    #カーブの作成
    curve  = liner_curve(dir)

    if props.with_bevel == True:
        #ベベル用のサークル生成
        bpy.ops.curve.primitive_bezier_circle_add()
        circleobj = bpy.context.active_object
        circleobj.scale = (0.05,0.05,0.05) 
        circleobj.data.resolution_u = 6


        curve.data.bevel_mode = 'OBJECT'
        curve.data.bevel_object = circleobj

    #curve.data.use_fill_caps = True
        try:
            obj.data.use_uv_as_generated = True    
        except:
            pass


def liner_curve(dir):
    props = bpy.context.scene.cyatools_oa

    bpy.ops.curve.primitive_bezier_curve_add()
    act  = utils.getActiveObj()
    pos = act.location

    utils.mode_e()    
    act.data.splines.active.bezier_points[0].co = Vector()

    if dir == 'x':
        act.data.splines.active.bezier_points[1].co = Vector((1,0,0))
    elif dir == 'y':
        act.data.splines.active.bezier_points[1].co = Vector((0,1,0))
    elif dir == 'z':
        act.data.splines.active.bezier_points[1].co = Vector((0,0,1))

    bpy.ops.curve.handle_type_set(type = 'AUTOMATIC')

    if props.curve_liner == True:
        bpy.ops.curve.spline_type_set(type='POLY')
    utils.mode_o()
    return act


def assign_bevel_loop( selected , bevelobj):
    for obj in selected:
        obj.data.bevel_mode = 'OBJECT'
        obj.data.bevel_object = bevelobj
        obj.data.use_fill_caps = True
        try:
            obj.data.use_uv_as_generated = True    
        except:
            pass


def assign_bevel():
    selected = utils.selected()
    bevelobj = utils.getActiveObj()
    assign_bevel_loop( selected , bevelobj)

def assign_circle_bevel():
    selected = utils.selected()
    bpy.ops.curve.primitive_bezier_circle_add()
    bevelobj = bpy.context.active_object
    assign_bevel_loop( selected , bevelobj)

def assign_liner_bevel():
    selected = utils.selected()
    bevelobj = liner_curve(dir)
    assign_bevel_loop( selected , bevelobj)

def select_bevel():
    act  = utils.getActiveObj()
    bevelobj = act.data.bevel_object

    utils.deselectAll()

    utils.activeObj(bevelobj)
    utils.select(bevelobj,True)