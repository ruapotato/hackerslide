# Hack pad: what a first build would cost (estimate, 2026-11-26)

**No quote was requested and nothing was ordered.** Parts drawn in the schematic so far were priced live from
JLCPCB's catalogue (price for 5 pieces); parts not drawn yet are priced from the research tables
(`docs/hack-pad-sensors.md`, `hardware/hackpad/data/radios/`, DigiKey figures read 2026-11-26) plus an allowance for
their small parts. Fees follow the same published JLCPCB fee schedule as `bom/purchasing.md` (Linux design).

## Parts on one main board

| Block | Estimate | Basis |
|---|---|---|
| Drawn so far (memory, power, keyboard, display link, card, audio, port expanders; not the brain) | $59 | priced live: 331 placements, 73 part types (49 "extended") |
| Brain, MIMXRT1176AVM8B | $27 | DigiKey, $26.83 (506 in stock) |
| Radios: sub-GHz, LoRa, NFC, Wi-Fi/BLE, 2.4 GHz, GPS, AM/FM/shortwave, infrared, 125 kHz | $45-65 | chip prices from the radio extraction; RF small parts, antennas and connectors allowed at $15-25 |
| SDR: AT86RF215, FPGA, reference, wide-range converter, shortwave receiver | $40-55 | DigiKey $7.61 + $6.71; converter $15-26 at JLCPCB; rest allowed |
| Sensors and bench tools, core set | $75-85 | the sensor table, $75, plus small parts |
| Sensors, extended set (radar, heart signal, gas) | $25-35 | research table prices, two not yet looked up |
| **One main board** | **$270-325** | |
| Lid board (e-paper drive circuit) | $2 | priced live |

Leaving the extended sensors and the wide-range converter off the first build saves about $45-60 a board.

## The first order (five boards made, two assembled)

| Item | Estimate | Basis |
|---|---|---|
| Main board, 6 layers, 125 x 69 mm, 1.0 mm, ENIG, filled vias under the BGA, impedance control, 5 pieces | *guess* $80-200 | JLCPCB publishes no 6-layer price for this; via-in-pad is free on 6 layers |
| Assembly fees, both sides | $300-360 | set-up and stencils about $70-100; about 140 extended part types x $1.53; joints about $10 |
| Parts for two main boards | $540-650 | above, x 2 |
| Lid boards, 2 layers, two assembled | $30-60 | |
| Slider cable, 20-way flex with stiffeners | $25-60 | JLCPCB's published starting price is $25 |
| Key plate, bare board | $10-30 | |
| **Factory order** | **$985-1,360** | |
| US tariff, 35 % (as in the Linux estimate) | $345-475 | |
| Shipping | *guess* $30-60 | |
| **Delivered** | ***$1,360-1,900*** | |

## The first prototype, and one after that

| Item | Cost |
|---|---|
| Boards, delivered (above) | $1,360-1,900 |
| E-paper panel with touch and front light (Good Display, $33.68, 94 in stock on 2026-11-26) plus shipping | $50-65 |
| Battery, GlobTek BL1950P4071611S1PCPT (DigiKey; price not recorded) | *estimate* $15-30 |
| Magnets, screws, prints, card | *estimate* $25-40 |
| **First prototype (it may not work)** | ***$1,450-2,050*** |
| Each further unit from the same boards (parts, tariff, panel, battery, case) | *estimate* $420-520 |

Development hardware (separate): Teensy 4.1 about $35 (planned); an RT1176 board later ($120-240, stock is thin).

## The whole effort

The main board is the risk (`docs/two-devices-risks.md`). Planning on two more main-board rounds at about
$1,000-1,400 each delivered, one more lid and cable round, and a spare panel, the total is roughly
***$4,000-5,500***. Building a smaller first board (brain, memory, power, display, keyboard, card, audio, two or
three radios) would cut the first order by about $300-500 and remove most of the risk from round one.

For comparison, the Linux handheld: first prototype $820-1,200, whole effort $2,000-3,000 (`bom/purchasing.md`).
