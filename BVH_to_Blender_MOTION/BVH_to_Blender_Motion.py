import bpy, time, os, shutil

# BVH 파일 저장 경로
bvh_folder_path = "C:/Users/054/Desktop/BVH_files"
files = [f for f in os.listdir(bvh_folder_path) if os.path.isfile(os.path.join(bvh_folder_path, f))]

# DB 설정
import pyodbc
import datetime

#Azure SQL DB Initialization 부분
server='tcp:sql-3dchatbot-server.database.windows.net,1433'
database='3D-ChatbotDB'
username='SKT1'
password=''

conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password+';Encrypt=yes;TrustServerCertificate=no;')

cursor = conn.cursor()

#DB 내의 가장 최근 파일을 불러오기 위해 2000년 1월 1일을 기준으로 설정
last_timestamp = datetime.datetime(2000, 1, 1)

# 메인 캐릭터, 시작 애니메이션 파일 위치는 BVH 파일 폴더와 다른 곳이어야 함
adot = bpy.data.objects.get("HelloBlender") # 기본 캐릭터 
adot_name = "HelloBlender"
first_anim_path = "C:/Users/054/Desktop/BVH_to_Blender_MOTION/HelloBlender.bvh"

# BVH 파일 저장 폴더 비우기
for filename in os.listdir(bvh_folder_path):
    file_path = os.path.join(bvh_folder_path, filename)
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"파일 삭제: {file_path}")
    except Exception as e:
        print(f"파일 삭제 실패: {file_path}, 오류: {e}")

def play_animation():
    bpy.ops.screen.animation_play()
    
def stop_animation():
    bpy.ops.screen.animation_cancel()
    
def get_animation_delete(bvh_path): # BVH파일을 블랜더 scene에 임포트, 기존 armature 삭제
    global adot, cur_animation
    bpy.ops.import_anim.bvh(filepath=bvh_path)
    armature_name = bvh_path.split("/")[-1]
    armature_name = armature_name.split(".")[0]
    
    bone_group_name = "BlueBones"
    
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE' and obj.name != armature_name:
            bpy.data.objects.remove(obj, do_unlink=True)
        elif obj.type == 'ARMATURE' and obj.name == armature_name:
            bone_group = obj.pose.bone_groups.new(name=bone_group_name)
            for bone in obj.pose.bones:
                bone.bone_group = bone_group
                bone.bone_group.color_set = 'CUSTOM'
            bpy.context.view_layer.objects.active = bpy.data.objects[armature_name]
            bpy.ops.object.mode_set(mode='POSE')
    
    object_name = "Empty"
    armature_name = armature_name
    bone_name = "Hips"
    empt_y = bpy.data.objects.get(object_name)
    copy_loc_constraint = empt_y.constraints.new(type='COPY_LOCATION')
    copy_loc_constraint.target = bpy.data.objects.get(armature_name)
    copy_loc_constraint.subtarget = bone_name
    copy_loc_constraint.use_x = True
    copy_loc_constraint.use_y = True
    copy_loc_constraint.influence = 1.0 
    
animation_on = True

def main_timer():
    global bvh_folder_path, files, animation_on, adot, anilist
    print(int((time.time()-startTime)*10)/10, end="\r") # 프로그램 켜놓은 시간 체크

    insert_query = """
    SELECT * FROM BVHdb WHERE Timestamp > ? ORDER BY Timestamp DESC
    """

    cursor.execute(insert_query, last_timestamp)
    rows = cursor.fetchall()

    data_id = rows[0]
    timestamp = rows[1]
    motion_content = rows[2]
    label_name = rows[3]
    file_name = rows[4]
    file_data = rows[5]

    last_timestamp = timestamp

    bvh_file_path = f"C:/Users/054/Desktop/BVH_files/{file_name}.bvh"

    with open(bvh_file_path, 'wb') as file:
        file.write(file_data)

    print(f"""
            DATA DOWNLOADED!!
            DataID:          {data_id}
            Timestamp:       {timestamp}
            MotionContent:   {motion_content}
            LabelName:       {label_name}
            FileName:        {file_name}
            FileData (size): {len(file_data) if file_data else 0} bytes
            """)

    files = [f for f in os.listdir(bvh_folder_path) if os.path.isfile(os.path.join(bvh_folder_path, f))]
    if len(files) > 1:
        files.sort(key=lambda f: os.path.getmtime(os.path.join(bvh_folder_path, f)))
        old_file_path = os.path.join(bvh_folder_path, files[0]).replace('\\', '/')
        os.remove(old_file_path)
        animation_on = True
    if animation_on and len(files) == 1:
        animation_on = False
        stop_animation()
        nowpath = os.path.join(bvh_folder_path, files[0]).replace('\\', '/')
        get_animation_delete(nowpath)
        bpy.app.timers.register(restart_animation, first_interval=0.075)
    
    return 0.05 # 타이머 간격 (초)

def restart_animation():
    global adot, anilist, cur_animation
    bpy.app.timers.unregister(restart_animation)
    
    play_animation()

# 타이머 등록, 타이머 간격을 주기로 update반복
bpy.app.timers.register(main_timer)
startTime = time.time()
get_animation_delete(first_anim_path) 
play_animation()