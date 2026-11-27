# Flat Li-polymer cells for the handheld: survey (2026-11-27)

The device needs flat 1S Li-polymer cells with a built-in protection circuit (PCM). Each cell must be in stock at an authorized distributor, sold as single units at a listed price, and backed by a real datasheet.

The bays are:
- (a) two identical cells, one per bay, each bay 38 x 64 mm at most;
- (b) one cell in a bay of about 56 x 68 mm.

Cell thickness can be anywhere from 5 to 10 mm.

All stock counts and prices come from DigiKey (digikey.com, USD) on 2026-11-27 unless marked otherwise. Datasheets are saved in `dl/`, and the drawings I rendered from them are in `img/`.

**Legend for where the data came from:**
- **P**: read from a primary page, meaning the distributor product or listing page, or the manufacturer's datasheet or UN 38.3 report.
- **D**: from the DigiKey listing only. No maker datasheet was read.
- **S**: from search snippets only. Not verified.

**Why thickness and width use two values.** "Thickness" is the maximum the datasheet gives *after cycling* where one is stated, because Li-polymer cells swell. Where the distributor's number differs, both are shown. Width and length are the datasheet maximum body size, not counting the PCM leads.

**Thermistor.** None of these cells has an NTC. For Jauch "2 WIRES" parts this is inferred from the 2-wire build. Adafruit and SparkFun state it outright.

**Lead time.** DigiKey shows a 28-week manufacturer lead time for Jauch parts and 4 weeks for MikroE.

## Candidate table

Wh is calculated as typical capacity x 3.7 V.

