import bpy
import imp

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
def assign():
    props = bpy.context.scene.cyatools_oa

    selected = utils.selected()
    active = utils.getActiveObj()

    utils.deselectAll()


    result = []
    for obj in selected:
        if obj != active:
            result.append(obj)

            #選択モデルをアクティブに
            utils.activeObj(obj)

            constraint =obj.constraints.new(props.const_type)
            constraint.target = active
    utils.mode_o
    utils.deselectAll()
