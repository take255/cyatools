import bpy
import imp
import math
from mathutils import ( Vector , Matrix )
import csv

from . import utils
imp.reload(utils)


#---------------------------------------------------------------------------------------
#ボーンの初期姿勢のコピー
#---------------------------------------------------------------------------------------

#コピー先、コピー元のボーンを選択(コピー元をアクティブ)、editモードに入り骨を選択。その後コマンドを実行
#最新版では複数のアーマチュアでエディットモードにはいれてしまう
#あらかじめコピー元のボーンを選択しておくのが正しいやり方な気がする
def copy_from_another():
    selected = utils.selected()

    for amt in selected:
        if amt == utils.getActiveObj():
            source = amt
        else:
            target = amt

    utils.mode_o()
    utils.act(source)
    utils.mode_e()
    selected = utils.get_selected_bones()

    dataarray = []
    for b in selected:
        #bone = amt.data.edit_bones[b.name]
        matrix = b.matrix
        dataarray.append( [ b.name , b.matrix ] )

        # head = Vector(bone.head)
        # vec = Vector(bone.tail) - head
        # length = vec.length/2
        # vec.normalize()
        # bone.tail = length * vec + head

    utils.mode_o()
    utils.act(target)
    utils.mode_e()

    for d in dataarray:
        bone = target.data.edit_bones[d[0]]
        bone.matrix = d[1]




#---------------------------------------------------------------------------------------
#長さ調整
#---------------------------------------------------------------------------------------

#最後に選択されたアクティブなボーンに長さをそろえる
def length_uniform():
    amt = bpy.context.object
    utils.mode_e()
    selected = utils.get_selected_bones()
    active = utils.get_active_bone()

    vec = Vector(active.head) - Vector(active.tail)
    length = vec.length

    for b in selected:
        bone = amt.data.edit_bones[b.name]
        vec = Vector(bone.head) - Vector(bone.tail)
        bone.tail = -(length/vec.length)*vec + bone.head

#選択されたボーンを全体の長さをキープしてそろえる
def length_uniform_all():
    amt = bpy.context.object
    utils.mode_e()
    selected = utils.get_selected_bones()
    #active = utils.get_active_bone()

    vec = Vector(selected[-1].tail) - Vector(selected[0].head)
    length = vec.length/len(selected)
    #num = len(selected)

    print(length)
    for b in selected:
        bone = amt.data.edit_bones[b.name]
        vec = Vector(bone.tail) - Vector(bone.head)
        bone.tail = (length/vec.length)*vec + bone.head




#選択されたボーンの長さを半分に
def length_half():
    amt = bpy.context.object
    utils.mode_e()
    selected = utils.get_selected_bones()

    for b in selected:
        bone = amt.data.edit_bones[b.name]
        head = Vector(bone.head)
        vec = Vector(bone.tail) - head
        length = vec.length/2
        vec.normalize()
        bone.tail = length * vec + head


#2つの骨を選択して実行。２つの骨の長さの割合を出す
def check_ratio():
    amt = bpy.context.object
    utils.mode_e()
    bones = utils.get_selected_bones()

    ratio = bones[0].length/bones[1].length
    print(ratio)

#---------------------------------------------------------------------------------------
#最初に選択したボーンの根本から、最後に選択したボーンの先端までのボーンを生成する
#---------------------------------------------------------------------------------------
def genarate_bone_from2():

    amt = bpy.context.object

    selected = utils.bone.sort()
    bone1 = amt.data.edit_bones[selected[0]]
    bone2 = amt.data.edit_bones[selected[1]]

    target = amt.data.edit_bones.new(bone1.name)
    target.head = bone1.head
    target.tail = bone2.tail
    target.roll = bone1.roll


