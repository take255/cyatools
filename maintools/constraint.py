import bpy
import imp
from mathutils import Matrix


from . import utils
imp.reload(utils)

TYPE = (
('COPY_LOCATION','COPY_LOCATION','') ,
('COPY_ROTATION','COPY_ROTATION','') ,
('COPY_SCALE','COPY_ROTATION',''),
('COPY_TRANSFORMS','COPY_TRANSFORMS','') ,
('LIMIT_DISTANCE','LIMIT_DISTANCE',''),
)

#Constraint---------------------------------------------------------------------------------------
#アクティブをコンスト先にする
def assign(mode):
    props = bpy.context.scene.cyatools_oa

    selected = utils.selected()
    active = utils.getActiveObj()

    utils.deselectAll()

    result = []
    for obj in selected:                    
        result.append(obj)
        if mode == 'assign':
            if obj != active:                
                result.append(obj)
                #選択モデルをアクティブに
                utils.activeObj(obj)

                constraint =obj.constraints.new(props.const_type)
                constraint.target = active

        else:
            utils.act(obj)

            m = Matrix(obj.matrix_world)
            for c in obj.constraints:
                if c.type == props.const_type:

                    if mode == 'apply' or mode == 'remove':
                        c.mute = True
                        obj.constraints.remove(c)

                    elif mode == 'show':
                        c.mute = False

                    elif mode == 'hide':
                        c.mute = True

            if mode == 'apply':
                obj.matrix_world = m
            
    utils.mode_o
    utils.deselectAll()

    for ob in result:
        utils.select(ob,True)



def apply_all(mode):
    selected = utils.selected()
    utils.deselectAll()

    result = []
    for ob in selected:                    

        result.append(ob)
        m = Matrix(ob.matrix_world)

        for c in ob.constraints:
            ob.constraints.remove(c)

        if mode == 0:
            ob.matrix_world = m


    for ob in result:
        utils.select(ob,True)