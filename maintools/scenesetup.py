import bpy
import math
import imp
from . import utils
from . import skinning

imp.reload(utils)

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