#---------------------------------------------------------------------------------------
#選択したボーンの名前を取得、LR入れ替えた骨を探し　LRの候補を数種類使えるように改良
#最初か最後に識別子があるかどうかに限定する
#---------------------------------------------------------------------------------------
Lsign = ('L_' , '_l' , '.l' ,'_L','.L')
Rsign = ('R_' , '_r' , '.r' ,'_R','.R')

def genarate_symmetry(mode):
    if mode == 1:
        genarate_symmetry2()
        return

    props = bpy.context.scene.cyarigtools_props
    amt = bpy.context.active_object

    for bone in bpy.context.selected_bones:
        name = bone.name
        head = bone.head
        tail = bone.tail
        roll = bone.roll

        for L ,R in zip( Lsign , Rsign ):
            Exist = True

            if name[-2:] == L:
                newname = name[:-2] + R
            elif name[-2:] == R:
                newname = name[:-2] + L
            elif name[:2] == L:
                newname = R + name[2:]
            elif name[:2] == R:
                newname = L + name[2:]
            else:
                Exist = False

            if Exist:
                newbone = amt.data.edit_bones[newname]
                newbone.head = (-head[0],head[1], head[2])
                newbone.tail = (-tail[0],tail[1], tail[2])

                if not props.mirror_pos_only:

                    if props.axismethod == 'old':
                        newbone.roll = -roll + math.pi #反転したあと１８０°回転させる

                    elif props.axismethod == 'new':
                        newbone.roll = -roll


#---------------------------------------------------------------------------------------
#骨のミラーリング。LR識別が中間にある場合にこちらを使用
#---------------------------------------------------------------------------------------
Lsign2 = ('_L_' , '_l_')
Rsign2 =  ('_R_' , '_r_')
def genarate_symmetry2():
    props = bpy.context.scene.cyarigtools_props

    amt = bpy.context.active_object

    for bone in bpy.context.selected_bones:
        name = bone.name
        head = bone.head
        tail = bone.tail
        roll = bone.roll

        for L ,R in zip( Lsign2 , Rsign2 ):
            Exist = True

            if name.find(L) != -1:
                newname = name.replace(L,R)
            else:
                Exist = False

            if Exist:
                newbone = amt.data.edit_bones[newname]
                newbone.head = (-head[0],head[1], head[2])
                newbone.tail = (-tail[0],tail[1], tail[2])

                if props.axismethod == 'old':
                    newbone.roll = -roll + math.pi #反転したあと１８０°回転させる

                elif props.axismethod == 'new':
                    newbone.roll = -roll


#---------------------------------------------------------------------------------------
#Bone direction
#---------------------------------------------------------------------------------------

#ジョイント向きを近いグローバルの軸に合わせる用定数
AXIS ={'x':(1,0,0),'y':(0,1,0),'z':(0,0,1)}

def Normal2bone(bone1,bone2):
    va = []
    #ボーンのベクトルを求め法線を割り出す
    for bone in (bone1,bone2):
        bone.roll = 0 #ボーンのロールを０にする
        v0 = Vector(bone.head) - Vector(bone.tail)
        v0.normalize()
        va.append(v0)

    nor = va[0].cross(va[1])
    nor.normalize()
    return nor


#平面の法線からボーンのロールを修正する
def AdjustRoll(bone,nor):
    props = bpy.context.scene.cyarigtools_props
    mat = bone.matrix

    z = Vector((mat[0][2],mat[1][2],mat[2][2]))
    z.normalize()

    #Xvectorを回転の正負判定に使う
    #Ｘ軸と法線の内積が正なら＋、負ならー
    x = Vector((mat[0][0],mat[1][0],mat[2][0]))
    sign= x.dot(nor)/math.fabs(x.dot(nor))

    cos_sita= z.dot(nor)
    sita = math.acos( cos_sita );

    if props.axismethod == 'old':
        bone.roll = sita*sign

    elif props.axismethod == 'new':
        bone.roll = sita*sign + math.pi/2


