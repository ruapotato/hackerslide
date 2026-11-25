"""HackerSlide 810 parametric enclosure (CadQuery).  All dimensions come from config.py.

python hackerslide.py [--out DIR]   builds every part, checks collisions closed + open, exports STL/STEP
                                    and writes scene files for the renders (render.sh).

World frame: X = device width, Y = device height with the TOP edge at Y = BODY_H (so a top view reads
naturally), Z = thickness (screen up).  Device-plan coordinates (y down from the top edge) are converted with
Y = BODY_H - y.
"""
import argparse
import json
import os
import sys

import cadquery as cq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C  # noqa: E402


def box(x0, y0, z0, x1, y1, z1):
    """Axis-aligned box from device-plan coords (y measured down from the top edge)."""
    return (cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, C.BODY_H - y1, z0)))


def rbox(x0, y0, z0, x1, y1, z1, r):
    b = box(x0, y0, z0, x1, y1, z1)
    r = min(r, (x1 - x0) / 2 - 0.01, (y1 - y0) / 2 - 0.01)
    return b.edges('|Z').fillet(r) if r > 0.05 else b


def cyl(x, y, z0, z1, d):
    return cq.Workplane('XY').circle(d / 2).extrude(z1 - z0).translate((x, C.BODY_H - y, z0))


carrier_to_device = C.carrier_to_device


# --------------------------------------------------------------------------------------------- envelopes
def envelopes():
    e = {}
    px, py = C.PANEL_XY
    e['panel'] = box(px, py, C.Z_PANEL_BOTTOM, px + C.PANEL['w'], py + C.PANEL['h'], C.Z_PANEL_TOP)
    # folded panel tails behind the panel: component bulge of the display tail (along the FPC edge = device right)
    # and the two connectors J4/J5 on the carrier's display side
    b = C.PANEL['tail_bulge']
    e['panel_tails'] = box(px + C.PANEL['w'] - C.PANEL['tft_bulge_len'], py + 4.0, C.Z_PANEL_BOTTOM - b,
                           px + C.PANEL['w'], py + C.PANEL['h'] - 4.0, C.Z_PANEL_BOTTOM)
    for (kx, ky), n in ((C.J4_KICAD, 20), (C.J5_KICAD, 8)):
        x, y = carrier_to_device(kx, ky)
        half = (0.5 * (n - 1) + 2.5) / 2
        e['panel_tails'] = e['panel_tails'].union(box(x - 0.4, y - half, C.Z_CARRIER_B, x + 3.4, y + half, C.Z_CARRIER_B + 1.0))
    cx, cy = C.CARRIER_XY
    e['carrier'] = rbox(cx, cy, C.Z_CARRIER_F, cx + C.CARRIER['w'], cy + C.CARRIER['h'], C.Z_CARRIER_B, C.CARRIER['r'])
    for (x, y) in C.SCREW_XY:
        e['carrier'] = e['carrier'].cut(cyl(x, y, C.Z_CARRIER_F - 1, C.Z_CARRIER_B + 1, 2.4))
    # module hangs below the carrier F side
    mx0, my0 = C.MODULE_XY
    e['module'] = box(mx0, my0, C.Z_CARRIER_F - C.MODULE['mated'], mx0 + C.MODULE['w'], my0 + C.MODULE['h'], C.Z_CARRIER_F)
    # tallest carrier parts on the F side (heights from the datasheets quoted in docs/audit-2026-11-24.md)
    jx, jy = carrier_to_device(0.6, C.JACK_KICAD_Y)
    e['carrier_parts'] = box(jx - 12.0, jy - 3.2, C.Z_CARRIER_F - 4.5, jx, jy + 3.2, C.Z_CARRIER_F)            # PJ-342, 4.5 high
    ux, uy = carrier_to_device(0.0, C.USB_KICAD_Y)
    e['carrier_parts'] = e['carrier_parts'].union(box(ux - 6.3, uy - 4.5, C.Z_CARRIER_F - 3.3, ux + 0.25, uy + 4.5, C.Z_CARRIER_F))
    sx_, sy_ = carrier_to_device(0.0, C.SD_KICAD_Y)
    e['carrier_parts'] = e['carrier_parts'].union(box(sx_ - 13.9, sy_ - 6.1, C.Z_CARRIER_F - 1.5, sx_, sy_ + 6.1, C.Z_CARRIER_F))
    lx, ly = carrier_to_device(54.2, 7.8)                                                                       # L3, 3.0 high
    e['carrier_parts'] = e['carrier_parts'].union(box(lx - 2.1, ly - 2.1, C.Z_CARRIER_F - 3.0, lx + 2.1, ly + 2.1, C.Z_CARRIER_F))
    bx0, by0 = C.BATT_XY
    e['battery'] = box(bx0, by0, C.Z_BACK_IN, bx0 + C.BATTERY['w'], by0 + C.BATTERY['h'], C.Z_BACK_IN + C.BATTERY['t'] + C.BATTERY['swell'])
    # thermal pad / copper shim from the SoC to the back-shell floor (SoC position = CM4 drawing estimate)
    sx = mx0 + C.SOC_XY[0] - C.MODULE['soc_size'][0] / 2
    sy = my0 + C.SOC_XY[1] - C.MODULE['soc_size'][1] / 2
    zb = C.Z_CARRIER_F - C.MODULE['mated']
    e['thermal_pad'] = box(sx, sy, C.Z_BACK_IN, sx + C.MODULE['soc_size'][0], sy + C.MODULE['soc_size'][1], zb)
    return e


