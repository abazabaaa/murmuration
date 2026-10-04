# Species-neutral copy of falcon/blender/falcon_build.py: object names use PREFIX (default 'Bird').
# Parametric bird for Blender (built for the peregrine, reused for the starling): lofted body, cambered wings and a tail fan,
# driven by an armature (shoulder/elbow/wrist per side + tail) with hand-set weights so the
# planform stays exactly what was measured. Units: metres. +Y forward, +X right wing, +Z up.
# Run inside Blender:  exec(open(PATH).read(), {'PARAMS': '/path/params.json'})
import bpy, bmesh, json, math
from mathutils import Matrix, Vector

P = json.load(open(PARAMS))                     # noqa: F821  (injected by the caller)
PREFIX = globals().get('PREFIX', P.get('prefix', 'Bird'))
# feather-bone attachment points: (arm bone, fraction along it)
FEATHER_ATTACH = [('humerus', .4), ('humerus', .9), ('forearm', .25), ('forearm', .6), ('forearm', .92)]


def interp(xs, ys, x):
    if x <= xs[0]: return ys[0]
    for k in range(1, len(xs)):
        if x <= xs[k]:
            t = (x - xs[k - 1]) / (xs[k] - xs[k - 1])
            return ys[k - 1] * (1 - t) + ys[k] * t
    return ys[-1]


def smooth_interp(xs, ys, x):                   # monotone-ish cubic (Catmull-Rom on samples)
    n = len(xs)
    if x <= xs[0]: return ys[0]
    if x >= xs[-1]: return ys[-1]
    k = max(i for i in range(n - 1) if xs[i] <= x)
    t = (x - xs[k]) / (xs[k + 1] - xs[k])
    y0 = ys[max(k - 1, 0)]; y1 = ys[k]; y2 = ys[k + 1]; y3 = ys[min(k + 2, n - 1)]
    return .5 * ((2 * y1) + (-y0 + y2) * t + (2 * y0 - 5 * y1 + 4 * y2 - y3) * t * t + (-y0 + 3 * y1 - 3 * y2 + y3) * t ** 3)


def clear():
    for ob in list(bpy.data.objects):
        if ob.name.startswith(PREFIX) or ob.name in ('Cube',):
            bpy.data.objects.remove(ob, do_unlink=True)
    for me in list(bpy.data.meshes):
        if me.users == 0: bpy.data.meshes.remove(me)
    for a in list(bpy.data.armatures):
        if a.users == 0: bpy.data.armatures.remove(a)


def mesh_object(name, verts, faces, coll):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    for p in me.polygons: p.use_smooth = True
    return ob


# ------------------------------------------------------------------ body
def build_body(coll):
    B = P['body']
    L = B['bill_to_tailbase']                   # m, bill tip (y=y_bill) back to tail base
    yb = B['y_bill']
    ts, ws, hs, zs = B['t'], B['halfwidth'], B['halfheight'], B['zcentre']   # t: 0 bill .. 1 tail base
    nr, nt = 24, 48
    verts, faces = [], []
    ring = []
    for i in range(nt + 1):
        t = (1 - math.cos(math.pi * i / nt)) / 2   # denser at the ends
        y = yb - t * L
        w, h, z = smooth_interp(ts, ws, t), smooth_interp(ts, hs, t), smooth_interp(ts, zs, t)
        idx = []
        for j in range(nr):
            a = 2 * math.pi * j / nr
            # superellipse-ish section: flatter belly, rounder back
            ca, sa = math.cos(a), math.sin(a)
            r_h = h * (1.0 if sa > 0 else B.get('belly_flat', .9))
            idx.append(len(verts)); verts.append((w * ca, y, z + r_h * sa))
        ring.append(idx)
    for i in range(nt):
        for j in range(nr):
            a, b = ring[i][j], ring[i][(j + 1) % nr]
            c, d = ring[i + 1][(j + 1) % nr], ring[i + 1][j]
            faces.append((a, d, c, b))
    # caps
    for k, rng in ((0, ring[0]), (1, ring[-1])):
        c = len(verts); verts.append(tuple(sum(verts[v][q] for v in rng) / nr for q in range(3)))
        for j in range(nr):
            f = (rng[j], rng[(j + 1) % nr], c)
            faces.append(f if k else f[::-1])
    ob = mesh_object(PREFIX + 'Body', verts, faces, coll)
    # hooked bill: a small cone pitched down
    bm = bmesh.new()
    # falcon defaults; bill_dy / bill_dz place the cone centre relative to the bill tip and the head axis
    bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=B['bill_r'], radius2=B.get('bill_r2', 0.0015), depth=B['bill_len'])
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90 + B['bill_droop']), 3, 'X'))
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, yb + B.get('bill_dy', -B['bill_len'] * .25), smooth_interp(ts, zs, .02) + B.get('bill_dz', -.004)))
    me = bpy.data.meshes.new(PREFIX + 'Bill'); bm.to_mesh(me); bm.free()
    bill = bpy.data.objects.new(PREFIX + 'Bill', me); coll.objects.link(bill)
    return ob, bill


