#!/bin/sh
# Regenerate every board from the Python sources, then run ERC/DRC.  Run from anywhere.
# Needs: KiCad 9 (kicad-cli + its python3 'pcbnew' module), standard KiCad 9 libraries.
# Optional: ROUTE=1 FREEROUTING_JAR=/path/freerouting-2.1.0.jar to autoroute (overwrites the boards' tracks).
set -e
cd "$(dirname "$0")"
OUT=${OUT:-$(mktemp -d)}
python3 mklib.py
python3 keyboard_design.py alps ../keyboard
python3 keyboard_pcb.py alps ../keyboard ${ROUTE:+--route}
python3 carrier_design.py ../carrier
python3 carrier_pcb.py ../carrier ${ROUTE:+--route}
python3 topplate_design.py ../keyboard-topplate
python3 topplate_design.py ../keyboard-topplate --pcb
python3 keyboard_design.py dome ../keyboard-5135
python3 keyboard_pcb.py dome ../keyboard-5135
python3 flex_design.py ../keyboard-flex
for b in keyboard:keyboard carrier:carrier keyboard-topplate:keyboard-topplate keyboard-flex:keyboard-flex keyboard-5135:keyboard-5135; do
  echo "== ${b%%:*}"; ./check.sh ../${b%%:*} ${b##*:} "$OUT"
done
echo "reports in $OUT"
