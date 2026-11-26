# Layout notes — 289 MAPBGA (14 x 14 mm, 0.8 mm pitch, 17 x 17 full matrix) and JLCPCB 6-layer facts

Sources: **HDUG** MIMXRT1170HDUG Rev 2 section 7 (p.18-21); **EVKBHUG** MIMXRT1170EVKBHUG Rev 4 section 3 Table 7; **LAY** LAY-55139 C1
(EVKB artwork/fab drawing PDF, page 3 fab notes and page 14 via-fill film; text layer); JLCPCB pages read on **2026-11-26** (saved as
`src/jlcpcb_*.html`).

## 1. What the NXP hardware guide says

| Topic | Statement | Where |
|---|---|---|
| Layer count | "The recommended stackup is six layers" (the EVK stack-up, Figures 4 and 5). No 4-layer stack-up is offered or discussed. | HDUG 7.1 |
| Material | NXP reference and validation boards: Isola FR4 | HDUG 7.1 |
| Via, BGA area | "18/8 mils" (pad / drill = 0.457 / 0.203 mm), trace width 4 mil (0.102 mm), trace space 3.79 mil (0.096 mm) | HDUG 7.2 |
| Via, rest of board | 18/8 mil via, 7 mil trace, 7 mil space | HDUG 7.2 |
| Decoupling | 0402 decouplers and 0603 bulk capacitors on the bottom side under the CPU, as close to the power balls as possible; per-ball placement in HDUG Table 1 (power.md section 6) | HDUG 7.2 |
| SDRAM | 50 ohm, two groups (data+DM; address+control), one on top referenced to L2 GND and one on bottom referenced to L5 GND, +-50 mil, copy EVK lengths | HDUG 7.4 |
| USB | 90 ohm differential, on top or bottom, pair mismatch < 5 mil, no layer changes/stubs, ground vias within 50 mil of any transition | HDUG 7.5 |
| FlexSPI | DQS pad floating for QSPI at 133 MHz | HDUG 7.3 |
| General | no plane gaps under high-speed nets, return vias within 100 mil, solid GND under crystals, clock spacing 2.5 x dielectric height | HDUG 7.7 |
| **Which ball rows escape on which layer** | **Not stated.** The guide gives only the via/trace geometry above and points to "the preferred BGA power-decoupling design layout ... at www.nxp.com". | HDUG 7.2 |

Not obtained: the HDUG stack-up figures as numbers (they are images; the numbers below come from the EVKB documents instead), NXP's BGA
land-pattern/solder-mask recommendation for this package (the data sheet package drawing, Figure 55, is an image and was not transcribed),
and the EVKB board file (only artwork PDF), so an NXP fan-out per ball row cannot be quoted.

## 2. The EVKB as built (6 layers, 62.4 mil)

EVKBHUG Table 7 and LAY fab-drawing stack-up detail (both agree):

| Layer | Use | Copper | Dielectric below |
|---|---|---|---|
| L1 (L1_PS) | signal | 1/2 oz (1.8 mil finished) | 3.5 mil |
| L2 (L2_GND_1) | GND plane | 1 oz (1.2 mil) | 5 mil |
| L3 (L3_INT_1) | signal | 1 oz | 37 mil |
| L4 (L4_PWR_1) | power plane | 1 oz | 5 mil |
| L5 (L5_GND_2) | GND plane | 1 oz | 3.5 mil |
| L6 (L6_SS) | signal | 1/2 oz (1.8 mil finished) | — |

LAY impedance table (tolerance 10 %): on L1 (ref L2), L3 (ref L2 and L4) and L6 (ref L5): 50 ohm single-ended = 5.0 mil; 90 ohm
differential = 4.7 mil width / 5.0 mil space; 100 ohm differential = 4.2 mil / 6.0 mil.
LAY drill chart: 8.0 mil finished plated holes x 2279 (ordinary vias); **8.1 mil x 171 + 36 = 207 via-in-pad vias**, fab note 22: "THIS BOARD
USES VIA-IN-PAD ... all vias using X.1 drill sizes are to be filled with non-conductive via fill ... overplate the filled via ... dimple or
protrusion no greater than .001 in". Finish ENIG both sides.
So NXP's own board uses three signal layers (L1, L3, L6), two ground planes, one power plane, 8 mil drills and filled via-in-pad.
Which of those 207 filled vias sit under the MCU was not determined (would need the board file or rendering the via-fill film).

## 3. JLCPCB capability facts (read 2026-11-26)

From https://jlcpcb.com/capabilities/pcb-capabilities (`src/jlcpcb_capabilities_pcb-capabilities.html`):

