"""Narrowest point of each power copper area on the carrier, and what it means for heating.

  python3 power_paths.py [BOARD.kicad_pcb]      (system python: needs pcbnew, numpy, scipy, Pillow)

For every path below the filled copper of the net on that layer is rasterised (25 um), and the widest corridor that
still joins the two ends is found by eroding it: that width is the bottleneck.  The temperature rise is the IPC-2221
estimate for a LONG track of that width (dT = (I / (k A^0.725))^(1/0.44), k = 0.048 outer / 0.024 inner, A in
square mil), so for a short neck it is pessimistic.  Finished copper: outer 0.035 mm, inner 0.0152 mm (JLCPCB).
"""
import sys

import numpy as np
import pcbnew
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt, label
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import maximum_flow

G = 0.025
# net, layer, from (x, y), to (x, y), amps, what
PATHS = [('VBUS', 'In2.Cu', (8.4, 30.6), (67.8, 16.5), 0.83, 'USB-C to charger (input limit 0.83 A max, R12)'),
         ('VBAT', 'B.Cu', (69.5, 5.1), (63.2, 23.6), 3.2, 'battery connector to charger (fuse limit 3.0 A typ)'),
         ('VSYS_LIM', 'In2.Cu', (70.5, 33.0), (52.9, 61.5), 3.2, 'battery fuse to 5 V boost'),
         ('VSYS_LIM', 'B.Cu', (66.3, 58.9), (52.9, 61.5), 3.2, 'the same, parallel path on the display side along the bottom strip'),
         ('+5V', 'B.Cu', (41.4, 56.9), (43.9, 52.0), 2.0, 'boost to module pins 77-87')]


def cut_width(cu, a, c, step=4):
    """Total copper across the narrowest line between the two ends: a minimum cut on a 0.1 mm grid of the area
    (vias and slots split the copper into several passages; this adds them up).  Counted along the grid axes, so a
    cut that runs diagonally reads up to 1.4 times too wide."""
    m = cu[::step, ::step]
    idx = -np.ones(m.shape, np.int64)
    idx[m] = np.arange(m.sum())
    n = int(m.sum())
    rows, cols = [], []
    for dy, dx in ((0, 1), (1, 0)):
        p, q = idx[:m.shape[0] - dy, :m.shape[1] - dx], idx[dy:, dx:]
        ok = (p >= 0) & (q >= 0)
        rows += [p[ok], q[ok]]
        cols += [q[ok], p[ok]]
    near = lambda pt: idx[max(0, int(pt[1] / G / step) - 8):int(pt[1] / G / step) + 8, max(0, int(pt[0] / G / step) - 8):int(pt[0] / G / step) + 8]
    sa, sc = near(a), near(c)
    sa, sc = sa[sa >= 0], sc[sc >= 0]
    rows += [np.full(len(sa), n), sc]
    cols += [sa, np.full(len(sc), n + 1)]
    r, cc = np.concatenate(rows), np.concatenate(cols)
    cap = np.ones(len(r), np.int32)
    cap[-(len(sa) + len(sc)):] = 10000
    g = coo_matrix((cap, (r, cc)), shape=(n + 2, n + 2)).tocsr()
    return maximum_flow(g, n, n + 1).flow_value * G * step


def main(path):
    b = pcbnew.LoadBoard(path)
    T = pcbnew.ToMM
    bb = b.GetBoardEdgesBoundingBox()
    W, H = int(T(bb.GetRight()) / G) + 40, int(T(bb.GetBottom()) / G) + 40
    print('| Path | Layer | Current | Widest single passage at the neck | All passages together | IPC-2221 rise for that total, if it were long |')
    print('|---|---|---|---|---|---|')
    for net, layer, a, c, amps, what in PATHS:
        im = Image.new('1', (W, H), 0)
        dr = ImageDraw.Draw(im)
        for z in b.Zones():
            if z.GetIsRuleArea() or z.GetNetname() != net:
                continue
            for l in z.GetLayerSet().CuStack():
                if b.GetLayerName(l) != layer:
                    continue
                sps = z.GetFilledPolysList(l)
                for i in range(sps.OutlineCount()):
                    o = sps.Outline(i)
                    dr.polygon([(T(o.CPoint(j).x) / G, T(o.CPoint(j).y) / G) for j in range(o.PointCount())], fill=1)
                    for h in range(sps.HoleCount(i)):
                        ho = sps.Hole(i, h)
                        dr.polygon([(T(ho.CPoint(j).x) / G, T(ho.CPoint(j).y) / G) for j in range(ho.PointCount())], fill=0)
        dist = distance_transform_edt(np.array(im, bool)) * G

        def joined(r):
            lab, _ = label(dist >= r)
            near = lambda p: set(np.unique(lab[max(0, int(p[1] / G) - 40):int(p[1] / G) + 40, max(0, int(p[0] / G) - 40):int(p[0] / G) + 40])) - {0}
            return bool(near(a) & near(c))
        if not joined(0.01):
            print(f'| {what} | {layer} | {amps} A | **not joined** | | |')
            continue
        lo, hi = 0.0, 6.0
        for _ in range(12):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if joined(mid) else (lo, mid)
        w = 2 * lo
        # where the neck is: just above that width the two ends fall apart; the gap between the two pieces is the neck
        lab, _ = label(dist >= hi + 0.02)
        box = lambda p: lab[max(0, int(p[1] / G) - 40):int(p[1] / G) + 40, max(0, int(p[0] / G) - 40):int(p[0] / G) + 40]
        ia = [v for v in np.unique(box(a)) if v]
        ic = [v for v in np.unique(box(c)) if v]
        at = ''
        if ia and ic:
            da = distance_transform_edt(~np.isin(lab, ia))
            da[~np.isin(lab, ic)] = 1e9
            ny, nx = np.unravel_index(np.argmin(da), da.shape)
            at = f' near ({nx * G:.0f}, {ny * G:.0f})'
        t = 0.035 if layer in ('F.Cu', 'B.Cu') else 0.0152
        tot = max(w, cut_width(np.array(im, bool), a, c))
        area = (tot / 0.0254) * (t / 0.0254)
        k = 0.048 if layer in ('F.Cu', 'B.Cu') else 0.024
        rise = (amps / (k * area ** 0.725)) ** (1 / 0.44)
        print(f'| {what} | {layer} | {amps} A | {w:.2f} mm{at} | {tot:.1f} mm | {rise:.0f} K |')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '../carrier/carrier.kicad_pcb')
