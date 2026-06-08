import bpy
import os
from mathutils import Vector

# ตั้งค่าโฟลเดอร์สำหรับ export
export_dir = os.getenv("AI_STUDIO_EXPORT_DIR")
if not export_dir:
    export_dir = os.path.join(os.getcwd(), "exports")
os.makedirs(export_dir, exist_ok=True)

# ล้าง scene ก่อนสร้าง object ใหม่
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

def create_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color  # RGBA 4 ค่า
    return mat

def create_object(name, shape, position, color, label_text):
    # สร้าง object
    if shape == "Cube":
        bpy.ops.mesh.primitive_cube_add(location=position)
    elif shape == "Door":
        bpy.ops.mesh.primitive_plane_add(location=position)
    elif shape == "Sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(location=position)
    obj = bpy.context.object
    obj.name = name

    # ตั้งค่า material สำหรับ object
    obj_mat = create_material(name + "_Material", color)
    obj.data.materials.append(obj_mat)

    # สร้าง Text Label
    text_obj = bpy.ops.object.text_add(location=position)
    text_obj = bpy.context.object
    text_obj.name = name + "_Label"
    text_obj.data.body = label_text
    text_obj.data.align_x = "CENTER"
    text_obj.data.align_y = "CENTER"

    # แปลง Text เป็น Mesh
    bpy.ops.object.convert(target="MESH")
    text_mesh = bpy.context.object
    text_mesh.name = name + "_Label_Mesh"

    # สร้าง material สำหรับ text
    text_mat = create_material(name + "_Text_Material", (1.0, 1.0, 1.0, 1.0))
    text_mesh.data.materials.append(text_mat)

# สร้าง object ทั้งหมด
create_object("Cube_Object", "Cube", (0, 0, 0.5), (0.2, 0.4, 0.8, 1.0), "Cube")
create_object("Door_Object", "Door", (2, 0, 0.5), (0.8, 0.2, 0.2, 1.0), "Door")
create_object("Sphere_Object", "Sphere", (-2, 0, 0.5), (0.8, 0.8, 0.2, 1.0), "Sphere")

# สร้าง UI Placeholder Text
ui_text = bpy.ops.object.text_add(location=(0, 5, 0))
ui_text = bpy.context.object
ui_text.name = "UI_Label"
ui_text.data.body = "Press E to Interact"
ui_text.data.align_x = "CENTER"
ui_text.data.align_y = "CENTER"

# แปลง Text เป็น Mesh
bpy.ops.object.convert(target="MESH")
ui_mesh = bpy.context.object
ui_mesh.name = "UI_Label_Mesh"

# สร้าง material สำหรับ UI Text
ui_mat = create_material("UI_Text_Material", (1.0, 1.0, 1.0, 1.0))
ui_mesh.data.materials.append(ui_mat)

# ตั้งค่า camera และ light
if not bpy.context.scene.camera:
    bpy.ops.object.camera_add(location=(5, 5, 5), rotation=(1.1, 0, 0))
    bpy.context.scene.camera = bpy.context.object

if not bpy.context.scene.objects.get("Light"):
    bpy.ops.object.light_add(type='SUN', radius=0.1)
    light = bpy.context.object
    light.location = (10, 10, 10)
    light.data.energy = 5

# ตั้งค่า export
export_path = os.path.join(export_dir, "interactive_objects.glb")
bpy.ops.export_scene.gltf(filepath=export_path, export_format="GLB")
print("EXPORTED:", export_path)
print("OBJECT_COUNT:", len(bpy.context.scene.objects))