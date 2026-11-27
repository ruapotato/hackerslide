"""HackerSlide hack pad: parametric model of the whole device (CadQuery).  Every dimension is in this file.

  python hackpad.py [--out DIR]     builds the parts, checks them for collisions closed and open, exports STEP and
                                    STL (one per part, plus per-pose scene files for the renders) and writes the
                                    stack table docs/hack-pad-stack.md.

CONCEPT MODEL, NOT A PRINTABLE CASE YET: shells, slider rails and screw bosses are simplified; there is no board
layout, so the parts under the board are blocks of the right size in plausible places.  What IS real: the heights,
taken from datasheets ([ds]) or marked as estimates ([est]), and therefore the thickness.

Arrangement (David asked for the mechanical design to be locked for the video, 2026-11-26; choices here are
Claude's working assumptions, flagged in docs/decisions/0009-hack-pad.md):
  base  = keyboard half: back cover, NFC coil sheet, battery, low parts, main board (keys on top), key plate
  lid   = display half: thin skin, e-paper panel, a strip board with the panel's drive circuit beside the panel
World frame: X width, Y depth (user edge at Y = 0), Z thickness, bottom of the back cover at Z = 0, screen up.
"""
import argparse
import json
import os
import sys

import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'hardware', 'scripts'))
import hp_layout as HP  # noqa: E402

# ------------------------------------------------------------------------------------------------ dimensions (mm)
BODY_W, BODY_H, CORNER_R = 128.0, 72.0, 6.0     # the Nokia N810's footprint
WALL = 1.5
BOARD = dict(w=124.6, h=68.6, t=1.0, r=4.3)     # main board, 6 layers at 1.0 mm; 0.2 mm clear of the walls
BACK = 1.2                                      # [est] back cover, printed
NFC = 0.3                                       # [est] flex coil plus ferrite sheet on the back cover, under the battery
BATTERY = dict(w=76.5, h=61.5, t=4.5, swell=0.3)  # [ds] GlobTek BL1950P4071611S1PCPT; swell allowance [est]
LOW_PARTS = 1.5                                 # tallest part allowed over the battery: brain BGA about 1.3 [est], memory 1.0 [ds]
PART_CLEAR = 0.2                                # [est] air between those parts and the battery
TALL_PARTS = 2.4                                # tallest part beside the battery: Wi-Fi module 2.4 [ds], jack 2.15 [ds]
SWITCH_H, NUB, FLANGE = 0.6, 0.3, 0.5           # [ds] Alps SKSWCFE010; keycap as on the Linux design
PLATE_T, PLATE_RIM = 0.8, 0.3
PLATE_STANDOFF = SWITCH_H + NUB + FLANGE + 0.1  # key plate above the board
SLIDE_GAP = 0.4                                 # [est]
LID_SKIN = 0.8                                  # [est] lid underside (faces the keys when closed)
PANEL = dict(w=105.33, h=62.37, t=1.98, aa_w=92.8, aa_h=55.68)   # [ds] Good Display GDEY0426T82-FT01C
PANEL_GLUE = 0.2                                # [est]
BEZEL_LIP = 0.4                                 # [est] lid rim above the panel face
LID_BOARD = dict(w=14.0, h=60.0, t=0.5, parts=1.5)   # strip beside the panel, 0.5 mm board; tallest part L1 1.5 [ds]
TRAVEL = 36.0                                   # lid travel: uncovers the key field (to Y = 33.7) with 2 mm to spare
N810 = dict(w=128.0, h=72.0, t=14.0)
LINUX = dict(w=131.5, h=74.0, t=19.35)          # the Linux handheld on branch linux-handheld

Z_NFC = BACK
Z_BATT = Z_NFC + NFC
Z_BATT_TOP = Z_BATT + BATTERY['t'] + BATTERY['swell']
Z_BOARD = Z_BATT_TOP + PART_CLEAR + LOW_PARTS
Z_BOARD_TOP = Z_BOARD + BOARD['t']
Z_PLATE = Z_BOARD_TOP + PLATE_STANDOFF
Z_BASE_TOP = Z_PLATE + PLATE_T + PLATE_RIM
Z_LID = Z_BASE_TOP + SLIDE_GAP
Z_PANEL = Z_LID + LID_SKIN + PANEL_GLUE
Z_TOP = Z_PANEL + PANEL['t'] + BEZEL_LIP
assert Z_BOARD - BACK >= TALL_PARTS + 0.2, 'tall parts beside the battery must clear the back cover'
BX, BY = (BODY_W - BOARD['w']) / 2, (BODY_H - BOARD['h']) / 2      # board corner in the body
BATT_X, BATT_Y = BODY_W - WALL - 1.0 - BATTERY['w'], (BODY_H - BATTERY['h']) / 2   # battery toward the right; tall parts left

