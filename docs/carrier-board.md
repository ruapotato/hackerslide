# Carrier board: design notes and review checklist

**DRAFT - NEEDS REVIEW. Fully routed: 0 open connections, no DRC errors, ERC and schematic parity clean.**
71.6 x 66 mm, 4 layers, 1.0 mm. Nobody but the author (an AI agent) has reviewed this layout; it has not been
built. See [routing-status.md](routing-status.md) for the current check results.

**How it was routed, and what that means for a reviewer.** Three kinds of copper are on this board:

1. **Hand-laid blocks** (`hardware/scripts/carrier_cells.py`): every part and track placed by coordinate, following
   the layout sections of the datasheets. These are the charger with the discharge limiter and the charge LED, the
   fuel gauge, the 5 V boost, the USB-C corner with the USB pair through the ESD part, and the three DSI pairs.
2. **Escape stubs** (`pcbgen.fanout`): a stub and a via for every used pin of the fine-pitch parts.
3. **Everything else** by `gridroute.py`, a small grid router in this repository: least-cost paths on F, In2 and B
   with rip-up and retry, then a repair loop that asks KiCad's design-rule check what is wrong, takes up the
   offending segments and lays them again until the check is quiet. It knows nothing about impedance, current or
   noise, so what it routed is ordinary signals only; the power paths and the two high-speed interfaces are in (1).

In1 is a solid ground plane. Power crosses the board as copper areas: VBUS and VSYS_LIM on In2, VBAT and +5V on the
display side. Things a reviewer should still distrust are listed in the table below.
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
drawing is the device seen from the back: board x = 0 is the device's right edge. The B side faces the display.
It carries the panel and touch connectors J4/J5, the discharge limiter, the fuel gauge, test pads and about fifty
0402-size parts for which the component side had no room. The tall ones are U13 (SOT-23-6, up to 1.45 mm), U4 and C17 (0.8 mm); the rest are at most 0.55 mm. The gap
behind the panel is 3.3 mm; a folded panel tail with its components is up to 1.7 mm thick, which leaves 1.6 mm under
a tail. `mechanical/src/config.py` asserts that the tallest display-side part fits there (0.15 mm to spare).

## Layout zones

| Zone | Contents |
|---|---|
| Module, x 7.5-62.5, y 12-52 | Nothing under the module on F (0.4-0.6 mm clearance), tracks only. Module turned so J1A (power, SD, I2S, UART, GPIO) is at the bottom, J1B (USB, DSI) at the top. On the display side under it: the I2S strap resistors R50-R59 next to their pins, and test pads |
| Right strip | USB-C, body screws HS1/HS2, USB ESD; on the display side under the connector the CC resistors and the unfitted adapter-detection links R21/R22 |
| Top strip | Jack and codec, power and volume buttons, hall switch, backlight driver, battery connector with the fuel gauge behind it |
| Left strip | Charger block: U3, L1, its capacitors; behind it the discharge limiter U13 and the thermistor divider |
| Bottom strip | microSD, debug UART, keyboard connector, 5 V boost block at the module's 5 V pins, boot/reset |

Module-connector escape vias are staggered in three rows, and in four rows on the GPIO end of J1A: with three
rows there the pins walled each other in.

## Nets a reviewer must look at when it is routed

| Net group | Requirement | Status |
|---|---|---|
| DSI_CLK, DSI_D0, DSI_D1 pairs | 100 ohm differential, matched within a pair, over unbroken ground | Hand-laid as edge-coupled pairs on F over In1, about 28-33 mm, 0.1 mm tracks with 0.12 mm gap. The clock pair drops to the display side for 2 mm at J1B to change places with lane 1. **Width and gap are estimates: `TODO(verify)` with the fab's impedance calculator.** Copper length per line, pad to pad including the escape stubs: clock 37.25 / 37.38 mm, lane 0 40.30 / 40.27, lane 1 36.13 / 36.10 (P / N), after small compensation bumps on the shorter line of each pair |
| USB_DP / USB_DM | 90 ohm differential | Hand-laid pair on F over In1, about 40 mm, through U2 pin to pin without a stub; D- has two vias at the connector, D+ none. 0.12 / 0.12 mm, **estimate, `TODO(verify)`**. Not length-compensated: the two lines differ by about 2 mm including their branches at the connector, inside the usual 3.8 mm allowance for USB 2.0 |
| CHG_SW, PMID, VSYS at U3/L1 | Tight loop; C11/C12 at PMID, C15/C16 at SYS | Hand-laid after TI SLUSC88C section 11: C11 0.2 mm from PMID, ground returns on vias into In1 beside the exposed pad, SW node 0.7 x 4 mm |
| BOOST_SW, +5V at U5/L2 | Output capacitors right at VOUT, small SW node | Hand-laid after TI SLVSAQ2C section 11. +5V reaches module pins 77-87 through three vias and an area on the display side: about 6 mm |
| VBAT, J10 to U3 | Up to 1.7 A (limiter) plus charge current 1.4 A | Area on the display side, 1.6 mm wide at its narrowest, three vias at U3 |
| VBUS, J2 to U3 | 1.3 A, about 75 mm | In2 area, 2.5 mm wide, routed around the J1B via rows; two or three vias at each end |
| VSYS_LIM, U13 to U5 and to the backlight | 1.7 A to the boost | In2 area down the left strip and along the bottom strip, 3.8 mm wide or more; the backlight feed (0.15 A) is an ordinary routed track |
| Everything routed by `gridroute.py` | Ordinary signals | Not reviewed for crosstalk. I2C, I2S and SD share layers with no spacing rules beyond the minimum clearance; SD runs at most 50 MHz here (UHS is disabled) |
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
- [ ] With a real panel: tail thickness measured. U13 (board x 68-71, y 30-32, display side, up to 1.45 mm) has only 0.15 mm to spare if a tail's component area lies over it.
- [ ] DSI and USB pair width and gap recalculated for the ordered stack-up (`carrier_cells.dsi`, `carrier_cells.usb`, `carrier_pcb.CLASSES`).
- [ ] The hand-laid power blocks compared with the TI layout examples by a second person.
- [ ] **Battery discharge limit** (requirement: never above the pack's rating, 5.6 A): U13 with R66 = 15k, 1.7 A. Check the limit on the bench before fitting a module; confirm the module runs inside it. See [power-budget.md](power-budget.md).
- [ ] Device-tree requirements collected: `ti,use-ilim-pin`, `ti,charge-current` 1.25 A, PWM period for the backlight, no UHS, `broken-cd` on Core3566.

## Open TODO(verify) items in the source

Run `grep -rn "TODO(verify)" hardware mechanical`. They are collected in [open-questions.md](open-questions.md).

## Reserved for the AMOLED step

The B side under the module now carries the I2S straps and test pads; a later revision that places the AMOLED's
39-way connector there has to move them. That panel also needs a three-rail power chip and 1.8 V logic; none of that is on rev 0.1.
