"""gridroute, pcbnew side: export a board's copper as polygons, and import routed tracks back.

  python3 gr_io.py export BOARD.kicad_pcb DRC.json OUT.json     (DRC.json from kicad-cli pcb drc --format json)
  python3 gr_io.py import BOARD.kicad_pcb ROUTES.json

See gridroute.py for what happens in between.  Runs with the system python3 (it needs pcbnew).
"""
import fnmatch
import json
import math
import os
import re
import sys

import pcbnew

MM = pcbnew.ToMM
ERR = pcbnew.FromMM(0.005)


def polys(sps):
    out = []
    for i in range(sps.OutlineCount()):
        o = sps.Outline(i)
        out.append([(MM(o.CPoint(j).x), MM(o.CPoint(j).y)) for j in range(o.PointCount())])
    return out


def export(board_path, drc_path, out_path):
    b = pcbnew.LoadBoard(board_path)
    cu = [l for l in b.GetEnabledLayers().CuStack()]
    names = {l: b.GetLayerName(l) for l in cu}
    items, holes, keepouts = [], [], []

    def add(item, net, layers, kind, smd=False, fine=False):
        for l in layers:
            sps = pcbnew.SHAPE_POLY_SET()
            item.TransformShapeToPolygon(sps, l, 0, ERR, pcbnew.ERROR_OUTSIDE)
            for p in polys(sps):
                if len(p) >= 3:
                    items.append({'net': net, 'layer': names[l], 'poly': p, 'kind': kind, 'smd': smd, 'fine': fine})

    for fp in b.GetFootprints():
        fine = fp.GetPadCount() >= 6          # ICs and FPC connectors: their pads get a no-via fan-out zone
        for pad in fp.Pads():
            ls = [l for l in cu if pad.IsOnLayer(l)]
            if ls:
                smd = pad.GetAttribute() == pcbnew.PAD_ATTRIB_SMD
                add(pad, pad.GetNetname(), ls, 'pad', smd=smd, fine=fine and smd)
            if pad.GetDrillSize().x > 0:
                holes.append({'x': MM(pad.GetPosition().x), 'y': MM(pad.GetPosition().y),
                              'd': MM(max(pad.GetDrillSize().x, pad.GetDrillSize().y)),
                              'net': pad.GetNetname() if pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH else ''})
    sc = Scripted(board_path, b)
    power = {}
    for code, net in b.GetNetsByNetcode().items():
        try:
            power[net.GetNetname()] = b.GetDesignSettings().m_NetSettings.GetEffectiveNetClass(net.GetNetname()).GetName()
        except Exception:
            pass
    for t in b.GetTracks():
        n_before = len(items)
        if t.Type() == pcbnew.PCB_VIA_T:
            add(t, t.GetNetname(), cu, 'via')
            holes.append({'x': MM(t.GetPosition().x), 'y': MM(t.GetPosition().y), 'd': MM(t.GetDrillValue()), 'net': t.GetNetname()})
        else:
            add(t, t.GetNetname(), [t.GetLayer()], 'track')
            # a segment the router itself laid in an earlier pass may be taken up again (gridroute --reroute);
            # the wide power class is left alone
            if sc.routed(t) and power.get(t.GetNetname()) not in ('Power', 'HV'):
                for it in items[n_before:]:
                    it['rip'] = {'seg': [MM(t.GetStart().x), MM(t.GetStart().y), MM(t.GetEnd().x), MM(t.GetEnd().y)], 'w': MM(t.GetWidth())}
    for z in b.Zones():
        if z.GetIsRuleArea() and (z.GetDoNotAllowTracks() or z.GetDoNotAllowVias()):
            for p in polys(z.Outline()):
                keepouts.append({'layers': [names[l] for l in cu if z.IsOnLayer(l)], 'poly': p})
        elif not z.GetIsRuleArea() and z.GetAssignedPriority() > 0:
            # a copper area that outranks the ground pours (power areas): real copper of its net
            for l in cu:
                if z.IsOnLayer(l):
                    for p in polys(z.GetFilledPolysList(l)):
                        if len(p) >= 3:
                            items.append({'net': z.GetNetname(), 'layer': names[l], 'poly': p, 'kind': 'zone', 'smd': False, 'fine': False})
    # every separate piece of the ground pours, so the router can give each one a via
    frags = []
    for z in b.Zones():
        if not z.GetIsRuleArea() and z.GetAssignedPriority() == 0:
            for l in cu:
                if z.IsOnLayer(l):
                    for p in polys(z.GetFilledPolysList(l)):
                        if len(p) >= 3:
                            frags.append({'net': z.GetNetname(), 'layer': names[l], 'poly': p})
    outline = pcbnew.SHAPE_POLY_SET()
    b.GetBoardPolygonOutlines(outline)
    bb = b.GetBoardEdgesBoundingBox()
    conns = []
    for u in json.load(open(drc_path))['unconnected_items']:
        ends = []
        for it in u['items']:
            d = it['description']
            m = re.search(r'\[(.*?)\]', d)
            if not m:
                ends = []
                break
            ls = [n for n in names.values() if re.search(r'\b' + re.escape(n) + r'\b', d)]
            if d.startswith('PTH') or d.startswith('Via') or not ls:
                ls = list(names.values())
            ends.append({'x': it['pos']['x'], 'y': it['pos']['y'], 'layers': ls, 'net': m.group(1), 'what': d[:40],
                         'zone': d.startswith('Zone')})
        if len(ends) == 2 and not (ends[0]['zone'] and ends[1]['zone']):
            if ends[0]['zone']:
                ends.reverse()
            conns.append({'net': ends[0]['net'], 'a': ends[0], 'b': ends[1]})
    classes = {}
    ns = b.GetDesignSettings().m_NetSettings
    for code, net in b.GetNetsByNetcode().items():
        try:
            classes[net.GetNetname()] = ns.GetEffectiveNetClass(net.GetNetname()).GetName()
        except Exception:
            classes[net.GetNetname()] = 'Default'
    json.dump({'bbox': [MM(bb.GetLeft()), MM(bb.GetTop()), MM(bb.GetRight()), MM(bb.GetBottom())],
               'layers': [names[l] for l in cu], 'outline': polys(outline), 'items': items, 'holes': holes,
               'keepouts': keepouts, 'conns': conns, 'classes': classes, 'pour_frags': frags}, open(out_path, 'w'))
    print(f'exported {len(items)} shapes, {len(holes)} holes, {len(conns)} connections')


