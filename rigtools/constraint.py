import bpy
import imp
from bpy.props import ( FloatProperty , EnumProperty ,BoolProperty )
import math
from . import utils
imp.reload(utils)
#from bpy.types import PropertyGroup

#this function can expand argument nimber.
#amt1:source amt2:target
#const_type , source_name , target_name , space ,axis_array , invert_array , ratio
#const_type == COPY_LOCATION , source_name , target_name , space ,axis_array , invert_array , ratio
#const_type == COPY_ROTATION , source_name , target_name , space ,axis_array , invert_array , influence
#const_type == COPY_TRANSFORMS , source_name , target_name , space ,head_tail

def do_const_2amt(*args):
    amt = args[0]
    amt_target = args[1]

    #utils.act(amt)
    #amt = bpy.context.object
    #bpy.ops.object.mode_set(mode='POSE')
    #utils.mode_p()

    const_type = args[2]
    source = amt.pose.bones[args[3]]
    target = args[4]
    space  = args[5]

    
    c =source.constraints.new(const_type)
    c.target = amt_target
    c.subtarget = target
    c.target_space = space
    c.owner_space = space

    if const_type == 'COPY_LOCATION':
        if len(args) > 8:
            c.head_tail = args[8]

    if const_type == 'COPY_ROTATION':
        if len(args) > 8:
            c.influence = args[8]


    if const_type != 'COPY_TRANSFORMS':
        axis_array = args[6]
        invert_array = args[7]

        c.use_x = axis_array[0]
        c.use_y = axis_array[1]
        c.use_z = axis_array[2]

        c.invert_x = invert_array[0]
        c.invert_y = invert_array[1]
        c.invert_z = invert_array[2]

    elif const_type == 'COPY_TRANSFORMS': 
        if len(args) > 6:
            c.head_tail = args[6]
    return c

#def constraint(source_name , target_name_array , const_type , space ,axis_x , axis_y , axis_z):
#コンストレインを返す
def constraint(source_name , target_name , const_type , space ,axis_array , invert_array ):
    bpy.ops.object.mode_set(mode='POSE')
    amt = bpy.context.object
    source = amt.pose.bones[source_name]
    target = target_name

    c =source.constraints.new(const_type)
    c.target = amt
    c.subtarget = target
    c.target_space = space
    c.owner_space = space


    if const_type != 'COPY_TRANSFORMS':
        if axis_array[0]:
            c.use_x = True
        else:
            c.use_x = False

        if axis_array[1]:
            c.use_y = True
        else:
            c.use_y = False

        if axis_array[2]:
            c.use_z = True
        else:
            c.use_z = False   

        c.invert_x = invert_array[0]
        c.invert_y = invert_array[1]
        c.invert_z = invert_array[2]
    
    return c

#this function can expand argument nimber.
#const_type , source_name , target_name , space ,axis_array , invert_array , ratio
#const_type == COPY_LOCATION , source_name , target_name , space ,axis_array , invert_array , ratio
#const_type == COPY_ROTATION , source_name , target_name , space ,axis_array , invert_array , influence
#const_type == COPY_TRANSFORMS , source_name , target_name , space ,head_tail

def do_const(*args):
    amt = bpy.context.object
    bpy.ops.object.mode_set(mode='POSE')

    const_type = args[0]
    source = amt.pose.bones[args[1]]
    target = args[2]
    space  = args[3]

    
    c =source.constraints.new(const_type)
    c.target = amt
    c.subtarget = target
    c.target_space = space
    c.owner_space = space

    if const_type == 'COPY_LOCATION':
        c.head_tail = args[6]

    if const_type == 'COPY_ROTATION':
        if len(args) > 6:
            c.influence = args[6]


    if const_type != 'COPY_TRANSFORMS':
        axis_array = args[4]
        invert_array = args[5]

        if axis_array[0]:
            c.use_x = True
        else:
            c.use_x = False

        if axis_array[1]:
            c.use_y = True
        else:
            c.use_y = False

        if axis_array[2]:
            c.use_z = True
        else:
            c.use_z = False   

        c.invert_x = invert_array[0]
        c.invert_y = invert_array[1]
        c.invert_z = invert_array[2]

    elif const_type == 'COPY_TRANSFORMS': 
        if len(args) > 4:
            c.head_tail = args[4]

    
    return c

def do_track_to(*args):
    amt = bpy.context.object
    bpy.ops.object.mode_set(mode='POSE')

    const_type = 'TRACK_TO'
    source = amt.pose.bones[args[0]]
    target = args[1]
    space  = args[2]

    
    c =source.constraints.new(const_type)
    c.target = amt
    c.subtarget = target
    c.target_space = space
    c.owner_space = space
    c.use_target_z = True
    c.up_axis = 'UP_Z'


    return c
