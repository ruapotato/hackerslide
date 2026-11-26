"""Blender scene of the whole device for stills and clips: enclosure, boards with their parts, module, pack, keys.

  blender -b --factory-startup -P scene.py -- SHOT OUT_DIR [--frames A B] [--size W H] [--samples N] [--engine cycles|eevee]

Needs ASSETS (default /var/tmp/hackerslide-agent/render/assets, or $HS_ASSETS) filled by assets.sh: board GLBs and
textures, the enclosure STLs and the screen picture.  Units are millimetres; the frame is the enclosure model's
(X width, Y up the device with the top edge at BODY_H, Z thickness, screen up).

Every shot is a function of time: it returns the slider position, how far the parts are pulled apart and where the
camera is, so a still is just one frame of a clip.  What is drawn schematically, not from CAD: the compute module
(a board with blocks where LuckFox's has parts), the battery pack and its leads, and the screen contents.
"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '../src'))
sys.path.insert(0, os.path.join(HERE, '../../hardware/scripts'))
import config as C          # noqa: E402
import kbd_layout as KL     # noqa: E402

ASSETS = os.environ.get('HS_ASSETS', '/var/tmp/hackerslide-agent/render/assets')
BH = C.BODY_H


# ----------------------------------------------------------------------------------------------- materials
def mat(name, rgb, rough=0.5, metal=0.0, emit=None, coat=0.0, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*rgb, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Alpha'].default_value = alpha
    if emit:
        b.inputs['Emission Color'].default_value = (*emit[0], 1)
        b.inputs['Emission Strength'].default_value = emit[1]
    return m


def image_mat(name, path, emit=0.0, rough=0.2):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.image = bpy.data.images.load(path)
    nt.links.new(tex.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough
    if emit:
        nt.links.new(tex.outputs['Color'], b.inputs['Emission Color'])
        b.inputs['Emission Strength'].default_value = emit
    return m


def board_mat(name, prefix, edge=(0.30, 0.27, 0.12), metres=True):
    """Top and bottom pictures mapped by the board's own x/y; faces looking sideways get the edge colour."""
    box = json.load(open(prefix + '.json'))
    w, h = box['x1'] - box['x0'], box['y1'] - box['y0']
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Location'].default_value = (-box['x0'] / w, box['y1'] / h, 0)     # object x = board x, object y = -board y
    k = 1.0 if metres is False else 1000.0                # KiCad's GLB meshes are in metres under a scaled parent
    mp.inputs['Scale'].default_value = (k / w, k / h, 1)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    tex = {}
    for side in ('top', 'bottom'):
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = bpy.data.images.load(f'{prefix}-{side}.png')
        t.extension = 'EXTEND'
        nt.links.new(mp.outputs['Vector'], t.inputs['Vector'])
        tex[side] = t
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Normal'], sep.inputs['Vector'])
    up = nt.nodes.new('ShaderNodeMath'); up.operation = 'GREATER_THAN'; up.inputs[1].default_value = 0.0
    nt.links.new(sep.outputs['Z'], up.inputs[0])
    face = nt.nodes.new('ShaderNodeMix'); face.data_type = 'RGBA'
    nt.links.new(up.outputs[0], face.inputs['Factor'])
    nt.links.new(tex['bottom'].outputs['Color'], face.inputs['A'])
    nt.links.new(tex['top'].outputs['Color'], face.inputs['B'])
    ab = nt.nodes.new('ShaderNodeMath'); ab.operation = 'ABSOLUTE'
    nt.links.new(sep.outputs['Z'], ab.inputs[0])
    flat = nt.nodes.new('ShaderNodeMath'); flat.operation = 'GREATER_THAN'; flat.inputs[1].default_value = 0.5
    nt.links.new(ab.outputs[0], flat.inputs[0])
    col = nt.nodes.new('ShaderNodeMix'); col.data_type = 'RGBA'
    col.inputs['A'].default_value = (*edge, 1)
    nt.links.new(flat.outputs[0], col.inputs['Factor'])
    nt.links.new(face.outputs['Result'], col.inputs['B'])
    nt.links.new(col.outputs['Result'], b.inputs['Base Color'])
    # gold where the picture is gold: red well above blue
    rgb = nt.nodes.new('ShaderNodeSeparateColor')
    nt.links.new(col.outputs['Result'], rgb.inputs['Color'])
    d = nt.nodes.new('ShaderNodeMath'); d.operation = 'SUBTRACT'
    nt.links.new(rgb.outputs['Red'], d.inputs[0]); nt.links.new(rgb.outputs['Blue'], d.inputs[1])
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value = 0.35; mr.inputs['From Max'].default_value = 0.5
    nt.links.new(d.outputs[0], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], b.inputs['Metallic'])
    ro = nt.nodes.new('ShaderNodeMapRange')
    ro.inputs['To Min'].default_value = 0.5; ro.inputs['To Max'].default_value = 0.28
    nt.links.new(mr.outputs['Result'], ro.inputs['Value'])
    nt.links.new(ro.outputs['Result'], b.inputs['Roughness'])
    b.inputs['Coat Weight'].default_value = 0.06
    return m


