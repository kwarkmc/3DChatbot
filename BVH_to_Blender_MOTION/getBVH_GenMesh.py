import bpy, sys, math, os, mathutils 
from typing import Any, Dict, Iterable, List, Tuple, Optional, Sequence

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
    principled_node.inputs['Base Color'].default_value = (0.1, 0.2, 0.7, 1.0)
    principled_node.inputs['Metallic'].default_value = 0.9
    principled_node.inputs['Roughness'].default_value = 0.1
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
    armature_mesh = create_armature_mesh(scene, armature, 'Mesh')
    armature_mesh.data.materials.append(mat)
    ################