#平面の法線からボーンのロールを修正する
#axis_planeプロパティをもとに計算
def AdjustRoll_axisplane(bone,nor):
    props = bpy.context.scene.cyarigtools_props
    mat = bone.matrix

    z = Vector((mat[0][2],mat[1][2],mat[2][2]))
    z.normalize()

    #Xvectorを回転の正負判定に使う
    #Ｘ軸と法線の内積が正なら＋、負ならー
    x = Vector((mat[0][0],mat[1][0],mat[2][0]))
    sign= x.dot(nor)/math.fabs(x.dot(nor))

    cos_sita= z.dot(nor)
    sita = math.acos( cos_sita );

    if props.axis_plane == 'Z':
        bone.roll = sita*sign

    elif props.axis_plane == 'X':
        bone.roll = sita*sign + math.pi/2



class VecComp:
    def __init__(self,axis,vec):
        self.axis = axis
        d = Vector(AXIS[axis]).dot(vec)
        self.dot =abs(d)

        if self.dot != 0:
            self.sign = d/self.dot
        else:
            self.sign = 1

    def __repr__(self):
        """
        representaion method
        """
        return self.axis


#---------------------------------------------------------------------------------------
#アクティブなボーンに位置をあわせる
#---------------------------------------------------------------------------------------
def align_position():
    selected = [x.name for x in utils.get_selected_bones() ]
    act = utils.get_active_bone().name
    amt=bpy.context.object
    utils.mode_e()

    if len(selected ) > 0 :

        for b in selected:
            bone = amt.data.edit_bones[b]
            bone.head = amt.data.edit_bones[act].head

#---------------------------------------------------------------------------------------
#アクティブなボーンに向きをあわせる
#アクティブなボーンに向きをあわせる ただしロールはそのまま
#---------------------------------------------------------------------------------------
def align_direction(mode):
    selected = [x.name for x in utils.get_selected_bones() ]
    act_name = utils.get_active_bone().name
    amt=bpy.context.object
    utils.mode_e()

    act = amt.data.edit_bones[act_name]
    matrix = Matrix(act.matrix)

    if len(selected ) > 0 :
        for bonename in selected:
            tgt = amt.data.edit_bones[bonename]
            head = Vector(tgt.head)
            tgt.matrix = matrix
            roll = tgt.roll

            l = tgt.length
            vec = Vector(act.tail)-Vector(act.head)
            vec.normalize()

            tgt.head = head
            tgt.tail = Vector(tgt.head) +vec * l

            if mode == 1:
                tgt.roll = roll



#---------------------------------------------------------------------------------------
#アクティブボーン上にそれ以外のボーンを並べる
#元ボーンのベクトルはheadとtailからもとめられる
#ターゲットボーンの近接点は元ボーンの単位ベクトルとの内積で求められる。
#---------------------------------------------------------------------------------------
def align_along():
    act_name = utils.get_active_bone().name
    selected = [x.name for x in utils.get_selected_bones() if x.name != act_name]
    amt=bpy.context.object
    utils.mode_e()

    act = amt.data.edit_bones[act_name]
    p = Vector( act.head )
    vec_act = Vector(act.tail) - p
    vec_act.normalize()

    for b in selected:
        bone = amt.data.edit_bones[b]
        a = Vector(bone.head)
        tail = Vector(bone.tail - bone.head)
        bone.head =p + vec_act * (a - p).dot( vec_act )
        bone.tail =bone.head + tail


#---------------------------------------------------------------------------------------
#近いグローバル軸に向ける
#---------------------------------------------------------------------------------------
def align_near_axis():
    selected = [x.name for x in utils.get_selected_bones()]
    amt=bpy.context.object
    utils.mode_e()

    for b in selected:
        bone = amt.data.edit_bones[b]
        v = Vector(bone.tail - bone.head)
        v.normalize()

        foolist = [ VecComp('x',v), VecComp('y',v), VecComp('z',v)]

        ax = max(foolist, key=lambda x:x.dot)
        vec = bone.length*ax.sign*Vector(AXIS[ax.axis])
        bone.tail = bone.head
        bone.tail += vec


