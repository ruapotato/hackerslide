# Thermal estimate

**Estimates only.** Plan: measure on the dev board in phase 1, then in the fit mule.

## The problem

The RK3566 dissipates about 2-3 W under load (from the brief; not measured). The device is sealed, has no fan,
and when the keyboard is closed the tray covers the back shell, which is where the SoC's heat goes.

## Heat path

SoC package, on the module side facing the back shell -> thermal pad or copper shim, 0.42 mm (`THERMAL_GAP`) ->
back shell floor, 1.2 mm -> 0.4 mm air gap -> keyboard tray. The module's other side faces the carrier.
The cell is beside the module, not under it; its nearest edge is about 9 mm from the module outline.

## Rough numbers

| Quantity | Value | Basis |
|---|---|---|
| Outer surface, closed | about 260 cm2 | 2 x 128 x 72 + perimeter x 18.65 mm |
| Natural convection plus radiation | about 10 W/m2K | Rule of thumb for a small hand-held object in still air |
| Average surface rise at 2.5 W, heat spread evenly | about 10 K | 2.5 / (10 x 0.026) |
| Average surface rise at 1.5 W | about 6 K | |

Heat will not spread evenly in a printed plastic shell (PLA conducts about 0.2 W/mK), so expect a hot spot over
the SoC well above the average, and a SoC temperature tens of kelvin above the surface. PLA softens near 55-60 degC:
**a PLA fit mule is not safe to run under sustained load.** Use PETG, and limit the CPU.

## What helps, in order of effect

1. The final shell material: aluminium spreads the heat across the whole back (the brief's stage 4).
2. A copper or graphite spreader on the inside of the back shell, larger than the SoC.
3. Capping CPU frequency: the brief already allows underclocking.
4. Vent slots in the prototype shells.

## What to measure

SoC temperature (kernel thermal zone) and back-shell temperature over the SoC, for idle, browsing and a 10-minute
full load, slider closed and open, at a known room temperature. Also the cell temperature while charging: the
charger stops above about 40-45 degC at its sensor.
