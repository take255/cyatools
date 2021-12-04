import bpy
import imp
import os
import glob
import shutil
from pathlib import Path
import datetime
import pickle


# from bpy.types import ( PropertyGroup , Panel , Operator ,UIList)
# from bpy.props import ( FloatVectorProperty , )

from . import utils
imp.reload(utils)


MODE = ('svn','work','backup','onedrive')

#パスの状態を読み込む
def load_sceneManagerData():
    prop,ui_list,itemlist = getprop()
    filename = os.path.join(os.path.join(os.environ['USERPROFILE']), r'Documents\Cyatools\sceneManagerPath.pkl')

    if os.path.exists(filename):
        f = open(  filename  ,'rb')
        dat = pickle.load( f )
        f.close()

        return dat[0]


def save_sceneManagerData(data):
    filename = os.path.join(os.path.join(os.environ['USERPROFILE']), r'Documents\Cyatools\sceneManagerPath.pkl')
    f = open( filename, 'wb' )
    pickle.dump( data, f ,protocol=0)
    f.close()


#---------------------------------------------------------------------------------------
#Popup Error Message
#---------------------------------------------------------------------------------------
# def msg01(self, context):
#     layout= self.layout
#     layout.label(text= "The selected object doesn't have a vertex color.")

# def msg02(self, context):
#     layout= self.layout
#     layout.label(text= "You must select a face.")



def selection_changed(self, context):
    prop,ui_list,itemlist = getprop()
    index = ui_list.active_index
    #newpath = os.path.join( prop.current_dir , itemlist[index].name )

    #prop = bpy.context.scene.cyascenemanager_oa
    #ui_list = bpy.context.window_manager.cyascenemanager_list
    #print(ui_list.active_index)

    prop.selected_file = itemlist[index].name


#【ファイル操作】：ワークディレクトリとバックアップフォルダを作成
def make_workdir():
    prop = bpy.context.scene.cyascenemanager_oa

    os.makedirs( prop.work_dir , exist_ok=True )
    os.makedirs( prop.backup_dir , exist_ok=True )

#廃止予定
def showhide(self, value):
    pass

def getprop():
    prop = bpy.context.scene.cyascenemanager_oa
    ui_list = bpy.context.window_manager.cyascenemanager_list
    itemlist = ui_list.itemlist

    return prop,ui_list,itemlist

#相対パスを返す
#先頭はルートなので削除する
def relative():
    prop = bpy.context.scene.cyascenemanager_oa
    parts = Path(prop.relative_path).parts
    return parts[1:]


#【ファイル操作】：Blenderファイルを開く
def open_file():
    prop,ui_list,itemlist = getprop()
    index = ui_list.active_index
    newpath = os.path.join( prop.current_dir , itemlist[index].name )

    bpy.ops.wm.open_mainfile(filepath=newpath)


#【ファイル操作】：リストで選択したファイルを上書き保存
def save_file():
    prop,ui_list,itemlist = getprop()
    #index = ui_list.active_index
    newpath = os.path.join( prop.current_dir , prop.selected_file )

    bpy.ops.wm.save_as_mainfile(filepath = newpath ,copy = False )

#【ファイル操作】：チェックついているファイルをコピー、もしくは移動
def move(mode):
    print("aaaa")
    prop,ui_list,itemlist = getprop()
    # ui_list = bpy.context.window_manager.cyascenemanager_list
    # itemlist = ui_list.itemlist

#    prop = bpy.context.scene.cyascenemanager_oa
    target = prop.copy_target


    if target == 'svn':
        root = prop.svn_root
    elif target == 'work':
        root = prop.work_root
    elif target == 'backup':
        root = prop.backup_root
    elif target == 'onedrive':
        root = prop.onedrive_root


    filearray = []
    for node in itemlist:
        if node.bool_val == True:
            filearray.append(node.name)

    dst_dir = os.path.join( root , prop.relative_path)
    os.makedirs(dst_dir, exist_ok=True )

    print(filearray)
    for file in filearray:
        src = os.path.join( prop.current_dir , file )

        #相対パスを出す
        dst = os.path.join( dst_dir , file )

        #print(Path(prop.relative_path).parts)
        # if mode == 'svn':
        #     dst = os.path.join( prop.svn_dir , file )
        # elif mode == 'work':
        #     dst = os.path.join( prop.work_dir , file )
        # elif mode == 'backup':
        #     dst = os.path.join( prop.backup_dir , file )


        print(src,dst)
        if mode == 'copy':
            shutil.copy(src , dst)
        elif mode == 'move':
            shutil.move(src , dst)


    reload( prop.current_dir )


#【ファイル操作】：バックアップパスにファイル名＋日付　でSave Copy
#現在ひらいているシーンをバックアップする
def save_backup():
    prop = bpy.context.scene.cyascenemanager_oa
    filepath = bpy.data.filepath

    basename = os.path.basename(filepath)
    buf = os.path.splitext(basename)

    now = datetime.datetime.now()
    newfilename = f'{buf[0]}_BackUp_{now:%y%m%d_%H%M}.blend'

    newpath = os.path.join( prop.backup_dir , newfilename )

    print(newpath)
    bpy.ops.wm.save_as_mainfile(filepath = newpath ,copy = True )


#oneDriveに源蔵
# def save_onedrive():
#     prop = bpy.context.scene.cyascenemanager_oa
#     filepath = bpy.data.filepath

#     basename = os.path.basename(filepath)
#     buf = os.path.splitext(basename)

#     now = datetime.datetime.now()
#     newfilename = f'{buf[0]}_BackUp_{now:%y%m%d_%H%M}.blend'

