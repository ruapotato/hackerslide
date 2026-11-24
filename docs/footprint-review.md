# Footprint review sheet

For a human with the datasheet open. Each row is one thing to measure in KiCad's footprint editor (or on a 1:1
print with the real part laid on it) against one page of one document. Tick it or write what you found.
Order a few of each part before the boards and print the boards 1:1 on paper first.

## 1. Hirose DF40C-100DS-0.4V(51), carrier J1A/J1B (the module sockets)

Document: Hirose DF40 catalogue, receptacle recommended PCB layout (p.3).

| Check | Expected | Found |
|---|---|---|
| Pad size | 0.20 x 0.70 mm | |
| Pitch along the row | 0.40 mm, 50 pads per row | |
| First to last pad, centre to centre | 19.6 mm | |
| Row centres apart | 3.08 mm (outer span 3.78, inner gap 2.38) | |
| No copper between the rows | Rule areas `df40_no_copper` on F.Cu | |
| On the board: J1A pad 1 to J1B pad 1 | 33.92 mm apart, both at the same end | |
| On the board: spacers H1-H4 | 48 x 33 mm rectangle, connectors centred between the 33 mm pair | |
| Module pin 1 lands on J1A pad 1 | Lay a real module (or a 1:1 print of the CM4 drawing, viewed from the top) on a 1:1 print of the F side | |

Note: the module is turned 180 degrees in the carrier frame compared with the Raspberry Pi IO board. J1A is the
connector nearer the bottom edge.

## 2. Hirose FH34SRJ-20S / -8S (carrier J4, J5, J9; keyboard J1)

Document: Hirose FH34 catalogue p.5.

| Check | Expected (20 / 8 way) | Found |
|---|---|---|
| Signal lands | 0.30 x 0.80 mm on 0.50 pitch | |
| First to last signal land | 9.5 / 3.5 mm | |
| Hold-down lands | 0.40 x 0.80 mm, centres 3.3 mm in front of the signal row, 11.5 / 5.5 mm apart | |
| Which side the cable enters | The hold-down side (the actuator is at the signal-row side) | |
| Contact 1 | At the right when the signal row is at the top and the opening at the bottom | |

## 3. Keystone 5135 dome

Document: Keystone catalogue p.97, and Keystone's Mini-series land drawing (to be requested).

| Check | Expected | Found |
|---|---|---|
| Dome | Four legs, 8.4 mm tip to tip, 7.0 mm across flats, feet on an 8.0 mm circle | |
| Our lands | Centre 3.0 mm; four 1.8 mm foot pads at (+/-2.83, +/-2.83). **Non-standard** | |
| Keystone's lands | Five 3.0 mm pads; outer circle drawn as 9.5 mm, which looks copied from a larger series | |
| Does a dome sit on our lands without bridging to the next column? | 0.84 mm between foot pads of neighbouring columns | |

Do not order the dome board until this is settled.

## 4. Sunlord inductors L1, L2, L3

Document: Sunlord MWSA and SWPA catalogues. The audit found all three KiCad footprints match exactly.

| Part | Body | Land pattern | Rating to confirm |
|---|---|---|---|
| L1 MWSA0402S-2R2MT | 4.2 x 4.4 x 1.8 | 1.5 x 2.5, gap 2.2 | Isat 4.0 A guaranteed |
| L2 MWSA0402S-1R0MT | 4.2 x 4.4 x 2.0 | same | Isat 5.6 A guaranteed (changed from the 0412S after the audit) |
| L3 SWPA4030S100MT | 4.0 x 4.0 x 3.0 | 1.1 x 3.7, gap 1.9 | Isat 1.95 A guaranteed |

Sunlord's "max" column is the guaranteed lower figure; LCSC listings quote either one.

## 5. Others worth a look

| Part | Check |
|---|---|
| PJ-342 jack (J6) | Lay the part on a print. Then buzz out which terminal is the sleeve: terminals 2 and 5 are assumed ring2 and sleeve |
| MAX17048 (U4) | TDFN-8 2 x 2 mm land pattern against Maxim 90-0065 |
| TCA8418 (keyboard U1) | Exposed pad 2.45 mm |
| ES8316 (U7) | 0.25 mm between the pads and the exposed pad |
| 1N4148W4 diodes | Height 0.5 mm or less: they sit under the keycap flanges |
| Wurth spacers | 9774015151R (carrier) and 9774015633R (keyboard): both 1.5 mm |
