#!/bin/sh
# gridroute.sh BOARD_DIR NAME [gridroute.py options...]
# One pass: DRC -> export -> route (venv python with numpy, Pillow, scikit-image) -> import.  Repeat until it
# reports nothing left.  VENV defaults to ../../.venv.
set -e
export PYTHONHASHSEED=0      # the same input gives the same routing
HERE=$(cd "$(dirname "$0")" && pwd); D=$1; N=$2; shift 2
PY=${VENV:-$HERE/../../.venv}/bin/python
T=$(mktemp -d)
kicad-cli pcb drc --format json -o "$T/drc.json" "$D/$N.kicad_pcb" >/dev/null
python3 "$HERE/gr_io.py" export "$D/$N.kicad_pcb" "$T/drc.json" "$T/in.json"
PYTHONHASHSEED=0 "$PY" "$HERE/gridroute.py" "$T/in.json" "$T/out.json" "$@"
python3 "$HERE/gr_io.py" import "$D/$N.kicad_pcb" "$T/out.json"
rm -rf "$T"