# ------------------------------------------------------------------ wing
def wing_planform():
    W = P['wing']
    hs = W['half_span']
    s, le, te = W['s'], W['le'], W['te']      # s: fraction of half-span from the centreline
    return hs, s, le, te


def build_wing(coll, side):
    W = P['wing']
    hs, s, le, te = wing_planform()
    x0 = W['root_x']                            # where the wing surface starts (inside the body)
    nu, nc = 56, 16
    top, bot = [], []
    verts, faces = [], []
    for i in range(nu + 1):
        q = i / nu
        x = x0 + (hs - x0) * (1 - (1 - q) ** 1.5)     # denser toward the tip
        sx = x / hs
        yl = smooth_interp(s, le, sx) * hs
        yt = smooth_interp(s, te, sx) * hs
        if i == nu:
            ym = (yl + yt) / 2; yl = yt = ym
        ch = yl - yt
        tmax = W['thick_root'] * (1 - sx) + W['thick_tip'] * sx       # fraction of chord
        camb = W['camber']
        rt, rb = [], []
        for j in range(nc + 1):
            c = (1 - math.cos(math.pi * j / nc)) / 2                 # 0 LE .. 1 TE
            y = yl - c * ch
            th = ch * tmax * 2.6 * math.sqrt(c) * (1 - c) ** 1.6     # blunt LE, thin TE
            zc = ch * camb * 4 * c * (1 - c)
            dz = W['dihedral'] * (x - x0)
            rt.append(len(verts)); verts.append((side * x, y, zc + th / 2 + dz))
            rb.append(len(verts)); verts.append((side * x, y, zc - th / 2 + dz))
        top.append(rt); bot.append(rb)
    for i in range(nu):
        for j in range(nc):
            f = (top[i][j], top[i][j + 1], top[i + 1][j + 1], top[i + 1][j])
            g = (bot[i][j], bot[i + 1][j], bot[i + 1][j + 1], bot[i][j + 1])
            faces.append(f if side > 0 else f[::-1])
            faces.append(g if side > 0 else g[::-1])
    for j in range(nc):                          # root cap
        f = (top[0][j], bot[0][j], bot[0][j + 1], top[0][j + 1])
        faces.append(f if side > 0 else f[::-1])
    ob = mesh_object(PREFIX + 'Wing.' + ('R' if side > 0 else 'L'), verts, faces, coll)
    return ob


