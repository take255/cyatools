

import bpy
import imp
from collections import ChainMap
from mathutils import ( Vector , Matrix )

from .. import utils
from . import arpbone
from . import constraint
from . import setup_ik

imp.reload(utils)
imp.reload(arpbone)
imp.reload(constraint)
imp.reload(setup_ik)


bconv={
'pelvis':'spine',
'spine_01':'spine.001',
'spine_02':'spine.002',
'spine_03':'spine.003',

'spine_03':'spine.004',
'spine_03':'spine.003',

'thigh_l':'thigh.L',
'thigh_r':'thigh.R',
'calf_l':'shin.L',
'calf_r':'shin.R',
'foot_l':'foot.L',
'foot_r':'foot.R',
'ball_l':'toe.L',
'ball_r':'toe.R',
}

#先端のボーン。向きをＸ軸方向に合わせる
tip =[
'toe.L',
'toe.R',
]


def move_layer(bone_name,number,amt):
    #まずは移動先をアクティブにする
    amt.data.layers[number] = True

    #レイヤをすべてアクティブではない状態にする
    for i in range(32):
        bpy.context.object.data.layers[number] = False
        bpy.context.object.data.bones[bone_name].layers[i] = False    

    bpy.context.object.data.bones[bone_name].layers[number] = True


#---------------------------------------------------------------------
#アーマチュアとボーン名,リグの親骨名　を渡して姿勢データを取得
#---------------------------------------------------------------------
def getBonePose( amt , bname , p ):
    b = amt.pose.bones[bname]
    #p = d_swap[bname]
    m = Matrix(b.matrix)
    head = Vector(b.head)
    tail = Vector(b.tail)
    return [b.name,m,head,tail,p]



