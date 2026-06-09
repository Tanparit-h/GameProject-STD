import bpy
import os
from mathutils import Vector

# ตั้งค่าโฟลเดอร์สำหรับ export
export_dir = os.getenv("AI_STUDIO_EXPORT_DIR")
if not export_dir:
    export_dir = os.path.join(os.getcwd(), "exports")
os.makedirs(export_dir, exist_ok=True)

# ล้าง scene ก่อนสร้าง object
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

def create_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color  # RGBA 4 ค่า
    return mat

# สร้าง Cube Placeholder
cube = bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube_obj = bpy.context.object
cube_obj.scale = (1, 1, 1)
cube_mat = create_material("Cube_Material", (0.0, 0.0, 1.0, 1.0))
cube_obj.data.materials.append(cube_mat)

# สร้าง Door Placeholder (Rectangle)
door = bpy.ops.mesh.primitive_cube_add(location=(2, 0, 0))
door_obj = bpy.context.object
door_obj.scale = (1, 0.2, 1)  # ปรับเป็น Rectangle
door_mat = create_material("Door_Material", (0.0, 1.0, 0.0, 1.0))
door_obj.data.materials.append(door_mat)

# สร้าง Sphere Placeholder
sphere = bpy.ops.mesh.primitive_uv_sphere_add(location=(-2, 0, 0))
sphere_obj = bpy.context.object
sphere_mat = create_material("Sphere_Material", (1.0, 1.0, 0.0, 1.0))
sphere_obj.data.materials.append(sphere_mat)

# สร้าง Text Label สำหรับ Object
def add_text_label(obj, text, align_x="CENTER", align_y="CENTER"):
    bpy.ops.object.text_add(location=obj.location)
    text_obj = bpy.context.object
    text_obj.data.body = text
    text_obj.data.align_x = align_x
    text_obj.data.align_y = align_y
    text_obj.data.size = 20  # ปรับขนาดตัวอักษร
    text_obj.location = obj.location + Vector((0, 0.5, 0))  # ปรับตำแหน่งให้อยู่เหนือ object
    text_mat = create_material("Text_Material", (1.0, 1.0, 1.0, 1.0))
    text_obj.data.materials.append(text_mat)
    return text_obj

# สร้าง Text Label สำหรับ Cube
cube_text = add_text_label(cube_obj, "Cube Placeholder", align_x="CENTER", align_y="CENTER")

# สร้าง Text Label สำหรับ Door
door_text = add_text_label(door_obj, "Door Placeholder", align_x="CENTER", align_y="CENTER")

# สร้าง Text Label สำหรับ Sphere
sphere_text = add_text_label(sphere_obj, "Sphere Placeholder", align_x="CENTER", align_y="CENTER")

# ตั้งค่า camera และ light
bpy.ops.object.camera_add(location=(5, 5, 5), rotation=(1.1, 0, 0))
camera = bpy.context.object
bpy.context.scene.camera = camera

bpy.ops.object.light_add(type='SUN', radius=0.1)
light = bpy.context.object
light.data.energy = 5

# ปรับการ render
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'GPU'

# สร้างไฟล์ export
export_path = os.path.join(export_dir, "door_placeholder.glb")
bpy.ops.export_scene.gltf(filepath=export_path, export_format="GLB")
print("EXPORTED:", export_path)