# ------------------------------------------------------------------ tail (shape keys: closed -> fanned)
def build_tail(coll):
    T = P['tail']
    yb, Lt = T['y_base'], T['length']
    nr, na = 10, 14
    def pt(r, a, fan):
        # r: 0 base .. 1 tip; a: -1 .. 1 across.  closed: tapered strap; fanned: circular sector
        half_ang = math.radians(T['fan_half_angle']) * fan
        wb, wt = T['base_halfwidth'], T['tip_halfwidth']
        if fan < 1e-6 or half_ang < 1e-4:
            x = a * (wb + (wt - wb) * r)
            y = yb - r * Lt
            if r == 1: y += T['tip_round'] * Lt * (a * a)            # slightly rounded corners
        else:
            ang = a * half_ang
            x = a * wb * (1 - r) + math.sin(ang) * r * Lt
            y = yb - math.cos(ang) * r * Lt
        return x, y
    verts, faces, idx = [], [], {}
    for k, zoff in ((0, .004), (1, -.004)):
        for i in range(nr + 1):
            for j in range(na + 1):
                r, a = i / nr, -1 + 2 * j / na
                x, y = pt(r, a, 0)
                th = (1 - r) * .5 + .5
                idx[k, i, j] = len(verts); verts.append((x, y, T['z'] + zoff * th))
    for i in range(nr):
        for j in range(na):
            faces.append((idx[0, i, j], idx[0, i, j + 1], idx[0, i + 1, j + 1], idx[0, i + 1, j]))
            faces.append((idx[1, i, j], idx[1, i + 1, j], idx[1, i + 1, j + 1], idx[1, i, j + 1]))
    for j in range(na):                          # tip and base rims
        faces.append((idx[0, nr, j], idx[0, nr, j + 1], idx[1, nr, j + 1], idx[1, nr, j]))
    for i in range(nr):
        faces.append((idx[0, i, 0], idx[0, i + 1, 0], idx[1, i + 1, 0], idx[1, i, 0]))
        faces.append((idx[0, i, na], idx[1, i, na], idx[1, i + 1, na], idx[0, i + 1, na]))
    ob = mesh_object(PREFIX + 'Tail', verts, faces, coll)
    ob.shape_key_add(name='Basis')
    sk = ob.shape_key_add(name='Fanned')
    for (k, i, j), vi in idx.items():
        r, a = i / nr, -1 + 2 * j / na
        x, y = pt(r, a, 1)
        sk.data[vi].co.x, sk.data[vi].co.y = x, y
    sk.value = 0.0                              # new keys can start at full strength
    return ob


