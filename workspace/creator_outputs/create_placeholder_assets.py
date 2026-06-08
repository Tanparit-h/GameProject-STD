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
    # Convert text to mesh
    bpy.ops.object.convert(target="MESH")
    return text_obj

# Create placeholder objects
# Cube (interactable object)
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube = bpy.context.object
cube.name = "Cube_Interactive"
cube.scale = (0.5, 0.5, 0.5)
cube.data.materials.append(create_material("Cube_Material", (0.2, 0.4, 0.8, 1.0)))

# Rectangle (door) - using scaled cube
bpy.ops.mesh.primitive_cube_add(location=(2, 0, 0))
door = bpy.context.object
door.name = "Door_Rectangle"
door.scale = (1.5, 0.2, 0.2)
door.data.materials.append(create_material("Door_Material", (0.8, 0.2, 0.4, 1.0)))

# Sphere (interactable object)
bpy.ops.mesh.primitive_uv_sphere_add(location=(0, -2, 0))
sphere = bpy.context.object
sphere.name = "Sphere_Interactive"
sphere.scale = (0.5, 0.5, 0.5)
sphere.data.materials.append(create_material("Sphere_Material", (0.4, 0.8, 0.2, 1.0)))

# Create UI text labels
ui_text = create_text_label("Press E to interact", (0, 3, 0), align_x="CENTER", align_y="CENTER")
ui_text.name = "UI_Text"
ui_text.scale = (2, 2, 2)
ui_text.data.materials.append(create_material("UI_Text_Material", (0.1, 0.1, 0.1, 1.0)))

# Set camera and light
if not bpy.data.cameras:
    bpy.ops.object.camera_add(location=(0, 0, 3))
    camera = bpy.context.object
    camera.rotation_euler = (1.1, 0, 0)
    bpy.context.scene.camera = camera

if not bpy.data.lights:
    bpy.ops.object.light_add(type='SUN', radius=0.1)
    light = bpy.context.object
    light.location = (0, 0, 5)

# Set active objects for export
bpy.context.view_layer.objects.active = cube
for obj in [cube, door, sphere, ui_text]:
    obj.select_set(True)

# Export as GLB
export_path = os.path.join(export_dir, "interactables_prototype.glb")
bpy.ops.export_scene.gltf(filepath=export_path, export_format="GLB")
print("EXPORTED:", export_path)