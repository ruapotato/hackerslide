"""Place (and optionally autoroute) the keyboard PCB.  Usage: keyboard_pcb.py alps|dome BOARD_DIR [--route]

The board is the floor of the keyboard tray and the bottom skin of the device (David, 2026-11-24), so EVERYTHING is
on the top (F) side and the bottom stays bare.  It covers the whole tray: the key area is y = 0..31, and the board
continues to y = -38 under the part of the tray that stays below the body (FPC connector, room for the cable loop).
The top plate sits 1.5 mm above the board on four SMT spacers; parts under it are at most 1.0 mm high, and the
diodes (0.5 mm) sit under the keycap flanges, which ride 0.9 mm above the board.
"""
import os
import sys

import pcbnew

import kbd_layout as KL
from pcbgen import Board, route, set_project_rules

TOP_PLATE_HOLES = KL.PLATE_HOLES

RULES = {'min_clearance': 0.127, 'min_track_width': 0.127, 'min_via_diameter': 0.45, 'min_through_hole_diameter': 0.2,
         'min_copper_edge_clearance': 0.3, 'min_hole_clearance': 0.2, 'min_hole_to_hole': 0.25,
         'min_via_annular_width': 0.1}
CLASSES = [{'name': 'Default', 'clearance': 0.15, 'track_width': 0.15, 'via_diameter': 0.45, 'via_drill': 0.2},
           {'name': 'Power', 'clearance': 0.15, 'track_width': 0.3, 'via_diameter': 0.5, 'via_drill': 0.25}]
PATTERNS = [('+3V3', 'Power'), ('GND', 'Power')]


U1_XY = (11.5, -13.0)
TRACK, VIA_D, VIA_DRILL = 0.2, 0.45, 0.2


def route_matrix(B, variant):
    """Deterministic routing of the regular part of the key matrix (Alps variant).  What it draws:

      F  key node: switch pad 2 -> its diode                 F  ROW0-3: one track 3.0 mm below each key row, then up
      B  COL0-9: a vertical per physical column, then a      F  folded columns 10/11: two tracks above each key row
         bus above the key area (one level per column)          bring COL0-3 / COL4-7 across to them; ROW4 on B
    The buses stop near U1; the scanner fan-out, the D-pad and the cable signals are left to the autorouter or a human.
    """
    MM = pcbnew.FromMM
    nets = B.nets

    def pad(ref, num):
        p = [q for q in B.fps[ref].Pads() if q.GetNumber() == num][0]
        return pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y), p.GetNetname()

    def track(net, pts, layer=pcbnew.F_Cu):
        for a, b in zip(pts, pts[1:]):
            if a == b:
                continue
            t = pcbnew.PCB_TRACK(B.b)
            t.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1]))); t.SetEnd(pcbnew.VECTOR2I(MM(b[0]), MM(b[1])))
            t.SetWidth(MM(TRACK)); t.SetLayer(layer); t.SetNet(nets[net])
            B.b.Add(t)

    def via(net, x, y):
        v = pcbnew.PCB_VIA(B.b)
        v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        v.SetWidth(pcbnew.F_Cu, MM(VIA_D))
        v.SetDrill(MM(VIA_DRILL)); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(nets[net])
        B.b.Add(v)

    Bcu = pcbnew.B_Cu
    keys = list(enumerate(KL.keys(variant)))
    rowy = {r: KL.key_center(r, 0)[1] for r in range(KL.ROWS)}
    colx = {c: KL.key_center(0, c)[0] for c in range(KL.COLS)}
    xv = {c: colx[c] - 2.7 for c in range(10)}                 # column verticals on B
    lvl = {c: -0.8 - 0.5 * c for c in range(10)}               # bus level per column, rising to the right
    lvl_row4 = -0.8 - 0.5 * 10
    x_bus_end = 21.5                                           # each bus ends in a via, staggered 0.9 mm, left of the risers
    rowx = {0: 23.7, 1: 23.3, 2: 22.9, 3: 22.5}                # ROW0-3 risers on F, left of column 0
    done = set()
    for i, (name, r, c, x, y) in keys:
        if r == 4:
            continue                                            # D-pad: local, not scripted
        sw = f'SW{i + 1}'
        p1x, p1y, coln = pad(sw, '1')
        p2x, p2y, kn = pad(sw, '2')
        dref = f'D{i + 1}'
        if dref not in B.fps:                                   # second Space switch: parallel to the first one
            first = [j for j, k in keys if k[0] == 'Space'][0]
            f1x, f1y, _ = pad(f'SW{first + 1}', '1')
            f2x, f2y, _ = pad(f'SW{first + 1}', '2')
            track(coln, [(f1x, f1y), (f1x, y - 1.4), (p1x, y - 1.4), (p1x, p1y)])
            track(kn, [(f2x, f2y), (f2x, y + 1.35), (p2x, y + 1.35), (p2x, p2y)])
            continue
        dkx, dky, _ = pad(dref, '1')
        drx, dry, rown = pad(dref, '2')
        track(kn, [(p2x, p2y), (p2x, dky), (dkx, dky)])
        if c < 10:
            # row track below the key row; column via beside the switch
            track(rown, [(drx, dry), (drx, y + 3.0)])
            done.add(('row', r))
            track(coln, [(p1x, p1y), (xv[c], y)])
            via(coln, xv[c], y)
        else:
            # folded column: its "column" net comes across on F above the row; its diode goes to ROW4 on B
            src = int(coln[3:])
            yh = y - (2.0 if c == 10 else 2.7)
            via(coln, xv[src], yh)
            track(coln, [(xv[src], yh), (p1x, yh), (p1x, p1y)])
            xr = x - 1.25
            track(rown, [(drx, dry), (xr, dry)])
            via(rown, xr, dry)
    # ROW0-3 on F: along the row, up the riser, to y = -1.2
    for r in range(4):
        y = rowy[r] + 3.0
        x_right = pad([f'D{i + 1}' for i, k in keys if k[1] == r and k[2] == 9][0], '2')[0]
        track(f'ROW{r}', [(x_right, y), (rowx[r], y), (rowx[r], -1.2)])
    # COL0-9 on B: vertical through all four rows, then the bus toward U1
    for c in range(10):
        track(f'COL{c}', [(xv[c], rowy[3]), (xv[c], lvl[c]), (x_bus_end - 0.9 * c, lvl[c])], Bcu)
        via(f'COL{c}', x_bus_end - 0.9 * c, lvl[c])
    # ROW4 on B: one vertical per folded column, joined above the key area, then the bus
    xa, xb = colx[10] - 1.25, colx[11] - 1.25
    track('ROW4', [(xa, rowy[3] + 2.1), (xa, lvl_row4)], Bcu)
    track('ROW4', [(xb, rowy[3] + 2.1), (xb, lvl_row4), (x_bus_end - 0.9 * 10, lvl_row4)], Bcu)
    via('ROW4', x_bus_end - 0.9 * 10, lvl_row4)


