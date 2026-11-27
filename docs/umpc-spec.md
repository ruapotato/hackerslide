# HackBrain (UMPC): specification draft (2026-11-27)

**Status: concept, nothing ordered or drawn as a schematic.** Revised 2026-11-27: two slide thumbsticks instead of
thumbstick + trackball, so the device stays thin (David); see "Controls" below. Branch `hackbrain` (name: David, 2026-11-27). A WiBrain B1-style handheld PC: a landscape screen in
the middle, thumb keys at the top of each side, an analogue thumbstick at the bottom left and a trackball at the
bottom right. Model: `mechanical/src/umpc.py` (`CONTROLS = 'ball'` or `'fallback'`); renders:
`mechanical/render/umpc_scene.py`, stills in `~/Videos/hackerslide/concepts/umpc7_*`. Aim (David): good performance
and good battery life; WiBrain-sized or smaller; normal colour screen; the module's built-in Wi-Fi.

## Summary

| | |
|---|---|
| Size | **160.0 x 72.0 x 15.0 mm** (the trackball sets the thickness; 12.7 mm with the fallback D-pad and touchpad). WiBrain B1: 192 x 82 x 28 mm; Nokia N810: 128 x 72 x 14 mm |
| Brain | LuckFox Core3566 module with Wi-Fi and Bluetooth (Rockchip RK3566: 4 x Cortex-A55 at 1.8 GHz, Mali-G52 GPU, video decode). 4 GB version recommended ($102.99 with Wi-Fi at LuckFox when read on 2026-11-26; 2 GB $83.99) |
| Storage | microSD (the eMMC versions of the module were out of stock) |
| Screen | 3.5" 640 x 480 (4:3) IPS with capacitive touch: BuyDisplay ER-TFT035-7 (RGB/SPI, outline 76.84 x 63.84 x 3.2 mm before touch, $20.87) or Newhaven NHD-3.5-640480EF-MSXP-CTP (MIPI DSI, touch, DigiKey) |
| Keys | 20 per side: left Esc 1-4, Q-T, A-G, Shift Z-V; right 5-8 Del, Y-P, H-L Enter, B N M Space Fn; two shoulder buttons |
| Pointer | Pimoroni PIM447 trackball breakout (phone-style trackball with click and RGBW light, I2C; 25 x 22 x 9.5 mm) bottom right |
| Thumbstick | SparkFun COM-09426, PSP-1000-style analogue slide stick (two potentiometers), bottom left |
| Battery | two 5.0 x 34 x 62 mm (503562-size) cells, about 1,200 mAh each, 2,400 mAh / 8.9 Wh in total (cell part to choose; e.g. Adafruit #258: verify) |
| Audio | ES8316 codec, headphone jack, two small speakers, microphone (from the Linux handheld) |
| Power | USB-C, BQ25895 charger, MAX17048 gauge, battery limiter, 5 V boost for the module (from the Linux handheld) |
| Cooling | SoC lid to an aluminium plate in the back through a 1.1 mm pad; no fan |

## Inputs: how they reach the processor

Proposed: a small microcontroller on each keyboard board, or one shared (an RP2040, in deep JLCPCB stock), scans the
keys, reads the thumbstick's two potentiometers, talks to the trackball's I2C controller and presents all of it to
the module as one USB keyboard + mouse + gamepad. Linux then needs no driver of ours, and the firmware is small.
The alternative is the TCA8418 keyboard scanner of the earlier designs plus an I2C analogue converter for the stick
and a small Linux driver for the trackball.

## Stack (from the model)

| Centre, bottom to top | mm | Sides, bottom to top | mm |
|---|---|---|---|
| Back | 1.2 | Back | 1.2 |
| Thermal pad | 1.1 | Cell | 5.0 |
| Module (SoC lid to carrier) | 3.6 | Gap | 0.3 |
| Carrier board | 1.0 | Trackball module below the frame (standing 1.0 mm out) | 8.5 |
| Parts and gap | 1.2 | | |
| Raised to the common top: screen with touch, frame | 4.2 + 0.4 | | |
| **Total** | **15.0** | | **15.0** |

## Performance and battery (rough estimates, not measured)

- RK3566 under load about 2-3 W with the screen; light use (terminal, music, reading) about 1.5-2 W.
- On 8.9 Wh: about 4.5-6 h of light use, about 3 h under load.
- More battery: the 15 mm body leaves room for cells about 8-9 mm thick everywhere except under the trackball. A
  custom-size pack (one factory-made 2-cell pack shaped around the trackball) could reach roughly 4,000 mAh and
  7-10 h. That needs a pack maker; off-the-shelf cells come in fixed sizes.
- Faster but hungrier: a Rockchip RK3576 module would fit the same carrier design (as planned for the Linux
  handheld) at higher power.

## Fallback controls

If the trackball or the slide stick disappoints: a 5-way D-pad (cross cap over five switches) and a touchpad drawn
as copper on the keyboard board with an Azoteq controller. Device 12.7 mm thick.

## Open items

- Real cells (exact part, stock, protection board, mating plug).
- Trackball and slide stick: exact heights, cap size and travel from datasheets or a sample; long-term supply
  (both are maker-shop parts; the trackball is a recovered phone design).
- Screen: touch thickness, interface (MIPI DSI preferred), driver timing.
- Whether the Core3566 suspends reliably (battery in standby).
- Carrier: reuse of the Linux handheld's checked schematic (branch `linux-handheld`) in the new outline.
- FCC: deferred by David (2026-11-27); the module's own Wi-Fi is used.

## Cost (rough)

Close to the Linux handheld: parts per unit about $230-290 (module $84-103, screen $21-40, two cells, trackball
about $15-20, stick about $4-7, boards and small parts); first prototype about $850-1,250 delivered; whole effort
about $2,000-3,000.

## Controls, revised (David, 2026-11-27): two slide thumbsticks

Two PSP-1000-style slide sticks (SparkFun COM-09426), bottom left and bottom right; the right one drives the
pointer (the input microcontroller turns it into mouse movement, with the shoulder buttons as clicks), the left
one is a gamepad stick or arrow keys. Without the trackball the device is **160.0 x 72.0 x 12.7 mm**
(`CONTROLS = 'sticks'` in the model), and the space under the sticks allows 6 mm cells instead of 5 mm: about
3,000 mAh / 11 Wh in total (estimate, cells to choose), so roughly 5.5-7.5 h of light use and 3.5-4.5 h under
load (rough). The trackball option remains in the model (`'ball'`, 15.0 mm) and in the table above.

## Pointer, revised again (David, 2026-11-27): a "virtual trackball"

The phone-style trackball (PIM447) is small (ball about 8 mm, estimate) and 9.5 mm deep. Options looked at:

- **Virtual trackball (modelled, `CONTROLS = 'padball'`):** a 35 mm round capacitive trackpad (Cirque GlidePoint
  TM035035 class, I2C or SPI; sold by Mouser, stock and thickness to confirm) set like a shallow dish, plus
  momentum in the input microcontroller's firmware (a flick keeps the pointer rolling and slows down, like the Steam
  Controller's trackball mode) and a haptic motor for a "rolling" tick: TI DRV2605L driver (JLCPCB 491) and an LRA
  motor (MD-LRA371-H20, JLCPCB 5,017). No thickness cost: the device stays **12.7 mm**.
- **A real, larger ball done properly:** a 12-13 mm ball on three support bearings over a low-power optical mouse
  sensor (PixArt PMW3610 class, as in wireless DIY trackballs; JLCPCB 0, other distributors to check). Depth about
  16-17 mm at that spot, so a local bump on the back under the ball; the cell on that side must be shortened.
- The PIM447 stays the simplest option at 15.0 mm overall.

### Virtual trackball: part chosen (2026-11-27)

David likes the virtual ball if it is in stock. Cirque GlidePoint 35 mm round trackpads at Mouser (aggregator
snapshots, to recheck before ordering): **TM035035-2024-003, curved overlay** (119 in stock, 215 on order, about
$9.62) is the first choice, since the dished surface feels more like a ball; **TM035035-2024-002, flat overlay**
(211 in stock, about $9.63) is the fallback. 40 mm versions exist (TM040040-2024-30x) but do not fit the 35 mm
space under the right keys. Interface I2C or SPI to the input microcontroller, which adds the momentum; the haptic
tick comes from a DRV2605L driver and an LRA motor (both JLCPCB stock). Brain stays the Core3566, 4 GB version, for
performance (David: "keep the power").

## Battery chosen (2026-11-27): two Adafruit #2011 cells

Search report: `docs/research/lipo-cells-2026-11-27.md` (DigiKey stock and datasheets read 2026-11-27).

- **Adafruit #2011**, 2000 mAh, 7.4 Wh each (cell: PKCELL LP803860, protection board, JST-PH plug, UN 38.3 report),
  DigiKey 3,704 in stock at $12.50, Active. One under each keyboard half, in parallel: **14.8 Wh**, the most of
  any off-the-shelf option found. Rated 2 A continuous each; at the 1.5 A peak each carries about 0.75 A.
- Size not settled between sources (Adafruit 60 x 36 x 7; a test sample 60 x 37 x 7.4; maker's drawing maximum
  62 x 38.5 x 8.5 mm): the bays are sized to the maximum.
- No thermistor in the cells: one on the board against each cell.
- Runner-up with better paperwork: Jauch LP503759JU (1350 mAh, 62 x 38 x 5.8 mm, DigiKey 1,304): 10 Wh per pair,
  thinner device.
- Model with these cells: **166.0 x 72.0 x 14.4 mm** (wider halves for the 38.5 mm cells; the slide stick over the
  cell sets the thickness; ends less rounded, radius 11 mm).
- Rough life with the Core3566 (light use about 1.5-2 W): about 7-10 h; under load about 4-5 h. To be redone with
  the module chosen for 8 GB.
