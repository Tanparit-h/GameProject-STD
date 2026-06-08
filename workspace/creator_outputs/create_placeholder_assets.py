import bpy
import os
from mathutils import Vector

# Set export directory
export_dir = os.getenv("AI_STUDIO_EXPORT_DIR")
if not export_dir:
    export_dir = os.path.join(os.getcwd(), "exports")
os.makedirs(export_dir, exist_ok=True)

# Clear existing objects
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

def create_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color  # RGBA 4 values
    return mat

def create_text_label(text, location, align_x="CENTER", align_y="CENTER"):
    bpy.ops.object.text_add(location=location)
    text_obj = bpy.context.object
    text_obj.data.body = text
    text_obj.data.align_x = align_x
    text_obj.data.align_y = align_y
    text_obj.data.size = 0.05
    text_obj.data.extrude = 0.01
    text_obj.data.bevel_depth = 0.005
    return text_obj

# Create placeholder objects
# 1. Cube (Interactable Box)
cube = bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
cube_obj = bpy.context.object
cube_mat = create_material("Cube_Material", (0.2, 0.4, 0.8, 1.0))
cube_obj.data.materials.append(cube_mat)
cube_label = create_text_label("Interactable Box", (0, 0, 0.75))

# 2. Rectangle (Interactable Door)
door = bpy.ops.mesh.primitive_cube_add(size=1, location=(1.5, 0, 0.5))
door_obj = bpy.context.object
door_obj.scale = (2, 0.2, 1)  # Create rectangle shape
door_mat = create_material("Door_Material", (0.8, 0.2, 0.4, 1.0))
door_obj.data.materials.append(door_mat)
door_label = create_text_label("Interactable Door", (1.5, 0, 0.75))

# 3. Sphere (Interactable Sphere)
sphere = bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(-1.5, 0, 0.5))
sphere_obj = bpy.context.object
sphere_mat = create_material("Sphere_Material", (0.4, 0.8, 0.2, 1.0))
sphere_obj.data.materials.append(sphere_mat)
sphere_label = create_text_label("Interactable Sphere", (-1.5, 0, 0.75))

# Set up camera and light
camera = bpy.ops.object.camera_add(location=(0, -5, 3), rotation=(1.1, 0, 0))
camera_obj = bpy.context.object
bpy.context.scene.camera = camera_obj

light = bpy.ops.object.light_add(type='SUN', location=(0, 5, 5))
light_obj = bpy.context.object
light_obj.data.energy = 5

# Export as GLB
export_path = os.path.join(export_dir, "interactable_placeholders.glb")
bpy.ops.export_scene.gltf(filepath=export_path, export_format="GLB")
print("EXPORTED:", export_path)