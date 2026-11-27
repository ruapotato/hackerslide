# Radio blocks: extracted datasheet facts (2026-11-26)

One JSON file per block: A CC1101, B LR1121, C ST25R3916B, E ESP32-C6-MINI-1, F Si24R1, G ATGM336H, H Si4732,
I infrared, J AT86RF215 + iCE40LP1K. Each lists the part, JLCPCB code and stock on that date, pin table, application
circuit, supplies, logic levels and its own `unverified` list.

**Status: extracted by parallel research jobs and checked only for form, not re-read against the datasheets.**
Every value has to be checked against its datasheet page when its sheet is drawn. Known weak spots: the LR1121
and CC1101 multi-band matching values (not from the makers' reference designs), the NFC matching (ST's values are
for a 47 x 34 mm antenna), the SDR's LVDS levels. DigiKey stock was not readable.

Block D (125 kHz reader) is not here: the only circuit found with values is Flipper Zero's, published "for
educational purposes only", which is not an open licence. It needs its own design or a properly licensed source.

What these facts do to the pin plan (`docs/hack-pad-pins.md`), which must change before the radio sheets are drawn:

- AT86RF215 logic cannot run from the 1.8 V pads (needs VDD - 0.4 V); the FPGA needs a 2.5 V bank with 100 ohm
  terminations for the radio's LVDS, has no PLL, and needs reset and a held-low select while loading.
- CC1101 GDO0 is an input needing 2.6 V or more when sending raw data: a divider only works for receiving.
- Unplanned lines that want brain pads: LR1121 BUSY and IRQ, Si24R1 CE and IRQ, NFC IRQ (push-pull, active high),
  ESP32-C6 handshake lines, CC1101 GDO2, a second infrared receiver, more lines for the 125 kHz reader.
- Si4732 has under 300 in stock at JLCPCB (226) and needs a bus, a 32.768 kHz clock and a reset line.
