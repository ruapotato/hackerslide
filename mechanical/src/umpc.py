"""HackerSlide UMPC concept (WiBrain-style): a landscape screen in the middle, a thumb keyboard on each side.

  python umpc.py [--out DIR]       parts as STL (closed and exploded scene files), stack.json, collision check

CONCEPT MODEL.  Brain: the LuckFox Core3566 module of the Linux handheld (55 x 40 mm, 4.50 mm above the carrier when
mated on its two DF40 sockets: measured on LuckFox's STEP model, mechanical/src/config.py on branch linux-handheld).
Screen: Focus LCDs E40RB-I-MW430-CB 4.0" 480 x 800 IPS with touch (data sheet dimensions), used landscape.  Batteries: two
flat cells under the keyboard halves, size an ESTIMATE, no cell chosen yet.  Everything marked [est] is a guess.

Layout, as asked (David, 2026-11-27): screen on top; under it the board and the batteries side by side in one
layer, for the thinnest stack.  X width, Y height (top edge at Y = H), Z thickness (back at Z = 0), screen up.
"""
import argparse
import json
import os

import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
# ------------------------------------------------------------------------------------------- dimensions (mm)
# Focus LCDs E40RB-I-MW430-CB, the Linux handheld's 4.0" 480 x 800 IPS with capacitive touch, used landscape:
# outline, active area and thickness from its data sheet (mechanical/src/config.py on branch linux-handheld)
PANEL_4IN = dict(w=98.10, h=58.26, t=4.25, aa_w=86.40, aa_h=51.84)
# Squarer option (David, 2026-11-27): a 3.5" 640 x 480 (4:3) IPS panel with capacitive touch.  Outline of BuyDisplay
# ER-TFT035-7 (76.84 x 63.84 x 3.2 mm, from its product page); active area and the touch panel's extra thickness are
# ESTIMATES.  The Newhaven NHD-3.5-640480EF-MSXP-CTP (MIPI DSI, touch, DigiKey) is the same class.
PANEL_35IN = dict(w=76.84, h=63.84, t=3.2 + 1.0, aa_w=70.08, aa_h=52.56)
PANEL = PANEL_35IN
MODULE = dict(w=55.0, h=40.0, mated=4.50, soc_top=3.60)      # LuckFox Core3566 (measured, see above)
CARRIER_T = 1.0
KEY = dict(pitch_x=7.0, pitch_y=7.0, cap_w=6.3, cap_h=6.2, cols=5, rows=4)
SWITCH_H, NUB, FLANGE, CAP_TOP = 0.6, 0.3, 0.5, 1.2           # as the keyboards of the earlier designs
KBD_PCB_T = 0.8
CELL = dict(w=38.5, h=62.0, t=8.5, inset=2.5)                # Adafruit #2011 (PKCELL LP803860, 2000 mAh, protection board, JST-PH),
                                                             # one per side, in parallel: DigiKey 3,704 at $12.50 on 2026-11-27.
                                                             # Bay sized to the maker's drawing maximum 62 x 38.5 x 8.5 mm
                                                             # (Adafruit says 60 x 36 x 7; a UN 38.3 sample measured 60 x 37 x 7.4)
CONTROLS = 'padball'                                         # 'padball': slide stick left, round 35 mm trackpad right used as a
                                                             # 'virtual trackball' (momentum + haptic, as the Steam Controller);
                                                             # 'sticks': two slide thumbsticks (David, 2026-11-27, to stay thin);
                                                             # 'ball': trackball + slide stick; 'fallback': D-pad + touchpad
TRACKBALL = dict(w=25.0, h=22.0, t=9.5, ball=8.0, protrude=1.0)   # Pimoroni PIM447 breakout: 25 x 22 x 9.5 mm (retailer
                                                             # data); ball size and how far it stands out: ESTIMATES
PADBALL = dict(d=35.0, t=2.5)                                # Cirque GlidePoint TM035035 class round trackpad (35 mm; thickness
                                                             # an ESTIMATE), set 0.5 mm below the frame like a dish