def import_(board_path, routes_path):
    b = pcbnew.LoadBoard(board_path)
    r = json.load(open(routes_path))
    lid = {b.GetLayerName(l): l for l in b.GetEnabledLayers().CuStack()}
    nets = {n.GetNetname(): n for n in b.GetNetsByNetcode().values()}
    F = pcbnew.FromMM
    key = lambda net, layer, c: (net, layer) + tuple(round(v, 3) for v in c)
    index = {}
    for t in b.GetTracks():
        if t.Type() != pcbnew.PCB_VIA_T:
            index[key(t.GetNetname(), b.GetLayerName(t.GetLayer()),
                      (MM(t.GetStart().x), MM(t.GetStart().y), MM(t.GetEnd().x), MM(t.GetEnd().y)))] = t
    victims = [index[k] for k in {key(s_['net'], s_['layer'], s_['seg']) for s_ in r.get('removed', [])} if k in index]
    gone = len(victims)
    for t in victims:
        b.Remove(t)
    if gone:
        print(f'took up {gone} earlier segments')
    for t in r['tracks']:
        for a, c in zip(t['pts'], t['pts'][1:]):
            s = pcbnew.PCB_TRACK(b)
            s.SetStart(pcbnew.VECTOR2I(F(a[0]), F(a[1]))); s.SetEnd(pcbnew.VECTOR2I(F(c[0]), F(c[1])))
            s.SetWidth(F(t['w'])); s.SetLayer(lid[t['layer']]); s.SetNet(nets[t['net']])
            b.Add(s)
    for v in r['vias']:
        s = pcbnew.PCB_VIA(b)
        s.SetPosition(pcbnew.VECTOR2I(F(v['x']), F(v['y'])))
        s.SetWidth(pcbnew.F_Cu, F(v['d'])); s.SetDrill(F(v['drill']))
        s.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); s.SetNet(nets[v['net']])
        b.Add(s)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(board_path, b)
    print(f"imported {len(r['tracks'])} tracks, {len(r['vias'])} vias; {len(r.get('failed', []))} connections failed", flush=True)
    os._exit(0)


