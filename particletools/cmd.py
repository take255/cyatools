import bpy
import imp

from . import utils
imp.reload(utils)



# class AttrProps:
#     def __init__(self):
#         pass

#     def set_attr(self,props):
#         props.shape = ps[ps.active_index].settings.shape

isBanApply = False

ATTRIBUTE = (
'shape',
'root_radius',
'tip_radius',
'radius_scale',
'render_step',
'display_step',
'use_hair_bspline',
)

#---------------------------------------------------------------------------------------
#テンプレートを使ってアトリビュートapplyの関数生成
#---------------------------------------------------------------------------------------
template_apply = """
def apply_%s(self,context):
    apply_attr('%s')
"""
for attr in ATTRIBUTE:
    exec( template_apply % (attr , attr) )

def apply_attr( attr ):
    checked = index_checked()
    props = bpy.context.scene.cyaparticletools_oa
    particle_systems = utils.getActiveObj().particle_systems
    for i , p in enumerate(particle_systems):
        print(i,checked[i])
        ps = p.settings
        if checked[i]:
            exec('ps.%s=props.%s' % (attr,attr))



def apply_edit_render_step(self,context):
    props = bpy.context.scene.cyaparticletools_oa
    bpy.context.scene.tool_settings.particle_edit.display_step = props.edit_display_step

#     checked = index_checked()
#     props = bpy.context.scene.cyaparticletools_oa
#     particle_systems = utils.getActiveObj().particle_systems
#     for i in enumerate(particle_systems):
#         #ps = p.settings
#         if checked[i]:
#             bpy.context.scene.tool_settings.particle_edit.display_step = props.edit_display_step
#             #exec('ps.%s=props.%s' % (attr,attr))

#     #edit_display_step :  IntProperty(name = "edit_display_step" , update=cmd.apply_edit_render_step)
    

#  #bpy.context.scene.tool_settings.particle_edit.display_step = 6


#UPDATE
# def update_shape():
#     particle_systems = utils.getActiveObj().particle_systems
#     for p in particle_systems:
#         bpy.data.particles[p.settings.name].shape = col

#---------------------------------------------------------------------------------------
#パーティクルセッティングを変更したときパラメータをアップデート
#---------------------------------------------------------------------------------------
def test(self,context):
    print('aaaaa')


#---------------------------------------------------------------------------------------
#パーティクルのパラメータアップデート
#---------------------------------------------------------------------------------------
def apply(self,context):

    checked = index_checked()


    global isBanApply

    print(isBanApply)
    if isBanApply:
        return
    # act = utils.getActiveObj()
    props = bpy.context.scene.cyaparticletools_oa

    particle_systems = utils.getActiveObj().particle_systems
    index = particle_systems.active_index

    for i , p in enumerate(particle_systems):
        #ps = bpy.data.particles[p.settings.name]
        ps = p.settings
        if checked[i]:
            for attr in ATTRIBUTE:
                exec('ps.%s=props.%s' % (attr,attr))
            # ps.shape = props.shape
            # ps.root_radius = props.root_radius
            # ps.tip_radius = props.tip_radius
            # ps.radius_scale = props.radius_scale


# def apply_shape(self,context):
#     checked = index_checked()
#     props = bpy.context.scene.cyaparticletools_oa
#     particle_systems = utils.getActiveObj().particle_systems
#     for i , p in enumerate(particle_systems):
#         ps = p.settings
#         if checked[i]:
#             ps.shape = props.shape






# def apply_shape(self,context):
#     apply_attr('shape')

# def apply_root_radius(self,context):
#     apply_attr('root_radius')

# def apply_tip_radius(self,context):
#     apply_attr('tip_radius')

# def apply_radius_scale(self,context):
#     apply_attr('radius_scale')

# def apply_render_step(self,context):
#     apply_attr('render_step')

# def apply_display_step(self,context):
#     apply_attr('display_step')

# def apply_use_hair_bspline(self,context):
#     apply_attr('use_hair_bspline')



def set_attribute():
    act = utils.getActiveObj()
    props = bpy.context.scene.cyaparticletools_oa

    ps = act.particle_systems
    index = ps.active_index

    for attr in ATTRIBUTE:
        exec('props.%s=ps[index].settings.%s' % (attr,attr))

    props.edit_display_step = bpy.context.scene.tool_settings.particle_edit.display_step

    # props.shape = ps[ps.active_index].settings.shape
    # props.root_radius = ps[ps.active_index].settings.root_radius
    # props.tip_radius = ps[ps.active_index].settings.tip_radius
    # props.radius_scale = ps[ps.active_index].settings.radius_scale

    # root_radius :  FloatProperty(name = "root_radius",precision = 4, update=cmd.apply)
    # tip_radius :  FloatProperty(name = "tip_radius",precision = 4, update=cmd.apply)
    # radius_scale :  FloatProperty(name = "radius_scale",precision = 4, update=cmd.apply)


#---------------------------------------------------------------------------------------
#現在のシーンをシーンメニューにセット
#---------------------------------------------------------------------------------------
# def set_collection():
#     props = bpy.context.scene.cyaparticletools_oa
#     props.allcollections.clear()

#     for col in bpy.data.collections:
#         props.allcollections.add().name = col.name

#     #パーティクルセッティング
#     props.allsettings.clear()
#     ps = set()

#     particle_systems = utils.getActiveObj().particle_systems
#     for p in particle_systems:
#         ps.add(p.settings.name)

