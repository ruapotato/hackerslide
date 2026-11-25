# 0007 Body, slider and thermals

**Status:** decided for rev 0.1 (David, 2026-11-24).

## Thickness

| Version | Thickness | Cell | Note |
|---|---|---|---|
| First draft: cell under the carrier | 21.0 mm | 3000 mAh assumed (no real cell) | |
| Cell stacked under the module, as the brief described | about 26.8 mm | | Rejected |
| Carrier cut out around the cell, real cell and panel | 20.65 mm | 2500 mAh | David: "carrier cut out around the battery" |
| Plus the keyboard PCB as tray floor | 18.65 mm | 2500 mAh | Superseded by the battery change |
| **With the BAK pack (5.6 A, 9.5 mm)** | **20.05 mm** | 2800 mAh min | **Current** (David, 2026-11-24) |
| Plus a carrier window for the panel tails and a thinner lip | about 17.5 mm (estimate) | about 1850 mAh | Not done |
| Plus the AMOLED | about 14.5 mm (estimate) | about 1850 mAh | Planned next step |
| Plus a solder-down module | about 12-14 mm (estimate) | about 1400 mAh | Loses the upgrade path; module not buyable |
| No keyboard at all | 14.65 mm with today's parts | 2500 mAh | Considered and set aside: the slider is the point |

Reference: N810 128 x 72 x 14 mm; Librem 5 152 x 74 x 15 mm.

What sets the thickness: the battery pack, 9.5 mm plus 0.3 mm for swelling. The module on its socket (5.1), the
board (1.0) and the panel's folded tails (1.9) need 8.4 mm, so 1.4 mm behind the panel is now spare.

## Slider

Rails with magnet detents, no spring (from the brief). One tray magnet per side over two body magnets. A hall
switch reports "closed". Everything is parametric; expect many fit-mule iterations.

## Thermals

No fan. Pad or shim from the SoC to the back shell, which becomes aluminium in the final build. See
[thermal.md](../thermal.md).

## What would change this

Fit-mule results; the AMOLED step; measured heat.