def rip(board_path, width, *nets):
    """Delete the tracks of the given nets that have the given width (the router's, not the fan-out stubs')."""
    b = pcbnew.LoadBoard(board_path)
    w = pcbnew.FromMM(float(width))
    gone = [t for t in b.GetTracks() if t.Type() != pcbnew.PCB_VIA_T and t.GetNetname() in nets and abs(t.GetWidth() - w) < 100]
    for t in gone:
        b.Remove(t)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(board_path, b)
    print(f'removed {len(gone)} track segments')


class Scripted:
    """What the generator itself put on the board (scripted.json next to it, written by pcbgen.save_scripted before
    the first routing pass).  Everything else is the router's and may be taken up again."""
    def __init__(self, board_path, b):
        p = os.path.join(os.path.dirname(os.path.abspath(board_path)), 'scripted.json')
        self.ok = os.path.exists(p)
        d = json.load(open(p)) if self.ok else {'vias': [], 'segs': []}
        self.vias = {tuple(v) for v in d['vias']}
        self.segs = {tuple(s_) for s_ in d['segs']}
        self.b = b

    def key(self, t):
        if t.Type() == pcbnew.PCB_VIA_T:
            return (round(MM(t.GetPosition().x), 3), round(MM(t.GetPosition().y), 3))
        return (t.GetNetname(), self.b.GetLayerName(t.GetLayer()), round(MM(t.GetStart().x), 3), round(MM(t.GetStart().y), 3),
                round(MM(t.GetEnd().x), 3), round(MM(t.GetEnd().y), 3))

    def routed(self, t):
        """True for a track segment or via that the router made"""
        if not self.ok:
            return False
        return self.key(t) not in (self.vias if t.Type() == pcbnew.PCB_VIA_T else self.segs)


def save_scripted(board_path):
    b = pcbnew.LoadBoard(board_path)
    sc = Scripted(board_path, b)
    json.dump({'vias': sorted(sc.key(t) for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T),
               'segs': sorted(sc.key(t) for t in b.GetTracks() if t.Type() != pcbnew.PCB_VIA_T)},
              open(os.path.join(os.path.dirname(os.path.abspath(board_path)), 'scripted.json'), 'w'))


def _finish(b, board_path, gone, what):
    seen = set()
    for t in gone:
        k = (t.Type(), t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y, t.GetLayer())
        if k not in seen:
            seen.add(k)
            b.Remove(t)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(board_path, b)
    print(f'{what}: removed {len(seen)} routed segments and vias', flush=True)
    os._exit(0)          # pcbnew 9.0.2 crashes on interpreter exit after Remove()


def _find(b, sc, it):
    """the routed track segment or via that a DRC item describes, or None"""
    d = it['description']
    x, y = it['pos']['x'], it['pos']['y']
    mv = re.match(r'Via \[(.*?)\]', d)
    if mv:
        for t in b.GetTracks():
            if (t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() == mv.group(1)
                    and abs(MM(t.GetPosition().x) - x) < 1e-3 and abs(MM(t.GetPosition().y) - y) < 1e-3):
                return t if sc.routed(t) else None
        return None
    m = re.match(r'Track \[(.*?)\] on (\S+?), length ([\d.]+)', d)
    if not m:
        return None
    best = None
    for t in b.GetTracks():
        if (t.Type() == pcbnew.PCB_VIA_T or t.GetNetname() != m.group(1) or b.GetLayerName(t.GetLayer()) != m.group(2)
                or abs(MM(t.GetLength()) - float(m.group(3))) > 0.002 or not sc.routed(t)):
            continue
        dd = min(abs(MM(q.x) - x) + abs(MM(q.y) - y) for q in (t.GetStart(), t.GetEnd(), t.GetCenter()))
        if best is None or dd < best[0]:
            best = (dd, t)
    return best[1] if best and best[0] < 0.05 else None


def ripdrc(board_path, drc_path):
    """Delete the routed segments and vias that the design-rule check objects to (clearance, short, hole clearance,
    rule area), so that the next gridroute pass lays them again.  Scripted copper is never touched."""
    b = pcbnew.LoadBoard(board_path)
    sc = Scripted(board_path, b)
    gone = []
    for v in json.load(open(drc_path))['violations']:
        if v['severity'] == 'error' and v['type'] in ('clearance', 'shorting_items', 'hole_clearance', 'items_not_allowed', 'tracks_crossing'):
            gone += [t for t in (_find(b, sc, it) for it in v['items']) if t is not None]
    _finish(b, board_path, gone, 'ripdrc')


