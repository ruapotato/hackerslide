"""kigen: generate KiCad 9 schematics (+ a netlist for the PCB step) from a Python netlist.

Why generated: the HackerSlide boards are described as code (hardware/scripts/<board>_design.py) so a
reviewer can read every connection in one place, diffs stay readable, and the schematic and PCB can never
drift apart.  The generated schematic is a real, editable KiCad schematic: every pin gets a global label with
its net name (the "label on every pin" style).  Once a human takes over a board in the KiCad GUI, stop
regenerating it and edit the KiCad files directly (see hardware/README.md).

Coordinates: KiCad symbol space is Y-up, schematic space is Y-down; all placement is on a 2.54 mm grid.
"""
import json
import os
import re
import uuid as uuidlib

import sexpr
from sexpr import Q, find, findall

KICAD_SYM_DIR = os.environ.get('KICAD9_SYMBOL_DIR', '/usr/share/kicad/symbols')
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_LIB = os.path.join(HERE, '..', 'lib', 'hackerslide.kicad_sym')
GRID = 2.54

_NS = uuidlib.UUID('6b1f3c2e-8f0a-4d6e-9a51-48a5c0de8101')


def uid(*parts):
    """Deterministic UUID so regenerating a board does not churn every file."""
    return str(uuidlib.uuid5(_NS, '/'.join(str(p) for p in parts)))


def snap(v, g=GRID):
    return round(v / g) * g


# ----------------------------------------------------------------------------------------------------------
# symbol libraries
_libcache = {}


def _load_lib(lib):
    if lib not in _libcache:
        path = PROJECT_LIB if lib == 'hackerslide' else os.path.join(KICAD_SYM_DIR, lib + '.kicad_sym')
        tree = sexpr.parse(open(path).read())
        _libcache[lib] = {s[1]: s for s in findall(tree, 'symbol')}
    return _libcache[lib]


def _deepcopy(n):
    if isinstance(n, list):
        return [_deepcopy(x) for x in n]
    return n


def get_symbol(lib, name):
    """Return a flattened copy of a library symbol (resolves `extends`)."""
    syms = _load_lib(lib)
    node = _deepcopy(syms[name])
    ext = find(node, 'extends')
    if ext:
        parent = get_symbol(lib, ext[1])
        child_props = {p[1]: p for p in findall(node, 'property')}
        out = [node[0], Q(name)]
        for item in parent[2:]:
            if isinstance(item, list) and item[0] == 'property' and item[1] in child_props:
                out.append(child_props.pop(item[1]))
            elif isinstance(item, list) and item[0] == 'symbol':
                item[1] = Q(re.sub('^' + re.escape(ext[1]) + '_', name + '_', item[1]))
                out.append(item)
            else:
                out.append(item)
        for p in child_props.values():
            out.insert(2, p)
        node = out
    return node


def sym_pins(node):
    """[(unit, number, name, etype, x, y, angle, hidden)] for body style 1 (or 0)."""
    name = node[1]
    pins = []
    for sub in findall(node, 'symbol'):
        m = re.match(re.escape(name) + r'_(\d+)_(\d+)$', sub[1])
        if not m:
            continue
        unit, style = int(m.group(1)), int(m.group(2))
        if style not in (0, 1):
            continue
        for p in findall(sub, 'pin'):
            at = find(p, 'at')
            hidden = any(x == 'hide' or (isinstance(x, list) and x[:2] == ['hide', 'yes']) for x in p)
            pins.append((unit, str(find(p, 'number')[1]), str(find(p, 'name')[1]), p[1],
                         float(at[1]), float(at[2]), float(at[3]) if len(at) > 3 else 0.0, hidden))
    return pins


def sym_units(node):
    units = {u for (u, *_r) in sym_pins(node) if u > 0}
    return sorted(units) or [1]


