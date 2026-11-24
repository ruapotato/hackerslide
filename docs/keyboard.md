# Keyboard

**DRAFT - NEEDS HUMAN REVIEW. Placed, not routed.**

## Stack

| Layer | Thickness | Note |
|---|---|---|
| Keyboard PCB | 1.0 mm | The floor of the tray and the bottom skin of the device. Nothing on its underside |
| Alps SKSWCFE010 switch | 0.6 mm | 3 x 2 mm, 2.4 N, 0.13 mm travel, 500,000 cycles |
| Keycap nub | 0.3 mm | Flat cylinder, 1.2 mm across (Alps asks for 1.0-1.5) |
| Keycap flange | 0.5 mm | Held captive under the top plate |
| Gap | 0.1 mm | |
| Top plate | 0.8 mm | Sits on four M1.6 SMT spacers, 1.5 mm, which also ground it |
| Tray rim | 0.3 mm | Keycap tops are flush with it |

Total 3.6 mm. Parts under the plate may be 1.0 mm high; the diodes sit under the keycap flanges, which ride
0.9 mm above the board, so they must be 0.5 mm or lower.

## Layout

48 keys on an 8.5 x 7.25 mm pitch (102 x 29 mm) plus a five-key D-pad in the 23 mm to the left.
[`kbd_layout.py`](../hardware/scripts/kbd_layout.py) holds the positions and legends and is shared by the keyboard, the top
plate and the enclosure model.

```
Esc   1  2  3  4  5  6  7  8  9  0  Bksp
Tab   Q  W  E  R  T  Y  U  I  O  P  -
Ctrl  A  S  D  F  G  H  J  K  L  ;  Enter
Shift Fn Z  X  C  V  [ Space ] B  N  M  .
```

Fn-layer legends are printed on the top plate. Both are proposals.

## Scanner

TI TCA8418 over I2C (address 0x34, mainline `tca8418_keypad`). No firmware. The chip has 8 rows and 10 columns, so
the 4 x 12 key field is folded:

| Chip row | Carries |
|---|---|
| ROW0-ROW3 | Physical rows 0-3, physical columns 0-9 |
| ROW4 | Physical column 10 on COL0-3, physical column 11 on COL4-7 |
| ROW5 | D-pad on COL0-4 |

Both Space switches share ROW3/COL6. Every key has a diode, anode toward the row: without diodes the chip reports
a phantom key for three-key combinations such as Ctrl + Shift + letter. The Fn layer is a Linux keymap matter.
The chip runs from 3.3 V.

Software notes: the device-tree keymap uses the chip's rows and columns, not the physical ones
(`matrix_pos()` in `kbd_layout.py` gives the mapping). `wakeup-source` is untested with this driver.

## Cable to the carrier

Our own flex circuit, [`hardware/keyboard-flex`](../hardware/keyboard-flex): one layer, 0.07 mm, 4.5 x 80 mm, eight
straight traces. It leaves carrier J9 toward the device's bottom edge, turns down through a slot in the back shell,
runs back under the body in a channel, makes a rolling loop of 1.9 mm radius in the tray's upper half, and enters
keyboard J1. Pin k of J9 is pin k of J1. Power and ground are mirror-symmetric, so a reversed cable cannot short
the supply.

- Stock flat cable is rated for 5-10 mm bend radius (Molex Premo-Flex datasheet). Use it on the fit mule only.
- JLCPCB advises a radius of 10-15 times the thickness for repeated bending and gives no life figure. **Cycle-test it.**
- Fallback: six bare pads LP1-LP6 on the keyboard sit under the carrier when the slider is open, for a spring-pin
  experiment. That would need a bus switch on the carrier and a driver re-initialisation on each open; neither exists.

## Switch options

| | Alps SKSWCFE010 | Keystone 5135 dome |
|---|---|---|
| Assembly | Fab-assembled, JLCPCB `C255576` | Hand placed, not soldered, adhesive retainer |
| Force | 2.4 N (1.6 and 1.8 N versions share the footprint) | 340 g; the 5133 is 220 g |
| State | Board placed | Footprint redrawn with non-standard lands; **board not generated** |

The dome variant needs Keystone's Mini-series land drawing before it can be trusted: Keystone's own lands do not
fit this key pitch. See [audit-status.md](audit-status.md), K6-K11.

## Assembly notes

- Switches: two reflow passes at most, no washing, 0.08 mm paste (Alps KSW-603).
- Spacers H1-H4 are hand soldered.
- The underside is handled by the user: tented vias, no exposed copper.

## Not done

Top-plate retention on the three edges away from the D-pad (frame lips, not modelled); keycap guidance against
tilting; the dome board.
