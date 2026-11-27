# HackLite: specification draft (2026-11-27)

**Status: concept; nothing drawn or ordered.** Branch `hacklite` (name: David, 2026-11-27). Model
`mechanical/src/hacklite.py`; renders with `mechanical/render/umpc_scene.py` (UMPC_MODEL=mechanical/hacklite,
SCREEN_EMIT=0.25); stills in `~/Videos/hackerslide/concepts/hl_*`. Research:
`docs/research/plugin-mcu-and-eink-2026-11-27.md` (boards and panels), `docs/research/lipo-cells-2026-11-27.md`.

A small HackOS handheld with the keys **left and right of the screen** (David, 2026-11-27: like the HackBrain, not a
keyboard under the screen). The width is set by the two key halves plus the screen. The brain is an existing
plug-in board (no custom compute module). Model `mechanical/src/hacklite.py --layout bar29|side31`.

| | **bar29** (slim bar) | **side31** |
|---|---|---|
| Size (model, no collisions) | **164.2 x 46.2 x 10.8 mm** | **158.0 x 61.4 x 13.0 mm** |
| Screen | Good Display GDEY029T71H, 2.9" 384 x 168 e-ink, 0.3 s partial refresh, no touch, $6.32 (79.98 x 35.57 mm) | Good Display GDEY031T10-T21, 3.1" 320 x 240 e-ink with touch, 0.4 s partial, $13.59 (73.8 x 53.2 x 1.53 mm) |
| Cell under the screen | Jauch LP503759JU, 1350 mAh, 5.0 Wh, 62 x 38 x 5.8 mm (DigiKey 1,304) | Adafruit #328, 2500 mAh, 9.25 Wh, 62.5 x 50.5 x 8.1 mm max (DigiKey 2,968) |
| Rough life in use (0.1-0.2 W) | about 1-2 days of continuous use | about 2-4 days of continuous use |

Both: **SparkFun MicroMod Teensy Processor** (NXP i.MX RT1062, the HackOS Teensy target; 22 x 22 mm card in an M.2
socket, about 6 mm above the board, swappable; $24.95, in stock) under the left keys; 20 keys per side (left Esc
1-4, Q-T, A-G, Shift Z-V; right 5-8 Del, Y-P, H-L Enter, B N M Space Fn); microSD and an I2S audio codec with a
headphone jack on the main board; no wireless. The Teensy 4.1 (in stock, $31.50) is the alternative brain, but at
61 mm long it only fits under the screen, competing with the cell.

Narrower: keys at 6.0 mm pitch instead of 7.0 save about 10 mm of width; four key columns per side instead of
five save about 14 mm (the number row then moves to Fn).

**Battery life basis (rough):** NXP's RT1062 power note: 18 mA at 132 MHz, 3 mA at 24 MHz, 1.6 mA low-power idle,
0.24 mA suspended; e-ink draws nothing while the image stays; idle with the image held: weeks. Reaching it is
HackOS power-management work.

**Risks:** Teensy boards are single-source (SparkFun); no front light at these e-ink sizes; the 2.9" panel has no touch.
