"""Files in the form JLCPCB's order page takes, one folder per board.  Nothing is uploaded or sent anywhere.

  python3 order_files.py [OUT_DIR]        (default: ../../order, which git ignores)

Per board: NAME-gerbers.zip (Gerbers and drill files from fab_outputs.sh, renamed to the Protel extensions JLCPCB's
KiCad guide asks for), and for the two assembled boards NAME-bom.csv and NAME-cpl.csv in JLCPCB's column layout.
The flex gets the stiffener areas as the extra Gerber layer JLCPCB's flex guide names (pib_0.225 = polyimide,
0.225 mm, bottom side).  Part numbers, stock and prices come from bom/bom.csv: run bom/tools/make_bom.py first.
See bom/ordering-guide.md for the settings to choose on the order form.
"""
import csv
import os
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '../..')
BOARDS = [('carrier', 'carrier', True), ('keyboard', 'keyboard', True), ('keyboard-topplate', 'keyboard-topplate', False),
          ('keyboard-flex', 'keyboard-flex', False)]
PROTEL = {'F_Cu': 'GTL', 'B_Cu': 'GBL', 'In1_Cu': 'G2', 'In2_Cu': 'G3', 'F_Paste': 'GTP', 'B_Paste': 'GBP',
          'F_Silkscreen': 'GTO', 'B_Silkscreen': 'GBO', 'F_Mask': 'GTS', 'B_Mask': 'GBS', 'Edge_Cuts': 'GM1'}


def stiffener_gerber(path, rects):
    """Filled rectangles (x0, y0, x1, y1 in board mm, y down) as an RS-274X file in the same frame as the others."""
    f = lambda v: f'{int(round(v * 1e6))}'
    with open(path, 'w') as fh:
        fh.write('%FSLAX46Y46*%\n%MOMM*%\n%LPD*%\nG01*\n')
        for (x0, y0, x1, y1) in rects:
            fh.write('G36*\n' + f'X{f(x0)}Y{f(-y0)}D02*\n' + ''.join(f'X{f(x)}Y{f(-y)}D01*\n' for x, y in
                     ((x1, y0), (x1, y1), (x0, y1), (x0, y0))) + 'G37*\n')
        fh.write('M02*\n')


def main(out):
    bom = list(csv.DictReader(open(os.path.join(ROOT, 'bom/bom.csv'))))
    for folder, name, assembled in BOARDS:
        d = os.path.join(out, name)
        os.makedirs(d, exist_ok=True)
        with tempfile.TemporaryDirectory() as t:
            subprocess.run([os.path.join(HERE, 'fab_outputs.sh'), os.path.join(HERE, '..', folder), name, t], check=True,
                           capture_output=True)
            if name == 'keyboard-flex':
                import flex_design as F
                L = F.LENGTH
                stiffener_gerber(os.path.join(t, f'{name}-pib_0.225.gbr'), [(-2.25, 0, 2.25, 4.0), (-2.25, L - 4.0, 2.25, L)])
            with zipfile.ZipFile(os.path.join(d, f'{name}-gerbers.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
                for fn in sorted(os.listdir(t)):
                    stem, ext = os.path.splitext(fn)
                    layer = stem[len(name) + 1:]
                    if ext == '.gbr' and layer in PROTEL:
                        z.write(os.path.join(t, fn), f'{name}.{PROTEL[layer]}')
                    elif ext == '.drl' or layer.startswith('pib_'):
                        z.write(os.path.join(t, fn), fn)
            if not assembled:
                continue
            placed = {}
            with open(os.path.join(t, f'{name}-pos.csv')) as fh, open(os.path.join(d, f'{name}-cpl.csv'), 'w', newline='') as cf:
                w = csv.writer(cf)
                w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
                for r in csv.DictReader(fh):
                    placed[r['Ref']] = r
                    w.writerow([r['Ref'], f"{float(r['PosX']):.4f}mm", f"{float(r['PosY']):.4f}mm",
                                'Top' if r['Side'] == 'top' else 'Bottom', f"{float(r['Rot']):.0f}"])
        left = []
        with open(os.path.join(d, f'{name}-bom.csv'), 'w', newline='') as bf:
            w = csv.writer(bf)
            w.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #'])
            for r in bom:
                if r['board'] != folder or r['fitted'] != 'yes':
                    continue
                if not r['lcsc'] or r['status'] != 'in stock':
                    left.append(f"{r['refs']} ({r['mpn'] or r['value']}: {r['status']})")
                    continue
                w.writerow([r['mpn'] or r['value'], ','.join(r['refs'].split()), r['footprint'], r['lcsc']])
        print(f'{name}: {len(placed)} placements; not in the BOM for the fab: {left or "none"}')
    print('order files in', os.path.abspath(out))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'order'))