SLIDEPAD = dict(base=19.0, t=4.0, cap=15.0, cap_t=1.6)       # SparkFun COM-09426, PSP-1000-style slide stick: ALL ESTIMATES
BACK, WALL, FRONT = 1.2, 1.6, 0.8                            # [est] printed back; front frame over the screen border
THERMAL_MIN = 0.5                                            # [est] thinnest pad from the SoC lid to an aluminium plate in the back
GAP = 0.3
HALF_W = max(KEY['cols'] * KEY['pitch_x'] + 4.0, CELL['w'] + CELL['inset'] + 1.0)   # keyboard half, wide enough for its cell
W = PANEL['w'] + 2 * HALF_W + 2 * WALL + 2.0
H = 72.0                                                     # the N810's height: room for keys above and a pad below on each side
END_R = 11.0                                                 # rounded grips at the two ends

# Z stack, centre (screen over the module) and sides (keys over the cells)
# carrier bottom face; the module hangs under it.  Its tallest part (an inductor, 4.50 below the carrier) needs 0.2 mm
# above the back; the SoC lid (3.60 below) then gets a thicker pad.
Z_CARRIER = BACK + max(THERMAL_MIN + MODULE['soc_top'], MODULE['mated'] + 0.2)
THERMAL = Z_CARRIER - MODULE['soc_top'] - BACK
Z_CARRIER_TOP = Z_CARRIER + CARRIER_T
KEYSTACK = KBD_PCB_T + SWITCH_H + NUB + FLANGE + CAP_TOP
Z_CELL = BACK
T_CENTRE = Z_CARRIER_TOP + 0.9 + GAP + PANEL['t'] + FRONT * 0.5    # 0.9 [est]: tallest part on the carrier's screen side
T_SIDE = Z_CELL + CELL['t'] + GAP + KEYSTACK
T_BALL = Z_CELL + CELL['t'] + GAP + TRACKBALL['t'] - TRACKBALL['protrude'] if CONTROLS == 'ball' else 0
T_STICK = Z_CELL + CELL['t'] + 0.2 + SLIDEPAD['t'] + 0.1 + FRONT * 0.5 if CONTROLS in ('ball', 'sticks', 'padball') else 0
T = max(T_CENTRE, T_SIDE, T_BALL, T_STICK)                            # everything is then raised to one top surface
Z_TOP = T
Z_FRONT = T - FRONT * 0.5                                    # the front frame sits on the panel border
Z_PANEL = Z_FRONT - PANEL['t']
Z_KBD = T - KEYSTACK
Z_KEYTOP = T
CX, CY = W / 2, H / 2


def rbox(x0, y0, z0, x1, y1, z1, r=0.0):
    b = cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))
    r = min(r, (x1 - x0) / 2 - 0.01, (y1 - y0) / 2 - 0.01)
    return b.edges('|Z').fillet(r) if r > 0.05 else b


def outline(z0, z1, inset=0.0):
    return rbox(inset, inset, z0, W - inset, H - inset, z1, END_R - inset)


def key_centres():
    out = []
    for side, x0 in (('L', WALL + 3.0), ('R', W - WALL - 3.0 - KEY['cols'] * KEY['pitch_x'])):
        for r in range(KEY['rows']):
            for c in range(KEY['cols']):
                out.append((side, r, c, x0 + (c + 0.5) * KEY['pitch_x'], H - WALL - 3.5 - (r + 0.5) * KEY['pitch_y']))
    return out


LEGENDS = {'L': [['Esc', '1', '2', '3', '4'], ['Q', 'W', 'E', 'R', 'T'], ['A', 'S', 'D', 'F', 'G'], ['Shift', 'Z', 'X', 'C', 'V']],
           'R': [['5', '6', '7', '8', 'Del'], ['Y', 'U', 'I', 'O', 'P'], ['H', 'J', 'K', 'L', 'Ent'], ['B', 'N', 'M', 'Spc', 'Fn']]}