#---------------------------------------------------------------------
#ARPとMixamoをコンストレインする
#Mixamo,ARPの順で選択する
#---------------------------------------------------------------------
def const(rig):

    if rig == 'ue4':
        bonedic =  arpbone.ue4
        root = 'pelvis'

    elif rig == 'ue4_ex':
        bonedic =  arpbone.ue4_ex
        root = 'pelvis'

    elif rig == 'mixamo':
        bonedic =  arpbone.mixamo
        root = 'mixamorig:Hips'


    selected = utils.selected()
    arp = utils.getActiveObj()
    selected.remove(arp)
    tgt = selected[0]

    #ボーン軸向きがおかしくなるのでミラーをオフにしておく
    bpy.context.object.data.use_mirror_x = False

    #tgtをアクティブにしてボーンを取得
    #ボーンの位置を取得する

    utils.act(tgt)
    utils.mode_p()
    bonelist = []

    d_swap = {v: k for k, v in bonedic.items()}#辞書の要素を反転

    #コンストレインを全削除
    for bone in tgt.pose.bones:
        for const in bone.constraints:
            bone.constraints.remove( const )

    allbonename = [b.name for b in tgt.pose.bones]
    

    for bname in bonedic.values():
        if bname in allbonename:
            p = d_swap[bname]
            bonelist.append(getBonePose( tgt , bname , p ))
            # b = tgt.pose.bones[bname]
            # p = d_swap[bname]
            # m = Matrix(b.matrix)
            # head = Vector(b.head)
            # tail = Vector(b.tail)
            # bonelist.append([b.name,m,head,tail,p])
            # print([b.name,p])

    print('-----------------------------')

    #---------------------------------------------------------------------
    #ue4_exの場合、背骨、首など別処理にする
    #---------------------------------------------------------------------
    if rig == 'ue4_ex':

        allneckbone = []
        for bone in allbonename:
            buf = bone.split('_')
            name = buf[0]

            #背骨の名前を生成して辞書に追加していく
            if name == 'spine':
                p = 'spine_%s.x' % buf[-1]
                bonelist.append(getBonePose( tgt , bone , p ))
                # getBonePose( tgt , bname )
                # bonelist.append( [bone , m , head , tail , p ])

            #しっぽ
            if name == 'tail':
                p = 'c_tail_%02d.x' % ( int(buf[-1]) - 1 )
                bonelist.append(getBonePose( tgt , bone , p ))

            #首骨をすべて拾ってから名前割り当て
            if name == 'neck':
                allneckbone.append(bone)
                # p = 'c_tail_%02d.x' % ( int(buf[-1]) - 1 )
                # bonelist.append(getBonePose( tgt , bone , p ))


            #---------------------------------------------------------------------
            #脚の対応するリグのボーン名を生成
            #thigh_bに関してはぶら下げるのに適当なボーンが見当たらないので　c_thigh_b　に直でぶら下げる
            #---------------------------------------------------------------------
            if name in arpbone.ue4_ex_additional:#辞書のキーに含まれる文字列で抽出
                
                num = ''

                #後ろから2番目の要素が数値なら３桁にする
                if buf[-2].isnumeric():
                    num = '_dupli_%03d' % int(buf[-2])
        
                if buf[1] == 'b':
                    name = name + '_b'

                if buf[1] == 'twist':
                    name = name + '_stretch'

                rigbonename = '%s%s.%s' % (arpbone.ue4_ex_additional[name],num,buf[-1])
                bonelist.append(getBonePose( tgt , bone , rigbonename ))

            #---------------------------------------------------------------------
            #extもコントローラに直にぶら下げる
            #---------------------------------------------------------------------
            if buf[0] == 'ext':
                if buf[-1] == 'l' or buf[-1] == 'r':
                    p = 'c_%s.%s' % (bone.replace('_' + buf[-1] , '') , buf[-1])
                else:
                    p = 'c_%s.x' % bone

                bonelist.append(getBonePose( tgt , bone , p ))


        #首骨　neckboneをソートして、最後の骨を　neck.x　にする
        #c_subneck_1.x c_subneck_2.x neck.x

        allneckbone.sort()        
        lastbone = allneckbone.pop()
        #bonedic[lastbone] = 'neck_ref.x'
        bonelist.append(getBonePose( tgt , lastbone , 'neck.x' ))

        for i,bone in enumerate(allneckbone):
            bonelist.append(getBonePose( tgt , bone , 'c_subneck_%01d.x' % (i+1) ))
            #bonedic[bone] = 'subneck_%01d_ref.x' % (i+1)



    for i in bonelist:
        print(i[0],i[-1])

    #---------------------------------------------------------------------
    #ここからARPリグの処理
    #arpの骨にtgtの骨を追加
    #---------------------------------------------------------------------
    utils.mode_o()
    utils.act(arp)
    utils.mode_e()

    bpy.context.object.data.layers[30] = True
    
    #ボーンが存在していたら削除
    bpy.ops.armature.select_all(action='DESELECT')
    constbones = [x.name for x in arp.data.edit_bones]
    for l in bonelist:
        if l[0] in constbones:
            arp.data.edit_bones[l[0]].select = True
    
    bpy.ops.armature.delete()


    #ボーン生成
    for l in bonelist:
        b = arp.data.edit_bones.new(l[0])
        
        b.head = l[2]
        b.tail = l[3]
        b.matrix = l[1]

        b.parent = arp.data.edit_bones[l[4]]


    #---------------------------------------------------------------------
    #ルートモーション用コンストレイン
    #---------------------------------------------------------------------

    #c_trajでスケルトンのルートを拘束する　root_base　を子供にする
    b = arp.data.edit_bones.new('root_base')
    b.head = Vector((0,0,0))
    b.tail = Vector((0,1,0))

    b.parent = arp.data.edit_bones['c_traj']
    #root_baseでroot(アーマチュア)をコンストレインする
    utils.mode_o()
    c = tgt.constraints.new('COPY_TRANSFORMS')
    c.target = arp
    c.subtarget = 'root_base'
    

    #---------------------------------------------------------------------
    #コンストレイン
    #---------------------------------------------------------------------
    utils.mode_o()
    utils.act(tgt)
    utils.mode_p()
    #for bname in bonedic.values():
    for item in bonelist:
        bname = item[0]
        print(bname)
        constraint.do_const_2amt(tgt,arp,'COPY_ROTATION',bname,bname,'WORLD',(True,True,True) , (False,False,False))

    #Hipsだけトランスもコンストレイン
    #bname = 'mixamorig:Hips'
    constraint.do_const_2amt(tgt,arp,'COPY_LOCATION',root,root,'WORLD',(True,True,True) , (False,False,False))

    #レイヤ３０に移動
    utils.mode_o()
    utils.act(arp)
    utils.mode_p()
    
    #for l in bonedic.values():
    for item in bonelist:
        setup_ik.move_layer( item[0] , 30 )


