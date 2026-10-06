"""Build and bake the existing species rigs, including XYZ, in Blender.

Run through the Blender MCP:
  exec(compile(open(PATH).read(), PATH, 'exec'), {'__file__': PATH})
or Blender --background --factory-startup --python motion/bake_motion.py.
Only MotionStarling/MotionFalcon objects and their generated actions are replaced.
Original species files and the user's other scenes are never opened or overwritten.
"""
import copy
import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'motion'
TARGETS = json.loads((OUT / 'reference-targets.json').read_text())
PHASES = [0, .23, .46, .73, .9, 1]
FLAP_KEYS = ['flap_top', 'flap_mid', 'flap_bottom', 'upstroke', 'upstroke_top', 'flap_top']


def mix_pose(a, b, t):
    """Parameter interpolation; rotations are evaluated by Blender before export."""
    out = {'bones': {}, 'fan': {}, 'tail_fan': a.get('tail_fan', 0) * (1-t) + b.get('tail_fan', 0) * t}
    for name in set(a.get('bones', {})) | set(b.get('bones', {})):
        aa, bb = a.get('bones', {}).get(name, {}), b.get('bones', {}).get(name, {})
        out['bones'][name] = {k: aa.get(k, d)*(1-t) + bb.get(k, d)*t for k, d in
                             [('sweep', 0), ('elev', 0), ('twist', 0), ('pitch', 0), ('scale_x', 1), ('scale_z', 1)]}
    aa, bb = a.get('fan', {}), b.get('fan', {})
    out['fan'] = {k: aa.get(k, d)*(1-t) + bb.get(k, d)*t for k, d in
                  [('aft', 0), ('sweep', 0), ('scale_x', 1), ('scale_y', 1)]}
    return out


def slope(h0, h1, d0, d1):
    if d0*d1 <= 0: return 0.0
    w0, w1 = 2*h1+h0, h1+2*h0
    return (w0+w1)/(w0/d0+w1/d1)


def cyclic_curve(xs, ys, t):
    """Periodic monotone Hermite: C1 at closure, no component overshoot."""
    t %= 1
    h = [b-a for a, b in zip(xs, xs[1:])]
    d = [(b-a)/hh for a, b, hh in zip(ys, ys[1:], h)]
    m = [slope(h[-1], h[0], d[-1], d[0])]
    m += [slope(h[i-1], h[i], d[i-1], d[i]) for i in range(1, len(h))]
    m.append(m[0])
    k = next(i for i in range(len(h)) if t < xs[i+1])
    u = (t-xs[k])/h[k]
    return ((2*u**3-3*u*u+1)*ys[k] + (u**3-2*u*u+u)*h[k]*m[k] +
            (-2*u**3+3*u*u)*ys[k+1] + (u**3-u*u)*h[k]*m[k+1])


def flap_pose(poses, t, phases):
    samples = [poses[n] for n in FLAP_KEYS]
    names = set().union(*(p.get('bones', {}) for p in samples))
    out = {'bones': {}, 'fan': {}}
    for name in sorted(names):
        out['bones'][name] = {k: cyclic_curve(phases, [p.get('bones', {}).get(name, {}).get(k, d) for p in samples], t)
                              for k, d in [('sweep', 0), ('elev', 0), ('twist', 0), ('scale_x', 1), ('scale_z', 1)]}
    out['fan'] = {k: cyclic_curve(phases, [p.get('fan', {}).get(k, d) for p in samples], t)
                  for k, d in [('aft', 0), ('sweep', 0), ('scale_x', 1), ('scale_y', 1)]}
    out['tail_fan'] = cyclic_curve(phases, [p.get('tail_fan', 0) for p in samples], t)
    return out


def path_pose(poses, names, times, t):
    if t >= 1: return copy.deepcopy(poses[names[-1]])
    k = next(i for i in range(len(times)-1) if t < times[i+1])
    u = (t-times[k])/(times[k+1]-times[k])
    u = u*u*(3-2*u)
    return mix_pose(poses[names[k]], poses[names[k+1]], u)


