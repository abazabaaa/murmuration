# Blender side of the sky work: the HDRI as the world, turned to match murmuration-sky.jpg, and the page camera.
# exec'd inside Blender with HDR, REG (registration.json path) in globals. Page axes x right, y up, z away
# become Blender (X, Y, Z) = (x, z, y), as in replay/replay_build.py.
import bpy, json, math

REGD = json.load(open(REG))                    # noqa: F821
CAM_H_M = 1.0                                  # page CAM_H = 2 u of 0.5 m
PITCH = math.atan(480 / (800 / math.tan(math.radians(23))))


def world(strength=1.0, hdr=None):
    """Environment texture turned so that a Blender camera looking along +Y sees what sky/common.reproject gives
    (checked: NCC 1.000 against it at 960x400). common.py's equirect layout is the mirror image of Blender's,
    so registration.json says mirror=True; in Blender the same pose is a plain turn of 270 deg - yaw."""
    sc = bpy.context.scene
    w = bpy.data.worlds.new('SkyWorld'); w.use_nodes = True; sc.world = w
    nt = w.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg = nt.nodes.new('ShaderNodeBackground'); bg.inputs[1].default_value = strength
    env = nt.nodes.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(hdr or HDR)   # noqa: F821
    env.interpolation = 'Linear'
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.vector_type = 'POINT'
    assert REGD['mirror']
    mp.inputs['Rotation'].default_value = (0, 0, math.radians(270 - REGD['yaw']))
    nt.links.new(tc.outputs['Generated'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], env.inputs['Vector'])
    nt.links.new(env.outputs['Color'], bg.inputs['Color']); nt.links.new(bg.outputs[0], out.inputs['Surface'])
    w.cycles_visibility.camera = True
    try:
        w.cycles.sampling_method = 'MANUAL'; w.cycles.sample_map_resolution = 4096
    except Exception as e:
        print('world sampling:', e)
    return w


def page_camera(res=(960, 400)):
    sc = bpy.context.scene
    cam = bpy.data.cameras.new('PageCam'); cam.sensor_fit = 'VERTICAL'; cam.angle_y = math.radians(46); cam.clip_end = 5000
    ob = bpy.data.objects.new('PageCam', cam); sc.collection.objects.link(ob)
    ob.location = (0, 0, CAM_H_M); ob.rotation_euler = (math.pi / 2 + PITCH, 0, 0)
    sc.camera = ob
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    return ob


def cycles(samples=64):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.samples = samples; sc.cycles.use_denoising = False
    try:
        bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'METAL'
        bpy.context.preferences.addons['cycles'].preferences.get_devices()
        for d in bpy.context.preferences.addons['cycles'].preferences.devices: d.use = True
        sc.cycles.device = 'GPU'
    except Exception as e:
        print('GPU:', e)
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.exposure = 0; sc.view_settings.look = 'None'
    sc.render.image_settings.file_format = 'HDR'
    sc.cycles.filter_width = .5
