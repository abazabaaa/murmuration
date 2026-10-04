# Export the peregrine's plan-view outline, vertex for vertex across poses, for murmuration.html.
#
#   /Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
#       --python falcon/blender/export_outline.py -- [--out falcon/outline/peregrine-outline.json] \
#       [--blend falcon/peregrine.blend] [--diag DIR] [--render DIR] [--wing-points 52]
#
# Builds the model from falcon_build.py + params_falcon.json (never opens peregrine.blend), applies
# every pose in poses_falcon.json and reads the deformed vertices with Subsurf disabled, so vertex
# index i is the same material point in every pose.  Everything is divided by the full-spread
# half-span, the same divisor for every pose, and written as flat [a, w, a, w, ...] lists:
# a along the body (forward +, measured from A_ORIGIN_M), w across the span (right +).
#
#   --blend   also save a clean .blend in the glide pose (materials, cameras, no actions)
#   --diag    write full-resolution chains, in-between rig poses and face-flip counts (diag.json)
#   --render  render each pose's top silhouette there, to compare with renders/silhouettes
import bpy, sys, os, json, math, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
FALCON = os.path.dirname(HERE)

# Forward position (model y, metres) that the page treats as the bird's position: the area
# centroid of the whole glide silhouette (renders/silhouettes/glide__top.png gives -0.081 m), 8 cm
# behind the shoulder line.  The bill tip is at +0.127 m and the closed tail tip at -0.340 m.
A_ORIGIN_M = -0.08
KEYS = ['glide', 'stoop_m', 'pullout_early', 'stoop_tuck']     # the dive, in order of folding

ap = argparse.ArgumentParser()
ap.add_argument('--out', default=os.path.join(FALCON, 'outline', 'peregrine-outline.json'))
ap.add_argument('--blend')
ap.add_argument('--diag')
ap.add_argument('--render')
ap.add_argument('--wing-points', type=int, default=52)
ap.add_argument('--tol', type=float, default=0.0008, help='body / tail simplification tolerance, half-spans')
args = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])

g = {'PARAMS': os.path.join(HERE, 'params_falcon.json'), 'POSES_PATH': os.path.join(HERE, 'poses_falcon.json'),
     '__name__': 'falcon'}
for f in ('falcon_build.py', 'falcon_render.py', 'falcon_measure.py', 'falcon_look.py'):
    exec(compile(open(os.path.join(HERE, f)).read(), f, 'exec'), g)
P, POSES, OBJS, set_pose = g['P'], g['POSES'], g['OBJS'], g['set_pose']
POSE_NAMES = [n for n in POSES if not n.startswith('_')]
HS = P['wing']['half_span']
rig, tail = OBJS['rig'], OBJS['tail']
wingR, body, bill = OBJS['wings'][0], OBJS['body'], OBJS['bill']
meshes = [body, bill, tail] + OBJS['wings']

# metrics as falcon_sheet.py takes them, before the look adds Subsurf and again after
metrics = {'no_subsurf': {}, 'subsurf': {}}
for n in POSE_NAMES:
    metrics['no_subsurf'][n] = {k: round(v, 3) for k, v in g['pose_and_measure'](n).items()}
g['apply_look'](OBJS)
g['beauty_setup']()
for n in POSE_NAMES:
    metrics['subsurf'][n] = {k: round(v, 3) for k, v in g['pose_and_measure'](n).items()}

if args.render:                                   # top silhouettes exactly as falcon_sheet.py renders them
    os.makedirs(args.render, exist_ok=True)
    engine, vt = bpy.context.scene.render.engine, bpy.context.scene.view_settings.view_transform
    g['silhouette_setup']()
    for n in POSE_NAMES:
        set_pose(rig, POSES[n], tail)
        g['render_to'](os.path.join(args.render, f'{n}__top.png'), g['CAMS']['top'], (1200, 1200))
    bpy.context.scene.render.engine = engine
    bpy.context.scene.view_settings.view_transform = vt


def subsurf(on):
    for ob in meshes:
        for md in ob.modifiers:
            if md.type == 'SUBSURF': md.show_viewport = on


def deformed(ob):                                 # world-space XY of every vertex, armature + shape keys applied
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    assert len(me.vertices) == len(ob.data.vertices), (ob.name, 'vertex count changed: is Subsurf still on?')
    mw = ob.matrix_world
    out = [(mw @ v.co) for v in me.vertices]
    out = [(p.x, p.y) for p in out]
    ev.to_mesh_clear()
    return out


NU, NC = 56, 16                                   # wing grid: stations root..tip, chord LE..TE (falcon_build.build_wing)
def top(i, j): return 2 * (i * (NC + 1) + j)
# leading edge root -> tip, trailing edge tip -> root; the tip station is one point (LE = TE there)
WING_CHAIN = [top(i, 0) for i in range(NU + 1)] + [top(i, NC) for i in range(NU - 1, -1, -1)]


