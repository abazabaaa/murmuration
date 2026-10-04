# Shaded look for the starling: winter (non-breeding) adult plumage, as in autumn/winter murmurations.
# Blackish with a purple-green gloss, the body spangled with pale buff-white spots (denser and larger
# below), wings dark brown-black with scalloped buff feather tips along the trailing edge, tail with buff
# tips, underwing grey-brown, bill dark (winter).
# exec'd after bird_build.py.  beauty_setup() is copied from falcon/blender/falcon_look.py (only the sun is renamed).
import bpy, math

scene = bpy.context.scene


def starling_mat(name, spots=0.0, underwing=False, fringes=False):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); out.location = (1100, 0)
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled'); bsdf.location = (850, 0)
    bsdf.inputs['Roughness'].default_value = .42
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    geo = nt.nodes.new('ShaderNodeNewGeometry'); geo.location = (-1100, 300)
    tc = nt.nodes.new('ShaderNodeTexCoord'); tc.location = (-1100, -200)
    sep_n = nt.nodes.new('ShaderNodeSeparateXYZ'); sep_n.location = (-900, 300)
    nt.links.new(geo.outputs['Normal'], sep_n.inputs[0])
    under = nt.nodes.new('ShaderNodeMapRange'); under.location = (-700, 300)            # 0 above .. 1 below
    under.inputs['From Min'].default_value = .15; under.inputs['From Max'].default_value = -.25
    nt.links.new(sep_n.outputs['Z'], under.inputs['Value'])
    # gloss: purple at facing angles, green toward grazing (layer weight), over near-black
    lw = nt.nodes.new('ShaderNodeLayerWeight'); lw.location = (-700, 50); lw.inputs['Blend'].default_value = .45
    gl = nt.nodes.new('ShaderNodeMix'); gl.data_type = 'RGBA'; gl.location = (-450, 50)
    nt.links.new(lw.outputs['Facing'], gl.inputs['Factor'])
    gl.inputs['A'].default_value = (.035, .02, .045, 1); gl.inputs['B'].default_value = (.015, .04, .03, 1)
    col = gl.outputs['Result']
    if underwing:                                     # underwing grey-brown
        uw = nt.nodes.new('ShaderNodeMix'); uw.data_type = 'RGBA'; uw.location = (-200, 150)
        nt.links.new(under.outputs['Result'], uw.inputs['Factor'])
        nt.links.new(col, uw.inputs['A']); uw.inputs['B'].default_value = (.16, .135, .115, 1)
        col = uw.outputs['Result']
    if fringes:                                       # buff feather tips: a scalloped pale band at the trailing edge
        # 'chord' (0 leading edge .. 1 trailing edge; tail: 0 base .. 1 tip) is written per vertex by
        # chord_attr(); the scallop period is one feather width (~1.4 cm, Feather Atlas primaries/rectrices)
        at = nt.nodes.new('ShaderNodeAttribute'); at.location = (-700, -300); at.attribute_name = 'chord'
        wv = nt.nodes.new('ShaderNodeTexWave'); wv.location = (-700, -500)
        wv.wave_type = 'BANDS'; wv.bands_direction = 'X'
        wv.inputs['Scale'].default_value = 0.314 / 0.014; wv.inputs['Distortion'].default_value = 0.0
        nt.links.new(tc.outputs['Object'], wv.inputs['Vector'])
        thr = nt.nodes.new('ShaderNodeMath'); thr.operation = 'MULTIPLY_ADD'; thr.location = (-500, -500)
        nt.links.new(wv.outputs['Fac'], thr.inputs[0]); thr.inputs[1].default_value = -.03; thr.inputs[2].default_value = .955
        d = nt.nodes.new('ShaderNodeMath'); d.operation = 'SUBTRACT'; d.location = (-350, -350)
        nt.links.new(at.outputs['Fac'], d.inputs[0]); nt.links.new(thr.outputs[0], d.inputs[1])
        fr = nt.nodes.new('ShaderNodeMapRange'); fr.location = (-200, -350)
        fr.inputs['From Min'].default_value = 0.0; fr.inputs['From Max'].default_value = .02
        nt.links.new(d.outputs[0], fr.inputs['Value'])
        wk = nt.nodes.new('ShaderNodeMapRange'); wk.location = (-200, -550)            # weaker on the underside
        nt.links.new(under.outputs['Result'], wk.inputs['Value'])
        wk.inputs['To Min'].default_value = .42; wk.inputs['To Max'].default_value = .2
        sc = nt.nodes.new('ShaderNodeMath'); sc.operation = 'MULTIPLY'; sc.location = (-50, -400)
        nt.links.new(fr.outputs['Result'], sc.inputs[0]); nt.links.new(wk.outputs['Result'], sc.inputs[1])
        fm = nt.nodes.new('ShaderNodeMix'); fm.data_type = 'RGBA'; fm.location = (100, -150)
        nt.links.new(sc.outputs[0], fm.inputs['Factor'])
        nt.links.new(col, fm.inputs['A']); fm.inputs['B'].default_value = (.36, .27, .17, 1)
        col = fm.outputs['Result']
    if spots > 0:                                     # spangles: Voronoi cells -> small pale dots
        vo = nt.nodes.new('ShaderNodeTexVoronoi'); vo.location = (-450, -600)
        vo.inputs['Scale'].default_value = spots; vo.inputs['Randomness'].default_value = .9
        nt.links.new(tc.outputs['Object'], vo.inputs['Vector'])
        sz = nt.nodes.new('ShaderNodeMapRange'); sz.location = (-250, -600)            # dot radius grows below
        nt.links.new(under.outputs['Result'], sz.inputs['Value'])
        sz.inputs['To Min'].default_value = .16; sz.inputs['To Max'].default_value = .30
        lt = nt.nodes.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'; lt.location = (-50, -600)
        nt.links.new(vo.outputs['Distance'], lt.inputs[0]); nt.links.new(sz.outputs['Result'], lt.inputs[1])
        sp = nt.nodes.new('ShaderNodeMix'); sp.data_type = 'RGBA'; sp.location = (250, -300)
        nt.links.new(lt.outputs[0], sp.inputs['Factor'])
        nt.links.new(col, sp.inputs['A']); sp.inputs['B'].default_value = (.80, .74, .62, 1)
        col = sp.outputs['Result']
    nt.links.new(col, bsdf.inputs['Base Color'])
    return mat


