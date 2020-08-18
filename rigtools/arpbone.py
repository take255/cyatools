
#--------------------------------------------------------
# Auto Rig Pro <> UE4
#--------------------------------------------------------
ue4 = {
'root.x':'pelvis',
'spine_01.x':'spine_01',
'spine_02.x':'spine_02',
'spine_03.x':'spine_03',
'neck.x':'neck_01',
'head.x':'head',

'shoulder.r':'clavicle_r',
'c_arm_twist_offset.r':'upperarm_r',
'arm_stretch.r':'upperarm_twist_01_r',
'forearm_stretch.r':'lowerarm_r',
'forearm_twist.r':'lowerarm_twist_01_r',
'hand.r':'hand_r',

'shoulder.l':'clavicle_l',
'c_arm_twist_offset.l':'upperarm_l',
'arm_stretch.l':'upperarm_twist_01_l',
'forearm_stretch.l':'lowerarm_l',
'forearm_twist.l':'lowerarm_twist_01_l',
'hand.l':'hand_l',

'thigh_twist.l':'thigh_l',
'thigh_stretch.l':'thigh_twist_01_l',
'leg_twist.l':'calf_l',
'leg_stretch.l':'calf_twist_01_l',
'foot.l':'foot_l',
'toes_01.l':'ball_l',

'thigh_twist.r':'thigh_r',
'leg_stretch.r':'thigh_twist_01_r',
'leg_twist.r':'calf_r',
'thigh_stretch.r':'calf_twist_01_r',
'foot.r':'foot_r',
'toes_01.r':'ball_r',

#'c_pinky1_base.l':'',
'pinky1.l':'pinky_01_l',
'c_pinky2.l':'pinky_02_l',
'c_pinky3.l':'pinky_03_l',
#'c_ring1_base.l':'',
'ring1.l':'ring_01_l',
'c_ring2.l':'ring_02_l',
'c_ring3.l':'ring_03_l',
#'c_middle1_base.l':'',
'middle1.l':'middle_01_l',
'c_middle2.l':'middle_02_l',
'c_middle3.l':'middle_03_l',
#'c_index1_base.l':'',
'index1.l':'index_01_l',
'c_index2.l':'index_02_l',
'c_index3.l':'index_03_l',
'thumb1.l':'thumb_01_l',
'c_thumb2.l':'thumb_02_l',
'c_thumb3.l':'thumb_03_l',

#'c_pinky1_base.r':'',
'pinky1.r':'pinky_01_r',
'c_pinky2.r':'pinky_02_r',
'c_pinky3.r':'pinky_03_r',
#'c_ring1_base.r':'',
'ring1.r':'ring_01_r',
'c_ring2.r':'ring_02_r',
'c_ring3.r':'ring_03_r',
#'c_middle1_base.r':'',
'middle1.r':'middle_01_r',
'c_middle2.r':'middle_02_r',
'c_middle3.r':'middle_03_r',
#'c_index1_base.r':'',
'index1.r':'index_01_r',
'c_index2.r':'index_02_r',
'c_index3.r':'index_03_r',
'thumb1.r':'thumb_01_r',
'c_thumb2.r':'thumb_02_r',
'c_thumb3.r':'thumb_03_r',

}

