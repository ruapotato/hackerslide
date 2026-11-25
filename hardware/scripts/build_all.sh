#!/bin/sh
# Regenerate every board from the Python sources, then run ERC/DRC.  Run from anywhere.
# Needs: KiCad 9 (kicad-cli + its python3 'pcbnew' module), standard KiCad 9 libraries.
# Optional: ROUTE=1 also finishes the routing with gridroute.py (slow; needs VENV=/path/to/venv with numpy,
# Pillow and scikit-image, default ../../.venv).  Without it the boards keep only their scripted tracks.
set -e
cd "$(dirname "$0")"
# The committed keyboard and carrier are ROUTED.  Regenerating them without ROUTE=1 would replace them with
# unrouted boards, so that needs FORCE=1.
pcb() {  # pcb SCRIPT ARGS... BOARD_FILE : run the board generator unless it would discard routing
  for last; do :; done
  if [ -z "$ROUTE" ] && [ -z "$FORCE" ] && grep -q '(segment' "$last" 2>/dev/null; then
    echo "keeping routed $last (set ROUTE=1 to regenerate and re-route, or FORCE=1 to regenerate unrouted)"
  else
    n=$(($# - 1)); python3 $(echo "$@" | cut -d' ' -f1-$n) ${ROUTE:+--route}
  fi
}
OUT=${OUT:-$(mktemp -d)}
python3 mklib.py
python3 keyboard_design.py alps ../keyboard
pcb keyboard_pcb.py alps ../keyboard ../keyboard/keyboard.kicad_pcb
python3 carrier_design.py ../carrier
pcb carrier_pcb.py ../carrier ../carrier/carrier.kicad_pcb
python3 topplate_design.py ../keyboard-topplate
python3 topplate_design.py ../keyboard-topplate --pcb
python3 keyboard_design.py dome ../keyboard-5135
python3 keyboard_pcb.py dome ../keyboard-5135
python3 flex_design.py ../keyboard-flex
for b in keyboard:keyboard carrier:carrier keyboard-topplate:keyboard-topplate keyboard-flex:keyboard-flex keyboard-5135:keyboard-5135; do
  echo "== ${b%%:*}"; ./check.sh ../${b%%:*} ${b##*:} "$OUT"
done
echo "reports in $OUT"
