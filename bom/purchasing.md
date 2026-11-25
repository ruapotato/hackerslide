# Purchasing list (rev 0.1 prototype)

Nothing here has been ordered. Prices were read on 2026-11-24 from the pages linked in [`bom.csv`](bom.csv);
anything marked *estimate* was not looked up. Regenerate the board part of the BOM, with fresh JLCPCB prices and
stock, with `python3 bom/tools/make_bom.py`.

## What David buys himself

| Item | Part | Qty | Unit price | Where | Notes |
|---|---|---|---|---|---|
| Compute module | LuckFox Core3566, 2 GB, Wi-Fi, no eMMC (`Core3566102000`) | 1 | $83.99 | [luckfox.com](https://www.luckfox.com/EN-Core3566) | In stock. Every eMMC SKU was out of stock, so it boots from microSD. 4 GB + Wi-Fi is $102.99 |
| Display | Focus LCDs E40RB-I-MW430-CB | 1 | $77.20 | [focuslcds.com](https://focuslcds.com/product/e40rb-i-mw430-cb/) | 10 in stock. Thin supply: buy a spare |
| Battery | BAK LP-454965-2P-3M, 2800 mAh min / 3000 typ, with protection and NTC | 1 | *not verified*: about EUR 24 seen at a reseller | [Farnell 2401855](https://uk.farnell.com/bak/lp-454965-2p-3m/battery-lithium-ion-3-7v-3000mah/dp/2401855) | Confirm stock and price by hand. Check which connector position is red (+) against carrier J10 before plugging in. Lithium cells usually ship by ground only |
| Top-plate spacers | Wurth 9774015633R, M1.6, 1.5 mm | 4 | $1.46 (JLC list price, 0 in stock) | DigiKey or Mouser, not checked | Hand soldered onto the keyboard board |
| microSD card | any A1/A2 card | 1 | *estimate* $8-12 | | |
| Magnets | N52 discs: 6 x 1 mm (4), 6 x 2 mm (2), 5 x 2 mm (1) | 7 | *estimate* $5-10 for assorted packs | | Sizes are parameters to tune on the fit mule |
| Fasteners | M2 heat-set inserts + screws (2), M2.5 x 4 screws (4), M1.6 x 3 screws (4) | | *estimate* $5-10 | | |
| Thermal pad or copper shim | 14 x 14 mm, about 0.4 mm | 1 | *estimate* $2-5 | | Thickness follows `THERMAL_GAP` in `mechanical/src/config.py` |
| Stock 8-way 0.5 mm FFC, about 80 mm | for the fit mule only | 1 | *estimate* $1-3 | | Not for long-term use: see `docs/keyboard.md` |
| Filament | PLA or PETG | | *estimate* $5-20 per set of prints | | Front shell, back shell, tray frame, keycaps |

Development tools, bought once: a CM4 IO board for first boot and power measurement (*estimate* $35-45), a
3.3 V USB-serial adapter or Raspberry Pi Debug Probe for the console, a USB power meter.

## What the fab makes (JLCPCB, see [`fab-orders.md`](fab-orders.md))

| Board | Parts cost per board | Extended part types | Notes |
|---|---|---|---|
| Carrier (4-layer, assembled) | $15.97 | 35 | Includes the four M2.5 spacers |
| Keyboard (2-layer, assembled) | $10.64 | 5 | 53 switches at $0.16 are most of it |
| Top plate (2-layer, bare) | - | - | |
| Keyboard flex (1-layer flex, bare) | - | - | |

Parts costs are from the JLCPCB parts API on 2026-11-24 at the price break for five boards. JLCPCB charges a
fee per extended part type per order (about $3 each, from the earlier handoff notes, not re-checked), so the
carrier's 35 types add roughly $105 to each order of five. PCB, stencil, set-up and shipping are not quoted here:
no quote was requested.

## Per-unit estimate, one Wi-Fi prototype

| Item | Cost |
|---|---|
| Module | $84 |
| Display | $77 |
| Battery | *estimate* $26 |
| Carrier: parts $16, plus a one-fifth share of PCB, assembly and extended-part fees | *estimate* $45-65 |
| Keyboard: parts $11, plus share of PCB and assembly | *estimate* $18-28 |
| Top plate and flex cable, share of five | *estimate* $5-12 |
| Spacers, magnets, fasteners, thermal pad, card | *estimate* $25-40 |
| Enclosure prints | *estimate* $5-20 |
| **Total** | ***estimate* $285-350** |

The module and display ($161) are read prices; everything else, including the battery, is an estimate until
prices are confirmed and fab quotes exist.