| Part | Maker | Distributor (stock, 2026-11-27) | Price (qty 1) | L x W x T mm (max) | Cap. typ / min mAh | Wh | Max cont. discharge | PCM (limits) | NTC | Connector | UN 38.3 | Status | Fits | Src | URL |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **2011** | Adafruit (cell is PKCELL LP803860) | DigiKey 3,704; Adafruit "in stock" | $12.50 | Adafruit: 60 x 36 x 7.0; UN38.3 sample measured 60.0 x 37.0 x 7.4; **datasheet drawing max 62 x 38.5 x 8.5** | 2000 / 1900 | 7.4 | 1C = 2.0 A | Yes. IC R5402N101KD + 8205 MOSFET; 3.0 V cut-off (Adafruit); no overcurrent figure published | No | JST-PH 2-pin | Yes. NCT report NCT180521074B1-1, 2019 | Active | (a)* | P | digikey.com/en/products/filter/…?keywords=adafruit ; adafruit.com/product/2011 ; cdn-shop.adafruit.com/datasheets/LiIon2000mAh37V.pdf |
| **LP503759JU+PCM+2 WIRES 70MM** | Jauch | DigiKey 1,304 | $11.48 | 62.0 x 38.0 x 5.8 (5.4 as delivered); DigiKey says 38.1 W | 1350 / 1300 | 5.0 | 2C = 2.7 A | Yes, plus a second IC. OV 4.28 V, UV 3.00 V, OC discharge 3.3–7.5 A | No | 2 bare wires, 70 mm, AWG26 | Yes (datasheet) | Active | (a) | P | jauch.com …matd_246517_lp503759jupcm2_wires_70mm.pdf |
| **LP883550JU+PCM+2 WIRES 70MM** | Jauch | DigiKey 653 | $13.82 | 52 x 35 x 9.72 (9.0 as delivered) | 1600 / 1500 | 5.9 | 1C = 1.6 A | Yes, plus a PTC. OV 4.28 V, UV 3.00 V, OC discharge 3–6 A | No | 2 wires, 70 mm, AWG24 | Yes; IEC 62133-2 compliant | Active | (a) | P | jauch.com …matd_251920_…lp883550….pdf |
| **LP633750JH+PCM+2 WIRES 70MM** | Jauch | DigiKey 286 | $14.09 | 53.5 x 37.5 x 6.8 (6.3 as delivered) | 1420 / 1400 (DigiKey says 1.2 Ah) | 5.3 | 1C = 1.4 A | Yes, plus a second IC. OV 4.28 V, UV 3.00 V, OC discharge 3.1–6.0 A | No | 2 wires, 70 mm, AWG26 | Yes; IEC 62133-2 compliant | Active | (a) | P | jauch.com …matd_246516_lp633750….pdf |
| **LP503562JU+PCM+2 WIRES 50MM** | Jauch | DigiKey 408 | $11.74 | 62 x 35 x 5.4 (DigiKey: 63.5 x 36 x 5.8) | 1265 / 1250 | 4.7 | 1C = 1.25 A | Yes. OV 4.28 V, UV 3.00 V; no overcurrent figure in the text | No | 2 wires, 50 mm, AWG26 | Yes | Active | (a) | P | jauch.com …matd_246897_…lp503562….pdf |
| **258** | Adafruit (PKCELL LP503562) | DigiKey 2,933; Adafruit 78 | $9.95 | 62 x 34 x 5.0 (nominal; no max given) | 1200 / 1140 | 4.4 | 1C = 1.2 A | Yes, 3.0 V cut-off; no limits published | No | JST-PH 2-pin | Yes (report linked) | Active | (a) | P | adafruit.com/product/258 |
| **PRT-26059** | SparkFun (cell by LiPol Battery LP783450) | DigiKey 90; SparkFun "in stock" | $16.54 at DigiKey ($15.95 at SparkFun) | 51±1 x 34±0.5 x 7.8±0.3 | 1510 / 1500 | 5.6 | 1.5 A | Yes. OV 4.275 V, UV 2.75 V, OC 2–2.5 A | No (stated) | JST-PH 2-pin (PHR-2) | Not stated; IEC 62133-2 certificate | Active | (a) | P | sparkfun.com/products/26059 ; cdn.sparkfun.com …LP783450_1500mAh_with_connector_.pdf |
| LP103450JH+PCM+PTC+2 WIRES 70MM | Jauch | DigiKey 860 | $17.10 | 52 x 34.5 x **11.0** (10.0 as delivered) | 1920 / 1900 | 7.1 | 1C | Yes, plus a second IC. OC discharge 2–7 A | No | 2 wires, AWG24 | Yes; IEC 62133-2 | Active | (a) only if T ≥ 11 mm | P | jauch.com …matd_246520….pdf |
| MIKROE-698 | MikroElektronika | DigiKey 42 | $14.14 | 53 x 35 x 5.9 | 1000 / ? | 3.7 | ? | ? | ? | Wires with connector | ? | Active | (a) | D | DigiKey listing |
| MIKROE-4473 | MikroElektronika | DigiKey 76 | $17.02 | 63 x **39.5** x 6.1 | 1500 | 5.6 | 0.75 A (DigiKey "discharge rate") | ? | ? | Wires with connector | ? | Active | no (too wide) | D | DigiKey listing |
| USE-903439-1400 mAh | US Electronics | DigiKey **Marketplace** 145 | $11.24 | 41 x 34.5 x 9.5 | 1350 | 5.0 | ? | ? | ? | ? | ? | Active | (a), but a Marketplace seller | D | DigiKey listing |
| **LP675365JU+PCM+2 WIRES 70MM** | Jauch | DigiKey 678 | $17.93 | 68.0 x 54.0 x 7.4 (6.9 as delivered; DigiKey: 7.5) | 3000 / 2800 | 11.1 (label: 10.36 Wh) | 2 A (wire limited) | Yes, plus a second IC. OV 4.28 V, UV 3.00 V, OC discharge 4.2–9.0 A | No | 2 wires, 70 mm, AWG26 | **NO** (datasheet Rev 1.3 says UN 38.3: NO; IEC 62133-2: NO) | Active | (b) | P | jauch.com …246522_lp675365_2wire_70mm.pdf |
| **328** | Adafruit (PKCELL LP785060) | DigiKey 2,968; Adafruit "in stock" | $14.95 | Datasheet max 62.5 x 50.5 x 8.1; UN38.3 sample measured 61 x 47 x 6.7; Adafruit: 60 x 50 x 7.3; DigiKey: 65 x 50 x 8 | 2500 / 2375 | 9.25 | 1.5 A | Yes. OV 4.25 V, UV 2.5 V, OC 2–5 A, 10–60 mΩ | No | JST-PH 2-pin | Yes. NCT180521075B1-1, 2019 | Active | (b) | P | adafruit.com/product/328 ; cdn-shop.adafruit.com/product-files/328/… |
| **LP605060JU+PCM+2 WIRES 70MM** | Jauch | DigiKey 568 | $16.71 | 63.0 x 50.5 x 6.6 (6.2 as delivered) | 1900 / 1850 | 7.0 | 1C = 1.9 A | Yes. OV 4.25 V, UV 2.50 V | No | 2 wires, 70 mm, AWG26 | Yes | Active | (b) | P | jauch.com …matd_246519_…lp605060….pdf |
| PRT-13855 | SparkFun (cell DTP 605068) | DigiKey 153 | $19.41 | SparkFun: 68.8 x 49.2 x 5.6; DigiKey: 61 x 53.3 x 6.4 (they conflict) | 2000 | 7.4 | ? | Yes (OV/OC/UV, no limits) | Not mentioned | JST-PH 2-pin | Not stated (MSDS only) | Active | (b), but 68.8 mm may be 0.8 mm too long | P (dimensions conflict) | sparkfun.com/products/13855 |
| MIKROE-4474 | MikroElektronika | DigiKey 826 | $26.00 | 63 x **57** x 8.1 | 3000 | 11.1 | 1.5 A (DigiKey "discharge rate") | ? | ? | Wires with connector | ? | Active | (b) only if the bay is 57 mm wide | D | DigiKey listing; MikroE site returned 403 |
| MIKROE-1120 | MikroElektronika | DigiKey 51 | $18.00 | 63.5 x 44.2 x 7.0 | 2000 | 7.4 | ? | ? | ? | Wires with connector | ? | Active | (b) | D | DigiKey listing |
| LP305166JH+PCM+2 WIRES 70MM | Jauch | DigiKey 311 | $11.02 | 66.0 x 51.5 x 3.3 | 1200 | 4.4 | ? | Yes | No | 2 wires | (not read) | Active | (b), but thinner than the 5 mm window | D | DigiKey listing |

