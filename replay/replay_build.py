# Builds a 3D replay of a stretch of a murmuration.html run in Blender, to see where the falcon really was
# relative to the flock when it seemed to fly through it on screen.
#
#   node murmuration-falcon.js 80 "seed=1&n=400" --export=75.5:80          -> replay/out/replay_....json
#   blender --background --factory-startup --python replay/replay_build.py -- replay/out/replay_....json [--at=T] [--anim]
#
# Writes next to the JSON: <name>.blend (scrub the timeline, orbit freely) and stills from four cameras at the
# frame where the falcon is closest to a bird: the page's own camera, from above, from the side, and an orbit.
# --anim also renders the orbit camera over the whole window as <name>_orbit.mp4.
# Inside a live Blender (MCP): set REPLAY = "<path to json>" in the globals and exec this file; it then only
# builds the scene.
#
# Axes: the page has x right, y up, z away from the viewer (world units of 0.5 m). Blender gets
# (X, Y, Z) = (x, z, y) * 0.5, so the page camera looks along +Y with X right and Z up, as on screen.
# Bird colours, as in the page's ?inset: grey calm, yellow alarmed, red dodging, blue rolling in a wave,
# magenta fleeing a flash expansion. Falcon path colours: red stoop, orange climb, cyan position, grey leave.
import bpy, bmesh, json, math, os, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
SRC = globals().get('REPLAY') or argv[0]
ANIM = '--anim' in argv
AT = next((float(a[5:]) for a in argv if a.startswith('--at=')), None)   # --at=T: stills at time T, not at the closest approach
LIVE = 'REPLAY' in globals()
D = json.load(open(SRC))
meta, U = D['meta'], D['meta']['unit_m']
NB, NF = meta['N'], len(D['t'])
OUT = os.path.splitext(SRC)[0]

def V(p):                                      # page (x, y, z) in world units -> Blender metres
    return Vector((p[0] * U, p[2] * U, p[1] * U))

STATE_COL = [(1, (1, .15, .15)), (8, (1, .2, 1)), (4, (.35, .6, 1)), (2, (1, .82, .25))]   # checked in this order
MODE_COL = {'stoop': (1, .3, .25), 'climb': (1, .6, .2), 'position': (.35, .8, 1), 'leave': (.7, .7, .75)}

