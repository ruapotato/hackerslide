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
PANEL = dict(w=98.10, h=58.26, t=4.25, aa_w=86.40, aa_h=51.84)
MODULE = dict(w=55.0, h=40.0, mated=4.50, soc_top=3.60)      # LuckFox Core3566 (measured, see above)
CARRIER_T = 1.0
KEY = dict(pitch_x=7.0, pitch_y=7.0, cap_w=6.3, cap_h=6.2, cols=5, rows=4)
SWITCH_H, NUB, FLANGE, CAP_TOP = 0.6, 0.3, 0.5, 1.2           # as the keyboards of the earlier designs
KBD_PCB_T = 0.8
CELL = dict(w=32.0, h=52.0, t=5.0, inset=7.0)                # [est] one flat cell per side, about 1,100-1,300 mAh each
BACK, WALL, FRONT = 1.2, 1.6, 0.8                            # [est] printed back; front frame over the screen border
THERMAL_MIN = 0.5                                            # [est] thinnest pad from the SoC lid to an aluminium plate in the back
GAP = 0.3
HALF_W = KEY['cols'] * KEY['pitch_x'] + 4.0                  # keyboard half including its margin
W = PANEL['w'] + 2 * HALF_W + 2 * WALL + 2.0
H = PANEL['h'] + 2 * WALL + 6.0
END_R = 14.0                                                 # rounded grips at the two ends

# Z stack, centre (screen over the module) and sides (keys over the cells)
# carrier bottom face; the module hangs under it.  Its tallest part (an inductor, 4.50 below the carrier) needs 0.2 mm
# above the back; the SoC lid (3.60 below) then gets a thicker pad.
Z_CARRIER = BACK + max(THERMAL_MIN + MODULE['soc_top'], MODULE['mated'] + 0.2)
THERMAL = Z_CARRIER - MODULE['soc_top'] - BACK
Z_CARRIER_TOP = Z_CARRIER + CARRIER_T
Z_PANEL = Z_CARRIER_TOP + 0.9 + GAP                          # 0.9 [est]: tallest part on the carrier's screen side
Z_FRONT = Z_PANEL + PANEL['t']                               # the front frame sits on the panel border
Z_TOP = Z_FRONT + FRONT * 0.5
Z_CELL = BACK
Z_KBD = max(Z_CELL + CELL['t'] + GAP, Z_TOP - (KBD_PCB_T + SWITCH_H + NUB + FLANGE + CAP_TOP))
Z_KEYTOP = Z_KBD + KBD_PCB_T + SWITCH_H + NUB + FLANGE + CAP_TOP
T = max(Z_TOP, Z_KEYTOP)
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
                out.append((side, r, c, x0 + (c + 0.5) * KEY['pitch_x'], CY + (1.5 - r) * KEY['pitch_y'] - 2.0))
    return out


LEGENDS = {'L': [['Q', 'W', 'E', 'R', 'T'], ['A', 'S', 'D', 'F', 'G'], ['Z', 'X', 'C', 'V', 'B'], ['Esc', 'Tab', 'Fn', 'Shift', 'Spc']],
           'R': [['Y', 'U', 'I', 'O', 'P'], ['H', 'J', 'K', 'L', 'Del'], ['N', 'M', ',', '.', 'Ent'], ['Spc', 'Alt', 'Ctrl', 'Sym', 'Shift']]}


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
    jx, jy = W - WALL - 3.0 - KEY['cols'] * KEY['pitch_x'] / 2, CY + 2.5 * KEY['pitch_y'] + 1.5     # mini joystick above the right keys
    stick = cq.Workplane('XY').circle(2.2).extrude(1.6).translate((jx, jy, T - 0.4))
    front = front.cut(cq.Workplane('XY').circle(3.0).extrude(3).translate((jx, jy, T - FRONT - 1)))
    kbd = None
    for x0 in (WALL + 1.0, W - WALL - 1.0 - (HALF_W - 1.0)):
        b = rbox(x0, WALL + 2, Z_KBD, x0 + HALF_W - 1.0, H - WALL - 2, Z_KBD + KBD_PCB_T, END_R - WALL - 1.0)
        kbd = b if kbd is None else kbd.union(b)
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
