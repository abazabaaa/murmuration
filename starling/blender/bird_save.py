# Save the model as a .blend: glide pose, materials, the dusk world, the ortho and 3/4 cameras, no actions
# and no UI (Blender opens it with the default layout).
# exec'd after build/render/measure/<species>_look with BLEND set; runs bird_beauty.py with no views
# so the cameras and look are made exactly as for the shaded renders.
import bpy
VIEWS = ()
exec(open(BIRD_DIR + 'bird_beauty.py').read())                          # noqa: F821
set_pose(OBJS['rig'], POSES['glide'], OBJS['tail'])                     # noqa: F821
for n in ('Camera', 'Light'):                                           # factory-startup leftovers
    ob = bpy.data.objects.get(n)
    if ob is not None: bpy.data.objects.remove(ob)
bpy.context.scene.camera = bpy.data.objects[PREFIX + 'Cam_below34']     # noqa: F821
bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y = 1200, 800
# write the scene and everything it uses, but no window manager or UI: save_as_mainfile stores the
# user's config path in the window manager's operator record
ids = set(bpy.data.scenes) | set(bpy.data.objects) | set(bpy.data.collections)
bpy.data.libraries.write(BLEND, ids, path_remap='NONE', fake_user=False, compress=True)   # noqa: F821
print('saved', BLEND)