def wing_chain(): v = deformed(wingR); return [v[k] for k in WING_CHAIN]


def flipped_faces():                 # top-surface quads whose plan-view orientation is reversed
    v = deformed(wingR); n = 0; area = 0.0; total = 0.0
    for i in range(NU):
        for j in range(NC):
            q = [v[top(i, j)], v[top(i, j + 1)], v[top(i + 1, j + 1)], v[top(i + 1, j)]]
            a = .5 * sum(q[k][0] * q[(k + 1) % 4][1] - q[(k + 1) % 4][0] * q[k][1] for k in range(4))
            total += abs(a)
            if a < 0: n += 1; area -= a           # this loop is counter-clockwise (positive) at rest
    return n, area, total


def lerp_pose(a, b, t):                           # interpolate the pose parameters, as the rig would move
    out = {'bones': {}, 'tail_fan': a.get('tail_fan', 0) * (1 - t) + b.get('tail_fan', 0) * t}
    for bn in set(a.get('bones', {})) | set(b.get('bones', {})):
        sa, sb = a.get('bones', {}).get(bn, {}), b.get('bones', {}).get(bn, {})
        out['bones'][bn] = {k: sa.get(k, d) * (1 - t) + sb.get(k, d) * t
                            for k, d in (('sweep', 0), ('elev', 0), ('twist', 0), ('scale_x', 1), ('scale_z', 1))}
    fa, fb = a.get('fan') or {}, b.get('fan') or {}
    out['fan'] = {k: fa.get(k, d) * (1 - t) + fb.get(k, d) * t
                  for k, d in (('aft', 0), ('sweep', 0), ('scale_x', 1), ('scale_y', 1))}
    return out


def seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    d2 = dx * dx + dy * dy
    t = 0 if d2 < 1e-18 else min(1, max(0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / d2))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def joint_simplify(chains, n=None, tol=None, keep=()):
    """Pick one index subset for several corresponding chains: greedily add the vertex that is
    furthest (worst case over the chains) from the polyline through the vertices kept so far,
    measured against the segment spanning that vertex's own index interval, so a kept vertex is
    the same material point in every chain.  Stop at n points or when the worst miss is < tol."""
    m = len(chains[0])
    kept = sorted({0, m - 1, *keep})
    while True:
        worst, wi = -1, None
        for a, b in zip(kept, kept[1:]):
            for i in range(a + 1, b):
                d = max(seg_dist(c[i], c[a], c[b]) for c in chains)
                if d > worst: worst, wi = d, i
        if wi is None or (n is not None and len(kept) >= n) or (tol is not None and worst < tol):
            return kept, max(worst, 0)
        kept = sorted(kept + [wi])


subsurf(False)

# ---- wing: every pose, one shared subset of the 113-point chain
full = {}
flips = {}
for n in POSE_NAMES:
    set_pose(rig, POSES[n], tail)
    full[n] = wing_chain()
    flips[n] = flipped_faces()
wing_idx, wing_miss = joint_simplify([full[n] for n in POSE_NAMES], n=args.wing_points, keep=(NU,))

# ---- body (never posed) and bill; tail closed and fanned
set_pose(rig, POSES['glide'], tail)
bv, billv = deformed(body), deformed(bill)
ring = [bv[i * 24] for i in range(49)]            # right-most point of each ring, nose -> rump


def body_halfwidth(y):
    for a, b in zip(ring, ring[1:]):
        if b[1] <= y <= a[1]:
            t = (a[1] - y) / max(a[1] - b[1], 1e-12)
            return a[0] + (b[0] - a[0]) * t
    return 0.0


tip = max(billv, key=lambda p: p[1])
bill_edge = sorted({(round(x, 6), round(y, 6)) for x, y in billv if x > 1e-5 and x > body_halfwidth(y) + 1e-5 and y < tip[1]},
                   key=lambda p: -p[1])
hull = []                                         # keep only the bill points on the outer (right) profile
for p in bill_edge:
    if not hull or p[0] > hull[-1][0]: hull.append(p)
ring_out = [p for p in ring if not hull or p[1] < hull[-1][1]]
body_chain = [(0.0, tip[1])] + hull + ring_out
body_idx, body_miss = joint_simplify([body_chain], tol=args.tol * HS)

TAIL_CHAIN = [i * 15 + 14 for i in range(11)] + [10 * 15 + j for j in range(13, 6, -1)]
key = tail.data.shape_keys.key_blocks['Fanned']
tails = []
for val in (0.0, 1.0):
    key.value = val; bpy.context.view_layer.update()
    v = deformed(tail); tails.append([v[k] for k in TAIL_CHAIN])
tail_idx, tail_miss = joint_simplify(tails, tol=args.tol * HS, keep=(10,))