def slide_stick(front, x, y):
    """A PSP-style slide stick: body just under the front frame (through a hole in the keyboard board), round cap
    moving in an opening.  Dimensions: SLIDEPAD, all estimates until a datasheet or sample is measured."""
    s = SLIDEPAD
    z0 = Z_FRONT - 0.1 - s['t']
    body = rbox(x - s['base'] / 2, y - s['base'] / 2, z0, x + s['base'] / 2, y + s['base'] / 2, z0 + s['t'], 1.5)
    stem = cq.Workplane('XY').circle(3.0).extrude(T - 0.2 - (z0 + s['t'])).translate((x, y, z0 + s['t']))
    cap = cq.Workplane('XY').circle(s['cap'] / 2).extrude(s['cap_t']).translate((x, y, T - 0.2)).edges('>Z').fillet(0.6)
    front = front.cut(cq.Workplane('XY').circle(s['cap'] / 2 + 2.5).extrude(3).translate((x, y, Z_FRONT - 1)))
    hole = rbox(x - s['base'] / 2 - 0.3, y - s['base'] / 2 - 0.3, Z_KBD - 1, x + s['base'] / 2 + 0.3, y + s['base'] / 2 + 0.3, Z_KBD + KBD_PCB_T + 1, 1.5)
    return front, body.union(stem).union(cap), hole


def controls(front):
    """Bottom-left and bottom-right controls; returns the front frame with its openings, the control solids, and the
    holes they need through the keyboard board."""
    zone_top = H - WALL - 3.5 - KEY['rows'] * KEY['pitch_y'] - 2.0
    dx, dy = WALL + 3.0 + KEY['cols'] * KEY['pitch_x'] / 2, (WALL + zone_top) / 2
    tx, ty = W - WALL - 3.0 - KEY['cols'] * KEY['pitch_x'] / 2, dy
    if CONTROLS == 'padball':
        front, solid, hole = slide_stick(front, dx, dy)
        r = PADBALL['d'] / 2
        z0 = Z_KBD + KBD_PCB_T                                      # module sits on the keyboard board
        assert T - 0.5 - z0 >= 1.6, 'trackpad module needs at least 1.6 mm'
        pad = cq.Workplane('XY').circle(r).extrude(T - 0.5 - z0).translate((tx, ty, z0))
        front = front.cut(cq.Workplane('XY').circle(r + 0.3).extrude(3).translate((tx, ty, Z_FRONT - 1)))
        return front, solid.union(pad), [hole]
    if CONTROLS == 'sticks':
        parts_, holes = None, []
        for x in (dx, tx):
            front, solid, hole = slide_stick(front, x, dy)
            parts_ = solid if parts_ is None else parts_.union(solid)
            holes.append(hole)
        return front, parts_, holes
    if CONTROLS == 'ball':
        # left: PSP-style slide stick standing on the keyboard board, its cap moving in a round opening
        s = SLIDEPAD
        z0 = Z_FRONT - 0.1 - s['t']                         # body just under the frame, through a hole in the keyboard board
        body = rbox(dx - s['base'] / 2, dy - s['base'] / 2, z0, dx + s['base'] / 2, dy + s['base'] / 2, z0 + s['t'], 1.5)
        hole_l = rbox(dx - s['base'] / 2 - 0.3, dy - s['base'] / 2 - 0.3, Z_KBD - 1, dx + s['base'] / 2 + 0.3, dy + s['base'] / 2 + 0.3, Z_KBD + KBD_PCB_T + 1, 1.5)
        cap = cq.Workplane('XY').circle(s['cap'] / 2).extrude(s['cap_t']).translate((dx, dy, T - 0.2)).edges('>Z').fillet(0.6)
        stem = cq.Workplane('XY').circle(3.0).extrude(T - 0.2 - (z0 + s['t'])).translate((dx, dy, z0 + s['t']))
        front = front.cut(cq.Workplane('XY').circle(s['cap'] / 2 + 2.5).extrude(3).translate((dx, dy, Z_FRONT - 1)))
        # right: trackball module hanging through the keyboard board, ball standing out of the frame
        b = TRACKBALL
        zt = T + b['protrude']
        mod = rbox(tx - b['w'] / 2, ty - b['h'] / 2, zt - b['t'], tx + b['w'] / 2, ty + b['h'] / 2, zt - b['ball'], 1.0)
        ball = cq.Workplane('XY').sphere(b['ball'] / 2).translate((tx, ty, zt - b['ball'] / 2))
        front = front.cut(cq.Workplane('XY').circle(b['ball'] / 2 + 0.6).extrude(3).translate((tx, ty, Z_FRONT - 1)))
        hole = rbox(tx - b['w'] / 2 - 0.3, ty - b['h'] / 2 - 0.3, Z_KBD - 1, tx + b['w'] / 2 + 0.3, ty + b['h'] / 2 + 0.3, Z_KBD + KBD_PCB_T + 1, 1.0)
        return front, body.union(stem).union(cap).union(mod).union(ball), [hole, hole_l]
    # fallback: a 5-way D-pad (cross cap over five switches) and a touchpad drawn as copper under a 0.5 mm overlay
    # bottom left: a 5-way D-pad (cross cap over five switches on the keyboard board); bottom right: a touchpad drawn
    # as copper on the keyboard board under a 0.5 mm overlay, read by an Azoteq trackpad controller (stock to check)
    cross = rbox(dx - 9.5, dy - 3.2, Z_KBD + KBD_PCB_T + SWITCH_H + NUB, dx + 9.5, dy + 3.2, Z_KEYTOP, 1.0).union(
        rbox(dx - 3.2, dy - 9.5, Z_KBD + KBD_PCB_T + SWITCH_H + NUB, dx + 3.2, dy + 9.5, Z_KEYTOP, 1.0))
    front = front.cut(cq.Workplane('XY').circle(11.0).extrude(3).translate((dx, dy, Z_FRONT - 1)))
    tw, th = KEY['cols'] * KEY['pitch_x'] - 2.0, (zone_top - WALL) - 5.0
    pad = rbox(tx - tw / 2, ty - th / 2, T - 0.6, tx + tw / 2, ty + th / 2, T - 0.3, 2.0)
    front = front.cut(rbox(tx - tw / 2 - 0.2, ty - th / 2 - 0.2, Z_FRONT - 1, tx + tw / 2 + 0.2, ty + th / 2 + 0.2, T + 1, 2.2))
    well = cq.Workplane('XY').circle(10.8).extrude(0.3).translate((dx, dy, Z_KBD + KBD_PCB_T))   # dark disc under the cross
    stick = cross.union(pad).union(well)
    return front, stick, []