#---------------------------------------------------------------------------------------
#２ボーンの平面を出して軸向きを合わせる
#ポールベクター設定の前処理
#根本、先の順に2軸を選択する。選択はリストで行う。
#2番目に選択される骨にＩＫが設定されている
#---------------------------------------------------------------------------------------
def along_2axis_plane():
    selected = utils.bone.sort()

    # selected = [x.name for x in utils.get_selected_bones()]
    amt = bpy.context.object

    utils.mode_e()

    bone1 = amt.data.edit_bones[selected[0]]
    bone2 = amt.data.edit_bones[selected[1]]

    nor = Normal2bone(bone1,bone2)

    #デバッグ用ボーン-----
##        b = amt.data.edit_bones.new('ctr.Bone')
##        b.head = Vector(bone.head)
##        b.tail = Vector(bone.head) + nor
    #デバッグ用ボーン----- ここまで

    #平面の法線からボーンのロールを修正する
    AdjustRoll_axisplane(bone1,nor)
    AdjustRoll_axisplane(bone2,nor)



#---------------------------------------------------------------------------------------
#２ボーンの平面を出して軸向きを合わせる
#平面の法線からボーン先端の最近点を求める
#---------------------------------------------------------------------------------------
def align_on_plane():
    #selected = [x.name for x in utils.get_selected_bones()]
    selected = utils.bone.sort()
    amt = bpy.context.object
    utils.mode_e()

    bone1 = amt.data.edit_bones[selected[0]]
    bone2 = amt.data.edit_bones[selected[1]]

    nor = Normal2bone( bone1 , bone2 )

    #３本目からのボーンの先端を平面に合わせていく
    #必要な値：
    # 平面上の１点 Vector(bone[0].head)
    # 法線 nor
    # 先端位置 Vector(bone.tail)

    # 平面上の最近点 = A - N * ( PA ・ N )
    # A 先端位置
    # N 面法線
    # P 平面上の点
    # PA・N　内積

    p = bone1.head

    for b in selected[2:]:
        bone = amt.data.edit_bones[b]
        a = Vector(bone.tail)
        pos =a + nor * (p - a).dot(nor)
        bone.tail = pos

    #平面の法線からボーンのロールを修正する
    for b in selected:
        bone = amt.data.edit_bones[b]
        AdjustRoll_axisplane(bone,nor)


#---------------------------------------------------------------------------------------
#最初のheadと最後のtailを含む平面の法線を割り出し、中間の関節をその平面の最近点に移動する
#選択順が必要なのでポーズモードで
#---------------------------------------------------------------------------------------
def align_at_flontview():
    #props = bpy.context.scene.cyarigtools_props
    #selected = [x.name for x in props.allbones ]
    amt = bpy.context.object
    utils.mode_e()

    selected = utils.bone.sort()
    bone1 = amt.data.edit_bones[selected[0]]
    bone2 = amt.data.edit_bones[selected[-1]]

    #法線を割り出す　normal.y = 0
    #vecのｘ、ｚを入れ替えればよい(どちらかにー符号をつける)
    vec0 = Vector(bone1.head) - Vector(bone2.tail)
    nor = Vector((vec0.z ,0 ,-vec0.x) )
    nor.normalize()

    p = Vector(bone1.head)

    for b in selected[1:]:
        bone = amt.data.edit_bones[b]
        a = Vector(bone.head)
        pos =a + nor * (p - a).dot(nor)
        bone.head = pos


