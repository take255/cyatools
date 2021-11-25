import bpy
import imp
import os
import glob
import shutil
from pathlib import Path
import datetime


# from bpy.types import ( PropertyGroup , Panel , Operator ,UIList)
# from bpy.props import ( FloatVectorProperty , )

from . import utils
imp.reload(utils)



#---------------------------------------------------------------------------------------
#Popup Error Message
#---------------------------------------------------------------------------------------
def msg01(self, context):
    layout= self.layout
    layout.label(text= "The selected object doesn't have a vertex color.")

def msg02(self, context):
    layout= self.layout
    layout.label(text= "You must select a face.")




#【ファイル操作】：ワークディレクトリとバックアップフォルダを作成
def make_workdir():
    prop = bpy.context.scene.cyascenemanager_oa
    os.makedirs( prop.work_dir , exist_ok=True )
    os.makedirs( prop.backup_dir , exist_ok=True )

#廃止予定
def showhide(self, value):
    pass

#【ファイル操作】：Blenderファイルを開く
def open_file():
    prop = bpy.context.scene.cyascenemanager_oa
    ui_list = bpy.context.window_manager.cyascenemanager_list
    itemlist = ui_list.itemlist

    index = ui_list.active_index
    newpath = os.path.join( prop.current_dir , itemlist[index].name )

    bpy.ops.wm.open_mainfile(filepath=newpath)


#【ファイル操作】：チェックついているファイルをコピー、もしくは移動
def move(mode):
    prop = bpy.context.scene.cyascenemanager_oa
    target = prop.copy_target


    if target == 'svn':
        root = prop.svn_dir
    elif target == 'work':
        root = prop.work_dir
    elif target == 'backup':
        root = prop.backup_dir


    ui_list = bpy.context.window_manager.cyascenemanager_list
    itemlist = ui_list.itemlist

    filearray = []
    for node in itemlist:
        if node.bool_val == True:
            filearray.append(node.name)

    for file in filearray:
        src = os.path.join( prop.current_dir , file )

        #相対パスを出す
        os.makedirs( os.path.join( root , prop.relative_path ) , exist_ok=True )
        dst = os.path.join( root , prop.relative_path , file )

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



#ここでさまざまなパスを設定してしまう
def setproject():
    prop = bpy.context.scene.cyascenemanager_oa
    filepath = os.path.dirname( bpy.data.filepath )

    rel_dir = ''
    #ルート以下の相対パスを抽出
    for root in ( prop.svn_root , prop.work_root , prop.backup_root ):
        if filepath.find( root ) != -1:
            rel_dir = filepath.replace( root , '' )
            #prop.current_root = root
            prop.relative_path = rel_dir


    print('rel_dir>' , rel_dir)

    if rel_dir != '':
        prop.svn_dir = prop.svn_root + rel_dir
        prop.work_dir = prop.work_root + rel_dir
        prop.backup_dir = prop.backup_root + rel_dir

    make_workdir()

    reload( filepath )


#リストにカレントファルダのファイルを追加
def reload(filepath):
    prop = bpy.context.scene.cyascenemanager_oa
    ui_list = bpy.context.window_manager.cyascenemanager_list
    itemlist = ui_list.itemlist

    prop.current_dir = filepath
    print('current', prop.current_dir)

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
    prop.relative_path =str(rel_path.parents[0])
    print(str(rel_path.parents[0]))


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
        print(rel_path)



