"""HackerSlide watch: concept model (CadQuery).  python watch.py [--out DIR]

CONCEPT ONLY: a case around real panel dimensions to see the size.  Panel: Good Display GDEY0154D67 (1.54", 200 x
200; data sheet rev 1.2: outline 31.80 x 37.32 x 1.0 mm, active 27.0 x 27.0 mm); the touch version (-T03) is
thicker by an amount not yet read, allowed for here.  Everything else is an estimate ([est]).
X width, Y height (12 o'clock up), Z thickness (back of the case at Z = 0).
"""
import argparse
import json
import os

import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
PANEL = dict(w=31.80, h=37.32, t=1.0 + 0.6, aa=27.0, aa_dy=2.5)   # +0.6 [est] touch layer; active area sits 2.5 mm toward 12 o'clock [est]
WALL, GLASS, BEZEL = 1.3, 0.7, 0.3          # [est]
BACK, BATT_T, BOARD_T, PARTS = 1.0, 3.8, 0.8, 1.0   # [est] 200 mAh class cell 3.8 x 25 x 30 mm; nRF5340 aQFN 0.85 mm
GAP = 0.2
W = PANEL['w'] + 2 * WALL + 1.0
H = PANEL['h'] + 2 * WALL + 1.0
R = 6.0
Z_BATT = BACK
Z_PARTS = Z_BATT + BATT_T + GAP
Z_BOARD = Z_PARTS + PARTS
Z_PANEL = Z_BOARD + BOARD_T + GAP
Z_GLASS = Z_PANEL + PANEL['t']
T = Z_GLASS + GLASS + BEZEL
STACK = [('Back', BACK), ('Battery, 200 mAh class', BATT_T), ('Clearance', GAP), ('Parts under the board', PARTS),
         ('Board', BOARD_T), ('Clearance', GAP), ('E-paper with touch', PANEL['t']), ('Cover glass', GLASS), ('Bezel lip', BEZEL)]


def rbox(x0, y0, z0, x1, y1, z1, r):
    b = cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))
    return b.edges('|Z').fillet(min(r, (x1 - x0) / 2 - 0.01, (y1 - y0) / 2 - 0.01))


def parts():
    case = rbox(0, 0, 0, W, H, T, R).edges('>Z').fillet(0.8)
    case = case.cut(rbox(WALL, WALL, BACK, W - WALL, H - WALL, T + 1, R - WALL))
    ax, ay = (W - PANEL['aa']) / 2 - 0.5, (H - PANEL['aa']) / 2 + PANEL['aa_dy'] - 0.5
    bezel = rbox(WALL, WALL, T - BEZEL, W - WALL, H - WALL, T, R - WALL).cut(rbox(ax, ay, T - BEZEL - 1, ax + PANEL['aa'] + 1, ay + PANEL['aa'] + 1, T + 1, 1.0))
    for i, y in enumerate((H * 0.3, H * 0.5, H * 0.7)):                       # three buttons on the right
        case = case.union(rbox(W - 0.2, y - 2.5, T * 0.35, W + 1.2, y + 2.5, T * 0.35 + 2.4, 0.6))
    for y0, y1 in ((-7, 0), (H, H + 7)):                                      # strap lugs
        lug = rbox(W / 2 - 11, y0, 1.5, W / 2 + 11, y1, T - 2.0, 2.0)
        case = case.union(lug.cut(rbox(W / 2 - 9.5, y0 - 1, 0, W / 2 + 9.5, y1 + 1, T, 0.5)))
    px, py = (W - PANEL['w']) / 2, (H - PANEL['h']) / 2
    panel = rbox(px, py, Z_PANEL, px + PANEL['w'], py + PANEL['h'], Z_PANEL + PANEL['t'], 0.5)
    glass = rbox(WALL + 0.1, WALL + 0.1, Z_GLASS, W - WALL - 0.1, H - WALL - 0.1, Z_GLASS + GLASS, R - WALL - 0.1)
    board = rbox(WALL + 0.3, WALL + 0.3, Z_BOARD, W - WALL - 0.3, H - WALL - 0.3, Z_BOARD + BOARD_T, R - WALL - 0.3)
    batt = rbox(W / 2 - 12.5, H / 2 - 15, Z_BATT, W / 2 + 12.5, H / 2 + 15, Z_BATT + BATT_T, 1.5)
    chips = rbox(W / 2 - 6, H / 2 - 6, Z_PARTS, W / 2 + 1, H / 2 + 1, Z_BOARD, 0.3).union(rbox(W / 2 + 3, H / 2 - 9, Z_PARTS, W / 2 + 9, H / 2 - 4, Z_BOARD, 0.3))
    strap = rbox(W / 2 - 9.4, -60, 2.0, W / 2 + 9.4, -4, 4.0, 1.0).union(rbox(W / 2 - 9.4, H + 4, 2.0, W / 2 + 9.4, H + 60, 4.0, 1.0))
    screen = (ax + 0.5, ay + 0.5, Z_PANEL + PANEL['t'], PANEL['aa'], PANEL['aa'])
    return dict(case=case, bezel=bezel, panel=panel, glass=glass, board=board, battery=batt, chips=chips, strap=strap), screen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(HERE, '..', 'watch'))
    out = ap.parse_args().out
    os.makedirs(os.path.join(out, 'scene'), exist_ok=True)
    d, screen = parts()
    for n, p in d.items():
        cq.exporters.export(p, os.path.join(out, 'scene', f'closed_{n}.stl'), tolerance=0.02, angularTolerance=0.1)
    json.dump(dict(w=W, h=H, t=T, screen=screen, stack=STACK), open(os.path.join(out, 'stack.json'), 'w'), indent=1)
    print(f'watch case {W:.1f} x {H:.1f} x {T:.2f} mm (without lugs and buttons)')
    for n, t in STACK:
        print(f'  {n:28s} {t:.2f}')


if __name__ == '__main__':
    main()