def ripnear(board_path, drc_path, radius):
    """Delete every routed segment and via within `radius` mm of the ends of the connections that are still open: the
    next pass routes those connections first and then puts the neighbours back (regional rip-up)."""
    b = pcbnew.LoadBoard(board_path)
    sc = Scripted(board_path, b)
    r = float(radius)
    pts = [(it['pos']['x'], it['pos']['y']) for u in json.load(open(drc_path))['unconnected_items'] for it in u['items']
           if not it['description'].startswith('Zone')]

    def dist(px, py, t):
        ax, ay, bx, by = MM(t.GetStart().x), MM(t.GetStart().y), MM(t.GetEnd().x), MM(t.GetEnd().y)
        vx, vy = bx - ax, by - ay
        L = vx * vx + vy * vy
        k = 0 if L == 0 else max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / L))
        return ((px - ax - k * vx) ** 2 + (py - ay - k * vy) ** 2) ** 0.5
    gone = [t for t in b.GetTracks() if sc.routed(t) and any(dist(px, py, t) < r for px, py in pts)]
    _finish(b, board_path, gone, f'ripnear {r} mm')


def anchor(board_path, fix='1'):
    """Give every track end a full-width joint.  The router works on a grid, so a track can end beside a pad, via or
    other track with only its round end cap overlapping it: connected for KiCad, but a neck of a few hundredths of a
    millimetre on the real board.  For each end whose centre is not inside copper of its own net, a short segment
    is added to the centre of the pad or via it touches, or square onto the centreline of the track it touches.
    With fix='0' it only counts."""
    b = pcbnew.LoadBoard(board_path)
    F = pcbnew.FromMM
    tracks = [t for t in b.GetTracks() if t.Type() != pcbnew.PCB_VIA_T]
    vias = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
    pads = [p for f in b.GetFootprints() for p in f.Pads() if p.GetNetname()]
    by = {}
    for t in tracks:
        by.setdefault((t.GetNetCode(), t.GetLayer()), []).append(t)
    vby, pby = {}, {}
    for v in vias:
        vby.setdefault(v.GetNetCode(), []).append(v)
    for p in pads:
        pby.setdefault(p.GetNetCode(), []).append(p)

    def foot(pt, t):          # nearest point on a segment's centreline, and the distance to it
        ax, ay, bx, by_ = t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y
        dx, dy = bx - ax, by_ - ay
        L2 = dx * dx + dy * dy
        u = 0.0 if not L2 else max(0.0, min(1.0, ((pt.x - ax) * dx + (pt.y - ay) * dy) / L2))
        qx, qy = ax + u * dx, ay + u * dy
        return (qx, qy), math.hypot(pt.x - qx, pt.y - qy)
    weak, added = 0, []
    for t in tracks:
        n, l, w = t.GetNetCode(), t.GetLayer(), t.GetWidth()
        for pt in (t.GetStart(), t.GetEnd()):
            target, inside = None, False
            for o in by[(n, l)]:
                if o is t:
                    continue
                q, d = foot(pt, o)
                if d <= o.GetWidth() / 2 - w / 4 or d < 2000:       # well inside the other track, or on its centreline
                    inside = True
                    break
                if d <= (o.GetWidth() + w) / 2 and (target is None or d < target[1]):
                    target = (q, d)
            if inside:
                continue
            for v in vby.get(n, []):
                d = math.hypot(pt.x - v.GetPosition().x, pt.y - v.GetPosition().y)
                if d < 2000:
                    inside = True
                    break
                if d <= (v.GetWidth(l) + w) / 2 and (target is None or d <= target[1] + w):
                    target = ((v.GetPosition().x, v.GetPosition().y), 0)
            if inside:
                continue
            for p in pby.get(n, []):
                if not p.IsOnLayer(l):
                    continue
                poly = p.GetEffectivePolygon(l, pcbnew.ERROR_INSIDE)
                if poly.Contains(pcbnew.VECTOR2I(pt.x, pt.y), -1, int(w / 4)) and not poly.Contains(pcbnew.VECTOR2I(pt.x, pt.y), -1, 0):
                    target = ((p.GetPosition().x, p.GetPosition().y), 0)       # on the rim
                elif poly.Contains(pcbnew.VECTOR2I(pt.x, pt.y), -1, 0):
                    # inside the pad: good if at least a quarter width from its edge, else pull it to the centre
                    shrunk = pcbnew.SHAPE_POLY_SET(poly)
                    shrunk.Deflate(int(w / 4), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, 5000)
                    if shrunk.OutlineCount() and shrunk.Contains(pcbnew.VECTOR2I(pt.x, pt.y), -1, 0):
                        inside = True
                    else:
                        target = ((p.GetPosition().x, p.GetPosition().y), 0)
                    break
                elif poly.Contains(pcbnew.VECTOR2I(pt.x, pt.y), -1, int(w / 2) + 1000):
                    target = ((p.GetPosition().x, p.GetPosition().y), 0)
            if inside or target is None:
                continue
            weak += 1
            if fix != '1':
                print(f'  {t.GetNetname()} on {t.GetLayerName()} at ({MM(pt.x):.3f}, {MM(pt.y):.3f}), track {MM(w):.2f} mm')
            if fix == '1':
                s = pcbnew.PCB_TRACK(b)
                s.SetStart(pcbnew.VECTOR2I(pt.x, pt.y)); s.SetEnd(pcbnew.VECTOR2I(int(target[0][0]), int(target[0][1])))
                s.SetWidth(w); s.SetLayer(l); s.SetNetCode(n)
                added.append(s)
    for s in added:
        b.Add(s)
    print(f'anchor: {weak} track ends joined only by their rim' + (f', {len(added)} extended' if fix == '1' else ''), flush=True)
    if added:
        json.dump([[s.GetNetname(), s.GetLayerName(), MM(s.GetStart().x), MM(s.GetStart().y), MM(s.GetEnd().x), MM(s.GetEnd().y)]
                   for s in added], open(board_path + '.anchored', 'w'))
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        pcbnew.SaveBoard(board_path, b)
    os._exit(0)


