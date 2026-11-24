"""Render PNGs of the enclosure with OpenSCAD (headless, private Xvfb display; never the user's display).

python3 render.py MECH_DIR   (expects MECH_DIR/renders/scene/*.stl from hackerslide.py)
"""
import os
import subprocess
import sys

COLORS = {
    'front_shell': ([0.20, 0.22, 0.25], 0.55), 'back_shell': ([0.30, 0.32, 0.36], 1.0), 'tray': ([0.25, 0.27, 0.30], 1.0),
    'panel': ([0.05, 0.08, 0.15], 1.0), 'carrier': ([0.05, 0.40, 0.15], 1.0), 'module': ([0.10, 0.25, 0.55], 1.0),
    'battery': ([0.75, 0.70, 0.30], 1.0), 'thermal_pad': ([0.85, 0.45, 0.20], 1.0), 'kbd_pcb': ([0.05, 0.40, 0.15], 1.0),
    'top_plate': ([0.08, 0.08, 0.08], 1.0), 'keycap_flanges': ([0.85, 0.85, 0.82], 1.0),
    'keycap_tops': ([0.92, 0.92, 0.90], 1.0), 'magnets': ([0.75, 0.75, 0.80], 1.0),
}
EXPLODE = {'tray': -18, 'kbd_pcb': -12, 'keycap_flanges': -8, 'keycap_tops': -8, 'top_plate': -4, 'magnets': -2,
           'back_shell': 4, 'battery': 12, 'module': 12, 'thermal_pad': 8, 'carrier': 22, 'panel': 30, 'front_shell': 40}


def scene(scene_dir, tag, explode=False, section=None, hide=()):
    lines = []
    for part, (rgb, a) in COLORS.items():
        f = os.path.join(scene_dir, f'{tag}_{part}.stl')
        if part in hide or not os.path.exists(f):
            continue
        dz = EXPLODE.get(part, 0) if explode else 0
        lines.append(f'color([{rgb[0]},{rgb[1]},{rgb[2]},{a}]) translate([0,0,{dz}]) import("{f}");')
    body = '\n'.join(lines)
    if section is not None:   # keep x < section: a cut through the module/SoC showing the stack
        body = f'intersection() {{ union() {{\n{body}\n}} translate([-50,-80,-20]) cube([{section + 50},300,80]); }}'
    return body


_disp = [390]


def render(scad_text, out_png, camera, size=(1600, 1000), ortho=False):
    _disp[0] = 391 + (_disp[0] - 390) % 9   # private displays :391-:399, a fresh one per render
    display = _disp[0]
    scad = out_png.replace('.png', '.scad')
    open(scad, 'w').write(scad_text)
    env = dict(os.environ)
    for k in ('DISPLAY', 'WAYLAND_DISPLAY'):
        env.pop(k, None)
    cmd = ['xvfb-run', '-n', str(display), '-s', '-screen 0 1920x1200x24', 'openscad', '-o', out_png,
           f'--imgsize={size[0]},{size[1]}', f'--camera={camera}', '--projection=' + ('o' if ortho else 'p'), '--colorscheme=Tomorrow',
           scad]
    r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=900)
    os.remove(scad)
    if r.returncode != 0 or not os.path.exists(out_png):
        print(r.stdout[-2000:], r.stderr[-2000:])
        raise SystemExit('render failed: ' + out_png)


def main():
    mech = os.path.abspath(sys.argv[1])
    sd = os.path.join(mech, 'renders', 'scene')
    out = os.path.join(mech, 'renders')
    # camera = translate x,y,z, rot x,y,z, distance (OpenSCAD gimbal camera)
    render(scene(sd, 'closed'), os.path.join(out, 'closed.png'), '64,36,10,55,0,25,300')
    render(scene(sd, 'open'), os.path.join(out, 'open.png'), '64,18,10,55,0,25,330')
    render(scene(sd, 'closed', explode=True), os.path.join(out, 'exploded.png'), '64,36,18,70,0,30,360')
    render(scene(sd, 'section'), os.path.join(out, 'section.png'), '86,36,11,90,0,90,175', ortho=True)
    render(scene(sd, 'open', hide=('front_shell',)), os.path.join(out, 'open_no_front.png'), '64,18,10,40,0,20,330')
    print('renders in', out)


if __name__ == '__main__':
    main()
