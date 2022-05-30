import bpy
import math
import imp
import json

from . import utils
from . import skinning


imp.reload(utils)
MOB_TYPE_DATA = {}

#プロキシ関連ツール
def make_proxy():
    props = bpy.context.scene.cyatools_oa

    #スキンバインドオプションがONならrootにバインド
    #ただし、rootオブジェクトが無い場合はできなかったダイアログを出す
    if props.proxy_with_skinbinding:
        binding = utils.objexists('root')
    else:
        binding = False

    proxyObjects = []

    for obj in utils.selected():
        #linkedObj = bpy.context.active_object
        col = obj.instance_collection

        for o in col.objects:
            utils.act(obj)
            bpy.ops.object.proxy_make(object=o.name)
            #print(o.name)
            act = utils.getActiveObj()
            act.name = o.name

            proxyObjects.append(act)


        #元のオブジェクトをハイドする
        if props.proxy_hide_source:
            utils.showhide(obj,True)

    #rootにバインドする
    #binding = True
    if binding:
        #print(proxyObjects)
        # utils.deselectAll()
        # for o in proxyObjects:
        #     print(o.name)
            #utils.selectByName(o,True)

        utils.multiSelection(proxyObjects)
        utils.selectByName('root',True)
        skinning.doSkinBind(False)
        # utils.select(ob,state):
        # ob.select_set(state=state)


#コレクション名に合わせてモデル名を変更する
#対象は00_Modelに入っているもので、アーマチュアは除外する
def rename_collection_model():

    for c in bpy.data.collections:

        if c.name.find('00_Model_') != -1:

            basename = c.name.replace( '00_Model_' , 'model_' ).lower()
            num = 1
            for ob in bpy.context.scene.objects:
                if ob.type == 'MESH':
                    cols = [x.name for x in ob.users_collection]
                    if c.name in cols:

                        print( '%s_%02d' % ( basename , num) )
                        ob.name =  '%s_%02d' % ( basename , num)
                        ob.data.name = ob.name
                        num += 1


PartsCollection = None
#コレクション生成
#もしPartsというコレクションがあったら子供にする
#Partsが無い場合は生成する
def create_new_collection():
    global PartsCollection
    PartsCollection = None
    props = bpy.context.scene.cyatools_oa


    #該当のコレクションの種類がすでにある場合、番号を調査して付加する
    category = props.newcollection_name2
    name0 = '00_Model_%s_%s_%s' % ( props.newcollection_name1 , category , props.newcollection_name3 )


    num = 1

    while True:
        name = '%s%02d' % (name0,num)
        if collection_search(name):
            break
        else:
            num += 1

    # for c in bpy.data.collections:
    #     name = '%s%02d' % (name0,num)
    #     if c.name.find(name0) != -1:
    collection = bpy.data.collections.new( name )
    #bpy.context.scene.collection.children.link(collection)

    #Partsというコレクションを見つける
    for c in bpy.data.collections:
        if c.name == 'Parts':
            if category == 'Parts':
                c.children.link(collection)

        if c.name == 'Skin':
            if category == 'Skin':
                c.children.link(collection)


def collection_search(name):
    for c in bpy.data.collections:
        # name = '%s%02d' % (name0,num)
        if c.name.find(name) != -1:
            return False

    return True


#Skin Partsの基本コレクションの作成
def create_new_skin_parts():
    #skinとpartsのコレクションが無かったら生成する

    for name in ('Skin', 'Parts'):
        Exist = False
        for c in bpy.data.collections:
            if c.name == name:
                Exist = True

        print(name,Exist)
        if not Exist:
            print(name)
            collection = bpy.data.collections.new( name )
            bpy.context.scene.collection.children.link(collection)


#     vlayer = bpy.context.view_layer #カレントビューレイヤー
#     for c in vlayer.layer_collection.children:
#         get_collection_loop(c)

#     PartsCollection.children.link(collection)


# def get_collection_loop( c ):
#     global PartsCollection

#     if c.name == 'Parts':
#         PartsCollection = c
#     else:
#         for c in c.children:
#             get_collection_loop(c)



    # bpy.ops.collection.create(name  = "MyTestCollection")
    # bpy.context.scene.collection.children.link(bpy.data.collections["MyTestCollection"])

def pick_collection_name():
    props = bpy.context.scene.cyatools_oa

    col = utils.collection.get_active()
    buf = col.name.split('_')

    props.newcollection_name1 = buf[2]
    props.newcollection_name2 = buf[3]
    props.newcollection_name3 = buf[4][:-2]


#---------------------------------------------------------------------------------------
#ビューレイヤーのステートをjsonで保存する
#全コレクションと親の保存　再構築できるようにする
#---------------------------------------------------------------------------------------
def save_collection_state():
    data = dict()

    visible = utils.collection.get_visible()#表示されている

    layers = [l.name for l in bpy.context.scene.view_layers]

    for l in layers:
        vlayer = bpy.context.scene.view_layers[l]
        bpy.context.window.view_layer = vlayer
        print(l)
        visible = utils.collection.get_visible()#表示されている
        print(visible)
        data[l] = visible


    print(json.dumps(data, ensure_ascii=False, indent=2))
    #dict = {"name": "tarou", "age": 23, "gender": "man"}
    # json_file = open('c:/tmp/test.json', 'w')
    # json.dump(dict, json_file)
    with open('c:/tmp/test.json', mode='wt', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


#---------------------------------------------------------------------------------------
#ビューレイヤーの表示状態をレンダリング状態にマッチさせる
#---------------------------------------------------------------------------------------
def match_render_to_view():

    vlayer = bpy.context.view_layer #カレントビューレイヤー

    #いったん全部表示状態にする
    for o in bpy.data.objects:
        o.hide_viewport = False


    for c in vlayer.objects:
        print(c.name,c.visible_get())

        bpy.data.objects[c.name].hide_viewport = not c.visible_get()
        bpy.data.objects[c.name].hide_render = not c.visible_get()


    visible = utils.collection.get_visible()#表示されている

    for v in visible:
        print(v)

def mob_offset():
    props = bpy.context.scene.cyatools_oa
    mob_offset = props.mob_offset

    val = MOB_TYPE_DATA[mob_offset]
    print(val)

    for ob in utils.selected():
        ob.location.z = float(val)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True, properties=True)


#---------------------------------------------------------------------------------------
#モブの頂点グループゲーム用に修正
#ファイルパスは決めうちで
#---------------------------------------------------------------------------------------
def mob_modify_vtxgrp():
    path = "D:/Prj/B01/Assets/Characters/Common/Data/"
    file1 = 'mob_vtxgrp_transfer.csv'
    file2 = 'mob_bonename_exchange.csv'

    skinning.transfer_with_csvtable( path + file1 )
    skinning.rename_with_csvtable( path + file2 )