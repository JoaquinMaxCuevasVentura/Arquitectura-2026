"""Vidrio de control solar: atajo actual (metálico 0,15) contra capa fina física (Thin Film).
Capa de óxido tipo TiO2 (n ≈ 2,4) de un cuarto de onda a 550 nm: d = 550 / (4 · 2,4) ≈ 57 nm -> reflectancia ≈ 34 %.
Uso: python prueba_vidrio.py -- archivo.blend carpeta camara ancho muestras"""
import math, sys, time
import bpy
from mathutils import Vector
args = sys.argv[sys.argv.index("--") + 1:]
blend, salida, camara, ancho, muestras = args[0], args[1], args[2], int(args[3]), int(args[4])
bpy.ops.wm.open_mainfile(filepath=blend)
sc = bpy.data.scenes["UYUNI_DIA"]
for ob in sc.objects:
    if ob.type == "LIGHT" and ob.data.type == "SUN":
        ob.data.energy *= 0.6
for n in sc.world.node_tree.nodes:
    if n.type == "BACKGROUND":
        n.inputs["Strength"].default_value *= 0.6
cam = bpy.data.objects[camara]
d = cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))
pitch = math.asin(max(-1, min(1, d.z)))
cam.rotation_euler = Vector((d.x, d.y, 0)).normalized().to_track_quat("-Z", "Y").to_euler()
cam.data.shift_y += math.tan(pitch) * cam.data.lens / cam.data.sensor_width
sc.camera = cam
r, cy = sc.render, sc.cycles
r.resolution_x, r.resolution_y, r.resolution_percentage = ancho, round(ancho * 9 / 16), 100
r.image_settings.file_format, r.image_settings.quality = "JPEG", 94
cy.device, cy.samples, cy.use_adaptive_sampling, cy.adaptive_threshold = "CPU", muestras, True, 0.01
cy.use_denoising = True
b = next(n for n in bpy.data.materials["UY_VIDRIO_CONTROL_SOLAR"].node_tree.nodes if n.type == "BSDF_PRINCIPLED")
print("vidrio hoy:", {k: (tuple(b.inputs[k].default_value) if hasattr(b.inputs[k].default_value, "__len__") else b.inputs[k].default_value)
                      for k in ("Base Color", "Metallic", "Roughness", "IOR", "Transmission Weight", "Thin Wall", "Thin Film Thickness", "Thin Film IOR")})


def render(nombre):
    r.filepath = f"{salida}/{camara}_{nombre}.jpg"
    t = time.time()
    bpy.ops.render.render(write_still=True, scene=sc.name)
    print(f"[VIDRIO] {nombre} -> {time.time() - t:.0f} s", flush=True)


render("V1_HOY_METALICO_015")
b.inputs["Metallic"].default_value = 0.0
b.inputs["Transmission Weight"].default_value = 1.0
b.inputs["Thin Film Thickness"].default_value = 57.0
b.inputs["Thin Film IOR"].default_value = 2.4
render("V2_CAPA_FINA_57NM")