STACK = [('Back cover', BACK, 'est'), ('NFC coil and ferrite sheet', NFC, 'est'),
         ('Battery, with swelling allowance', BATTERY['t'] + BATTERY['swell'], 'ds + est'),
         ('Low parts over the battery, with clearance', PART_CLEAR + LOW_PARTS, 'ds + est'),
         ('Main board', BOARD['t'], 'chosen'), ('Switches, keycaps and key plate', PLATE_STANDOFF + PLATE_T + PLATE_RIM, 'ds'),
         ('Slide gap', SLIDE_GAP, 'est'), ('Lid skin and adhesive', LID_SKIN + PANEL_GLUE, 'est'),
         ('E-paper panel with touch and front light', PANEL['t'], 'ds'), ('Rim above the panel', BEZEL_LIP, 'est')]
assert abs(sum(s[1] for s in STACK) - Z_TOP) < 1e-6


def box(x0, y0, z0, x1, y1, z1, r=0.0):
    b = cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))
    r = min(r, (x1 - x0) / 2 - 0.01, (y1 - y0) / 2 - 0.01)
    return b.edges('|Z').fillet(r) if r > 0.05 else b


def base_shell():
    s = box(0, 0, 0, BODY_W, BODY_H, Z_BASE_TOP, CORNER_R)
    s = s.cut(box(WALL, WALL, BACK, BODY_W - WALL, BODY_H - WALL, Z_BASE_TOP + 1, CORNER_R - WALL))
    # openings on the right edge: USB-C, headphone jack, card (positions are placeholders until the layout exists)
    for y, w, z0, h in ((14, 9.4, Z_BOARD - 2.0, 3.4), (34, 6.6, Z_BOARD - 2.6, 4.6), (52, 12.0, Z_BOARD - 1.7, 1.9)):
        s = s.cut(box(BODY_W - WALL - 1, y, z0, BODY_W + 1, y + w, z0 + h))
    return s


def board():
    return box(BX, BY, Z_BOARD, BX + BOARD['w'], BY + BOARD['h'], Z_BOARD_TOP, BOARD['r'])


KEYS_DEPTH = 30.0                               # hp_layout: the key field is 30 mm deep


def key_xy(x, y):
    """hp_layout coordinates (origin at the key field's top left, y down) -> body coordinates.  The keys sit along the
    user edge (Y = 0), so sliding the lid away from the user uncovers them."""
    return BX + (BOARD['w'] - HP.FIELD_W - HP.LEFT_W) / 2 + x, BY + 2.0 + (KEYS_DEPTH - y)


def keycaps():
    caps = None
    for k in HP.keys():
        x, y = key_xy(k['x'], k['y'])
        w, h = k['w'] - HP.CAP_GAP, k['h'] - HP.CAP_GAP
        c = box(x - w / 2, y - h / 2, Z_BOARD_TOP + SWITCH_H + NUB, x + w / 2, y + h / 2, Z_BASE_TOP, 1.0)
        caps = c if caps is None else caps.union(c)
    return caps


def key_plate():
    p = box(WALL + 0.2, WALL + 0.2, Z_PLATE, BODY_W - WALL - 0.2, BODY_H - WALL - 0.2, Z_PLATE + PLATE_T, CORNER_R - WALL)
    for k in HP.keys():
        x, y = key_xy(k['x'], k['y'])
        w, h = k['w'] - HP.CAP_GAP + 0.3, k['h'] - HP.CAP_GAP + 0.3
        p = p.cut(box(x - w / 2, y - h / 2, Z_PLATE - 1, x + w / 2, y + h / 2, Z_PLATE + 2, 1.0))
    return p


def battery():
    return box(BATT_X, BATT_Y, Z_BATT, BATT_X + BATTERY['w'], BATT_Y + BATTERY['h'], Z_BATT + BATTERY['t'], 2.0)


def nfc_coil():
    return box(BATT_X + 8, BATT_Y + 6, Z_NFC, BATT_X + 8 + 50, BATT_Y + 6 + 40, Z_NFC + NFC, 4.0)


