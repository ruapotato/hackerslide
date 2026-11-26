# 0004 Power and battery

**Status:** decided, with open risks.

## Context

1S LiPo, 3000-4000 mAh wanted. Charger and gauge on the carrier. USB-C as a 5 V sink with 5.1k pull-downs, no PD.

## Findings that shaped it

- CM4-format modules take 5 V only, so a boost converter follows the charger (about 10 % loss, estimate).
- Ordinary cells of this size are rated for 0.6-1 times their capacity. PKCELL LP785060 (2500 mAh, 8.1 mm,
  Adafruit, in stock) allows only 1.5 A discharge, less than the 5 V boost can ask for.
- David requires that the battery is never drawn beyond its rating (2026-11-24).
- The BQ25895 asks fast-charge adapters for 9-12 V by default and resets to 2.048 A charge current.

## Choices

| Part | Choice | Alternatives considered |
|---|---|---|
| Charger | TI BQ25895, as the brief proposed | - |
| Fuel gauge | **MAX17048** (approved by David): 25,000 in stock, no sense resistor, mainline `max17040` | BQ27441 from the brief: 86 in stock. Cost of the swap: no discharge-current reading |
| Boost | TPS61230 (not the 61230A): 2.3-5.5 V in, true output disconnect | TPS61089 for more margin |
| USB-C | Sink only, one port (David, 2026-11-24). Charger detection disconnected, so VBUS stays at 5 V | A second host port, or a dual-role port: dropped for rev 0.1 because the cell's 1.5 A rating leaves little for peripherals |
| Battery | **BAK LP-454965-2P-3M** (David, 2026-11-24): factory 1S2P pack, 2800 mAh min, 5.6 A discharge, 1.4 A charge, NTC, 9.5 x 50 x 68 mm, beside the module in a bay the carrier does not cover. Costs 1.4 mm of thickness | PKCELL LP785060: thinner, but 1.5 A. EEMB LP604765 (1900 mAh, 3.8 A): quote only. Akyga AKY2210: unverified. Cell under the module: far too thick |
| Discharge limit | TPS2553 switch at 1.7 A feeding the boost and the backlight | A 4 A eFuse (TPS2595) if the module needs more; TPS61236P boost with programmable output current: larger redesign |

## Open risks

The pack's Farnell stock and price are unconfirmed; the limiter's 1.7 A ceiling may be below the module's peak;
booting without a charged battery needs a strong source; the device tree must set the charge current (1.4 A or
less) and enable the input-limit pin. See [power-budget.md](../power-budget.md).

## What would change this

Measured module current; a better cell; a decision to add a host port.

## Change, 2026-11-27: battery

The BAK LP-454965-2P-3M went end-of-life with no US source. Two searches (distributors; makers and retailers) found
no pack in production, orderable in ones in the USA, that fits 50 x 68 x 9.8 mm at 3 A. David chose the **Jauch
LP675365JU** (DigiKey, "Active", datasheet rev 1.3 of 12/2024): 2800 mAh min, 7.4 x 54 x 68 mm, 2 A, no thermistor,
two bare leads.

Consequences: body 131.5 mm wide and 19.35 mm thick (was 128 and 20.05); fuse resistor R66 1.1 kohm for 1.86 A
typical (was 680 ohm, 3.0 A); the carrier's thermistor TH1 fitted and link R68 left out; the leads are crimped into
a Molex 5264 housing for the unchanged J10. No copper changed on the carrier.