def fix_part_material(m):
    """KiCad's GLB export marks everything metallic and rough; sort the materials into metal, gold and plastic."""
    b = m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
    if not b:
        return
    r, g, bl, _ = b.inputs['Base Color'].default_value
    hi, lo = max(r, g, bl), min(r, g, bl)
    if r - bl > 0.25 and r > 0.5:                      # gold contacts
        b.inputs['Metallic'].default_value, b.inputs['Roughness'].default_value = 1.0, 0.3
    elif hi - lo < 0.08 and 0.4 < hi < 0.9:            # tin, steel shells
        b.inputs['Metallic'].default_value, b.inputs['Roughness'].default_value = 1.0, 0.32
    elif hi < 0.15:                                    # black plastic, IC bodies
        b.inputs['Metallic'].default_value, b.inputs['Roughness'].default_value = 0.0, 0.45
        b.inputs['Base Color'].default_value = (max(r, 0.02), max(g, 0.02), max(bl, 0.022), 1)
    else:                                              # ceramic, cream housings
        b.inputs['Metallic'].default_value, b.inputs['Roughness'].default_value = 0.0, 0.55


# ----------------------------------------------------------------------------------------------- geometry helpers
def link(o, parent=None):
    if o.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(o)
    if parent:
        o.parent = parent
    return o


def empty(name, parent=None):
    return link(bpy.data.objects.new(name, None), parent)


def cube(name, x0, y0, z0, x1, y1, z1, material, parent=None, bevel=0.0, rot=0.0):
    """Box given in world coordinates (y is world y here)."""
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object
    o.name = name
    o.scale = (x1 - x0, y1 - y0, z1 - z0)
    o.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    o.rotation_euler = (0, 0, rot)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        bv = o.modifiers.new('bevel', 'BEVEL')
        bv.width, bv.segments, bv.limit_method = bevel, 3, 'ANGLE'
        for p in o.data.polygons:
            p.use_smooth = True
    o.data.materials.append(material)
    if parent:
        o.parent = parent
    return o


def dbox(name, x0, y0, z0, x1, y1, z1, material, parent=None, bevel=0.0):
    """Box in device-plan coordinates (y down from the top edge), like the CadQuery model's box()."""
    return cube(name, x0, BH - y1, z0, x1, BH - y0, z1, material, parent, bevel)


def cylinder(name, x, y, z0, z1, d, material, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=d / 2, depth=z1 - z0, location=(x, BH - y, (z0 + z1) / 2))
    o = bpy.context.active_object
    o.name = name
    for p in o.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    o.data.materials.append(material)
    if parent:
        o.parent = parent
    return o


def smooth(o, angle=35):
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    op = getattr(bpy.ops.object, 'shade_auto_smooth', None) or bpy.ops.object.shade_smooth_by_angle
    try:
        op(angle=math.radians(angle))
    except AttributeError:
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle))


def stl(name, material, parent=None):
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=os.path.join(ASSETS, 'scene', f'closed_{name}.stl'))
    o = (set(bpy.data.objects) - before).pop()
    o.name = name
    o.data.materials.append(material)
    smooth(o)
    if parent:
        o.parent = parent
    return o


