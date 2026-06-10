import os
import bpy

export_dir = os.getenv("AI_STUDIO_EXPORT_DIR") or os.path.join(os.getcwd(), "exports")
os.makedirs(export_dir, exist_ok=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))
asset = bpy.context.object
asset.name = "ai_office_placeholder_asset"
asset.scale = (0.6, 0.6, 0.6)

material = bpy.data.materials.new("ai_office_placeholder_material")
material.diffuse_color = (0.3, 0.7, 0.9, 1.0)
asset.data.materials.append(material)

target = os.path.join(export_dir, "ai_office_placeholder_asset.glb")
bpy.ops.export_scene.gltf(filepath=target, export_format="GLB")
print(f"EXPORTED: {target}")
