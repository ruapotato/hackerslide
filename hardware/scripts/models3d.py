"""3D models for the footprints that KiCad's library gives none for, drawn from datasheet envelope dimensions.

  VENV/bin/python models3d.py [OUT_DIR]      (CadQuery; default OUT_DIR: ../lib/hackerslide.3dshapes)

These are for pictures and for checking heights by eye: bodies, shells and contact rows, not the makers' CAD.
Everything is our own geometry (same licence as the rest of the hardware), so nothing here is copied from a vendor
model.  Coordinates are the footprint's own, with y turned over (KiCad footprints have y down, models y up) and
z = 0 on the board surface.  attach_models.py points the board footprints at these files.
"""
import os
import sys

import cadquery as cq

METAL = cq.Color(0.78, 0.78, 0.80)
GOLD = cq.Color(0.85, 0.68, 0.25)
BLACK = cq.Color(0.07, 0.07, 0.08)
DARK = cq.Color(0.16, 0.16, 0.17)
CREAM = cq.Color(0.90, 0.87, 0.78)
WHITE = cq.Color(0.93, 0.93, 0.90)
TIN = cq.Color(0.70, 0.70, 0.68)


def box(x0, y0, z0, x1, y1, z1):
    """Box in footprint coordinates (y down), turned into model coordinates."""
    return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, -y1, z0))


def union(solids):
    u = solids[0]
    for s in solids[1:]:
        u = u.union(s)
    return u


def qfn(size, h, n_side, pitch, pad_w, two_sided=False):
    """Leadless package: body, pin-1 dot, terminal faces on the edges."""
    def build():
        hs = size / 2
        body = box(-hs, -hs, 0.02, hs, hs, h).edges('|Z').chamfer(0.08)
        body = body.cut(cq.Workplane('XY').circle(0.18).extrude(0.05).translate((-hs + 0.45, hs - 0.45, h - 0.03)))
        pins = []
        for k in range(n_side):
            c = (k - (n_side - 1) / 2) * pitch
            sides = ((c, -hs), (c, hs)) if two_sided else ((c, -hs), (c, hs), (-hs, c), (hs, c))
            for (x, y) in sides:
                w, d = (pad_w, 0.12) if abs(y) == hs and abs(x) != hs or two_sided else (0.12, pad_w)
                if not two_sided and abs(x) == hs:
                    w, d = 0.12, pad_w
                pins.append(box(x - w / 2, y - d / 2, 0.0, x + w / 2, y + d / 2, 0.2))
        return [(body, DARK), (union(pins), TIN)]
    return build


def usb_c():
    # HRO TYPE-C-31-M-12: shell 8.94 wide, 3.26 high, 7.35 deep; mouth toward +y of the footprint
    w, h, y0, y1, t = 8.94, 3.26, -3.7, 3.7, 0.28
    def stadium(ww, hh):
        return cq.Workplane('XZ').slot2D(ww, hh).extrude(-(y1 - y0)).translate((0, -y1, h / 2))
    shell = stadium(w, h).cut(stadium(w - 2 * t, h - 2 * t).translate((0, -0.6, 0))
                              .intersect(box(-9, y0 + 0.6, -1, 9, y1 + 1, 9)))
    tongue = box(-3.35, y0 + 0.5, h / 2 - 0.35, 3.35, y1 - 0.9, h / 2 + 0.35)
    pads = union([box(-3.0 + 0.5 * k, y0 + 1.6, h / 2 + 0.35, -2.75 + 0.5 * k, y1 - 1.2, h / 2 + 0.40) for k in range(12)])
    legs = union([box(x - 0.3, y - 0.6, -0.6, x + 0.3, y + 0.6, 0.6) for x in (-4.32, 4.32) for y in (-3.13, 1.05)])
    return [(shell.union(legs), METAL), (tongue, BLACK), (pads, GOLD)]


def microsd():
    # Molex 104031-0811: 1.45 high push-push socket; card enters from -y
    shell = box(-6.0, -5.9, 0.05, 6.0, 5.75, 1.45)
    shell = shell.cut(box(-5.6, -6.5, 0.35, 5.2, 4.9, 1.20))                 # card cavity, open at the mouth
    shell = shell.cut(box(-4.2, -3.5, 1.0, -1.0, 2.0, 2.0)).cut(box(0.6, -3.5, 1.0, 3.8, 2.0, 2.0))   # windows in the lid
    floor = box(-5.6, -5.4, 0.0, 5.2, 4.9, 0.35)
    pins = union([box(-3.1 + 1.1 * k - 0.3, 3.2, 0.35, -3.1 + 1.1 * k + 0.3, 4.6, 0.5) for k in range(8)])
    return [(shell, METAL), (floor, BLACK), (pins, GOLD)]