def parts():
    shell = outline(0, Z_FRONT).cut(outline(BACK, T, WALL))
    px0, py0 = CX - PANEL['w'] / 2, CY - PANEL['h'] / 2
    front = outline(Z_FRONT, T)
    ax0, ay0 = CX - PANEL['aa_w'] / 2, CY - PANEL['aa_h'] / 2
    front = front.cut(rbox(ax0 - 0.5, ay0 - 0.5, T - FRONT - 1, ax0 + PANEL['aa_w'] + 0.5, ay0 + PANEL['aa_h'] + 0.5, T + 1, 1.5))
    caps = None
    for side, r, c, x, y in key_centres():
        w = KEY['cap_w']
        cap = rbox(x - w / 2, y - KEY['cap_h'] / 2, Z_KBD + KBD_PCB_T + SWITCH_H + NUB, x + w / 2, y + KEY['cap_h'] / 2, Z_KEYTOP, 1.2)
        caps = cap if caps is None else caps.union(cap)
        front = front.cut(rbox(x - w / 2 - 0.3, y - KEY['cap_h'] / 2 - 0.3, T - FRONT - 1, x + w / 2 + 0.3, y + KEY['cap_h'] / 2 + 0.3, T + 1, 1.4))
    front, stick, holes = controls(front)
    kbd = None
    for x0 in (WALL + 1.0, W - WALL - 1.0 - (HALF_W - 1.0)):
        b = rbox(x0, WALL + 2, Z_KBD, x0 + HALF_W - 1.0, H - WALL - 2, Z_KBD + KBD_PCB_T, END_R - WALL - 1.0)
        kbd = b if kbd is None else kbd.union(b)
    for hole in holes:
        kbd = kbd.cut(hole)
    cells = None
    for x0 in (WALL + CELL['inset'], W - WALL - CELL['inset'] - CELL['w']):
        b = rbox(x0, CY - CELL['h'] / 2, Z_CELL, x0 + CELL['w'], CY + CELL['h'] / 2, Z_CELL + CELL['t'], 2.0)
        cells = b if cells is None else cells.union(b)
    carrier = rbox(px0 + 2, py0 + 2, Z_CARRIER, px0 + PANEL['w'] - 2, py0 + PANEL['h'] - 2, Z_CARRIER_TOP, 3.0)
    zb = Z_CARRIER - 1.5                                                                    # sockets 1.5, module board 1.2
    mod = rbox(CX - MODULE['w'] / 2, CY - MODULE['h'] / 2, zb - 1.2, CX + MODULE['w'] / 2, CY + MODULE['h'] / 2, zb, 1.0)
    mod = mod.union(rbox(CX - 20, CY - 16, zb, CX + 20, CY + 16, Z_CARRIER, 0.3))           # the two sockets, as one block
    soc = rbox(CX - 7.5, CY - 7.5, Z_CARRIER - MODULE['soc_top'], CX + 7.5, CY + 7.5, zb - 1.2, 0.5)
    ind = rbox(CX + 15, CY - 6, Z_CARRIER - MODULE['mated'], CX + 19, CY - 2, zb - 1.2, 0.3)   # tallest part
    soc = soc.union(ind)
    thermal = rbox(CX - 9, CY - 9, BACK, CX + 9, CY + 9, BACK + THERMAL, 0.5)
    panel = rbox(px0, py0, Z_PANEL, px0 + PANEL['w'], py0 + PANEL['h'], Z_PANEL + PANEL['t'], 1.0)
    shoulders = None
    for x in (W * 0.16, W * 0.84):
        b = rbox(x - 9, H - 0.4, T * 0.3, x + 9, H + 1.6, T * 0.3 + 3.2, 1.0)
        shoulders = b if shoulders is None else shoulders.union(b)
    screen = (CX - PANEL['aa_w'] / 2, CY - PANEL['aa_h'] / 2, Z_PANEL + PANEL['t'], PANEL['aa_w'], PANEL['aa_h'])
    d = dict(shell=shell, front=front, keycaps=caps, stick=stick, kbd_pcb=kbd, cells=cells, carrier=carrier,
             module=mod.union(soc), thermal=thermal, panel=panel, shoulders=shoulders)
    return d, screen


