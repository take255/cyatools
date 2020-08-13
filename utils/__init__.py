from bpy.types import Panel
import bpy

class panel(Panel):   
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category ='cya'
    bl_options = {'DEFAULT_CLOSED'}

icon = {
    'OBJECT':'OBJECT_DATA',
    'ADD':'ADD',
    'REMOVE':'REMOVE',
    'UP':'TRIA_UP_BAR',
    'DOWN':'TRIA_DOWN_BAR',
    'CANCEL':'CANCEL',
    'SELECT':'RESTRICT_SELECT_OFF',
    'BONE':"BONE_DATA"
    }

def activeObj(ob):
     bpy.context.view_layer.objects.active = ob

def getActiveObj():
    return bpy.context.active_object
    
def select(ob,state):
     ob.select_set(state=state)

#シングルオブジェクトの選択とアクティブ化。それ以外のオブジェクトの選択解除
def act(ob):
     deselectAll()
     select(ob,True)
     activeObj(ob)

def actByName(obname):
     deselectAll()
     ob = bpy.data.objects[obname]
     ob.select_set(state=True)
     select(ob,True)
     activeObj(ob)

def delete(ob):
     bpy.ops.object.select_all(action='DESELECT')
     select(ob,True)
     bpy.ops.object.delete()

#---------------------------------------------------------------------------------------
#ボーン関連 edit mode
#---------------------------------------------------------------------------------------
def get_selected_bones():
     #ポーズモードなら
     if current_mode() == 'POSE':
          return bpy.context.selected_pose_bones
     elif current_mode() == 'EDIT':
          return bpy.context.selected_bones
     elif current_mode() == 'OBJECT':
          return []

def get_active_bone():
     #ポーズモードなら
     if current_mode() == 'POSE':
          return bpy.context.active_pose_bone
     elif current_mode() == 'EDIT':
          return bpy.context.active_bone
     elif current_mode() == 'OBJECT':
          return []



#選択をすべて解除して最後のオブジェクトをアクティブにする
def multiSelection(objarray):
     if len(objarray) == 0:return
     deselectAll()
     for ob in objarray:
          select(ob,True)

     activeObj(objarray[0])

def deselectAll():
     bpy.ops.object.select_all(action='DESELECT')

def selectByName(obname,state):
    bpy.data.objects[obname].select_set(state=state)

def objectByName(obname):
    return bpy.data.objects[obname]

def showhide(ob,state):
     bpy.data.objects[ob.name].hide_viewport = state

def sceneLink(ob):
     bpy.context.scene.collection.objects.link(ob)

def sceneUnlink(ob):
     bpy.context.scene.collection.objects.unlink(ob)

#パブリッシュシーンをアクティブに
def sceneActive(fix_scene):
     scn = bpy.data.scenes[fix_scene]
     bpy.context.window.scene = scn
     return scn

def selected():
    return bpy.context.selected_objects

#UV meshデータを入れると新規UVを返す
def UV_new(mesh_data):
     return mesh_data.uv_layers.new()

#カーソルを原点に
def cursorOrigin():
     bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
     bpy.context.scene.cursor.location = (0,0,0)

def mirrorBoneXaxis():
     bpy.ops.transform.mirror(orient_type='GLOBAL', constraint_axis=(True, False, False))


#マテリアル関連
#ノーマルマップイメージのカラースペース指定
def nmt_colorspace(node):
     node.image.colorspace_settings.name = 'Non-Color'


#マトリックスの掛け算
def m_mul(m0,m1):
     return m0 @ m1


#---------------------------------------------------------------------------------------
#モード
#---------------------------------------------------------------------------------------
def current_mode():
     return bpy.context.object.mode

def mode_e():
     bpy.ops.object.mode_set(mode = 'EDIT')

def mode_o():
     bpy.ops.object.mode_set(mode = 'OBJECT')

def mode_p():
     bpy.ops.object.mode_set(mode = 'POSE')


#---------------------------------------------------------------------------------------
#カーソル
#---------------------------------------------------------------------------------------
def init_cursor():
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)


#---------------------------------------------------------------------------------------
#リグのルートボーンを作成
#---------------------------------------------------------------------------------------
def rigroot():
     mode_e()
     root = 'rig_root'
     amt = bpy.context.object  
     if root not in amt.data.edit_bones:
          rootbone = amt.data.edit_bones.new(root)
          rootbone.head = (0,0,0)
          rootbone.tail = (0,0,1)

          #mode_p()
          #amt.pose.bones[root].use_deform = False
          amt.data.edit_bones[root].use_deform = False
     else:
          rootbone = amt.data.edit_bones[root]

     return rootbone