| Item | Published value |
|---|---|
| Min track / space, 1 oz, multilayer | 0.09 / 0.09 mm (3.5 / 3.5 mil); "3 mil is acceptable in BGA fan-outs" |
| Min via hole / via diameter | 0.15 / 0.25 mm; 0.1 / 0.2 mm only for board thickness <= 1 mm with ENIG/OSP |
| Via diameter rule | at least 0.1 mm (0.15 mm preferred) larger than the hole; "Preferred Min. Via hole size: 0.2mm" |
| Extra-cost vias | "0.1mm or 0.15mm hole size with any size via diameter, and 0.2mm or 0.25mm hole size with via diameter less than 0.45mm, will cost more" |
| BGA | pad diameter down to 0.2 mm (0.2-0.25 mm needs ENIG); pad-to-trace clearance >= 0.1 mm (0.09 mm minimum on multilayer); "Vias can be placed within BGA pads using filled and plated-over vias" |
| Via-in-pad process | "Epoxy Filled & Capped" / "Copper paste Filled & Capped": "Vias are filled with epoxy resin or copper paste and then plated over"; **"This process is the default for 6-layer and above multilayer boards"**; "Compatible with via diameters from 0.15 to 0.55 mm"; "Filled vias must be no wider than 0.5 mm diameter" |
| Controlled impedance | offered on 4/6/8/... layers, tolerance +-10 % |
| Hole position tolerance | +-0.075 mm |

Cost and requirements of via-in-pad:
* https://jlcpcb.com/help/article/pcb-via-covering (page says "Last updated on Nov 10, 2026"): "For our 6-layer and above multi-layer
  boards, resin filling is now available for free"; plugged and epoxy-filled via holes "should not be larger than 0.5 mm"; leave a note or
  image saying which vias are to be filled.
* https://jlcpcb.com/news/free-via-in-pad-6-20-layer-pcbs-pofv (dated Nov 02, 2022): via-in-pad on 6-20 layer boards upgraded to POFV
  (plated over filled via) "for free ... the free default"; filled vias "should be placed more than 0.45 mm from regular PTHs or NPTHs".
* The stated 0.2 mm drill / 0.45 mm pad via is therefore the smallest via that avoids the extra-cost class, and on a 6-layer order it can
  sit in a BGA pad at no extra charge according to these pages. Prices were not obtained (the quote form needs an order).

Impedance stack-ups, https://jlcpcb.com/impedance (`src/jlcpcb_impedance.html`):
* The page offers 6-layer controlled-impedance stack-ups for finished thickness **1.2 mm, 1.6 mm and 2.0 mm**. **No 1.0 mm 6-layer
  option is listed** (4-layer has 0.8/1.0/1.2/1.6/2.0 mm). Outer copper 1 oz or 2 oz; inner 0.5 oz, 1 oz or 2 oz.
* Only the default 1.6 mm tab is present in the static HTML that could be saved: codes JLC06161H-3313 (3313 prepreg 0.0994 mm outer, two
  0.55 mm cores, 2116 0.1088 mm centre), -7628 (7628 0.2104 mm, 0.4 mm cores), -1080 (1080 0.0764 mm, 0.55 mm cores), -2116A, -1080A/B/C,
  -3313A/B/C/D/E, -2116/B/C, -7628A/B/D; copper 0.035 mm outer, 0.0152 mm inner.
* **Not obtained: the 1.2 mm 6-layer stack-up codes and their prepreg/core thicknesses** (loaded by script when the 1.2 mm tab is
  selected). They must be read from the page or the JLCPCB impedance calculator before trace widths are fixed.

## 4. Geometry check for 0.8 mm pitch (COMPUTED from the figures above, not from a source)

* Ball pitch 0.8 mm; diagonal 1.131 mm. NXP's via for the BGA area (0.457 mm pad / 0.203 mm drill) placed at the centre of four pads
  leaves (1.131 - land - 0.457) / 2 to each land; with an assumed 0.40 mm land (assumption — NXP's land size was not obtained) that is
  0.137 mm, above JLCPCB's 0.09-0.1 mm pad-to-trace/clearance class, so classic dog-bone fan-out with the 0.2 / 0.45 mm via is possible
  without via-in-pad.
* Between two adjacent lands the channel is 0.8 - land = 0.40 mm (same assumption): one 0.09-0.10 mm track fits with 0.15 mm each side;
  two 0.09 mm tracks need 0.45 mm and do not fit.
* A full 17 x 17 matrix with one track per channel lets the outer two rows escape on the top layer; deeper rows need vias and inner or
  bottom layers. NXP's board does it with three signal layers.
