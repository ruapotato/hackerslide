"""pcbgen: build a KiCad 9 board from kigen's netlist.json with the pcbnew Python API.

Placement is explicit for parts whose position matters (connectors, switches, the CM4 sockets) and a greedy
"pack near anchor" for small parts.  Routing is done by Freerouting (see route()), which is an autorouter:
treat its output as a starting point for a human layout, never as a finished board.
"""
import json
import math
import os
import subprocess

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
FPDIR = os.environ.get('KICAD9_FOOTPRINT_DIR', '/usr/share/kicad/footprints')
MM = pcbnew.FromMM


def fp_path(lib):
    if lib == 'hackerslide':
        return os.path.join(HERE, '..', 'lib', 'hackerslide.pretty')
    return os.path.join(FPDIR, lib + '.pretty')


class Board:
    def __init__(self, netlist_path, layers=2, thickness=1.6):
        self.nl = json.load(open(netlist_path))
        self.dir = os.path.dirname(os.path.abspath(netlist_path))
        self.name = self.nl['name']
        self.b = pcbnew.CreateEmptyBoard() if hasattr(pcbnew, 'CreateEmptyBoard') else pcbnew.BOARD()
        self.b.SetCopperLayerCount(layers)
        self.b.GetDesignSettings().SetBoardThickness(MM(thickness))
        self.layers = layers
        self.thickness = thickness
        self.nets = {}
        self.fps = {}
        self.comp = {c['ref']: c for c in self.nl['components']}
        self.occupied = []      # (side, x0, y0, x1, y1)
        for c in self.nl['components']:
            for net in list(c['pads'].values()) + list(c.get('nc', {}).values()):
                self._net(net)
            self._load(c)

    def _net(self, name):
        if name not in self.nets:
            ni = pcbnew.NETINFO_ITEM(self.b, name)
            self.b.Add(ni)
            self.nets[name] = ni
        return self.nets[name]

    def _load(self, c):
        lib, name = c['footprint'].split(':')
        fp = pcbnew.FootprintLoad(fp_path(lib), name)
        if fp is None:
            raise RuntimeError(f'footprint {c["footprint"]} not found for {c["ref"]}')
        fp.SetReference(c['ref'])
        fp.SetValue(c['value'])
        fp.SetFPIDAsString(c['footprint'])
        fp.SetPath(pcbnew.KIID_PATH(f"/{c['sheet_uuid']}/{c['sym_uuid']}"))
        fp.SetSheetname(c['sheet'])
        fp.SetSheetfile(c['sheetfile'])
        for k, v in c['fields'].items():
            if k in ('Reference', 'Value', 'Footprint', 'Datasheet'):
                continue
            fp.SetField(k, str(v))
            f = fp.GetFieldByName(k)
            if f:
                f.SetVisible(False)
        if not c.get('in_bom', True):
            fp.SetExcludedFromBOM(True)
        if c['dnp']:
            fp.SetDNP(True)
            fp.SetExcludedFromPosFiles(True)
        for pad in fp.Pads():
            net = c['pads'].get(pad.GetNumber()) or c.get('nc', {}).get(pad.GetNumber())
            if net:
                pad.SetNet(self.nets[net])
        fp.Reference().SetTextSize(pcbnew.VECTOR2I(MM(0.8), MM(0.8)))
        fp.Reference().SetTextThickness(MM(0.12))
        self.b.Add(fp)
        self.fps[c['ref']] = fp

    # ---------------------------------------------------------------------------------------------------
    def place(self, ref, x, y, rot=0.0, side='F'):
        fp = self.fps[ref]
        if side == 'B' and not fp.IsFlipped():
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        fp.SetOrientationDegrees(rot)
        self.occupied.append((side,) + self.bbox(ref))
        # drilled pads (through-hole pins, pegs, thermal vias) also take room on the other side
        other = 'B' if side == 'F' else 'F'
        for p in fp.Pads():
            d = max(p.GetDrillSize().x, p.GetDrillSize().y)
            if d > 0:
                r = pcbnew.ToMM(max(d, p.GetSize().x if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH else d)) / 2 + 0.3
                px, py = pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)
                self.occupied.append((other, px - r, py - r, px + r, py + r))
        fp.placed = True

    margin = 0.15     # extra room around every placed part; raise it where a router needs lanes between parts

    def bbox(self, ref, margin=None):
        margin = self.margin if margin is None else margin
        fp = self.fps[ref]
        bb = fp.GetCourtyard(pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd).BBox()
        if bb.GetWidth() == 0:
            bb = fp.GetBoundingBox(False)
        return (pcbnew.ToMM(bb.GetLeft()) - margin, pcbnew.ToMM(bb.GetTop()) - margin,
                pcbnew.ToMM(bb.GetRight()) + margin, pcbnew.ToMM(bb.GetBottom()) + margin)

    def size(self, ref, rot=0.0):
        fp = self.fps[ref]
        fp.SetOrientationDegrees(rot)
        fp.SetPosition(pcbnew.VECTOR2I(0, 0))
        x0, y0, x1, y1 = self.bbox(ref)
        return x1 - x0, y1 - y0, -x0, -y0   # w, h, offset of origin from bbox corner

    def pack(self, refs, ax, ay, side='F', region=None, step=0.25, rot=0.0, keepout=()):
        """Place each ref at the free spot nearest to (ax, ay) (spiral search), staying inside region."""
        rx0, ry0, rx1, ry1 = region or self.region
        for ref in refs:
            fp = self.fps[ref]
            if side == 'B' and not fp.IsFlipped():
                fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
            w, h, ox, oy = self.size(ref, rot)
            best = None
            for ring in range(0, 400):
                cands = []
                r = ring * step
                n = max(1, int(2 * math.pi * r / step))
                for k in range(n):
                    a = 2 * math.pi * k / n
                    cx, cy = ax + r * math.cos(a), ay + r * math.sin(a)
                    x0, y0 = cx - w / 2, cy - h / 2
                    if x0 < rx0 or y0 < ry0 or x0 + w > rx1 or y0 + h > ry1:
                        continue
                    box = (x0, y0, x0 + w, y0 + h)
                    if any(sd == side and not (box[2] <= o[0] or box[0] >= o[2] or box[3] <= o[1] or box[1] >= o[3])
                           for (sd, *o) in self.occupied):
                        continue
                    if any(not (box[2] <= k[0] or box[0] >= k[2] or box[3] <= k[1] or box[1] >= k[3]) for k in keepout):
                        continue
                    cands.append((x0 + ox, y0 + oy))
                if cands:
                    best = cands[0]
                    break
            if best is None:
                if not os.environ.get('PLACE_DEBUG'):
                    raise RuntimeError(f'no room for {ref} near {ax},{ay}')
                print(f'PLACE_DEBUG: no room for {ref} near {ax},{ay}')      # layout work: place it anyway and look
                best = (ax, ay)
            self.place(ref, best[0], best[1], rot, side)

    # ---------------------------------------------------------------------------------------------------
    def outline(self, x0, y0, x1, y1, r=1.0, cutouts=()):
        self.region = (x0 + 0.3, y0 + 0.3, x1 - 0.3, y1 - 0.3)
        def seg(a, b):
            s = pcbnew.PCB_SHAPE(self.b)
            s.SetShape(pcbnew.SHAPE_T_SEGMENT)
            s.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1])))
            s.SetEnd(pcbnew.VECTOR2I(MM(b[0]), MM(b[1])))
            s.SetLayer(pcbnew.Edge_Cuts)
            s.SetWidth(MM(0.05))
            self.b.Add(s)
        def arc(c, start, ang):
            s = pcbnew.PCB_SHAPE(self.b)
            s.SetShape(pcbnew.SHAPE_T_ARC)
            s.SetCenter(pcbnew.VECTOR2I(MM(c[0]), MM(c[1])))
            s.SetStart(pcbnew.VECTOR2I(MM(start[0]), MM(start[1])))
            s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(ang, pcbnew.DEGREES_T), True)
            s.SetLayer(pcbnew.Edge_Cuts)
            s.SetWidth(MM(0.05))
            self.b.Add(s)
        seg((x0 + r, y0), (x1 - r, y0)); seg((x1, y0 + r), (x1, y1 - r))
        seg((x1 - r, y1), (x0 + r, y1)); seg((x0, y1 - r), (x0, y0 + r))
        arc((x1 - r, y0 + r), (x1 - r, y0), 90); arc((x1 - r, y1 - r), (x1, y1 - r), 90)
        arc((x0 + r, y1 - r), (x0 + r, y1), 90); arc((x0 + r, y0 + r), (x0, y0 + r), 90)
        for (cx0, cy0, cx1, cy1) in cutouts:
            seg((cx0, cy0), (cx1, cy0)); seg((cx1, cy0), (cx1, cy1)); seg((cx1, cy1), (cx0, cy1)); seg((cx0, cy1), (cx0, cy0))

    def text(self, s, x, y, layer=pcbnew.F_SilkS, size=1.0, rot=0, mirror=False):
        t = pcbnew.PCB_TEXT(self.b)
        t.SetText(s)
        t.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        t.SetLayer(layer)
        t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
        t.SetTextThickness(MM(size * 0.15))
        t.SetTextAngleDegrees(rot)
        if mirror:
            t.SetMirrored(True)
        self.b.Add(t)

    def line(self, a, b, layer, w=0.1):
        s = pcbnew.PCB_SHAPE(self.b)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1])))
        s.SetEnd(pcbnew.VECTOR2I(MM(b[0]), MM(b[1])))
        s.SetLayer(layer)
        s.SetWidth(MM(w))
        self.b.Add(s)

    def rect(self, x0, y0, x1, y1, layer, w=0.1):
        for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            self.line(a, b, layer, w)

    def zone(self, net, layer, pts, priority=0, clearance=0.2, min_width=0.2, thermal_gap=0.25, keepout=False):
        z = pcbnew.ZONE(self.b)
        z.SetLayer(layer)
        if net:
            z.SetNet(self.nets[net])
        ol = z.Outline()
        ol.NewOutline()
        for (x, y) in pts:
            ol.Append(MM(x), MM(y))
        z.SetAssignedPriority(priority)
        z.SetLocalClearance(MM(clearance))
        z.SetMinThickness(MM(min_width))
        z.SetThermalReliefGap(MM(thermal_gap))
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)      # fab-assembled boards: solid joints, no starved spokes
        if keepout:
            z.SetIsRuleArea(True)
            z.SetDoNotAllowTracks(False)
            z.SetDoNotAllowVias(False)
            z.SetDoNotAllowPads(False)
            z.SetDoNotAllowCopperPour(False)
        self.b.Add(z)
        return z

    def fanout(self, ref, lengths=(1.3, 2.3), width=0.2, via_d=0.45, drill=0.2, skip=('GND',), only=None, where=None):
        """Dog-bone fan-out: from every SMD pad of `ref` a straight stub away from the part and a via at its end.
        Neighbouring pads alternate between the stub lengths so their vias are staggered.  The router then only
        has to reach the vias, not thread between fine-pitch pads."""
        fp = self.fps[ref]
        pads = [p for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]
        cx = sum(p.GetPosition().x for p in pads) / len(pads)
        cy = sum(p.GetPosition().y for p in pads) / len(pads)
        layer = pcbnew.B_Cu if fp.IsFlipped() else pcbnew.F_Cu
        sides = {}
        for p in pads:
            net = p.GetNetname()
            bb = p.GetBoundingBox()
            if where and not where(pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)):
                continue
            if (not net or net in skip or net.startswith('unconnected-') or (only and net not in only)
                    or p.GetNumber() in ('MP', 'SH', '')):        # mounting / shield pads join the pour instead
                continue
            horiz = bb.GetWidth() > bb.GetHeight()            # a pad's long axis points away from the part
            if bb.GetWidth() == bb.GetHeight():
                continue                                       # square pad (exposed pad, hold-down): no stub
            d = (1 if p.GetPosition().x > cx else -1, 0) if horiz else (0, 1 if p.GetPosition().y > cy else -1)
            sides.setdefault(d, []).append(p)
        for d, ps in sides.items():
            ps.sort(key=lambda p: p.GetPosition().y if d[0] else p.GetPosition().x)
            for i, p in enumerate(ps):
                L = MM(lengths[i % len(lengths)])
                a = p.GetPosition()
                e = pcbnew.VECTOR2I(a.x + d[0] * L, a.y + d[1] * L)
                t = pcbnew.PCB_TRACK(self.b)
                t.SetStart(a); t.SetEnd(e); t.SetWidth(MM(width)); t.SetLayer(layer); t.SetNet(p.GetNet())
                self.b.Add(t)
                v = pcbnew.PCB_VIA(self.b)
                v.SetPosition(e); v.SetWidth(pcbnew.F_Cu, MM(via_d)); v.SetDrill(MM(drill))
                v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(p.GetNet())
                self.b.Add(v)
                # later pack() calls keep clear of the stub (its own side) and of the via (both sides)
                ax, ay, ex, ey = pcbnew.ToMM(a.x), pcbnew.ToMM(a.y), pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
                m = via_d / 2 + 0.2
                side = 'B' if fp.IsFlipped() else 'F'
                self.occupied.append((side, min(ax, ex) - 0.25, min(ay, ey) - 0.25, max(ax, ex) + 0.25, max(ay, ey) + 0.25))
                for sd in ('F', 'B'):
                    self.occupied.append((sd, ex - m, ey - m, ex + m, ey + m))

    # ---- scripted routing (hand-laid blocks) -------------------------------------------------------------
    def pad_xy(self, ref, num):
        """Centre of pad `num` of `ref` in mm (the largest pad, where a footprint has several with one number)."""
        ps = [p for p in self.fps[ref].Pads() if p.GetNumber() == str(num)]
        p = max(ps, key=lambda q: q.GetSize().x * q.GetSize().y)
        return pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)

    def track(self, net, pts, w, layer=pcbnew.F_Cu):
        """A polyline of track segments.  A point is (x, y) or (ref, pad)."""
        pts = [self.pad_xy(*p) if isinstance(p[0], str) else p for p in pts]
        side = 'B' if layer == pcbnew.B_Cu else 'F' if layer == pcbnew.F_Cu else None
        for a, b in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(self.b)
            t.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1]))); t.SetEnd(pcbnew.VECTOR2I(MM(b[0]), MM(b[1])))
            t.SetWidth(MM(w)); t.SetLayer(layer); t.SetNet(self.nets[net])
            self.b.Add(t)
            if side:
                m = w / 2 + 0.15
                self.occupied.append((side, min(a[0], b[0]) - m, min(a[1], b[1]) - m, max(a[0], b[0]) + m, max(a[1], b[1]) + m))

    def via(self, net, x, y, d=0.45, drill=0.2):
        v = pcbnew.PCB_VIA(self.b)
        v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y))); v.SetWidth(pcbnew.F_Cu, MM(d)); v.SetDrill(MM(drill))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(self.nets[net])
        self.b.Add(v)
        m = d / 2 + 0.2
        for sd in ('F', 'B'):
            self.occupied.append((sd, x - m, y - m, x + m, y + m))

    def via_xy(self, net, near):
        """position of the via of `net` nearest to the point `near` (for hooking scripted tracks onto fan-out vias)"""
        vs = [(pcbnew.ToMM(t.GetPosition().x), pcbnew.ToMM(t.GetPosition().y)) for t in self.b.GetTracks()
              if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() == net]
        return min(vs, key=lambda v: (v[0] - near[0]) ** 2 + (v[1] - near[1]) ** 2)

    def fill(self):
        pcbnew.ZONE_FILLER(self.b).Fill(self.b.Zones())

    def unplaced(self):
        return [r for r, f in self.fps.items() if not getattr(f, 'placed', False)]

    def save(self, path=None):
        path = path or os.path.join(self.dir, self.name + '.kicad_pcb')
        pcbnew.SaveBoard(path, self.b)
        # Fill the zones on a reloaded copy (filling the in-memory board crashes pcbnew 9.0.2), so that DRC
        # 'unconnected' counts only what really needs routing.
        b2 = pcbnew.LoadBoard(path)
        pcbnew.ZONE_FILLER(b2).Fill(b2.Zones())
        pcbnew.SaveBoard(path, b2)
        return path