**Checked and rejected:**
- **SparkFun PRT-13856** is 6 Ah but 73 x 51 x 20 mm (DigiKey), too thick.
- **SparkFun PRT-08483** is obsolete, with 0 in stock.
- **SparkFun PRT-13813 and PRT-18286** are obsolete.
- **Adafruit 354, 353 and 5035** are 18 mm or more thick.
- **GlobTek BL2200/BL3000 F903178** cells are 78 mm long.
- **Jauch LP735977, LP705176, LP685077, LP504783 and LP906090** are 78 mm or more long.
- **Grepow** parts at DigiKey are all Marketplace listings, and the cells are small.
- **EEMB:** no DigiKey listing. One SOS Electronic listing for LP503759 has a minimum order of 500 (S).
- **Renata ICP:** no DigiKey listing. Snippets point to ICP543759PMT (1320 mAh, 61 x 37.5 x 5.95) at Mouser, and ICP606168PRT (2700 mAh, 71 x 62 x 6.7) is too long. I could not read Mouser stock because the pages timed out (S).
- **VARTA LPP 503759 8HH** (1400 mAh, with PCM and NTC) appears in Farnell and RS datasheets (S). It is not at DigiKey, and I did not verify stock.
- **Ultralife UBP001 (UBP103450/PCM, 1.75 Ah, S):** about 10 mm thick, below the Jauch LP103450 in capacity, and stock was not verified.
- **Tenergy:** no DigiKey flat-cell listing found.
- I could not check Mouser or Arrow stock pages because they timed out.

## Energy per mm of device thickness

**(a) Two identical cells, in parallel.** Thickness is the datasheet maximum.

| Rank | Part | Pair Wh (typ) | T max mm | Wh per mm | Stock |
|---|---|---|---|---|---|
| 1 | Adafruit 2011 | **14.8** | 8.5 (7.4 measured) | 1.74 (2.0 at 7.4) | 3,704 |
| 2 | Jauch LP503759JU | 10.0 | 5.8 | 1.72 | 1,304 |
| 3 | Adafruit 258 | 8.9 | 5.0 (nominal) | ~1.78 | 2,933 |
| – | Jauch LP503562JU | 9.4 | 5.4 | 1.73 | 408 |
| – | Jauch LP633750JH | 10.5 | 6.8 | 1.55 | 286 |
| – | SparkFun PRT-26059 | 11.2 | 8.1 | 1.38 | 90 |
| – | Jauch LP883550JU | 11.8 | 9.7 | 1.22 | 653 |
| – | Jauch LP103450JH | 14.2 | 11.0 | 1.29 | 860 (too thick) |

