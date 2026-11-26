# How to order the boards (JLCPCB)

**Nothing has been ordered, quoted or uploaded, and nothing in this design has been built or powered.** These are
the steps for David to do himself; the files stay on this machine until he uploads them. The settings come from
JLCPCB's help pages as read on 2026-11-26 (links at the end); the order form itself was not opened, so a field
may be named differently from what is written here.

## 1. Make the files

```sh
python3 bom/tools/make_bom.py                 # fresh stock and prices into bom/bom.csv
hardware/scripts/verify.sh                    # every automatic check; must end "ALL CHECKS PASS"
python3 hardware/scripts/order_files.py       # writes order/<board>/
```

| Board | Upload as | Files in `order/` |
|---|---|---|
| Carrier | PCB + assembly | `carrier/carrier-gerbers.zip`, `carrier-bom.csv`, `carrier-cpl.csv` |
| Keyboard | PCB + assembly | `keyboard/keyboard-gerbers.zip`, `keyboard-bom.csv`, `keyboard-cpl.csv` |
| Top plate | PCB only | `keyboard-topplate/keyboard-topplate-gerbers.zip` |
| Keyboard cable | Flex PCB only | `keyboard-flex/keyboard-flex-gerbers.zip` (includes the stiffener layer `pib_0.225`) |

The zips hold the same Gerbers that `gerber_check.py` compares with the board files, renamed to the Protel
extensions JLCPCB's KiCad guide asks for. The BOM has the four columns JLCPCB wants (Comment, Designator,
Footprint, LCSC Part #) and leaves out every part marked DNP.

## 2. Carrier

On the PCB form:

| Field | Choose | Why |
|---|---|---|
| Layers | 4 | |
| Dimensions | 71.6 x 66 mm (read from the file) | |
| Quantity | 5 (the minimum) | |
| Thickness | 1.0 mm | The enclosure stack is built on it |
| Impedance control | Yes, stack-up **JLC04101H-3313** | The USB and display pairs are drawn for it |
| Surface finish | ENIG | 0.4 mm-pitch sockets |
| Outer / inner copper | 1 oz / 0.5 oz | |
| Via covering | Tented | |
| Min via hole / diameter | 0.2 mm / 0.45 mm (read from the file) | |
| Remove order number | "Specify location" is not prepared in the silkscreen; pick "Yes" (small fee) or accept the number anywhere | |
| Confirm production file | Yes | You see what they will build before they build it |

On the assembly form:

| Field | Choose | Why |
|---|---|---|
| PCBA type | **Standard** | Economic does one side and standard stack-ups only |
| Assembly side | Both | |
| PCBA quantity | 5, or 2 to spend less on parts | The fixed fees are the same either way |
| Edge rails / fiducials | Added by JLCPCB | See the first caution below |
| Confirm parts placement | Yes ($0.45) | |
| Through-hole | Let them hand-solder J10 (the battery header) | Otherwise it is the one part to solder at home |

Then upload the BOM and the CPL. In the parts list, every line should match a part in stock; the BOM was written
from parts that were in stock when `make_bom.py` last ran.

**Look at the placement preview before paying.** JLCPCB's part library sometimes turns a part 90 or 180 degrees
against KiCad's convention. Their engineers correct this from the silkscreen, but check these yourself: the pin-1
dot of every IC (U2-U13), the diodes and LEDs (D1-D13), the USB-C socket and the jack facing outward, the two
100-pin sockets, and the three connectors on the display side (J4, J5 and the parts round U13).

Cautions to put in the order remark, in your own words:

1. **The board is 66 mm on one side and Standard assembly lists 70 x 70 mm as the smallest single board.** JLCPCB
   says it adds edge rails for smaller boards. The USB-C socket, the jack and the card slot overhang one edge and
   the buttons sit at another, so ask them to put the rails where no part overhangs, or to tell you if they cannot.
2. **Clearances go down to 0.09 mm (3.54 mil)**; tracks are 0.1 mm or wider. JLCPCB charges 20 % more for 4-layer
   boards with track or gap of 3.0-3.5 mil. This design is just on the cheap side of that line; if their checker
   disagrees, that is the reason.
3. The two DF40C-100DS sockets are 0.4 mm pitch: ask for X-ray or careful inspection of them.

## 3. Keyboard

PCB form: 2 layers, 125 x 69 mm, 5 pieces, **1.0 mm**, ENIG, vias tented. Assembly: top side only; try
**Economic** first (JLCPCB's pages do not say whether a 1.0 mm ENIG board qualifies; if the form refuses, use
Standard). Upload the BOM and the CPL.

Put this in the remark: "Alps SKSWCFE010 tact switches: maximum two reflow passes, no board washing, no flux on
the switch tops, solder paste 0.08 mm."

Not fitted by the fab: the four M1.6 spacers H1-H4 (Wurth 9774015633R, not stocked at JLCPCB). Buy them at DigiKey
and solder them by hand.

## 4. Top plate

PCB only: 2 layers, 125 x 31 mm, 5 pieces, **0.8 mm**, any finish, black solder mask. Remark: "Internal cut-outs
are intentional; webs between them are 1.2 mm; please rout, do not V-cut."

## 5. Keyboard cable

Flex PCB form: 1 layer, 4.5 x 79 mm, 5 pieces (ask for a panel if offered), 0.07 mm, 18 um copper, yellow
coverlay, ENIG. Stiffener: polyimide, 0.225 mm; the areas are in the Gerber layer `pib_0.225` (bottom side, 4 mm
at each end). Outline tolerance +/- 0.05 mm if it can be asked for: the 4.5 mm width has to fit the connector.

## 6. Order of work

1. Keyboard, top plate and cable first. They are cheap and they let the slider and the keys be tried.
2. The carrier, the module, the panel and the battery together, so the checks that need parts
   ([docs/open-questions.md](../docs/open-questions.md)) happen on the first build.
3. An assembly order is paid when it is placed: that is what reserves the parts.

## 7. What it will cost

See [purchasing.md](purchasing.md). Most of JLCPCB's board prices are not published; the estimate there is built
from the fees that are, and is marked where it is a guess. Orders shipped to the USA carry a 35 % tariff collected
at checkout (JLCPCB's notice of 2026-03-17).

## Sources

- Files and KiCad settings: https://jlcpcb.com/help/article/how-to-generate-gerber-and-drill-files-in-kicad-9 and
  https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad
- Economic and Standard assembly: https://jlcpcb.com/capabilities/pcb-assembly-capabilities
- Assembly fees: https://jlcpcb.com/help/article/pcb-assembly-price
- Edge rails: https://jlcpcb.com/help/article/how-to-add-edge-rails-fiducials-for-pcb-assembly-order
- Extra charges: https://jlcpcb.com/help/article/in-what-cases-will-there-be-charged-extra
- Flex stiffeners: https://jlcpcb.com/help/article/fpc-stiffener-emi-guide
- US tariff: https://jlcpcb.com/help/article/us-tariff-policy-faq
