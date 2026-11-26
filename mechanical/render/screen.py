"""The picture shown on the panel in the renders: an invented terminal desktop, 800 x 480 drawn at 2x.

  python3 screen.py OUT.png      (Pillow)
It is a mock-up for the pictures only; no software has run on this hardware.
"""
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 960


def font(size, bold=False):
    name = 'DejaVuSansMono-Bold.ttf' if bold else 'DejaVuSansMono.ttf'
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + name, size)


def main(out):
    im = Image.new('RGB', (W, H), (10, 13, 20))
    d = ImageDraw.Draw(im)
    for y in range(H):                                  # soft vertical gradient
        d.line([(0, y), (W, y)], fill=(10 + y // 60, 13 + y // 50, 20 + y // 28))
    d.rectangle((0, 0, W, 56), fill=(18, 22, 32))
    d.text((24, 12), 'hackerslide', font=font(30, True), fill=(240, 176, 60))
    d.text((W - 330, 12), '12:42   87%', font=font(30), fill=(200, 205, 215))
    d.rounded_rectangle((40, 96, W - 40, H - 40), 18, fill=(6, 8, 12), outline=(50, 58, 75), width=3)
    d.rectangle((40, 96, W - 40, 150), fill=(24, 29, 40))
    d.text((64, 106), 'terminal', font=font(28), fill=(150, 158, 172))
    amber, grey, green, blue = (240, 176, 60), (200, 205, 215), (120, 200, 130), (120, 170, 240)
    lines = [(amber, 'user@hackerslide'), (grey, ':'), (blue, '~'), (grey, '$ uname -m && cat /etc/hostname')]
    x, y = 72, 180
    for c, t in lines:
        d.text((x, y), t, font=font(34, True), fill=c)
        x += d.textlength(t, font=font(34, True))
    body = ['aarch64', 'hackerslide', '', '  slide-out keyboard    53 keys + D-pad', '  screen                4.0 in, 480 x 800',
            '  battery               2800 mAh', '  ports                 USB-C, 3.5 mm, microSD', '']
    y += 54
    for t in body:
        d.text((72, y), t, font=font(34), fill=green if t.startswith('  ') else grey)
        y += 50
    x = 72
    for c, t in [(amber, 'user@hackerslide'), (grey, ':'), (blue, '~'), (grey, '$ ')]:
        d.text((x, y), t, font=font(34, True), fill=c)
        x += d.textlength(t, font=font(34, True))
    d.rectangle((x, y + 4, x + 20, y + 40), fill=grey)
    im.save(out)


if __name__ == '__main__':
    main(sys.argv[1])
