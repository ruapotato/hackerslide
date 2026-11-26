#!/bin/sh
# fab_outputs.sh BOARD_DIR NAME OUT_DIR
# Gerbers (RS-274X, .gbr names), Excellon drill files with a drill map, placement file and IPC-D-356 netlist
# for one board, into OUT_DIR.  For inspection: nothing here is sent anywhere, and the output is not committed.
set -e
D=$1; N=$2; O=$3
mkdir -p "$O"
LAYERS=$(python3 - "$D/$N.kicad_pcb" <<'PY'
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
cu = [b.GetLayerName(l) for l in b.GetEnabledLayers().CuStack()]
print(','.join(cu + ['F.Paste', 'B.Paste', 'F.SilkS', 'B.SilkS', 'F.Mask', 'B.Mask', 'Edge.Cuts']))
PY
)
kicad-cli pcb export gerbers --layers "$LAYERS" --subtract-soldermask --use-drill-file-origin --no-protel-ext -o "$O/" "$D/$N.kicad_pcb" >/dev/null
kicad-cli pcb export drill --format excellon --excellon-separate-th --excellon-units mm --generate-map --map-format gerberx2 \
    --drill-origin plot -o "$O/" "$D/$N.kicad_pcb" >/dev/null
kicad-cli pcb export pos --format csv --units mm --side both --exclude-dnp -o "$O/$N-pos.csv" "$D/$N.kicad_pcb" >/dev/null
kicad-cli pcb export ipcd356 -o "$O/$N.d356" "$D/$N.kicad_pcb" >/dev/null
ls "$O" | wc -l
