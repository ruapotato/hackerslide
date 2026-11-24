# 0004 Power and battery

**Status:** decided, with open risks.

## Context

1S LiPo, 3000-4000 mAh wanted. Charger and gauge on the carrier. USB-C as a 5 V sink with 5.1k pull-downs, no PD.

## Findings that shaped it

- CM4-format modules take 5 V only, so a boost converter follows the charger (about 10 % loss, estimate).
- No stocked cell with a datasheet gives 3000 mAh in the space. PKCELL LP785060 (2500 mAh, 8.1 mm) is the
  nearest; it allows 1.5 A charge and 1.5 A discharge.
- The BQ25895 asks fast-charge adapters for 9-12 V by default and resets to 2.048 A charge current.

## Choices

| Part | Choice | Alternatives considered |
|---|---|---|
| Charger | TI BQ25895, as the brief proposed | - |
| Fuel gauge | **MAX17048** (approved by David): 25,000 in stock, no sense resistor, mainline `max17040` | BQ27441 from the brief: 86 in stock. Cost of the swap: no discharge-current reading |
| Boost | TPS61230 (not the 61230A): 2.3-5.5 V in, true output disconnect | TPS61089 for more margin |
| USB-C | Sink only, one port (David, 2026-11-24). Charger detection disconnected, so VBUS stays at 5 V | A second host port, or a dual-role port: dropped for rev 0.1 because the cell's 1.5 A rating leaves little for peripherals |
| Cell | PKCELL LP785060 beside the module, in a bay the carrier does not cover | Cell under the module: 26.8 mm. Jauch LP605060JU 1850 mAh for a thinner build |

## Open risks

Module peaks may exceed the cell's rating; booting without a charged cell needs a strong source; the device tree
must set the charge current and enable the input-limit pin. See [power-budget.md](../power-budget.md).

## What would change this

Measured module current; a better cell; a decision to add a host port.