def build(variant, bdir, do_route=False):
    name = 'keyboard' if variant == 'alps' else 'keyboard-5135'
    top = -KL.BOARD_TOP_EXT
    B = Board(os.path.join(bdir, 'netlist.json'), layers=2, thickness=KL.PCB_T)
    B.outline(0, top, KL.BOARD_W, KL.BOARD_H, r=1.5)
    B.region = (0.4, top + 0.4, KL.BOARD_W - 0.4, KL.BOARD_H - 0.4)
    keepout = [(x - 2.6, y - 2.6, x + 2.6, y + 2.6) for (x, y) in TOP_PLATE_HOLES]
    for i, (x, y) in enumerate(TOP_PLATE_HOLES):
        B.place(f'H{i + 1}', x, y, 0, 'F')
    # keycap flanges ride 0.9 mm above the board: only the 0.5 mm diodes may sit under them
    c = KL.CAP
    flanges = []
    for i, (kname, r, col, x, y) in enumerate(KL.keys(variant)):
        B.place(f'SW{i + 1}', x, y, 0, 'F')
        B.text(kname, x, y - (2.6 if variant == 'alps' else 0), pcbnew.F_Fab, 0.8)
        hw, hh = (2.8, 2.8) if r == 4 else (c['flange_w'] / 2, c['flange_h'] / 2)
        flanges.append((x - hw - 0.2, y - hh - 0.2, x + hw + 0.2, y + hh + 0.2))
    # one diode per matrix position
    if variant == 'alps':            # next to its switch and under the same keycap
        for i, (kname, r, col, x, y) in enumerate(KL.keys(variant)):
            if f'D{i + 1}' in B.fps:
                if r < 4:            # rot 180: pad 1 (key node) toward +x, next to the switch's key-node pad
                    B.place(f'D{i + 1}', x, y + 2.1, 180, 'F')
                else:
                    B.pack([f'D{i + 1}'], x, y + 2.1, 'F', rot=0, keepout=keepout, region=(x - 3.6, y - 3.2, x + 3.6, y + 3.2))
    else:                            # domes cover their whole cell: diodes stand in the 1.5 mm gaps between columns
        dpad_spots = [(-5.6, -5.6), (5.6, -5.6), (-5.6, 5.6), (5.6, 5.6), (9.0, 5.6)]
        for i, (kname, r, col, x, y) in enumerate(KL.keys(variant)):
            if f'D{i + 1}' not in B.fps:
                continue
            if r == 4:
                dx, dy = dpad_spots[col]
                B.place(f'D{i + 1}', KL.DPAD_C[0] + dx, KL.DPAD_C[1] + dy, 0, 'F')
            elif col == KL.COLS - 1:     # last column has no gap to its right: share the gap on its left
                B.place(f'D{i + 1}', x - KL.PITCH_X / 2, y + 1.1, 90, 'F')
            else:
                B.place(f'D{i + 1}', x + KL.PITCH_X / 2, y - (1.1 if col == KL.COLS - 2 else 0.0), 90, 'F')
    # FPC connector above the key area, opening toward the top of the tray, straight below carrier J9; ESD clamp at it
    jx, jy = KL.J1_XY
    B.place('J1', jx, jy, 180, 'F')
    if variant == 'alps':
        B.place('U2', jx - 9.0, jy - 2.0, 90, 'F')     # beside J1, clear of its pins, so both can fan out
    else:                            # a dome foot is in the way below J1
        B.place('U2', jx + 6.0, jy - 1.0, 90, 'F')
    # spring-pin landing pads: device x 105..120, under the carrier bottom strip when open (tray y 19..33)
    for i in range(6):
        B.place(f'LP{i + 1}', 104.0 + 3.0 * i, -13.5, 0, 'F')
    # scanner and its passives: D-pad zone corners, clear of the D-pad keycaps and of the spacers
    ko = keepout + flanges
    B.place('U1', *U1_XY, 0, 'F')      # above the key area, where the row and column buses arrive
    if variant == 'dome':            # the dome footprint has no courtyard: keep parts out of every dome's 8.4 mm box
        ko = keepout + [(x - 4.3, y - 4.3, x + 4.3, y + 4.3) for (_n, _r, _c, x, y) in KL.keys(variant)]
        B.pack(['C1', 'C2', 'R3', 'R4', 'R1', 'R2', 'TP1', 'TP2', 'TP3', 'TP4'], 11.5, -9.0, 'F', keepout=ko,
               region=(0.6, -14.0, 22.4, 30.4))
    else:
        # passives stay 3 mm clear of U1 so its fan-out vias are not boxed in
        B.pack(['C1', 'C2', 'R3', 'R4', 'R1', 'R2', 'TP1', 'TP2', 'TP3', 'TP4'], U1_XY[0], U1_XY[1] - 8.0, 'F', keepout=ko,
               region=(0.6, -30.0, 30.0, -19.3))
        route_matrix(B, variant)
        for ref in ('U1', 'J1', 'U2'):          # escape stubs and vias for the fine-pitch parts
            B.fanout(ref, lengths=(1.2, 2.2, 3.2) if ref == 'U1' else (1.2, 2.2))
    left = B.unplaced()
    assert not left, left
    B.text('HackerSlide 810 keyboard ' + ('Alps SKSW' if variant == 'alps' else 'Keystone 5135 domes') + ' rev 0.1 DRAFT  CERN-OHL-S-2.0',
           KL.BOARD_W / 2, -20.0, pcbnew.F_SilkS, 1.0)
    pts = [(0, top), (KL.BOARD_W, top), (KL.BOARD_W, KL.BOARD_H), (0, KL.BOARD_H)]
    if not do_route:
        B.zone('GND', pcbnew.B_Cu, pts, clearance=0.2)        # GND pour on both layers
        B.zone('GND', pcbnew.F_Cu, pts, clearance=0.2)
    path = B.save(os.path.join(bdir, name + '.kicad_pcb'))
    set_project_rules(path.replace('.kicad_pcb', '.kicad_pro'), RULES, CLASSES, PATTERNS)
    # The Wuerth WA-SMSI footprint is a solder ring around its own non-plated hole: not a clearance fault.
    open(path.replace('.kicad_pcb', '.kicad_dru'), 'w').write(
        '(version 1)\n(rule "wuerth_spacer_ring"\n  (condition "A.memberOfFootprint(\'H?\') && B.memberOfFootprint(\'H?\')")\n'
        '  (constraint hole_clearance (min 0mm)))\n')
    if do_route:
        # The scripted matrix and fan-outs are in; gridroute.py finishes the rest.  Ground is routed as ordinary
        # tracks first (on two layers the pours get cut into pieces by the signals), and the pours go on last.
        import subprocess
        gr = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gridroute.sh')
        for extra in (['--width', '0.2'], ['--width', '0.15'], ['--width', '0.13', '--clearance', '0.17']):
            subprocess.run([gr, os.path.abspath(bdir), name, '--pour', '', '--power-width', '0.2'] + extra, check=True)
        b = pcbnew.LoadBoard(path)
        for layer in (pcbnew.B_Cu, pcbnew.F_Cu):
            z = pcbnew.ZONE(b)
            z.SetLayer(layer); z.SetNet(b.FindNet('GND'))
            ol = z.Outline(); ol.NewOutline()
            for (x, y) in pts:
                ol.Append(pcbnew.FromMM(x), pcbnew.FromMM(y))
            z.SetLocalClearance(pcbnew.FromMM(0.2)); z.SetMinThickness(pcbnew.FromMM(0.2))
            z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
            z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
            b.Add(z)
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        pcbnew.SaveBoard(path, b)
        # saving from this process rewrites the project file with defaults: put the rules back
        set_project_rules(path.replace('.kicad_pcb', '.kicad_pro'), RULES, CLASSES, PATTERNS)
    return path


if __name__ == '__main__':
    print(build(sys.argv[1], sys.argv[2], '--route' in sys.argv))