# ------------------------------------------------------------------ armature + weights
def build_rig(coll, wings, body, bill, tail):
    R = P['rig']
    arm = bpy.data.armatures.new(PREFIX + 'Rig')
    rig = bpy.data.objects.new(PREFIX + 'Rig', arm)
    coll.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    for ob in bpy.context.selected_objects: ob.select_set(False)
    rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.edit_bones
    root = eb.new('body'); root.head = (0, R['body_tail_y'], 0); root.tail = (0, R['body_head_y'], 0)
    tb = eb.new('tail'); tb.head = (0, P['tail']['y_base'], P['tail']['z']); tb.tail = (0, P['tail']['y_base'] - P['tail']['length'], P['tail']['z']); tb.parent = root
    for side, sfx in ((1, 'R'), (-1, 'L')):
        sh = Vector((side * R['shoulder'][0], R['shoulder'][1], R['shoulder'][2]))
        el = Vector((side * R['elbow'][0], R['elbow'][1], R['elbow'][2]))
        wr = Vector((side * R['wrist'][0], R['wrist'][1], R['wrist'][2]))
        tp = Vector((side * R['tip'][0], R['tip'][1], R['tip'][2]))
        prev = root
        for name, h, t in (('humerus', sh, el), ('forearm', el, wr), ('hand', wr, tp)):
            b = eb.new(f'{name}.{sfx}'); b.head = h; b.tail = t; b.parent = prev
            b.use_connect = prev is not root
            b.align_roll(Vector((0, 0, 1)))    # local Z up, local X ≈ chordwise
            b.inherit_scale = 'NONE'
            prev = b
        # feather bones: tertials on the humerus, secondaries on the forearm.  Each pivots at its
        # own attachment point and points aft, so folding the arm can keep the feathers trailing
        # instead of swinging the whole arm wing round as one plate.
        for k, (pname, f) in enumerate(FEATHER_ATTACH):
            p0, p1 = (sh, el) if pname == 'humerus' else (el, wr)
            h = p0.lerp(p1, f)
            fb = eb.new(f'fthr{k}.{sfx}'); fb.head = h; fb.tail = h + Vector((0, -0.10, 0))
            fb.parent = eb[f'{pname}.{sfx}']; fb.use_connect = False
            fb.align_roll(Vector((0, 0, 1))); fb.inherit_scale = 'NONE'
    bpy.ops.object.mode_set(mode='OBJECT')
    arm.display_type = 'STICK'                  # octahedral bones poke through the thin wing

    def add_mod(ob):
        ob.parent = rig
        m = ob.modifiers.new('Armature', 'ARMATURE'); m.object = rig
        return ob

    for ob in (body, bill):
        add_mod(ob); vg = ob.vertex_groups.new(name='body')
        vg.add(list(range(len(ob.data.vertices))), 1.0, 'REPLACE')
    add_mod(tail); vg = tail.vertex_groups.new(name='tail')
    vg.add(list(range(len(tail.data.vertices))), 1.0, 'REPLACE')

    # wing weights by span position: body | humerus | forearm | hand with soft blends; the aft
    # part of the arm wing (chord fraction c > ~0.2) is handed to the feather bones
    bw = R['blend']
    xe, xw = R['elbow'][0], R['wrist'][0]
    xs = R['shoulder'][0]
    hs, s_, le_, te_ = wing_planform()
    def lerp3(a, b, f): return [a[i] + (b[i] - a[i]) * f for i in range(3)]
    fx = [lerp3(R['shoulder'], R['elbow'], f)[0] if p == 'humerus' else lerp3(R['elbow'], R['wrist'], f)[0]
          for p, f in FEATHER_ATTACH]
    def smooth01(t): t = min(max(t, 0), 1); return t * t * (3 - 2 * t)
    for ob in wings:
        sfx = ob.name[-1]
        names = ['body', f'humerus.{sfx}', f'forearm.{sfx}', f'hand.{sfx}'] + [f'fthr{k}.{sfx}' for k in range(len(fx))]
        g = {n: ob.vertex_groups.new(name=n) for n in names}
        for v in ob.data.vertices:
            x = abs(v.co.x)
            def ramp(x, a, w=bw):               # 0 well inside a, 1 well outside, smoothstep over ±w
                t = min(max((x - a + w) / (2 * w), 0), 1); return t * t * (3 - 2 * t)
            rb = R.get('root_blend', 2 * bw)    # the patagium root stretches over a wider band
            r_s, r_e, r_w = ramp(x, R.get('root_center', xs + rb), rb), ramp(x, xe), ramp(x, xw)
            w_body = 1 - r_s
            w_hum = r_s * (1 - r_e)
            w_fore = r_e * (1 - r_w)
            w_hand = r_w
            # chord fraction in the rest planform
            yl = smooth_interp(s_, le_, x / hs) * hs; yt = smooth_interp(s_, te_, x / hs) * hs
            c = (yl - v.co.y) / max(yl - yt, 1e-4)
            fo, fw = R.get('fan_fade', (.02, .07))                         # falcon-scale metres; scale with the bird
            f = smooth01((c - .15) / .4) * (1 - ramp(x, xw - fo, fw))      # wide hand-off: no square corner where secondaries meet primaries
            arm = (w_hum + w_fore) * f
            w = {'body': w_body, f'humerus.{sfx}': w_hum * (1 - f), f'forearm.{sfx}': w_fore * (1 - f), f'hand.{sfx}': w_hand}
            # spread the feather share over the attachment points with hat functions in x
            if x <= fx[0]: hat = {0: 1.0}
            elif x >= fx[-1]: hat = {len(fx) - 1: 1.0}
            else:
                k = max(i for i in range(len(fx) - 1) if fx[i] <= x); t = (x - fx[k]) / (fx[k + 1] - fx[k])
                hat = {k: 1 - t, k + 1: t}
            for k, h in hat.items(): w[f'fthr{k}.{sfx}'] = arm * h
            for n, wt in w.items():
                if wt > 1e-4: g[n].add([v.index], wt, 'REPLACE')
    for ob in wings: add_mod(ob)
    return rig