def keyboard_stack(dy=0.0):
    """Keyboard PCB, switches as a slab, keycaps (as one slab per row) and top plate, in tray coords + dy."""
    kx, ky = C.KBD_XY
    w, h = C.KBD_PCB['w'], C.KBD_PCB['h']
    z = C.TRAY_FLOOR + C.KBD_PCB['under_gap']
    s = {}
    s['kbd_pcb'] = box(kx, ky - C.KBD_PCB['top_ext'] + dy, z, kx + w, ky + h + dy, z + C.KBD_PCB['t'])   # = tray floor
    z += C.KBD_PCB['t'] + C.SWITCH_H + C.KEYCAP['nub_h']      # keycap flange underside (the nub reaches the switch)
    zf = z + C.KEYCAP['flange_t']
    zp0 = zf + 0.1
    s['top_plate'] = box(kx, ky + dy, zp0, kx + w, ky + h + dy, zp0 + C.PLATE_T)
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'hardware', 'scripts'))
    import kbd_layout as KL
    c = KL.CAP
    flanges, tops = None, None
    for (name, r, col, x, y) in KL.keys('alps'):
        if name == 'Space' and col == 7:
            continue                                   # 2u space cap is drawn once, centred on both switches
        fw, fh, tw, th = c['flange_w'], c['flange_h'], c['top_w'], c['top_h']
        if name == 'Space':
            x += KL.PITCH_X / 2
            fw += KL.PITCH_X
            tw += KL.PITCH_X
        if r == 4:
            fw = fh = 5.6
            tw = th = 4.6
        X, Y = kx + x, ky + y + dy
        f = box(X - fw / 2, Y - fh / 2, z, X + fw / 2, Y + fh / 2, z + c['flange_t'])
        t = box(X - tw / 2, Y - th / 2, z + c['flange_t'] - 0.01, X + tw / 2, Y + th / 2, z + c['flange_t'] + c['top_t'])
        flanges = f if flanges is None else flanges.union(f)
        tops = t if tops is None else tops.union(t)
    s['keycap_flanges'] = flanges
    s['keycap_tops'] = tops
    return s