ue4_={
'pelvis':'root.x',
'spine_01':'spine_01.x',
'spine_02':'spine_02.x',
'spine_03':'spine_03.x',
'neck_01':'neck.x',
'head':'head.x',
'clavicle_r':'shoulder.r',
'upperarm_r':'c_arm_twist_offset.r',
'upperarm_twist_01_r':'arm_stretch.r',
'lowerarm_r':'forearm_stretch.r',
'lowerarm_twist_01_r':'forearm_twist.r',
'hand_r':'hand.r',
'clavicle_l':'shoulder.l',
'upperarm_l':'c_arm_twist_offset.l',
'upperarm_twist_01_l':'arm_stretch.l',
'lowerarm_l':'forearm_stretch.l',
'lowerarm_twist_01_l':'forearm_twist.l',
'hand_l':'hand.l',
'thigh_l':'thigh_twist.l',
'thigh_twist_01_l':'thigh_stretch.l',
'calf_l':'leg_twist.l',
'calf_twist_01_l':'leg_stretch.l',
'foot_l':'foot.l',
'ball_l':'toes_01.l',
'thigh_r':'thigh_twist.r',
'thigh_twist_01_r':'leg_stretch.r',
'calf_r':'leg_twist.r',
'calf_twist_01_r':'thigh_stretch.r',
'':'foot.r',
'':'toes_01.r',
'pinky_01_l':'pinky1.l',
'pinky_02_l':'c_pinky2.l',
'pinky_03_l':'c_pinky3.l',
'ring_01_l':'ring1.l',
'ring_02_l':'c_ring2.l',
'ring_03_l':'c_ring3.l',
'middle_01_l':'middle1.l',
'middle_02_l':'c_middle2.l',
'middle_03_l':'c_middle3.l',
'index_01_l':'index1.l',
'index_02_l':'c_index2.l',
'index_03_l':'c_index3.l',
'thumb_01_l':'thumb1.l',
'thumb_02_l':'c_thumb2.l',
'thumb_03_l':'c_thumb3.l',
'pinky_01_r':'pinky1.r',
'pinky_02_r':'c_pinky2.r',
'pinky_03_r':'c_pinky3.r',
'ring_01_r':'ring1.r',
'ring_02_r':'c_ring2.r',
'ring_03_r':'c_ring3.r',
'middle_01_r':'middle1.r',
'middle_02_r':'c_middle2.r',
'middle_03_r':'c_middle3.r',
'index_01_r':'index1.r',
'index_02_r':'c_index2.r',
'index_03_r':'c_index3.r',
'thumb_01_r':'thumb1.r',
'thumb_02_r':'c_thumb2.r',
'thumb_03_r':'c_thumb3.r',
}



ue4_ref={
'pelvis':'root_ref.x',
'spine_01':'spine_01_ref.x',
'spine_02':'spine_02_ref.x',
'spine_03':'spine_03_ref.x',
'neck_01':'neck_ref.x',
'head':'head_ref.x',

'clavicle_r':'shoulder_ref.r',
'upperarm_r':'arm_ref.r',
'lowerarm_r':'forearm_ref.r',
'hand_r':'hand_ref.r',

'clavicle_l':'shoulder_ref.l',
'upperarm_l':'arm_ref.l',
'lowerarm_l':'forearm_ref.l',
'hand_l':'hand_ref.l',

'thigh_l':'thigh_ref.l',
'calf_l':'leg_ref.l',
'foot_l':'foot_ref.l',
'ball_l':'toes_01_ref.l',

'thigh_r':'thigh_ref.r',
'calf_r':'leg_ref.r',
'foot_r':'foot_ref.r',
'ball_r':'toes_01_ref.r',

'pinky_01_l':'pinky1_ref.l',
'pinky_02_l':'pinky2_ref.l',
'pinky_03_l':'pinky3_ref.l',

'ring_01_l':'ring1_ref.l',
'ring_02_l':'ring2_ref.l',
'ring_03_l':'ring3_ref.l',

'middle_01_l':'middle1_ref.l',
'middle_02_l':'middle2_ref.l',
'middle_03_l':'middle3_ref.l',

'index_01_l':'index1_ref.l',
'index_02_l':'index2_ref.l',
'index_03_l':'index3_ref.l',

'thumb_01_l':'thumb1_ref.l',
'thumb_02_l':'thumb2_ref.l',
'thumb_03_l':'thumb3_ref.l',

'pinky_01_r':'pinky1_ref.r',
'pinky_02_r':'pinky2_ref.r',
'pinky_03_r':'pinky3_ref.r',

'ring_01_r':'ring1_ref.r',
'ring_02_r':'ring2_ref.r',
'ring_03_r':'ring3_ref.r',

'middle_01_r':'middle1_ref.r',
'middle_02_r':'middle2_ref.r',
'middle_03_r':'middle3_ref.r',

'index_01_r':'index1_ref.r',
'index_02_r':'index2_ref.r',
'index_03_r':'index3_ref.r',

'thumb_01_r':'thumb1_ref.r',
'thumb_02_r':'thumb2_ref.r',
'thumb_03_r':'thumb3_ref.r',
}