def flat(pts, idx=None):
    pts = pts if idx is None else [pts[i] for i in idx]
    out = []
    for x, y in pts:
        out += [round((y - A_ORIGIN_M) / HS, 3) + 0.0, round(x / HS, 3) + 0.0]
    return out


# where each key sits in the 0..1 dive: spaced by how far the outline moves between keys (rms over
# the chain), so the shape changes at an even rate
legs = [math.sqrt(sum((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 for p, q in zip(full[a], full[b])) / len(full[a]))
        for a, b in zip(KEYS, KEYS[1:])]
knots = [round(sum(legs[:k]) / sum(legs), 2) for k in range(len(KEYS))]

doc = {
    'source': 'falcon/blender/export_outline.py: deformed top-surface vertices of the headless build, Subsurf off, plan view',
    'units': 'half-spans (halfSpanM); flat [a, w] pairs, a forward from aOriginM, w to the right; right side only',
    'halfSpanM': round(HS, 4),
    'aOriginM': A_ORIGIN_M,
    'keys': KEYS,
    'knots': knots,
    'wingChainIndex': wing_idx,
    'wingMaxMiss': round(wing_miss / HS, 4),
    'wing': {n: flat(full[n], wing_idx) for n in POSE_NAMES},
    'body': flat(body_chain, body_idx),
    'tail': flat(tails[0], tail_idx),
    'tailFan': flat(tails[1], tail_idx),
    'tailFanOfPose': {n: POSES[n].get('tail_fan', 0) for n in POSE_NAMES},
}
os.makedirs(os.path.dirname(args.out), exist_ok=True)
with open(args.out, 'w') as fh:
    fh.write('{\n' + ',\n'.join(
        ' ' + json.dumps(k) + ': ' + (json.dumps(v, separators=(',', ':')) if k not in ('wing',) else
                                      '{\n' + ',\n'.join('  ' + json.dumps(n) + ': ' + json.dumps(c, separators=(',', ':')) for n, c in v.items()) + '\n }')
        for k, v in doc.items()) + '\n}\n')
print('OUTLINE', args.out, 'wing points', len(wing_idx), 'max miss (half-spans)', round(wing_miss / HS, 4),
      'body', len(body_idx), 'tail', len(tail_idx))
print('FLIPPED top-surface quads (count, area m2, total m2):', json.dumps(flips))

if args.diag:
    os.makedirs(args.diag, exist_ok=True)
    diag = {'halfSpanM': HS, 'aOriginM': A_ORIGIN_M, 'metrics': metrics, 'flips': flips, 'full': full,
            'body_chain': body_chain, 'bill': billv, 'tails': tails, 'between': {}, 'miss_vs_n': {}}
    for n in (32, 40, 48, 52, 56, 64, 80):
        diag['miss_vs_n'][n] = joint_simplify([full[p] for p in POSE_NAMES], n=n, keep=(NU,))[1] / HS
    pairs = [('glide', 'stoop_tuck')] + list(zip(KEYS, KEYS[1:]))
    for a, b in pairs:                             # what the rig does between two poses
        for t in (.25, .5, .75):
            set_pose(rig, lerp_pose(POSES[a], POSES[b], t), tail)
            diag['between'][f'{a}>{b}@{t}'] = {'chain': wing_chain(), 'flips': flipped_faces()}
    json.dump(diag, open(os.path.join(args.diag, 'diag.json'), 'w'))

if args.blend:
    subsurf(True)
    set_pose(rig, POSES['glide'], tail)
    cams = bpy.data.collections.get('FalconCams') or bpy.data.collections.new('FalconCams')
    if cams.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(cams)
    for name, loc, lens in (('FalconCam_below34', (0.55, 0.75, -1.75), 50), ('FalconCam_above34', (1.15, -1.25, 1.05), 42)):
        c = g['look_cam'](name, loc, (0, -0.08, 0), lens)          # as falcon_beauty.py sets them
        for col in list(c.users_collection): col.objects.unlink(c)
        cams.objects.link(c)
    for a in list(bpy.data.actions): bpy.data.actions.remove(a)
    for name in ('Camera', 'Light'):                               # factory-startup leftovers
        ob = bpy.data.objects.get(name)
        if ob is not None: ob.hide_render = True; ob.hide_viewport = True
    bpy.context.scene.camera = g['CAMS']['top']
    bpy.context.scene.unit_settings.system = 'METRIC'
    # write the scene and what it uses, without the window manager: a normal save records the user's config path there
    ids = set(bpy.data.scenes) | set(bpy.data.objects) | set(bpy.data.collections)
    bpy.data.libraries.write(os.path.abspath(args.blend), ids, path_remap='NONE', fake_user=False, compress=True)
    print('BLEND', args.blend, 'actions:', [a.name for a in bpy.data.actions])