def glb(name, parent, body_material):
    """A board from KiCad (metres, x = board x, y = -board y, z = 0 at the bottom face), scaled to mm under `parent`."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(ASSETS, name + '.glb'))
    new = list(set(bpy.data.objects) - before)
    root = empty(name + '_root', parent)
    root.scale = (1000, 1000, 1000)
    meshes = [o for o in new if o.type == 'MESH']
    body = max(meshes, key=lambda o: o.dimensions.x * o.dimensions.y)
    for o in new:
        if o.parent is None:
            o.parent = root
    for o in meshes:
        if o is body:
            o.data.materials.clear()
            o.data.materials.append(body_material)
        else:
            for s in o.material_slots:
                if s.material and not s.material.get('fixed'):
                    fix_part_material(s.material)
                    s.material['fixed'] = True
    return root


def text(name, body, x, y, z, size, material, parent=None, align='CENTER'):
    cu = bpy.data.curves.new(name, 'FONT')
    cu.body = body
    cu.size = size
    cu.align_x, cu.align_y = align, 'CENTER'
    for f in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',):
        if os.path.exists(f):
            cu.font = bpy.data.fonts.load(f, check_existing=True)
    o = link(bpy.data.objects.new(name, cu), parent)
    o.location = (x, y, z)
    o.data.materials.append(material)
    return o


def tube(name, pts, radius, material, parent=None):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    cu.bevel_depth = radius
    cu.bevel_resolution = 4
    o = link(bpy.data.objects.new(name, cu), parent)
    o.data.materials.append(material)
    return o


# ----------------------------------------------------------------------------------------------- the device
class Device:
    def __init__(self, parts='all'):
        M = self.M = {
            'shell': mat('shell', (0.035, 0.038, 0.045), 0.42, coat=0.2),
            'tray': mat('tray', (0.06, 0.064, 0.072), 0.45, coat=0.1),
            'cap': mat('cap', (0.62, 0.63, 0.65), 0.38),
            'legend': mat('legend', (0.03, 0.03, 0.035), 0.6),
            'glass': mat('glass', (0.008, 0.008, 0.01), 0.22, coat=0.25),
            'foil': mat('foil', (0.72, 0.73, 0.75), 0.38, metal=1.0),
            'kapton': mat('kapton', (0.75, 0.45, 0.05), 0.35),
            'label': mat('label', (0.08, 0.09, 0.11), 0.5),
            'white': mat('white', (0.85, 0.85, 0.82), 0.5),
            'magnet': mat('magnet', (0.75, 0.75, 0.78), 0.2, metal=1.0),
            'steel': mat('steel', (0.6, 0.6, 0.62), 0.3, metal=1.0),
            'pad': mat('pad', (0.75, 0.42, 0.55), 0.8),
            'modpcb': mat('modpcb', (0.02, 0.05, 0.16), 0.4, coat=0.2),
            'chip': mat('chip', (0.03, 0.03, 0.035), 0.4),
            'lid': mat('lid', (0.7, 0.7, 0.72), 0.25, metal=1.0),
            'red': mat('red', (0.6, 0.03, 0.03), 0.5), 'yellow': mat('yellow', (0.75, 0.6, 0.05), 0.5),
            'blackwire': mat('blackwire', (0.02, 0.02, 0.02), 0.5),
            'flex': board_mat('flexmat', os.path.join(ASSETS, 'flex'), edge=(0.5, 0.3, 0.05)),
            'ghost': mat('ghost', (0.8, 0.45, 0.15), 0.5),
        }
        g = self.g = {n: empty('g_' + n) for n in ('front', 'panel', 'carrier', 'module', 'battery', 'pad', 'back', 'tray',
                                                   'kbd', 'caps', 'plate', 'flex', 'n810')}
        self.root = empty('device')
        for e in g.values():
            e.parent = self.root
        # printed parts
        stl('front_shell', M['shell'], g['front'])
        stl('button_caps', M['cap'], g['front'])
        stl('back_shell', M['shell'], g['back'])
        stl('tray', M['tray'], g['tray'])
        stl('thermal_pad', M['pad'], g['pad'])
        self.panel()
        self.boards()
        self.module()
        self.battery()
        self.keys()
        self.small_parts()
        self.n810()
        self.flex_obj = None
        self.set(0.0, 0.0)

    def panel(self):
        px, py = C.PANEL_XY
        P = C.PANEL
        dbox('panel_body', px, py, C.Z_PANEL_BOTTOM, px + P['w'], py + P['h'], C.Z_PANEL_TOP, self.M['glass'], self.g['panel'], bevel=0.15)
        ax, ay = px + (P['w'] - P['aa_w']) / 2 - 1.5, py + (P['h'] - P['aa_h']) / 2      # active area sits toward the left
        scr = image_mat('screen', os.path.join(ASSETS, 'screen.png'), emit=1.8, rough=0.45)
        scr.node_tree.nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value = 0.12     # anti-glare panel
        bpy.ops.mesh.primitive_plane_add(size=1)
        o = bpy.context.active_object
        o.name = 'screen'
        o.scale = (P['aa_w'], P['aa_h'], 1)
        o.location = (ax + P['aa_w'] / 2, BH - (ay + P['aa_h'] / 2), C.Z_PANEL_TOP + 0.02)
        o.data.materials.append(scr)
        o.parent = self.g['panel']
        tail = C.PANEL['tail_bulge']
        dbox('panel_tail', px + P['w'] - 14, py + 8, C.Z_PANEL_BOTTOM - 0.25, px + P['w'] + 0.6, py + P['h'] - 8, C.Z_PANEL_BOTTOM,
             self.M['kapton'], self.g['panel'])

    def boards(self):
        A = ASSETS
        cx, cy = C.CARRIER_XY
        e = empty('carrier_at', self.g['carrier'])              # the carrier is mounted component side down
        e.location = (cx + C.CARRIER['w'], BH - cy, C.Z_CARRIER_F + C.CARRIER['t'])
        e.rotation_euler = (0, math.pi, 0)
        glb('carrier', e, board_mat('carrier_m', os.path.join(A, 'carrier')))
        kx, ky = C.KBD_XY
        e = empty('kbd_at', self.g['kbd'])
        e.location = (kx, BH - ky, C.TRAY_FLOOR)
        glb('keyboard', e, board_mat('keyboard_m', os.path.join(A, 'keyboard')))
        e = empty('plate_at', self.g['plate'])
        e.location = (kx, BH - ky, C.TRAY_FLOOR + C.KBD_PCB['t'] + C.PLATE_STANDOFF)
        glb('topplate', e, board_mat('plate_m', os.path.join(A, 'topplate'), edge=(0.05, 0.05, 0.05)))

    def module(self):
        M, g = self.M, self.g['module']
        x0, y0 = C.MODULE_XY
        zt = C.Z_CARRIER_F - C.MODULE['stack']                 # face toward the carrier
        zb = zt - 1.2
        dbox('mod_pcb', x0, y0, zb, x0 + 55, y0 + 40, zt, M['modpcb'], g, bevel=0.1)
        sx, sy = x0 + C.SOC_XY[0], y0 + C.SOC_XY[1]
        cube('soc', sx - 7.5, BH - sy - 7.5, zb - 0.9, sx + 7.5, BH - sy + 7.5, zb, M['chip'], g, bevel=0.1, rot=math.pi / 4)
        cube('soc_lid', sx - 5, BH - sy - 5, zb - 0.92, sx + 5, BH - sy + 5, zb - 0.85, M['lid'], g, rot=math.pi / 4)
        for (n, ax, ay, w, h, t, m) in (('ram', 6, 6, 12, 10, 0.9, 'chip'), ('emmc', 6, 22, 11.5, 13, 0.9, 'chip'),
                                        ('wifi', 40, 4, 12, 12, 1.7, 'lid'), ('pmic', 42, 24, 5, 5, 0.85, 'chip'),
                                        ('l1', 34, 31, 4, 4, 1.8, 'chip'), ('l2', 40, 31, 4, 4, 1.8, 'chip'),
                                        ('l3', 46, 31, 4, 4, 1.8, 'chip')):
            dbox('mod_' + n, x0 + ax, y0 + ay, zb - t, x0 + ax + w, y0 + ay + h, zb, M[m], g, bevel=0.12)
        for ky in (C.MODULE_KICAD[1] + 8.0, C.MODULE_KICAD[1] + 32.0):     # the two plugs that mate with J1A/J1B
            px, py = C.carrier_to_device(C.MODULE_KICAD[0] + 27.5, ky)
            dbox('mod_plug', px - 11.3, py - 1.4, zt, px + 11.3, py + 1.4, zt + 1.0, M['white'], g)

    def battery(self):
        M, g = self.M, self.g['battery']
        bx, by = C.BATT_XY
        B = C.BATTERY
        z0 = C.Z_BACK_IN
        dbox('cell', bx, by + 4, z0, bx + B['w'], by + B['h'], z0 + B['t'], M['foil'], g, bevel=1.2)
        dbox('cell_pcm', bx + 1, by, z0 + 1.5, bx + B['w'] - 1, by + 4.5, z0 + B['t'] - 1.5, M['kapton'], g, bevel=0.5)
        dbox('cell_label', bx + 6, by + 16, z0 + B['t'] - 0.02, bx + B['w'] - 6, by + 52, z0 + B['t'] + 0.03, M['label'], g)
        t = text('cell_text', 'Li-ion 3.7 V\n2800 mAh 1S2P', bx + B['w'] / 2, BH - (by + 34), z0 + B['t'] + 0.05, 3.2, M['white'], g)
        t.rotation_euler = (0, 0, math.pi / 2)
        (xa, ya), (xb, yb) = C.carrier_to_device(*C.BATT_PLUG_KICAD[:2]), C.carrier_to_device(*C.BATT_PLUG_KICAD[2:])
        px0, px1, py0, py1 = min(xa, xb), max(xa, xb), min(ya, yb), max(ya, yb)
        zc = C.Z_CARRIER_F
        dbox('plug', px1 - 5.0, py0 + 0.3, zc - 4.6, px1, py1 - 0.3, zc - 0.6, M['white'], g, bevel=0.2)
        for k, m in enumerate(('red', 'yellow', 'blackwire')):
            yw = py0 + 1.5 + 2.5 * k
            tube('lead_' + m, [(bx + B['w'] - 6 - 3 * k, BH - (by + 1.0), z0 + 5), (bx + B['w'] + 1, BH - (by - 0.6 + 0.4 * k), z0 + 4.5),
                               (px1 - 8, BH - (yw - 0.5), zc - 2.8), (px1 - 5.0, BH - yw, zc - 2.6)], 0.42, M[m], g)

    def keys(self):
        M, g = self.M, self.g['caps']
        kx, ky = C.KBD_XY
        c = KL.CAP
        z = C.TRAY_FLOOR + C.KBD_PCB['t'] + C.SWITCH_H + C.KEYCAP['nub_h']
        zt = z + c['flange_t'] + c['top_t']
        nice = {'Bksp': '⌫', 'Enter': '⏎', 'Shift': '⇧', 'Up': '▲', 'Down': '▼', 'Left': '◀', 'Right': '▶', 'Space': '', 'OK': '●',
                'Tab': '⇥'}
        for (name, r, col, x, y) in KL.keys('alps'):
            if name == 'Space' and col == 7:
                continue
            fw, fh, tw, th = c['flange_w'], c['flange_h'], c['top_w'], c['top_h']
            if name == 'Space':
                x += KL.PITCH_X / 2; fw += KL.PITCH_X; tw += KL.PITCH_X
            if r == 4:
                fw = fh = 5.6; tw = th = 4.6
            X, Y = kx + x, ky + y
            dbox('flange', X - fw / 2, Y - fh / 2, z, X + fw / 2, Y + fh / 2, z + c['flange_t'], M['cap'], g)
            dbox('captop', X - tw / 2, Y - th / 2, z + c['flange_t'] - 0.05, X + tw / 2, Y + th / 2, zt, M['cap'], g, bevel=0.35)
            lab = nice.get(name, name)
            if lab:
                text('leg', lab, X, BH - Y, zt + 0.01, 2.6 if len(lab) == 1 else 1.7, M['legend'], g)

    def small_parts(self):
        M = self.M
        mb, mt, mh = C.MAGNET_BODY, C.MAGNET_TRAY, C.MAGNET_HALL
        for x in C.MAGNET_X:
            for y in (C.MAGNET_Y_CLOSED, C.MAGNET_Y_OPEN):
                cylinder('mag_body', x, y, C.Z_BODY_BOTTOM, C.Z_BODY_BOTTOM + mb['t'], mb['d'], M['magnet'], self.g['back'])
            cylinder('mag_tray', x, C.MAGNET_Y_CLOSED, C.Z_TRAY_TOP - 0.1 - mt['t'], C.Z_TRAY_TOP - 0.1, mt['d'], M['magnet'], self.g['tray'])
        hx, hy = C.HALL_XY
        cylinder('mag_hall', hx, hy, C.Z_TRAY_TOP - 0.1 - mh['t'], C.Z_TRAY_TOP - 0.1, mh['d'], M['magnet'], self.g['tray'])
        for (x, y) in C.SCREW_XY:
            cylinder('screw_head', x, y, C.Z_BODY_BOTTOM - 0.01, C.Z_BODY_BOTTOM + 0.5, 3.6, M['steel'], self.g['back'])
            cylinder('screw', x, y, C.Z_BODY_BOTTOM, C.Z_CARRIER_B + 3.0, 2.0, M['steel'], self.g['back'])

    def flex(self, slide, lift_c, lift_k):
        """The keyboard cable as a ribbon: from carrier J9 down through the floor slot, back under the body, round the
        rolling loop and forward into keyboard J1.  lift_* are the z offsets of the carrier and the keyboard."""
        if self.flex_obj:
            bpy.data.objects.remove(self.flex_obj, do_unlink=True)
        x = C.KBD_FPC_X
        dy = C.TRAVEL * slide
        yj9 = C.CARRIER_XY[1] + C.KBD_FPC_KICAD[1] + 0.5
        ys = C.FPC_SLOT['y']
        zc = C.Z_CARRIER_F - 0.5 + lift_c
        zch = C.Z_BODY_BOTTOM + C.FPC['channel'] - 0.1
        zk = C.TRAY_FLOOR + C.KBD_PCB['t'] + 0.15 + lift_k
        ya = C.FPC_LOOP_Y_CLOSED + dy / 2
        yj1 = C.J1_TRAY_Y + dy + 2.0
        R = (zch - (zk - lift_k)) / 2
        pts = [(yj9, zc), (ys - 1.0, zc), (ys, zc - 1.0), (ys, zch + 1.0), (ys - 1.0, zch)]
        pts += [(ya, zch)]
        for k in range(1, 12):
            a = math.pi * k / 12
            pts.append((ya - R * math.sin(a), zch - R + R * math.cos(a) + (lift_k if k > 6 else 0) * 1.0))
        pts += [(ya, zk), (yj1, zk)]
        verts, faces = [], []
        w = C.FPC['w'] / 2
        for (y, z) in pts:
            verts += [(x - w, BH - y, z), (x + w, BH - y, z)]
        for i in range(len(pts) - 1):
            faces.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
        me = bpy.data.meshes.new('flex')
        me.from_pydata(verts, [], faces)
        o = link(bpy.data.objects.new('flex', me), self.g['flex'])
        o.data.materials.append(mat('flexflat', (0.75, 0.42, 0.06), 0.35) if 'flexflat' not in bpy.data.materials
                                else bpy.data.materials['flexflat'])
        sd = o.modifiers.new('solid', 'SOLIDIFY'); sd.thickness = 0.12
        for p in o.data.polygons:
            p.use_smooth = True
        self.flex_obj = o

    # explode offsets in z at explode = 1
    LIFT = {'front': 62, 'panel': 38, 'carrier': 21, 'module': 10, 'battery': 6, 'pad': 3, 'back': 0, 'flex': 0,
            'plate': -9, 'caps': -15, 'kbd': -23, 'tray': -31, 'n810': 0}

    def set(self, slide, explode, hide=(), only=None, flip=False, module_lift=0.0):
        """slide 0..1, explode 0..1; hide / only name groups; flip turns the device over (component side of the
        carrier up); module_lift pulls the module off its sockets by that many mm."""
        dy = -C.TRAVEL * slide
        hide = set(hide) | ({'n810'} if not only or 'n810' not in only else set())
        if explode > 0.03:
            hide.add('flex')               # the cable is not drawn stretching between parts that are pulled apart
        for n, e in self.g.items():
            moving = n in ('tray', 'kbd', 'caps', 'plate')
            e.location = (0, dy if moving else 0, self.LIFT[n] * explode - (module_lift if n == 'module' else 0))
            off = n in hide or (only is not None and n not in only)
            for o in e.children_recursive:
                o.hide_render = off
        self.flex(slide, self.LIFT['carrier'] * explode, self.LIFT['kbd'] * explode)
        self.flex_obj.hide_render = 'flex' in hide or (only is not None and 'flex' not in only)
        self.root.rotation_euler = (math.pi, 0, 0) if flip else (0, 0, 0)
        self.root.location = (0, BH, C.Z_CARRIER_F + 1.0) if flip else (0, 0, 0)

    def n810(self):
        """A plain block the size of a Nokia N810 (128 x 72 x 14 mm), for scale, beside the device."""
        g = self.g['n810']
        o = cube('n810_block', 140, 1, 0, 268, 73, 14, self.M['ghost'], g, bevel=3.0)
        t = text('n810_text', 'Nokia N810\n128 x 72 x 14 mm', 204, 37, 14.05, 7, self.M['legend'], g)
        return o


# ----------------------------------------------------------------------------------------------- stage
def stage(engine='cycles', samples=160, size=(1920, 1080), floor=True, transparent=False):
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.film_transparent = transparent
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    if engine == 'eevee':
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
        sc.eevee.taa_render_samples = 64
        sc.eevee.use_raytracing = True
        sc.eevee.use_shadows = True
    else:
        sc.render.engine = 'CYCLES'
        p = bpy.context.preferences.addons['cycles'].preferences
        gpu = None
        for kind in ('OPTIX', 'CUDA'):                  # the distribution's Blender has neither: it renders on the CPU
            try:
                p.compute_device_type = kind
                p.get_devices()
                if any(d.type == kind for d in p.devices):
                    gpu = kind
                    break
            except TypeError:
                pass
        for d in p.devices:
            d.use = d.type == gpu
        sc.cycles.device = 'GPU' if gpu else 'CPU'
        print('CYCLES on', gpu or 'CPU', flush=True)
        sc.cycles.samples = samples
        sc.cycles.use_adaptive_sampling = True
        sc.cycles.adaptive_threshold = 0.02
        sc.cycles.use_denoising = False
        for den in (['OPTIX'] if gpu == 'OPTIX' else []) + ['OPENIMAGEDENOISE']:
            try:
                sc.cycles.denoiser = den
                sc.cycles.use_denoising = True
                break
            except TypeError:
                pass
        sc.cycles.max_bounces = 6
        sc.cycles.sample_clamp_indirect = 4.0
        sc.render.use_persistent_data = True
    w = bpy.data.worlds.new('w')
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes['Background']
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Generated'], sep.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position, ramp.color_ramp.elements[0].color = 0.35, (0.012, 0.014, 0.02, 1)
    ramp.color_ramp.elements[1].position, ramp.color_ramp.elements[1].color = 0.95, (0.10, 0.11, 0.14, 1)
    nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = 1.0

    def soft(name, loc, size_, watts, colour=(1, 1, 1)):
        l = bpy.data.lights.new(name, 'AREA')
        l.shape, l.size, l.size_y = 'RECTANGLE', size_[0], size_[1]
        l.energy, l.color = watts, colour
        o = link(bpy.data.objects.new(name, l))
        o.location = loc
        o.rotation_euler = (Vector((64, 37, 8)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        return o
    # mm scene: a light a few hundred "metres" away needs watts in the millions
    soft('key', (-140, -120, 330), (300, 220), 2.2e6, (1.0, 0.97, 0.92))
    soft('fill', (330, -40, 160), (260, 200), 5e5, (0.85, 0.9, 1.0))
    soft('rim', (90, 330, 150), (360, 120), 1.4e6, (0.9, 0.95, 1.0))
    if floor:
        bpy.ops.mesh.primitive_plane_add(size=6000, location=(64, 37, -60))
        f = bpy.context.active_object
        f.name = 'floor'
        f.data.materials.append(mat('floor', (0.016, 0.018, 0.024), 0.5))
    cam = bpy.data.cameras.new('cam')
    co = link(bpy.data.objects.new('cam', cam))
    cam.lens, cam.sensor_width = 70, 36
    cam.clip_start, cam.clip_end = 5, 20000
    sc.camera = co
    return co


def aim(cam, target, az, el, dist, lens=70):
    az, el = math.radians(az), math.radians(el)
    t = Vector(target)
    cam.location = t + Vector((dist * math.cos(el) * math.sin(az), -dist * math.cos(el) * math.cos(az), dist * math.sin(el)))
    cam.rotation_euler = (t - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = lens


def ease(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


# shot(u) with u = 0..1 -> dict(slide, explode, target, az, el, dist, hide, floor_z)
def s_hero(u):
    return dict(slide=0, explode=0, target=(64, 37, 10), az=lerp(-35, 35, ease(u)), el=lerp(34, 26, ease(u)), dist=430)


def s_open(u):
    return dict(slide=ease((u - 0.15) / 0.5), explode=0, target=(64, lerp(37, 20, ease(u)), 8), az=lerp(-22, -8, ease(u)),
                el=lerp(30, 40, ease(u)), dist=lerp(430, 470, ease(u)))


def s_explode(u):
    e = ease((u - 0.1) / 0.55)
    return dict(slide=1, explode=e, target=(64, 20, lerp(8, 12, e)), az=lerp(-8, 40, ease(u)), el=lerp(40, 14, e),
                dist=lerp(470, 640, e))


BOARD = ('carrier',)


def s_board(u):
    """The carrier alone, component side up, turning."""
    return dict(slide=0, explode=0, only=BOARD, flip=True, target=(90, 39, 2), az=lerp(120, 235, ease(u)), el=lerp(48, 32, ease(u)),
                dist=330, floor_z=-1.2)


def s_board_b(u):
    """The carrier's display side."""
    return dict(slide=0, explode=0, only=BOARD, target=(90, 39, C.Z_CARRIER_B), az=lerp(30, -40, ease(u)), el=lerp(55, 40, ease(u)),
                dist=330, floor_z=C.Z_CARRIER_F - 5.2)