#---------------------------------------------------------------------------------------
#ロール値をボーン平面に合わせて修正。
#複数のボーンを同時に修正がどうしてもうまくいかない。
#なので、妥協案として2本づつおこなう
#選択はポーズモードで
#---------------------------------------------------------------------------------------
def adjust_roll():
    props = bpy.context.scene.cyarigtools_props
    amt = bpy.context.object
    selected = [x.name for x in props.allbones ]
    utils.mode_e()

    bone1 = amt.data.edit_bones[selected[0]]
    bone2 = amt.data.edit_bones[selected[1]]

    nor = Normal2bone(bone1,bone2)

    #平面の法線からボーンのロールを修正する
    AdjustRoll(bone1,nor)
    AdjustRoll(bone2,nor)


def roll_degree(op):
    for bone in bpy.context.selected_bones:
        if op == '90d':
            bone.roll += math.pi/2
        if op == '-90d':
            bone.roll -= math.pi/2
        if op == '180d':
             bone.roll += math.pi

#平面に投影　単純にtailの値をheadに合わせる
def projection(op):
    for bone in bpy.context.selected_bones:
        head = Vector(bone.head)
        tail = Vector(bone.tail)
        if op == 'xy':
            bone.tail = Vector((tail[0],tail[1],head[2]))
        if op == 'yz':
            bone.tail = Vector((head[0],tail[1],tail[2]))
        if op == 'zx':
            bone.tail = Vector((tail[0],head[1],tail[2]))



def axis_swap(axis):
    props = bpy.context.scene.cyarigtools_props

    for bone in utils.get_selected_bones():
        #mat = bone.matrix
        head = Vector(bone.head)
        matrix = bone.matrix.to_3x3()
        matrix.transpose()

        if axis == 'x':
            x =  matrix[0]
            y =  matrix[2]
            z = -matrix[1]

        elif axis == 'y':
            x =  matrix[2]
            y =  matrix[1]
            z =  -matrix[0]

        elif axis == 'z':
            x =  matrix[1]
            y = -matrix[0]
            z =  matrix[2]

        elif axis == 'invert':
            x = -matrix[0]
            y = -matrix[1]
            z = -matrix[2]


        m = Matrix((x,y,z))

        m.transpose()
        bone.matrix = m.to_4x4()

        tail = Vector(bone.tail)

        bone.head = head
        bone.tail = head + tail


#---------------------------------------------------------------------------------------
#ロールをグローバル平面上にそろえる
# ラジオボタンで選択
# ボーン軸(X,Z)　グローバル軸　(x,y,z,x,y,z)
#y軸とグローバル軸の外積から直行するベクトルをだし、そのベクトルとY軸との外積でグローバル軸に沿ったベクトルを割り出す
#---------------------------------------------------------------------------------------
def align_roll_global():
    bpy.ops.object.mode_set(mode = 'EDIT')
    for bone in bpy.context.selected_bones:
        m = Matrix(bone.matrix)
        m.transpose()
        y_axis = Vector(m[1][:-1])

        #グローバル軸との外積
        vec0 = y_axis.cross(Vector((0,0,1.0)))
        vec1 = y_axis.cross(vec0)
        new_m = Matrix(( (vec0[0],vec0[1],vec0[2],0.0) ,(y_axis[0],y_axis[1],y_axis[2],0.0),(vec1[0],vec1[1],vec1[2],0.0) ,m[3]))

        new_m.transpose()

        bone.matrix = new_m


#---------------------------------------------------------------------------------------
#コンストレイン
#---------------------------------------------------------------------------------------
def constraint_cleanup():
    for bone in bpy.context.selected_pose_bones:
        for const in bone.constraints:
            bone.constraints.remove( const )

def constraint_cleanup_empty():
    for bone in bpy.context.selected_pose_bones:

        for const in bone.constraints:
            isempty = False

            if hasattr(const, 'target'):
                if const.target is None:
                    isempty = True

            if hasattr(const, 'subtarget'):
                if const.subtarget == '':
                    isempty = True

            const.driver_remove('influence')
            if isempty is True:
                bone.constraints.remove( const )