def sym_bbox(node, unit):
    xs, ys = [0.0], [0.0]
    name = node[1]
    for sub in findall(node, 'symbol'):
        m = re.match(re.escape(name) + r'_(\d+)_(\d+)$', sub[1])
        if not m or int(m.group(1)) not in (0, unit):
            continue
        for g in sub[2:]:
            if not isinstance(g, list):
                continue
            for k in ('start', 'end', 'center', 'mid'):
                e = find(g, k)
                if e:
                    xs.append(float(e[1]))
                    ys.append(float(e[2]))
            pts = find(g, 'pts')
            if pts:
                for xy in findall(pts, 'xy'):
                    xs.append(float(xy[1]))
                    ys.append(float(xy[2]))
            if g[0] == 'pin':
                at = find(g, 'at')
                xs.append(float(at[1]))
                ys.append(float(at[2]))
    return min(xs), min(ys), max(xs), max(ys)


# ----------------------------------------------------------------------------------------------------------
class Part:
    def __init__(self, sheet, ref, lib, sym, value, footprint, nets, fields=None, dnp=False, unit_pos=None, in_bom=None):
        self.sheet, self.ref, self.lib, self.sym = sheet, ref, lib, sym
        self.in_bom = (sym != 'TestPoint') if in_bom is None else in_bom
        self.value, self.footprint, self.dnp = value, footprint, dnp
        self.nets = {str(k): v for k, v in nets.items()}
        self.fields = fields or {}
        self.node = get_symbol(lib, sym)
        self.pins = sym_pins(self.node)
        self.uuid = uid(sheet.design.name, sheet.name, ref)
        self.pos = {}
        numbers = {p[1] for p in self.pins}
        bad = set(self.nets) - numbers
        if bad:
            raise ValueError(f'{ref}: pins {sorted(bad)} not in symbol {lib}:{sym} (has {sorted(numbers)[:12]}...)')

    @property
    def lib_id(self):
        return f'{self.lib}:{self.sym}'


class Sheet:
    def __init__(self, design, name, title, paper='A3', notes=()):
        self.design, self.name, self.title, self.paper = design, name, title, paper
        self.notes = list(notes)
        self.parts = []
        self.uuid = uid(design.name, 'sheet', name)
        self.file = name + '.kicad_sch'
        self.flags = []

    def add(self, ref, lib, sym, value, footprint, nets, **kw):
        p = Part(self, ref, lib, sym, value, footprint, nets, **kw)
        self.parts.append(p)
        self.design.parts.append(p)
        return p


