"""gridroute: a small deterministic grid router for the connections the scripted routing leaves open.

  VENV/bin/python gridroute.py IN.json OUT.json [--grid 0.05] [--layers F.Cu,B.Cu] [--only NET,NET] [--skip NET,..]

Needs numpy, Pillow and scikit-image (not pcbnew): run it from the venv.  gr_io.py exports IN.json from a board and
imports OUT.json back.  build flow: hardware/scripts/gridroute.sh.

Method: every copper shape is rasterised per layer, grown by clearance + half the track width, into an occupancy
map that records which net owns each cell.  A connection is a least-cost path (scikit-image MCP, 8 directions in a
layer, through-vias between layers) through cells that are free or belong to its own net.  Each finished path is
added to the maps before the next one.  No rip-up: a connection that finds no path is reported, not forced.
It does not know about differential pairs or impedance.  Clearance is checked afterwards by KiCad's DRC.
"""
import argparse
import json
import math
import re

import numpy as np
from PIL import Image, ImageDraw
from skimage.graph import MCP_Geometric

WIDTH = {'Default': None, 'Power': 0.4}     # None = the --width argument
VIA_COST = 40.0
FANOUT = 1.3


class Maps:
    def __init__(self, d, g, layers, clr, via_d, via_drill, edge_clr):
        self.g, self.clr, self.via_d, self.via_drill = g, clr, via_d, via_drill
        x0, y0, x1, y1 = d['bbox']
        self.x0, self.y0 = x0 - 1.0, y0 - 1.0
        self.W = int(math.ceil((x1 - x0 + 2.0) / g)) + 1
        self.H = int(math.ceil((y1 - y0 + 2.0) / g)) + 1
        self.all_layers, self.layers = d['layers'], layers
        self.d = d
        self.netid = {}
        self.edge_clr = edge_clr
        self.pour_net = None

    def nid(self, net):
        return self.netid.setdefault(net, len(self.netid) + 1) if net else -1

    def px(self, x, y):
        return (x - self.x0) / self.g, (y - self.y0) / self.g

    def cell(self, x, y):
        return int(round((y - self.y0) / self.g)), int(round((x - self.x0) / self.g))

    def mask_poly(self, poly, grow):
        """Boolean mask of a polygon grown by `grow` mm (polygon + thick outline + round joints)."""
        pts = [self.px(*p) for p in poly]
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        r = grow / self.g
        bx0, by0 = max(0, int(min(xs) - r - 2)), max(0, int(min(ys) - r - 2))
        bx1, by1 = min(self.W, int(max(xs) + r + 3)), min(self.H, int(max(ys) + r + 3))
        if bx1 <= bx0 or by1 <= by0:
            return None
        im = Image.new('1', (bx1 - bx0, by1 - by0), 0)
        dr = ImageDraw.Draw(im)
        q = [(x - bx0, y - by0) for x, y in pts]
        dr.polygon(q, fill=1)
        if r > 0.3:
            dr.line(q + [q[0]], fill=1, width=max(1, int(round(2 * r))))
            for (x, y) in q:
                dr.ellipse([x - r, y - r, x + r, y + r], fill=1)
        return (by0, by1, bx0, bx1, np.array(im, dtype=bool))

    @staticmethod
    def stamp(occ, m, n):
        if m is None:
            return
        by0, by1, bx0, bx1, mask = m
        v = occ[by0:by1, bx0:bx1]
        v[mask & (v != 0) & (v != n)] = -1
        v[mask & (v == 0)] = n

    def build(self, width):
        """occ[layer] for tracks of `width`, and viaok for vias, both as net-id maps (0 free, -1 blocked)."""
        g = self.g
        self.width = width
        self.occ = {l: np.zeros((self.H, self.W), np.int32) for l in self.layers}
        self.own = {l: np.zeros((self.H, self.W), np.int32) for l in self.layers}     # the copper itself, not grown
        self.padown = {l: np.zeros((self.H, self.W), np.int32) for l in self.layers}  # pads and vias only
        self.vocc = np.zeros((self.H, self.W), np.int32)
        gt, gv = self.clr + width / 2, self.clr + self.via_d / 2
        for it in self.d['items']:
            n = self.nid(it['net'])
            if it['layer'] in self.occ:
                self.stamp(self.occ[it['layer']], self.mask_poly(it['poly'], gt), n)
                self.stamp(self.own[it['layer']], self.mask_poly(it['poly'], 0), n)
                if it['kind'] in ('pad', 'via'):
                    self.stamp(self.padown[it['layer']], self.mask_poly(it['poly'], 0), n)
            # a through via must clear copper on every layer; never put one in or against an SMD pad
            self.stamp(self.vocc, self.mask_poly(it['poly'], gv), -1 if it['smd'] else n)
            if it.get('fine'):
                # no vias within FANOUT of fine-pitch pads: a via there would close the neighbours' escape lanes
                self.stamp(self.vocc, self.mask_poly(it['poly'], FANOUT), -1)
        for h in self.d['holes']:
            circ = [(h['x'] + h['d'] / 2 * math.cos(a), h['y'] + h['d'] / 2 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 48, endpoint=False)]
            hn = self.nid(h.get('net')) if h.get('net') else -1      # a plated hole of net X only blocks other nets
            for l in self.layers:
                self.stamp(self.occ[l], self.mask_poly(circ, 0.26 + width / 2), hn)     # hole-to-copper rule 0.2 + rounding
            self.stamp(self.vocc, self.mask_poly(circ, 0.3 + self.via_d / 2), -1)
        for k in self.d['keepouts']:
            for l in k['layers']:
                if l in self.occ:
                    self.stamp(self.occ[l], self.mask_poly(k['poly'], width / 2), -1)
            self.stamp(self.vocc, self.mask_poly(k['poly'], self.via_d / 2), -1)
        # outside the board, and the edge margin
        inside = Image.new('1', (self.W, self.H), 0)
        dr = ImageDraw.Draw(inside)
        for i, p in enumerate(self.d['outline']):
            dr.polygon([self.px(*q) for q in p], fill=1 if i == 0 else 0)
        ins = np.array(inside, dtype=bool)
        from scipy.ndimage import binary_erosion
        r = int(math.ceil((self.edge_clr + max(width, self.via_d) / 2) / g))
        yy, xx = np.ogrid[-r:r + 1, -r:r + 1]
        ins = binary_erosion(ins, structure=(xx * xx + yy * yy <= r * r))
        for l in self.layers:
            self.occ[l][~ins] = -1
        self.vocc[~ins] = -1
        self.erode_own()

    def erode_own(self):
        """core[l] = own copper shrunk by (width/2 - grid/2): cells where a new track of this width, centred there,
        stays inside copper of its own net (to within half a grid step).  Such cells are always passable."""
        from scipy.ndimage import maximum_filter, minimum_filter
        k = 2 * max(0, int((self.width / 2 - self.g / 2) / self.g)) + 1        # floor: narrow 0.5 mm-pitch pads keep a core
        self.core = {}
        for l in self.layers:
            o = self.own[l]
            self.core[l] = np.where((minimum_filter(o, size=k) == o) & (maximum_filter(o, size=k) == o), o, 0)
            # a pad is always enterable, even by a track wider than itself (KiCad's DRC judges the result)
            p = self.padown[l]
            self.core[l] = np.where(p > 0, p, self.core[l])

    def add_track(self, net, layer, pts, width):
        n = self.nid(net)
        for l, grow, target in [(layer, self.clr + width / 2 + self.width / 2, self.occ[layer]), (layer, 0.0, self.own[layer]),
                                (None, self.clr + width / 2 + self.via_d / 2, self.vocc)]:
            for a, b in zip(pts, pts[1:]):
                dx, dy = b[0] - a[0], b[1] - a[1]
                L = math.hypot(dx, dy) or 1e-9
                nx, ny = -dy / L * 1e-3, dx / L * 1e-3
                self.stamp(target, self.mask_poly([(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)],
                                                  grow if grow else width / 2), n)

    def refresh(self):
        self.erode_own()

    def add_via(self, net, x, y):
        n = self.nid(net)
        circ = [(x + self.via_d / 2 * math.cos(a), y + self.via_d / 2 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)]
        for l in self.layers:
            self.stamp(self.occ[l], self.mask_poly(circ, self.clr + self.width / 2), n)
            self.stamp(self.own[l], self.mask_poly(circ, 0), n)
        self.stamp(self.vocc, self.mask_poly(circ, self.clr + self.via_d / 2), -1)


