import bpy , bmesh
import imp

from . import utils
imp.reload(utils)


#Backsideというフェイスマップを選択する
def select_backside():
    
    for ob in utils.selected():
        utils.mode_o()
        mesh = ob.data

        print('--------------------------------------------')
        face_index = None
        for i,fmaps in enumerate(ob.face_maps):
            print(fmaps.name , fmaps.name.find('Backside'))
            if fmaps.name.find('Backside') != -1:
                face_index = i 
            
        #print(face_index)
        utils.mode_e()

        bm = bmesh.from_edit_mesh(mesh)
        fm = bm.faces.layers.face_map.verify()

        for face in bm.faces:
            face.select = False


        for face in bm.faces:
            face_idx = face.index    
            map_idx = face[fm]
            #print(f"face {face_idx}, map {map_idx}")
            
            if map_idx == face_index:
                face.select = True
            