#リグコンストレイン旧仕様
def const_(rig):

    if rig == 'ue4':
        bonedic =  arpbone.ue4
        root = 'pelvis'

    elif rig == 'mixamo':
        bonedic =  arpbone.mixamo
        root = 'mixamorig:Hips'


    selected = utils.selected()
    arp = utils.getActiveObj()
    selected.remove(arp)
    tgt = selected[0]

    #ボーン軸向きがおかしくなるのでミラーをオフにしておく
    bpy.context.object.data.use_mirror_x = False

    
    #tgtをアクティブにしてボーンを取得
    #ボーンの位置を取得する

    utils.act(tgt)
    utils.mode_p()
    bonelist = []

    d_swap = {v: k for k, v in bonedic.items()}

    #コンストレインを全削除
    for bone in tgt.pose.bones:
        for const in bone.constraints:
            bone.constraints.remove( const )

    allbonename = [b.name for b in tgt.pose.bones]
    for bname in bonedic.values():
        if bname in allbonename:
            b = tgt.pose.bones[bname]
            p = d_swap[bname]
            m = Matrix(b.matrix)
            head = Vector(b.head)
            tail = Vector(b.tail)
            # roll = b.roll
            bonelist.append([b.name,m,head,tail,p])


    # for b in bonelist:
    #     print(b)
    #arpの骨にtgtの骨を追加
    utils.mode_o()
    utils.act(arp)
    utils.mode_e()
    
    
    bpy.context.object.data.layers[30] = True
    
    #ボーンが存在していたら削除
    bpy.ops.armature.select_all(action='DESELECT')
    constbones = [x.name for x in arp.data.edit_bones]
    for l in bonelist:
        if l[0] in constbones:
            arp.data.edit_bones[l[0]].select = True
            #b.select = True
    
    bpy.ops.armature.delete()


    #ボーン生成
    for l in bonelist:
        b = arp.data.edit_bones.new(l[0])
        
        b.head = l[2]
        b.tail = l[3]
        b.matrix = l[1]

        b.parent = arp.data.edit_bones[l[4]]

        #print(l)


    #コンストレイン
    utils.mode_o()
    utils.act(tgt)
    utils.mode_p()
    for bname in bonedic.values():
        constraint.do_const_2amt(tgt,arp,'COPY_ROTATION',bname,bname,'WORLD',(True,True,True) , (False,False,False))

    #Hipsだけトランスもコンストレイン
    #bname = 'mixamorig:Hips'
    constraint.do_const_2amt(tgt,arp,'COPY_LOCATION',root,root,'WORLD',(True,True,True) , (False,False,False))

    #レイヤ３０に移動
    utils.mode_o()
    utils.act(arp)
    utils.mode_p()
    
    for l in bonedic.values():
        setup_ik.move_layer(l,30)


def const_(rig):
    if rig == 'ue4':
        bonedic =  arpbone.ue4
        root = 'pelvis'
    if rig == 'mixamo':
        bonedic =  arpbone.mixamo
        root = 'mixamorig:Hips'


    selected = utils.selected()
    arp = utils.getActiveObj()
    selected.remove(arp)
    tgt = selected[0]


    print(arp)
    print(tgt)
    
    #tgtをアクティブにしてボーンを取得
    #ボーンの位置を取得する

    utils.act(tgt)
    utils.mode_e()
    bonelist = []

    d_swap = {v: k for k, v in bonedic.items()}

    allbonename = [b.name for b in tgt.data.edit_bones]
    for bname in bonedic.values():
        if bname in allbonename:
            b = tgt.data.edit_bones[bname]
            p = d_swap[bname]
            head = Vector(b.head)
            tail = Vector(b.tail)
            roll = b.roll
            bonelist.append([b.name,head,tail,roll,p])

    #arpの骨にtgtの骨を追加
    utils.mode_o()
    utils.act(arp)
    utils.mode_e()

    
    bpy.context.object.data.layers[30] = True
    for l in bonelist:
        b = arp.data.edit_bones.new(l[0])
        b.head = l[1]
        b.tail = l[2]
        b.roll = l[3]

        b.parent = arp.data.edit_bones[l[4]]

        print(l)

    #コンストレイン
    utils.mode_o()
    utils.act(tgt)
    utils.mode_p()
    for bname in bonedic.values():
        constraint.do_const_2amt(tgt,arp,'COPY_ROTATION',bname,bname,'WORLD',(True,True,True) , (False,False,False))

    #Hipsだけトランスもコンストレイン
    #bname = 'mixamorig:Hips'
    constraint.do_const_2amt(tgt,arp,'COPY_LOCATION',root,root,'WORLD',(True,True,True) , (False,False,False))

    #レイヤ３０に移動
    utils.mode_o()
    utils.act(arp)
    utils.mode_p()
    
    for l in bonedic.values():
        setup_ik.move_layer(l,30)


#実装されてない
def extracter():
    print(arpbone.bonedic)


