# Thermal estimate

**Estimates only.** Plan: measure on the dev board in phase 1, then in the fit mule.

## The problem

The RK3566 dissipates about 2-3 W under load (from the brief; not measured). The device is sealed, has no fan,
and when the keyboard is closed the tray covers the back shell, which is where the SoC's heat goes.

## Heat path

SoC package, on the module side facing the back shell -> **1.9 mm** to the back-shell floor (`THERMAL_GAP`) ->
back shell floor, 1.2 mm -> 0.4 mm air gap -> keyboard tray. The module's other side faces the carrier.

The 1.9 mm comes from LuckFox's own 3D model of the module (SoC lid 3.6 mm above the carrier, cavity 5.5 mm); an
earlier figure of 0.42 mm used the module height in the datasheet text, which is the CM4's. A 2 mm silicone pad at
3 W/mK over the 15 x 15 mm package is about 3 K/W, so 6-9 K across the pad at 2-3 W: acceptable, but a copper or
aluminium block (a 1.5 mm shim plus a 0.5 mm pad) would cut that to about 1 K/W. The tallest part on that side of
the module is an inductor 0.9 mm higher than the SoC, 19 mm away, so a flat spreader plate must be stepped or stay
within about 15 mm of the SoC centre. **Measure the real module before cutting anything.**
The cell is beside the module, not under it; its nearest edge is about 9 mm from the module outline.

## Rough numbers

| Quantity | Value | Basis |
|---|---|---|
| Outer surface, closed | about 274 cm2 | 2 x 131.5 x 74 + perimeter x 19.35 mm |
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
