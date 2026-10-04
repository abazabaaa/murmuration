# Render helpers for the falcon. exec'd after falcon_build.py in the same globals.
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


def look_cam(name, loc, target=(0, -0.05, 0), lens=50):
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
    bpy.ops.render.render(write_still=True)
    return path


# cameras: dorsal (above, head up in frame), ventral (below), front, side
SPAN_VIEW = 1.25
CAMS = {
    'top':   ensure_cam('FalconCam_top',   (0, -0.05, 3), (0, 0, 0), SPAN_VIEW),
    'below': ensure_cam('FalconCam_below', (0, -0.05, -3), (180, 0, 0), SPAN_VIEW),
    'front': ensure_cam('FalconCam_front', (0, 3, 0), (90, 0, 180), SPAN_VIEW),
    'side':  ensure_cam('FalconCam_side',  (3, -0.05, 0), (90, 0, 90), SPAN_VIEW),
}
