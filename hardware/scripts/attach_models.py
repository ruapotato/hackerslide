"""Point board footprints at the models from models3d.py where KiCad's own library has none.

  python3 attach_models.py BOARD.kicad_pcb [...]      (system python: pcbnew)

Only the 3D model reference of a footprint changes; copper, pads and positions are not touched.  Footprints whose
library model exists on this machine keep it.
"""
import os
import re
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
SHAPES = os.path.join(HERE, '../lib/hackerslide.3dshapes')
REF = '${KIPRJMOD}/../lib/hackerslide.3dshapes/'
KICAD = '/usr/share/kicad/3dmodels'


def exists(fn):
    p = re.sub(r'\$\{KICAD\d+_3DMODEL_DIR\}', KICAD, fn)
    return any(os.path.exists(os.path.splitext(p)[0] + e) for e in ('.step', '.wrl', '.stp'))


def attach(path):
    b = pcbnew.LoadBoard(path)
    n = 0
    for f in b.GetFootprints():
        name = f.GetFPID().GetUniStringLibItemName()
        own = os.path.join(SHAPES, name + '.step')
        if not os.path.exists(own):
            continue
        ms = f.Models()
        if any(m.m_Filename.startswith(REF) for m in ms) or any(exists(m.m_Filename) for m in ms):
            continue
        ms.clear()
        m = pcbnew.FP_3DMODEL()
        m.m_Filename = REF + name + '.step'
        ms.push_back(m)
        n += 1
    if n:
        pcbnew.SaveBoard(path, b)
    print(f'{path}: {n} footprints given a model')


if __name__ == '__main__':
    for p in sys.argv[1:]:
        attach(p)