ue4_additional = {
'arm_ref.l'
'upperarm_r':'arm_ref.l',
'lowerarm_r':'forearm_ref.r',


    
}



#--------------------------------------------------------
# Auto Rig Pro <> mixamo
#--------------------------------------------------------

mixamo={
'root.x':'mixamorig:Hips',
'spine_01.x':'mixamorig:Spine',
'spine_02.x':'mixamorig:Spine1',
'spine_03.x':'mixamorig:Spine2',
'neck.x':'mixamorig:Neck',
'head.x':'mixamorig:Head',

#'':'mixamorig:HeadTop_End',
'shoulder.l':'mixamorig:LeftShoulder',
'c_arm_twist_offset.l':'mixamorig:LeftArm',
'forearm_stretch.l':'mixamorig:LeftForeArm',
'hand.l':'mixamorig:LeftHand',
'index1.l':'mixamorig:LeftHandIndex1',
'c_index2.l':'mixamorig:LeftHandIndex2',
'c_index3.l':'mixamorig:LeftHandIndex3',
#'':'mixamorig:LeftHandIndex4',

'shoulder.r':'mixamorig:RightShoulder',
'c_arm_twist_offset.r':'mixamorig:RightArm',
'forearm_stretch.r':'mixamorig:RightForeArm',
'hand.r':'mixamorig:RightHand',
'index1.r':'mixamorig:RightHandIndex1',
'c_index2.r':'mixamorig:RightHandIndex2',
'c_index3.r':'mixamorig:RightHandIndex3',
#'':'mixamorig:RightHandIndex4',

'thigh_twist.l':'mixamorig:LeftUpLeg',
'leg_twist.l':'mixamorig:LeftLeg',
'foot.l':'mixamorig:LeftFoot',
'toes_01.l':'mixamorig:LeftToeBase',
#'':'mixamorig:LeftToe_End',

'thigh_twist.r':'mixamorig:RightUpLeg',
'leg_twist.r':'mixamorig:RightLeg',
'foot.r':'mixamorig:RightFoot',
'toes_01.r':'mixamorig:RightToeBase',
#'':'mixamorig:RightToe_End'



}



# c_skull_01.x
# jawbone.x
# tong_03.x
# tong_02.x
# tong_01.x
# c_chin_01.x
# c_chin_02.x
# c_teeth_bot.x
# c_teeth_bot.l
# c_teeth_bot.r
# c_lips_bot_01.l
# c_lips_bot_01.r
# c_lips_bot.l
# c_lips_bot.r
# c_lips_bot.x
# c_teeth_top.x
# c_teeth_top.l
# c_teeth_top.r
# c_lips_top.x
# c_lips_top.l
# c_lips_top.r
# c_lips_top_01.l
# c_lips_top_01.r
# c_lips_smile.l
# c_lips_smile.r
# c_skull_02.x
# c_eye_offset.l
# c_eyelid_corner_01.l
# c_eyelid_corner_02.l
# c_eye.l
# c_eyelid_top_01.l
# c_eyelid_top_02.l
# c_eyelid_top_03.l
# c_eyelid_bot_01.l
# c_eyelid_bot_02.l
# c_eyelid_bot_03.l
# c_cheek_smile.l
# c_eye_offset.r
# c_eyelid_corner_01.r
# c_eyelid_corner_02.r
# c_eye.r
# c_eyelid_top_01.r
# c_eyelid_top_02.r
# c_eyelid_top_03.r
# c_eyelid_bot_01.r
# c_eyelid_bot_02.r
# c_eyelid_bot_03.r
# c_cheek_smile.r
# c_nose_03.x
# c_nose_01.x
# c_nose_02.x
# c_cheek_inflate.l
# c_cheek_inflate.r
# c_eyebrow_03.r
# c_eyebrow_02.r
# c_eyebrow_01.r
# c_eyebrow_01_end.r
# c_eyebrow_03.l
# c_eyebrow_02.l
# c_eyebrow_01.l
# c_eyebrow_01_end.l
# c_ear_01.l
# c_ear_02.l
# c_ear_01.r
# c_ear_02.r
# c_skull_03.x
# c_eye_ref_track.l
# c_eye_ref_track.r



