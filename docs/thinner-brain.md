# A thinner, cooler brain: what exists (researched 2026-11-26)

David asked whether something thinner and lower-power than the CM4-format module could bring the device closer to
an N810 (14 mm), accepting speed only somewhat above the original's 400 MHz and 128 MB. **Nothing here is decided
and rev 0.1 is unchanged.** Heights are from datasheets or drawings unless marked; several prices came from search
snippets because distributor pages blocked reading, and are marked.

## What a thinner brain is worth in this enclosure

Today the module stands 4.5 mm above the carrier. It does not set the thickness on its own: the headphone jack
(5.0 mm) and the battery header (4.9 mm) are taller, and beside them all sits a 7.4 mm battery.

| Change | Thickness |
|---|---|
| Rev 0.1 as it is | 19.35 mm |
| Clear the five capacitors under the display tail's parts | 18.65 mm |
| Plus a brain of 3 mm or less, a mid-mount jack and a low battery connector | about 17.2 mm: the 7.4 mm battery then sets it |
| Plus a battery of about 6 mm (a lower-power brain needs less capacity) | about 15.8 mm (estimate): the USB-C socket, 3.3 mm tall, then sets the cavity |
| Plus the 0.75 mm AMOLED in place of the 4.25 mm panel | about 12.5 mm (estimate) |

So the brain matters most through **power**: a brain that draws a third of the power lets the battery, which is the
thickest single part, shrink.

## Options

| Option | What it is | Height above the carrier | Power | Display | Buyable | Linux | Work |
|---|---|---|---|---|---|---|---|
| **Forlinx FET3506J-S** | Solder-down module, RK3506: 3 x Cortex-A7, 512 MB, 8 GB eMMC, no GPU, no Wi-Fi | 2.3 mm | 0.27 W idle, 0.72 W full load (maker's brief) | 2-lane DSI: our panel | about $20 at DigiKey (*snippet; stock not confirmed*) | Drivers merged in mainline, but no RK3506 device tree there yet; vendor kernel 6.1 | New carrier around it; add a Wi-Fi part |
| **Octavo OSD32MP157** | One BGA with an STM32MP157 (2 x A7 + GPU), 512 MB or 1 GB RAM and its power chip inside | 2.4 mm | about 0.33 W on the core rail, peripherals off | 2-lane DSI | DigiKey $70.55, **0 in stock, 18 weeks** | Mature mainline | Chip on our own board (1.0 mm ball pitch), no memory or power design; add storage and Wi-Fi |
| Compulab MCM-iMX8M-Mini | Solder-down module, 4 x A53, 1-4 GB | under 3 mm | 0.24 W display off, 1.1 W typical, 15 mW suspend | 4-lane DSI, open GPU driver | **Quote only** | Good | New carrier; add Wi-Fi; runs straight from the cell, so the 5 V boost goes |
| Ka-Ro QSXP-ML81 | Solder-down module, i.MX 8M Plus, 2 GB | 2.6 mm | not published | 4-lane DSI, open GPU driver | Mouser, *snippets disagree: $141 or $312* | SoC yes, module no | As above |
| Boardcon CM3566 | Solder-down module with the **same RK3566** | 2.8 mm | same as today | same | By inquiry | Same software as rev 0.1 | New carrier; hand-solderable edge pads |
| Sophgo SG2000 | Bare chip, one core, 512 MB inside | about 1.3 mm | under 0.5 W | DSI, vendor kernel only | Not at US distributors; *a 2025 US export listing was recalled by the researcher and is unverified* | No display driver in mainline | Full chip-down design |

What the low-power ones can do: a terminal, SSH, light GTK programs and a simple browser. Not Firefox.

## Ruled out, one reason each

Raspberry Pi Zero 2 W (no DSI on pads, 5.2 mm); Raspberry Pi CM0 (2.8 mm, but idles at about 1.1 W: no cooler than
today); Radxa Zero 3W and Luckfox Pico (no DSI); LicheeRV Nano and Milk-V Duo (64-256 MB); every CM4-format module
(same sockets, same height); RK3562 and Allwinner T527 modules (no mainline display); Qualcomm QCM2290 modules
(about 2.8 mm with Wi-Fi, charger and codec on board, but not sold in ones); Toradex, Variscite, TQ, Digi (3.2-6 mm).
Nothing verified reaches 2 mm as a module.

## Not checked

Suspend current of the RK3506 modules; the height of a Wi-Fi add-on; whether JLCPCB will place a customer-supplied
module; modules from ADLINK, Avnet, iWave, SolidRun and Phytec.
