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
| Thermal pad | 14 x 14 mm, 2 mm soft | 1 | *estimate* $2-5 | | Fills `THERMAL_GAP` in `mechanical/src/config.py` (1.9 mm) |
| Stock 8-way 0.5 mm FFC, about 80 mm | for the fit mule only | 1 | *estimate* $1-3 | | Not for long-term use: see `docs/keyboard.md` |
| Filament | PLA or PETG | | *estimate* $5-20 per set of prints | | Front shell, back shell, tray frame, keycaps |

Development tools, bought once: optionally a CM4 IO board for first boot and power measurement (*estimate* $35-45; not
needed, see phase 1 of `docs/bring-up-plan.md`), a
3.3 V USB-serial adapter or Raspberry Pi Debug Probe for the console, a USB power meter.

## What the fab makes (JLCPCB, see [`ordering-guide.md`](ordering-guide.md) and [`fab-orders.md`](fab-orders.md))

**No quote was requested.** JLCPCB publishes its assembly fees but not most board prices, so each row is the
published fees added up, plus a guessed board price. Parts costs and counts are from `bom.csv` (2026-11-26); fees
from JLCPCB's assembly price page (updated 2026-10-22). Five boards each, all five assembled.

| Order | Published fees and parts | Board price (*guess*) | Estimate |
|---|---|---|---|
| Carrier, Standard assembly, both sides | $255: set-up $51.12, stencils $16.42, loading 61 part types x $1.53 = $93.33, 3,820 joints $6.11, hand-soldered header $3.83, parts 5 x $16.63 = $83.15, small fees $0.95 | $40-100 (4 layers, ENIG, 1.0 mm, impedance stack-up) | **$300-400** |
| Keyboard, one side | $82 on Economic (set-up $8.18, stencil $1.53, 5 extended types x $3.07, 2,085 joints $3.34, parts 5 x $10.63 = $53.15); $105 on Standard | $15-40, plus JLCPCB's "keyboard design" charge of about $18 if they apply it | **$100-165** |
| Top plate, bare | | $5-30 | **$5-30** |
| Keyboard cable, flex with stiffeners | | $25 is the published starting price | **$25-60** |
| **Five sets of boards** | | | **$430-655** |
| US tariff, 35 % | | | $150-230 |
| Shipping | | not published | *guess* $25-60 |
| **Delivered to the USA** | | | ***estimate* $600-950** |

Assembling two carriers instead of five saves about $50 of parts; the fixed fees stay.

## The first prototype, and one after that

"Prototype" here means the first one assembled. Whether it works is what building it finds out.

| Item | Cost |
|---|---|
| Five sets of boards, delivered (above) | *estimate* $600-950 |
| Module | $84 (read 2026-11-26) |
| Display | $77 (read 2026-11-26; 10 in stock) |
| Battery | $20-37 plus shipping; see the battery note below |
| Top-plate spacers, 4 | $4 plus shipping (DigiKey, $1.02 each, read 2026-11-26) |
| Card, magnets, screws and inserts, thermal pad | *estimate* $20-35 |
| Enclosure prints | about $2 of filament |
| USB-serial adapter or debug probe | *estimate* $10-15 |
| **First prototype (it may not work)** | ***estimate* $820-1,200** |
| Each further unit from the same five board sets | *estimate* $210-260 |

**For the whole effort**, plan on more than one round. A second carrier order costs about as much as the first
($400-600 delivered on its own), and a keyboard or cable change $150-300. With two more carrier rounds, one more
keyboard round and a spare panel, the total comes to roughly ***$2,000-3,000***. That figure is a plan, not a
measurement: it assumes the first boards mostly work.

## Battery note (decision open)

The BAK LP-454965-2P-3M the enclosure and J10 were drawn for is marked no longer manufactured. Farnell UK showed
about 20 left at GBP 33.93 (search snippet, undated) and exports only after a phone call; no US listing was found.
Alternatives found in single quantity in the USA, both from BatterySpace, both build-to-order in about a week,
both with bare leads (the Molex 5264 plug would have to be crimped on):

| Pack | Size (mm) | Capacity | Discharge / charge limit | Thermistor | Price |
|---|---|---|---|---|---|
| LP-804765 | 8.3 x 47.5 x 67 | 2500 mAh | 5 A / 2.5 A | none | $20.13 |
| CU-J484 (open-wire option) | 7.0 x 50 x 68; the cell's own sheet allows 51 wide | 2000 mAh | 4 A / 2.45 A | 10k, B 3435 | $25-37 |

Neither has a full pack datasheet. Without a thermistor, a 10k resistor across J10's T and - pins makes the
charger believe it is always 25 degC, which gives up the temperature cut-off. Details and sources:
[docs/open-questions.md](../docs/open-questions.md).
