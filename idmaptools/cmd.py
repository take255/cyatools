import bpy , bmesh
import imp

# from bpy.types import ( PropertyGroup , Panel , Operator ,UIList)
# from bpy.props import ( FloatVectorProperty , )

from . import utils
imp.reload(utils)


VERTEX_COLOR = {
'' : '' ,
'SET01'  :("ff0000","ffff00","00ff00","00FFFF","0000FF","FF00FF","000000","ffffff"),
'SET02(GRAY)'  :("FEFEFE","9A9A9A","676767","414141","262626","0C0C0C","040404","000000"),
'SET03(RED)'  :("220000","550000","7D0000","A40001","E60013","E60013","EC6841","FAD6AD"),
'SET04(YELLOW)'  :("322B00","625B00","8A8100","B7AB00","FFF100","FFF45C","FFF899","FFF899"),
'SET05(GREEN)'  :("001200","00370C","005F16","0D7D25","24AC39","7FC269","ACD598","D7EEC9"),
'SET06(BLUE)'  :("00001D","00004A","000762","0008A9","0022E9","0055EE","7FCEF4","B5EBFB"),
'SET07(PURPLE)'  :("200020","350045","450062","530053","601986","8944A1","C177C1","FFAAFF"),

'METAL'  :("ff0000","00ffff","FFA500","333339","ff9999","99ffe9","ffdb99","e4e54c"),
'LEATHER':("fff900","0000ff","999933","333399","ffff99","99bcff","062d0c","ffa500"),
'CLOTH'  :("00ff00","ff00ff","339943","753399","ff6600","db99ff","0d0d59","ec008c"),
'OTHER'  :("590d29","56493d","798ba8","b58f7b","32590d","3e0d59","41410d","af4ce5"),

}

#---------------------------------------------------------------------------------------
#List Rerated Commands
#---------------------------------------------------------------------------------------

#リストからアイテムを取得
def get_item(self):
    return self["name"]

#リストに選択を登録する
def set_item(self, value):
    self["name"] = value

def change_mattype(self,contex):
    props = bpy.context.scene.cyamaterialtools_oa
    add(props.material_type)
    #index = props.material_index

def add(mattype):
    if mattype == '':return

    ui_list = bpy.context.window_manager.cyamaterialtools_list
    itemlist = ui_list.itemlist

    itemlist.clear()
    for index in range(8):
        item = itemlist.add()
        item.name = str(index)

        a = VERTEX_COLOR[ mattype ][ index ]
        item.color = [conv(a[:2]) , conv(a[2:4]) , conv(a[4:]) , 1.0]

        #item.color = (0.75,0.0,0.8,1.0)
        #ui_list.active_index = len(itemlist) - 1

def get_color_value(self):
    return self.get('color', (1.0, 0.0, 1.0))

def set_color_value(self, value):
    self['color'] = value
    #self['color_enum'] = 6


#---------------------------------------------------------------------------------------

def conv(v):
    return float(int(v,16))/255

def color_vertex(ob, vert, color,mode):
    utils.act(ob)
    mesh = ob.data 

    if mesh.vertex_colors:
        vcol_layer = mesh.vertex_colors.active
    else:
        vcol_layer = mesh.vertex_colors.new()

    for poly in mesh.polygons:
        if mode == 0:
            for loop_index in poly.loop_indices:
                vcol_layer.data[loop_index].color = color
        elif mode == 1:
            if poly.select == True:
                for loop_index in poly.loop_indices:
                    vcol_layer.data[loop_index].color = color
            

#---------------------------------------------------------------------------------------
#頂点カラーをアサイン
#assign vertex color only selected vex
#---------------------------------------------------------------------------------------
def assign_vertex_color(mode):
    props = bpy.context.scene.cyamaterialtools_oa

    ui_list = bpy.context.window_manager.cyamaterialtools_list
    itemlist = ui_list.itemlist    
    index = ui_list.active_index

    mat_type = props.material_type

    a = VERTEX_COLOR[ props.material_type ][ index ]
    color = [conv(a[:2]) , conv(a[2:4]) , conv(a[4:]) , 1.0]

    utils.mode_o()
    for ob in utils.selected():
        color_vertex(ob, 2, color , mode)

    if mode == 0:
        utils.mode_o()
    if mode == 1:
        utils.mode_e()
        

#---------------------------------------------------------------------------------------    
#モデルのマテリアルカラーを取得。
#シェーダーはPrincipled BSDFである必要がある。
#---------------------------------------------------------------------------------------
def convert_vertex_color():
    for ob in utils.selected():
        for mat in ob.data.materials:
            nodes = mat.node_tree.nodes
            Node = nodes.get("Principled BSDF")
            color = Node.inputs["Base Color"].default_value[:]
            print(color)
            color_vertex(ob, 2, color)

#---------------------------------------------------------------------------------------    
# First, select polugon face (not vertex) and execute this command.
# 0:assign 1:assign selected  2:pick
#---------------------------------------------------------------------------------------    
def pick_vertex_color(mode):
    props = bpy.context.scene.cyamaterialtools_oa
    mesh = bpy.context.object.data

    #err0 = Msg("The selected object doesn't have a vertex color.")
    if mode == 2:
        utils.mode_o()
        vcol_layer = mesh.vertex_colors.active

        if vcol_layer == None:
            #print('It do not have a vertex color.')
            #err0.draw()
            bpy.context.window_manager.popup_menu( msg01 , title="Error!", icon='INFO')
            return

        vtx_index = [loop_index for poly in mesh.polygons if poly.select for loop_index in poly.loop_indices]

        if len(vtx_index) > 0:
            props.material_color = vcol_layer.data[vtx_index[0]].color[0:4]
            utils.mode_e()
        else:
            #err0.draw()
            bpy.context.window_manager.popup_menu( msg02 , title="Error!", icon='INFO')

    else:
        for ob in utils.selected():
            props = bpy.context.scene.cyamaterialtools_oa
            utils.mode_o()
            color_vertex(ob, 2, props.material_color , mode)

        utils.mode_e()

# class Msg:
#     def __init__(self,text):
#         self.text = text

#     def draw(self):
#         bpy.context.window_manager.popup_menu( self.msg , title="Error!", icon='INFO')

#     def msg(self, context):
#         layout= self.layout
#         layout.label(text= self.text)

#---------------------------------------------------------------------------------------    
#Popup Error Message
#---------------------------------------------------------------------------------------    
def msg01(self, context):
    layout= self.layout
    layout.label(text= "The selected object doesn't have a vertex color.")

def msg02(self, context):
    layout= self.layout
    layout.label(text= "You must select a face.")