# blocks under the board: (name, x, y, w, h, height) with x, y the corner in board coordinates.  Low parts sit over the
# battery (right 77 mm), tall ones in the strip on the left.  PLACEHOLDERS until there is a layout.
PARTS = [('brain', 78, 26, 14, 14, 1.3), ('ram1', 96, 20, 8, 9, 1.0), ('ram2', 96, 33, 8, 9, 1.0), ('flash', 70, 30, 6, 5, 0.8),
         ('fpga', 60, 46, 7, 7, 0.9), ('sdr', 72, 50, 7, 7, 0.9), ('charger', 50, 10, 4, 4, 0.8), ('codec', 108, 8, 4, 4, 0.8),
         ('lora', 90, 52, 4, 4, 0.9), ('subghz', 100, 52, 4, 4, 0.9), ('nfc', 110, 46, 5, 5, 1.0),
         ('wifi', 4, 4, 13.2, 16.6, 2.4), ('gps', 20, 4, 10.1, 9.7, 2.4), ('usb', 30, 60, 9, 7.4, 1.8), ('jack', 6, 56, 7.6, 12.5, 2.15),
         ('card', 20, 48, 11.9, 15, 1.45), ('batt_header', 34, 30, 10, 6, 2.4), ('inductor', 22, 24, 4, 4, 1.8),
         ('sensors', 36, 6, 8, 20, 1.2)]


def board_parts():
    out = None
    for name, x, y, w, h, t in PARTS:
        over_batt = BX + x + w > BATT_X and BY + y + h > BATT_Y and BY + y < BATT_Y + BATTERY['h']
        assert t <= (LOW_PARTS if over_batt else TALL_PARTS) + 1e-6, (name, t)
        b = box(BX + x, BY + y, Z_BOARD - t, BX + x + w, BY + y + h, Z_BOARD, 0.3)
        out = b if out is None else out.union(b)
    return out


def lid_parts(dy=0.0):
    """Lid at slide offset dy (0 = closed, TRAVEL = open)."""
    shell = box(0, 0, Z_LID, BODY_W, BODY_H, Z_TOP, CORNER_R)
    shell = shell.cut(box(WALL, WALL, Z_LID + LID_SKIN, BODY_W - WALL, BODY_H - WALL, Z_TOP - BEZEL_LIP, CORNER_R - WALL))
    px = WALL + 1.5 + LID_BOARD['w'] + 1.0                       # strip board on the left, panel to its right
    py = (BODY_H - PANEL['h']) / 2
    # the top is a frame over the panel border and the strip board, with a window 0.6 mm larger than the active area
    wx, wy = px + (PANEL['w'] - PANEL['aa_w']) / 2 - 0.6, py + (PANEL['h'] - PANEL['aa_h']) / 2 - 0.6
    shell = shell.cut(box(wx, wy, Z_TOP - BEZEL_LIP - 0.1, wx + PANEL['aa_w'] + 1.2, wy + PANEL['aa_h'] + 1.2, Z_TOP + 1, 1.0))
    panel = box(px, py, Z_PANEL, px + PANEL['w'], py + PANEL['h'], Z_PANEL + PANEL['t'], 1.0)
    ax, ay = px + (PANEL['w'] - PANEL['aa_w']) / 2, py + (PANEL['h'] - PANEL['aa_h']) / 2
    screen = box(ax, ay, Z_PANEL + PANEL['t'] - 0.02, ax + PANEL['aa_w'], ay + PANEL['aa_h'], Z_PANEL + PANEL['t'] + 0.01)
    lb = box(WALL + 1.5, (BODY_H - LID_BOARD['h']) / 2, Z_LID + LID_SKIN + 0.1, WALL + 1.5 + LID_BOARD['w'],
             (BODY_H + LID_BOARD['h']) / 2, Z_LID + LID_SKIN + 0.1 + LID_BOARD['t'])
    lp = box(WALL + 4, 20, Z_LID + LID_SKIN + 0.1 + LID_BOARD['t'], WALL + 4 + 3, 23, Z_LID + LID_SKIN + 0.1 + LID_BOARD['t'] + LID_BOARD['parts'])
    assert Z_LID + LID_SKIN + 0.1 + LID_BOARD['t'] + LID_BOARD['parts'] <= Z_TOP - BEZEL_LIP, 'lid board parts hit the lid top'
    return {n: p.translate((0, dy, 0)) for n, p in dict(lid_shell=shell, panel=panel, screen=screen, lid_board=lb, lid_board_parts=lp).items()}


def parts(dy=0.0):
    d = dict(base_shell=base_shell(), nfc_coil=nfc_coil(), battery=battery(), board_parts=board_parts(), board=board(),
             key_plate=key_plate(), keycaps=keycaps())
    d.update(lid_parts(dy))
    return d


