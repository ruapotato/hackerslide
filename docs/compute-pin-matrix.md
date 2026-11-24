# Compute module pin matrix

CM4 pin numbers. Checked in the 2026-11-24 audit against the LuckFox Core3566 datasheet, the Raspberry Pi CM4
datasheet, the Radxa CM4 schematic v1.20 and the ArmSoM-CM5 pin list (2024-04-22). The BigTreeTech CB2 column is
from its user manual. No Core3566 schematic is published, so its I/O domains and strap pins are unconfirmed.

**Supported in rev 0.1: LuckFox Core3566 (default) and Radxa CM4 (RK3576).** ArmSoM-CM5 boots with a different
resistor stuffing but has no backlight PWM and no audio. BigTreeTech CB2 is not supported.

| Function | Pins | Core3566 | Radxa CM4 | ArmSoM-CM5 | CB2 |
|---|---|---|---|---|---|
| 5 V in | 77-87 odd | yes | yes | yes | yes |
| 3.3 V / 1.8 V out | 84, 86 / 88, 90 | 600 mA each | 600 mA each | not confirmed | **200 / 100 mA** |
| GPIO reference | 78 | VREF, must not float | supplies VCCIO3/4 | **VRTC** | NC |
| DSI, 4 lanes (2 used) | 175-189 | DSI1 | yes | yes | yes |
| USB 2.0 OTG | 103, 105; ID on 101 | true OTG | yes | yes | yes |
| SD card | 57, 61, 62, 63, 67, 69 | yes | yes | yes | yes |
| SD card detect | 76 | NC: use `broken-cd` | 1.8 V-only input | same signal | not checked |
| I2C A (touch) | 80, 82 | I2C1 | I2C0_M1 | I2C5_M3 | yes |
| I2C B (charger, gauge, codec, keyboard) | 35, 36 | I2C3_M1 | I2C6_M3 | I2C4_M3 | I2C1 |
| Debug UART | 55 TX, 51 RX | UART2, 1.5 Mbaud | UART0 | **camera pins; UART on 54/56** | yes |
| I2S | 25, 26, 27, 29, 30, 49 | I2S3_M1 via R50-R54 | SAI2 via R55-R59 | **no mapping** | **different pins** |
| Backlight PWM | 48 | PWM14_M0 | PWM1_CH0_M2 | **TP_INT; PWM is on 41** | **no PWM** |
| Power key | 99 | **"GLOBAL_EN", reads as an output** | PWRON_L | PWRON_L | PMIC_PWRON |
| Reset | 92 | yes | yes | yes | labelled PWRON |
| Boot mode | 93 | low = loader | 0 V = maskrom | 0 V = maskrom | not checked |
| Activity LED | 21 | yes | yes | yes | yes |
| Plain GPIO | 24, 28, 31, 34, 37-41, 44-47, 50 | yes | yes, 3.3 V with pin 78 | 44/46 are I2C0 | 34 is NC |

## Carrier nets on the plain GPIO pins

| Pin | Net | Pin | Net |
|---|---|---|---|
| 24 | TOUCH_INT | 40 | GAUGE_INT |
| 28 | TOUCH_RST_N | 41 | PWR_KEY_N (the power button as a GPIO key) |
| 31 | LCD_RST_N | 44 | CODEC_IRQ |
| 34 | CHG_INT_N | 45 | KB_RST_N |
| 37 | KB_INT_N | 46 | LCD_TE |
| 38 | VOL_UP_N | 47 | SLIDE_DET (low = slider closed) |
| 39 | VOL_DN_N | 50 | HP_DET (jack detect, also on the codec) |

## Stuffing variants

| Module | Fit | Do not fit |
|---|---|---|
| Core3566 (default) | R30, R33, R34, R50-R54 | R35, R36, R55-R59 |
| Radxa CM4 | R30, R33, R34, R55-R59 | R35, R36, R50-R54 |
| ArmSoM-CM5 (boot and display only) | R35, R36 | R30, R33, R34, all I2S straps |

## Mainline device trees (torvalds/linux, read 2026-11-24)

| Module | Device tree |
|---|---|
| LuckFox Core3566 | none |
| Radxa CM4 (RK3576) | none |
| ArmSoM-CM5 | `rk3576-armsom-cm5.dtsi` |
| BigTreeTech CB2 | `rk3566-bigtreetech-cb2.dtsi` |

## To verify on a real Core3566

Pin 99 behaviour; that the GPIO bank really follows pin 78; SD and eMMC coexistence; module height.