#メタリグをアクティブにして選択
def fit_metarig():
    metarig = utils.getActiveObj()#
    print(metarig.name)

    selected = utils.selected()
    utils.deselectAll()

    for r in selected:
        if r != metarig:
            utils.mode_o()
            utils.act(r)

            print(r.name)
            utils.mode_e()

            m_array = {}
            for bone in r.data.edit_bones:
                matrix = bone.matrix
                if bone.name in bconv:

                    # matrix = bone.matrix
                    # #matrix = bone.matrix.to_3x3()
                    # matrix.transpose()

                    # x =  -matrix[2]
                    # y =  matrix[0]
                    # z = -matrix[1]


                    head = Vector(bone.head)
                    # m = Matrix((x,y,z,matrix[3]))
                    # m.transpose()
                    # #matrix = m.to_4x4()

                    m_array[ bconv[bone.name] ] = head
                    print(bone.name,bone.matrix )
    

            utils.mode_o()
            utils.act(metarig)
            utils.mode_e()

            for bone in metarig.data.edit_bones:
                if bone.name in m_array:
                    print('>>',bone.name)
                    bone.head = m_array[bone.name]
                    #bone.head = m_array[bone.name][0]
                    #print(bone.name,bone.matrix )

def check_transform():
    loc = bpy.context.object.location
    
