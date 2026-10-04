# Shaded "final" look: approximate adult peregrine plumage and a dusk light. exec'd after build.
# Dorsal slate blue-grey, darker hand; ventral pale buff with fine dark barring; black hood.
import bpy, math

scene = bpy.context.scene


def node(nt, typ, loc, **inputs):
    n = nt.nodes.new(typ); n.location = loc
    for k, v in inputs.items():
        n.inputs[k].default_value = v
    return n


def plumage(name, hood=False, hand_dark=False):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled'); bsdf.location = (650, 0)
    bsdf.inputs['Roughness'].default_value = .75
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    geo = nt.nodes.new('ShaderNodeNewGeometry'); geo.location = (-900, 200)
    tc = nt.nodes.new('ShaderNodeTexCoord'); tc.location = (-900, -200)
    sep_n = nt.nodes.new('ShaderNodeSeparateXYZ'); sep_n.location = (-700, 200)
    nt.links.new(geo.outputs['Normal'], sep_n.inputs[0])
    # underside factor from the world normal's z
    under = nt.nodes.new('ShaderNodeMapRange'); under.location = (-500, 200)
    under.inputs['From Min'].default_value = .15; under.inputs['From Max'].default_value = -.25
    nt.links.new(sep_n.outputs['Z'], under.inputs['Value'])
    # fine barring along the body axis (object Y), plus a slight wobble
    wave = nt.nodes.new('ShaderNodeTexWave'); wave.location = (-500, -150)
    wave.wave_type = 'BANDS'; wave.bands_direction = 'Y'
    wave.inputs['Scale'].default_value = 75; wave.inputs['Distortion'].default_value = 4   # fine (~8 mm) wavy barring that reads as texture
    wave.inputs['Detail'].default_value = 1.5
    nt.links.new(tc.outputs['Object'], wave.inputs['Vector'])
    bars = nt.nodes.new('ShaderNodeValToRGB'); bars.location = (-300, -150)
    bars.color_ramp.elements[0].position = .45; bars.color_ramp.elements[0].color = (.78, .72, .62, 1)
    bars.color_ramp.elements[1].position = .62; bars.color_ramp.elements[1].color = (.30, .28, .28, 1)
    nt.links.new(wave.outputs['Fac'], bars.inputs[0])
    top = nt.nodes.new('ShaderNodeRGB'); top.location = (-300, 100)
    top.outputs[0].default_value = (.075, .09, .12, 1)         # slate blue-grey (linear)
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.location = (100, 50)
    nt.links.new(under.outputs['Result'], mix.inputs['Factor'])
    nt.links.new(top.outputs[0], mix.inputs['A'])
    nt.links.new(bars.outputs[0], mix.inputs['B'])
    col = mix.outputs['Result']
    sep_o = nt.nodes.new('ShaderNodeSeparateXYZ'); sep_o.location = (-700, -400)
    nt.links.new(tc.outputs['Object'], sep_o.inputs[0])
    if hood:                                                    # black hood ahead of the shoulders, white throat
        hr = nt.nodes.new('ShaderNodeMapRange'); hr.location = (-300, -400)
        hr.inputs['From Min'].default_value = P['rig']['shoulder'][1] + .035   # noqa: F821
        hr.inputs['From Max'].default_value = P['rig']['shoulder'][1] + .06    # noqa: F821
        nt.links.new(sep_o.outputs['Y'], hr.inputs['Value'])
        throat = nt.nodes.new('ShaderNodeMath'); throat.operation = 'MULTIPLY'; throat.location = (-100, -400)
        nt.links.new(hr.outputs['Result'], throat.inputs[0]); nt.links.new(under.outputs['Result'], throat.inputs[1])
        hood_m = nt.nodes.new('ShaderNodeMix'); hood_m.data_type = 'RGBA'; hood_m.location = (300, 0)
        nt.links.new(hr.outputs['Result'], hood_m.inputs['Factor'])
        nt.links.new(col, hood_m.inputs['A']); hood_m.inputs['B'].default_value = (.04, .04, .05, 1)
        th = nt.nodes.new('ShaderNodeMix'); th.data_type = 'RGBA'; th.location = (480, 0)
        nt.links.new(throat.outputs[0], th.inputs['Factor'])
        nt.links.new(hood_m.outputs['Result'], th.inputs['A']); th.inputs['B'].default_value = (.95, .92, .85, 1)
        col = th.outputs['Result']
    if hand_dark:                                               # primaries darker toward the tip
        hr = nt.nodes.new('ShaderNodeMapRange'); hr.location = (-300, -650)
        nt.links.new(sep_o.outputs['X'], hr.inputs['Value'])
        hr.inputs['From Min'].default_value = P['rig']['wrist'][0] * .9        # noqa: F821
        hr.inputs['From Max'].default_value = P['wing']['half_span']           # noqa: F821
        ab = nt.nodes.new('ShaderNodeMath'); ab.operation = 'ABSOLUTE'; ab.location = (-500, -650)
        nt.links.new(sep_o.outputs['X'], ab.inputs[0]); nt.links.new(ab.outputs[0], hr.inputs['Value'])
        dk = nt.nodes.new('ShaderNodeMix'); dk.data_type = 'RGBA'; dk.location = (480, -250)
        sc = nt.nodes.new('ShaderNodeMath'); sc.operation = 'MULTIPLY'; sc.location = (250, -500)
        sc.inputs[1].default_value = .6
        nt.links.new(hr.outputs['Result'], sc.inputs[0]); nt.links.new(sc.outputs[0], dk.inputs['Factor'])
        nt.links.new(col, dk.inputs['A']); dk.inputs['B'].default_value = (.06, .06, .08, 1)
        col = dk.outputs['Result']
    nt.links.new(col, bsdf.inputs['Base Color'])
    return mat


def apply_look(objs):
    body_m = plumage('FalconBody_mat', hood=True)
    wing_m = plumage('FalconWing_mat', hand_dark=True)
    tail_m = plumage('FalconTail_mat')
    bill_m = bpy.data.materials.get('FalconBill_mat') or bpy.data.materials.new('FalconBill_mat')
    bill_m.use_nodes = True
    b = next(n for n in bill_m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (.35, .38, .45, 1)
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
    sun = bpy.data.objects.get('FalconSun')
    if sun is None:
        sun = bpy.data.objects.new('FalconSun', bpy.data.lights.new('FalconSun', 'SUN'))
        scene.collection.objects.link(sun)
    sun.data.energy = 2.2; sun.data.color = (1, .78, .6); sun.data.angle = math.radians(3)
    sun.rotation_euler = (math.radians(55), math.radians(10), math.radians(150))
    for ob in list(scene.objects):
        if ob.name in ('Light',) and ob.type == 'LIGHT':
            ob.hide_render = True
    return scene.render.engine
