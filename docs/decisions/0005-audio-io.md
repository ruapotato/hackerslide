# 0005 Audio and I/O

**Status:** decided (codec approved by David, 2026-11-24).

## Context

The brief assumed the RK809 PMIC's codec would drive the headphone jack. No CM4-format module brings codec pins to
the connector, so that cannot be built.

## Options

| Option | For | Against |
|---|---|---|
| **ES8316 I2S codec on the carrier** | Mainline `snd-soc-es8316`; $0.91; capless headphone output; mic input | I2S pins differ between modules: resistor straps per module; none for ArmSoM |
| USB audio chip | Works with any module | Needs the hub that was removed; more power |

**Choice: ES8316**, with a PJ-342 jack that has a detect switch. Jack detect goes to the codec and to a module GPIO.

## Other I/O

microSD (Molex 104031-0811) on the module's SD pins, 3.3 V signalling only; power and volume buttons on the top
edge; boot and reset buttons inside; charge and activity LEDs; debug UART on a 3-pin JST-SH with the Raspberry Pi
debug-probe pin order; a hall switch for the slider. No speaker in rev 0.1.

## What would change this

A need for a speaker; ArmSoM support.
