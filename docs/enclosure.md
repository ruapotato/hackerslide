# Enclosure

Parametric CadQuery model in [`mechanical/src`](../mechanical/src). Every dimension is in `config.py`, tagged
`[ds]` (datasheet), `[dec]` (decision) or `[est]` (estimate to tune on the fit mule). **Fit-mule level: it checks
that parts fit, it is not a finished shell.**

```sh
cd mechanical/src
../../.venv/bin/python hackerslide.py     # parts, STL/STEP, collision report
python3 render.py ..                      # PNG renders under a private Xvfb display
```

## Parts

| Part | What it does |
|---|---|
| Front shell | Holds the panel under a bezel lip; side openings for USB-C, jack, microSD; screw bosses that stand on the carrier |
| Back shell | Removable. Floor with detent magnet pockets, the cable slot and channel; bosses that clamp the carrier from below; rail grooves on its sides |
| Tray frame | Printed frame with the rails, three magnet posts, the travel-stop arm and a rim that holds the top plate. It has no floor: the keyboard PCB closes it |
| Keycaps | 1u, 2u Space, D-pad |
| Button caps | Three, for power and volume: a stem through the top wall with a flange inside |

How to print and assemble them: [printing.md](printing.md).

## Results (`mechanical/collision-report.json`)

131.5 x 74 x 19.35 mm closed, 109.9 mm open, 35.9 mm travel (David 2026-11-27: 3.5 mm wider on the battery side for the Jauch pack, which is 2.1 mm thinner than the pack before it). No collisions closed or open, with envelopes for the panel and
its folded tails, the carrier and its tallest parts, the module, the cell and the keyboard stack.

Size comparison renders: `renders/compare_stack.png` and `compare.png` (N810 128 x 72 x 14 mm; Librem 5
152 x 74 x 15 mm).

## Slider

- Rails: 0.8 mm lips on the tray frame's 1.2 mm side walls run in grooves on the back shell, whose side walls are
  2.2 mm thick so that 1.15 mm of plastic stays behind each groove. 0.25 mm clearance, estimate.
- Travel stop: a tab on a spring arm along the tray's top wall runs in a blind channel under the back-shell floor.
  The channel's ends stop the tray closed and open, so it cannot slide off; a ramp on the body's user edge lets
  the tab snap in when the tray is first slid on.
- Detents: one 6 x 2 mm magnet per side in the tray, two 6 x 1 mm magnets per side in the back-shell floor, 35.9 mm
  apart. The tray magnet sits over one when closed and the other when open; nothing in between. Sizes are
  parameters. Whether they hold the tray is unknown until the fit mule.
- Position sensing: a 5 x 2 mm magnet in the tray sits under hall switch U10 when closed, about 6.7 mm away
  (about 20 mT against a 4.8 mT threshold, estimate) and 36 mm away when open.

## Thermal path

See [thermal.md](thermal.md). The model draws a pad from the SoC to the back-shell floor, 0.42 mm thick with the
datasheet module height.

## What holds it together

- Carrier side: two M2 screws through the back shell and the carrier into heat-set inserts in the front shell.
- Battery side: three rigid hooks on the back shell catch ledges inside the front shell's left wall. Hook, swing
  shut, screw.
- Top plate: four screws into spacers in the D-pad zone, and the tray's rim over its other three edges.
- Keyboard board: glued into the tray frame; it bears on the three magnet posts.

## Open items

- Everything in [printing.md](printing.md)'s check table: none of these fits has been printed.
- Cover or film for the keyboard PCB underside, if wanted. The 2 mm gap above the board's top edge is open.
- A light pipe or window for the charge, activity and 5 V LEDs. The shell hides them.
- Antenna position for the module's U.FL lead; matters once the shell is aluminium.
- Keycap legends (the renders show them; the printed caps are blank).
