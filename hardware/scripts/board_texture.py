"""Top and bottom pictures of a board for the 3D renders: solder mask over copper, gold where the mask is open,
silkscreen on top.

  python3 board_texture.py BOARD.kicad_pcb OUT_PREFIX [mask]      (system python: pcbnew, Pillow, numpy; kicad-cli,
                                                                   rsvg-convert)
Writes OUT_PREFIX-top.png and OUT_PREFIX-bottom.png, PPM pixels per mm, covering exactly the board outline's
bounding box, both as seen from the TOP (the bottom picture is not mirrored: the renderer maps both by board x/y).
Also OUT_PREFIX.json with the box in board coordinates.  mask: green (default), black, or flex.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

import numpy as np
import pcbnew
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
PPM = 40
LOOK = {   # mask over bare board, mask over copper, bare board in a mask opening, silkscreen
    'green': ((14, 74, 40), (30, 112, 62), (150, 135, 95), (238, 238, 232)),
    'black': ((16, 17, 19), (38, 40, 44), (120, 110, 85), (235, 235, 230)),
    'flex': ((190, 120, 30), (215, 150, 50), (190, 120, 30), (240, 240, 235)),
}
GOLD = (214, 172, 78)
T = pcbnew.ToMM


def layer(board, name, d):
    svg = os.path.join(d, 'l.svg')
    png = os.path.join(d, 'l.png')
    subprocess.run(['kicad-cli', 'pcb', 'export', 'svg', '--layers', name, '--exclude-drawing-sheet', '--page-size-mode', '2',
                    '--black-and-white', '-o', svg, board], check=True, capture_output=True)
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', open(svg).read(4000)).group(1).split()]
    subprocess.run(['rsvg-convert', '-w', str(int(round(vb[2] * PPM))), '-b', 'white', svg, '-o', png], check=True)
    return np.asarray(Image.open(png).convert('L')) < 128, vb


def main(path, prefix, look='green'):
    b = pcbnew.LoadBoard(path)
    e = b.GetBoardEdgesBoundingBox()
    box = b.ComputeBoundingBox(False)
    x0, y0, x1, y1 = T(e.GetLeft()), T(e.GetTop()), T(e.GetRight()), T(e.GetBottom())
    base, over_cu, bare, silk_c = LOOK[look]
    with tempfile.TemporaryDirectory() as d:
        for side, tag in (('F', 'top'), ('B', 'bottom')):
            cu, vb = layer(path, f'{side}.Cu', d)
            mask, _ = layer(path, f'{side}.Mask', d)
            silk, _ = layer(path, f'{side}.SilkS', d)
            img = np.empty(cu.shape + (3,), np.uint8)
            img[:] = base
            img[cu] = over_cu
            img[mask] = bare
            img[mask & cu] = GOLD
            img[silk & ~mask] = silk_c
            px = lambda x: int(round((x - vb[0] - T(box.GetLeft())) * PPM))
            py = lambda y: int(round((y - vb[1] - T(box.GetTop())) * PPM))
            Image.fromarray(img).crop((px(x0), py(y0), px(x1), py(y1))).save(f'{prefix}-{tag}.png')
    json.dump({'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1, 't': b.GetDesignSettings().GetBoardThickness() / 1e6},
              open(prefix + '.json', 'w'))
    print(prefix, x0, y0, x1, y1)


if __name__ == '__main__':
    main(*sys.argv[1:4])