#コンストレインを返す
#map_form , map_to = lOCATION or ROTATION or SCALE
#
def constraint_transformation(source_name , target_name , const_type , space , map_from , map_to ,transform ):
    bpy.ops.object.mode_set(mode='POSE')
    amt = bpy.context.object
    source = amt.pose.bones[source_name]
    target = target_name

    c =source.constraints.new(const_type)
    c.target = amt
    c.subtarget = target
    c.target_space = space
    c.owner_space = space

 
    c.map_from = map_from
    c.map_to = map_to

    c.from_min_y_rot = -3.14159
    c.from_max_y_rot = 3.14159
    c.from_min_x_rot = -3.14159
    c.from_max_x_rot = 3.14159
    c.from_min_z_rot = -3.14159
    c.from_max_z_rot = 3.14159


    if transform[0] != 'Mute':
        c.to_min_x_rot = -3.14159
        c.to_max_x_rot = 3.14159

        c.map_to_x_from = transform[0]


    if transform[1] != 'Mute':
        c.to_min_y_rot = -3.14159
        c.to_max_y_rot = 3.14159

        c.map_to_y_from = transform[1]


    if transform[2] != 'Mute':
        c.to_min_z_rot = -3.14159
        c.to_max_z_rot = 3.14159

        c.map_to_y_from = transform[2]
    return c


# source_name , 0:target_name , 1:space , 2:map_from , 3:map_to , 4:map_to_from , 5:map , 6:range_from , 7:range_to , 8:inf
# 9:from_rotation_mode , 10:to_euler_order
#
# map_from: 'LOCATION' , 'ROTATION' , 'SCALE'
# map_to: 'LOCATION' , 'ROTATION' , 'SCALE'
#
# map : [map_to_x_from , map_to_y_from . map_to_z_from] // 'X' , 'Y' , 'Z'
#
# range_from [min_x , max_x , min_y , max_y , min_z , max_z ] 
# range_to [min_x , max_x , min_y , max_y , min_z , max_z ] 
# from_rotation_mode = 'YXZ'
# to_euler_order = 'YXZ'


def do_transformation(*args):
    bpy.ops.object.mode_set(mode='POSE')
    amt = bpy.context.object
    source = amt.pose.bones[args[0]]
    target = args[1]

    c =source.constraints.new('TRANSFORM')
    c.target = amt
    c.subtarget = target
    c.target_space = args[2]
    c.owner_space = args[2]

 
    c.map_from = args[3]
    c.map_to = args[4]

    c.map_to_x_from = args[5][0]
    c.map_to_y_from = args[5][1]
    c.map_to_z_from = args[5][2]

    if args[3] == 'ROTATION':
        c.from_min_x_rot = math.radians(args[6][0])
        c.from_max_x_rot = math.radians(args[6][1])
        c.from_min_y_rot = math.radians(args[6][2])
        c.from_max_y_rot = math.radians(args[6][3])
        c.from_min_z_rot = math.radians(args[6][4])
        c.from_max_z_rot = math.radians(args[6][5])

    elif args[3] == 'SCALE':
        c.from_max_x_scale = args[6][1]
        c.from_min_y_scale = args[6][2]
        c.from_min_x_scale = args[6][0]
        c.from_max_y_scale = args[6][3]
        c.from_min_z_scale = args[6][4]
        c.from_max_z_scale = args[6][5]



    if args[4] == 'ROTATION':
        c.to_min_x_rot = math.radians(args[7][0])
        c.to_max_x_rot = math.radians(args[7][1])
        c.to_min_y_rot = math.radians(args[7][2])
        c.to_max_y_rot = math.radians(args[7][3])
        c.to_min_z_rot = math.radians(args[7][4])
        c.to_max_z_rot = math.radians(args[7][5])

    c.influence = args[8]
    c.from_rotation_mode = args[9]
    c.to_euler_order = args[10]
    return c

def const_limit_rotation( source , angle ):
    amt = bpy.context.object
    utils.mode_p()

    const_type = 'LIMIT_ROTATION'
    
    c =source.constraints.new(const_type)
    c.use_limit_x = True
    c.use_limit_y = True
    c.use_limit_z = True

    c.min_x = -math.radians(angle)
    c.max_x = math.radians(angle)
    c.min_y = -math.radians(angle)
    c.max_y = math.radians(angle)
    c.min_z = -math.radians(angle)
    c.max_z = math.radians(angle)


# class ConstraintTools(bpy.types.Operator):
#     bl_idname = "rigtool.constrainttools"
#     bl_label = "コンストレインツール"

#     def execute(self, context):
#         return {'FINISHED'}

#     def invoke(self, context, event):
#         return context.window_manager.invoke_props_dialog(self)

#     def draw(self, context):
#         scn = context.scene
#         layout = self.layout

#         layout.operator("rigtool.setup_constraint")


#         row = layout.row()
#         row.alignment = 'EXPAND'

