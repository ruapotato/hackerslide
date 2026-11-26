# E-paper panel: Good Display GDEY0426T82-FT01C

Read on 2026-11-26 from the maker's documents linked on its product page (good-display.com/product/938.html):
the specification `GDEY0426T82-FT01C.pdf` (20 pages), the outline drawing `GDEY0426T82-FT01C-CAD.pdf` and the
front-light adapter schematic `CV0426.pdf`. Copies: `/var/tmp/hackerslide-agent/epd/src/` (not in the repo).

- **Stack (outline drawing):** touch film 0.30 + adhesive 0.18 + light guide 0.40 + adhesive 0.18 + panel 0.93 = 1.99 mm.
- **Display cable:** 24 contacts, 0.5 mm pitch; pin table in specification section 5. SPI, controller SSD1677.
  VCI 2.2-3.6 V, 8 mA typical while updating, 0.0066 mW in standby. Update times at 23 C: full 3.5 s, fast 1.5 s,
  partial 0.42 s.
- **Drive circuit (specification 8.2):** 47 uH inductor, Si1308EDL, three MBR0530, 1 M, 2.2 ohm, 4.7 uF / 25 V and
  1 uF capacitors. Drawn on the lid board. The diode directions in the maker's drawing are too coarse to read; the
  schematic follows the usual circuit of this controller family.
- **Touch cable (outline drawing):** 6 contacts: 1 GND, 2 VDD 3.3 V, 3 RST, 4 INT, 5 SDA, 6 SCL. FT6336U, 2.8-3.6 V.
- **Front-light cable (outline drawing):** 6 contacts: 1 cool +, 2 cool -, 3 and 4 not connected, 5 warm +, 6 warm -.
  Two separate strings. The maker's adapter feeds them from a 15 V rail through a resistor each.
- **Not stated anywhere in these documents:** the string current and forward voltage, and which way round the
  cables enter their sockets. Both must be settled with the panel in hand (or by asking the maker).