# -------------------------------------------------------------------------------------------------------
def set_project_rules(pro_path, rules, classes, patterns, sheets=None, title=None):
    d = json.load(open(pro_path))
    ds = d['board']['design_settings']
    ds['rules'].update(rules)
    defaults = d['net_settings']['classes'][0]
    out = []
    for c in classes:
        base = dict(defaults)
        base.update(c)
        out.append(base)
    d['net_settings']['classes'] = out
    d['net_settings']['netclass_patterns'] = [{'netclass': nc, 'pattern': p} for (p, nc) in patterns]
    if sheets:
        d['sheets'] = sheets
    # Severity tweaks (documented in hardware/README.md): silkscreen overlaps are cosmetic on a DRAFT board.
    sev = ds.setdefault('rule_severities', {})
    sev.update({'silk_overlap': 'ignore', 'silk_over_copper': 'warning', 'silk_edge_clearance': 'warning',
                'lib_footprint_issues': 'warning', 'lib_footprint_mismatch': 'warning', 'text_height': 'warning',
                'text_thickness': 'warning'})
    json.dump(d, open(pro_path, 'w'), indent=2)


def save_scripted(board_path):
    """record what the generator put on the board (gr_io.Scripted): call after save(), before the first routing pass"""
    subprocess.run(['python3', os.path.join(HERE, 'gr_io.py'), 'save_scripted', board_path], check=True)