# --------------------------------------------------------------------------------------------- printed parts
def front_shell():
    z0 = C.Z_BODY_BOTTOM + C.BACK_TUB_H
    z1 = C.Z_BODY_TOP
    s = rbox(0, 0, z0, C.BODY_W, C.BODY_H, z1, C.CORNER_R)
    s = s.cut(rbox(C.WALL, C.WALL, z0 - 0.01, C.BODY_W - C.WALL, C.BODY_H - C.WALL, z1 - C.BEZEL_LIP, C.CORNER_R - C.WALL))
    px, py = C.PANEL_XY
    s = s.cut(box(px - 0.2, py - 0.2, C.Z_PANEL_BOTTOM - 0.5, px + C.PANEL['w'] + 0.2, py + C.PANEL['h'] + 0.2, C.Z_PANEL_TOP))
    lip = 1.5   # roof overlaps the lens edge by 1.5 mm (lens 97.70 x 57.86, touch view area 87.40 x 52.44)
    s = s.cut(rbox(px + lip, py + lip, z1 - C.BEZEL_LIP - 0.1, px + C.PANEL['w'] - lip, py + C.PANEL['h'] - lip, z1 + 0.1, 1.0))
    # screw bosses with M2 heat-set inserts (screws come in from the back).  They stand on the carrier's display
    # side around HS1/HS2: together with the back-shell bosses they clamp the board.
    for (x, y) in C.SCREW_XY:
        boss = cyl(x, y, C.Z_CARRIER_B, z1 - C.BEZEL_LIP, C.BOSS_D)
        s = s.union(boss).cut(cyl(x, y, C.Z_CARRIER_B - 0.01, C.Z_CARRIER_B + C.SCREWS['insert_l'] + 0.5, C.SCREWS['insert_d']))
    # side openings on the device right edge (audit E1: the connector mouths are 0.3-0.6 mm behind the outer face,
    # so an opening only needs to pass the metal plug, with 0.3 mm play)
    zc = C.Z_CARRIER_F
    xw = C.BODY_W - C.WALL - 0.5
    _, yu = carrier_to_device(0, C.USB_KICAD_Y)
    s = s.cut(rbox_x(xw, yu - 4.7, zc - 3.5, C.BODY_W + 0.5, yu + 4.7, zc + 0.1))                    # USB-C shell 8.94 x 3.26
    _, yj = carrier_to_device(0, C.JACK_KICAD_Y)
    s = s.cut(cq.Workplane('YZ').circle(2.8).extrude(C.WALL + 1.0).translate((xw, C.BODY_H - yj, zc - 2.3)))   # jack collar dia 5
    _, ys = carrier_to_device(0, C.SD_KICAD_Y)
    s = s.cut(box(xw, ys - 6.0, zc - 1.6, C.BODY_W + 0.5, ys + 6.0, zc - 0.1))                       # microSD card 11 wide
    # button openings on the top edge (printed button caps bridge the 1.6 mm from the switch plunger to the wall)
    for kx in C.BUTTON_KICAD_X:
        xx, _ = carrier_to_device(kx, 0)
        s = s.cut(box(xx - 2.2, -0.5, zc - 2.0, xx + 2.2, C.WALL + 0.5, zc - 0.1))
    return s


def rbox_x(x0, y0, z0, x1, y1, z1):
    """Box with its edges along X rounded (a slot through a side wall)."""
    r = min((z1 - z0), (y1 - y0)) / 2 - 0.05
    return box(x0, y0, z0, x1, y1, z1).edges('|X').fillet(r)


def back_shell():
    z0 = C.Z_BODY_BOTTOM
    z1 = z0 + C.BACK_TUB_H
    xi = C.RAIL_INSET
    s = rbox(xi, 0, z0, C.BODY_W - xi, C.BODY_H, z1, C.CORNER_R - xi)
    s = s.cut(rbox(xi + C.WALL, C.WALL, C.Z_BACK_IN, C.BODY_W - xi - C.WALL, C.BODY_H - C.WALL, z1 + 0.01,
                   0.8))        # nearly square inside corners: the 50 x 68 mm battery pack fills the bay end to end
    # screw bosses: from the floor up to the carrier's component side (clamp), screw from outside
    for (x, y) in C.SCREW_XY:
        s = s.union(cyl(x, y, z0, C.Z_CARRIER_F, C.BOSS_D)).cut(cyl(x, y, z0 - 0.01, C.Z_CARRIER_F + 0.01, C.SCREWS['screw_d']))
    # detent magnet pockets in the floor, pressed in from outside: A = closed, B = open (audit E2/E3)
    m = C.MAGNET_BODY
    for x in C.MAGNET_X:
        for y in (C.MAGNET_Y_CLOSED, C.MAGNET_Y_OPEN):
            s = s.cut(cyl(x, y, z0 - 0.01, z0 + m['t'], m['d'] + 2 * m['clear']))
    # the 4.5 mm jack hangs lower than the tub wall top: notch the wall there
    jx, jy = carrier_to_device(0.6, C.JACK_KICAD_Y)
    s = s.cut(box(jx - 12.4, jy - 3.6, C.Z_CARRIER_F - 4.8, C.BODY_W, jy + 3.6, z1 + 0.01))
    # keyboard cable slot through the floor, below carrier J9 (audit E5)
    f = C.FPC_SLOT
    s = s.cut(box(C.KBD_FPC_X - f['w'] / 2, f['y'] - f['l'] / 2, z0 - 0.5, C.KBD_FPC_X + f['w'] / 2, f['y'] + f['l'] / 2, C.Z_BACK_IN + 0.5))
    # channel in the underside of the floor for the cable run and its rolling loop (0.4 mm of floor remains)
    s = s.cut(box(C.KBD_FPC_X - f['w'] / 2, C.FPC_LOOP_Y_OPEN_TRAY - 1.0, z0 - 0.01, C.KBD_FPC_X + f['w'] / 2, f['y'], z0 + C.FPC['channel']))
    # rail grooves on the left/right outer faces (the tray lips run in these); cut last so bosses cannot fill them
    gz = z0 + 0.7
    gh = 0.8 + 2 * C.RAIL['clear']
    for x0 in (xi - 0.01, C.BODY_W - xi - C.RAIL['lip'] - C.RAIL['clear']):
        s = s.cut(box(x0, -0.5, gz, x0 + C.RAIL['lip'] + C.RAIL['clear'] + 0.01, C.BODY_H + 0.5, gz + gh))
    return s


