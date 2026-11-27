# HackLite: specification draft (2026-11-27)

**Status: concept; nothing drawn or ordered.** Branch `hacklite` (name: David, 2026-11-27). Model
`mechanical/src/hacklite.py`; renders with `mechanical/render/umpc_scene.py` (UMPC_MODEL=mechanical/hacklite,
SCREEN_EMIT=0.25); stills in `~/Videos/hackerslide/concepts/hl_*`. Research:
`docs/research/plugin-mcu-and-eink-2026-11-27.md` (boards and panels), `docs/research/lipo-cells-2026-11-27.md`.

A small, pocketable HackOS device that runs for days: e-ink screen on top, a split thumb keyboard below whose width
sets the device width, a 5-way nav switch between the halves (the touch screen does the pointing). The brain is an
existing plug-in board (David: no custom compute module).

| | |
|---|---|
| Size | **90.2 x 93.4 x 13.0 mm** (model, no collisions) |
| Brain | **PJRC Teensy 4.1**: NXP i.MX RT1062, 600 MHz Cortex-M7, 1 MB RAM, 8 MB flash, pads for up to 16 MB PSRAM, microSD socket; $31.50, in stock at SparkFun (DEV-16771). HackOS already has a Teensy 4.1 target. Mounted under the main board with its pins cut short (about 4.5 mm stack, estimate) |
| Runner-up | SparkFun MicroMod Teensy Processor (same chip, 16 MB flash, 22 x 22 mm on an M.2 socket, $24.95, in stock): swappable, about 6 mm above the board |
| Screen | **Good Display GDEY031T10-T21**: 3.1" e-ink, 320 x 240, 4 grey levels, capacitive touch, 0.4 s partial refresh, SPI; outline 73.8 x 53.2 x 1.53 mm; $13.59 (bare panel GDEY031T10 $10.16; avoid GDEQ031T10, end of life). No front light at this size |
| Keys | 20 per side (left Esc 1-4, Q-T, A-G, Shift Z-V; right 5-8 Del, Y-P, H-L Enter, B N M Space Fn) |
| Battery | **Adafruit #328** (PKCELL LP785060), 2500 mAh, 9.25 Wh, protection board, UN 38.3 report; DigiKey 2,968 at $14.95 on 2026-11-27; datasheet maximum 62.5 x 50.5 x 8.1 mm, under the screen |
| Audio | I2S codec and headphone jack (as before), MP3 decoding in software |
| Storage | the Teensy's microSD |
| Wireless | none on the Teensy (could be added later as a small module) |

Stack: back 1.2, cell 8.1, gap 0.3, main board 0.8, keys 2.6 (screen side: panel 1.53 + frame 0.4 over the board).

**Battery life (rough estimates, not measured):** NXP's power note for the RT1062 gives 18 mA at 132 MHz, 3 mA at
24 MHz, 1.6 mA in low-power idle, 0.24 mA suspended. Reading or typing at a slow clock: about 0.1 W, so about
3-4 days of continuous use; listening to an audiobook on headphones: about 0.15-0.2 W, about 2 days of continuous
playback; idle with the image held on the e-ink: weeks. Getting there is HackOS power-management work: slow
clocks, low-power idle between keys, near-off when idle.

**Risks:** Teensy is now single-source (SparkFun; Adafruit stopped in January 2026); its Ethernet chip is fitted
and must be held powered down; through-hole pins make it sit about 4-5 mm deep; no wireless.
