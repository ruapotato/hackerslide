#!/bin/sh
# Board renders with KiCad's ray-less 3D renderer, headless (no display needed).  Output: hardware/renders/
cd "$(dirname "$0")/.."
mkdir -p renders
for b in ${*:-carrier keyboard keyboard-topplate keyboard-flex keyboard-5135}; do
  for side in top bottom; do
    env -u DISPLAY -u WAYLAND_DISPLAY kicad-cli pcb render --side $side --width 2000 --height 1200 --zoom 1 \
      -o renders/$b-$side.png $b/$b.kicad_pcb >/dev/null && echo renders/$b-$side.png
  done
done
