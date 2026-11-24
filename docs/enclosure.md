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
| Tray frame | Printed frame with the rails and three magnet posts. It has no floor: the keyboard PCB closes it |
| Keycaps | 1u, 2u Space, D-pad |

## Results (`mechanical/collision-report.json`)

18.65 mm closed, 107.9 mm open, 35.9 mm travel. No collisions closed or open, with envelopes for the panel and
its folded tails, the carrier and its tallest parts, the module, the cell and the keyboard stack.

Size comparison renders: `renders/compare_stack.png` and `compare.png` (N810 128 x 72 x 14 mm; Librem 5
152 x 74 x 15 mm).

## Slider

- Rails: lips on the tray frame's side walls run in grooves on the back shell. 0.25 mm clearance, estimate.
- Detents: one 6 x 2 mm magnet per side in the tray, two 6 x 1 mm magnets per side in the back-shell floor, 35.9 mm
  apart. The tray magnet sits over one when closed and the other when open; nothing in between. Sizes are
  parameters. Whether they hold the tray is unknown until the fit mule.
- Position sensing: a 5 x 2 mm magnet in the tray sits under hall switch U10 when closed, about 6.7 mm away
  (about 20 mT against a 4.8 mT threshold, estimate) and 36 mm away when open.

## Thermal path

See [thermal.md](thermal.md). The model draws a pad from the SoC to the back-shell floor, 0.42 mm thick with the
datasheet module height.

## Open items

- Only two body screws, on the carrier side. The cell side needs snap hooks.
- Top-plate retention lips on the tray frame.
- Button caps for power and volume (the switch plungers are 1.6 mm inside the wall).
- Cover or film for the keyboard PCB underside, if wanted.
- A light pipe or window for the two LEDs.
- Antenna position for the module's U.FL lead; matters once the shell is aluminium.
- Print rules from the brief still apply: 1.2-1.6 mm walls, heat-set inserts, removable back.