#--------------------------------------------------------
# Auto Rig Pro <> ARP Reference
#--------------------------------------------------------
# ue4 = {
# 'root.x':'root_ref.x',
# 'spine_01.x':'spine_01_ref.x',
# 'spine_02.x':'spine_02_ref.x',
# 'spine_03.x':'spine_03_ref.x',
# 'neck.x':'neck_01',
# 'head.x':'head',

# 'shoulder.r':'clavicle_r',
# 'c_arm_twist_offset.r':'upperarm_r',
# 'arm_stretch.r':'upperarm_twist_01_r',
# 'forearm_stretch.r':'lowerarm_r',
# 'forearm_twist.r':'lowerarm_twist_01_r',
# 'hand.r':'hand_r',

# 'shoulder.l':'clavicle_l',
# 'c_arm_twist_offset.l':'upperarm_l',
# 'arm_stretch.l':'upperarm_twist_01_l',
# 'forearm_stretch.l':'lowerarm_l',
# 'forearm_twist.l':'lowerarm_twist_01_l',
# 'hand.l':'hand_l',

# 'thigh_twist.l':'thigh_l',
# 'thigh_stretch.l':'thigh_twist_01_l',
# 'leg_twist.l':'calf_l',
# 'leg_stretch.l':'calf_twist_01_l',
# 'foot.l':'foot_l',
# 'toes_01.l':'ball_l',

# 'thigh_twist.r':'thigh_r',
# 'leg_stretch.r':'thigh_twist_01_r',
# 'leg_twist.r':'calf_r',
# 'thigh_stretch.r':'calf_twist_01_r',
# 'foot.r':'',
# 'toes_01.r':'',

# #'c_pinky1_base.l':'',
# 'pinky1.l':'pinky_01_l',
# 'c_pinky2.l':'pinky_02_l',
# 'c_pinky3.l':'pinky_03_l',
# #'c_ring1_base.l':'',
# 'ring1.l':'ring_01_l',
# 'c_ring2.l':'ring_02_l',
# 'c_ring3.l':'ring_03_l',
# #'c_middle1_base.l':'',
# 'middle1.l':'middle_01_l',
# 'c_middle2.l':'middle_02_l',
# 'c_middle3.l':'middle_03_l',
# #'c_index1_base.l':'',
# 'index1.l':'index_01_l',
# 'c_index2.l':'index_02_l',
# 'c_index3.l':'index_03_l',
# 'thumb1.l':'thumb_01_l',
# 'c_thumb2.l':'thumb_02_l',
# 'c_thumb3.l':'thumb_03_l',

# #'c_pinky1_base.r':'',
# 'pinky1.r':'pinky_01_r',
# 'c_pinky2.r':'pinky_02_r',
# 'c_pinky3.r':'pinky_03_r',
# #'c_ring1_base.r':'',
# 'ring1.r':'ring_01_r',
# 'c_ring2.r':'ring_02_r',
# 'c_ring3.r':'ring_03_r',
# #'c_middle1_base.r':'',
# 'middle1.r':'middle_01_r',
# 'c_middle2.r':'middle_02_r',
# 'c_middle3.r':'middle_03_r',
# #'c_index1_base.r':'',
# 'index1.r':'index_01_r',
# 'c_index2.r':'index_02_r',
# 'c_index3.r':'index_03_r',
# 'thumb1.r':'thumb_01_r',
# 'c_thumb2.r':'thumb_02_r',
# 'c_thumb3.r':'thumb_03_r',

# }