def route_one(M, c, margin=None):
    """Least-cost path from ANY copper already connected to end a, to ANY copper already connected to end b.
    Returns [] if they are already joined, None if no path exists."""
    from scipy.ndimage import label
    n = M.nid(c['net'])
    L = M.layers
    core = np.stack([M.core[l] == n for l in L])                 # (layers, H, W): where net n may always run
    st = np.zeros((3, 3, 3), bool); st[1] = True; st[:, 1, 1] = True      # 8-connected in a layer, straight up/down
    lab, _ = label(core, structure=st)

    def cluster(end):
        y, x = M.cell(end['x'], end['y'])
        r = int(1.0 / M.g)
        ids = set()
        for l in end['layers']:
            if l not in L:
                continue
            w = lab[L.index(l), max(0, y - r):y + r + 1, max(0, x - r):x + r + 1]
            ys, xs = np.nonzero(w)
            if len(ys):                                          # nearest own copper to the reported anchor
                j = np.argmin((ys - min(r, y)) ** 2 + (xs - min(r, x)) ** 2)
                ids.add(int(w[ys[j], xs[j]]))
        return ids
    ia = cluster(c['a'])
    to_pour = c['b'].get('zone') and c['net'] == M.pour_net
    ib = set() if to_pour else cluster(c['b'])
    if not ia or (not ib and not to_pour):
        return None
    if ia & ib:
        return []
    ma = np.isin(lab, list(ia))
    mb = None if to_pour else np.isin(lab, list(ib))
    nz = 2 * len(L) - 1
    cost = np.full((nz, M.H, M.W), -1.0, np.float32)
    for i, l in enumerate(L):
        o = M.occ[l]
        cost[2 * i][(o == 0) | (o == n) | core[i]] = 1.0         # free, own clearance zone, or inside own copper
        if i:
            cost[2 * i - 1][(M.vocc == 0) | (M.vocc == n)] = VIA_COST
    # start on the outline of cluster a only (fewer seeds, same result)
    from scipy.ndimage import binary_erosion
    edge = ma & ~binary_erosion(ma, structure=st)
    starts = [(2 * int(z), int(y), int(x)) for z, y, x in np.argwhere(edge)]
    mcp = MCP_Geometric(cost, offsets=[(0, dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx] + [(1, 0, 0), (-1, 0, 0)])
    costs, _ = mcp.find_costs(starts)
    if to_pour:
        # the pour (or ground plane) is everywhere copper is allowed: end in the nearest legal via site
        if nz < 3:
            return None
        cb = costs[1::2]
        if not np.isfinite(cb.min()):
            return None
        z, y, x = np.unravel_index(np.argmin(cb), cb.shape)
        return [tuple(int(v) for v in p) for p in mcp.traceback((2 * int(z) + 1, int(y), int(x)))]
    cb = np.where(mb, costs[0::2], np.inf)
    if not np.isfinite(cb.min()):
        return None
    z, y, x = np.unravel_index(np.argmin(cb), cb.shape)
    return [tuple(int(v) for v in p) for p in mcp.traceback((2 * int(z), int(y), int(x)))]


def to_segments(M, path, net, width):
    tracks, vias = [], []
    run = []
    def flush(z):
        if len(run) >= 2:
            pts = [run[0]]
            for p, q, r in zip(run, run[1:], run[2:]):
                if (q[0] - p[0], q[1] - p[1]) != (r[0] - q[0], r[1] - q[1]):
                    pts.append(q)
            pts.append(run[-1])
            tracks.append({'net': net, 'layer': M.layers[z // 2], 'w': width,
                           'pts': [(round(M.x0 + x * M.g, 4), round(M.y0 + y * M.g, 4)) for (y, x) in pts]})
    cur = path[0][0]
    for z, y, x in path:
        if z % 2:                                   # in a via layer
            if not vias or (vias[-1]['x'], vias[-1]['y']) != (round(M.x0 + x * M.g, 4), round(M.y0 + y * M.g, 4)):
                vias.append({'net': net, 'x': round(M.x0 + x * M.g, 4), 'y': round(M.y0 + y * M.g, 4), 'd': M.via_d, 'drill': M.via_drill})
            flush(cur); run = [(y, x)]
            continue
        if z != cur:
            flush(cur); run = [run[-1]] if run else []
            cur = z
        run.append((y, x))
    flush(cur)
    return tracks, vias


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('inp'); ap.add_argument('out')
    ap.add_argument('--grid', type=float, default=0.05)
    ap.add_argument('--layers', default='F.Cu,B.Cu')
    ap.add_argument('--width', type=float, default=0.2)
    ap.add_argument('--clearance', type=float, default=0.2)      # board rule 0.15 + one grid step of rounding
    ap.add_argument('--via', type=float, default=0.45); ap.add_argument('--drill', type=float, default=0.2)
    ap.add_argument('--edge', type=float, default=0.35)
    ap.add_argument('--only', default=''); ap.add_argument('--skip', default='')
    ap.add_argument('--pour', default='GND', help='net of the ground pours/plane: a via anywhere connects to it')
    ap.add_argument('--stitch', action='store_true', help='give every separate piece of the pour a via')
    ap.add_argument('--power-width', type=float, default=0.4)
    ap.add_argument('--power-last', action='store_true', help='route the Power class after the signals (small boards)')
    a = ap.parse_args()
    d = json.load(open(a.inp))
    only, skip = set(filter(None, a.only.split(','))), set(filter(None, a.skip.split(',')))
    conns = [c for c in d['conns'] if (not only or c['net'] in only) and c['net'] not in skip]
    out = {'tracks': [], 'vias': [], 'failed': []}
    by_w = {}
    for c in conns:
        w = a.power_width if d['classes'].get(c['net'], 'Default') == 'Power' else a.width
        by_w.setdefault(w, []).append(c)
    for w in sorted(by_w, reverse=not a.power_last):     # wide (power) nets first unless --power-last
        M = Maps(d, a.grid, a.layers.split(','), a.clearance, a.via, a.drill, a.edge)
        M.pour_net = a.pour
        M.build(w)
        for t in out['tracks']:
            M.add_track(t['net'], t['layer'], t['pts'], t['w'])
        for v in out['vias']:
            M.add_via(v['net'], v['x'], v['y'])
        def prio(c):
            # fine-pitch IC and connector pins first (their escape lanes are one cell wide), then short before long
            fine = any(re.search(r'of (U|J)\d', c[e]['what']) for e in 'ab')
            return (0 if fine else 1, abs(c['a']['x'] - c['b']['x']) + abs(c['a']['y'] - c['b']['y']))
        cs = sorted(by_w[w], key=prio)
        for c in cs:
            path = route_one(M, c)
            if path == []:
                continue                                 # already joined by an earlier route
            if not path:
                out['failed'].append(c)
                print('FAILED', c['net'], c['a']['what'], '->', c['b']['what'])
                continue
            tr, vs = to_segments(M, path, c['net'], w)
            for t in tr:
                M.add_track(t['net'], t['layer'], t['pts'], t['w'])
            for v in vs:
                M.add_via(v['net'], v['x'], v['y'])
            M.refresh()
            out['tracks'] += tr; out['vias'] += vs
    if a.stitch:
        # Stitching: every separate piece of the pour on every layer gets one via (placed as deep inside the piece
        # as possible), which ties the pieces together through the other layers / the ground plane.
        from scipy.ndimage import distance_transform_edt
        n = M.nid(a.pour)
        has = np.zeros((M.H, M.W), bool)                      # where a pour-net via or plated hole already is
        for h in d['holes']:
            if h.get('net') == a.pour:
                y, x = M.cell(h['x'], h['y'])
                has[max(0, y - 2):y + 3, max(0, x - 2):x + 3] = True
        for v in out['vias']:
            if v['net'] == a.pour:
                y, x = M.cell(v['x'], v['y'])
                has[max(0, y - 2):y + 3, max(0, x - 2):x + 3] = True
        ok = np.isin(M.vocc, (0, n))
        for l in M.layers:
            ok &= np.isin(M.occ[l], (0, n))
        k = 0
        for f in sorted(d.get('pour_frags', []), key=lambda f: -len(f['poly'])):
            if f['net'] != a.pour:
                continue
            m = M.mask_poly(f['poly'], 0)
            if m is None:
                continue
            by0, by1, bx0, bx1, mask = m
            if (mask & has[by0:by1, bx0:bx1]).any():
                continue
            cand = mask & ok[by0:by1, bx0:bx1]
            if not cand.any():
                continue
            dist = distance_transform_edt(np.pad(cand, 1))[1:-1, 1:-1]
            y, x = np.unravel_index(np.argmax(dist), dist.shape)
            if dist[y, x] * a.grid < a.via / 2 + 0.1:
                continue                                       # piece too narrow to hold a via
            vx, vy = round(M.x0 + (x + bx0) * M.g, 4), round(M.y0 + (y + by0) * M.g, 4)
            M.add_via(a.pour, vx, vy)
            yy, xx = M.cell(vx, vy)
            has[max(0, yy - 2):yy + 3, max(0, xx - 2):xx + 3] = True
            ok[max(0, yy - 14):yy + 15, max(0, xx - 14):xx + 15] = False
            out['vias'].append({'net': a.pour, 'x': vx, 'y': vy, 'd': M.via_d, 'drill': M.via_drill})
            k += 1
        print('stitching vias:', k)
    json.dump(out, open(a.out, 'w'))
    print(f"routed {len(conns) - len(out['failed'])} of {len(conns)} connections, {len(out['vias'])} vias")


if __name__ == '__main__':
    main()
