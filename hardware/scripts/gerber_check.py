"""Compare the fabrication files of one board with the board file, using a Gerber reader that is not KiCad's.

  VENV=/path/to/venv python3 gerber_check.py BOARD.kicad_pcb FAB_DIR      (system python: pcbnew, numpy, Pillow;
                                                                           the venv needs pygerber 2.x)

FAB_DIR is the output of fab_outputs.sh.  Checks, each printed as one table row:
  copper   every copper Gerber is drawn by pygerber and laid over a picture of the same layer drawn here from the
           board file (pads, tracks, vias, zone fills); the area that differs is reported
  drill    every hole in the Excellon files is a pad or via hole of the board with the same diameter, and the reverse;
           every plated hole is surrounded by copper on both outer layers of the Gerbers
  mask     every pad that should be bare is open in the mask Gerber
  paste    every pad that should get paste has it, and nothing without a pad gets paste
  outline  the Edge.Cuts Gerber has the board's size
Exit status 1 if any check fails.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

import numpy as np
import pcbnew
from PIL import Image, ImageDraw

Image.MAX_IMAGE_PIXELS = None
DPMM = 40
T = pcbnew.ToMM
RENDER = r'''
import json, sys
from pygerber.gerberx3.api.v2 import GerberFile, ColorScheme
from pygerber.common.rgba import RGBA
W, K = RGBA.from_rgba(255, 255, 255, 255), RGBA.from_rgba(0, 0, 0, 255)
cs = ColorScheme(background_color=K, clear_color=K, solid_color=W, clear_region_color=K, solid_region_color=W)
out = {}
for src, dst in zip(sys.argv[2::2], sys.argv[3::2]):
    p = GerberFile.from_file(src).parse()
    i = p.get_info()
    p.render_raster(dst, dpmm=int(sys.argv[1]), color_scheme=cs)
    out[src] = [float(i.min_x_mm), float(i.min_y_mm), float(i.max_x_mm), float(i.max_y_mm)]
print(json.dumps(out))
'''


def canvas(w, h):
    return Image.new('1', (int(w * DPMM) + 2, int(h * DPMM) + 2), 0)


def poly(dr, sps, x0, y0):
    for i in range(sps.OutlineCount()):
        o = sps.Outline(i)
        dr.polygon([((T(o.CPoint(j).x) - x0) * DPMM, (T(o.CPoint(j).y) - y0) * DPMM) for j in range(o.PointCount())], fill=1)
        for h in range(sps.HoleCount(i)):
            ho = sps.Hole(i, h)
            dr.polygon([((T(ho.CPoint(j).x) - x0) * DPMM, (T(ho.CPoint(j).y) - y0) * DPMM) for j in range(ho.PointCount())], fill=0)


def reference(b, layer, x0, y0, w, h):
    """the copper of one layer drawn from the board file"""
    im = canvas(w, h)
    dr = ImageDraw.Draw(im)
    for z in b.Zones():
        if not z.GetIsRuleArea() and z.IsOnLayer(layer):
            poly(dr, z.GetFilledPolysList(layer), x0, y0)
    for t in b.GetTracks():
        if t.GetClass() == 'PCB_VIA':
            if t.IsOnLayer(layer):
                r = T(t.GetWidth(layer)) / 2 * DPMM
                cx, cy = (T(t.GetPosition().x) - x0) * DPMM, (T(t.GetPosition().y) - y0) * DPMM
                dr.ellipse((cx - r, cy - r, cx + r, cy + r), fill=1)
        elif t.GetLayer() == layer:
            r = T(t.GetWidth()) / 2 * DPMM
            a = ((T(t.GetStart().x) - x0) * DPMM, (T(t.GetStart().y) - y0) * DPMM)
            c = ((T(t.GetEnd().x) - x0) * DPMM, (T(t.GetEnd().y) - y0) * DPMM)
            dr.line((a, c), fill=1, width=max(1, int(round(2 * r))))
            for p in (a, c):
                dr.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=1)
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.IsOnLayer(layer) and p.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH:
                sps = pcbnew.SHAPE_POLY_SET()
                p.TransformShapeToPolygon(sps, layer, 0, pcbnew.FromMM(0.005), pcbnew.ERROR_INSIDE)
                poly(dr, sps, x0, y0)
    return np.array(im, bool)


def holes(b):
    out = []
    for t in b.GetTracks():
        if t.GetClass() == 'PCB_VIA':
            out.append((T(t.GetPosition().x), T(t.GetPosition().y), T(t.GetDrillValue()), True))
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.GetDrillSize().x:
                out.append((T(p.GetPosition().x), T(p.GetPosition().y), T(p.GetDrillSize().x),
                            p.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH, T(p.GetDrillSize().y)))
    return [h[:4] for h in out]


def excellon(path):
    tools, cur, hits = {}, None, []
    for line in open(path):
        line = line.strip()
        m = re.match(r'T(\d+)C([\d.]+)', line)
        if m:
            tools[m.group(1)] = float(m.group(2))
            continue
        m = re.match(r'T(\d+)$', line)
        if m:
            cur = tools.get(m.group(1))
            continue
        m = re.match(r'X(-?[\d.]+)Y(-?[\d.]+)(?:G85X(-?[\d.]+)Y(-?[\d.]+))?', line)
        if m and cur:
            x, y = float(m.group(1)), -float(m.group(2))
            if m.group(3):                      # a slot: the board file gives its centre
                x, y = (x + float(m.group(3))) / 2, (y - float(m.group(4))) / 2
            hits.append((x, y, cur))
    return hits


def place(img, ext, x0, y0, w, h):
    """a pygerber picture put into the board frame (Gerber y points up, the plot origin is the page origin)"""
    a = np.array(Image.open(img).convert('L')) > 127
    out = np.zeros((int(h * DPMM) + 2, int(w * DPMM) + 2), bool)
    px, py = int(round((ext[0] - x0) * DPMM)), int(round((-ext[3] - y0) * DPMM))
    sy, sx = max(0, -py), max(0, -px)
    hh, ww = min(a.shape[0] - sy, out.shape[0] - max(py, 0)), min(a.shape[1] - sx, out.shape[1] - max(px, 0))
    out[max(py, 0):max(py, 0) + hh, max(px, 0):max(px, 0) + ww] = a[sy:sy + hh, sx:sx + ww]
    return out


def main(board, fab):
    b = pcbnew.LoadBoard(board)
    name = os.path.splitext(os.path.basename(board))[0]
    bb = b.GetBoardEdgesBoundingBox()
    x0, y0 = T(bb.GetLeft()) - 1, T(bb.GetTop()) - 1
    w, h = T(bb.GetWidth()) + 2, T(bb.GetHeight()) + 2
    cu = [l for l in b.GetEnabledLayers().CuStack()]
    files = {b.GetLayerName(l): os.path.join(fab, f'{name}-{b.GetLayerName(l).replace(".", "_")}.gbr') for l in cu}
    for n, f in (('F.Mask', 'F_Mask'), ('B.Mask', 'B_Mask'), ('F.Paste', 'F_Paste'), ('B.Paste', 'B_Paste'), ('Edge.Cuts', 'Edge_Cuts')):
        files[n] = os.path.join(fab, f'{name}-{f}.gbr')
    ok = True
    print('| Check | Result |')
    print('|---|---|')
    with tempfile.TemporaryDirectory() as d:
        args = []
        for n, f in files.items():
            args += [f, os.path.join(d, n + '.png')]
        venv = os.environ.get('VENV', os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../.venv'))
        r = subprocess.run([os.path.join(venv, 'bin/python'), '-c', RENDER, str(DPMM)] + args, capture_output=True, text=True)
        if r.returncode:
            print(r.stderr[-2000:])
            sys.exit(2)
        ext = json.loads(r.stdout.strip().splitlines()[-1])
        g = {n: place(os.path.join(d, n + '.png'), ext[f], x0, y0, w, h) for n, f in files.items()}
    # copper
    for l in cu:
        n = b.GetLayerName(l)
        ref = reference(b, l, x0, y0, w, h)
        diff = ref ^ g[n]
        # rims one or two pixels wide (0.05 mm) along edges are rasterising, not a difference: count only what
        # survives two erosions, that is anything at least 0.125 mm across
        core = diff
        for _ in range(2):
            core = core[1:-1, 1:-1] & core[:-2, 1:-1] & core[2:, 1:-1] & core[1:-1, :-2] & core[1:-1, 2:]
        mm2 = core.sum() / DPMM ** 2
        good = mm2 < 0.05
        ok &= good
        print(f'| copper {n} | Gerber {g[n].sum() / DPMM ** 2:.0f} mm2, board file {ref.sum() / DPMM ** 2:.0f} mm2, '
              f'differing {mm2:.2f} mm2: {"same" if good else "**DIFFERENT**"} |')
    # drill
    want = holes(b)
    hits = [(x, y, dd, True) for x, y, dd in excellon(os.path.join(fab, name + '-PTH.drl'))]
    hits += [(x, y, dd, False) for x, y, dd in excellon(os.path.join(fab, name + '-NPTH.drl'))]
    same = lambda p, q: abs(p[0] - q[0]) < 0.01 and abs(p[1] - q[1]) < 0.01 and abs(p[2] - q[2]) < 0.005 and p[3] == q[3]
    only_files = [q for q in hits if not any(same(q, p) for p in want)]
    only_board = [p for p in want if not any(same(p, q) for q in hits)]
    good = not only_files and not only_board and len(want) == len(hits)
    ok &= good
    sizes = sorted({q[2] for q in hits})
    print(f'| drill | {len(hits)} holes in the files ({sum(q[3] for q in hits)} plated), {len(want)} on the board; '
          f'sizes {", ".join("%.2f" % s for s in sizes)} mm; only in files {len(only_files)}, only on board {len(only_board)}: '
          f'{"same" if good else "**DIFFERENT**"} |')
    outer = (b.GetLayerName(cu[0]), b.GetLayerName(cu[-1]))
    bad = 0
    for x, y, dd, plated in hits:
        if not plated:
            continue
        for n in outer:
            ring = [g[n][int(round((y - y0 + (dd / 2 + 0.06) * sy_) * DPMM)), int(round((x - x0 + (dd / 2 + 0.06) * sx_) * DPMM))]
                    for sx_, sy_ in ((1, 0), (-1, 0), (0, 1), (0, -1), (0.7, 0.7), (-0.7, 0.7), (0.7, -0.7), (-0.7, -0.7))]
            bad += not all(ring)
    ok &= bad == 0
    print(f'| annular ring | plated holes without copper all round on an outer layer: {bad} |')
    # mask and paste
    for side, cu_l, mask, paste in (('F', pcbnew.F_Cu, pcbnew.F_Mask, pcbnew.F_Paste), ('B', pcbnew.B_Cu, pcbnew.B_Mask, pcbnew.B_Paste)):
        pads = [p for f in b.GetFootprints() for p in f.Pads()]
        at = lambda p, a: a[int(round((T(p.GetPosition().y) - y0) * DPMM)), int(round((T(p.GetPosition().x) - x0) * DPMM))]
        solid = lambda p: not p.GetDrillSize().x
        m_bad = [p for p in pads if p.IsOnLayer(mask) and solid(p) and not at(p, g[side + '.Mask'])]
        p_miss = [p for p in pads if p.IsOnLayer(paste) and solid(p) and not at(p, g[side + '.Paste'])]
        ref = np.zeros_like(g[side + '.Paste'])
        im = Image.fromarray(ref)
        dr = ImageDraw.Draw(im)
        for p in pads:
            if p.IsOnLayer(paste):
                sps = pcbnew.SHAPE_POLY_SET()
                p.TransformShapeToPolygon(sps, cu_l, pcbnew.FromMM(0.05), pcbnew.FromMM(0.005), pcbnew.ERROR_INSIDE)
                poly(dr, sps, x0, y0)
        stray = (g[side + '.Paste'] & ~np.array(im, bool)).sum() / DPMM ** 2
        good = not m_bad and not p_miss and stray < 0.05
        ok &= good
        print(f'| mask and paste {side} | pads not open in the mask: {len(m_bad)}; pads missing paste: {len(p_miss)}; '
              f'paste outside pads: {stray:.2f} mm2; pads with paste: {sum(1 for p in pads if p.IsOnLayer(paste))} |')
    # outline
    e = ext[files['Edge.Cuts']]
    gw, gh = e[2] - e[0], e[3] - e[1]
    good = abs(gw - T(bb.GetWidth())) < 0.11 and abs(gh - T(bb.GetHeight())) < 0.11
    ok &= good
    print(f'| outline | Gerber {gw:.2f} x {gh:.2f} mm, board {T(bb.GetWidth()):.2f} x {T(bb.GetHeight()):.2f} mm (both include the line width) |')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