def build_species(species):
    prefix = 'MotionStarling' if species == 'starling' else 'MotionFalcon'
    params = ROOT / species / 'blender' / ('params_starling.json' if species == 'starling' else 'params_falcon.json')
    posefile = params.with_name('poses_' + ('starling' if species == 'starling' else 'falcon') + '.json')
    g = {'PARAMS': str(params), 'PREFIX': prefix, '__name__': 'motion_builder'}
    builder = ROOT / 'starling/blender/bird_build.py'
    exec(compile(builder.read_text().replace('OBJS = build()', ''), str(builder), 'exec'), g)
    def clear_ours():
        for ob in list(bpy.data.objects):
            if ob.name.startswith(prefix): bpy.data.objects.remove(ob, do_unlink=True)
    g['clear'] = clear_ours
    objs = g['build']()
    for pb in objs['rig'].pose.bones: pb.rotation_mode = 'QUATERNION'
    return g, objs, json.loads(posefile.read_text()), params, posefile


def points(ob):
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    me = ev.to_mesh()
    result = [ob.matrix_world @ v.co for v in me.vertices]
    ev.to_mesh_clear()
    return result


def tip_height(g, objs, pose):
    g['set_pose'](objs['rig'], pose, objs['tail'])
    tip = points(objs['wings'][0])[2*56*17]
    sh = objs['rig'].matrix_world @ objs['rig'].pose.bones['humerus.R'].head
    return tip.z-sh.z


def fit_starling(g, objs, poses):
    report = []
    for name, goal in [('flap_top', TARGETS['starling']['stroke']['topHeightM']),
                       ('flap_bottom', TARGETS['starling']['stroke']['bottomHeightM'])]:
        before = tip_height(g, objs, poses[name])
        old = poses[name]['bones']['humerus']['elev']
        lo, hi = old-15, old+15
        for _ in range(28):
            angle = (lo+hi)/2
            poses[name]['bones']['humerus']['elev'] = angle
            if tip_height(g, objs, poses[name]) < goal: lo = angle
            else: hi = angle
        actual = tip_height(g, objs, poses[name])
        assert abs(actual-goal) < .0001, (name, actual, goal)
        report.append({'pose': name, 'targetM': goal, 'beforeM': before, 'afterM': actual,
                       'humerusElevBeforeDeg': old, 'humerusElevAfterDeg': angle,
                       'method': 'one-parameter fit of evaluated mesh wingtip to existing side-view landmarks'})
    return report


def topology(objs):
    """Fixed material-point grid, shared by all frames and two draw LODs."""
    slots, high, low = [], [], []
    def slot(ob, idx):
        slots.append((ob, idx)); return len(slots)-1
    def face(dst, v):
        for k in range(1, len(v)-1): dst.append([v[0], v[k], v[k+1]])
    def grid(ob, indices, nr, nc, high_rows=None, high_cols=None, low_rows=None, low_cols=None):
        ids = [[slot(ob, indices(r, c)) for c in range(nc)] for r in range(nr)]
        for dst, rows, cols in [(high, high_rows or list(range(nr)), high_cols or list(range(nc))),
                                (low, low_rows or list(range(nr)), low_cols or list(range(nc)))]:
            for a, b in zip(rows, rows[1:]):
                for c, d in zip(cols, cols[1:]): face(dst, [ids[a][c], ids[a][d], ids[b][d], ids[b][c]])
        return ids
    bodyrings = [0, 6, 12, 20, 28, 36, 42, 48]
    bid = grid(objs['body'], lambda r, c: bodyrings[r]*24+(c%8)*3, 8, 9,
               low_rows=[0, 3, 5, 7], low_cols=[0, 2, 4, 6, 8])
    for dst, cols in [(high, list(range(8))), (low, [0, 2, 4, 6])]:
        for r in [0, 7]: face(dst, [bid[r][c] for c in cols])
    for wing in objs['wings']:
        for layer in [0, 1]:
            low_start = len(low)
            ids = grid(wing, lambda r, c: 2*((r*4)*17+c*8)+layer, 15, 3,
                       low_rows=[0, 5, 10, 14], low_cols=[0, 2])
            if layer == 1: del low[low_start:]  # distant wings are two-sided thin surfaces, not duplicate skins
    for layer in [0, 1]:
        rows, cols = [0, 3, 7, 10], [0, 3, 7, 11, 14]
        grid(objs['tail'], lambda r, c: layer*165+rows[r]*15+cols[c], 4, 5,
             low_rows=[0, 3], low_cols=[0, 2, 4])
        if layer == 1: del low[-4:]
    bill = objs['bill']
    billmap = {v.index: slot(bill, v.index) for v in bill.data.vertices}
    for p in bill.data.polygons: face(high, [billmap[i] for i in p.vertices])
    # Far bill still has volume, but four coarse sides suffice at a few screen pixels.
    bv = points(bill); tip = max(range(len(bv)), key=lambda i: bv[i].y)
    base = [i for i in range(len(bv)) if i != tip]
    extremes = sorted(set([min(base, key=lambda i: bv[i].x), max(base, key=lambda i: bv[i].z),
                           max(base, key=lambda i: bv[i].x), min(base, key=lambda i: bv[i].z)]),
                      key=lambda i: math.atan2(bv[i].z, bv[i].x))
    for a, b in zip(extremes, extremes[1:]+extremes[:1]): face(low, [billmap[tip], billmap[a], billmap[b]])
    return slots, {'near': high, 'far': low}


