# Footprint review sheet

Every land pattern against its manufacturer drawing. The "Found" column records the checks of 2026-11-25: an
independent reviewer (an AI agent working from the drawings, not from the author's notes) went through the
footprints pad by pad, a second one fetched the five drawings the first could not get, and the module's own 3D
model was laid over the board's socket and spacer positions. No person has repeated these. The cheap last check is
still worth doing: order a few of each connector before the boards and lay them on a 1:1 print.

## 1. Hirose DF40C-100DS-0.4V(51), carrier J1A/J1B (the module sockets)

Document: Hirose DF40 catalogue, receptacle recommended PCB layout (p.3).

| Check | Expected | Found |
|---|---|---|
| Pad size | 0.20 x 0.70 mm | matches |
| Pitch along the row | 0.40 mm, 50 pads per row | matches |
| First to last pad, centre to centre | 19.6 mm | matches |
| Row centres apart | 3.08 mm (outer span 3.78, inner gap 2.38) | matches |
| No copper between the rows | Rule areas `df40_no_copper` on F.Cu | present; the router honours them |
| On the board: J1A pad 1 to J1B pad 1 | 33.92 mm apart, both at the same end | matches the CM4IO board. LuckFox's 3D model of the Core3566 has its two plugs 34.00 mm apart: 0.04 mm per side, inside what the connector takes up |
| On the board: spacers H1-H4 | 48 x 33 mm rectangle, connectors centred between the 33 mm pair | matches the Core3566 model: holes 48 x 33 mm, plugs 2.51 mm off the hole centre along the long axis (board: 2.50) |
| Module pin 1 lands on J1A pad 1 | Lay a real module (or a 1:1 print of the CM4 drawing, viewed from the top) on a 1:1 print of the F side | numbering, row order and absence of mirroring checked against the CM4IO board files. The 3D model does not mark pin 1: look at the real module once before it is pressed on |

Note: the module is turned 180 degrees in the carrier frame compared with the Raspberry Pi IO board. J1A is the
connector nearer the bottom edge.

## 2. Hirose FH34SRJ-20S / -8S (carrier J4, J5, J9; keyboard J1)

Document: Hirose FH34 catalogue p.5.

| Check | Expected (20 / 8 way) | Found |
|---|---|---|
| Signal lands | 0.30 x 0.80 mm on 0.50 pitch | matches |
| First to last signal land | 9.5 / 3.5 mm | matches |
| Hold-down lands | 0.40 x 0.80 mm, centres **2.5 mm** in front of the signal row (3.3 mm from the outer edge of the signal lands to the outer edge of these: the drawing dimensions edges, not centres), 11.5 / 5.5 mm apart | Checked against Hirose FH34 catalogue p.5 on 2026-11-25; an earlier 3.3 mm centre distance was wrong |
| Which side the cable enters | The hold-down side (the actuator is at the signal-row side) | as drawn in the catalogue |
| Contact 1 | At the right when the signal row is at the top and the opening at the bottom | as drawn in the catalogue |

## 3. Keystone 5135 dome

Document: Keystone catalogue p.97, and Keystone's Mini-series land drawing (to be requested).

| Check | Expected | Found |
|---|---|---|
| Dome | Four legs, 8.4 mm tip to tip, 7.0 mm across flats, feet on an 8.0 mm circle | |
| Our lands | Centre 3.0 mm; four 1.8 mm foot pads at (+/-2.83, +/-2.83). **Non-standard** | |
| Keystone's lands | Five 3.0 mm pads; outer circle drawn as 9.5 mm, which looks copied from a larger series | |
| Does a dome sit on our lands without bridging to the next column? | 0.84 mm between foot pads of neighbouring columns | |

Do not order the dome board until this is settled. It is an alternative, not part of rev 0.1: the Alps switch
board (`hardware/keyboard`) is the one to build.

## 4. Sunlord inductors L1, L2, L3

Document: Sunlord MWSA and SWPA catalogues. The audit found all three KiCad footprints match exactly.

| Part | Body | Land pattern | Rating to confirm |
|---|---|---|---|
| L1 MWSA0402S-2R2MT | 4.2 x 4.4 x 1.8 | 1.5 x 2.5, gap 2.2 | Isat 4.0 A guaranteed |
| L2 MWSA0402S-1R0MT | 4.2 x 4.4 x 2.0 | same | Isat 5.6 A guaranteed (changed from the 0412S after the audit) |
| L3 SWPA4030S100MT | 4.0 x 4.0 x 3.0 | 1.1 x 3.7, gap 1.9 | Isat 1.95 A guaranteed |

Sunlord's "max" column is the guaranteed lower figure; LCSC listings quote either one.

## 5. The rest

| Part | Drawing | Found |
|---|---|---|
| Molex 5268-03A battery header (J10) | Molex 52680001-SD rev B | Pitch 2.5, hole 0.85 for a 0.7 pin, body 9.9 x 7.9 with 6.6 mm in front of the pin row, circuit 1 position: all match. The mated plug reaches 11.6 mm from the pin row, which the keep-out in `carrier_pcb.PLUG` and the enclosure model allow for |
| JST SM03B-SRSS-TB debug socket (J8) | JST SH catalogue 2024-10 | Signal pads 0.6 x 1.55 on 1.0 pitch, mounting pads 1.2 x 1.8 at +/-2.3, circuit 1: all match |
| MAX17048 (U4), TDFN-8 2 x 2 | Maxim 21-0168 rev M, 90-0065 rev E | Pitch, row spacing and pin 1 match. Pads 0.25 x 0.775 against Maxim's 0.30 x 0.70 and exposed pad 0.8 x 1.2 against 0.8 x 1.38: inside the package tolerances, solderable |
| Wuerth spacers 9774015151R (carrier), 9774015633R (keyboard) | Wuerth datasheets 2020 | Hole, solder ring and stencil match. Both 1.5 mm high. The M2.5 part's boss is 1.4 mm long: it shows 0.4 mm on the display side of the 1.0 mm carrier (room there: 1.6 mm). The M1.6 part's 0.7 mm boss stays inside the keyboard board. Paste 0.15 mm or thicker for the M2.5 part |
| 1N4148W4 keyboard diodes | BORN datasheet 2022-01 | 0.45 / 0.50 / 0.55 mm high. The keycap flange comes down to 0.77 mm when pressed: 0.22 mm to spare |
| The ICs (charger, boost, backlight driver, fuse, codec, keyboard scanner, USB ESD part) | Their datasheets | The first reviewer compared every IC land pattern that had a drawing: all match. The TPS61230 is on TI's older land pattern (exposed pad 0.15 mm oversize): solderable. USB-C, microSD and the buttons use KiCad's stock footprints for the exact part numbers |
| PJ-342 jack (J6) | Shouhan drawing | Pads match after one fix (pad 4 is 2.6 mm long). **Open:** whether the part has four poles (its circuit diagram) or three (its outline). Headphones work either way; the microphone needs four. Straps R60-R63 choose which terminal is the sleeve |
