# Carrier board: design notes and review checklist

**DRAFT - NEEDS HUMAN REVIEW. Placed; 214 of 301 connections autorouted, 87 open, no DRC errors.**
71.6 x 66 mm, 4 layers, 1.0 mm. The open connections are listed in [routing-status.md](routing-status.md).

**How it was routed, and what that means for a reviewer.** Every fine-pitch pin has a scripted escape stub and
via (`pcbgen.fanout`). The connections were then made by `gridroute.py`, a small grid router in this repository:
least-cost paths on F, In2 and B, no rip-up, no knowledge of differential pairs, impedance, current or noise.
In1 is a solid ground plane. Treat every routed track as a suggestion: the power loops, DSI and USB in the table
below need to be laid out again by a person, and the 87 open connections finished, before this board is ordered.
Source of truth: [`hardware/scripts/carrier_design.py`](../hardware/scripts/carrier_design.py) (circuit, read it top to
bottom) and [`carrier_pcb.py`](../hardware/scripts/carrier_pcb.py) (placement). The KiCad schematic puts a label on every
pin, so it reads as a netlist; it matches the script exactly.

## Reference designs used

| Block | Copied from |
|---|---|
| Charger | TI BQ25895 datasheet SLUSC88C, Fig. 9-1 |
| Boost | TI TPS61230 datasheet SLVSAQ2C, typical application and EN/HYS section 8.3.4 |
| Backlight | TI TPS61169 datasheet SNVSA40B |
| Codec | Everest ES8316 datasheet p.4; cross-checked with the Pinebook Pro schematic p.17 |
| Module sockets | Raspberry Pi CM4 datasheet and CM4IO board geometry |
| Debug connector | Raspberry Pi 3-pin Debug Connector Specification |

## Orientation

The board is drawn from its component (F) side. In the device that side faces DOWN, toward the back shell, so the
drawing is the device seen from the back: board x = 0 is the device's right edge. Only J4, J5 and three test
points are on the B side, which faces the display.

## Layout zones

| Zone | Contents |
|---|---|
| Module, x 7.5-62.5, y 12-52 | Nothing under the module on F (0.4-0.6 mm clearance). Module turned so J1A (power, SD, I2S, UART, GPIO) is at the bottom, J1B (USB, DSI) at the top |
| Right strip | USB-C, body screws HS1/HS2, USB ESD |
| Top strip | Jack and codec, power and volume buttons, hall switch, backlight driver, battery connector |
| Left strip | Charger, fuel gauge, next to the cell |
| Bottom strip | microSD, debug UART, keyboard connector, I2S straps, 5 V boost at the module's 5 V pins, boot/reset |

## Nets a reviewer must look at when it is routed

| Net group | Requirement | Status |
|---|---|---|
| DSI_CLK, DSI_D0, DSI_D1 pairs | 100 ohm differential, length-matched within a pair, over unbroken ground, about 15 mm from J1B to J4 with one layer change to the B side | Widths are placeholders: `TODO(verify)` with the fab's impedance calculator |
| USB_DP / USB_DM | 90 ohm differential, J1B to J2 via U2, about 45 mm | Placeholder widths |
| CHG_SW, PMID, VSYS at U3/L1 | Tight loop; C11/C12 at PMID, C15/C16 at SYS | Parts are adjacent |
| BOOST_SW, VSYS at U5/L2, +5V to the module pins | Tight loop; C21 at U5 pin 10; C22-C24 between U5 and the pins; 2 A to pins 77-87 | Parts are adjacent; +5V runs about 8 mm |
| VBAT, J10 to U3 | Up to about 4 A peaks | Short: both in the left/top-left |
| VBUS, J2 to U3 | 1.3 A, about 75 mm across the board | Route wide, on the inner layer |
| BL_SW, LED_A | 13-39 V node, keep small and away from the codec | |
| HP_L, HP_R, MIC, HPGND | Away from switch nodes; HPGND joins ground only at R49 by the jack | Codec is next to the jack; the boost is at the opposite edge |
| DF40 pads | 0.4 mm pitch, 0.2 mm pads, no copper between the rows | Rule areas present |

## Review checklist

- [ ] Every item in [footprint-review.md](footprint-review.md).
- [ ] Pin 99 measured on a real Core3566 (see [compute-pin-matrix.md](compute-pin-matrix.md)).
- [ ] Module height measured; `MODULE['mated']` in `mechanical/src/config.py` updated.
- [ ] Stack-up chosen and DSI/USB geometry calculated.
- [ ] J10 against the BAK pack's connector: which position is red (+), which is the thermistor.
- [ ] PJ-342 sleeve terminal identified; straps R60-R63 set.
- [ ] Panel tail fold and pin 1 confirmed on a real panel against J4 and J5.
- [ ] **Battery discharge limit** (requirement: never above the pack's rating, 5.6 A): U13 with R66 = 15k, 1.7 A. Check the limit on the bench before fitting a module; confirm the module runs inside it. See [power-budget.md](power-budget.md).
- [ ] Device-tree requirements collected: `ti,use-ilim-pin`, `ti,charge-current` 1.25 A, PWM period for the backlight, no UHS, `broken-cd` on Core3566.

## Open TODO(verify) items in the source

Run `grep -rn "TODO(verify)" hardware mechanical`. They are collected in [open-questions.md](open-questions.md).

## Reserved for the AMOLED step

The B side under the module is kept free of parts so that a later revision can place the AMOLED's 39-way
connector there. That panel also needs a three-rail power chip and 1.8 V logic; none of that is on rev 0.1.
