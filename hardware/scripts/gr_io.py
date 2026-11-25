"""gridroute, pcbnew side: export a board's copper as polygons, and import routed tracks back.

  python3 gr_io.py export BOARD.kicad_pcb DRC.json OUT.json     (DRC.json from kicad-cli pcb drc --format json)
  python3 gr_io.py import BOARD.kicad_pcb ROUTES.json

See gridroute.py for what happens in between.  Runs with the system python3 (it needs pcbnew).
"""
import json
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
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            add(t, t.GetNetname(), cu, 'via')
            holes.append({'x': MM(t.GetPosition().x), 'y': MM(t.GetPosition().y), 'd': MM(t.GetDrillValue()), 'net': t.GetNetname()})
        else:
            add(t, t.GetNetname(), [t.GetLayer()], 'track')
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
    print(f"imported {len(r['tracks'])} tracks, {len(r['vias'])} vias; {len(r.get('failed', []))} connections failed")


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


if __name__ == '__main__':
    if sys.argv[1] == 'rip':
        rip(*sys.argv[2:])
    elif sys.argv[1] == 'export':
        export(*sys.argv[2:5])
    else:
        import_(*sys.argv[2:4])
