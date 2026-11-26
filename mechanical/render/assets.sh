#!/bin/sh
# assets.sh [ASSETS_DIR]   everything scene.py loads, made from the design files.
# Needs: KiCad 9 (kicad-cli, pcbnew), rsvg-convert, Pillow, and VENV (CadQuery) for the part models and enclosure.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
A=${1:-${HS_ASSETS:-/var/tmp/hackerslide-agent/render/assets}}
V=${VENV:-$HERE/../../.venv}
HW=$HERE/../../hardware
mkdir -p "$A"
"$V/bin/python" "$HW/scripts/models3d.py" >/dev/null 2>&1                 # part models the boards point at
"$V/bin/python" "$HERE/../src/hackerslide.py" >/dev/null 2>&1              # enclosure, with the scene STLs
rm -rf "$A/scene" && cp -r "$HERE/../renders/scene" "$A/scene"
for b in carrier:carrier:green keyboard:keyboard:green keyboard-topplate:topplate:black keyboard-flex:flex:flex; do
    d=${b%%:*}; r=${b#*:}; n=${r%%:*}; look=${r##*:}
    python3 "$HW/scripts/board_texture.py" "$HW/$d/$d.kicad_pcb" "$A/$n" "$look" >/dev/null 2>&1
    kicad-cli pcb export glb --subst-models --no-dnp -f -o "$A/$n.glb" "$HW/$d/$d.kicad_pcb" >/dev/null 2>&1
done
python3 "$HERE/screen.py" "$A/screen.png"
ls "$A"
