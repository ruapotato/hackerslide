# Carrier board: design notes and status

**Rev 0.1. Fully routed: 0 open connections, no DRC errors, ERC and schematic parity clean. Not built.**
71.6 x 66 mm, 4 layers, 1.0 mm, JLCPCB stack-up JLC04101H-3313. No person has reviewed this layout and none is
going to before the first boards (David, 2026-11-25): it was checked by scripts in this repository and by
independent AI reviewers ([review-2026-11-25.md](review-2026-11-25.md)), and the first boards are the test.
See [routing-status.md](routing-status.md) for the current check results, [bring-up-plan.md](bring-up-plan.md) and
[test-points.md](test-points.md) for the bench.

**How it was routed.** Three kinds of copper are on this board:

1. **Hand-laid blocks** (`hardware/scripts/carrier_cells.py`): every part and track placed by coordinate, following
   the layout sections of the datasheets. These are the charger with the battery fuse and the charge LED, the
   fuel gauge, the 5 V boost, the backlight driver, the USB-C corner with the USB pair through the ESD part, the
   three DSI pairs, the escape of the touch connector J5 (it is fenced in by power copper on two layers; its five
   signals leave through a gap kept in the display-side strap) and the reset switch with its resistor.
2. **Escape stubs** (`pcbgen.fanout`): a stub and a via for every used pin of the fine-pitch parts.
3. **Everything else** by `gridroute.py`, a small grid router in this repository: least-cost paths on F, In2 and B
   with rip-up and retry, then a repair loop that asks KiCad's design-rule check what is wrong, takes up the
   offending segments and lays them again until the check is quiet. It knows nothing about impedance, current or
   noise, so what it routed is ordinary signals only; the power paths and the two high-speed interfaces are in (1).

In1 is a solid ground plane. Power crosses the board as copper areas: VBUS and VSYS_LIM on In2, VBAT and +5V on the
display side, with a second VSYS_LIM area there in parallel. What was checked on each group of nets is in the table
below.
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
It carries the panel and touch connectors J4/J5 (1.0 mm), the battery fuse U13, the fuel gauge U4 and C17 (0.8 mm),
test pads and about sixty 0402-size parts for which the component side had no room (0.55 mm at most; the unfitted
diode D9 would be 1.1 mm). The gap behind the panel is 3.3 mm; a folded panel tail with its components is up to
1.7 mm thick, which leaves 1.6 mm under a tail. `hardware/scripts/fit_check.py` checks every part's height at its
real position against these figures.

## Layout zones

| Zone | Contents |
|---|---|
| Module, x 7.5-62.5, y 12-52 | Nothing under the module on F (0.4-0.6 mm clearance), tracks only. Module turned so J1A (power, SD, I2S, UART, GPIO) is at the bottom, J1B (USB, DSI) at the top. On the display side under it: the I2S strap resistors R50-R59 next to their pins, and test pads |
| Right strip | USB-C, body screws HS1/HS2, USB ESD; on the display side under the connector the CC resistors and the unfitted adapter-detection links R21/R22 |
| Top strip | Jack and codec, power and volume buttons, hall switch, battery connector (the plug lies over the strip toward the module) with the fuel gauge behind it |
| Left strip | Charger block: U3, L1, its capacitors; behind it the battery fuse U13 and the thermistor divider; below it the backlight driver U6 with L3 |
| Bottom strip | microSD, debug UART (socket J8 and pads), keyboard connector, 5 V boost block at the module's 5 V pins, boot/reset, the 5 V lamp D13 |

Module-connector escape vias are staggered in three rows, and in four rows on the GPIO end of J1A: with three
rows there the pins walled each other in.

## What was checked, net group by net group

| Net group | Requirement | How it is met, and how that was checked |
|---|---|---|
| DSI_CLK, DSI_D0, DSI_D1 pairs | 100 ohm differential, matched within a pair, over unbroken ground | Hand-laid edge-coupled pairs on F over the In1 plane, 0.10 mm tracks with 0.15 mm gap: **100 ohm** on the 3313 prepreg (0.0994 mm, er 4.1) by the field solution in `impedance.py`. The clock pair drops to the display side for 2 mm at J1B to change places with lane 1. Lengths pad to pad, P / N: clock 37.24 / 37.37 mm, lane 0 40.29 / 40.26, lane 1 36.12 / 36.09, after compensation bumps on the shorter line of each pair. Lane-to-lane differences of a few mm do not matter at this panel's bit rate |
| USB_DP / USB_DM | 90 ohm differential | Hand-laid pair on F over In1, about 40 mm, through U2 pin to pin without a stub; 0.12 / 0.12 mm: **89 ohm** by `impedance.py`. The two lines differ by about 2 mm including their branches at the connector, inside the 3.8 mm that USB 2.0 high speed allows |
| CHG_SW, PMID, VSYS at U3/L1 | Tight loop; C11/C12 at PMID, C15/C16 at SYS | Hand-laid after TI SLUSC88C section 11: C11 0.2 mm from PMID, ground returns on vias into In1 beside the exposed pad, SW node 0.7 x 4 mm |
| BOOST_SW, +5V at U5/L2 | Output capacitors right at VOUT, small SW node | Hand-laid after TI SLVSAQ2C section 11. +5V reaches module pins 77-87 through three vias and an area on the display side: 1.0 mm wide at its narrowest for 2 A |
| VBUS, J2 to U3 | 0.83 A at most (R12), about 75 mm | In2 area routed around the J1B via rows, 1.5 mm wide at its narrowest; two or three vias at each end |
| VBAT, J10 to U3 | 3 A (fuse) | Area on the display side, 1.65 mm wide at its narrowest, vias at U3 |
| VSYS_LIM, U13 to U5 and to the backlight | 3 A to the boost | Two parallel areas down the left strip and along the bottom strip: In2 (3.8 mm of copper in all between the vias at its narrowest) and the display side (1.85 mm, along the bottom strip and beside the charger; it is open for 1.8 mm below the touch connector). Together they carry the 3 A with an estimated rise of 41 K if the inner layer carried it alone over a long run (it does so for 2 mm); see the table below |
| Everything routed by `gridroute.py` | Ordinary signals | Crosstalk screened by `coupling.py` (table below): the worst pair is estimated at 0.6 %, far below what 3.3 V logic notices. SD runs at most 50 MHz here (UHS is disabled) |
| BL_SW, LED_A | 13-39 V switching node, keep small and away from the codec and the DSI vias | Backlight driver in the left strip, 56 mm from the codec and 4.9 mm from the nearest DSI via; the BL_SW copper is 3.9 mm long |
| HP_L, HP_R, MIC, HPGND | Away from switch nodes; HPGND joins ground only at R49 by the jack | Codec next to the jack; nearest switch node (charger) 14 mm from the nearest audio track. No audio net runs beside a clock or a switch node (`coupling.py`) |
| DF40 pads | 0.4 mm pitch, 0.2 mm pads, no copper between the rows | Rule areas present; the router keeps tracks and vias out of them, and DRC is clean |