def chord_attr(ob, kind):
    """Per-vertex 'chord' on the rest mesh: wing 0 at the leading edge .. 1 at the trailing edge;
    tail 0 at its base .. 1 at its tip.  The armature and the fan shape key carry it along."""
    me = ob.data
    at = me.attributes.get('chord') or me.attributes.new('chord', 'FLOAT', 'POINT')
    if kind == 'wing':
        hs, s_, le_, te_ = wing_planform()                                         # noqa: F821
        for v in me.vertices:
            x = abs(v.co.x); yl = smooth_interp(s_, le_, x / hs) * hs; yt = smooth_interp(s_, te_, x / hs) * hs   # noqa: F821
            at.data[v.index].value = max(0.0, min(1.0, (yl - v.co.y) / max(yl - yt, 1e-4)))
    else:
        T = P['tail']                                                              # noqa: F821
        for v in me.vertices:
            at.data[v.index].value = max(0.0, min(1.0, (T['y_base'] - v.co.y) / T['length']))


def apply_look(objs):
    pre = PREFIX                                                                    # noqa: F821
    for w in objs['wings']: chord_attr(w, 'wing')
    chord_attr(objs['tail'], 'tail')
    body_m = starling_mat(pre + 'Body_mat', spots=180)
    wing_m = starling_mat(pre + 'Wing_mat', underwing=True, fringes=True)
    tail_m = starling_mat(pre + 'Tail_mat', fringes=True)
    bill_m = bpy.data.materials.get(pre + 'Bill_mat') or bpy.data.materials.new(pre + 'Bill_mat')
    bill_m.use_nodes = True
    b = next(n for n in bill_m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (.05, .045, .045, 1)                     # winter bill: dark
    for ob, m in ((objs['body'], body_m), (objs['tail'], tail_m), (objs['bill'], bill_m), *((w, wing_m) for w in objs['wings'])):
        ob.data.materials.clear(); ob.data.materials.append(m)
        if not any(md.type == 'SUBSURF' for md in ob.modifiers):
            sd = ob.modifiers.new('Subsurf', 'SUBSURF'); sd.levels = 1; sd.render_levels = 2


def beauty_setup():
    eng = scene.render.engine
    for cand in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE', 'CYCLES'):
        try:
            scene.render.engine = cand; break
        except TypeError:
            continue
    scene.view_settings.view_transform = 'AgX' if 'AgX' in [i.identifier for i in scene.view_settings.bl_rna.properties['view_transform'].enum_items] else 'Filmic'
    scene.render.film_transparent = False
    w = scene.world or bpy.data.worlds.new('World'); scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = next(n for n in nt.nodes if n.type == 'BACKGROUND')
    sky = nt.nodes.get('DuskGrad') or nt.nodes.new('ShaderNodeTexGradient'); sky.name = 'DuskGrad'
    ramp = nt.nodes.get('DuskRamp') or nt.nodes.new('ShaderNodeValToRGB'); ramp.name = 'DuskRamp'
    tc = nt.nodes.get('DuskTC') or nt.nodes.new('ShaderNodeTexCoord'); tc.name = 'DuskTC'
    mp = nt.nodes.get('DuskMap') or nt.nodes.new('ShaderNodeMapping'); mp.name = 'DuskMap'
    mp.inputs['Rotation'].default_value = (0, math.radians(-90), 0)      # gradient along world Z
    nt.links.new(tc.outputs['Generated'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], sky.inputs['Vector'])
    nt.links.new(sky.outputs['Fac'], ramp.inputs['Fac'])
    ramp.color_ramp.elements[0].color = (.95, .55, .32, 1)
    ramp.color_ramp.elements[1].color = (.18, .14, .35, 1)
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = .55
    sn = PREFIX + 'Sun'                                                            # noqa: F821
    sun = bpy.data.objects.get(sn)
    if sun is None:
        sun = bpy.data.objects.new(sn, bpy.data.lights.new(sn, 'SUN'))
        scene.collection.objects.link(sun)
    sun.data.energy = 2.2; sun.data.color = (1, .78, .6); sun.data.angle = math.radians(3)
    sun.rotation_euler = (math.radians(55), math.radians(10), math.radians(150))
    for ob in list(scene.objects):
        if ob.name in ('Light',) and ob.type == 'LIGHT':
            ob.hide_render = True
    return scene.render.engine
