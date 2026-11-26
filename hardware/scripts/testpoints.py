"""Test-point map of the carrier for bring-up: a table and two labelled pictures.

  python3 testpoints.py [BOARD.kicad_pcb] [OUT_DIR]     (system python: pcbnew, Pillow; needs kicad-cli, rsvg-convert)

Writes OUT_DIR/test-points.md and OUT_DIR/img/testpoints-{module,display}-side.png (default OUT_DIR: ../../docs).
The display-side picture is mirrored left to right, so it shows that side as you see it with the board turned over.
"""
import os
import re
import subprocess
import sys
import tempfile

import pcbnew
from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None
PPM = 24
# net -> what a meter or scope should show
EXPECT = {
    'VBUS': '5 V with USB plugged in',
    'VSYS': '3.5-4.3 V: charger output (about 3.65 V on USB with no pack)',
    'VBAT': 'pack voltage, 3.0-4.2 V',
    'VSYS_LIM': 'same as VSYS when the fuse U13 is on; 0 V if it has tripped or is held off',
    '+5V': '5.0 V (4.75-5.25) when the boost runs',
    'GND': 'ground: scope clip',
    'BOOST_PG': 'high (3.3 V) when 5 V is in regulation',
    'REGN': 'about 6 V with USB in, charger internal supply',
    'CHG_TS': '30-74 % of REGN with the pack thermistor connected (charging allowed)',
    'CHG_QON_N': 'high (pack voltage); low while the power button is held',
    '+3V3': '3.3 V from the module',
    '+1V8': '1.8 V from the module',
    'RUN_PG': 'high when the module runs; pulled low by RESET',
    'USB_OTG_ID': 'module OTG ID pin',
    'LED_A': 'backlight anode: about 12.8 V when lit, up to 39 V if the panel is unplugged (careful)',
    'TOUCH_INT': 'pulses low on touch',
    'I2S_LRCK': '48 kHz while audio plays', 'I2S_MCLK': '12.288 MHz while the codec is open',
    'I2S_SCLK': 'bit clock while audio plays', 'I2S_DACDAT': 'data while audio plays',
    'UART_DBG_TX': 'console out of the module, 3.3 V idle high, 1,500,000 baud 8N1: to the adapter\'s RX',
    'UART_DBG_RX': 'console into the module: from the adapter\'s TX (3.3 V adapters only)',
    'I2C_B_SCL': 'system I2C clock, idles at 3.3 V (0x6A charger, 0x36 gauge, 0x10 codec, 0x34 keyboard)',
    'I2C_B_SDA': 'system I2C data, idles at 3.3 V',
}
EXTRA = ('J8', 'J10', 'SW4', 'SW5', 'D1', 'D2', 'D13', 'SW1')
EXTRA_WHAT = {'J8': 'debug UART socket (JST-SH, Raspberry Pi Debug Probe lead): 1 RX in, 2 GND, 3 TX out',
              'J10': 'battery: + / thermistor / - marked on the board. Check the plug with a meter first',
              'SW4': 'BOOT: hold while applying power for the USB loader', 'SW5': 'RESET',
              'D1': 'red: charging (blinks on a charger fault)', 'D2': 'green: module activity',
              'D13': 'green: 5 V rail is up', 'SW1': 'power button'}


def render(board, layers, out):
    with tempfile.TemporaryDirectory() as d:
        svg = os.path.join(d, 'b.svg')
        subprocess.run(['kicad-cli', 'pcb', 'export', 'svg', '--layers', layers, '--exclude-drawing-sheet', '--page-size-mode',
                        '2', '--black-and-white', '-o', svg, board], check=True, capture_output=True)
        vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', open(svg).read(4000)).group(1).split()]
        subprocess.run(['rsvg-convert', '-w', str(int(round(vb[2] * PPM))), '-b', 'white', svg, '-o', out], check=True)
    return vb


