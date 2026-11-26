"""Heights of the carrier's parts, at their real positions, against the room the enclosure model gives them.

  python3 fit_check.py [BOARD.kicad_pcb]        (system python: pcbnew; reads mechanical/src/config.py)

Three rules, each a row of the table it prints:
  module side   every part fits in the cavity between the board and the back shell
  under module  nothing but the two sockets and the four spacers stands under the module (0.4 mm of air there),
                and nothing stands where the battery plug lies
  display side  every part fits behind the panel: under the folded display tail's component strip (config
                TAIL_ZONE_KICAD) with that strip's 1.7 mm on top, elsewhere with a flat tail (0.3 mm) on top
Heights are datasheet maxima by package; a package missing from the table is an error, not a pass.
"""
import os
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '../../mechanical/src'))
import config as cfg          # noqa: E402
import carrier_pcb as cp      # noqa: E402

# footprint name fragment -> maximum height above the board, mm
HEIGHT = [('C_0402', 0.55), ('C_0603', 0.9), ('C_0805', 1.45), ('R_0402', 0.4), ('D_SOD-123F', 1.1), ('D_SOD-323', 1.1),
          ('D_SOD-882', 0.5), ('DF40C', 1.5), ('FH34SRJ', 1.0), ('JST_SH', 2.95), ('PJ-342', 5.0), ('MWSA0402S', 2.0),
          ('SWPA4030S', 3.0), ('Molex_SPOX_5268', cfg.BATT_CONN_H), ('LED_0603', 0.8), ('SOT-23-6', 1.45), ('SOT-23', 1.12),
          ('SOT-353', 1.1), ('EVQP7C', 1.6), ('TDFN-8', 0.8), ('RTW_WQFN', 0.8), ('PVSON', 1.0), ('HRO_TYPE-C', 3.26),
          ('USON-10', 0.55), ('VQFN-32', 0.9), ('WSON-8', 0.8), ('microSD', 1.45), ('WA-SMSI', 1.5), ('TestPoint', 0.0),
          ('MountingHole', 0.0)]
T = pcbnew.ToMM


def height(fp):
    name = fp.GetFPID().GetUniStringLibItemName()
    for k, h in HEIGHT:
        if k in name:
            return h
    raise KeyError(name)


def main(path):
    b = pcbnew.LoadBoard(path)
    cavity = cfg.CAVITY
    zx0, zy0, zx1, zy1 = cfg.TAIL_ZONE_KICAD
    under_strip, elsewhere = cfg.PANEL_GAP - cfg.PANEL['tail_bulge'], cfg.PANEL_GAP - cfg.TAIL_FLAT
    mx0, my0, mx1, my1 = cp.MODULE
    px0, py0, px1, py1 = cp.PLUG
    tall_f, tall_b, under, plug = [], [], [], []
    top_f = top_b = top_s = ('', 0.0)
    for f in b.GetFootprints():
        ref, h = f.GetReference(), height(f)
        x, y = T(f.GetPosition().x), T(f.GetPosition().y)
        if f.IsFlipped():
            bb = f.GetBoundingBox(False, False)
            in_strip = T(bb.GetRight()) > zx0 and T(bb.GetLeft()) < zx1 and T(bb.GetBottom()) > zy0 and T(bb.GetTop()) < zy1
            if in_strip:
                top_s = max(top_s, (ref, h), key=lambda t: t[1])
            top_b = max(top_b, (ref, h), key=lambda t: t[1])
            if h > (under_strip if in_strip else elsewhere) + 1e-9:
                tall_b.append(ref)
            continue
        top_f = max(top_f, (ref, h), key=lambda t: t[1])
        if h > cavity:
            tall_f.append(ref)
        if h > 0 and mx0 < x < mx1 and my0 < y < my1 and not ref.startswith(('J1', 'H')):
            under.append(ref)
        if h > 0 and px0 < x < px1 and py0 < y < py1 and ref != 'J10':
            plug.append(ref)
    rows = [('module side', f'tallest {top_f[0]} {top_f[1]:.2f} mm in a {cavity:.2f} mm cavity', tall_f),
            ('under the module', 'parts other than the sockets and spacers', under),
            ('battery plug', f'parts in x {px0}-{px1}, y {py0}-{py1}', plug),
            ('display side', f'under the display tail\'s parts: tallest {top_s[0]} {top_s[1]:.2f} mm, {under_strip:.2f} mm free; '
                             f'elsewhere: tallest {top_b[0]} {top_b[1]:.2f} mm, {elsewhere:.2f} mm free '
                             f'({cfg.PANEL_GAP:.2f} mm gap)', tall_b)]
    print('| Rule | Found | Verdict |')
    print('|---|---|---|')
    for name, what, bad in rows:
        print(f'| {name} | {what} | {"ok" if not bad else "**" + " ".join(sorted(bad)) + "**"} |')
    sys.exit(1 if any(r[2] for r in rows) else 0)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '../carrier/carrier.kicad_pcb'))