#---------------------------------------------------------------------
# UE4,MIXAMOのボーン位置にARPリファレンスボーンを合わせる
# UE4,またはMIXAMOのアーマチュアを選択し、最後にARPリファレンスボーンを選択して実行する
#リグがアプライされていなければ注意を出す
#---------------------------------------------------------------------
def adjust_arp(mode):
    if mode == 'ue4':
        bonedic =  arpbone.ue4_ref
        root = 'pelvis'
    if mode == 'mixamo':
        bonedic =  arpbone.mixamo_
        root = 'mixamorig:Hips'
    if mode == 'ue4_ex':
        bonedic =  arpbone.ue4_ex_ref
        root = 'pelvis'

    init_matrix = Matrix()
    selected = utils.selected()

    #フリーズされていなければ処理を中断
    for ob in selected:
        if ob.matrix_world != init_matrix:
            msg = 'トランスフォームがフリーズされていません。'
            bpy.ops.cyatools.messagebox('INVOKE_DEFAULT', message = msg)
            return

    arp = utils.getActiveObj()
    arp.data.use_mirror_x = False #角度がおかしくなるのでミラーオプションを切る。多分 r>lの順に処理すれば切らなくても大丈夫

    selected.remove(arp)
    tgt = selected[0]

    print(arp)
    print(tgt)
    
    #tgtをアクティブにしてボーンを取得
    #ボーンの位置を取得する
    #ターゲットのトランスフォームフリーズ
    utils.act(tgt)
    #bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    utils.mode_p()
    bonelist = []

    #d_swap = {v: k for k, v in bonedic.items()}

    #コンストレインを全削除
    for bone in tgt.pose.bones:
        for const in bone.constraints:
            bone.constraints.remove( const )



    #---------------------------------------------------------------------
    #アジャスト実行
    #---------------------------------------------------------------------
    
    allbonename = [b.name for b in tgt.pose.bones]


    #追加骨用変数
    extbonedic = {} #追加骨の辞書
    bonelist_ext = []

    #人型以外のスケルトンは別処理にする
    #背骨と首骨は長さが一定ではないので、ボーンを抽出して名前を変換
    if mode == 'ue4_ex':
        
        allneckbone = []
        alltailbone = []
        for bone in allbonename:
            buf = bone.split('_')

            #背骨の名前を生成して辞書に追加していく
            if buf[0] == 'spine':
                print(bone,'%s_ref.x' % bone)
                bonedic[bone] = '%s_ref.x' % bone

            #首骨をすべて拾ってから名前割り当て
            if buf[0] == 'neck':
                allneckbone.append(bone)

            #しっぽ リグのインデックスは 00　始まり
            if buf[0] == 'tail':
                alltailbone.append(bone)


            #脚などの骨  thigh_ref_dupli_001.l
            if buf[0] in ('thigh', 'calf' , 'foot' , 'ball' ):
                num = ''
                sign = buf[-1]
                name = arpbone.ue4_ex_ref_additional[buf[0]]

                #後ろから2番目の要素が数値なら３桁にする
                if buf[-2].isnumeric():
                    num = '_dupli_%03d' % int(buf[-2])
        
                if buf[1] == 'b':
                    name = '%s_b' % name
        
                bonedic[bone] = '%s_ref%s.%s' % (name , num , sign )

            #ext骨を抜き出しリグのボーンを生成する
            #規則　ext_hair_06_01 > c_ext_hair_06_01.x
            #lrがついている　 ext_skin_calf_l > c_ext_skin_calf.l
            if buf[0] == 'ext':
                if buf[-1] == 'l' or buf[-1] == 'r':
                    extbonedic[bone] = 'c_%s.%s' % (bone.replace('_' + buf[-1] , '') , buf[-1])
                else:
                    extbonedic[bone] = 'c_%s.x' % bone



        #首骨　neckboneをソートして、最後の骨をrefにする
        allneckbone.sort()
        
        lastbone = allneckbone.pop()
        bonedic[lastbone] = 'neck_ref.x'

        for i,bone in enumerate(allneckbone):
            bonedic[bone] = 'subneck_%01d_ref.x' % (i+1)

        #しっぽ tail_00_ref.x
        alltailbone.sort()
        for i,bone in enumerate(alltailbone):
            bonedic[bone] = 'tail_%02d_ref.x' % i



        # for b in bonedic:
        #     print(b,bonedic[b])


    for bname in bonedic:
        if bname in allbonename:
            b = tgt.pose.bones[bname]

            name = bonedic[bname]
            head = Vector(b.head)
            tail = Vector(b.tail)
            m = Matrix(b.matrix)

            bonelist.append( [ name , head , tail , m ] )

    #---------------------------------------------------------------------
    #追加骨をリグツリーにコピーするためのデータを生成する
    #追加骨のリグ骨はリファレンス用の骨に親子付けしても作動させられない　変換する必要がある
    # head_ref.x >> c_head.x  _refを抜いて頭に c_ をつける
    #全部の骨の辞書を生成　親骨の取得に使用
    #---------------------------------------------------------------------

    bonedic_all = ChainMap(bonedic , extbonedic) 
    for bname in extbonedic:
        b = tgt.pose.bones[bname]

        name = extbonedic[bname]
        head = Vector(b.head)
        tail = Vector(b.tail)

        #親がリファレンスならばコントローラに変換
        parent = bonedic_all[b.parent.name]

        if parent.find('_ref') != -1:
                parent = 'c_' + parent.replace('_ref' , '')

        print(parent)
        m = Matrix(b.matrix)

        bonelist_ext.append( [ name , head , tail , m ,parent] )


    #arpの骨にtgtの骨を追加
    utils.mode_o()
    utils.act(arp)
    utils.mode_e()

    for l in bonelist:
        if l[0] in arp.data.edit_bones:
            b = arp.data.edit_bones[l[0]]
            b.head = l[1]
            b.tail = l[2]
            b.matrix = l[3]

    #もし存在していないなら　追加骨を生成 
    for l in bonelist_ext:
        if l[0] in arp.data.edit_bones:
            b = arp.data.edit_bones[l[0]]
        else:
            b = arp.data.edit_bones.new(l[0])
    
        b.head = l[1]
        b.tail = l[2]
        b.matrix = l[3]

    #追加骨の親子付けはすべて生成されたから
    for l in bonelist_ext:
        b = arp.data.edit_bones[l[0]]
        b.parent = arp.data.edit_bones[l[4]]


    #レイヤーを０に移動してシェイプをスフィアに変更
    utils.mode_p()
    for l in bonelist_ext:
        setup_ik.move_layer(l[0],0)
        arp.pose.bones[l[0]].custom_shape = bpy.data.objects['cs_sphere']
        #bpy.context.object.pose.bones["c_ext_hair_01_01.x"].bone_group = bpy.context.active_object.pose.bone_groups['body.r'
        arp.pose.bones[l[0]].bone_group = arp.pose.bone_groups['body.l_sel'] #ボーングループを設定してカラー割り当て


    msg = '処理完了'
    bpy.ops.cyatools.messagebox('INVOKE_DEFAULT', message = msg)




#---------------------------------------------------------------------
#IKストレッチを無効化する
#---------------------------------------------------------------------
def disable_ikstretch():
    amt = utils.getActiveObj()
    utils.mode_p()
    for b in amt.pose.bones:
        for const in b.constraints:
            if const.type == 'IK':
                const.use_stretch = False



    msg = '処理完了 すべてのikStretchを無効化しました'
    bpy.ops.cyatools.messagebox('INVOKE_DEFAULT', message = msg)



#---------------------------------------------------------------------
#プロキシ関連ツール
#---------------------------------------------------------------------
def proxy_rig(mode):
    linkedObj = bpy.context.active_object
    col = linkedObj.instance_collection
    print(col.name)

    for o in col.objects:
        utils.act(linkedObj)
        bpy.ops.object.proxy_make(object=o.name)
        print(o.name)
        act = utils.getActiveObj()
        act.name = o.name
        