def s_module(u):
    """The compute module coming down onto its two sockets."""
    return dict(slide=0, explode=0, only=('carrier', 'module'), flip=True, module_lift=28 * (1 - ease((u - 0.15) / 0.55)),
                target=(90, 39, 4), az=lerp(150, 195, ease(u)), el=lerp(30, 42, ease(u)), dist=360, floor_z=-1.2)


def s_keyboard(u):
    """The keyboard board with its switches, alone."""
    return dict(slide=0, explode=0, only=('kbd',), target=(64, 36, 1), az=lerp(-25, 25, ease(u)), el=lerp(50, 38, ease(u)), dist=400,
                floor_z=-0.05)


def s_compare(u):
    """Closed, beside a block the size of an N810."""
    return dict(slide=0, explode=0, only=None, show_n810=True, target=(134, 37, 8), az=lerp(-25, 0, ease(u)), el=lerp(32, 12, ease(u)),
                dist=lerp(700, 640, ease(u)))


def s_keys(u):
    return dict(slide=1, explode=0, target=(lerp(40, 88, ease(u)), -14, 3), az=lerp(-18, 12, ease(u)), el=38, dist=210, lens=85)


def s_ports(u):
    return dict(slide=0, explode=0, target=(128, 37, 10), az=lerp(60, 100, ease(u)), el=lerp(16, 8, ease(u)), dist=230, lens=85)