def constraint_showhide(self,state):
    for bone in bpy.context.selected_pose_bones:
        for const in bone.constraints:
            const.mute = self.const_disp_hide

def constraint_change_influence(self,context):
    bpy.ops.object.mode_set(mode = 'POSE')
    for bone in bpy.context.selected_pose_bones:
        for const in bone.constraints:
            const.influence = self.const_influence

#---------------------------------------------------------------------------------------
#connect chain
#---------------------------------------------------------------------------------------
def connect_chain():
    utils.mode_e()
    for b in utils.bone.get_selected_bones():
        b.use_connect = True

#---------------------------------------------------------------------------------------
#delete rig
#---------------------------------------------------------------------------------------
def delete_rig_loop(bone,root):
    p = bone.parent
    if p == None:
        return False

    elif p.name == root:
        return True

    else:
        return delete_rig_loop(p,root)



def delete_rig():
    utils.mode_p()
    bpy.context.object.data.layers[8] = True

    amt = bpy.context.object
    root = 'rig_root'


    #delete all driver
    utils.mode_p()
    for b in amt.pose.bones:
        b.driver_remove("ik_stretch")
        for c in b.constraints:
            c.driver_remove("influence")
            b.constraints.remove( c )


    utils.mode_e()
    bpy.ops.armature.select_all(action='DESELECT')

    result = []
    for b in amt.data.edit_bones:
        if delete_rig_loop( b , root ):
            result.append(b)


    for b in result:
        b.select = True

    bpy.ops.armature.delete()


#---------------------------------------------------------------------------------------
# add bones at the selected objects
#---------------------------------------------------------------------------------------
class AddBoneObj():
    def __init__( self , ob ):
        m = Matrix(ob.matrix_world)
        m.transpose()
        self.x = [ m[0][0], m[0][1], m[0][2] ]
        self.y = [ m[1][0], m[1][1], m[1][2] ]
        self.z = Vector([ m[2][0], m[2][1], m[2][2] ])
        self.head = Vector([ m[3][0], m[3][1], m[3][2] ])

        self.name = ob.name

        self.axis_forward = {}

        self.axis_forward['X']  = Vector([ m[0][0], m[0][1], m[0][2] ])
        self.axis_forward['-X'] = Vector([ -m[0][0], -m[0][1], -m[0][2] ])
        self.axis_forward['Y']  = Vector([ m[1][0], m[1][1], m[1][2] ])
        self.axis_forward['-Y'] = Vector([ -m[1][0], -m[1][1], -m[1][2] ])
        self.axis_forward['Z'] = Vector([ m[2][0], m[2][1], m[2][2] ])
        self.axis_forward['-Z']  = Vector([ -m[2][0], -m[2][1], -m[2][2] ])


def add_bone():
    props = bpy.context.scene.cyarigtools_props
    amt = utils.getActiveObj()

    af = props.axis_forward
    au = props.axis_up

    m_array = []
    for ob in utils.selected():
        if ob != amt:
            m_array.append( AddBoneObj(ob) )

    utils.act(amt)
    utils.mode_e()

    for m in m_array:
        b = amt.data.edit_bones.new( m.name )
        b.head = m.head
        b.tail = m.head + m.axis_forward[ af ]
        print(m.axis_forward[ af ])
        bpy.ops.armature.select_all(action='DESELECT')


# First, select object next select armature. Enter edit mode and select bone to align.
def snap_bone_at_obj():
    amt = utils.getActiveObj()
    bone = utils.get_active_bone()

    for ob in utils.selected():
        if ob != amt:
            loc = ob.location

    bone.head = loc