**(b) One cell in the 56 x 68 mm bay.**

| Rank | Part | Wh (typ) | T max mm | Wh per mm | Stock |
|---|---|---|---|---|---|
| 1 | Jauch LP675365JU | **11.1** | 7.4 | 1.50 | 678 |
| 2 | Adafruit 328 | 9.25 | 8.1 (6.7 measured) | 1.14 (1.38 at 6.7) | 2,968 |
| 3 | Jauch LP605060JU | 7.0 | 6.6 | 1.07 | 568 |
| – | SparkFun PRT-13855 | 7.4 | 5.6–6.4 | ~1.2 | 153 (length conflict) |
| – | MIKROE-4474 | 11.1 | 8.1 | 1.37 | 826 (57 mm wide) |

## Recommendations

### (a) Two cells in 38 x 64 mm bays

1. **Adafruit 2011 (2 x 2000 mAh, 14.8 Wh).** This option has the most energy and the deepest stock, and it carries a UN 38.3 report and a JST-PH lead. The 1C rating (2 A per cell) covers the 1.5 A peak with a lot of margin, because the parallel pair draws only about 0.75 A each.
   - **Caveat: the size depends on the source.** Adafruit gives 60 x 36 x 7. The 2014 PKCELL drawing gives a maximum of 62 x **38.5** x **8.5**. The 2019 UN 38.3 sample measured 60 x 37 x 7.4.
   - Design the bay to at least 39 x 63 x 8.5 mm.
   - Adafruit does not publish the PCM's overcurrent threshold.
2. **Jauch LP503759JU (2 x 1350 mAh, 10 Wh at 5.8 mm).** This is the thin choice, with the best documentation. The datasheet gives full PCM limits, a second protection IC, a 2C discharge rating and UN 38.3. The width is exactly 38.0 mm maximum. The leads are bare wires.
3. **Adafruit 258 (2 x 1200 mAh, 8.9 Wh at about 5 mm).** This one is very thin and DigiKey stock is deep. Thickness is given only as a nominal value.

   For the best-certified mid-thickness option instead, consider the Jauch LP883550JU: 11.8 Wh, 9.7 mm, UN 38.3 plus IEC 62133-2, and a PTC.

### (b) One cell in the 56 x 68 mm bay

1. **Jauch LP675365JU (11.1 Wh typ, 10.4 Wh min, 7.4 mm, 678 in stock).**
   - **Red flag:** the Jauch datasheet Rev 1.3 (12/2024) says **UN 38.3: NO**. DigiKey also says air shipment of lithium products is unavailable.
   - It is 68.0 mm long, which fills the bay exactly.
2. **Adafruit 328 (9.25 Wh, 8.1 mm maximum, 2,968 in stock).** It has a UN 38.3 report, full PCM limits, a 1.5 A continuous rating and a JST-PH lead.
3. **Jauch LP605060JU (7.0 Wh, 6.6 mm, 568 in stock).** It has UN 38.3 and is thin.

### Bottom line

The two-bay layout wins.

| Layout | Energy | Device thickness | Wh per mm |
|---|---|---|---|
| Two Adafruit 2011 cells | 14.8 Wh | 8.5 mm | 1.74 |
| One Jauch LP675365JU | 11.1 Wh | 7.4 mm | 1.50 |
| Two Jauch LP503759JU cells | 10 Wh | 5.8 mm | — |

Even the Jauch pair nearly matches the single large cell while being 1.6 mm thinner.

**Runtime estimate (my own arithmetic):** at the 1.5 A x 3.7 V peak, about 5.5 W, 14.8 Wh lasts about 2.4 h after 90 % boost efficiency. The average load will be lower than the peak, so real runtime should be longer.

**Before relying on these figures:**
- Re-check stock at order time.
- Jauch's standard lead time is 28 weeks, so DigiKey's stock on hand is what matters.
- No cell here has an NTC. If thermal monitoring is needed, put a board-side thermistor against the cells.
