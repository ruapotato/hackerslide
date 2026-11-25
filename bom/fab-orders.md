# Fab order sheets (JLCPCB)

**Do not order yet.** The carrier is only partly routed (87 connections open, power and high-speed nets not
reviewed), the keyboard has one open connection, and no Gerbers exist. These sheets
record what each order needs, so they can be checked now. Capabilities quoted are from
[JLCPCB's capability pages](https://jlcpcb.com/capabilities/pcb-capabilities) and
[flex capabilities](https://jlcpcb.com/capabilities/flex-pcb-capabilities), read 2026-11-24.

## 1. Carrier (`hardware/carrier`)

| Setting | Value | Why |
|---|---|---|
| Size | 71.6 x 66.0 mm, 3 mm corner radius, no slots | |
| Layers | 4 | DSI and USB pairs over a solid ground plane |
| Thickness | 1.0 mm | Sets the enclosure stack |
| Stack-up | Impedance-controlled stack-up, *to be chosen* | The DSI (100 ohm) and USB (90 ohm) widths in `carrier_pcb.py` are placeholders: `TODO(verify)` with JLCPCB's impedance calculator before routing |
| Copper | 1 oz outer, 0.5 oz inner | |
| Min track / space | 0.09 / 0.09 mm in the rules; 0.1 mm used | The 0.4 mm-pitch DF40 sockets need 0.1 mm work |
| Min via | 0.45 mm pad, 0.2 mm drill | |
| Finish | ENIG | 0.4 mm-pitch sockets and QFNs |
| Assembly | Both sides: everything on the F side, J4 and J5 (and three test points) on the B side | |
| Not fitted by the fab | J3 (solder pads), DNP resistors listed in the BOM | |
| Special parts | Two DF40C-100DS sockets: ask for X-ray or careful inspection. H1-H4 are SMT spacers | |

## 2. Keyboard (`hardware/keyboard`)

| Setting | Value | Why |
|---|---|---|
| Size | 125 x 69 mm | It is the tray floor |
| Layers | 2 | |
| Thickness | 1.0 mm | Structural: the bottom skin of the device |
| Finish | ENIG | Bare landing pads; and required if the dome variant is ever ordered |
| Solder mask | Both sides. Bottom: vias tented, no exposed copper | The bottom is touched by hands |
| Assembly | Top side only | Nothing is on the bottom |
| **Assembly note** | **"Alps SKSWCFE010: maximum two reflow passes, no board washing, no flux on the switch tops, solder paste 0.08 mm."** | Alps specification KSW-603, section 10 |
| Not fitted by the fab | H1-H4 (Wurth 9774015633R, not stocked): hand soldered | |

## 3. Top plate (`hardware/keyboard-topplate`)

2 layers, 0.8 mm, 125 x 31 mm, bare board, any finish, black solder mask suggested. Internal cut-outs for the
keycaps: the webs between them are 1.2 mm wide, so ask for routing rather than V-cut and expect a fragile part.
The 0.6 mm Fn legends are below JLCPCB's recommended silkscreen height and may print poorly.

## 4. Keyboard flex cable (`hardware/keyboard-flex`)

| Setting | Value | Why |
|---|---|---|
| Type | Flexible PCB, 1 layer | Thinnest and most bend-tolerant |
| Size | 4.5 x 73 mm | Under 20 x 20 mm is "best panelised" per JLCPCB; this is long but narrow, ask for a panel |
| Thickness | 0.07 mm (25 um polyimide) | Loop radius 1.9 mm is 27 x thickness; JLCPCB advises >= 10-15 x for repeated bending |
| Copper | 18 um (0.5 oz) | The thinnest offered on single-sided flex |
| Copper type | Ask for rolled-annealed if offered | JLCPCB's page does not say which is standard |
| Coverlay | Yellow | |
| Finish | ENIG | Contact fingers |
| Stiffener | Polyimide 0.225 mm on the BACK of both ends, 4 mm long | 0.07 + 0.225 = 0.3 mm, which the FH34SRJ connector needs (0.3 +/- 0.03) |
| Outline tolerance | +/- 0.05 mm on request | 4.5 mm width must fit the connector |

JLCPCB gives no flex-life figure. Cycle-test the cable on the fit mule before relying on it.

## Order of work

1. Route the keyboard and carrier; human review of both.
2. Board renders and Gerbers, drill, position and BOM files in JLCPCB format.
3. Order the keyboard, top plate and flex first (cheap, and they exercise the slider), then the carrier.