def jst_sh(n=3):
    # JST SM0xB-SRSS-TB side entry: 2.95 high, mouth toward +y
    hw = (n - 1) / 2 + 1.55
    body = box(-hw, -1.3, 0.0, hw, 2.62, 2.95)
    body = body.cut(box(-hw + 0.5, -0.4, 0.5, hw - 0.5, 3.0, 2.45))
    pins = union([box(k - (n - 1) / 2 - 0.1, -2.6, 0.0, k - (n - 1) / 2 + 0.1, 1.8, 0.2).union(
        box(k - (n - 1) / 2 - 0.1, -1.0, 1.3, k - (n - 1) / 2 + 0.1, 2.2, 1.5)) for k in range(n)])
    tabs = union([box(s * (hw + 0.05) - 0.4, 1.0, 0.0, s * (hw + 0.05) + 0.4, 2.7, 0.25) for s in (-1, 1)])
    return [(body, CREAM), (pins.union(tabs), TIN)]


def molex_5268():
    # Molex 5268-03A right-angle header: shroud 10 x 8 x 4.9, the plug enters from +y
    body = box(-2.5, -1.35, 0.0, 7.5, 6.65, 4.9)
    body = body.cut(box(-1.9, 0.6, 0.7, 6.9, 7.0, 4.3)).cut(box(-0.8, 3.0, 4.2, 5.8, 7.0, 5.0))    # cavity + latch slot
    pins = union([box(2.5 * k - 0.32, 0.2, 2.3, 2.5 * k + 0.32, 5.6, 2.94).union(
        cq.Workplane('XY').rect(0.64, 0.64).extrude(-3.2).translate((2.5 * k, 0, 2.4))) for k in range(3)])
    return [(body, WHITE), (pins, TIN)]


def evqp7():
    # Panasonic EVQ-P7C side-push switch: 3.5 x 2.9 x 1.35, plunger toward +y
    body = box(-1.75, -1.5, 0.0, 1.75, 1.4, 1.35)
    cover = box(-1.75, -1.5, 1.2, 1.75, 1.4, 1.37)
    plunger = box(-0.9, 1.4, 0.3, 0.9, 2.15, 1.1).edges('|Z').fillet(0.2)
    legs = union([box(sx * 2.2 - 0.3, sy * 0.72 - 0.35, 0.0, sx * 2.2 + 0.3, sy * 0.72 + 0.35, 0.3)
                  for sx in (-1, 1) for sy in (-1, 1)])
    return [(body, BLACK), (cover.union(legs), METAL), (plunger, DARK)]


def spacer(od=5.2, thread=2.5, h=1.5):
    def build():
        s = cq.Workplane('XY').circle(od / 2).circle(thread / 2).extrude(h)
        return [(s, TIN)]
    return build


def df40_100():
    # Hirose DF40C-100DS-0.4V receptacle: 22.7 x 3.48, 1.47 high, 2 x 50 contacts
    hy, hx, h = 11.35, 1.74, 1.47
    body = box(-hx, -hy, 0.0, hx, hy, h).cut(box(-0.95, -10.3, 0.35, 0.95, 10.3, h + 0.1))
    ridge = box(-0.28, -10.1, 0.3, 0.28, 10.1, h - 0.2)
    con = []
    for k in range(50):
        y = -9.8 + 0.4 * k
        for s in (-1, 1):
            con.append(box(s * 1.95 - 0.25, y - 0.09, 0.0, s * 1.95 + 0.25, y + 0.09, 0.15))
    inner = union([box(s * 0.62 - 0.33, -9.9, 0.4, s * 0.62 + 0.33, 9.9, h - 0.25) for s in (-1, 1)])
    ends = union([box(-hx - 0.1, s * (hy - 0.5) - 0.5, 0.0, hx + 0.1, s * (hy - 0.5) + 0.5, 0.6) for s in (-1, 1)])
    return [(body.union(ridge), CREAM), (union(con).union(inner), GOLD), (ends, METAL)]