def sample(g, objs, slots, pose, origin):
    g['set_pose'](objs['rig'], pose, objs['tail'])
    cache = {ob.name: points(ob) for ob in {ob for ob, _ in slots}}
    hs = g['P']['wing']['half_span']
    out = []
    for ob, idx in slots:
        p = cache[ob.name][idx]
        out += [round((p.y-origin)/hs, 5), round(p.x/hs, 5), round(p.z/hs, 5)]
    assert all(math.isfinite(v) for v in out)
    return out


def keyframe(objs, frame):
    for pb in objs['rig'].pose.bones:
        loc, rot, scale = pb.matrix_basis.decompose()
        pb.location, pb.rotation_quaternion, pb.scale = loc, rot, scale
        for key in ['location', 'rotation_quaternion', 'scale']: pb.keyframe_insert(key, frame=frame, group=pb.name)
    objs['tail'].data.shape_keys.key_blocks['Fanned'].keyframe_insert('value', frame=frame)


def fcurves(idblock):
    anim = idblock.animation_data
    if not anim or not anim.action: return []
    action = anim.action
    # Blender 5 layered action API; inspect slots rather than assuming legacy fcurves.
    result = []
    for layer in action.layers:
        for strip in layer.strips:
            bag = strip.channelbag(anim.action_slot)
            if bag: result += list(bag.fcurves)
    return result


def animate(g, objs, poses, phases, species):
    rig, tail = objs['rig'], objs['tail']
    for ob in [rig, tail.data.shape_keys]: ob.animation_data_clear()
    if species == 'starling':
        frames = sorted(set([i/32 for i in range(33)] + phases))
        for t in frames:
            g['set_pose'](rig, flap_pose(poses, t, phases), tail)
            keyframe(objs, 1+t*10)  # 120 fps / 12 Hz; CYCLES repeats the 10-frame wingbeat
        for ob in [rig, tail.data.shape_keys]:
            ob.animation_data.action.name = 'MotionStarling_Flap_12Hz'
            for fc in fcurves(ob):
                for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
                fc.modifiers.new('CYCLES')
    else:
        names, times = ['glide', 'stoop_m', 'stoop_tuck', 'stoop_tuck', 'pullout_early', 'stoop_m', 'glide'], [0, .15, .30, .55, .68, .82, 1]
        for i in range(121):
            t = i/120
            g['set_pose'](rig, path_pose(poses, names, times, t), tail)
            keyframe(objs, 1+t*480)
        for ob in [rig, tail.data.shape_keys]:
            ob.animation_data.action.name = 'MotionFalcon_Dive_4s_EstimatedTiming'
            for fc in fcurves(ob):
                for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'


