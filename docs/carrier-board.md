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
| VSYS_LIM, U13 to U5 and to the backlight | 3 A to the boost | In2 area down the left strip and along the bottom strip, 3.8 mm of copper in all between the vias at its narrowest, with display-side straps in parallel above and below the touch connector (2.55 mm along the bottom), tied to In2 by three vias at each end; six vias at the boost inductor. See the table below |
| Everything routed by `gridroute.py` | Ordinary signals | Crosstalk screened by `coupling.py` (table below): the worst pair is estimated at 0.3 %, far below what 3.3 V logic notices. SD runs at most 50 MHz here (UHS is disabled) |
| BL_SW, LED_A | 13-39 V switching node, keep small and away from the codec and the DSI vias | Backlight driver in the left strip, 56 mm from the codec and 4.9 mm from the nearest DSI via; the BL_SW copper is 3.9 mm long |
| HP_L, HP_R, MIC, HPGND | Away from switch nodes; HPGND joins ground only at R49 by the jack | Codec next to the jack; nearest switch node (charger) 14 mm from the nearest audio track. R49 sits at the jack beside the sleeve strap R60 with its own ground via. The jack's ESD diodes sit on the display-side ground pour, with a via beside each where there was room |
| DF40 pads | 0.4 mm pitch, 0.2 mm pads, no copper between the rows | Rule areas present; the router keeps tracks and vias out of them, and DRC is clean |

### Power copper (`power_paths.py`)

| Path | Layer | Current | Widest single passage at the neck | All passages together | IPC-2221 rise for that total, if it were long |
|---|---|---|---|---|---|
| USB-C to charger (input limit 0.83 A max, R12) | In2.Cu | 0.83 A | 1.50 mm near (65, 13) | 1.5 mm | 9 K |
| battery connector to charger (fuse limit now 1.86 A typ; row computed at the earlier 3.0 A setting) | B.Cu | 3.2 A | 1.55 mm near (63, 16) | 1.6 mm | 9 K |
| battery fuse to 5 V boost | In2.Cu | 3.2 A | 2.01 mm near (69, 37) | 3.8 mm | 41 K |
| the same, parallel path on the display side along the bottom strip | B.Cu | 3.2 A | 2.55 mm | 2.6 mm | 4 K |
| boost to module pins 77-87 | B.Cu | 2.0 A | 1.00 mm near (43, 53) | 1.0 mm | 7 K |

"Widest single passage" is the widest corridor between vias at the narrowest line; "all passages together" adds up
the copper between the vias there. The rise is the IPC-2221 figure for a long track of that total width, so for
these short necks it overstates. The fuse output runs on In2 with a display-side strap in parallel above and below
the touch connector (vias at both ends of each strap); across the 1.8 mm gap kept for that connector's signals,
In2 carries it alone on 4.7-6.9 mm of copper.

### Side-by-side runs (`coupling.py`)

| Net | Neighbour | Layer | Side by side | Centre spacing | Estimated crosstalk |
|---|---|---|---|---|---|
| I2C_A_SCL | I2C_A_SDA | B | 12.2 mm | 0.25 mm | 0.3 % |
| I2C_A_SDA | TOUCH_INT | B | 9.9 mm | 0.25 mm | 0.2 % |
| TOUCH_INT | TOUCH_RST_N | B | 9.2 mm | 0.25 mm | 0.2 % |
| +3V3 | I2C_A_SCL | B | 12.2 mm | 0.30 mm | 0.2 % |
| SD_CLK | SD_D0 | B | 11.3 mm | 0.32 mm | 0.2 % ** |
| LED_ACT_N | RUN_PG | F | 9.3 mm | 0.30 mm | 0.2 % ** |
| I2S_DACDAT | I2S_MCLK | In2 | 1.9 mm | 0.40 mm | 0.0 % ** |
| +1V8 | I2S_MCLK | F | 1.6 mm | 0.40 mm | 0.0 % ** |
| HP_DET_SOC | I2S_MCLK | B | 1.2 mm | 0.35 mm | 0.0 % ** |
| I2S_ADCDAT | I2S_SCLK | F | 1.2 mm | 0.35 mm | 0.0 % ** |

128 net pairs run side by side within 0.3 mm; worst estimate 0.3 %.

The estimate assumes copper 0.1 mm below or above the tracks, which holds on F (over In1) and on B and In2 where a
ground pour or power area faces them. Where an In2 track has neither, the coupling is a few times higher: still
well under a tenth of the logic swing at these lengths.

### Track ends (`gr_io.py anchor`)

The router works on a grid, so a track can end beside a pad or via with only its round end cap overlapping:
connected for KiCad, a neck of a few hundredths of a millimetre on the board. An independent layout review found
about 200 of these. Every such end is now extended into the centre of what it joins (336 on this board; two
extensions were taken back because they came too close to a neighbour). `python3 gr_io.py anchor BOARD 0` lists
what is left: four ends of hand-laid power tracks that end across a pair of pins, each overlapping both pads fully.

### Known compromises

| What | Why it was left |
|---|---|
| +3V3 and +1V8 are distributed as 0.1-0.13 mm tracks: 0.3-0.4 ohm to the SD socket, the touch connector and the codec | Routing them wide made the board unroutable in one pass. About 60 mV drop at 200 mA; a 3.3 V area on In2 is the fix for a second revision |
| Codec capacitors are on the display side behind the codec, 0.5-5.6 mm from their pins through the board, each on the ground pour | The module side around the codec is taken by its escape vias. Expect some charge-pump ripple in the audio until the codec is laid by hand |
| Boost input capacitor C21 is 4.4 mm of 0.4 mm track from VIN; SW and VOUT leave the chip on 0.5 mm tracks | Wider tracks short to the neighbouring pins of the 0.5 mm-pitch package; lengths are 1-3 mm |
| The three switchers return through the In1 plane (0.1 mm below) rather than on the component layer | Vias beside every capacitor; a same-layer return needs the parts turned, which did not fit the strips |
| LED_A (up to 38 V if the panel is unplugged) has 0.18 mm to its nearest neighbour | IPC-2221 asks 0.13 mm at that voltage on a coated outer layer |

## What is left for the bench

Each item has a step in [bring-up-plan.md](bring-up-plan.md) and a fallback in the last table of
[open-questions.md](open-questions.md).

- **Battery plug polarity**, with a meter on the loose plug, before anything else. The board is marked +, T, -.
- Core3566 pin 99: what the power button does after `poweroff` (not documented by LuckFox; the board works either way).
- Console TX on TP34 idles at 3.3 V (expected from LuckFox's device tree; confirms the I/O voltage of pins 21, 51, 55, 80, 82).
- The fuse limit (R66 = 1.1 kohm, about 1.86 A) and that the module runs inside it.
- Panel tail fold, reach and thickness against J4/J5; pack lead dress against the plug space.
- PJ-342 sleeve terminal; straps R60-R63.
- Device tree: [device-tree.md](device-tree.md).

## Open TODO(verify) items in the source

Run `grep -rn "TODO(verify)" hardware mechanical`. They are collected in [open-questions.md](open-questions.md).

## Reserved for the AMOLED step

The B side under the module now carries the I2S straps and test pads; a later revision that places the AMOLED's
39-way connector there has to move them. That panel also needs a three-rail power chip and 1.8 V logic; none of that is on rev 0.1.