def tray(dy=0.0):
    """Keyboard tray FRAME incl. side rails (lips) and magnet posts.  It has no floor: the keyboard PCB closes the
    bottom and is glued into the frame.  dy = slide offset in device-plan y."""
    zt = C.Z_TRAY_TOP
    zp = C.TRAY_FLOOR + C.KBD_PCB['t']             # top face of the keyboard PCB
    s = rbox(0, dy, 0, C.BODY_W, C.BODY_H + dy, zt, C.CORNER_R)
    s = s.cut(rbox(C.WALL, C.WALL + dy, -0.01, C.BODY_W - C.WALL, C.BODY_H - C.WALL + dy, zt + 0.01, 1.0))
    # side rails: walls rising beside the back-shell tub, with an inward lip into its groove
    zr1 = C.Z_BODY_BOTTOM + C.BACK_TUB_H - 0.3
    gz = C.Z_BODY_BOTTOM + 0.7 + C.RAIL['clear']
    for (x0, x1, lx0, lx1) in ((0, C.RAIL['w'], C.RAIL['w'], C.RAIL['w'] + C.RAIL['lip']),
                               (C.BODY_W - C.RAIL['w'], C.BODY_W, C.BODY_W - C.RAIL['w'] - C.RAIL['lip'], C.BODY_W - C.RAIL['w'])):
        s = s.union(box(x0, dy + C.CORNER_R, zt - 0.01, x1, C.BODY_H + dy - C.CORNER_R, zr1))
        s = s.union(box(lx0, dy + C.CORNER_R, gz, lx1, C.BODY_H + dy - C.CORNER_R, gz + 0.8))
    # magnet posts on the PCB, tied to the nearest frame wall by a rib: one detent magnet per side and the
    # slider-closed sense magnet
    posts = ([(x, C.MAGNET_Y_CLOSED, C.MAGNET_TRAY, 'x') for x in C.MAGNET_X] + [C.HALL_XY + (C.MAGNET_HALL, 'y')])
    for (x, y, m, rib) in posts:
        d = m['d'] + 2.4
        post = cyl(x, y + dy, zp, zt - 0.1, d)
        if rib == 'x':
            xw = C.WALL if x < C.BODY_W / 2 else C.BODY_W - C.WALL
            post = post.union(box(min(x, xw), y + dy - d / 2, zp, max(x, xw), y + dy + d / 2, zt - 0.1))
        else:
            post = post.union(box(x - d / 2, C.WALL + dy - 0.01, zp, x + d / 2, y + dy, zt - 0.1))
        s = s.union(post).cut(cyl(x, y + dy, zt - 0.1 - m['t'], zt, m['d'] + 2 * m['clear']))
    # The keyboard cable makes its rolling loop above the PCB in the tray's upper half, in the lane
    # x = KBD_FPC_X +/- 4 mm, which is kept free of posts (see docs/enclosure.md).
    return s


def magnets(dy_tray=0.0):
    out = []
    mb, mt, mh = C.MAGNET_BODY, C.MAGNET_TRAY, C.MAGNET_HALL
    for x in C.MAGNET_X:
        for y in (C.MAGNET_Y_CLOSED, C.MAGNET_Y_OPEN):
            out.append(cyl(x, y, C.Z_BODY_BOTTOM, C.Z_BODY_BOTTOM + mb['t'], mb['d']))
        out.append(cyl(x, C.MAGNET_Y_CLOSED + dy_tray, C.Z_TRAY_TOP - 0.1 - mt['t'], C.Z_TRAY_TOP - 0.1, mt['d']))
    hx, hy = C.HALL_XY
    out.append(cyl(hx, hy + dy_tray, C.Z_TRAY_TOP - 0.1 - mh['t'], C.Z_TRAY_TOP - 0.1, mh['d']))
    u = out[0]
    for o in out[1:]:
        u = u.union(o)
    return u