def fh34(n):
    # Hirose FH34SRJ back-flip FPC connector, 0.5 mm pitch, 1.0 high: cable enters from +y, the flap is at the back
    def build():
        hw = (n - 1) * 0.25 + 1.3
        body = box(-hw, -0.5, 0.0, hw, 3.1, 0.62).cut(box(-hw + 0.5, 1.2, 0.3, hw - 0.5, 3.3, 0.7))
        flap = box(-hw + 0.25, -0.6, 0.62, hw - 0.25, 1.2, 1.0)
        pins = union([box((k - (n - 1) / 2) * 0.5 - 0.1, -0.85, 0.0, (k - (n - 1) / 2) * 0.5 + 0.1, 2.6, 0.32) for k in range(n)])
        tabs = union([box(s * (hw + 0.1) - 0.25, 2.0, 0.0, s * (hw + 0.1) + 0.25, 3.0, 0.4) for s in (-1, 1)])
        return [(body, CREAM), (flap, BLACK), (pins, GOLD), (tabs, METAL)]
    return build


def pj342():
    # SHOUHAN PJ-342 3.5 mm jack: body 12 x 6 x 4.5, collar toward -x
    body = box(0.0, -3.0, 0.0, 12.05, 3.0, 4.5).edges('|X').chamfer(0.5)
    bore = cq.Workplane('YZ').circle(1.8).extrude(14.0).translate((-2.2, 0, 2.3))
    collar = cq.Workplane('YZ').circle(2.5).extrude(2.05).translate((-2.05, 0, 2.3))
    body = body.union(collar).cut(bore)
    legs = union([box(x - 0.6, sy * 3.6 - 0.8, 0.0, x + 0.6, sy * 3.6 + 0.8, 0.3)
                  for (x, sy) in ((2.95, -1), (10.25, -1), (12.25, -1), (2.95, 1), (10.25, 1))])
    ring = cq.Workplane('YZ').circle(1.82).circle(1.6).extrude(9.0).translate((0.5, 0, 2.3))
    return [(body, BLACK), (legs, TIN), (ring, GOLD)]


def alps_sksw():
    # Alps SKSWCFE010 tact switch, 3.0 x 2.0 x 0.6 with a 1.2 mm actuator dome
    base = box(-1.5, -1.0, 0.0, 1.5, 1.0, 0.42)
    cover = box(-1.5, -1.0, 0.42, 1.5, 1.0, 0.5)
    dome = cq.Workplane('XY').circle(0.6).extrude(0.1).translate((0, 0, 0.5)).edges('>Z').fillet(0.06)
    legs = union([box(s * 1.7 - 0.25, -0.7, 0.0, s * 1.7 + 0.25, 0.7, 0.2) for s in (-1, 1)])
    return [(base, BLACK), (cover.union(legs), METAL), (dome, DARK)]


# footprint name -> builder
MODELS = {
    'USB_C_Receptacle_HRO_TYPE-C-31-M-12': usb_c,
    'microSD_HC_Molex_104031-0811': microsd,
    'JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal': jst_sh,
    'Molex_SPOX_5268-03A_1x03_P2.50mm_Horizontal': molex_5268,
    'SW_SPST_EVQP7C': evqp7,
    'Mounting_Wuerth_WA-SMSI-M2.5_H1.5mm_9774015151R': spacer(5.2, 2.5, 1.5),
    'MountingHole_M1.6_Pad': spacer(3.0, 1.6, 1.5),            # Wuerth 9774015633R on the keyboard board
    'Hirose_DF40C-100DS-0.4V_2x50_P0.4mm': df40_100,
    'Hirose_FH34SRJ-8S-0.5SH_1x08-1MP_P0.50mm_Horizontal': fh34(8),
    'Hirose_FH34SRJ-20S-0.5SH_1x20-1MP_P0.50mm_Horizontal': fh34(20),
    'Jack_3.5mm_SHOUHAN_PJ-342': pj342,
    'SW_Alps_SKSWCFE010_3x2mm': alps_sksw,
    'VQFN-32-1EP_4x4mm_P0.4mm_EP2.8x2.8mm': qfn(4.0, 0.9, 8, 0.4, 0.2),
    'WQFN-24-1EP_4x4mm_P0.5mm_EP2.45x2.45mm': qfn(4.0, 0.75, 6, 0.5, 0.25),
    'TDFN-8-1EP_2x2mm_P0.5mm_EP0.8x1.2mm': qfn(2.0, 0.75, 4, 0.5, 0.25, two_sided=True),
}


def main(out):
    os.makedirs(out, exist_ok=True)
    for name, build in MODELS.items():
        asm = cq.Assembly(name=name.replace('.', '_'))
        for i, (solid, colour) in enumerate(build()):
            asm.add(solid, name=f'p{i}', color=colour)
        asm.save(os.path.join(out, name + '.step'))
        print(name)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                           '../lib/hackerslide.3dshapes'))
