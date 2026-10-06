# Cycles reference: the measured starling model under the photographed sky, seen from the page camera (step d).
# Run through the starling build (starling/blender/run_headless.py) with bird_build, bird_render, bird_measure and
# starling_look loaded, then this file as `after`, with HDR, REG, SKY_DIR (this directory), OUT (json path),
# N (configurations), SEED, SPP in the globals.
#
# Each configuration puts the bird at a random place in the frame, 60 m out (radiance does not depend on distance
# without haze; haze is added analytically later), with a random heading, a little pitch, a bank that is usually
# small and sometimes a wave roll, and a random pose. A narrow camera at the page camera's position looks straight
# at it; the film is transparent so the alpha gives coverage. Each configuration is rendered with uniform grey
# plumage of albedo 0.03, 0.05 and 0.10 and with the model's own plumage (starling_look). Recorded: the mean
# linear colour over the bird (premultiplied sum / alpha sum), the alpha sum, and the geometry in page axes.
import bpy, json, math, random
from mathutils import Matrix, Vector

exec(open(SKY_DIR + 'bl_world.py').read())                     # noqa: F821
random.seed(SEED)                                             # noqa: F821
sc = bpy.context.scene
for n in ('Camera', 'Light', 'Cube'):
    ob = bpy.data.objects.get(n)
    if ob is not None: bpy.data.objects.remove(ob)
for ob in [o for o in bpy.data.objects if o.type in ('LIGHT', 'CAMERA')]:
    bpy.data.objects.remove(ob)
cycles(SPP)                                                   # noqa: F821
world()
sc.render.film_transparent = True
sc.render.image_settings.file_format = 'OPEN_EXR'; sc.render.image_settings.color_depth = '32'
sc.render.image_settings.color_mode = 'RGBA'
RES = 96
sc.render.resolution_x = sc.render.resolution_y = RES
cam_d = bpy.data.cameras.new('BirdCam'); cam_d.sensor_fit = 'VERTICAL'; cam_d.clip_end = 5000
cam = bpy.data.objects.new('BirdCam', cam_d); sc.collection.objects.link(cam); sc.camera = cam
CAM = Vector((0, 0, CAM_H_M))

rig, tail = OBJS['rig'], OBJS['tail']                         # noqa: F821
meshes = [o for o in bpy.data.objects if o.type == 'MESH' and o.parent == rig]
look = {o.name: list(o.data.materials) for o in meshes}
grey = {}
for a in (.03, .05, .10):
    m = bpy.data.materials.new('grey%.2f' % a); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (a, a, a, 1); b.inputs['Roughness'].default_value = .42
    grey[a] = m


def use(mats):
    for o in meshes:
        o.data.materials.clear()
        for m in (mats[o.name] if isinstance(mats, dict) else [mats]):
            o.data.materials.append(m)


F_PAGE = (800 / math.tan(math.radians(23)))
POSE_NAMES = [k for k in POSES if not k.startswith('_')]      # noqa: F821


def page_dir(col, row):                                       # page camera ray through a pixel of the 3840x1600 sky, Blender axes
    x = (col - 1920) / F_PAGE; y = -(row - 800) / F_PAGE
    d = Vector((x, 1, y)).normalized()                        # camera frame: X right, Y forward, Z up
    return Matrix.Rotation(PITCH, 3, 'X') @ d


def to_page(v):
    return [round(v.x, 5), round(v.z, 5), round(v.y, 5)]


rows = []
for k in range(N):                                            # noqa: F821
    col = random.uniform(200, 3640); row = random.uniform(100, 1150)
    d = page_dir(col, row)
    h = random.uniform(-math.pi, math.pi); pt = math.radians(random.uniform(-12, 12))
    roll = math.radians(random.uniform(-20, 20) if random.random() < .7 else random.uniform(-80, 80))
    pose = random.choice(POSE_NAMES)
    Fw = Vector((math.sin(h) * math.cos(pt), math.cos(h) * math.cos(pt), math.sin(pt)))
    R0 = Fw.cross(Vector((0, 0, 1))).normalized(); U0 = R0.cross(Fw)
    Rr = Matrix.Rotation(roll, 3, Fw)
    R, U = Rr @ R0, Rr @ U0
    M = Matrix((R, Fw, U)).transposed().to_4x4()             # model X right wing, Y bill, Z up
    dist = 60.0
    M.translation = CAM + d * dist
    rig.matrix_world = M
    set_pose(rig, POSES[pose], tail)                          # noqa: F821
    cam.location = CAM
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    cam_d.angle_y = 2 * math.atan(.24 / dist)
    out = {'k': k, 'col': col, 'row': row, 'pose': pose, 'view': to_page(d), 'fwd': to_page(Fw), 'up': to_page(U),
           'right': to_page(R), 'heading': h, 'pitch': pt, 'roll': roll}
    for name, mats in [('g03', grey[.03]), ('g05', grey[.05]), ('g10', grey[.10]), ('look', look)]:
        use(mats)
        sc.render.filepath = OUT + '.tmp.exr'                 # noqa: F821
        bpy.ops.render.render(write_still=True)
        img = bpy.data.images.load(OUT + '.tmp.exr', check_existing=False)   # noqa: F821
        px = list(img.pixels); bpy.data.images.remove(img)
        sr = sg = sb = sa = 0.0
        for i in range(0, len(px), 4):
            sr += px[i]; sg += px[i + 1]; sb += px[i + 2]; sa += px[i + 3]
        out[name] = [sr / max(sa, 1e-9), sg / max(sa, 1e-9), sb / max(sa, 1e-9), sa]
    rows.append(out)
    if k % 10 == 0:
        print('bird', k, pose, [round(x, 4) for x in out['g05'][:3]], 'alpha', round(out['g05'][3], 1), flush=True)
json.dump(rows, open(OUT, 'w'))                               # noqa: F821
print('wrote', OUT, len(rows))
