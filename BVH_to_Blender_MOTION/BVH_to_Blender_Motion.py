import sys, bpy, time, os, shutil, random
from datetime import datetime
import bpy, sys, math, os, mathutils 
from typing import Any, Dict, Iterable, List, Tuple, Optional, Sequence

# BVH 파일 저장 경로
bvh_folder_path = "C:/Users/054/Desktop/BVH_files"
files = [f for f in os.listdir(bvh_folder_path) if os.path.isfile(os.path.join(bvh_folder_path, f))]

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
    
    armature_name = bvh_path.split("/")[-1]
    armature_name = armature_name.split(".")[0]+"_main_char_"
    
    ################
    def Import_BVH_Mesh(bvh_path):
    
        scene = bpy.data.scenes["Scene"]
        world = scene.world

        input_bvh_path = bvh_path
        def create_mesh_from_pydata(scene: bpy.types.Scene,
                                    vertices: Iterable[Iterable[float]],
                                    faces: Iterable[Iterable[int]],
                                    mesh_name: str,
                                    object_name: str,
                                    use_smooth: bool = True) -> bpy.types.Object:
            # Add a new mesh and set vertices and faces
            # In this case, it does not require to set edges
            # After manipulating mesh data, update() needs to be called
            new_mesh: bpy.types.Mesh = bpy.data.meshes.new(mesh_name)
            new_mesh.from_pydata(vertices, [], faces)
            new_mesh.update()
            def set_smooth_shading(mesh: bpy.types.Mesh) -> None:
                for polygon in mesh.polygons:
                    polygon.use_smooth = True
            if use_smooth:
                set_smooth_shading(new_mesh)

            new_object: bpy.types.Object = bpy.data.objects.new(object_name, new_mesh)
            scene.collection.objects.link(new_object)

            return new_object
        ################
        def create_armature_from_bvh(bvh_path: str) -> bpy.types.Object:
            global_scale = 1  # This value needs to be changed depending on the motion data
            bpy.ops.import_anim.bvh(filepath=bvh_path,
                                    axis_forward='-Z',
                                    axis_up='Y',
                                    target='ARMATURE',
                                    global_scale=global_scale,
                                    frame_start=1,
                                    use_fps_scale=True,
                                    update_scene_fps=False,
                                    update_scene_duration=True)
            armature = bpy.context.object
            return armature
        ################
        def add_subdivision_surface_modifier(mesh_object: bpy.types.Object, level: int, is_simple: bool = False) -> None:
            '''
            https://docs.blender.org/api/current/bpy.types.SubsurfModifier.html
            '''

            modifier: bpy.types.SubsurfModifier = mesh_object.modifiers.new(name="Subsurf", type='SUBSURF')

            modifier.levels = level
            modifier.render_levels = level
            modifier.subdivision_type = 'SIMPLE' if is_simple else 'CATMULL_CLARK'
        ################
        def create_armature_mesh(scene: bpy.types.Scene, armature_object: bpy.types.Object, mesh_name: str) -> bpy.types.Object:
            assert armature_object.type == 'ARMATURE', 'Error'
            assert len(armature_object.data.bones) != 0, 'Error'

            def add_rigid_vertex_group(target_object: bpy.types.Object, name: str, vertex_indices: Iterable[int]) -> None:
                new_vertex_group = target_object.vertex_groups.new(name=name)
                for vertex_index in vertex_indices:
                    new_vertex_group.add([vertex_index], 1.0, 'REPLACE')

            def generate_bone_mesh_pydata(horizontal_radius: float, vertical_radius: float, length: float, segments: int = 16) -> Tuple[List[mathutils.Vector], List[List[int]]]:
                vertices = []
                faces = []
                segments = 16
                # Generate the top and bottom circles of the ellipsoid
                for y in [0, length]:
                    for i in range(segments):
                        angle = (i / segments) * 2 * math.pi
                        x = horizontal_radius * math.cos(angle)
                        z = vertical_radius * math.sin(angle)
                        vertices.append(mathutils.Vector((x, y, z)))
                        
                # Center points
                vertices.append(mathutils.Vector((0, 0, 0)))           # bottom center
                vertices.append(mathutils.Vector((0, length, 0)))      # top center
                
                # Create faces for the bottom and top
                for i in range(segments):
                    next_i = (i + 1) % segments
                    # Bottom
                    faces.append([i, next_i, segments * 2])
                    # Top
                    faces.append([i + segments, next_i + segments, segments * 2 + 1])
                    
                # Create the side faces
                for i in range(segments):
                    next_i = (i + 1) % segments
                    faces.append([i, next_i, next_i + segments, i + segments])

                return vertices, faces

            armature_data: bpy.types.Armature = armature_object.data

            vertices: List[mathutils.Vector] = []
            faces: List[List[int]] = []
            vertex_groups: List[Dict[str, Any]] = []
            
            modified_length = 0.1
            
            for bone in armature_data.bones:
                print(bone.name)
                if bone.name == "Neck":
                    horizontal_radius = 0.7 * (0.10 + bone.length)
                    vertical_radius = 0.7 * (0.10 + bone.length)
                    modified_length = bone.length * 1.25
                elif bone.name == "Spine":
                    horizontal_radius = 0.8 * (0.10 + bone.length)  # 옆면 면적을 더 크게 만들기 위해 값을 조정
                    vertical_radius = 0.8 * (0.10 + bone.length)
                    modified_length = bone.length * 2
                elif bone.name == "Spine1":
                    horizontal_radius = 1.3 * (0.10 + bone.length)
                    vertical_radius = 1.3 * (0.10 + bone.length)
                    modified_length = bone.length * 2
                elif bone.name == "Spine2":
                    horizontal_radius = 0.8 * (0.10 + bone.length)
                    vertical_radius = 0.8 * (0.10 + bone.length)
                    modified_length = bone.length * 0.5
                elif bone.name == "Hips":
                    horizontal_radius = 0.9 * (0.10 + bone.length)
                    vertical_radius = 0.9 * (0.10 + bone.length)
                    modified_length = bone.length * 1.5
                else:
                    horizontal_radius = 0.1 * (0.10 + bone.length)
                    vertical_radius = 0.1 * (0.10 + bone.length)
                    modified_length = bone.length * 1
                    
                temp_vertices, temp_faces = generate_bone_mesh_pydata(horizontal_radius, vertical_radius, modified_length)

                vertex_index_offset = len(vertices)

                temp_vertex_group = {'name': bone.name, 'vertex_indices': []}
                for local_index, vertex in enumerate(temp_vertices):
                    vertices.append(bone.matrix_local @ vertex)
                    temp_vertex_group['vertex_indices'].append(local_index + vertex_index_offset)
                vertex_groups.append(temp_vertex_group)

                for face in temp_faces:
                    if len(face) == 3:
                        faces.append([
                            face[0] + vertex_index_offset,
                            face[1] + vertex_index_offset,
                            face[2] + vertex_index_offset,
                        ])
                    else:
                        faces.append([
                            face[0] + vertex_index_offset,
                            face[1] + vertex_index_offset,
                            face[2] + vertex_index_offset,
                            face[3] + vertex_index_offset,
                            
                        ])

            new_object = create_mesh_from_pydata(scene, vertices, faces, mesh_name, mesh_name)
            new_object.matrix_world = armature_object.matrix_world
            new_object.name = armature_name

            for vertex_group in vertex_groups:
                add_rigid_vertex_group(new_object, vertex_group['name'], vertex_group['vertex_indices'])

            armature_modifier = new_object.modifiers.new('Armature', 'ARMATURE')
            armature_modifier.object = armature_object
            armature_modifier.use_vertex_groups = True

            add_subdivision_surface_modifier(new_object, 1, is_simple=True)
            add_subdivision_surface_modifier(new_object, 2, is_simple=False)

            # Set the armature as the parent of the new object
            bpy.ops.object.select_all(action='DESELECT')
            new_object.select_set(True)
            armature_object.select_set(True)
            bpy.context.view_layer.objects.active = armature_object
            bpy.ops.object.parent_set(type='OBJECT')

            return new_object
        ################
        def add_material(name: str = "Material",
                        use_nodes: bool = False,
                        make_node_tree_empty: bool = False) -> bpy.types.Material:
            '''
            https://docs.blender.org/api/current/bpy.types.BlendDataMaterials.html
            https://docs.blender.org/api/current/bpy.types.Material.html
            '''

            # TODO: Check whether the name is already used or not

            material = bpy.data.materials.new(name)
            material.use_nodes = use_nodes
            
            def clean_nodes(nodes: bpy.types.Nodes) -> None:
                for node in nodes:
                    nodes.remove(node)
                    
            if use_nodes and make_node_tree_empty:
                clean_nodes(material.node_tree.nodes)

            return material
        ################
        mat = add_material("BlueMetal", use_nodes=True, make_node_tree_empty=True)
        output_node = mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
        principled_node = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
        R, G, B = random.random(), random.random(), random.random()
        principled_node.inputs['Base Color'].default_value = (R, G, B, 0.5) #(0.1, 0.2, 0.7, 0.5)
        principled_node.inputs['Metallic'].default_value = 0.6 #0.9
        principled_node.inputs['Roughness'].default_value = 0.1 #0.1
        mat.node_tree.links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
        ################
        def arrange_nodes(node_tree: bpy.types.NodeTree, verbose: bool = False) -> None:
            max_num_iters = 2000
            epsilon = 1e-05
            target_space = 50.0

            second_stage = False

            fix_horizontal_location = True
            fix_vertical_location = True
            fix_overlaps = True

            if verbose:
                print("-----------------")
                print("Target nodes:")
                for node in node_tree.nodes:
                    print("- " + node.name)

            # In the first stage, expand nodes overly
            target_space *= 2.0

            # Gauss-Seidel-style iterations
            previous_squared_deltas_sum = sys.float_info.max
            for i in range(max_num_iters):
                squared_deltas_sum = 0.0

                if fix_horizontal_location:
                    for link in node_tree.links:
                        k = 0.9 if not second_stage else 0.5
                        threshold_factor = 2.0

                        x_from = link.from_node.location[0]
                        x_to = link.to_node.location[0]
                        w_from = link.from_node.width
                        signed_space = x_to - x_from - w_from
                        C = signed_space - target_space
                        grad_C_x_from = -1.0
                        grad_C_x_to = 1.0

                        # Skip if the distance is sufficiently large
                        if C >= target_space * threshold_factor:
                            continue

                        lagrange = C / (grad_C_x_from * grad_C_x_from + grad_C_x_to * grad_C_x_to)
                        delta_x_from = -lagrange * grad_C_x_from
                        delta_x_to = -lagrange * grad_C_x_to

                        link.from_node.location[0] += k * delta_x_from
                        link.to_node.location[0] += k * delta_x_to

                        squared_deltas_sum += k * k * (delta_x_from * delta_x_from + delta_x_to * delta_x_to)

                if fix_vertical_location:
                    k = 0.5 if not second_stage else 0.05
                    socket_offset = 20.0

                    def get_from_socket_index(node: bpy.types.Node, node_socket: bpy.types.NodeSocket) -> int:
                        for i in range(len(node.outputs)):
                            if node.outputs[i] == node_socket:
                                return i
                        assert False

                    def get_to_socket_index(node: bpy.types.Node, node_socket: bpy.types.NodeSocket) -> int:
                        for i in range(len(node.inputs)):
                            if node.inputs[i] == node_socket:
                                return i
                        assert False

                    for link in node_tree.links:
                        from_socket_index = get_from_socket_index(link.from_node, link.from_socket)
                        to_socket_index = get_to_socket_index(link.to_node, link.to_socket)
                        y_from = link.from_node.location[1] - socket_offset * from_socket_index
                        y_to = link.to_node.location[1] - socket_offset * to_socket_index
                        C = y_from - y_to
                        grad_C_y_from = 1.0
                        grad_C_y_to = -1.0
                        lagrange = C / (grad_C_y_from * grad_C_y_from + grad_C_y_to * grad_C_y_to)
                        delta_y_from = -lagrange * grad_C_y_from
                        delta_y_to = -lagrange * grad_C_y_to

                        link.from_node.location[1] += k * delta_y_from
                        link.to_node.location[1] += k * delta_y_to

                        squared_deltas_sum += k * k * (delta_y_from * delta_y_from + delta_y_to * delta_y_to)

                if fix_overlaps and second_stage:
                    k = 0.9
                    margin = 0.5 * target_space

                    # Examine all node pairs
                    for node_1 in node_tree.nodes:
                        for node_2 in node_tree.nodes:
                            if node_1 == node_2:
                                continue

                            x_1 = node_1.location[0]
                            x_2 = node_2.location[0]
                            w_1 = node_1.width
                            w_2 = node_2.width
                            cx_1 = x_1 + 0.5 * w_1
                            cx_2 = x_2 + 0.5 * w_2
                            rx_1 = 0.5 * w_1 + margin
                            rx_2 = 0.5 * w_2 + margin

                            # Note: "dimensions" and "height" may not be correct depending on the situation
                            def get_height(node: bpy.types.Node) -> float:
                                if node.dimensions.y > epsilon:
                                    return node.dimensions.y
                                elif math.fabs(node.height - 100.0) > epsilon:
                                    return node.height
                                else:
                                    return 200.0

                            y_1 = node_1.location[1]
                            y_2 = node_2.location[1]
                            h_1 = get_height(node_1)
                            h_2 = get_height(node_2)
                            cy_1 = y_1 - 0.5 * h_1
                            cy_2 = y_2 - 0.5 * h_2
                            ry_1 = 0.5 * h_1 + margin
                            ry_2 = 0.5 * h_2 + margin

                            C_x = math.fabs(cx_1 - cx_2) - (rx_1 + rx_2)
                            C_y = math.fabs(cy_1 - cy_2) - (ry_1 + ry_2)

                            # If no collision, just skip
                            if C_x >= 0.0 or C_y >= 0.0:
                                continue

                            # Solve collision for the "easier" direction
                            if C_x > C_y:
                                grad_C_x_1 = 1.0 if cx_1 - cx_2 >= 0.0 else -1.0
                                grad_C_x_2 = -1.0 if cx_1 - cx_2 >= 0.0 else 1.0
                                lagrange = C_x / (grad_C_x_1 * grad_C_x_1 + grad_C_x_2 * grad_C_x_2)
                                delta_x_1 = -lagrange * grad_C_x_1
                                delta_x_2 = -lagrange * grad_C_x_2

                                node_1.location[0] += k * delta_x_1
                                node_2.location[0] += k * delta_x_2

                                squared_deltas_sum += k * k * (delta_x_1 * delta_x_1 + delta_x_2 * delta_x_2)
                            else:
                                grad_C_y_1 = 1.0 if cy_1 - cy_2 >= 0.0 else -1.0
                                grad_C_y_2 = -1.0 if cy_1 - cy_2 >= 0.0 else 1.0
                                lagrange = C_y / (grad_C_y_1 * grad_C_y_1 + grad_C_y_2 * grad_C_y_2)
                                delta_y_1 = -lagrange * grad_C_y_1
                                delta_y_2 = -lagrange * grad_C_y_2

                                node_1.location[1] += k * delta_y_1
                                node_2.location[1] += k * delta_y_2

                                squared_deltas_sum += k * k * (delta_y_1 * delta_y_1 + delta_y_2 * delta_y_2)

                if verbose:
                    print("Iteration #" + str(i) + ": " + str(previous_squared_deltas_sum - squared_deltas_sum))

                # Check the termination conditiion
                if math.fabs(previous_squared_deltas_sum - squared_deltas_sum) < epsilon:
                    if second_stage:
                        break
                    else:
                        target_space = 0.5 * target_space
                        second_stage = True

                previous_squared_deltas_sum = squared_deltas_sum
    ################
        arrange_nodes(mat.node_tree)
    ################
        armature = create_armature_from_bvh(bvh_path=input_bvh_path)
        armature.name = armature_name+"0" ## 만들어진 뼈대이름은 Mesh이름 +0
        armature_mesh = create_armature_mesh(scene, armature, 'Mesh')
        armature_mesh.data.materials.append(mat)
    ################
        
    Import_BVH_Mesh(bvh_path) # bvh파일 임포트하고 mesh입히는 함수, yuki-koyama님의 blender-cli-rendering 모듈 통합, 수정
    ################
    
    print(armature_name)
    for obj in bpy.context.scene.objects:
        if (obj.type == 'ARMATURE' and '_main_char_' in obj.name and obj.name != armature_name+'0') or (obj.type == 'MESH' and '_main_char_' in obj.name and obj.name != armature_name):
            bpy.data.objects.remove(obj) ##뼈대이름예시 : running_main_char_0 ##메시이름예시 : running_main_char_ 만약 새로운 bvh임포트되면 기존거 두개 삭제
            
    #bone_group_name = "BlueBones"
        # elif obj.type == 'ARMATURE' and obj.name == armature_name:
        #     bone_group = obj.pose.bone_groups.new(name=bone_group_name)
        #     for bone in obj.pose.bones:
        #         bone.bone_group = bone_group
        #         bone.bone_group.color_set = 'CUSTOM'
        #     bpy.context.view_layer.objects.active = bpy.data.objects[armature_name]
        #     bpy.ops.object.mode_set(mode='POSE')
    