def main(path, out):
    b = pcbnew.LoadBoard(path)
    T = pcbnew.ToMM
    bb = b.GetBoardEdgesBoundingBox()
    x0, y0, x1, y1 = T(bb.GetLeft()), T(bb.GetTop()), T(bb.GetRight()), T(bb.GetBottom())
    rows = []
    for f in b.GetFootprints():
        ref = f.GetReference()
        if ref.startswith('TP') or ref in EXTRA:
            p = f.GetPosition()
            net = list(f.Pads())[0].GetNetname() if ref.startswith('TP') else ''
            rows.append((ref, net, 'display' if f.IsFlipped() else 'module', T(p.x), T(p.y)))
    rows.sort(key=lambda r: (not r[0].startswith('TP'), int(re.sub(r'\D', '', r[0]))))
    os.makedirs(os.path.join(out, 'img'), exist_ok=True)
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
    except OSError:
        font = ImageFont.load_default()
    box = b.ComputeBoundingBox(False)
    for side, layers, mirror in (('module', 'F.Fab,F.Mask,Edge.Cuts', False), ('display', 'B.Fab,B.Mask,Edge.Cuts', True)):
        png = os.path.join(out, 'img', f'testpoints-{side}-side.png')
        vb = render(path, layers, png)
        im = Image.open(png).convert('RGB')
        if mirror:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        im = Image.blend(im, Image.new('RGB', im.size, 'white'), 0.6)
        dr = ImageDraw.Draw(im)
        taken = []
        for ref, net, s, x, y in rows:
            if s != side:
                continue
            px = (x - vb[0] - T(box.GetLeft())) * PPM
            px = im.size[0] - px if mirror else px
            py = (y - vb[1] - T(box.GetTop())) * PPM
            dr.ellipse((px - 9, py - 9, px + 9, py + 9), outline=(200, 0, 0), width=3)
            taken.append((px - 10, py - 10, px + 10, py + 10))
        for ref, net, s, x, y in rows:
            if s != side:
                continue
            px = (x - vb[0] - T(box.GetLeft())) * PPM
            px = im.size[0] - px if mirror else px
            py = (y - vb[1] - T(box.GetTop())) * PPM
            label = ref if not net else f'{ref} {net}'
            w = dr.textlength(label, font=font)
            for k in range(40):       # nearest free place for the label, joined to its pad by a line
                r = 12 + 14 * (k // 4)
                tx, ty = ((px - w / 2, py + r), (px + r, py - 12), (px - w / 2, py - r - 24), (px - r - w, py - 12))[k % 4]
                tx = min(max(tx, 2), im.size[0] - w - 2); ty = min(max(ty, 2), im.size[1] - 26)
                bx = (tx - 2, ty, tx + w + 2, ty + 24)
                if not any(bx[0] < t[2] and t[0] < bx[2] and bx[1] < t[3] and t[1] < bx[3] for t in taken):
                    break
            taken.append(bx)
            dr.line((px, py, (bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2), fill=(200, 0, 0), width=1)
            dr.rectangle(bx, fill=(255, 255, 255))
            dr.text((tx, ty), label, fill=(160, 0, 0), font=font)
        im.save(png)
    with open(os.path.join(out, 'test-points.md'), 'w') as fh:
        fh.write('# Carrier test points\n\nGenerated by `hardware/scripts/testpoints.py` from the board file; do not edit.\n'
                 'Positions are board coordinates in mm (origin top left, seen from the module side). The display-side\n'
                 'picture is mirrored, so it shows that side as you see it with the board turned over.\n\n'
                 '![module side](img/testpoints-module-side.png)\n\n![display side](img/testpoints-display-side.png)\n\n'
                 '| Ref | Net | Side | x | y | What to expect |\n|---|---|---|---|---|---|\n')
        for ref, net, s, x, y in rows:
            fh.write(f'| {ref} | {net} | {s} | {x:.1f} | {y:.1f} | {EXPECT.get(net) or EXTRA_WHAT.get(ref, "")} |\n')
    print(os.path.join(out, 'test-points.md'), len(rows), 'points')


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, '../carrier/carrier.kicad_pcb'),
         sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, '../../docs'))