def clear():                                   # only what this script made
    for ob in [o for o in bpy.data.objects if o.name.startswith('Replay_')]:
        bpy.data.objects.remove(ob, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for b in [b for b in coll if b.name.startswith('Replay_') and b.users == 0]:
            coll.remove(b)

def material(name, col=None, attr=None, emit=.0):
    m = bpy.data.materials.new('Replay_' + name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    if attr:
        a = nt.nodes.new('ShaderNodeVertexColor'); a.layer_name = attr
        nt.links.new(a.outputs['Color'], bsdf.inputs['Base Color'])
        if emit:
            nt.links.new(a.outputs['Color'], bsdf.inputs['Emission Color']); bsdf.inputs['Emission Strength'].default_value = emit
    else:
        bsdf.inputs['Base Color'].default_value = (*col, 1)
        if emit:
            bsdf.inputs['Emission Color'].default_value = (*col, 1); bsdf.inputs['Emission Strength'].default_value = emit
    bsdf.inputs['Roughness'].default_value = .8
    return m

def link(ob):
    bpy.context.scene.collection.objects.link(ob)
    return ob

def key_visible(ob, f):                        # shown on frame f only
    for fr, hide in ((f - 1, True), (f, False), (f + 1, True)):
        ob.hide_viewport = ob.hide_render = hide
        ob.keyframe_insert('hide_viewport', frame=fr); ob.keyframe_insert('hide_render', frame=fr)

def build():
    clear()
    if not LIVE:                               # --factory-startup scene: drop its cube, light and camera
        for n in ('Cube', 'Light', 'Camera'):
            if n in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[n], do_unlink=True)
    sc = bpy.context.scene
    om = bpy.data.meshes.new('Replay_observer')   # where the page's camera stands: a 1 m post
    om.from_pydata([(0, 0, 0), (0, 0, meta['cam']['CAM_H'] * U)], [(0, 1)], [])
    ob = link(bpy.data.objects.new('Replay_observer', om))
    ob.modifiers.new('skin', 'SKIN'); ob.data.materials.append(material('observer', (.9, .2, .9), emit=1))
    sc.frame_start, sc.frame_end = 0, NF - 1
    sc.render.fps = meta['hz']
    birdMat = material('birds', attr='col', emit=.35)
    s = .25                                    # glyph half-size, m (birds are drawn about twice life size on the page too)
    octa = [(s, 0, 0), (-s, 0, 0), (0, s, 0), (0, -s, 0), (0, 0, s * .5), (0, 0, -s * .5)]
    faces = [(0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)]
    for f in range(NF):                        # one mesh per frame, shown only on its frame: scrubs without handlers
        pos, st = D['birds']['pos'][f], D['birds']['state'][f]
        verts, fcs, cols = [], [], []
        for i in range(NB):
            c = V(pos[3 * i:3 * i + 3]); b = len(verts)
            verts += [(c.x + o[0], c.y + o[1], c.z + o[2]) for o in octa]
            fcs += [(b + p, b + q, b + r) for p, q, r in faces]
            col = next((cc for bit, cc in STATE_COL if st[i] & bit), (.78, .78, .82))
            cols += [col] * 6
        me = bpy.data.meshes.new(f'Replay_birds_{f:04d}')
        me.from_pydata(verts, [], fcs)
        ca = me.color_attributes.new('col', 'FLOAT_COLOR', 'POINT')
        for k, c in enumerate(cols): ca.data[k].color = (*c, 1)
        me.materials.append(birdMat)
        key_visible(link(bpy.data.objects.new(f'Replay_birds_{f:04d}', me)), f)

    # Falcon: a flat wedge pointing along its velocity, keyframed; a drop line to the ground; its path by mode.
    fm = bpy.data.meshes.new('Replay_falcon')
    fm.from_pydata([(0, .6, 0), (-.55, -.3, 0), (.55, -.3, 0), (0, -.25, .12)], [], [(0, 1, 3), (0, 3, 2), (0, 2, 1), (1, 2, 3)])
    fm.materials.append(material('falcon', (.05, .02, .03)))
    fal = link(bpy.data.objects.new('Replay_falcon', fm))
    fal.rotation_mode = 'QUATERNION'
    dm = bpy.data.meshes.new('Replay_drop'); dm.from_pydata([(0, 0, 0), (0, 0, -1)], [(0, 1)], [])
    drop = link(bpy.data.objects.new('Replay_drop', dm))
    for f in range(NF):
        p, v = D['falcon']['pos'][f], D['falcon']['vel'][f]
        if p is None: continue
        P = V(p); fal.location = P
        fal.rotation_quaternion = V(v).to_track_quat('Y', 'Z')
        fal.keyframe_insert('location', frame=f); fal.keyframe_insert('rotation_quaternion', frame=f)
        drop.location = P; drop.scale = (1, 1, max(P.z, .01))
        drop.keyframe_insert('location', frame=f); drop.keyframe_insert('scale', frame=f)
    runs, cur = [], None                       # one polyline per stretch of a single mode
    for f in range(NF):
        p, md = D['falcon']['pos'][f], D['falcon']['mode'][f]
        if p is None: cur = None; continue
        if not cur or cur[0] != md:
            if cur: cur[1].append(V(p))       # join the stretches
            cur = (md, [V(p)]); runs.append(cur)
        else: cur[1].append(V(p))
    for k, (md, pts) in enumerate(runs):
        cu = bpy.data.curves.new(f'Replay_path_{k}', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = .06
        sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
        for j, q in enumerate(pts): sp.points[j].co = (*q, 1)
        cu.materials.append(material(f'path_{md}', MODE_COL.get(md, (1, 1, 1)), emit=1))
        link(bpy.data.objects.new(f'Replay_path_{k}', cu))

    # Ground at y = 0 with a 10 m grid, under a high sun, so every bird and the falcon cast a shadow below.
    cen = [sum((V(D['birds']['pos'][f][3 * i:3 * i + 3]) for i in range(NB)), Vector()) / NB for f in range(NF)]   # flock centre per frame
    mid = cen[NF // 2]
    gm = bpy.data.meshes.new('Replay_ground')
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=40, y_segments=40, size=200); bm.to_mesh(gm); bm.free()
    g = link(bpy.data.objects.new('Replay_ground', gm)); g.location = (mid.x, mid.y, 0)
    g.data.materials.append(material('ground', (.32, .32, .30)))
    grid = link(bpy.data.objects.new('Replay_grid', gm.copy())); grid.location = (mid.x, mid.y, .02)
    w = grid.modifiers.new('wire', 'WIREFRAME'); w.thickness = .08
    grid.data.materials.clear(); grid.data.materials.append(material('grid', (.16, .16, .16)))
    sun = bpy.data.lights.new('Replay_sun', 'SUN'); sun.energy = 2.2; sun.angle = .01
    so = link(bpy.data.objects.new('Replay_sun', sun)); so.rotation_euler = (math.radians(8), math.radians(4), 0)
    w = bpy.data.worlds.get('Replay_world') or bpy.data.worlds.new('Replay_world')
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND'); bg.inputs[0].default_value = (.42, .45, .52, 1); bg.inputs[1].default_value = .7
    sc.world = w

    # Cameras: the page's (to check the export), from above, from the side, and an orbit round the flock.
    c = meta['cam']
    cam = bpy.data.cameras.new('Replay_cam_page'); cam.sensor_fit = 'VERTICAL'
    cam.angle_y = 2 * math.atan(c['H'] / 2 / c['f']); cam.clip_end = 2000
    pc = link(bpy.data.objects.new('Replay_cam_page', cam))
    pc.location = (0, 0, c['CAM_H'] * U); pc.rotation_euler = (math.pi / 2 + c['pitch'], 0, 0)
    ext = max((V(D['birds']['pos'][NF // 2][3 * i:3 * i + 3]) - mid).length for i in range(NB))
    fp = [V(p) for p in D['falcon']['pos'] if p]
    span = max([ext] + [(q - mid).length for q in fp]) * 2 + 20
    cams = {}
    for name, rot, off in (('top', (0, 0, 0), (0, 0, 300)), ('side', (math.pi / 2, 0, math.pi / 2), (300, 0, 0))):
        cd = bpy.data.cameras.new('Replay_cam_' + name); cd.type = 'ORTHO'; cd.ortho_scale = span; cd.clip_end = 2000
        ob = link(bpy.data.objects.new('Replay_cam_' + name, cd)); ob.rotation_euler = rot
        for f in range(NF):
            ob.location = cen[f] + Vector(off); ob.keyframe_insert('location', frame=f)
        cams[name] = ob
    piv = link(bpy.data.objects.new('Replay_orbit_pivot', None))
    for f in range(NF):
        piv.location = cen[f]; piv.rotation_euler = (0, 0, 2 * math.pi * f / NF)
        piv.keyframe_insert('location', frame=f); piv.keyframe_insert('rotation_euler', frame=f)
    od = bpy.data.cameras.new('Replay_cam_orbit'); od.lens = 35; od.clip_end = 2000
    oc = link(bpy.data.objects.new('Replay_cam_orbit', od)); oc.parent = piv
    oc.location = (0, -span * .9, span * .35); oc.rotation_euler = (math.radians(70), 0, 0)
    cams['page'], cams['orbit'] = pc, oc
    for ob in [o for o in bpy.data.objects if o.name.startswith('Replay_')]:
        if ob.animation_data and ob.animation_data.action:
            for fc in getattr(ob.animation_data.action, 'fcurves', []):
                for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT' if fc.data_path.startswith('hide') else 'LINEAR'
    for mk, e in enumerate(D['events']):       # stoops, strikes and wave pulses on the timeline
        f = min(range(NF), key=lambda k: abs(D['t'][k] - e['t']))
        sc.timeline_markers.new(e['type'], frame=f)
    sc.camera = cams['orbit']
    try: sc.view_settings.view_transform = 'Standard'   # keep the state colours as given
    except TypeError as e: print(e)
    return cams

def check_page_camera(cam):                    # the page's own projection of a few birds vs Blender's camera
    from bpy_extras.object_utils import world_to_camera_view
    sc, c = bpy.context.scene, meta['cam']
    sc.render.resolution_x, sc.render.resolution_y = int(c['W']), int(c['H'])
    bpy.context.view_layer.update()            # matrix_world is stale until the depsgraph is evaluated
    err = 0
    for e in D['check']:
        f = min(range(NF), key=lambda k: abs(D['t'][k] - e['t']))
        p = V(D['birds']['pos'][f][3 * e['i']:3 * e['i'] + 3])
        n = world_to_camera_view(sc, cam, p)
        err = max(err, math.hypot(n.x * c['W'] - e['sx'], (1 - n.y) * c['H'] - e['sy']))
    print(f'page camera vs page projection: largest error {err:.2f} px over {len(D["check"])} points')
    return err

def closest_frame():
    best, bf = 1e9, 0
    for f in range(NF):
        p = D['falcon']['pos'][f]
        if p is None: continue
        pos = D['birds']['pos'][f]
        d = min(math.dist(p, pos[3 * i:3 * i + 3]) for i in range(NB))
        if d < best: best, bf = d, f
    return bf, best * U

def render(cams):
    sc = bpy.context.scene
    try: sc.render.engine = 'BLENDER_EEVEE'
    except TypeError as e: print(e)
    f, d = closest_frame()
    print(f'closest approach: frame {f} (t {D["t"][f]:.2f} s), nearest bird {d:.2f} m, falcon mode {D["falcon"]["mode"][f]}')
    if AT is not None:
        f = min(range(NF), key=lambda k: abs(D['t'][k] - AT))
        print(f'stills at frame {f} (t {D["t"][f]:.2f} s), falcon mode {D["falcon"]["mode"][f]}')
    sc.frame_set(f)
    for name, ob in cams.items():
        sc.camera = ob
        c = meta['cam']
        sc.render.resolution_x, sc.render.resolution_y = (int(c['W']), int(c['H'])) if name == 'page' else (1200, 900)
        sc.render.filepath = f'{OUT}_{name}.png'
        bpy.ops.render.render(write_still=True)
    if ANIM:
        sc.camera = cams['orbit']; sc.render.resolution_x, sc.render.resolution_y = 960, 720
        sc.render.image_settings.media_type = 'VIDEO' if hasattr(sc.render.image_settings, 'media_type') else sc.render.image_settings.file_format
        try: sc.render.image_settings.file_format = 'FFMPEG'
        except TypeError as e: print(e)
        sc.render.ffmpeg.format = 'MPEG4'; sc.render.ffmpeg.codec = 'H264'
        sc.render.filepath = f'{OUT}_orbit.mp4'
        bpy.ops.render.render(animation=True)

cams = build()
check_page_camera(cams['page'])
if not LIVE:
    render(cams)
    bpy.context.scene.frame_set(closest_frame()[0])
    bpy.ops.wm.save_as_mainfile(filepath=OUT + '.blend')
    print('wrote', OUT + '.blend')
