# 0007 Body, slider and thermals

**Status:** decided for rev 0.1 (David, 2026-11-24).

## Thickness

| Version | Thickness | Cell | Note |
|---|---|---|---|
| First draft: cell under the carrier | 21.0 mm | 3000 mAh assumed (no real cell) | |
| Cell stacked under the module, as the brief described | about 26.8 mm | | Rejected |
| Carrier cut out around the cell, real cell and panel | 20.65 mm | 2500 mAh | David: "carrier cut out around the battery" |
| **Plus the keyboard PCB as tray floor** | **18.65 mm** | 2500 mAh | **Current** |
| Plus a carrier window for the panel tails and a thinner lip | about 17.5 mm (estimate) | about 1850 mAh | Not done |
| Plus the AMOLED | about 14.5 mm (estimate) | about 1850 mAh | Planned next step |
| Plus a solder-down module | about 12-14 mm (estimate) | about 1400 mAh | Loses the upgrade path; module not buyable |
| No keyboard at all | 14.65 mm with today's parts | 2500 mAh | Considered and set aside: the slider is the point |

Reference: N810 128 x 72 x 14 mm; Librem 5 152 x 74 x 15 mm.

What sets the thickness: the module on its socket (5.1), the board (1.0) and the panel's folded tails (1.9) add up
to the same 8.4 mm as the cell bay, so a thinner cell alone does not help.

## Slider

Rails with magnet detents, no spring (from the brief). One tray magnet per side over two body magnets. A hall
switch reports "closed". Everything is parametric; expect many fit-mule iterations.

## Thermals

No fan. Pad or shim from the SoC to the back shell, which becomes aluminium in the final build. See
[thermal.md](../thermal.md).

## What would change this

Fit-mule results; the AMOLED step; measured heat.
