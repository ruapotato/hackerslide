#!/bin/sh
# verify.sh [OUT_DIR] : every automatic check on the boards as they are in the repository.  Nothing is regenerated
# and nothing leaves the machine.  Needs KiCad 9 (kicad-cli, python3 pcbnew), numpy, scipy, Pillow, and for the
# Gerber comparison VENV=/path/to/venv with pygerber 2.x (default ../../.venv).
#   1 ERC, DRC and schematic parity of every board        4 part heights at their positions (carrier)
#   2 narrowest point of each power area (carrier)        5 fabrication files written to OUT_DIR and compared with
#   3 side-by-side runs of auto-routed signals (carrier)    the board files by an independent Gerber reader
# Exit status is non-zero if a check fails.
cd "$(dirname "$0")"
O=${1:-$(mktemp -d)}; mkdir -p "$O"; bad=0
for b in carrier keyboard keyboard-topplate keyboard-flex; do
  echo "== $b: ERC / DRC"; ./check.sh ../$b $b "$O" | tee "$O/$b-check.txt"
  grep -q "'error'" "$O/$b-check.txt" && bad=1
  grep -q "unconnected items: 0" "$O/$b-check.txt" || bad=1
  grep -q "parity: clean" "$O/$b-check.txt" || bad=1
done
echo "== carrier: power copper";      python3 power_paths.py 2>/dev/null | tee "$O/power.txt"; grep -q "not joined" "$O/power.txt" && bad=1
echo "== carrier: side-by-side runs"; python3 coupling.py 2>/dev/null
for b in carrier keyboard; do echo "== $b: track ends joined only by their rim"; python3 gr_io.py anchor ../$b/$b.kicad_pcb 0 2>/dev/null | tail -6; done
echo "== carrier: part heights";      python3 fit_check.py 2>/dev/null || bad=1
for b in carrier keyboard keyboard-topplate keyboard-flex; do
  echo "== $b: fabrication files in $O/fab/$b"
  ./fab_outputs.sh ../$b $b "$O/fab/$b" >/dev/null 2>&1 || bad=1
  python3 gerber_check.py ../$b/$b.kicad_pcb "$O/fab/$b" 2>/dev/null || bad=1
done
[ $bad = 0 ] && echo "ALL CHECKS PASS" || echo "SOME CHECKS FAILED"
exit $bad