def collisions(d, tol=0.01):
    names, bad = list(d), []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if {a, b} == {'panel', 'screen'}:
                continue
            try:
                v = d[a].intersect(d[b]).val().Volume()
            except Exception:
                v = 0.0
            if v > tol:
                bad.append((a, b, round(v, 2)))
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(HERE, '..', 'hackpad'))
    out = ap.parse_args().out
    for sub in ('step', 'scene'):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    closed, opened = parts(0.0), parts(TRAVEL)
    for tag, d in (('closed', closed), ('open', opened)):
        bad = collisions(d)
        print(tag, 'collisions:', bad or 'none')
        assert not bad
        for n, p in d.items():
            cq.exporters.export(p, os.path.join(out, 'scene', f'{tag}_{n}.stl'), tolerance=0.05, angularTolerance=0.2)
    asm = cq.Assembly()
    for n, p in closed.items():
        cq.exporters.export(p, os.path.join(out, 'step', n + '.step'))
        asm.add(p, name=n)
    asm.save(os.path.join(out, 'step', 'assembly_closed.step'))
    rows = ['# Hack pad: thickness stack', '', 'Generated by `mechanical/src/hackpad.py` from the dimensions in that file. A concept model:',
            'heights are from datasheets or marked estimates; the case details and the part positions under the board are not final.', '',
            '| Layer, bottom to top | mm | Source |', '|---|---|---|']
    rows += [f'| {n} | {t:.2f} | {"datasheet" if s == "ds" else "estimate" if s == "est" else "datasheet and estimate" if "+" in s else s} |' for n, t, s in STACK]
    rows += [f'| **Total** | **{Z_TOP:.2f}** | |', '',
             f'Keyboard half {Z_BASE_TOP:.2f} mm, display half {Z_TOP - Z_LID:.2f} mm, gap {SLIDE_GAP:.2f} mm. Footprint {BODY_W:.0f} x {BODY_H:.0f} mm.', '',
             f'For comparison: Nokia N810 {N810["w"]:.0f} x {N810["h"]:.0f} x {N810["t"]:.0f} mm; the Linux handheld design '
             f'{LINUX["w"]} x {LINUX["h"]:.0f} x {LINUX["t"]} mm.', '',
             f'Parts taller than {LOW_PARTS} mm (up to {TALL_PARTS} mm) must sit in the {BATT_X - WALL:.0f} mm strip beside the battery; '
             f'that strip has {Z_BOARD - BACK:.1f} mm of height.', '']
    open(os.path.join(HERE, '..', '..', 'docs', 'hack-pad-stack.md'), 'w').write('\n'.join(rows))
    px, py = WALL + 1.5 + LID_BOARD['w'] + 1.0, (BODY_H - PANEL['h']) / 2
    keys = []
    for k in HP.keys():
        x, y = key_xy(k['x'], k['y'])
        keys.append(dict(name=k['name'], fn=k['fn'], x=x, y=y, w=k['w'] - HP.CAP_GAP, h=k['h'] - HP.CAP_GAP))
    json.dump(dict(total=Z_TOP, base=Z_BASE_TOP, lid=Z_TOP - Z_LID, travel=TRAVEL, body=[BODY_W, BODY_H], z_key_top=Z_BASE_TOP,
                   screen=[px + (PANEL['w'] - PANEL['aa_w']) / 2, py + (PANEL['h'] - PANEL['aa_h']) / 2, Z_PANEL + PANEL['t'],
                           PANEL['aa_w'], PANEL['aa_h']],
                   z=dict(back=BACK, batt=Z_BATT, board=Z_BOARD, plate=Z_PLATE, lid=Z_LID, panel=Z_PANEL, top=Z_TOP),
                   stack=[[n, t, src] for n, t, src in STACK], keys=keys), open(os.path.join(out, 'stack.json'), 'w'), indent=1)
    cut = box(-5, -5, -5, BODY_W * 0.5, BODY_H + 5, Z_TOP + 5)          # section: the left half, cut through the battery
    for n, p in closed.items():
        try:
            sp = p.intersect(cut)
            if sp.val().Volume() > 0.001:
                cq.exporters.export(sp, os.path.join(out, 'scene', f'section_{n}.stl'), tolerance=0.03, angularTolerance=0.15)
        except Exception:
            pass
    print(f'total {Z_TOP:.2f} mm (base {Z_BASE_TOP:.2f}, lid {Z_TOP - Z_LID:.2f})')


if __name__ == '__main__':
    main()
