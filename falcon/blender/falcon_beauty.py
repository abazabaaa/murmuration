# Shaded renders of every pose. exec'd after build/render/measure/look.
import bpy, os, math
from mathutils import Vector
os.makedirs(OUT_DIR, exist_ok=True)                                     # noqa: F821
apply_look(OBJS)                                                        # noqa: F821
eng = beauty_setup()                                                    # noqa: F821
sc = bpy.context.scene
try:
    sc.eevee.taa_render_samples = 48
except Exception:
    pass
cams = {
    'below': look_cam('FalconCam_below34', (0.55, 0.75, -1.75), (0, -0.08, 0), 50),     # noqa: F821  a ground observer's view: below, a little ahead and aside
    'above': look_cam('FalconCam_above34', (1.15, -1.25, 1.05), (0, -0.08, 0), 42),     # noqa: F821
}
for c in cams.values():
    for col in list(c.users_collection): col.objects.unlink(c)
    bpy.data.collections['FalconCams'].objects.link(c)
for n in POSES:                                                         # noqa: F821
    if n.startswith('_') or (ONLY and n not in ONLY): continue          # noqa: F821
    set_pose(OBJS['rig'], POSES[n], OBJS['tail'])                       # noqa: F821
    for v in VIEWS:                                                     # noqa: F821
        render_to(f'{OUT_DIR}/{n}__{v}.png', cams[v], RES)              # noqa: F821
print(eng)