### Power copper (`power_paths.py`)

| Path | Layer | Current | Widest single passage at the neck | All passages together | IPC-2221 rise for that total, if it were long |
|---|---|---|---|---|---|
| USB-C to charger (input limit 0.83 A max, R12) | In2.Cu | 0.83 A | 1.50 mm near (65, 13) | 1.5 mm | 9 K |
| battery connector to charger (fuse limit 3.0 A typ) | B.Cu | 3.2 A | 1.65 mm near (63, 23) | 1.7 mm | 8 K |
| battery fuse to 5 V boost | In2.Cu | 3.2 A | 2.01 mm near (69, 37) | 3.8 mm | 41 K |
| the same, parallel path on the display side along the bottom strip | B.Cu | 3.2 A | 1.85 mm | 1.9 mm | 7 K |
| boost to module pins 77-87 | B.Cu | 2.0 A | 1.00 mm near (43, 53) | 1.0 mm | 7 K |

The rise is the IPC-2221 figure for a long track of the narrowest width, so for these short necks it overstates.

### Side-by-side runs (`coupling.py`)

| Net | Neighbour | Layer | Side by side | Centre spacing | Estimated crosstalk |
|---|---|---|---|---|---|
| I2C_A_SCL | I2C_A_SDA | B | 24.3 mm | 0.25 mm | 0.6 % |
| CHG_INT_N | LCD_TE | F | 16.5 mm | 0.30 mm | 0.3 % |
| I2C_A_SDA | TOUCH_INT | B | 9.9 mm | 0.25 mm | 0.2 % |
| TOUCH_INT | TOUCH_RST_N | B | 9.2 mm | 0.25 mm | 0.2 % |
| +3V3 | I2C_A_SCL | B | 12.2 mm | 0.30 mm | 0.2 % |
| LCD_RST_N | LED_ACT_N | B | 10.0 mm | 0.30 mm | 0.2 % ** |
| LED_ACT_N | RUN_PG | F | 9.3 mm | 0.30 mm | 0.2 % ** |
| CODEC_IRQ | I2S_MCLK | B | 7.9 mm | 0.35 mm | 0.1 % ** |
| I2S_MCLK | USB_OTG_ID | B | 6.8 mm | 0.35 mm | 0.1 % ** |
| I2C_B_SDA | I2S_MCLK | B | 2.8 mm | 0.35 mm | 0.0 % ** |
| HPGND | I2S_SCLK | B | 2.1 mm | 0.30 mm | 0.0 % ** |
| I2C_B_SCL | LED_ACT_N | In2 | 2.0 mm | 0.35 mm | 0.0 % ** |
| CHG_QON_N | DSI_D1_P | F | 1.3 mm | 0.31 mm | 0.0 % ** |
| +1V8 | I2S_MCLK | F | 1.6 mm | 0.40 mm | 0.0 % ** |

The estimate assumes copper 0.1 mm below or above the tracks, which holds on F (over In1) and on B and In2 where a
ground pour or power area faces them. Where an In2 track has neither, the coupling is a few times higher: still
well under a tenth of the logic swing at these lengths.

## What is left for the bench

Each item has a step in [bring-up-plan.md](bring-up-plan.md) and a fallback in the last table of
[open-questions.md](open-questions.md).

- **Battery plug polarity**, with a meter on the loose plug, before anything else. The board is marked +, T, -.
- Core3566 pin 99 and the I/O voltage of module pins 55 and 80 (must be 3.3 V): measured on a stock carrier first.
- The fuse limit (R66 = 680 ohm, about 3.0 A) and that the module runs inside it.
- Panel tail fold, reach and thickness against J4/J5; pack lead dress against the plug space.
- PJ-342 sleeve terminal; straps R60-R63.
- Device tree: [device-tree.md](device-tree.md).

## Open TODO(verify) items in the source

Run `grep -rn "TODO(verify)" hardware mechanical`. They are collected in [open-questions.md](open-questions.md).

## Reserved for the AMOLED step

The B side under the module now carries the I2S straps and test pads; a later revision that places the AMOLED's
39-way connector there has to move them. That panel also needs a three-rail power chip and 1.8 V logic; none of that is on rev 0.1.
