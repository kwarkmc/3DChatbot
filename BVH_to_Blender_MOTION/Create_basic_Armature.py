import bpy, os

# BVH 파일 경로 설정
bvh_file_path = r"C:\Users\054\Desktop\Temp_bvh\HelloBlender.bvh"
bvh_file_path = os.path.normpath(bvh_file_path)
bpy.ops.import_anim.bvh(filepath=bvh_file_path)
bpy.ops.screen.animation_play()
