# Purchasing list (rev 0.1 prototype)

Nothing here has been ordered. Prices were read on 2026-11-24 from the pages linked in [`bom.csv`](bom.csv);
anything marked *estimate* was not looked up. Regenerate the board part of the BOM, with fresh JLCPCB prices and
stock, with `python3 bom/tools/make_bom.py`.

## What David buys himself

| Item | Part | Qty | Unit price | Where | Notes |
|---|---|---|---|---|---|
| Compute module | LuckFox Core3566, 2 GB, Wi-Fi, no eMMC (`Core3566102000`) | 1 | $83.99 | [luckfox.com](https://www.luckfox.com/EN-Core3566) | In stock. Every eMMC SKU was out of stock, so it boots from microSD. 4 GB + Wi-Fi is $102.99 |
| Display | Focus LCDs E40RB-I-MW430-CB | 1 | $77.20 | [focuslcds.com](https://focuslcds.com/product/e40rb-i-mw430-cb/) | 10 in stock. Thin supply: buy a spare |
| Battery | Jauch LP675365JU+PCM+2 WIRES 70MM, 2800 mAh min / 3000 typ, with protection, no thermistor | 1 | $17.93 (read 2026-11-26) | [DigiKey](https://www.digikey.com/en/products/filter/batteries-rechargeable-secondary/91?keywords=LP675365JU) | 678 in stock, "Active". Ground shipping only. Two bare 26 AWG leads |
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
| Carrier, Standard assembly, both sides | $258: set-up $51.12, stencils $16.42, loading 63 part types x $1.53 = $96.39, 3,830 joints $6.13, hand-soldered header $3.83, parts 5 x $16.65 = $83.25, small fees $0.95 | $40-100 (4 layers, ENIG, 1.0 mm, impedance stack-up) | **$300-400** |
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
| Battery, plug housing and crimp terminals | $20 plus shipping |
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

## Battery (decided 2026-11-27)

**Jauch LP675365JU** from DigiKey. The BAK LP-454965-2P-3M the design was first drawn for went end-of-life with
no US source. What the change costs and gives:

| | BAK (before) | Jauch (now) |
|---|---|---|
| Capacity | 2800 mAh min | 2800 mAh min |
| Discharge limit | 5.6 A | 2 A, set by its leads |
| Size | 9.5 x 50 x 68 mm | 7.4 x 54 x 68 mm after cycling |
| Thermistor | 10k in the pack | none: the carrier's own (TH1) is fitted |
| Leads | plug fitted | two bare 26 AWG leads |
| Device | 128 x 74 x 20.05 mm | 131.5 x 74 x 19.35 mm |
| Fuse | 3.0 A | 1.86 A typ (R66 = 1.1 kohm) |

Also needed, from DigiKey or Mouser: one Molex 5264 3-way housing (50-37-5033) and two 5263 crimp terminals
(08-70-1040, for 22-28 AWG), and a crimp tool. Nothing is soldered. Red goes in circuit 1, black in circuit 3,
circuit 2 stays empty; circuit 1 is the pin marked + on the board. *Part numbers from Molex's catalogue, not yet
checked for stock.*

Jauch's datasheet (rev 1.3, 12/2024) says UL 1642 yes, UN 38.3 no, IEC 62133-2 no. That does not matter for a
prototype on a bench; it would for anything shipped to someone else.

Other packs looked at on 2026-11-26, and why not: Adafruit 328 (1.5 A), BatterySpace LP-804765 (5 A, fits the old
bay, but no datasheet and no evidence it is a current product), BatterySpace CU-J484 (has a thermistor; same
problem).