#         row.operator("rigtool.constraint_cleanup")
#         row.operator("rigtool.constraint_empty_cleanup")
#         # row.prop(scn, "const_disp_hide", icon='BLENDER', toggle=True)

        # layout.prop(scn, "const_influence", icon='BLENDER', toggle=True)


#Muteでコンストレイン無効にする
TRANSFORM_ITEM = (('X','X',''),('Y','Y',''),('Z','Z',''),('Mute','Mute',''))
TRANSFORM_TYPE = (('LOCATION','LOCATION',''),('ROTATION','ROTATION',''),('SCALE','SCALE',''))

#複数ボーンのコンストレイン適用ツール
#リストに複数のボーンを登録し、同時にコンストレインする。
#選択をコンストレイン元を指定、チェックされたものをコンストレインのターゲット
class KIARIGTOOLS_MT_constrainttools(bpy.types.Operator):
    """複数ボーンをコンストレインする\nリストに対象のボーンを登録して実行する\nボタンを押すとUIが起動する\n選択されたものをコンストレイン元とし、チェックされたものを対象とする。"""
    bl_idname = "cyarigtools.constrainttools"
    bl_label = "add constraint"

    const_type : bpy.props.EnumProperty(items = (
    ('COPY_TRANSFORMS','TRANSFORM',''),
    ('COPY_ROTATION','ROTATION',''),
    ('COPY_LOCATION','LOCATION',''),
    ('TRANSFORM','TRANSFORMATION',''),
    ('LIMIT_ROTATION','LIMIT_ROTATION','')
    ),name = 'const_type')

    space : bpy.props.EnumProperty(items = (
    ('WORLD','WORLD',''),
    ('LOCAL','LOCAL',''),
    ),name = 'space')

    transform_x : bpy.props.EnumProperty(default ='X'  , items = TRANSFORM_ITEM , name = 'X')
    transform_y : bpy.props.EnumProperty(default ='Y'  ,items = TRANSFORM_ITEM , name = 'Y')
    transform_z : bpy.props.EnumProperty(default ='Z'  ,items = TRANSFORM_ITEM , name = 'Z')

    map_from : bpy.props.EnumProperty(default ='LOCATION'  ,items = TRANSFORM_TYPE , name = 'source')
    map_to : bpy.props.EnumProperty(default ='LOCATION'  ,items = TRANSFORM_TYPE , name = 'destination')


    use_x : BoolProperty(name="X" ,  default = True)
    use_y : BoolProperty(name="Y" ,  default = True)
    use_z : BoolProperty(name="Z" ,  default = True)

    invert_x : BoolProperty(name="X" ,  default = False)
    invert_y : BoolProperty(name="Y" ,  default = False)
    invert_z : BoolProperty(name="Z" ,  default = False)

    rot_limit_angle : FloatProperty( name = "rotlimit", min=-180.0 , max=180.0, default=0.0)


    def draw(self, context) :
        layout = self.layout
        layout.prop(self, "const_type")
        layout.prop(self, "space")

        box = layout.row().box()
        row = box.row(align=False)
        row.prop(self, "use_x")
        row.prop(self, "use_y")
        row.prop(self, "use_z")

        box = layout.row().box()
        box.label(text = "Invert")
        row = box.row(align=False)
        row.prop(self, "invert_x")
        row.prop(self, "invert_y")
        row.prop(self, "invert_z")

        box = layout.row().box()
        box.label(text = "Transformation")
        #row = box.row(align=False)

        box.prop(self, "map_from")
        box.prop(self, "map_to")
        
        row = box.row(align=False)
        row.prop(self, "transform_x")
        row.label(text = '>>X')

        row = box.row(align=False)
        row.prop(self, "transform_y")
        row.label(text = '>>Y')

        row = box.row(align=False)
        row.prop(self, "transform_z")
        row.label(text = '>>Z')



        box = layout.row().box()
        box.label(text = "Rotation Limit")
        row = box.row(align=False)
        row.prop(self, "rot_limit_angle")



    #チェックされたものを対象とする。
    #コンストレインの元は選択されたもの
    def execute(self, context):
       #ポーズモードにする
        bpy.ops.object.mode_set(mode = 'POSE')

        amt = bpy.context.object
        for tgt in utils.get_selected_bones():
            if self.const_type == 'TRANSFORM':
                constraint_transformation( tgt , first  ,self.const_type , self.space ,
                self.map_from,self.map_to,
                (self.transform_x , self.transform_y , self.transform_z) )

            elif self.const_type == 'LIMIT_ROTATION':
                const_limit_rotation(tgt , self.rot_limit_angle)

            else:
                constraint(tgt , first  ,self.const_type , self.space ,
                (self.use_x,self.use_y,self.use_z) ,
                (self.invert_x , self.invert_y , self.invert_z)
                )
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)



def register():
    bpy.utils.register_class(KIARIGTOOLS_MT_constrainttools)

def unregister():
    bpy.utils.unregister_class(KIARIGTOOLS_MT_constrainttools)