def keycap(kind='key'):
    """Printable test keycap: flange under the top plate + top through it."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'hardware', 'scripts'))
    import kbd_layout as KL
    c = KL.CAP
    tw, th = c['top_w'], c['top_h']
    fw, fh = c['flange_w'], c['flange_h']
    if kind == 'space':
        tw += KL.PITCH_X
        fw += KL.PITCH_X
    if kind == 'dpad':
        tw = th = 4.6
        fw = fh = 5.6
    k = cq.Workplane('XY').rect(fw, fh).extrude(c['flange_t']).edges('|Z').fillet(0.4)
    k = k.union(cq.Workplane('XY').rect(tw, th).extrude(c['flange_t'] + c['top_t']).edges('|Z').fillet(0.8))
    k = k.faces('>Z').edges().fillet(0.25)
    # actuator nub under the cap centre: flat cylinder dia 1.2 (Alps asks for 1.0-1.5), height from config (audit K1)
    return k.union(cq.Workplane('XY').circle(0.6).extrude(-C.KEYCAP['nub_h']))


# --------------------------------------------------------------------------------------------- assembly
def assembly(open_=False):
    dy = C.TRAVEL if open_ else 0.0   # open: the tray moves toward the user by TRAVEL (plan +y)
    parts = {'front_shell': front_shell(), 'back_shell': back_shell(), 'tray': tray(dy), 'magnets': magnets(dy)}
    parts.update(envelopes())
    parts.update(keyboard_stack(dy))
    return parts


def collisions(parts, tol=0.01):
    names = sorted(parts)
    hits = []
    allowed = {('magnets', 'back_shell'), ('magnets', 'tray'), ('module', 'thermal_pad'), ('back_shell', 'thermal_pad'),
               ('carrier', 'panel_tails'),
               ('keycap_tops', 'top_plate'), ('keycap_flanges', 'keycap_tops')}   # caps pass through plate openings
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if (a, b) in allowed or (b, a) in allowed:
                continue
            try:
                v = parts[a].intersect(parts[b]).val().Volume()
            except Exception:
                v = 0.0
            if v > tol:
                hits.append((a, b, round(v, 3)))
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    ap.add_argument('--no-check', action='store_true')
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    for d in ('stl', 'step', 'renders'):
        os.makedirs(os.path.join(out, d), exist_ok=True)
    report = {'stack_mm': {k: round(getattr(C, k), 2) for k in ('TRAY_T', 'Z_BODY_BOTTOM', 'Z_BACK_IN', 'BAY_H', 'CAVITY', 'THERMAL_GAP', 'PANEL_GAP', 'FPC_LOOP_R', 'FPC_LEN',
                                                                  'Z_CARRIER_F', 'Z_PANEL_TOP', 'BODY_T', 'TOTAL_T',
                                                                  'TRAVEL', 'OPEN_H')},
              'battery_layout': C.BATTERY_LAYOUT}
    closed = assembly(False)
    opened = assembly(True)
    if not a.no_check:
        report['collisions_closed'] = collisions(closed)
        report['collisions_open'] = collisions(opened)
    # printable / machinable parts
    printable = {'front_shell': closed['front_shell'], 'back_shell': closed['back_shell'], 'keyboard_tray': tray(0.0),
                 'keycap_1u': keycap('key'), 'keycap_space_2u': keycap('space'), 'keycap_dpad': keycap('dpad')}
    for n, p in printable.items():
        cq.exporters.export(p, os.path.join(out, 'stl', n + '.stl'), tolerance=0.02, angularTolerance=0.1)
        cq.exporters.export(p, os.path.join(out, 'step', n + '.step'))
    # assembly STEP (closed) and per-part scene STLs for the renders
    asm = cq.Assembly(name='hackerslide810_closed')
    for n, p in closed.items():
        asm.add(p, name=n)
    asm.save(os.path.join(out, 'step', 'assembly_closed.step'))
    scene = os.path.join(out, 'renders', 'scene')
    os.makedirs(scene, exist_ok=True)
    for tag, parts in (('closed', closed), ('open', opened)):
        for n, p in parts.items():
            cq.exporters.export(p, os.path.join(scene, f'{tag}_{n}.stl'), tolerance=0.05, angularTolerance=0.2)
    # section through the SoC (x = SECTION_X): keep x < SECTION_X of every closed part
    cut = box(-10, -10, -10, C.SECTION_X, C.BODY_H + 50, 40)
    for n, p in closed.items():
        try:
            sp = p.intersect(cut)
            if sp.val().Volume() > 0.01:
                cq.exporters.export(sp, os.path.join(scene, f'section_{n}.stl'), tolerance=0.05, angularTolerance=0.2)
        except Exception:
            pass
    json.dump(report, open(os.path.join(out, 'collision-report.json'), 'w'), indent=1)
    print(json.dumps(report, indent=1))


if __name__ == '__main__':
    main()