def unanchor(board_path, drc_path):
    """Take back the extensions made by anchor() that the design-rule check objects to (an extension toward a pad's
    centre can come too close to a neighbour).  Those few ends keep their rim joint; anchor(fix='0') counts them."""
    b = pcbnew.LoadBoard(board_path)
    added = json.load(open(board_path + '.anchored'))
    bad = [it for v in json.load(open(drc_path))['violations'] if v['severity'] == 'error' for it in v['items']]
    gone = []
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            continue
        k = [t.GetNetname(), t.GetLayerName(), MM(t.GetStart().x), MM(t.GetStart().y), MM(t.GetEnd().x), MM(t.GetEnd().y)]
        if not any(k[:2] == a[:2] and all(abs(p - q) < 1e-4 for p, q in zip(k[2:], a[2:])) for a in added):
            continue
        mx, my = (k[2] + k[4]) / 2, (k[3] + k[5]) / 2
        L = math.hypot(k[4] - k[2], k[5] - k[3])
        for it in bad:
            if f'[{k[0]}]' in it['description'] and it['description'].startswith('Track') and \
                    math.hypot(it['pos']['x'] - mx, it['pos']['y'] - my) <= L / 2 + 0.05:
                gone.append(t)
                break
    for t in gone:
        b.Remove(t)
    print(f'anchor: {len(gone)} extensions taken back', flush=True)
    if gone:
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        pcbnew.SaveBoard(board_path, b)
    os._exit(0)


def tidy(board_path, drc_path, skip=''):
    """Remove what the check calls dangling, if the router made it: vias used on one layer only and segments that end
    in nothing.  Scripted escape vias that turned out unused are removed too; scripted tracks stay."""
    b = pcbnew.LoadBoard(board_path)
    sc = Scripted(board_path, b)
    gone = []
    for v in json.load(open(drc_path))['violations']:
        it = v['items'][0]
        m = re.search(r'\[(.*?)\]', it['description'])
        if not m or m.group(1) in skip.split(',') or v['type'] not in ('via_dangling', 'track_dangling'):
            continue
        if v['type'] == 'via_dangling':
            for t in b.GetTracks():
                if (t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() == m.group(1)
                        and abs(MM(t.GetPosition().x) - it['pos']['x']) < 1e-3 and abs(MM(t.GetPosition().y) - it['pos']['y']) < 1e-3):
                    gone.append(t)
                    break
        else:
            t = _find(b, sc, it)
            if t is not None:
                gone.append(t)
    _finish(b, board_path, gone, 'tidy')


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd in ('tidy', 'ripdrc', 'ripnear', 'rip', 'save_scripted', 'anchor', 'unanchor'):
        globals()[cmd](*sys.argv[2:])
    elif cmd == 'export':
        export(*sys.argv[2:5])
    else:
        import_(*sys.argv[2:4])
