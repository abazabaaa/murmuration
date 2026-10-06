# Species-neutral copy of falcon/blender/falcon_render.py.
# Render helpers. exec'd after bird_build.py in the same globals.
import bpy, math
from mathutils import Vector, Euler

scene = bpy.context.scene


def ensure_cam(name, loc, rot, ortho=None, lens=50):
    cam = bpy.data.objects.get(name)
    if cam is None:
        cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
        scene.collection.objects.link(cam)
    cam.location = loc; cam.rotation_euler = Euler([math.radians(a) for a in rot])
    if ortho:
        cam.data.type = 'ORTHO'; cam.data.ortho_scale = ortho
    else:
        cam.data.type = 'PERSP'; cam.data.lens = lens
    cam.data.clip_start = .01; cam.data.clip_end = 100
    return cam


def look_cam(name, loc, target=None, lens=50):
    target = target or (0, VIEW_CY, 0)
    cam = ensure_cam(name, loc, (0, 0, 0), None, lens)
    d = Vector(target) - Vector(loc)
    cam.rotation_euler = d.to_track_quat('-Z', 'Z').to_euler()
    return cam


def silhouette_setup():
    scene.render.engine = 'BLENDER_WORKBENCH'
    sh = scene.display.shading
    sh.light = 'FLAT'; sh.color_type = 'SINGLE'; sh.single_color = (0, 0, 0)
    sh.show_object_outline = False; sh.show_cavity = False; sh.show_shadows = False
    sh.background_type = 'VIEWPORT'; sh.background_color = (1, 1, 1)
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'Standard'
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.resolution_percentage = 100


def render_to(path, cam, res=(1600, 1600)):
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.filepath = path
    scene.render.use_stamp_filename = False  # else the PNG metadata records the .blend path
    bpy.ops.render.render(write_still=True)
    return path


# cameras: dorsal (above, head up in frame), ventral (below), front, side
# frame scales with the bird: ortho width 1.215 x full span (falcon: 1.25 m for 1.03 m), centred
# between bill tip and closed tail tip
SPAN_VIEW = P.get('view', {}).get('ortho', round(2.43 * P['wing']['half_span'], 4))          # noqa: F821
VIEW_CY = P.get('view', {}).get('cy', (P['body']['y_bill'] + P['tail']['y_base'] - P['tail']['length']) / 2)   # noqa: F821
D = 6 * SPAN_VIEW
CAMS = {
    'top':   ensure_cam(PREFIX + 'Cam_top',   (0, VIEW_CY, D), (0, 0, 0), SPAN_VIEW),        # noqa: F821
    'below': ensure_cam(PREFIX + 'Cam_below', (0, VIEW_CY, -D), (180, 0, 0), SPAN_VIEW),     # noqa: F821
    'front': ensure_cam(PREFIX + 'Cam_front', (0, D, 0), (90, 0, 180), SPAN_VIEW),           # noqa: F821
    'side':  ensure_cam(PREFIX + 'Cam_side',  (D, VIEW_CY, 0), (90, 0, 90), SPAN_VIEW),      # noqa: F821
}
