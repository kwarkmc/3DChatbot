# https://github.com/sigal-raab/Motion (git clone)
# test.py와 동일한 위치에 변환하고자 하는 .npy 위치
# mdm 성공
import numpy as np 

def smpl2bvh(file):
    from Motion.InverseKinematics import animation_from_positions
    from Motion import BVH
    npy_file = file
    motion_path = f'{npy_file}'
    pos = np.load(motion_path, allow_pickle=True)
    pos_dictionary = dict(enumerate(pos.flatten()))[0]
    pos_dictionary["motion"] = pos_dictionary["motion"].tolist()
    pos_motion = pos_dictionary['motion']

    # 다시 ndaaray로 변환
    pos_motion = np.array(pos_motion)
    pos = pos_motion.transpose(0, 3, 1, 2) # samples x joints x coord x frames ==> samples x frames x joints x coord
    parents = [-1, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9, 12, 13, 14, 16, 17, 18, 19]
    bvh_path = motion_path[:-4] + 'anim{}.bvh'
    SMPL_JOINT_NAMES = [
    'Hips', # 0
    'LeftUpLeg', # 1
    'rightUpLeg', # 2
    'Spine', # 3
    'LeftLeg', # 4
    'RightLeg', # 5
    'Spine1', # 6
    'LeftFoot', # 7
    'RightFoot', # 8
    'Spine2', # 9
    'LeftToeBase', # 10
    'RightToeBase', # 11
    'Neck', # 12
    'LeftShoulder', # 13
    'RightShoulder', # 14
    'Head', # 15
    'LeftArm', # 16
    'RightArm', # 17
    'LeftForeArm', # 18
    'RightForeArm', # 19
    'LeftHand', # 20
    'RightHand', # 21
    ]
    for i, p in enumerate(pos):
        print(f'starting anim no. {i}')
    anim, sorted_order, _ = animation_from_positions(p, parents)
    BVH.save(bvh_path.format(i), anim, names=np.array(SMPL_JOINT_NAMES)[sorted_order])

smpl2bvh('변환하고자 하는 .npy')