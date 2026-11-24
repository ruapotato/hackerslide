# 0002 Display

**Status:** decided for rev 0.1 (David, 2026-11-24: "we will need one in stock"). A thin AMOLED is the planned
next step, not yet committed.

## Context

The brief's target, Focus E43GB-I-MW405-C (4.3"), turned out to be "not recommended for new designs" and out of
stock, which breaks the in-production rule. The panel must have a published datasheet and init sequence.

## Options

| Option | For | Against |
|---|---|---|
| **Focus E40RB-I-MW430-CB**, 4.0" 480x800 IPS, ST7701S, GT911, 2-lane DSI | In stock (10), "recommended for new designs", $77.20; ST7701 has a mainline driver used on an RK3566 device; init code published; pin-out like the old family | 4.25 mm thick; folded tails need 1.9 mm behind it; no ready panel entry in the driver; thin supply |
| Focus E43RB2-FW405-CB, 4.3" | The in-production 4.3" part | Out of stock |
| Focus E43RB1 parts, 4.3" | In stock | Not recommended for new designs |
| Waveshare 4.3" / 4" DSI modules | Easy on a Pi | Pi-style driver board; no evidence on Rockchip mainline |
| **DisplayModule DMKDO04301ACA**, 4.39" AMOLED 568x1210, on-cell touch | 0.75 mm thick: about 14.5 mm device (estimate); $59, 60 in stock | No mainline driver for the SD5207 controller or CST3530 touch; init sequence not in the datasheet; needs a three-rail power chip, 1.8 V logic, a 0.3 mm-pitch connector and our own cover lens; one vendor, no lifecycle statement; 2.13:1 strip shape |
| Panox ED410AC73.A AMOLED | 1.63 mm with cover glass | Supply unconfirmed |

## Choice

Focus E40RB-I-MW430-CB for rev 0.1, mounted with its FPC edge to the device right; both tails fold behind the
panel onto connectors on the carrier's display side.

## Why

It is the only candidate found that is in stock, in production and has a mainline controller driver.
David preferred to keep the first carrier on known parts and treat the AMOLED as a later step once it has been lit
on a dev board (2026-11-24).

## What would change this

The AMOLED working on a dev board (then the thin version follows); the E40RB going out of stock; a thin in-production
panel with a mainline driver turning up.
