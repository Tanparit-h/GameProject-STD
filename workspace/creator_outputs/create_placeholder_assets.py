import bpy
import os
from mathutils import Vector

# Set export directory
export_dir = os.getenv("AI_STUDIO_EXPORT_DIR")
if not export_dir:
    export_dir = os.path.join(os.getcwd(), "exports")
os.makedirs(export_dir, exist_ok=True)

# Clear scene
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

def create_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color  # RGBA 4 values
    return mat

# Create objects
# Cube
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
cube = bpy.context.object
cube.name = "Interactable_Cube"
cube.data.materials.append(create_material("Cube_Material", (0.2, 0.4, 0.8, 1.0)))

# Rectangle (scaled cube)
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.5, 0, 0))
rect = bpy.context.object
rect.name = "Interactable_Door"
rect.scale = (2, 1, 0.5)
rect.data.materials.append(create_material("Door_Material", (0.8, 0.2, 0.2, 1.0)))

# Sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(3, 0, 0))
sphere = bpy.context.object
sphere.name = "Interactable_Sphere"
sphere.data.materials.append(create_material("Sphere_Material", (0.8, 0.8, 0.2, 1.0)))

# Add text labels
def add_text_label(obj_name, text_content):
    # Get object position
    obj_pos = Vector((0, 0, 0))
    for obj in bpy.context.scene.objects:
        if obj.name == obj_name:
            obj_pos = obj.location
            break
    # Add text object
    bpy.ops.object.text_add(location=(obj_pos.x, obj_pos.y, obj_pos.z + 0.8))
    text_obj = bpy.context.object
    text_obj.name = f"{obj_name}_Label"
    text_obj.data.body = text_content
    text_obj.data.align_x = "CENTER"
    text_obj.data.align_y = "CENTER"
    # Convert text to mesh
    bpy.ops.object.convert(target="MESH")
    # Assign material
    text_mat = create_material(f"{obj_name}_Label_Material", (0.2, 0.2, 0.2, 1.0))
    text_obj.data.materials.append(text_mat)

add_text_label("Interactable_Cube", "Interactable Cube")
add_text_label("Interactable_Door", "Interactable Door")
add_text_label("Interactable_Sphere", "Interactable Sphere")

# Set camera and light
bpy.ops.object.camera_add(location=(4, 4, 4), rotation=(1.1, 0, 0))
camera = bpy.context.object
camera.name = "Prototype_Camera"
bpy.context.scene.camera = camera

bpy.ops.object.light_add(type='SUN', radius=0.1)
light = bpy.context.object
light.name = "Prototype_Light"
light.location = (4, 4, 8)

# Export as .glb
export_path = os.path.join(export_dir, "interactable_objects.glb")
bpy.ops.export_scene.gltf(filepath=export_path, export_format="GLB")
print("EXPORTED:", export_path)