animation_on = True

nowpath = None
target_armature_name = ""
object_name = ""

def make_target(nowpath):
    global target_armature_name, object_name
    target_armature_name = nowpath.split("/")[-1].split(".")[0]+'_main_char_0'
    object_name = "Empty"
    bone_name = "Hips"
    empt_y = bpy.data.objects.get("Empty")
    copy_loc_constraint = empt_y.constraints.new(type='COPY_LOCATION')
    copy_loc_constraint.target = bpy.data.objects.get(target_armature_name)
    copy_loc_constraint.subtarget = bone_name
    copy_loc_constraint.use_x = True
    copy_loc_constraint.use_y = True
    copy_loc_constraint.influence = 1.0 

def main_timer():
    global bvh_folder_path, files, animation_on, adot, anilist, nowpath, target_armature_name, object_name
    print(int((time.time()-startTime)*10)/10, end="\r") # 프로그램 켜놓은 시간 체크
    files = [f for f in os.listdir(bvh_folder_path) if os.path.isfile(os.path.join(bvh_folder_path, f))]
    if len(files) > 1:
        files.sort(key=lambda f: os.path.getmtime(os.path.join(bvh_folder_path, f)))
        old_file_path = os.path.join(bvh_folder_path, files[0]).replace('\\', '/')
        os.remove(old_file_path)
        animation_on = True
        print('bvh획득시간 :',datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    if animation_on and len(files) == 1:
        animation_on = False
        stop_animation()
        nowpath = os.path.join(bvh_folder_path, files[0]).replace('\\', '/')
        get_animation_delete(nowpath)
        make_target(nowpath)
        
        for obj in bpy.context.selected_objects:
            if ('_main_char_' in obj.name):
                obj.hide_viewport = True
                break
        bpy.ops.object.select_all(action='DESELECT')
        
        print('bvh획득시간 :',datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        bpy.app.timers.register(restart_animation, first_interval=0.15)
    
    return 0.05 # 타이머 간격 (초)

def restart_animation():
    global adot, anilist, cur_animation
    bpy.app.timers.unregister(restart_animation)
    play_animation()

# 타이머 등록, 타이머 간격을 주기로 update반복
bpy.app.timers.register(main_timer)
startTime = time.time()
get_animation_delete(first_anim_path) 
make_target(first_anim_path)

for obj in bpy.context.selected_objects:
    if ('_main_char_' in obj.name):
        obj.hide_viewport = True
        break
bpy.ops.object.select_all(action='DESELECT')
        
play_animation()