#---------------------------------------------------------------------------------------
#Faceitから骨を移行する
#  キャラボーン　faceit の順で２つ選択 (faceitをアクティブに)
# csvに従って骨生成
# 骨名、ルート用位置骨、head or tail、テール用位置骨、root or tail、親骨
#eye_l , master_eye.L , head , master_eye.L , tail , head
#E:/data/dcctools/blender/2.91/scripts/addons/cyatools/data/faceit2ingame.csv
#---------------------------------------------------------------------------------------
class BoneData:
    name = ""
    headbone = ""
    head_pos = ""
    tailbone = ""
    tail_pos = ""
    parent = ""

    def __init__(self,row):
        print(row)
        self.name = row[0]
        self.headbone = row[1]
        self.head_pos = row[2]
        self.tailbone = row[3]
        self.tail_pos = row[4]
        self.parent = row[5]

    def get_coord(self,amt):

        utils.mode_o()
        loc = amt.location

        utils.mode_e()
        headbone = amt.data.edit_bones[self.headbone]


        if self.head_pos == "head":
            self.head = headbone.head + loc

        elif self.head_pos == "tail":
            self.head = headbone.tail+ loc

        tailbone = amt.data.edit_bones[self.tailbone]

        if self.tail_pos == "head":
            self.tail =  tailbone.head+ loc

        elif self.tail_pos == "tail":
            self.tail =  tailbone.tail+ loc


        print(self.head)
        print(self.tail)
        utils.mode_o()

    #存在している骨はnewしない
    def generate(self,amt):
        utils.mode_e()

        if self.name in amt.data.edit_bones:
            b = amt.data.edit_bones[self.name]
        else:
            b = amt.data.edit_bones.new( self.name )

        b.parent = amt.data.edit_bones[self.parent]
        b.head = self.head
        b.tail = self.tail


#---------------------------------------------------------------------------------------
#骨をコピーして別の骨に複製する
#---------------------------------------------------------------------------------------
def bone_copy_with_csv(path):

    #path = "E:/data/dcctools/blender/2.91/scripts/addons/cyatools/data/faceit2ingame.csv"

    bdataarray = []
    with open( path ) as f:
        reader = csv.reader(f)
        for row in reader:
            bdata = BoneData(row)

            bdataarray.append(bdata)
            #dic[row[0]] = row[1]


    selected = utils.selected()

    for amt in selected:
        if amt == utils.getActiveObj():
            faceit = amt
        else:
            target = amt



    utils.act(faceit)

    for bdata in bdataarray:
        bdata.get_coord(faceit)


    utils.act(target)

    for bdata in bdataarray:
        bdata.generate(target)


#---------------------------------------------------------------------------------------
#CSVに骨名を出力する
#---------------------------------------------------------------------------------------
def export_bonelist(path):

    amt = bpy.context.object

    utils.mode_p()
    result = [[b.name,] for b in amt.pose.bones]

    with open(path, 'w' , newline = "") as f:
        writer = csv.writer(f)
        writer.writerows(result)

    utils.mode_o()



#---------------------------------------------------------------------------------------
#CSV変換テーブルを使って骨をリネーム
#---------------------------------------------------------------------------------------
def rename_bone_with_csv(path):

    amt = bpy.context.object

    utils.mode_p()
    for b in amt.pose.bones:
        print(b.name)

    #辞書として読み込む
    dic = {}
    with open( path ) as f:
        reader = csv.reader(f)
        for row in reader:
            dic[row[0]] = row[1]
            print(row)

    amt = utils.getActiveObj()

    #辞書に含まれていたらリネームする
    for bone in  amt.pose.bones:
        if bone.name in dic:
            bone.name = dic[bone.name]



#---------------------------------------------------------------------------------------
#リネーム
#---------------------------------------------------------------------------------------

#プレフィックスの削除
def bone_rename_delete_prefix():

    act_name = utils.get_active_bone().name
    selected = [x.name for x in utils.get_selected_bones() if x.name != act_name]
    amt=bpy.context.object
    utils.mode_e()

    for b in selected:
        bone = amt.data.edit_bones[b]
        n = bone.name
        buf = n.split(':')
        print(buf[-1])
        bone.name = buf[-1]
