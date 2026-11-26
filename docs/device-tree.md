# Device-tree requirements for rev 0.1

What the kernel has to be told about this carrier, collected from the schematic notes so that none of it is
found by accident during bring-up. Pin numbers are CM4 connector pins; the SoC GPIO behind each pin comes from the
module vendor's own device tree (LuckFox publishes no mainline one for the Core3566, see
[compute-pin-matrix.md](compute-pin-matrix.md)). Nothing here has run on hardware.

## Things that protect hardware: get these right first

| Node | Property | Value | Why |
|---|---|---|---|
| Charger `ti,bq25895` at 0x6A on I2C B | `ti,use-ilim-pin` | present | R12 (470 ohm) caps the input current at 0.83 A. With that cap the pack gets at most about 1.25 A even at the charger's reset charge current, with no software at all. Without the property the driver switches the cap off |
| | `ti,charge-current` | 1250000 (uA) or less | Pack limit 1.4 A |
| | `ti,battery-regulation-voltage` | 4200000 | |
| | `ti,termination-current`, `ti,precharge-current` | 128000, 256000 | Pack: 2800 mAh |
| | `ti,minimum-sys-voltage` | 3500000 | Boost turns off below 3.0 V at VSYS |
| | `ti,boost-voltage`, `ti,boost-max-current` | 5000000, 500000 | Required by the binding. The port is sink-only: OTG is strapped off (pin OTG low), so these are never used |
| | interrupt | pin 34, falling | |
| | adapter detection | nothing to set | D+/D- are not connected to the charger (R21/R22 unfitted), so it cannot ask an adapter for 9-12 V whatever the driver does |
| SD card `sdmmc` | `no-1-8-v` (no `sd-uhs-*`) | present | The card's I/O is fixed at 3.3 V on the carrier |
| | `broken-cd` | present on Core3566 | Pin 76 is not connected on that module |
| Backlight `pwm-backlight` | PWM period | 40000 ns (25 kHz); allowed 10000-200000 | The TPS61169 reads its CTRL pin as PWM only between 5 and 100 kHz; slower than that it sees one-wire commands or shuts down |
| | PWM pin | pin 48 (Core3566: PWM14_M0) | Pulled low by R43: dark until driven |

## The rest

| Function | Driver / compatible | Bus, address | Pins | Notes |
|---|---|---|---|---|
| Fuel gauge | `maxim,max17048` (`max17040_battery`) | I2C B, 0x36 | alert: pin 40, falling | `maxim,alert-low-soc-level` as wanted |
| Battery fuse flag | `gpio-keys` or a plain input | | pin 58, low while U13 is limiting or has tripped | Useful in the log during bring-up |
| Codec | `everest,es8316` with `simple-audio-card` | I2C B, 0x10 | I2S on pins 25-30 and 49 (Core3566: I2S3_M1, straps R50-R54); interrupt pin 44 | MCLK must run whenever the codec is open. Headphone detect: pin 50, and the codec's own pin |
| Keyboard | `ti,tca8418` (`tca8418_keypad`) | I2C B, 0x34 | interrupt pin 37 (falling), reset pin 45 (low = reset) | `keypad,num-rows` 6, `keypad,num-columns` 10; the keymap is in chip rows and columns, see [keyboard.md](keyboard.md) |
| Panel | `panel-sitronix-st7701` | DSI, 2 lanes | reset pin 31; TE pin 46 (unused by the driver) | 480 x 800. **No entry for the Focus E40RB-I-MW430-CB exists**: one has to be written from Focus's initialisation file. Supplies are always on |
| Touch | `goodix,gt911` | I2C A, 0x5D or 0x14 | interrupt pin 24, reset pin 28 | Address is chosen by the reset/interrupt sequence the driver performs |
| Volume keys | `gpio-keys` | | pins 38, 39, active low | Pulled up on the carrier |
| Power key | `gpio-keys`, `KEY_POWER`, wake-up source | | pin 41, active low | The same button also reaches the charger's /QON (12-18 s: battery disconnect) |
| Slider | `gpio-keys`, `SW_KEYPAD_SLIDE` | | pin 47, low = closed | Hall switch on the carrier, magnet in the tray |
| Activity LED | `gpio-leds` | | pin 21, active low | |
| Console | `stdout-path` | UART on pins 55 / 51 | | Core3566: UART2, 1,500,000 baud |
| USB | `dr_mode = "peripheral"` (or `otg` with ID on pin 101) | | | The carrier does not supply VBUS, so host mode needs a powered hub; VBUS presence can be taken from the charger (`usb-phy` / extcon) |

## Not in the device tree

Ship mode (charger BATFET off for storage) needs an I2C write from userspace or a driver patch (audit item P9).