#     for p in ps:    
#         props.allsettings.add().name = p


#---------------------------------------------------------------------------------------
def effector_collection_assign(mode):
    if mode:
        props = bpy.context.scene.cyaparticletools_oa

        for col in bpy.data.collections:
            props.allcollections.add().name = col.name

        col = bpy.data.collections[props.collection_name]

    else:
        col = None

    particle_systems = utils.getActiveObj().particle_systems
    for p in particle_systems:
        bpy.data.particles[p.settings.name].effector_weights.collection = col

#---------------------------------------------------------------------------------------
#新しい髪の毛のパーティクルセッティングを生成
#---------------------------------------------------------------------------------------
def create_particle_setting():
    bpy.ops.object.particle_system_add()

    ob = bpy.context.object
    ps = ob.particle_systems[-1]
    s = ps.settings
    s.type = 'HAIR'
    s.count = 0
    s.hair_length = 1
    s.child_type = 'SIMPLE'
    s.display_step = 7
    s.render_step = 9

    reload()
    # for p in object.particle_systems:
    # print(p.name)
    
    #print(object.particle_systems[-1])  

    #bpy.data.particles["ParticleSettings.001"].type = 'HAIR'


#---------------------------------------------------------------------------------------
#パーティクルセッティングをコピー
#---------------------------------------------------------------------------------------
def copy_particle_settings():
    checked = index_checked()
    particle_systems = utils.getActiveObj().particle_systems
    
    active_setting = particle_systems[active_index()].settings

    for i, p in enumerate(particle_systems):
        if checked[i]:
            p.settings = active_setting
        
    
# def sort_particle_sistem():
#     ps = utils.getActiveObj().particle_systems
#     print(dir(ps))
#     ps[0] = ps[1]
#     reload()


#---------------------------------------------------------------------------------------
#リストコマンド
#---------------------------------------------------------------------------------------
def itemlist():
    ui_list = bpy.context.window_manager.cyaparticletools_list
    return ui_list.itemlist    

def active_index():
    ui_list = bpy.context.window_manager.cyaparticletools_list
    return ui_list.active_index

#パーティクルシステム順のインデックス
def active_ps_index():
    ui_list = bpy.context.window_manager.cyaparticletools_list

    #print(itemlist())
    index = itemlist()[ui_list.active_index].idx
   # print(itemlist()[ui_list.active_index].mod)

    return index
    #return ui_list[ui_list.active_index].idx
    #return ui_list.active.idx


def active_index_set(index):
    #index_list = 0
    for i,x in enumerate(itemlist()):
        if x.idx == index:
            index_list = i

    ui_list = bpy.context.window_manager.cyaparticletools_list
    ui_list.active_index = index_list

def index_checked():
    # result = []
    # for node in itemlist():
    #     node.bool_val = True
    return [x.check  for x in itemlist()]

def disp(self,context):
    for x in itemlist():
        if x.disp:
            x.iconname = 'RESTRICT_VIEW_OFF'
            bpy.context.object.modifiers[x.mod].show_viewport = True

        else:
            x.iconname = 'RESTRICT_VIEW_ON'
            bpy.context.object.modifiers[x.mod].show_viewport = False


def get_item():
    pass
def showhide():
    pass
def set_item():
    pass
def clear():
    il = itemlist()
    il.clear()

def reload():
    clear()
    act = utils.getActiveObj()
    #ui_list = bpy.context.window_manager.cyaparticletools_list
    il = itemlist()
    
    particle_systems = act.particle_systems

    # if len(particle_systems) == 0:
    #     return True
    
    #パーティクルのモディファイヤを取得。リストに加える
    mod_dic = {}
    for mod in act.modifiers:
        if mod.type == 'PARTICLE_SYSTEM':
        
            mod_dic[mod.particle_system.name] = [ mod.name , mod.show_viewport ]


    #名前でソートする
    #パーティクル名、インデックス、モディファイヤ名、現在の表示状態
    result = []
    for i,p in enumerate(particle_systems):
        result.append([p.name ,i , mod_dic[p.name][0] , mod_dic[p.name][1] ] )
    
    result.sort()
    
    for p in result:
        item = il.add()
        item.name = p[0]
        item.iconname = 'RESTRICT_VIEW_OFF'
        item.idx = p[1]
        item.mod = p[2]
        item.disp = p[3]

    #return False
    # for p in particle_systems:
    #     item = il.add()
    #     item.name = p.name
    #     item.iconname = 'GROUP'

#アクティブオブジェクトにパーティクルがあるかどうかチェック
def check_not_ps():
    act = utils.getActiveObj()
    particle_systems = act.particle_systems
    if len(particle_systems) == 0:
        return True
    else:
        False

#すべてのパーティクルの表示状態変更
def showhide_all(mode):
    for x in itemlist():
        x.disp = mode

#チェックを付けたパーティクルの表示状態変更
def showhide_check(mode):
    for x in itemlist():
        if x.check:
            x.disp = True
        else:
            x.disp = False

    #disp()

    # if mode:
    #     for x in itemlist():
    #         x.disp = mode
    #         print(x.mod)
    #         x.iconname = 'RESTRICT_VIEW_OFF'
    #         bpy.context.object.modifiers[x.mod].show_viewport = True
    # else:
    #     for x in itemlist():
    #         x.iconname = 'RESTRICT_VIEW_ON'
    #         bpy.context.object.modifiers[x.mod].show_viewport = False