# ------------------------------------------------------------------ poses
def set_pose(rig, pose, tail_ob=None):
    """pose: {bone: {sweep, elev, twist (deg, body frame, right-wing convention), scale_x}} ; tail_fan 0..1"""
    for pb in rig.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    # optional per-side overrides: pose['sides'] = {'R': {bone: {...}}, 'L': {...}} merged over pose['bones']
    sides = pose.get('sides', {})
    names = list(pose.get('bones', {})) + [n for sd in sides.values() for n in sd if n not in pose.get('bones', {})]
    for name in dict.fromkeys(names):
        for sfx, side in (('R', 1), ('L', -1)):
            spec = {**pose.get('bones', {}).get(name, {}), **sides.get(sfx, {}).get(name, {})}
            bn = f'{name}.{sfx}' if name not in ('body', 'tail') else name
            if bn not in rig.pose.bones: continue
            pb = rig.pose.bones[bn]
            sw, el, tw = (math.radians(spec.get(k, 0)) for k in ('sweep', 'elev', 'twist'))
            # right wing: sweep back = -Z rot, elevate tip = -Y rot, pitch LE up = +X rot.
            # Applied to the bone in its rest (lateral) direction: twist, then elevate about the
            # body's long axis, then sweep, so a drooped hand stays drooped when swept back.
            Rb = Matrix.Rotation(-side * sw, 4, 'Z') @ Matrix.Rotation(-side * el, 4, 'Y') @ Matrix.Rotation(tw, 4, 'X')
            if name == 'tail':
                Rb = Matrix.Rotation(math.radians(spec.get('pitch', 0)), 4, 'X')
            rest = pb.bone.matrix_local.to_3x3().to_4x4()
            basis = rest.inverted() @ Rb @ rest
            sx = spec.get('scale_x', 1.0)
            basis = basis @ Matrix.Diagonal((sx, 1, spec.get('scale_z', 1.0), 1))
            pb.matrix_basis = basis
            if name in ('body', 'tail'): break
    # feather fans: 'aft' (0..1) cancels that share of the arm's accumulated sweep so the feathers
    # keep trailing as the arm folds; scale_x narrows the fan (feathers sliding over each other)
    fan = pose.get('fan')
    if fan:
        bones = pose.get('bones', {})
        for sfx, side in (('R', 1), ('L', -1)):
            for k, (pname, _) in enumerate(FEATHER_ATTACH):
                pb = rig.pose.bones[f'fthr{k}.{sfx}']
                acc = bones.get('humerus', {}).get('sweep', 0) + (bones.get('forearm', {}).get('sweep', 0) if pname == 'forearm' else 0)
                sw = math.radians(-fan.get('aft', 0) * acc + fan.get('sweep', 0))
                Rb = Matrix.Rotation(-side * sw, 4, 'Z')
                rest = pb.bone.matrix_local.to_3x3().to_4x4()
                pb.matrix_basis = rest.inverted() @ Rb @ rest @ Matrix.Diagonal((fan.get('scale_x', 1.0), fan.get('scale_y', 1.0), 1, 1))
    if tail_ob is not None and tail_ob.data.shape_keys:
        tail_ob.data.shape_keys.key_blocks['Fanned'].value = pose.get('tail_fan', 0)
    bpy.context.view_layer.update()


def build():
    clear()
    coll = bpy.data.collections.get(PREFIX) or bpy.data.collections.new(PREFIX)
    if coll.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(coll)
    body, bill = build_body(coll)
    wings = [build_wing(coll, 1), build_wing(coll, -1)]
    tail = build_tail(coll)
    rig = build_rig(coll, wings, body, bill, tail)
    return dict(rig=rig, body=body, bill=bill, wings=wings, tail=tail)


OBJS = build()
