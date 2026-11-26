#!/bin/sh
# render_all.sh OUT_DIR [SHOT...]   every shot of scene.py as PNG frames (WORK/frames/SHOT/) and an .mp4 in OUT_DIR.
# FORCE=1 renders frames again that are already on disk.
# BLENDER picks the Blender to use: one with GPU Cycles (the official builds) renders a frame in about 3 s.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=$1; shift
WORK=${HS_WORK:-/var/tmp/hackerslide-agent/render}
BLENDER=${BLENDER:-blender}
SHOTS=${*:-hero open explode keys ports board board_b module keyboard compare}
mkdir -p "$OUT"
for s in $SHOTS; do
    "$BLENDER" -b --factory-startup -P "$HERE/scene.py" -- "$s" "$WORK/frames/$s" --samples "${SAMPLES:-128}" ${FORCE:+--force} 2>&1 | grep -E "^FRAME|Traceback|Error" | awk 'NR%30==1'
    ffmpeg -y -loglevel error -framerate 30 -i "$WORK/frames/$s/$s-%04d.png" -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p "$OUT/$s.mp4"
    echo "done $s"
done
