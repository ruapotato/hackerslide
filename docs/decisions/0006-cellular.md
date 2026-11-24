# 0006 Cellular

**Status:** not in v1 (from the brief).

The common Quectel EG25-G Mini PCIe has no Band 71 and is too thick. For a later variant, a modem listing Band 71 is
needed. Two findings from 2026-11-24:

- The carrier no longer has a USB hub, so a USB modem would need one added back.
- The Quectel SG560D-NA (a QCM6490 "smart module") lists LTE B71 and 5G n71, but it is a whole compute module, sold
  at about EUR 500 in reel quantities, not an add-on modem.

A product with a built-in cellular module needs its own certification and carrier approval.