SHOTS = {'hero': (s_hero, 180), 'open': (s_open, 150), 'explode': (s_explode, 240), 'keys': (s_keys, 120),
         'ports': (s_ports, 120), 'board': (s_board, 240), 'board_b': (s_board_b, 150), 'module': (s_module, 150),
         'keyboard': (s_keyboard, 150), 'compare': (s_compare, 150)}


def main():
    argv = sys.argv[sys.argv.index('--') + 1:]
    shot, out = argv[0], argv[1]
    opt = dict(zip(argv[2::1], argv[3::1]))

    def arg(name, n, default):
        if name in argv:
            i = argv.index(name)
            return [type(default[0])(v) for v in argv[i + 1:i + 1 + n]]
        return default
    fn, total = SHOTS[shot]
    a, b = arg('--frames', 2, [0, total - 1])
    size = arg('--size', 2, [1920, 1080])
    samples = arg('--samples', 1, [160])[0]
    engine = arg('--engine', 1, ['cycles'])[0]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    dev = Device()
    cam = stage(engine, samples, size)
    os.makedirs(out, exist_ok=True)
    floor = bpy.data.objects.get('floor')
    for f in range(a, b + 1):
        if os.path.exists(os.path.join(out, f'{shot}-{f:04d}.png')) and '--force' not in argv:
            continue                       # resume: frames already on disk are kept
        st = fn(f / max(1, total - 1))
        only = st.get('only')
        if st.get('show_n810'):
            only = tuple(dev.g)
        dev.set(st['slide'], st['explode'], st.get('hide', ()), only, st.get('flip', False), st.get('module_lift', 0.0))
        if floor:
            floor.hide_render = not st.get('floor', True)
            floor.location.z = st.get('floor_z', -32 * st['explode'] - 0.05)
        aim(cam, st['target'], st['az'], st['el'], st['dist'], st.get('lens', 70))
        bpy.context.scene.render.filepath = os.path.join(out, f'{shot}-{f:04d}.png')
        bpy.ops.render.render(write_still=True)
        print('FRAME', shot, f, flush=True)


if __name__ == '__main__':
    main()