EXPLODE = dict(shell=0, thermal=6, cells=12, module=20, carrier=28, kbd_pcb=34, panel=44, keycaps=50, stick=56, front=62, shoulders=0)


def collisions(d, tol=0.01):
    bad, names = [], list(d)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if {a, b} in ({'module', 'carrier'}, {'module', 'thermal'}, {'shoulders', 'shell'}, {'stick', 'front'}):
                continue                       # touching by design (sockets, thermal pad, buttons in the wall)
            try:
                v = d[a].intersect(d[b]).val().Volume()
            except Exception:
                v = 0.0
            if v > tol:
                bad.append((a, b, round(v, 2)))
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(HERE, '..', 'umpc'))
    out = ap.parse_args().out
    os.makedirs(os.path.join(out, 'scene'), exist_ok=True)
    d, screen = parts()
    bad = collisions(d)
    print('collisions:', bad or 'none')
    for n, p in d.items():
        cq.exporters.export(p, os.path.join(out, 'scene', f'closed_{n}.stl'), tolerance=0.03, angularTolerance=0.15)
    keys = [dict(side=s, r=r, c=c, x=x, y=y, label=LEGENDS[s][r][c]) for s, r, c, x, y in key_centres()]
    stack = [('Back (printed; aluminium plate behind the SoC)', BACK), ('Thermal pad', THERMAL),
             ('Module, hanging under the carrier (SoC lid to carrier)', MODULE['soc_top']), ('Carrier board', CARRIER_T),
             ('Parts on the carrier\'s screen side + gap', 0.9 + GAP), ('LCD with touch and cover glass', PANEL['t']),
             ('Front frame, half above the glass', FRONT * 0.5)]
    json.dump(dict(w=W, h=H, t=T, z_keytop=Z_KEYTOP, screen=screen, keys=keys, explode=EXPLODE,
                   stack=stack, side_stack=[('Back', BACK), ('Cell [est]', CELL['t']), ('Gap', GAP), ('Keyboard board', KBD_PCB_T),
                                            ('Switch, nub, flange, cap', SWITCH_H + NUB + FLANGE + CAP_TOP)]),
              open(os.path.join(out, 'stack.json'), 'w'), indent=1)
    print(f'UMPC {W:.1f} x {H:.1f} x {T:.2f} mm; key tops at {Z_KEYTOP:.2f}, screen top {Z_TOP:.2f}')
    for n, t in stack:
        print(f'  {n:55s} {t:.2f}')


if __name__ == '__main__':
    main()
