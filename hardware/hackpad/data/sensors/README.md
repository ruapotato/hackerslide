# Sensor parts: extracted datasheet facts (2026-11-26)

One JSON file per part plus `REPORT.md` (I2C address map, which lines need brain pads or expander bits, current
budget). Extracted by research jobs; two files (INA237, MCP4728) were spot-checked against their datasheets and
found correct, the rest are checked only for form. Every value must be re-read from its datasheet page when its
sheet is drawn. Weak spots: RV-3032 (read from the application manual), BGT60LTR11AIP footprint and radome distance
(from memory), VL53L5CX address-change procedure (from memory).

Conflicts with the pin plan that must be resolved before the sensor sheets: both rangefinders answer at 0x29 (one
is moved in software at each start); a third port expander is needed; the motion-sensor interrupt and both
microphones need level translation; no wake pad is left for the radar; the heart-signal electrodes cannot share the
digital bench header; two analogue outputs need dividers for the 1.8 V ADC reference.