def finish_routing(board, route_args, clearances, rounds=10):
    """Close the loop with KiCad's own check, after the plain gridroute passes.

    Each round: run the design-rule check; take up the routed segments and vias it objects to; route what is open,
    allowing the router to take up its earlier work (--reroute).  The clearance alternates between the given values.
    When a round changes nothing, everything routed within 1.5 mm (then 3, 4.5 ...) of the open ends is taken up and
    those connections are routed first.  Ends when the check is quiet or the rounds are used up.  Then a tidy pass
    removes unused vias and dead ends, undone per net if it would open a connection.
    """
    import json
    import re
    import shutil
    import tempfile
    gr_io = os.path.join(HERE, 'gr_io.py')
    bdir, name = os.path.dirname(board), os.path.basename(board)[:-len('.kicad_pcb')]

    def check():
        drc = os.path.join(tempfile.mkdtemp(), 'drc.json')
        subprocess.run(['kicad-cli', 'pcb', 'drc', '--format', 'json', '-o', drc, board], check=True, capture_output=True)
        d = json.load(open(drc))
        return drc, d, (sum(v['severity'] == 'error' for v in d['violations']), len(d['unconnected_items']))
    nets = lambda d: sorted({m.group(1) for u in d['unconnected_items'] for it in u['items']
                             for m in [re.search(r'\[(.*?)\]', it['description'])] if m})
    last, stuck = None, 0
    for i in range(rounds):
        drc, d, state = check()
        print('repair round', i, 'errors, open:', state, flush=True)
        if state == (0, 0):
            break
        stuck = stuck + 1 if state == last else 0
        last = state
        subprocess.run(['python3', gr_io, 'ripdrc', board, drc], check=True)
        extra = []
        if stuck:
            subprocess.run(['python3', gr_io, 'ripnear', board, drc, str(1.5 * stuck)], check=True)
            extra = ['--first', ','.join(nets(d))]
        subprocess.run([os.path.join(HERE, 'gridroute.sh'), bdir, name] + route_args +
                       ['--clearance', str(clearances[i % len(clearances)]), '--reroute'] + extra, check=True)
    skip = set()                                   # nets where removing a "dangling" item opened a connection
    for i in range(6):
        drc, d, state = check()
        n = sum(v['type'] in ('via_dangling', 'track_dangling') and not any(f'[{s_}]' in v['items'][0]['description'] for s_ in skip)
                for v in d['violations'])
        if not n:
            break
        shutil.copy(board, board + '.pretidy')
        subprocess.run(['python3', gr_io, 'tidy', board, drc, ','.join(sorted(skip))], check=True)
        _, d2, state2 = check()
        if state2[1] > state[1] or state2[0] > state[0]:
            opened = set(nets(d2))
            shutil.copy(board + '.pretidy', board)
            print('tidy: undone for', sorted(opened), flush=True)
            if not opened or opened <= skip:
                break
            skip |= opened
    if os.path.exists(board + '.pretidy'):
        os.remove(board + '.pretidy')
    return check()[2]


def route(board_path, passes=20, timeout=3600, jar=None):
    """Export DSN, run Freerouting headless, import the SES back. Returns Freerouting's log tail."""
    jar = jar or os.environ['FREEROUTING_JAR']   # path to freerouting-2.1.0.jar (2.1.0 runs on Java 21)
    b = pcbnew.LoadBoard(board_path)
    dsn = board_path.replace('.kicad_pcb', '.dsn')
    ses = board_path.replace('.kicad_pcb', '.ses')
    pcbnew.ExportSpecctraDSN(b, dsn)
    cmd = ['java', '-Xmx3g', '-Djava.awt.headless=true', '-jar', jar, '--gui.enabled=false', '-de', dsn, '-do', ses,
           '-mp', str(passes)]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    log = (p.stdout + p.stderr)[-3000:]
    if os.path.exists(ses):
        pcbnew.ImportSpecctraSES(b, ses)
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        pcbnew.SaveBoard(board_path, b)
    for f in (dsn, ses):
        if os.path.exists(f):
            os.remove(f)
    return log