#     newpath = os.path.join( prop.backup_dir , newfilename )

#     print(newpath)
#     bpy.ops.wm.save_as_mainfile(filepath = newpath ,copy = True )



#【ファイル操作】：テクスチャの読み込み
#アクティブなマテリアルにテクスチャノードを追加する
def load_textures():
    prop,ui_list,itemlist = getprop()

    filearray = []
    for node in itemlist:
        if node.bool_val == True:
            filearray.append(node.name)

    imgarray = []
    for file in filearray:
        filepath = os.path.join( prop.current_dir , file )
        img = bpy.data.images.load(filepath, check_existing=False)
        imgarray.append(img)
        print(filepath)


    for image in bpy.data.images:
        image.reload()


    #マテリアルにイメージ読み込み
    mat = bpy.context.active_object.active_material
    nodes = mat.node_tree.nodes

    for i,img in enumerate(imgarray):
        tex = nodes.new(type='ShaderNodeTexImage')
        tex.image = img
        img.colorspace_settings.name = 'sRGB' #カラースペースをsRGBに強制
        tex.location.x = -500
        tex.location.y = 100*i



#ここでさまざまなパスを設定してしまう
#新規にBlenderを立ち上げたときに空シーンを開くので、そのタイミングで保存したシーンパスを読み込む
def setproject():
    prop = bpy.context.scene.cyascenemanager_oa
    filepath = os.path.dirname( bpy.data.filepath )

    #パスが空の場合は保存してあったパスを読み込む
    if filepath =='':
        filepath = load_sceneManagerData()

    rel_dir = ''
    #ルート以下の相対パスを抽出
    for root,mode in zip(( prop.svn_root , prop.work_root , prop.backup_root , prop.onedrive_root ) , MODE ):
        if filepath.find( root ) != -1:
            rel_dir = filepath.replace( root , '' )
            prop.relative_path = rel_dir[1:]#最初の￥を削除
            prop.switch_path = mode


    if rel_dir != '':
        prop.svn_dir = prop.svn_root + rel_dir
        prop.work_dir = prop.work_root + rel_dir
        prop.backup_dir = prop.backup_root + rel_dir
        prop.onedrive_dir = prop.onedrive_root + rel_dir

    make_workdir()

    reload( filepath )


#リストにカレントファルダのファイルを追加
def reload(filepath):
    prop = bpy.context.scene.cyascenemanager_oa
    ui_list = bpy.context.window_manager.cyascenemanager_list
    itemlist = ui_list.itemlist

    prop.current_dir = filepath

    make_workdir()

    #リストにファイルを登録
    files = glob.glob( f"{filepath}/*" )
    itemlist.clear()

    for file in files:
        basename = os.path.basename(file)
        item = itemlist.add()
        item.name = basename

        if os.path.isdir(file):
            item.filetype = 'dir'

        else:
            if basename.find('blend') != -1:
                item.filetype = 'blend'

            elif basename.find('TGA') != -1:
                item.filetype = 'image'

            elif basename.find('png') != -1:
                item.filetype = 'image'

            else:
                item.filetype = ''

        ui_list.active_index = len(itemlist) - 1

    save_sceneManagerData([filepath])



#フォルダ変更】：ワークフォルダにスイッチ
def switch_path(self, context):
    prop,ui_list,itemlist = getprop()
    mode = prop.switch_path
    #switch_work()
    prop = bpy.context.scene.cyascenemanager_oa

    if mode == 'svn':
        reload(prop.svn_dir)
        prop.current_root = prop.svn_root

    elif mode == 'work':
        reload(prop.work_dir)
        prop.current_root = prop.work_root

    elif mode == 'backup':
        reload(prop.backup_dir)
        prop.current_root = prop.backup_root

    elif mode == 'onedrive':
        reload(prop.onedrive_dir)
        prop.current_root = prop.onedrive_root


#削除予定
#【フォルダ変更】：ワークフォルダにスイッチ
def switch_work(mode):
    prop = bpy.context.scene.cyascenemanager_oa

    if mode == 'svn':
        reload(prop.svn_dir)
        prop.current_root = prop.svn_root

    elif mode == 'work':
        reload(prop.work_dir)
        prop.current_root = prop.work_root

    elif mode == 'backup':
        reload(prop.backup_dir)
        prop.current_root = prop.backup_root



    # prop.current_dir = targetdir

    # print(targetdir)
    # #make_workdir()

    # files = glob.glob( f"{targetdir}/*.blend" )


    # itemlist.clear()

    # for file in files:
    #     basename = os.path.basename(file)
    #     item = itemlist.add()
    #     item.name = basename
    #     ui_list.active_index = len(itemlist) - 1




#【ディレクトリ操作】：１階層上のフォルダに移動
def go_up_dir():
    prop = bpy.context.scene.cyascenemanager_oa
    path = Path(prop.current_dir)#この段階で最下層のディレクトリは除外される（最下層がファイルとみなされるので）

    rel_path = Path(prop.relative_path)
    print(str(rel_path))
    prop.relative_path =str(rel_path.parents[0])


    prop.current_dir = str(path.parents[0])
    reload( prop.current_dir )


#【ディレクトリ操作】：選択フォルダに移動
def go_down_dir(mode,name):
    prop = bpy.context.scene.cyascenemanager_oa

    if mode == 'dir':
        prop.current_dir = os.path.join( prop.current_dir , name )
        reload( prop.current_dir )

        rel_path = os.path.join( prop.relative_path , name )
        prop.relative_path =rel_path