def bake(species):
    g, objs, poses, params, posefile = build_species(species)
    fit = fit_starling(g, objs, poses) if species == 'starling' else []
    slots, faces = topology(objs)
    origin = 0 if species == 'starling' else -.08
    phases = PHASES if species == 'starling' else [0, .25, .5, .75, .9, 1]
    clips = {}
    resolution = 32 if species == 'starling' else 64
    times = sorted(set([i/resolution for i in range(resolution+1)] + phases))
    clips['flap'] = {'times': times, 'loop': True, 'frames': [sample(g, objs, slots, flap_pose(poses, t, phases), origin) for t in times]}
    for n in poses:
        if not n.startswith('_'):
            clips[n] = {'times': [0], 'loop': False, 'frames': [sample(g, objs, slots, poses[n], origin)]}
    if species == 'falcon':
        for name, keys, knots in [('tuck', ['glide', 'stoop_m', 'stoop_tuck'], [0, .4, 1]),
                                 ('pullout', ['stoop_tuck', 'pullout_early', 'stoop_m', 'glide'], [0, .3, .65, 1])]:
            ts = sorted(set([i/24 for i in range(25)] + knots))
            clips[name] = {'times': ts, 'loop': False,
                           'frames': [sample(g, objs, slots, path_pose(poses, keys, knots, t), origin) for t in ts]}
    # Independent dense samples (not saved as runtime data) bound interpolation error at withheld phases.
    max_error = 0
    for i in range(96):
        t = (i+.5)/96
        exact = sample(g, objs, slots, flap_pose(poses, t, phases), origin)
        k = next(j for j in range(len(times)-1) if t < times[j+1])
        u = (t-times[k])/(times[k+1]-times[k])
        a, b = clips['flap']['frames'][k:k+2]
        max_error = max(max_error, max(math.dist(exact[v:v+3], [a[z]*(1-u)+b[z]*u for z in range(v,v+3)]) for v in range(0,len(exact),3)))
    report = {'fit': fit, 'denseWithheldFlapMaxVertexErrorM': max_error*g['P']['wing']['half_span'],
              'vertices': len(slots), 'trianglesNear': len(faces['near']), 'trianglesFar': len(faces['far']),
              'notValidated': ['live skeletal joint limits', 'raw multi-view video', 'aerodynamic forces'],
              'knownApproximation': 'existing scale_x folding controls retained; feather overlap is not physically solved'}
    assert report['denseWithheldFlapMaxVertexErrorM'] < .003, report
    if species == 'falcon':
        errors = {}
        for name, keys, knots in [('tuck', ['glide', 'stoop_m', 'stoop_tuck'], [0, .4, 1]),
                                 ('pullout', ['stoop_tuck', 'pullout_early', 'stoop_m', 'glide'], [0, .3, .65, 1])]:
            clip = clips[name]; error = 0
            for i in range(96):
                t = (i+.5)/96
                exact = sample(g, objs, slots, path_pose(poses, keys, knots, t), origin)
                k = next(j for j in range(len(clip['times'])-1) if t < clip['times'][j+1])
                u = (t-clip['times'][k])/(clip['times'][k+1]-clip['times'][k])
                a,b = clip['frames'][k:k+2]
                error = max(error, max(math.dist(exact[v:v+3], [a[z]*(1-u)+b[z]*u for z in range(v,v+3)]) for v in range(0,len(exact),3)))
            errors[name] = error*g['P']['wing']['half_span']
        report['denseWithheldTransitionMaxVertexErrorM'] = errors
        assert max(errors.values()) < .003, report

    result = {'halfSpanM': g['P']['wing']['half_span'], 'originM': origin, 'lengthM': g['P']['L'],
              'faces': faces, 'clips': clips, 'reference': TARGETS[species], 'report': report,
              'inputs': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [params, posefile, ROOT/'starling/blender/bird_build.py', OUT/'reference-targets.json']}}
    (OUT / (species+'-motion.json')).write_text(json.dumps(result, separators=(',', ':'))+'\n')
    animate(g, objs, poses, phases, species)
    return result, objs


def main():
    scene = bpy.data.scenes.get('Bird Motion Lab') or bpy.data.scenes.new('Bird Motion Lab')
    if bpy.context.window: bpy.context.window.scene = scene
    data = {'format': 1, 'coordinates': '[forward, right, up] in full-spread half-spans', 'species': {}}
    rigs = {}
    for species in ['starling', 'falcon']:
        data['species'][species], rigs[species] = bake(species)
        print(species, json.dumps(data['species'][species]['report']))
    (OUT/'motion-data.js').write_text('// Generated by motion/bake_motion.py; do not hand edit.\nglobalThis.MURMURATION_MOTION_DATA='+json.dumps(data, separators=(',', ':'))+';\n')
    # Side-by-side in the live scene. Geometry was exported BEFORE these display translations.
    rigs['starling']['rig'].location.x = -.65
    rigs['falcon']['rig'].location.x = .4
    scene.render.fps = 120
    scene.frame_start, scene.frame_end = 1, 481
    scene.unit_settings.system = 'METRIC'
    scene.frame_set(1)
    for ob in scene.objects: ob.select_set(False)
    rig = rigs['falcon']['rig']; rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    rig.show_in_front = True
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                from mathutils import Quaternion
                area.spaces.active.region_3d.view_location = (0, -.1, 0)
                area.spaces.active.region_3d.view_distance = 2.8
    # Save only this scene and its dependencies, never the user’s window-manager history.
    bpy.data.libraries.write(str(OUT/'birds-motion.blend'), {scene}, path_remap='NONE', fake_user=True, compress=True)
    print('Motion scene and browser data written to', OUT)


if __name__ in ['__main__', 'builtins'] or globals().get('RUN_MOTION_BAKE', False): main()
