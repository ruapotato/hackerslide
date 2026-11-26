# Printing the enclosure

**Nothing here has been printed.** The model passes its own collision check closed and open, with envelopes for
every bought part, but clearances, snap fits and magnet strengths are estimates until the first print. Expect to
change numbers in `mechanical/src/config.py` and print again; that is what this "fit mule" is for.

Regenerate the files with `python mechanical/src/hackerslide.py` (CadQuery). They land in `mechanical/stl` and
`mechanical/step`.

## Parts

| File | Qty | Size (mm) | Plastic | Lay it on the bed | Supports |
|---|---|---|---|---|---|
| `front_shell.stl` | 1 | 131.5 x 74 x 12.4 | 10.2 cm3 | Screen side down | Port and button openings bridge on their own; the three hook ledges inside the left wall overhang 1 mm |
| `back_shell.stl` | 1 | 128.6 x 74 x 6.7 | 11.7 cm3 | Outside (floor) down | None. The two channels and the magnet pockets in the underside are 0.7-1.0 mm deep: bridges |
| `keyboard_tray.stl` | 1 | 131.5 x 74 x 6.7 | 2.9 cm3 | **Upside down**, top rim on the bed | None. The 0.3 mm rim that holds the top plate is then the first layer |
| `small_parts_plate.stl` | 1 | 112 x 72 x 3.6 | 4.2 cm3 | As exported | None. 50 keycaps (46 used), the 2u Space, 6 D-pad caps (5 used), 4 button caps (3 used), tops down |

`keycap_1u.stl`, `keycap_space_2u.stl`, `keycap_dpad.stl` and `button_cap.stl` are the single parts, for reprints.
`small_parts_plate.stl` is not kept in git (28 MB); the script writes it.

About 29 cm3 in all: roughly 36 g of PETG, a dollar or two of filament.

## Settings

- PETG or PLA, 0.4 mm nozzle, 0.2 mm layers for the shells and the tray, 0.12 mm for the small parts plate.
- Walls are 1.4 mm (the rail walls 1.2 mm): three perimeters, so infill hardly matters.
- The keycap legends are not in the model. The renders show printed legends; for a prototype use a paint pen or
  labels. The Fn-layer legends are silkscreen on the top plate.

## Other hardware

| Item | Qty | Where it goes |
|---|---|---|
| M2 heat-set insert, 3.2 mm outer, 3 mm long | 2 | Front-shell bosses, pressed in from the open side with a soldering iron |
| M2 x 10 screw, 3.6 mm head or smaller | 2 | Through the back shell and the carrier into the inserts |
| M2.5 x 4 screw | 4 | Module onto the carrier's spacers |
| M1.6 x 3 screw | 4 | Top plate onto the keyboard board's spacers |
| N52 disc magnet 6 x 1 mm | 4 | Back-shell floor, pressed in from outside (detents: closed and open) |
| N52 disc magnet 6 x 2 mm | 2 | Tray posts, one per side |
| N52 disc magnet 5 x 2 mm | 1 | Tray post under the hall switch |
| Thermal pad, 14 x 14 mm, 2 mm soft (compresses to 1.9) | 1 | SoC to back-shell floor |
| Glue (CA or epoxy) | | Keyboard board into the tray frame; magnets if they are loose |

Magnet poles: the tray magnet must attract both body magnets on its side. Check each pair before gluing.

## Putting it together

1. **Keyboard.** Solder the four M1.6 spacers to the keyboard board. Lay the keycaps on their switches, put the top
   plate over them and screw it to the spacers.
2. **Tray.** Press the three tray magnets into their posts. Push the keyboard assembly up into the tray frame from
   below until the top plate meets the rim, and glue the board's edge to the frame.
3. **Front shell.** Inserts in. Lay the shell face down, put the three button caps in their openings, then the panel
   with its tails folded back.
4. **Carrier.** Module onto the carrier (four screws, thermal pad on the SoC). Plug both panel tails into J4 and J5,
   then lower the carrier, module side up, onto the bosses.
5. **Battery.** Crimp the pack's two leads into the Molex 5264 housing (red in circuit 1, black in circuit 3), then
   put a meter on the plug ([bring-up-plan.md](bring-up-plan.md)). Pack into its bay beside the carrier, label up,
   leads across the top, plug into J10. The bay is 1.4 mm deeper than the pack: a strip of foam on top keeps it still.
6. **Back shell.** Four magnets into the floor. Feed the keyboard cable from J9 through the slot. Hook the shell's
   three hooks over the ledges on the battery side, swing it shut, two screws on the carrier side.
7. **Slide the tray on** from the user edge. The keyboard's connector J1 is under the body in both the open and
   the closed position, so plug the cable in on the way: with the tray on its rails but still about 10 mm short of
   the open position, J1 is just outside the body's user edge. Then push the tray home; the stop tab clicks into
   its channel under the floor and the cable forms its loop.

To take the tray off again, pull the stop arm down from below: it lies in the 2 mm gap above the keyboard board's
top edge.

## What to look at on the first print

| Check | Parameter in `config.py` |
|---|---|
| Does the tray slide freely without rattling? | `RAIL['clear']` (0.25) |
| Do the magnets hold it closed and open, and can a thumb still push it? | `MAGNET_BODY`, `MAGNET_TRAY` |
| Does the stop tab snap in, and does it stop the tray at both ends? | `STOP` |
| Do the hooks let the back shell swing shut? | `HOOKS` |
| Do the button caps move, and do they reach the switch plungers? | `BUTTON_CAP` |
| Do the keycaps move in the top plate and sit flush with the rim? | `KEYCAP`, `PLATE_RIM` |
| Does the pack fit its bay with its leads? | `BATTERY`, `BATT_LEAD_GAP` |