class Design:
    def __init__(self, name, title, rev='0.1', company='HackerSlide project (AGPL-3.0)', comments=()):
        self.name, self.title, self.rev, self.company = name, title, rev, company
        self.comments = list(comments)
        self.sheets = []
        self.parts = []
        self.root_uuid = uid(name, 'root')

    def sheet(self, name, title, **kw):
        s = Sheet(self, name, title, **kw)
        self.sheets.append(s)
        return s

    # ------------------------------------------------------------------------------------------------------
    def nets(self):
        out = {}
        for p in self.parts:
            for (unit, num, pname, etype, *_r) in p.pins:
                net = p.nets.get(num)
                if net:
                    out.setdefault(net, []).append((p.ref, num, etype))
        return out

    def check(self):
        problems = []
        for net, conns in sorted(self.nets().items()):
            if len(conns) < 2 and not net.startswith('TP_'):
                problems.append(f'net {net} has only one connection: {conns}')
        refs = [p.ref for p in self.parts]
        dup = {r for r in refs if refs.count(r) > 1}
        if dup:
            problems.append(f'duplicate refs {sorted(dup)}')
        return problems

    # ------------------------------------------------------------------------------------------------------
    def write(self, outdir):
        os.makedirs(outdir, exist_ok=True)
        nets = self.nets()
        # PWR_FLAG on nets that have power inputs but nothing that drives them
        flagged = set()
        for net, conns in sorted(nets.items()):
            types = {c[2] for c in conns}
            if 'power_in' in types and 'power_out' not in types:
                first = next(p for p in self.parts if net in p.nets.values())
                first.sheet.flags.append(net)
                flagged.add(net)
        for s in self.sheets:
            self._write_sheet(s, outdir)
        self._write_root(outdir)
        self._write_project(outdir)
        self._write_netlist(outdir)
        return flagged

    def _paper_size(self, paper):
        return {'A4': (297, 210), 'A3': (420, 297), 'A2': (594, 420), 'A1': (841, 594)}[paper]

    def _layout(self, sheet):
        """Place every unit of every part in rows; returns list of (part, unit, x, y)."""
        W, H = self._paper_size(sheet.paper)
        x0, y0 = 20.32, 40.64
        x, y, rowh = x0, y0, 0
        placed = []
        items = []
        for p in sheet.parts:
            for u in sym_units(p.node):
                items.append((p, u))
        for net in sheet.flags:
            items.append(('FLAG', net))
        for it in items:
            if it[0] == 'FLAG':
                w, h, ox, oy = 25.4, 12.7, 12.7, 2.54
            else:
                p, u = it
                bx0, by0, bx1, by1 = sym_bbox(p.node, u)
                lab = 3.0 + max([len(str(p.nets.get(pp[1]) or '')) for pp in p.pins if pp[0] in (0, u)] + [2]) * 1.05
                left = lab if any(pp[6] == 0 for pp in p.pins if pp[0] in (0, u)) else 4
                right = lab if any(pp[6] == 180 for pp in p.pins if pp[0] in (0, u)) else 4
                top = lab if any(pp[6] == 270 for pp in p.pins if pp[0] in (0, u)) else 5
                bot = lab if any(pp[6] == 90 for pp in p.pins if pp[0] in (0, u)) else 5
                w = (bx1 - bx0) + left + right + 5
                h = (by1 - by0) + top + bot + 5
                ox, oy = left - bx0, top + by1     # symbol origin offset inside its cell (schematic coords)
            if x + w > W - 15 and x > x0:
                x, y, rowh = x0, y + rowh, 0
            placed.append((it, snap(x + ox), snap(y + oy)))
            x += w
            rowh = max(rowh, h)
        if y + rowh > H - 35:
            raise OverflowError(f'sheet {sheet.name} does not fit on {sheet.paper}')
        return placed

    def _write_sheet(self, sheet, outdir):
        W, H = self._paper_size(sheet.paper)
        placed = self._layout(sheet)
        out = []
        libsyms = {}
        path = f'/{self.root_uuid}/{sheet.uuid}'
        for (it, X, Y) in placed:
            if it[0] == 'FLAG':
                net = it[1]
                node = get_symbol('power', 'PWR_FLAG')
                libsyms['power:PWR_FLAG'] = node
                u = uid(self.name, sheet.name, 'flag', net)
                self._flg = getattr(self, '_flg', 0) + 1
                out.append(self._symbol_inst('power:PWR_FLAG', f'#FLG{self._flg:03d}', 'PWR_FLAG', '', X, Y, 1,
                                             u, ['1'], path, dnp=False, hide_ref=True))
                out.append(self._label(net, X, Y, 270))
                continue
            p, unit = it
            libsyms[p.lib_id] = p.node
            pins = [pp for pp in p.pins if pp[0] in (0, unit)]
            out.append(self._symbol_inst(p.lib_id, p.ref, p.value, p.footprint, X, Y, unit, uid(p.uuid, unit),
                                         [pp[1] for pp in pins], path, fields=p.fields, dnp=p.dnp, in_bom=p.in_bom))
            for (u_, num, pname, etype, px, py, pa, hidden) in pins:
                ax, ay = X + px, Y - py
                net = p.nets.get(num)
                if net:
                    out.append(self._label(net, ax, ay, (pa + 180) % 360))
                elif etype != 'no_connect':
                    out.append(f'\t(no_connect (at {sexpr.fmt(ax)} {sexpr.fmt(ay)}) (uuid "{uid(p.uuid, "nc", num)}"))')
        # notes block
        ty = 15.24
        out.append(self._text(sheet.title, 15.24, ty, 3.0))
        for i, n in enumerate(sheet.notes):
            out.append(self._text(n, 15.24, ty + 6 + i * 4.2, 1.6))
        lib_block = '\t(lib_symbols\n' + ''.join(
            '\t\t' + sexpr.dump(self._embed(k, v), 2) + '\n' for k, v in sorted(libsyms.items())) + '\t)\n'
        text = (f'(kicad_sch\n\t(version 20250114)\n\t(generator "eeschema")\n\t(generator_version "9.0")\n'
                f'\t(uuid "{uid(self.name, "file", sheet.name)}")\n\t(paper "{sheet.paper}")\n'
                + self._title_block(sheet.title) + lib_block + '\n'.join(out) + '\n\t(embedded_fonts no)\n)\n')
        open(os.path.join(outdir, sheet.file), 'w').write(text)

    def _embed(self, lib_id, node):
        n = _deepcopy(node)
        n[1] = Q(lib_id)
        return n

    def _title_block(self, title):
        c = ''.join(f'\t\t(comment {i + 1} {sexpr.quote(t)})\n' for i, t in enumerate(self.comments[:4]))
        return (f'\t(title_block\n\t\t(title {sexpr.quote(self.title + " - " + title)})\n\t\t(rev {sexpr.quote(self.rev)})\n'
                f'\t\t(company {sexpr.quote(self.company)})\n{c}\t)\n')

    def _text(self, s, x, y, size):
        return (f'\t(text {sexpr.quote(s)} (exclude_from_sim no) (at {sexpr.fmt(x)} {sexpr.fmt(y)} 0) '
                f'(effects (font (size {size} {size})) (justify left bottom)) (uuid "{uid(self.name, "txt", s, x, y)}"))')

    def _label(self, net, x, y, ang):
        ang = int(ang) % 360
        just = {0: 'left', 180: 'right', 90: 'left', 270: 'right'}[ang]
        return (f'\t(global_label {sexpr.quote(net)} (shape bidirectional) (at {sexpr.fmt(x)} {sexpr.fmt(y)} {ang}) '
                f'(fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify {just})) '
                f'(uuid "{uid(self.name, "lbl", net, round(x, 2), round(y, 2))}") '
                f'(property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {sexpr.fmt(x)} {sexpr.fmt(y)} 0) '
                f'(effects (font (size 1.27 1.27)) (hide yes))))')

    def _symbol_inst(self, lib_id, ref, value, fp, X, Y, unit, u, pinnums, path, fields=None, dnp=False,
                     hide_ref=False, in_bom=True):
        f = lambda v: sexpr.fmt(v)
        props = [('Reference', ref, X + 2.54, Y - 3.81, hide_ref), ('Value', value, X + 2.54, Y + 3.81, False),
                 ('Footprint', fp, X, Y, True), ('Datasheet', (fields or {}).get('Datasheet', '~'), X, Y, True),
                 ('Description', (fields or {}).get('Description', ''), X, Y, True)]
        for k, v in (fields or {}).items():
            if k not in ('Datasheet', 'Description'):
                props.append((k, v, X, Y, True))
        ps = ''.join(f'\t\t(property {sexpr.quote(k)} {sexpr.quote(v)} (at {f(x)} {f(y)} 0) (effects (font (size 1.27 1.27))'
                     f'{" (hide yes)" if h else ""}))\n' for (k, v, x, y, h) in props)
        pins = ''.join(f'\t\t(pin {sexpr.quote(n)} (uuid "{uid(u, "pin", n)}"))\n' for n in pinnums)
        return (f'\t(symbol (lib_id {sexpr.quote(lib_id)}) (at {f(X)} {f(Y)} 0) (unit {unit}) (exclude_from_sim no) '
                f'(in_bom {"no" if lib_id.startswith("power:") or not in_bom else "yes"}) (on_board {"no" if lib_id.startswith("power:") else "yes"}) '
                f'(dnp {"yes" if dnp else "no"}) (uuid "{u}")\n{ps}{pins}'
                f'\t\t(instances (project {sexpr.quote(self.name)} (path "{path}" (reference {sexpr.quote(ref)}) (unit {unit}))))\n\t)')

    def _write_root(self, outdir):
        blocks = []
        x, y = 25.4, 50.8
        for i, s in enumerate(self.sheets):
            blocks.append(
                f'\t(sheet (at {x} {y}) (size 50.8 20.32) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) '
                f'(fields_autoplaced yes) (stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0.0000)) (uuid "{s.uuid}")\n'
                f'\t\t(property "Sheetname" {sexpr.quote(s.name)} (at {x} {y - 0.7} 0) (effects (font (size 1.27 1.27)) (justify left bottom)))\n'
                f'\t\t(property "Sheetfile" {sexpr.quote(s.file)} (at {x} {y + 21} 0) (effects (font (size 1.27 1.27)) (justify left top)))\n'
                f'\t\t(instances (project {sexpr.quote(self.name)} (path "/{self.root_uuid}" (page "{i + 2}"))))\n\t)')
            x += 63.5
            if x > 330:
                x, y = 25.4, y + 38.1
        notes = [self._text(self.title, 25.4, 25.4, 4.0)]
        for i, c in enumerate(self.comments):
            notes.append(self._text(c, 25.4, 32 + i * 4.5, 1.8))
        text = (f'(kicad_sch\n\t(version 20250114)\n\t(generator "eeschema")\n\t(generator_version "9.0")\n'
                f'\t(uuid "{self.root_uuid}")\n\t(paper "A3")\n' + self._title_block('overview') +
                '\t(lib_symbols)\n' + '\n'.join(notes + blocks) +
                '\n\t(sheet_instances (path "/" (page "1")))\n\t(embedded_fonts no)\n)\n')
        open(os.path.join(outdir, self.name + '.kicad_sch'), 'w').write(text)

    def _write_project(self, outdir):
        pro = os.path.join(outdir, self.name + '.kicad_pro')
        data = {}
        if os.path.exists(pro):
            data = json.load(open(pro))
        data.setdefault('meta', {'filename': self.name + '.kicad_pro', 'version': 3})
        data['sheets'] = [[self.root_uuid, 'Root']] + [[s.uuid, s.name] for s in self.sheets]
        json.dump(data, open(pro, 'w'), indent=2)
        libdir = '${KIPRJMOD}/../lib'
        sym_libs = sorted({p.lib for p in self.parts} | {'power'})
        rows = []
        for l in sym_libs:
            uri = f'{libdir}/hackerslide.kicad_sym' if l == 'hackerslide' else f'${{KICAD9_SYMBOL_DIR}}/{l}.kicad_sym'
            rows.append(f'  (lib (name "{l}")(type "KiCad")(uri "{uri}")(options "")(descr ""))')
        open(os.path.join(outdir, 'sym-lib-table'), 'w').write('(sym_lib_table\n  (version 7)\n' + '\n'.join(rows) + '\n)\n')
        fp_libs = sorted({p.footprint.split(':')[0] for p in self.parts if p.footprint})
        rows = []
        for l in fp_libs:
            uri = f'{libdir}/hackerslide.pretty' if l == 'hackerslide' else f'${{KICAD9_FOOTPRINT_DIR}}/{l}.pretty'
            rows.append(f'  (lib (name "{l}")(type "KiCad")(uri "{uri}")(options "")(descr ""))')
        open(os.path.join(outdir, 'fp-lib-table'), 'w').write('(fp_lib_table\n  (version 7)\n' + '\n'.join(rows) + '\n)\n')

    def _write_netlist(self, outdir):
        comps = []
        for p in self.parts:
            comps.append({'ref': p.ref, 'value': p.value, 'footprint': p.footprint, 'dnp': p.dnp,
                          'sheet': p.sheet.name, 'sheet_uuid': p.sheet.uuid, 'sheetfile': p.sheet.file,
                          'sym_uuid': uid(p.uuid, sym_units(p.node)[0]),
                          'fields': p.fields, 'pads': p.nets, 'in_bom': p.in_bom,
                          'nc': {pp[1]: 'unconnected-(%s-%s-Pad%s)' % (p.ref, (pp[2] if pp[2] != '~' else '').replace(' ', '_'), pp[1])
                                 for pp in p.pins if not p.nets.get(pp[1])}})
        json.dump({'name': self.name, 'components': comps}, open(os.path.join(outdir, 'netlist.json'), 'w'), indent=1)
