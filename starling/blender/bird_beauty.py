# Shaded renders of every pose (species-neutral copy of falcon/blender/falcon_beauty.py).
# exec'd after build/render/measure/<species>_look.  Camera distances scale with the full span.
import bpy, os
os.makedirs(OUT_DIR, exist_ok=True)                                     # noqa: F821
apply_look(OBJS)                                                        # noqa: F821
eng = beauty_setup()                                                    # noqa: F821
sc = bpy.context.scene
try:
    sc.eevee.taa_render_samples = 48
except Exception:
    pass
k = P['wing']['half_span'] / 0.5143                                     # noqa: F821  (falcon framing = 1)
tgt = (0, VIEW_CY - 0.03 * k, 0)                                        # noqa: F821
cams = {
    'below': look_cam(PREFIX + 'Cam_below34', (0.55 * k, 0.75 * k, -1.75 * k), tgt, 50),    # noqa: F821  ground observer
    'above': look_cam(PREFIX + 'Cam_above34', (1.15 * k, -1.25 * k, 1.05 * k), tgt, 42),    # noqa: F821
}
coll = bpy.data.collections.get(PREFIX + 'Cams') or bpy.data.collections.new(PREFIX + 'Cams')   # noqa: F821
if coll.name not in sc.collection.children: sc.collection.children.link(coll)
for c in cams.values():
    for col in list(c.users_collection): col.objects.unlink(c)
    coll.objects.link(c)
for n in POSES:                                                         # noqa: F821
    if n.startswith('_') or (ONLY and n not in ONLY): continue          # noqa: F821
    set_pose(OBJS['rig'], POSES[n], OBJS['tail'])                       # noqa: F821
    for v in VIEWS:                                                     # noqa: F821
        render_to(f'{OUT_DIR}/{n}__{v}.png', cams[v], RES)              # noqa: F821
print(eng)
