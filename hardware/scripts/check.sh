#!/bin/sh
# check.sh BOARD_DIR NAME OUTDIR : run ERC + DRC (with schematic parity) and print a summary
set -e
D=$1; N=$2; O=${3:-$D}
kicad-cli sch erc --format json --severity-all -o "$O/$N-erc.json" "$D/$N.kicad_sch" >/dev/null
kicad-cli pcb drc --schematic-parity --format json -o "$O/$N-drc.json" "$D/$N.kicad_pcb" >/dev/null
python3 - "$O/$N-erc.json" "$O/$N-drc.json" <<'PY'
import json, sys
from collections import Counter
e = json.load(open(sys.argv[1])); d = json.load(open(sys.argv[2]))
ev = Counter((v['severity'], v['type']) for s in e['sheets'] for v in s['violations'])
dv = Counter((v['severity'], v['type']) for v in d['violations'])
print('ERC:', dict(ev) or 'clean')
print('DRC:', dict(dv) or 'clean')
print('DRC unconnected items:', len(d['unconnected_items']))
print('DRC schematic parity:', dict(Counter(v['type'] for v in d['schematic_parity'])) or 'clean')
PY
