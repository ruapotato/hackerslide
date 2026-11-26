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

    def pour_holes(self):
        """cells at the centre of plated holes of the pour net"""
        if getattr(self, '_ph', None) is None:
            self._ph = np.zeros((self.H, self.W), bool)
            for h in self.d['holes']:
                if h.get('net') == self.pour_net:
                    y, x = self.cell(h['x'], h['y'])
                    self._ph[y, x] = True
        return self._ph

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
        self.vz = np.zeros((self.H, self.W), np.int32)             # inner-layer power areas: closed to vias, except ground vias
        gt, gv = self.clr + width / 2, self.clr + self.via_d / 2
        for it in self.d['items']:
            n = self.nid(it['net'])
            if it['layer'] in self.occ:
                self.stamp(self.occ[it['layer']], self.mask_poly(it['poly'], gt), n)
                self.stamp(self.own[it['layer']], self.mask_poly(it['poly'], 0), n)
                if it['kind'] in ('pad', 'via'):
                    self.stamp(self.padown[it['layer']], self.mask_poly(it['poly'], 0), n)
            # a through via must clear copper on every layer; never put one in or against an SMD pad.
            # A power area on a layer the via only passes through is no obstacle: KiCad refills the area around it.
            # (in a narrow strip only ground vias are allowed that: a row of signal vias could cut it)
            if it['kind'] == 'zone' and it['layer'] not in ('F.Cu', 'B.Cu'):
                m = self.mask_poly(it['poly'], gv)
                if m is not None:
                    self.vz[m[0]:m[1], m[2]:m[3]][m[4]] = n
            else:
                self.stamp(self.vocc, self.mask_poly(it['poly'], gv), -1 if it['smd'] else n)
            if it.get('fine'):
                # no vias within FANOUT of fine-pitch pads: a via there would close the neighbours' escape lanes
                self.stamp(self.vocc, self.mask_poly(it['poly'], FANOUT), -1)
        if self.vz.any():
            # ... except where the area is more than 3 mm wide: a via there cannot cut it
            from scipy.ndimage import distance_transform_edt
            r = 1.5 / g
            wide = distance_transform_edt(self.vz != 0) >= r
            self.vz[distance_transform_edt(~wide) <= r] = 0
        for h in self.d['holes']:
            circ = [(h['x'] + h['d'] / 2 * math.cos(a), h['y'] + h['d'] / 2 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 48, endpoint=False)]
            hn = self.nid(h.get('net')) if h.get('net') else -1      # a plated hole of net X only blocks other nets
            for l in self.layers:
                self.stamp(self.occ[l], self.mask_poly(circ, 0.26 + width / 2), hn)     # hole-to-copper rule 0.2 + rounding
            self.stamp(self.vocc, self.mask_poly(circ, 0.3 + self.via_d / 2), -1)
        self.keep = {l: np.zeros((self.H, self.W), bool) for l in self.layers}      # no-track rule areas: closed even to own copper
        for k in self.d['keepouts']:
            for l in k['layers']:
                if l in self.occ:
                    m = self.mask_poly(k['poly'], width / 2 + g)
                    self.stamp(self.occ[l], m, -1)
                    if m is not None:
                        self.keep[l][m[0]:m[1], m[2]:m[3]] |= m[4]
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
        self.owner = {l: np.zeros((self.H, self.W), np.int32) for l in self.layers}   # which route blocked a cell
        self.vowner = np.zeros((self.H, self.W), np.int32)
        self.base = ({l: a.copy() for l, a in self.occ.items()}, {l: a.copy() for l, a in self.own.items()},
                     self.vocc.copy())
        self.erode_own()

    def reset(self):
        """back to the board as exported: forget every route added in this run"""
        for l in self.layers:
            self.occ[l][:] = self.base[0][l]; self.own[l][:] = self.base[1][l]; self.owner[l][:] = 0
        self.vocc[:] = self.base[2]; self.vowner[:] = 0

    def stamp_owned(self, occ, owner, m, n, rid):
        if m is None:
            return
        by0, by1, bx0, bx1, mask = m
        if rid:
            o = owner[by0:by1, bx0:bx1]
            o[mask] = rid
        self.stamp(occ, m, n)

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

    def add_track(self, net, layer, pts, width, rid=0):
        n = self.nid(net)
        for a, b in zip(pts, pts[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1e-9
            nx, ny = -dy / L * 1e-3, dx / L * 1e-3
            quad = [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]
            self.stamp_owned(self.occ[layer], self.owner[layer], self.mask_poly(quad, self.clr + width / 2 + self.width / 2), n, rid)
            self.stamp(self.own[layer], self.mask_poly(quad, width / 2), n)
            self.stamp_owned(self.vocc, self.vowner, self.mask_poly(quad, self.clr + width / 2 + self.via_d / 2), n, rid)

    def refresh(self):
        self.erode_own()

    def add_via(self, net, x, y, rid=0):
        n = self.nid(net)
        circ = [(x + self.via_d / 2 * math.cos(a), y + self.via_d / 2 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)]
        for l in self.layers:
            self.stamp_owned(self.occ[l], self.owner[l], self.mask_poly(circ, self.clr + self.width / 2), n, rid)
            self.stamp(self.own[l], self.mask_poly(circ, 0), n)
            self.stamp(self.padown[l], self.mask_poly(circ, 0), n) if not rid else None
        m = self.mask_poly(circ, self.clr + self.via_d / 2)
        if m is not None:
            by0, by1, bx0, bx1, mask = m
            if rid:
                self.vowner[by0:by1, bx0:bx1][mask] = rid
            self.vocc[by0:by1, bx0:bx1][mask] = -1


RIP_COST = 60.0


def route_one(M, c, relaxed=False):
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
        seeds = []
        for l in end['layers']:
            if l not in L:
                continue
            w = lab[L.index(l), max(0, y - r):y + r + 1, max(0, x - r):x + r + 1]
            ys, xs = np.nonzero(w)
            if len(ys):                                          # nearest own copper to the reported anchor
                j = np.argmin((ys - min(r, y)) ** 2 + (xs - min(r, x)) ** 2)
                ids.add(int(w[ys[j], xs[j]]))
                seeds.append((2 * L.index(l), int(ys[j]) + max(0, y - r), int(xs[j]) + max(0, x - r)))
        return ids, seeds
    ia, sa = cluster(c['a'])
    to_pour = c['b'].get('zone') and c['net'] == M.pour_net
    ib, sb = (set(), []) if to_pour else cluster(c['b'])
    if not ia or (not ib and not to_pour):
        return None
    joined = bool(ia & ib)
    ma = np.isin(lab, list(ia))
    mb = None if to_pour else np.isin(lab, list(ib))
    nz = 2 * len(L) - 1
    cost = np.full((nz, M.H, M.W), -1.0, np.float32)
    for i, l in enumerate(L):
        o = M.occ[l]
        ok = (o == 0) | (o == n) | core[i]                       # free, own clearance zone, or inside own copper
        if relaxed:                                              # cells blocked only by this run's routes: dear, not closed
            o0 = M.base[0][l]
            cost[2 * i][(o0 == 0) | (o0 == n) | core[i]] = RIP_COST
        cost[2 * i][ok] = 1.0
        cost[2 * i][M.keep[l]] = -1.0
        if i:
            if relaxed:
                cost[2 * i - 1][(M.base[2] == 0) | (M.base[2] == n)] = VIA_COST + RIP_COST
            cost[2 * i - 1][(M.vocc == 0) | (M.vocc == n)] = VIA_COST
            if c['net'] != M.pour_net:
                cost[2 * i - 1][(M.vz != 0) & (M.vz != n)] = -1.0
    # start on the outline of cluster a only (fewer seeds, same result)
    from scipy.ndimage import binary_erosion
    edge = ma & ~binary_erosion(ma, structure=st)
    starts = [(2 * int(z), int(y), int(x)) for z, y, x in np.argwhere(edge)]
    if joined:
        # The raster says the two ends already touch, the design-rule check says they do not: copper of this net
        # that lies within a grid cell of each other without overlapping.  Lay a track from one anchor to the other
        # (through the net's own copper wherever it can), which closes the gap.
        mcp = MCP_Geometric(cost, offsets=[(0, dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx] + [(1, 0, 0), (-1, 0, 0)])
        costs, _ = mcp.find_costs(sa[:1], sb[:1])
        if not np.isfinite(costs[sb[0]]):
            return None
        return [tuple(int(v) for v in p) for p in mcp.traceback(sb[0])]
    mcp = MCP_Geometric(cost, offsets=[(0, dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx] + [(1, 0, 0), (-1, 0, 0)])
    costs, _ = mcp.find_costs(starts)
    if to_pour:
        # the pour (or ground plane) is everywhere copper is allowed: end in the nearest legal via site
        if nz < 3:
            return None
        cb = costs[1::2]
        # ... or on a plated hole that is already in the plane (an existing ground via or through-hole pin)
        ch = np.where(M.pour_holes()[None], costs[0::2], np.inf)
        if not np.isfinite(cb.min()) and not np.isfinite(ch.min()):
            return None
        if ch.min() <= cb.min() + VIA_COST:
            z, y, x = np.unravel_index(np.argmin(ch), ch.shape)
            return [tuple(int(v) for v in p) for p in mcp.traceback((2 * int(z), int(y), int(x)))]
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
    ap.add_argument('--fine', default='', help='WIDTH:CLEARANCE for a second attempt at what failed')
    ap.add_argument('--reroute', action='store_true', help='segments laid by earlier passes may be ripped up and laid again')
    ap.add_argument('--first', default='', help='nets to route before all others')
    ap.add_argument('--stitch', action='store_true', help='give every separate piece of the pour a via')
    ap.add_argument('--power-width', type=float, default=0.4)
    ap.add_argument('--power-last', action='store_true', help='route the Power class after the signals (small boards)')
    a = ap.parse_args()
    d = json.load(open(a.inp))
    pre = [it for it in d['items'] if it.get('rip')] if a.reroute else []
    if a.reroute:
        d['items'] = [it for it in d['items'] if not it.get('rip')]
    only, skip = set(filter(None, a.only.split(','))), set(filter(None, a.skip.split(',')))
    first = set(filter(None, a.first.split(',')))
    conns = [c for c in d['conns'] if (not only or c['net'] in only) and c['net'] not in skip]
    out = {'tracks': [], 'vias': [], 'failed': [], 'removed': []}
    if a.pour:
        # A piece of the pour that holds pads but no via is cut off from the plane: give one of its pads a route
        # to a via.  (KiCad reports these only as zone-to-zone gaps, which say nothing about where.)
        T = Maps(d, a.grid, a.layers.split(','), a.clearance, a.via, a.drill, a.edge)
        hv = np.zeros((T.H, T.W), bool)
        for h in d['holes']:
            if h.get('net') == a.pour:
                y, x = T.cell(h['x'], h['y'])
                hv[max(0, y - 1):y + 2, max(0, x - 1):x + 2] = True
        pads = [(it, sum(p[0] for p in it['poly']) / len(it['poly']), sum(p[1] for p in it['poly']) / len(it['poly']))
                for it in d['items'] if it['net'] == a.pour and it['kind'] == 'pad' and it['smd']]
        extra = 0
        for f in d.get('pour_frags', []):
            if f['net'] != a.pour or f['layer'] not in T.layers:
                continue
            m = T.mask_poly(f['poly'], 0)
            if m is None:
                continue
            by0, by1, bx0, bx1, mask = m
            if (mask & hv[by0:by1, bx0:bx1]).any():
                continue
            for it, px, py in pads:
                if it['layer'] != f['layer']:
                    continue
                y, x = T.cell(px, py)
                if by0 <= y < by1 and bx0 <= x < bx1 and mask[y - by0, x - bx0]:
                    conns.append({'net': a.pour, 'a': {'x': px, 'y': py, 'layers': [f['layer']], 'what': 'stranded pour pad', 'zone': False},
                                  'b': {'x': 0, 'y': 0, 'layers': [], 'what': 'pour', 'zone': True}})
                    extra += 1
                    break
        print('stranded pour pads:', extra, flush=True)
    by_w = {}
    for c in conns:
        w = a.power_width if d['classes'].get(c['net'], 'Default') in ('Power', 'HV') else a.width
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
            fast = d['classes'].get(c['net'], 'Default') in ('DSI', 'USB')     # high-speed nets get the direct paths
            if c['net'] in first:
                return (-1, 0)
            return (0 if fast else 1 if fine else 2, abs(c['a']['x'] - c['b']['x']) + abs(c['a']['y'] - c['b']['y']))
        cs = sorted(by_w[w], key=prio)
        import collections
        queue = collections.deque(cs)
        ripped = collections.Counter()
        routes = {}                                       # rid -> (connection, tracks, vias) made at this width
        next_rid = [1]

        def restamp():
            M.reset()
            for t in done_tracks:
                M.add_track(t['net'], t['layer'], t['pts'], t['w'])
            for v in done_vias:
                M.add_via(v['net'], v['x'], v['y'])
            for rid, (_c, tr, vs, _p) in routes.items():
                for t in tr:
                    M.add_track(t['net'], t['layer'], t['pts'], t['w'], rid)
                for v in vs:
                    M.add_via(v['net'], v['x'], v['y'], rid)
            M.refresh()
        done_tracks, done_vias = list(out['tracks']), list(out['vias'])     # from wider classes: never ripped
        pre_rids = {}
        if w == a.width:
            for it in pre:
                if it['layer'] not in M.layers:
                    continue
                x0, y0, x1, y1 = it['rip']['seg']
                end = lambda x, y: {'x': x, 'y': y, 'layers': [it['layer']], 'what': 'earlier segment', 'zone': False}
                t = {'net': it['net'], 'layer': it['layer'], 'w': it['rip']['w'], 'pts': [(x0, y0), (x1, y1)]}
                rid = next_rid[0]; next_rid[0] += 1
                routes[rid] = ({'net': it['net'], 'a': end(x0, y0), 'b': end(x1, y1)}, [t], [], None)
                pre_rids[rid] = {'net': it['net'], 'layer': it['layer'], 'seg': it['rip']['seg']}
                M.add_track(t['net'], t['layer'], t['pts'], t['w'], rid)
            M.refresh()
        # Phases: first at the normal width and clearance; then the connections that failed are tried again with
        # the fine profile (--fine WIDTH:CLEARANCE), still able to rip up and re-route anything made in this run.
        phases = [(w, a.clearance)]
        if a.fine and w == a.width:
            fw, fc = (float(v) for v in a.fine.split(':'))
            phases.append((fw, fc))
        class_failed = []
        for ph, (wcur, ccur) in enumerate(phases):
            if ph:
                if not class_failed:
                    break
                print(f'fine phase: {len(class_failed)} connections at width {wcur}, clearance {ccur}', flush=True)
                M.clr = ccur
                M.build(wcur)
                restamp()
                queue = collections.deque(class_failed)
                class_failed = []
                ripped.clear()
            while queue:
                c = queue.popleft()
                path = route_one(M, c)
                if path == []:
                    continue                                 # already joined by an earlier route
                if not path:
                    # A track that stops at the rim of a via or pin of its own net (the raster calls that joined, the
                    # design-rule check does not): run it into the centre of the hole.
                    br = []
                    for e in (c['a'], c['b']):
                        if len(e['layers']) != 1 or e['layers'][0] not in M.layers:
                            continue
                        near = [(math.hypot(h['x'] - e['x'], h['y'] - e['y']), h) for h in d['holes'] + out['vias']
                                if h.get('net') == c['net']]
                        near = [q for q in near if 0.02 < q[0] < 0.5]
                        if near:
                            h = min(near, key=lambda q: q[0])[1]
                            br.append({'net': c['net'], 'layer': e['layers'][0], 'w': wcur, 'pts': [(e['x'], e['y']), (h['x'], h['y'])]})
                    if br and not c.get('bridged'):
                        c['bridged'] = True
                        rid = next_rid[0]; next_rid[0] += 1
                        routes[rid] = (c, br, [], [])
                        for t in br:
                            M.add_track(t['net'], t['layer'], t['pts'], t['w'], rid)
                        M.refresh()
                        print('bridged', c['net'], flush=True)
                        continue
                    # Rip-up and retry: find the cheapest path that may cross this run's routes, remove the routes
                    # it crosses, route this connection, and queue the removed ones again (at most 3 times each).
                    if ripped[id(c)] < 4 and routes:
                        rp = route_one(M, c, relaxed=True)
                        if rp:
                            n = M.nid(c['net'])
                            victims = set()
                            for z, y, x in rp:
                                if z % 2:
                                    if M.vocc[y, x] not in (0, n):
                                        victims.add(int(M.vowner[y, x]))
                                else:
                                    l = M.layers[z // 2]
                                    if M.occ[l][y, x] not in (0, n) and M.core[l][y, x] != n:
                                        victims.add(int(M.owner[l][y, x]))
                            victims.discard(0)
                            victims = {v for v in victims if v in routes}
                            if victims:
                                for v in victims:
                                    queue.append(routes.pop(v)[0])
                                ripped[id(c)] += 1
                                restamp()
                                queue.appendleft(c)
                                continue
                    class_failed.append(c)
                    print('FAILED', c['net'], c['a']['what'], '->', c['b']['what'], flush=True)
                    continue
                tr, vs = to_segments(M, path, c['net'], wcur)
                for t in tr:                                 # ends that stop at the rim of an own-net hole: run to its centre
                    for idx in (0, -1):
                        px, py = t['pts'][idx]
                        near = [(math.hypot(h['x'] - px, h['y'] - py), h) for h in d['holes'] + out['vias'] + vs if h.get('net') == c['net']]
                        near = [q for q in near if 0.02 < q[0] < 0.36]
                        if near:
                            h = min(near, key=lambda q: q[0])[1]
                            if idx == 0:
                                t['pts'].insert(0, (h['x'], h['y']))
                            else:
                                t['pts'].append((h['x'], h['y']))
                rid = next_rid[0]; next_rid[0] += 1
                routes[rid] = (c, tr, vs, path)
                for t in tr:
                    M.add_track(t['net'], t['layer'], t['pts'], t['w'], rid)
                for v in vs:
                    M.add_via(v['net'], v['x'], v['y'], rid)
                M.refresh()
        out['failed'] += class_failed
        # Final check: rebuild the maps from the exported board and replay the routes one by one.  A route whose
        # cells are no longer all free at its turn is dropped and reported, so what is written out is consistent.
        M.reset()
        for t in done_tracks:
            M.add_track(t['net'], t['layer'], t['pts'], t['w'])
        for v in done_vias:
            M.add_via(v['net'], v['x'], v['y'])
        M.refresh()
        dropped = 0
        out['removed'] += [seg for rid, seg in pre_rids.items() if rid not in routes]
        for rid, (c, tr, vs, path) in routes.items():
            if rid in pre_rids:                              # still on the board, untouched
                for t in tr:
                    M.add_track(t['net'], t['layer'], t['pts'], t['w'], rid)
                continue
            n = M.nid(c['net'])
            good = True
            for z, y, x in path:
                if z % 2:
                    good = M.vocc[y, x] in (0, n)
                else:
                    l = M.layers[z // 2]
                    good = M.occ[l][y, x] in (0, n) or M.core[l][y, x] == n
                if not good:
                    break
            if not good:
                dropped += 1
                out['failed'].append(c)
                print('DROPPED (failed the final check)', c['net'], c['a']['what'], '->', c['b']['what'], flush=True)
                continue
            for t in tr:
                M.add_track(t['net'], t['layer'], t['pts'], t['w'], rid)
            for v in vs:
                M.add_via(v['net'], v['x'], v['y'], rid)
            M.refresh()
            out['tracks'] += tr; out['vias'] += vs
        print(f'width {w}: {len(routes) - dropped} routed, rip-ups {sum(ripped.values())}, dropped {dropped}', flush=True)
    if a.stitch and by_w:
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
