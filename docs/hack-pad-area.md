# Hack pad: does it all fit on one board? (estimate, 2026-11-26)

Not a layout. Footprint outlines of the parts in the schematic were added up by script; the blocks not drawn yet
are rough allowances.

| | mm² |
|---|---|
| Board, one side (125 x 69) | 8,625 |
| Battery lying against the underside (76.5 x 61.5) | 4,705 |
| Underside left for parts | about 3,900 |
| Parts drawn so far, outlines only (brain, memory, power, card, audio, connectors; not the keys) | 1,975 |
| Unfitted second memory bank | 225 |
| Radios, SDR, sensors, bench tools still to draw (allowance) | 2,500 to 3,000 |
| Outlines in all | about 4,700 to 5,200 |
| Board area that needs at a dense 50 % fill | about 9,400 to 10,400 |

The key side can take only parts under about 0.5 mm between the switches (small resistors and capacitors), so nearly
all of this has to go on the underside, where about 3,900 mm² is free: roughly 2.5 times too little. The NFC loop
(about 40 x 30 mm clear of copper and battery) is not even counted.

Ways out, each with its cost (decision for David):

1. Battery under the parts instead of beside them: everything fits; about 2 mm thicker (about 15.5 mm).
2. A battery of about half the area (about 1,000 mAh): frees about 2,300 mm²; still short unless features go too.
3. A second thin board behind the e-paper in the lid for the radios and antennas: good for reception, keeps the
   keyboard half thin; the lid grows from about 3 mm to about 5.5 mm and the slider cable carries more.
4. Fewer features on the first board (leave off the wide-range converter, the extended sensors, some radios).