#---------------------------------------------------------------------------------------
#コレクション関連
#---------------------------------------------------------------------------------------
class collection:
     @classmethod
     def create( self , name ):          
          collection = bpy.context.scene.collection
          if name in [x.name for x in bpy.data.collections]:
               col = bpy.data.collections[name]
          else:
               col = bpy.data.collections.new(name)
               collection.children.link(col)
          return col

     # @classmethod
     # def get_obj( self ,col):
     #      return bpy.context.view_layer.active_layer_collection 

     @classmethod
     def get_active( self ):
          return bpy.context.view_layer.active_layer_collection 
     
     @classmethod
     def move_obj( self , ob , to_col):
          for col in ob.users_collection:
               col.objects.unlink(ob)
          to_col.objects.link(ob)

     @classmethod
     def move_obj_to_root( self , ob ):
          for col in ob.users_collection:
               col.objects.unlink(ob)
          bpy.context.scene.collection.objects.link(ob)


     @classmethod
     def move_col( self , collection ):
          current = bpy.context.window.scene.name
          for col in self.get_parent(collection):
               col.children.unlink(collection)               
          bpy.context.window.scene.collection.children.link(collection)

     @classmethod     
     def root(self):
          return bpy.context.scene.collection

     @classmethod     
     def children(self , col):
          pass

     @classmethod     
     def get_parent(self , col):
          result = []

          #マスターコレクションを調べる
          master = bpy.context.window.scene.collection
          c = master.children
          if col.name in [x.name for x in c]:
               result.append(master)

          #以外を調べる
          for c in bpy.data.collections:
               if col.name in [x.name for x in c.children]:
                    result.append(c)          
          return result

     @classmethod     
     def isMaster(self , col):
          master = bpy.context.window.scene.collection
          if col == master:
               return True
          else:
               return False           

     #colがカレントシーンにあるかどうか調べる
     @classmethod
     def exist(self , col):
          current_scn = bpy.context.window.scene
          exist = self.exist_loop( col , current_scn.collection ,False)
          return exist

     @classmethod
     def exist_loop( self , col  , current ,  exist ):
          children = current.children

          if children != None:
               for c in children:
                    if col.name == c.name:
                         exist = True

                    exist = self.exist_loop(col ,c, exist)

          return exist


class scene:
     #オブジェクトがあるシーンに移動する
     @classmethod
     def move_obj_scene(self , ob):
          for col in ob.users_collection:
               for scn in bpy.data.scenes:
                    #print( scn.name )
                    #print( scn.name , self.exist_loop( col , scn.collection ,False) )

                    if self.exist_loop( col , scn.collection ,False):
                         self.active(scn)

     @classmethod
     def exist_loop( self , col  , current ,  exist ):
          if col == current:
               exist = True

          children = current.children

          if children != None:
               for c in children:
                    if col.name == c.name:
                         exist = True

                    exist = self.exist_loop(col ,c, exist)

          return exist

     @classmethod
     def active(self , scn):
          bpy.context.window.scene = scn

     @classmethod
     def activebyname(self,scenename):
          scn = bpy.data.scenes[scenename]
          bpy.context.window.scene = scn
          return scn

     @classmethod
     def IsExistence(self,scenename):
          if scenename in [scn.name for scn in bpy.data.scenes]:
               return True
          else:
               return False




#---------------------------------------------------------------------------------------
#ボーン関連
#---------------------------------------------------------------------------------------
class bone:
     # Check the armature whether it is correct or not.
     # Armature rotation must be applied.
     @classmethod
     def check_correct(self):
          amt = bpy.context.object
          amt.rotation

     #選択ボーンを選択順にソート
     @classmethod
     def sort(self):
          result = []
          for bone in get_selected_bones():
               #print(b.name)
               count = 0
               b = bone
               while b != None:
                    b = b.parent
                    count += 1

               result.append([count,bone.name])
 
          result.sort()
          return [x[1] for x in result]

     @classmethod
     def get_selected_bones(self):
          #ポーズモードなら
          if current_mode() == 'POSE':
               return bpy.context.selected_pose_bones
          elif current_mode() == 'EDIT':
               return bpy.context.selected_bones
          elif current_mode() == 'OBJECT':
               return []

     @classmethod
     def get_active_bone(self):
          #ポーズモードなら
          if current_mode() == 'POSE':
               return bpy.context.active_pose_bone
          elif current_mode() == 'EDIT':
               return bpy.context.active_bone
          elif current_mode() == 'OBJECT':
               return []

     @classmethod
     def selectByName(self,obname,state):
          amt = bpy.context.object

          if current_mode() == 'EDIT':
               amt.data.edit_bones[obname].select = state
          elif current_mode() == 'POSE':
               mode_e()
               amt.data.edit_bones[obname].select = state
               mode_p()
          bpy.context.view_layer.update()