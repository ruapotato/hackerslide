# FCC modular approval for a handheld / wrist-worn device: which off-the-shelf radio modules can be used with only an SDoC for the host?

Research date: 2026-11-26. Read-only public web. All downloaded source files are in
`/var/tmp/hackerslide-agent/fcc/src/` (grant pages saved as `fccid_<FCCID>.html`; exhibits as `um_*`, `rfx_*`, `lwb_*` PDF + `.txt`; eCFR XML/text as `ecfr_*.{xml,txt}`; 10-1-2025 CFR PDF `cfr2025_1.1307.pdf`).

## How to read this report

- **[GRANT]** is the text of the grant itself. The FCC's own EAS (apps.fcc.gov/oetcf/eas) returned HTTP 503 or 403 to every automated request, so the grant texts were read from **fccid.io**. That site reproduces the TCB grant and, for most IDs, the FCC "EAS Grant ... COPY" page word for word (both are in the saved HTML). This is a secondary mirror of a primary document. Wherever both copies were present, the TCB copy and the EAS copy matched.
- **[EXHIBIT]** is a PDF exhibit from the FCC filing (user manual / integration guide, RF-exposure report), downloaded through fccid.io and read with `pdftotext`.
- **[eCFR]** is the current CFR text from the eCFR API (Title 47 up to date as of 2026-11-24). Formula images were read from the GPO 10-1-2025 CFR PDF.
- **[FCC-DOC]** is an FCC KDB or TCB-workshop document. apps.fcc.gov/kdb returned 403, so I used FCC-hosted workshop slides and a third-party mirror of KDB 996369 D04 v01 (newbtl.com). The current version is v02, which I could not open.
- **[SECONDARY]** is a web page or search snippet. **[MEMORY]** is my own background knowledge and has not been checked here.

---

## 0. Bottom line

1. **No Wi-Fi HaLow module checked has a grant that allows portable use (closer than 20 cm) by a third-party host.** This covers Quectel FGH100M, Morse Micro MM6108-MF08651, MF08251, MF16858, MM8108-MF15457, MM8108-M20-US, and AzureWave AW-HM593/AW-HM593W. Every grant says 20 cm. The one portable authorization in the HaLow family (2A74O-737B5B, MM8108-MF15457) was added by a **Class II permissive change with SAR testing, limited to Morse Micro's own USB dongle**, and its highest reported SAR was **1.58 W/kg**, just under the 1.6 W/kg limit. A HaLow radio held in the hand or to the ear therefore needs a C2PC by the grantee, or a change in ID plus C2PC, or a new FCC ID. It cannot go out on SDoC.
2. **None of the Espressif modules (ESP32-C6-MINI-1, C3-MINI-1, S3-MINI-1, PICO-MINI-02) allow portable use.** All are 20 cm, and the grants say "Separate approval is required for all other operating configurations, including portable configurations with respect to 2.1093".
3. **None of the Linux SDIO Wi-Fi/BT modules checked are portable-capable, except the original Laird/Ezurio Sterling-LWB (TFB-1003).** Its grant says "must be installed to provide the minimum separation distance specified in the filing in order to meet the SAR exemption threshold listed in KDB447498 and be authorized for portable or mobile operation". Its integration guide gives **29 mm** for portable use. Murata 1DX (VPYLB1DX) is a *limited* modular grant, "For professional installation only. Device shall not be sold to general public", and says "Use in portable RF exposure conditions will require additional filing for SAR compliance". The Sterling-LWB+ (SQG-LWBPLUS), Fn-Link 6223A-SRD (RTL8723DS) and BL-M8723DS1 (RTL8723DS) are all 20 cm. I found no FCC ID for AW-CM256SM.
4. **The Nordic-based BLE modules are the ones whose grants or filings cover portable use.**
   - **Raytac MDBT50Q** (nRF52840): grant says "This is a portable device". The manual allows 5 mm.
   - **Raytac MDBT53/MDBT53V** (nRF5340): the RF-exposure exhibit lists the chip/PCB antennas as "Portable", and the manual allows 5 mm. The grant text itself does not say portable.
   - **u-blox NINA-B3** (NINA-B31x): grant says "meets SAR test exclusion for host applications, where the radiating part is at least 10 mm away from the human body". A 2022 C2PC wording says 5 mm.
   - **u-blox NINA-B4**: the manual says "approved for installation into mobile and/or portable host platforms" with at least 5 mm. The grant text has no RF-exposure restriction.
   - **u-blox ANNA-B4**: the exhibit and manual say it is below the SAR exclusion at 0–5 mm. The grant text has no RF-exposure restriction.
5. **None of the LoRa modules allow portable use.** RAK3172 and Seeed LoRa-E5 / Wio-E5 / Wio-E5-LE are all 20 cm. Ebyte E22-900M22S *does* have an FCC ID (2ALPH-E22900M22S), but it is 20 cm with "Separate approval is required for ... portable configurations". It is also **granted at only 0.0076 W (about 8.8 dBm) conducted, with tune-up maximum 9.0 dBm**. Running the module at its rated 22 dBm would fall outside that grant.
6. **A host maker cannot rely on the §1.1307(b)(3) exemption to use a 20-cm-only module in a portable product without a filing.** §1.1307(b)(2) says the exemption is "solely from the obligation to perform a routine environmental evaluation ... it is **not exemption from the equipment authorization procedures described in part 2**". The grants themselves say "Separate approval is required for ... portable configurations". The FCC record shows hosts that clearly met the exemption still went through a C2PC (Sterling-LWB's GK001 host: 0.106 against the 3.0 limit, done by C2PC). The exemption calculation can be the *content* of a C2PC (no SAR test needed). It does not replace one.
7. **E-labelling (f): yes.** §2.935(a) allows a device with an integrated screen to show "the FCC Identifier ... or other information that the Commission's rules would otherwise require to be shown on a physical label". Espressif's and Ebyte's integration text explicitly says "physical or e-label stating 'Contains FCC ID: ...'". The FCC ID or model plus web page must still appear on the device or its packaging at sale (§2.935(f)).
8. **Hearing-aid compatibility (g): applies.** A handheld held to the ear making VoIP calls over Wi-Fi or HaLow to a publicly available service is a "Handset" used for "Digital mobile service", which the rule defines to include "both interconnected and non-interconnected voice over internet protocol (VoIP) services, to the extent that such service is provided over frequencies specified in the ... 2019 ANSI standard" (614 MHz–6 GHz, which covers 902–928 MHz and 2.4 GHz). The 2015 order expanded the scope to "a voice communications service over Wi-Fi". **From 14 Dec 2026 handset manufacturers can no longer claim de minimis status** (§20.19(e)(4)), and 100 % of handset models must meet 2019-ANSI acoustic coupling plus a second form (telecoil or Bluetooth) (§20.19(c)(2)).

---

## 1. Rules (primary text)

### 1.1 47 CFR 1.1307(b)(3)(i) [eCFR, current as of 2026-11-24; formula image read from GPO CFR 10-1-2025 ed., p. 294]

> (3) *Determination of exemption.* (i) For single RF sources (i.e., any single fixed RF source, mobile device, or portable device, as defined in paragraph (b)(2) of this section): A single RF source is exempt if:
>
> (A) The available maximum time-averaged power is no more than 1 mW, regardless of separation distance. This exemption may not be used in conjunction with other exemption criteria other than those in paragraph (b)(3)(ii)(A) of this section. Medical implant devices may only use this exemption and that in paragraph (b)(3)(ii)(A);
>
> (B) Or the available maximum time-averaged power or effective radiated power (ERP), whichever is greater, is less than or equal to the threshold P_th (mW) described in the following formula. This method shall only be used at separation distances (cm) from 0.5 centimeters to 40 centimeters and at frequencies from 0.3 GHz to 6 GHz (inclusive). P_th is given by:
>
> P_th (mW) = ERP_20cm · (d/20 cm)^x for d ≤ 20 cm; = ERP_20cm for 20 cm < d ≤ 40 cm
> where x = −log10( 60 / (ERP_20cm · √f) ) and f is in GHz; and
> ERP_20cm (mW) = 2040·f for 0.3 GHz ≤ f < 1.5 GHz; = 3060 for 1.5 GHz ≤ f ≤ 6 GHz;
> d = the separation distance (cm);
>
> (C) Or using Table 1 and the minimum separation distance (R in meters) from the body of a nearby person for the frequency (f in MHz) at which the source operates, the ERP (watts) is no more than the calculated value prescribed for that frequency. For the exemption in Table 1 to apply, R must be at least λ/2π ... [Table 1: 300–1,500 MHz: 0.0128 R²f; 1,500–100,000 MHz: 19.2 R²]

Multiple sources (ii)(A): each source ≤ 1 mW **and** 2 cm between radiating structures (or the sum below 1 mW). (ii)(B): the sum of each source's P_i/P_th,i plus ERP_j/ERP_th,j plus Evaluated_k/Limit_k must be ≤ 1.

Definitions in §1.1307(b)(2) [eCFR], quoted verbatim:

> *Available maximum time-averaged power* for an RF source is the maximum available RF power (into a matched load) as averaged over a time-averaging period;
> *Exemption* for (an) RF source(s) is solely from the obligation to perform a routine environmental evaluation to demonstrate compliance with the RF exposure limits in § 1.1310 of this chapter; **it is not exemption from the equipment authorization procedures described in part 2 of this chapter**, not exemption from general obligations of compliance with the RF exposure limits ...
> *Time-averaging period* is ... a time period inherent from device transmission characteristics not to exceed 30 minutes for mobile and portable RF sources;
> *Separation distance* (variable R in Table 1) is the minimum distance in any direction from any part of a radiating structure and any part of the body of a nearby person;

§2.1091(b) mobile: "...a separation distance of at least 20 centimeters is normally maintained...". §2.1093(b) portable: "...used in such a way that the RF source's radiating structure(s) is/are within 20 centimeters of the body of the user." [eCFR]

### 1.2 Computed P_th (formula above; "available maximum time-averaged power or ERP, whichever is greater")

| d | 915 MHz (ERP20 = 1866.6 mW, x = 1.4736) | 2450 MHz (ERP20 = 3060 mW, x = 1.9022) |
|---|---|---|
| 0.5 cm | **8.1 mW (9.1 dBm)** | **2.7 mW (4.4 dBm)** |
| 1.0 cm | 22.6 mW (13.5 dBm) | 10.3 mW (10.1 dBm) |
| 1.5 cm | 41.0 mW (16.1 dBm) | 22.2 mW (13.5 dBm) |
| 2.5 cm | 87.2 mW (19.4 dBm) | 58.6 mW (17.7 dBm) |
| 5 cm | 242.0 mW (23.8 dBm) | 219.0 mW (23.4 dBm) |
| (10 cm) | 672 mW | 819 mW |
| (20 cm) | 1867 mW | 3060 mW |

What this means for the modules. These are time-averaged figures, and a duty-cycle reduction is allowed when it is inherent to the device:
- A HaLow module at full power (MF08651 0.51 W / 0.96 W conducted; FGH100M 0.14 W) is far above P_th at any handheld distance. At about 1 cm from the hand, 915 MHz allows about 22 mW time-averaged.
- A 0 to +8 dBm BLE module at 5 mm is at or near 2.7 mW. The Raytac and u-blox filings used the older KDB 447498 v06 "3.0" test-exclusion formula at 5 mm.
- An ear-held HaLow handset would have to average about 8 mW (0.5 cm) to 23 mW (1 cm). VoIP talk at the full module power would exceed that.

Note: KDB 447498 v06 allowed 2.5 times the 1-g figure for 10-g extremity (hand/wrist) exposure ("≤ 7.5 for 10-g extremity SAR", quoted in the Raytac/u-blox exhibits). The §1.1307(b)(3)(i)(B) rule text has no extremity multiplier. Whether KDB 447498 D04 still allows one, I could not confirm because the KDB site blocked access [MEMORY: D04 has an extremity provision; unverified].

### 1.3 Can a host use a mobile-only (20 cm) module in a portable host if it is under the exemption? [eCFR + FCC-DOC + GRANT]

**Short answer: not without a filing.** The evidence:

- §1.1307(b)(2) [eCFR]: exemption "is not exemption from the equipment authorization procedures described in part 2 of this chapter".
- §15.212(a)(1)(viii) [eCFR]: "The modular transmitter must comply with any applicable RF exposure requirements in its final configuration." §15.212(b): "Limited modular approval also may be granted in those instances where compliance with RF exposure rules is demonstrated only for particular product configurations."
- §2.1043(b)(4) [eCFR]: "Class I and Class II permissive changes may only be made by the holder of the grant of certification, except as specified."
- The grant conditions themselves, for example ESP32-C3-MINI-1, ESP32-S3-MINI-1, ESP32-PICO-MINI-02 and E22-900M22S [GRANT]: "**Separate approval is required for all other operating configurations, including portable configurations with respect to 2.1093** and different antenna configurations." FGH100M manual [EXHIBIT]: "This module is limited to installation in mobile or fixed applications, according to Part 2.1091(b). The separate approval is required for all other operating configurations, including portable configurations with respect to Part 2.1093".
- KDB 996369 D04 Module Integration Guide v01, §2.0(c) [FCC-DOC, via newbtl.com mirror; current version v02 not readable]:
  > c) Confirm that the integration instructions for RF exposure requirements are followed for the host product. The integration instructions should provide instructions equivalent to one of the following:
  > i) The host product operating conditions must be such that there is a minimum separation distance of 20 cm (or possibly greater than 20 cm) between the antenna radiating structures and nearby persons. The host manufacturer is obligated to confirm the use conditions of the host product to ensure that the distance specified in the instructions is met. In this case the host product is classified as either a mobile device or a fixed device for RF exposure purposes; or
  > ii) The modular transmitter is authorized to be used in a specific type of host platform and installed such that it can be operated at closer than 20 cm to users or nearby persons. ... In this case the integration instructions will be very detailed about the specific host conditions ...
  > ...If the integration instructions do not contain clear directions for limited modules or for RF exposure compliance, the host product manufacturer must contact the module manufacturer responsible for the FCC certification.
- FCC TCB workshop April 2021, "Module Integration and Co-Location" [FCC-DOC]: the routes to show RF exposure was addressed are "The final host has its own FCC ID – Class II PC to one of the modules ... – Change in ID followed by Class II Permissive Change".
- **FCC filing precedent [GRANT/EXHIBIT]:** Sterling-LWB C2PC (2019-04-04): "C2PC Application to show compliance with RF Exposure requirements when installed into a new host". Its exhibit (`lwb_RF-Exposure-Analysis-4227239`) shows the GK001 host exempt: "(34.36∗0.01)/5 ∗√2.4 = 0.106 ... 0.106 is less than 3.0, so no SAR is required". Even so, it was done by C2PC. ESP32-S3-MINI-1 C2PC (2025-12-24) for a handheld knife host includes SAR values. MM8108-MF15457 C2PC adds "portable use" only for named Morse dongles.
- **[MEMORY, not verified]:** KDB 996369 D02 Q&A and KDB 447498 D01 v06 also say that a change from mobile to portable exposure conditions needs a C2PC or a new application, and that for simultaneous transmission in mobile hosts a Class I change can apply only when the sum of MPE ratios is ≤ 1. The April 2021 workshop slide confirms the Class I case for *mobile* co-location: "When simultaneous transmission MPE test exclusion applies, [∑ of MPE ratios] is ≤ 1.0 transmitter modules may be incorporated in host devices according to Class I Permissive Change requirements."

The lesson is about route, not burden. Where a module's own grant or filing already covers portable use at a stated distance (Raytac MDBT50Q/MDBT53, u-blox NINA-B3/B4, ANNA-B4, Sterling-LWB), the host can follow those instructions with no filing. Where it does not, the cheapest compliant route is to ask the grantee for a C2PC, which can rest on an exemption calculation with no SAR test. The alternative is a change in ID plus C2PC by the host maker.

---

## 2. Module-by-module findings

Notation: "Out W" is the output power on the grant (conducted unless noted). All are 47 CFR Part 15 Subpart C (15C), §15.247 unless noted.

### (a) Wi-Fi HaLow

#### Morse Micro MM6108-MF08651 → **2A74O-628C73** (3.3 V FEM) and **2A74O-DB3F2B** (4.3 V FEM) — MOBILE ONLY
- Which ID is which [EXHIBIT]: both user guides are titled "MM6108-MF08651-US ... User Guide UG100". The 628C73 guide says "Max output power: 21.5 dBm (Average power)" with VDD_FEM 3.0–3.6 V. The DB3F2B guide says "24 dBm" with VDD_FEM up to 4.3 V and a revision note "Update VFEM voltage to include 4.3V; Update FCC & IC identification numbers". **The reported ID 2A74O-DB3F2B is correct for the 4.3 V-FEM MF08651.** The original 3.3 V version is 2A74O-628C73.
- Grantee: Morse Micro Pty Ltd. Grant dates: 628C73 **2024-01-22**; DB3F2B **2024-09-10** [GRANT]. Rule part 15C, DTS. Frequency 903.5–926.5 MHz. Out: 628C73 **0.5129 W**; DB3F2B **0.9638 W**.
- Modular type: **Single Modular Approval**.
- Grant condition (identical text for both) [GRANT]:
  > "Single Modular Approval. Output power listed is conducted. This 802.11ah device supports 1, 2, 4, and 8 MHz modes. This device must be installed to provide a separation distance of at least 20 cm from all persons and must not be collocated or operating in conjunction with any other antenna or transmitter except in accordance with FCC multi-transmitter product procedures. This device can only be used when installed in a host device that follows the required instructions for use of a trace reference design. Compliance of this device in all final host configurations is the responsibility of the Grantee. The host integrator and end-users must be provided with specific operating instructions for satisfying RF exposure compliance. The host integrator must follow the integration instructions provided by the module manufacturer and ensure that the composite-system end product complies with the FCC requirements by a technical assessment or evaluation to the FCC rules and to KDB Publication 996369. The host integrator is instructed to ensure that the end user has no manual instructions to remove or install the device."
- RF-exposure exhibit for DB3F2B is titled "FCC MPE based exemption" (an MPE evaluation at 20 cm).
- Antenna [EXHIBIT, DB3F2B UG]: "802.11 ah Dipole Antenna 902-928 1.00 [dBi]". No integrated antenna; external via a 50 Ω trace to an SMA (628C73: RP-SMA/SMA) connector. "The trace from Pin No. 38 to antenna connector on the OEM PCB must be maintained identical as the above specification".
- Host obligations [EXHIBIT]: "Any device incorporating this module must include an external, visible, permanent marking or label which states: 'Contains FCC ID: 2A74O-DB3F2B'". "The final host product still requires Part 15 Subpart B compliance testing with the modular transmitter installed." Refers to KDB 996369 D04 and D02 Q12. End-user manual must carry the 20 cm statement: "This equipment should be installed and operated with a minimum distance 20cm between the radiator and your body."

#### AzureWave AW-HM593 → **TLZ-HM593**; AW-HM593W → **TLZ-HM593W** — MOBILE ONLY
- [GRANT] TLZ-HM593: "Change in identification of presently authorized equipment. Original FCC ID: 2A74O-628C73 Grant Date: 01/22/2024". So **AW-HM593 is the Morse MF08651 (3.3 V) under AzureWave's ID**. Change in ID granted 2024-04-16; C2PC 2024-06-07 ("C2PC to add Dipole type antenna with higher antenna gain"). 903.5–926.5 MHz, **0.5129 W**, Single Modular.
- TLZ-HM593W: change in ID from **2A74O-DB3F2B** (granted 2025-02-07), C2PC 2025-02-18 ("C2PC to add new antenna as described in the filing"). **0.9638 W**.
- Condition text: identical to the Morse 628C73/DB3F2B text above ("...must be installed to provide a separation distance of at least 20 cm from all persons...").
- Antenna [EXHIBIT]: "Model: AN0915-5001BSM, Type: Dipole Antenna, Gain: 2.34dBi". Label "Contains FCC ID: TLZ-HM593" / "TLZ-HM593W".

#### Morse Micro MM6108-MF08251 → **2A74O-8A7DD6** — MOBILE ONLY
- [GRANT] Original 2022-09-12; C2PC 2022-12-27 and 2023-06-06. 903.5–927.5 MHz, **0.122 W**. Single Modular.
- Condition: "Output power listed is conducted. **Single Modular Approval for mobile RF Exposure conditions.** The module's antenna is limited to 1.0 dBi gain and must be installed to meet the RF exposure compliance separation distance of 20 cm and any additional testing and authorization process as required. Co-location of this module with other transmitters that operate simultaneously are required to be evaluated using the FCC multi-transmitter procedures. Approved for OEM integration only. ... This grant is valid only when the device is sold to OEM integrators and the OEM integrators are instructed to ensure that the end-user has no manual instructions to remove or install the device. ... Class II Permissive Change: Component changes as described in this filing."
- Manual [EXHIBIT]: "In the users manual of the end product, the end user has to be informed to keep at least 20cm separation with the antenna..." Label: "Contains TX FCC ID: 2A74O-8A7DD6".

#### Quectel FGH100M → **XMR2023FGH100M** — MOBILE ONLY
- [GRANT] Quectel Wireless Solutions Company Limited; grant **2023-12-11**; 15C DTS; 903.5–926.5 MHz; **0.13996 W**; Single Modular.
- Condition: "Output power listed is conducted. **Single Modular Approval for mobile RF Exposure conditions.** The module antenna(s) must be installed to meet the RF exposure compliance separation distance of 20 cm from all persons and any additional testing and authorization process as required. Co-location of this module with other transmitters that operate simultaneously are required to be evaluated using the FCC multi-transmitter procedures. Approved for OEM integration only. ... This grant is valid only when the device is sold to OEM integrators and the OEM integrators are instructed to ensure that the end-user has no manual instructions to remove or install the device. This module can only be used with a host antenna circuit trace layout design in strict compliance with the OEM instructions provided. Any proposed changes must be notified to Quectel."
- Manual [EXHIBIT, FGH100M Hardware Design, "OEM/Integrators Installation Manual"]: "2. This module is limited to installation in mobile or fixed applications, according to Part 2.1091(b). 3. The separate approval is required for all other operating configurations, including portable configurations with respect to Part 2.1093 and different antenna configurations". Also: "(1) The antenna must be installed such that 20 cm is maintained between the antenna and users, (2) The transmitter module may not be co-located with any other transmitter or antenna. In the event that these conditions cannot be met ... the FCC authorization is no longer considered valid and the FCC ID cannot be used on the final product."
- Antenna: "802.11ah 902 ~ 928MHz Dipole 2.5 [dBi Max Peak Gain]". Any antenna-trace deviation needs a C2PC by Quectel, or a change in ID plus C2PC.
- Label: "Contains FCC ID: XMR2023FGH100M" (visible through a window or on a second outside label).

#### Morse Micro MM8108-MF15457 → **2A74O-737B5B** — MOBILE ONLY for third parties (portable only for Morse's own dongles, via C2PC with SAR)
- [GRANT] Original **2025-05-11** (notes "MM8108-MF15457"); C2PCs 2025-08-12 (notes "AW-HM677", "CIIPC for adding antenna"), 2026-10-27 and 2026-10-29 (notes "HaLow Dongle"). 902.5–927.5 MHz, **0.885 W**, Single Modular.
- Base condition: "Single Modular Approval. Output power listed is conducted. ... The module antenna(s) must be installed to meet the RF exposure compliance separation distance of 20 cm. Co-location of this module with other transmitters that operate simultaneously are required to be evaluated using the FCC multi-transmitter procedures. The module grantee is responsible for providing the documentation to the host integrator on restrictions of use, for continuing compliance of the module. The host integrator installing this module into their product must ensure that the final composite product complies with the FCC requirements by a technical assessment or evaluation to the FCC rules, including the transmitter operation and should refer to guidance in KDB 996369. This module can only be used with a host antenna circuit trace layout design in strict compliance with the OEM instructions provided."
- 2026 C2PCs add: "**Class II Permissive Change: Authorizes portable use when integrated into Morse Micro Wi-Fi HaLow USB Dongles, Models MM-U0-A, MM-U0-A-XX, MM-U0-C, MM-U0-C-XX ... The highest reported SAR was 1.58 W/kg. This host device requires professional installation.**" SAR report exhibits are in the filing.
- Antenna [EXHIBIT UG]: "802.11 ah Dipole Antenna 902-928 1.00 [dBi]" (more antennas added by C2PC). Label "Contains FCC ID: 2A74O-737B5B".

#### Other Morse IDs found (for completeness) — MOBILE ONLY
- **2A74O-B075FC** MM6108-MF16858, 2025-08-26, 902.5–927.5 MHz, 0.6281 W. Same "20 cm ... host antenna circuit trace layout" text as MF15457 [GRANT].
- **2A74O-ED502A** MM8108-M20-US, 2026-03-30, 902.5–927.5 MHz, 0.718 W. Same 20 cm text [GRANT]. Its user manual could not be downloaded.

### (b) Wi-Fi + Bluetooth

#### Espressif ESP32-C6-MINI-1 → **2AC7Z-ESPC6MINI1** — MOBILE ONLY
- [GRANT] 2023-09-04; 15C; 2402–2480 MHz 0.1076 W (BLE); 2405–2480 MHz 0.1012 W (802.15.4); 2412–2462 MHz 0.5297 W (Wi-Fi); Single Modular.
- "Single Modular Approval. Output power is conducted. ... The module antenna(s) must be installed to meet the RF exposure compliance separation distance of 20 cm and any additional testing and authorization process as required. Co-location ... FCC multi-transmitter procedures. Approved for OEM integration only. ... This grant is valid only when the device is sold to OEM integrators and the OEM integrators are instructed to ensure that the end user has no manual instructions to remove or install the device."
- Manual [EXHIBIT, "4 U.S. FCC Statement", says it follows KDB 996369 D03]: on-board PCB antenna, "Gain: 3.96 dBi Max". "Trace Antenna Designs: Not applicable. The module has its own antenna". "The module must be installed in the host equipment such that at least 20cm is maintained between the antenna and users' body; and if RF exposure statement or module layout is changed, then the host product manufacturer required to take responsibility of the module through a change in FCC ID or new application." "The transmitter module may not be co-located with any other transmitter or antenna." Label: "Host product manufacturers need to provide a **physical or e-label** stating 'Contains FCC ID: 2AC7Z-ESPC6MINI1'".
- Note the grant power: 0.5297 W for Wi-Fi as listed (as shown on the grant; it looks high for this part, but this is the listed figure).

#### Espressif ESP32-C3-MINI-1 → **2AC7Z-ESPC3MINI1** — MOBILE ONLY
- [GRANT] 2021-06-16; 2402–2480 MHz 0.005 W; 2412–2462 MHz 0.071 W; Single Modular.
- "Single Modular Approval. Power listed is conducted. **This device is to be used only for mobile and fixed applications.** The module antenna(s) must be installed to meet the RF exposure compliance separation distance of 20 cm ... Separate approval is required for all other operating configurations, including portable configurations with respect to 2.1093 and different antenna configurations."
- The filed user manual (v0.1 pre-release) contains no FCC statement. The FCC text is in the grant. The sibling ID 2AC7Z-ESPC3MINII is ESP32-C3-MINI-1U (external antenna 2.33 dBi; FPC up to 4.9 dBi after the 2026 C2PC), also 20 cm.

#### Espressif ESP32-S3-MINI-1 → **2AC7Z-ESPS3MINI1** — MOBILE ONLY
- [GRANT] Original 2022-02-28; 2402–2480 MHz 0.0107 W; 2412–2462 MHz 0.3365 W; Single Modular. "...should refer to guidance in KDB 996369. **Separate approval is required for all other operating configurations, including portable configurations with respect to 2.1093** and different antenna configurations."
- C2PC 2025-12-24: "Class 2 Permissive Change to disable the Wi-Fi by software and integrate the module into the host device: Seattle Ultrasonics C-200 Ultrasonic Chef's Knife ... The highest reported SAR for body and extremity (hand) exposure conditions are 0.12 W/kg and 0.03 W/kg". This is a hand-held host done by C2PC with SAR.
- Manual: PCB antenna 3.96 dBi (MINI-1) / 4.54 dBi (MINI-1U); 20 cm; "physical or e-label".

#### Espressif ESP32-PICO-MINI-02 → **2AC7Z-ESPPICOMINI** — MOBILE ONLY
- [GRANT] 2022-01-26; BT 0.006 W; BLE 0.002 W; Wi-Fi 0.049 W; also 15B. "This device is to be used only for mobile and fixed applications. This module can only be used with the antenna design in strict compliance with the OEM instructions provided. The module antenna(s) must be installed to meet the RF exposure compliance separation distance of 20 cm ... Separate approval is required for all other operating configurations, including portable configurations with respect to 2.1093".
- Datasheet/manual covers PICO-MINI-02 (on-board PCB antenna) and -02U (external). Gain 3.96 dBi max. "physical or e-label".

#### Murata Type 1DX / LBEE5KL1DX (CYW4343W) → **VPYLB1DX** — LIMITED MODULAR, PROFESSIONAL INSTALL, MOBILE ONLY
- [GRANT] Original 2016-04-27; C2PC 2016-06-24. BT 0.009 W, BLE 0.007 W, Wi-Fi 0.174 W. **Limited Single Modular**.
- "Limited Modular Approval. Power listed is conducted. **For professional installation only. Device shall not be sold to general public.** The antenna(s) used for this transmitter must be installed to provide a separation distance of at least 20cm from all persons and must not be co-located ... **Use in portable RF exposure conditions will require additional filing for SAR compliance.** ... This module can only be used with a host antenna circuit trace layout design in strict compliance with the OEM instructions provided."

#### Laird/Ezurio Sterling-LWB (CYW43430) → **TFB-1003** — PORTABLE ALLOWED at ≥ 29 mm (per the integration guide)
- [GRANT] Laird Connectivity LLC. Original 2016-05-27 (Single Modular); C2PCs 2019-04-04 and 2022-01-20 (modular type now **Limited Single Modular**). BT 0.0078 W, BLE 0.0056 W, Wi-Fi 0.2519 W.
- Condition: "Modular Approval. Output power listed is conducted. **This device must be installed to provide the minimum separation distance specified in the filing in order to meet the SAR exemption threshold listed in KDB447498 and be authorized for portable or mobile operation.** Installers and end-users must be provided with transmitter installation and operation conditions for satisfying RF exposure compliance. The antenna(s) used for this transmitter must not transmit simultaneously with any other antenna or transmitter, except in accordance with FCC multi-transmitter product procedures. ... This module can only be used with a host antenna circuit trace layout design in strict compliance with the OEM instructions provided. The grantee remains responsible for continuing compliance in all final installations." 2019 C2PC adds: "C2PC Application to show compliance with RF Exposure requirements when installed into a new host as shown in this filing."
- RF exhibit (LSR, 2016) [EXHIBIT]: "EIRP = 15.36 dBm = 34.36mW. Minimum separation distance for SAR test exclusion (1g tissue) = (34.36*1.55)/3 = 17.75 mm"; RSS-102 needs 28.13 mm.
- Application guide 330-0192 R4.x §7.6 [EXHIBIT]: "**In a portable application the minimum separation distance to the user is 29 mm. In a mobile application the minimum separation distance to the user is 20cm.**" §7.2 approved antennas: LSR 001-0001 dipole (via U.FL→RP-SMA), LSR 001-0014 FlexPIFA, LSR 001-0015 FlexNotch, Johanson 2450AT18D0100 chip (gains 1.5–2.0 dBi). Substitutes ≤ +2.0 dBi on U.FL. Also "the antenna must be placed such that at least a 20 cm separation distance is maintained from the antenna to all other radio transmitters." Label: "Contains FCC ID: TFB-1003".
- Caveats: 29 mm is fine for a hand-held device held away from the body (antenna 29 mm from the user's skin). It is **not** fine for at-ear use or wrist-worn contact. Orderability and EOL status of the original Sterling-LWB were not checked.

#### Laird/Ezurio Sterling-LWB+ (CYW43439) → **SQG-LWBPLUS** — MOBILE ONLY, professional install
- [GRANT] Original 2021-12-21; C2PCs 2022-12-12 and 2023-05-24. BLE 0.004 W, BT 0.005 W, Wi-Fi 0.428 W. "Professional Installation. Modular Approval. ... The antenna's as listed in this application must be installed to provide a separation distance of at least 20 cm from all persons and must not be co-located ... End-users may not be provided with the module installation instructions."

#### RTL8723DS-based modules — MOBILE ONLY
- **Fn-Link 6223A-SRD → 2AATL-6223ASRD** [GRANT]. Original 2017-12-08/09 (BT 0.00144 W: "SAR evaluation is valid for mobile applications only (minimum distance of 20cm to human bodies)"). C2PC 2022-11-24: "Separate approval is required for all other operating configurations, including portable configurations with respect to 2.1093. The antenna(s) used for this transmitter must be installed to provide a separation distance of at least 20 cm from all persons." New DTS grant 2024-11-15: Wi-Fi 0.04954 W, BLE 0.00188 W, "...must be installed to provide a separation distance of at least 20 cm from all persons and must not transmit simultaneously with any other antenna...".
- **Robart BL-M8723DS1 → 2AV5VBL-M8723DS1** [GRANT] 2020-05-07, **Limited Single Modular**. "RF exposure compliance is addressed for 1.1310 and 2.1091 MPE limits. The antenna(s) used for this transmitter must be installed to provide a separation distance of at least 20 cm from all persons. The maximum antenna gain is 2.0dBi."

#### AzureWave AW-CM256SM — no FCC ID found
- Not in AzureWave's (TLZ) grantee list on fccid.io (pages 1–2 checked). A secondary page [SECONDARY, techinfodepot] lists it only under host IDs (2A3PA-ROCK4C, 2A3PA-RADXA-CM3), i.e. certified inside specific Radxa boards, not as a stand-alone module.

### (c) Bluetooth LE only

#### Raytac MDBT50Q (nRF52840) → **SH6MDBT50Q** — PORTABLE ALLOWED (5 mm)
- [GRANT] Raytac Corp. Original **2018-07-26**; C2PCs 2020-05-15 and 2020-07-15. BLE 2402–2480 MHz 0.0066 W; 802.15.4 2405–2480 MHz 0.0066 W. Original Single Modular; the 2020-07 C2PC shows "**Limited Single Modular**".
- Condition: "Modular Approval. **This is a portable device.** Power Output is conducted. This grant is valid only when the module is sold to OEM integrators and must be installed by the OEM or OEM integrators. End-users may not be provided with the module installation instructions. OEM integrators and end-users must be provided with transmitter operating conditions for satisfying RF exposure compliance." (C2PCs added specific hosts: "Proxy mobile Reader Nano".)
- RF-exposure exhibit (SGS E2/2018/50091) [EXHIBIT]: "This is a Portable device ... the distance between radiating structure and human is less than 20cm." BLE: "6.166(mW)/5(mm)*√2.48 (GHz) =1.942< 3.0"; BT5: "6.998/5*√2.442 = 2.187 < 3.0".
- Manual [EXHIBIT]: "For body worn operation, this device has been tested and meets FCC RF exposure guidelines when used with an accessory that contains no metal and that positions the handset a minimum of 5mm from the body." "**This transmitter module is authorized only for use in device where the antenna may be installed such that 5mm may be maintained between the antenna and users.** The final end product must be labeled in a visible area with the following: Contains FCC ID: SH6MDBT50Q". Antennas: "u.FL antenna, Chip Antenna, PCB Antenna; Antenna Gain: 5dBi, -0.65dBi, 0.41dBi". The IC part also says "must not be co-located".
- Co-location: the grant does not state one. If a BLE radio plus another transmitter (Wi-Fi/HaLow) transmit together in the host, simultaneous-transmission evaluation under §1.1307(b)(3)(ii) applies.

#### Raytac MDBT53 (nRF5340) → **SH6MDBT53** (and MDBT53V → SH6MDBT53V) — PORTABLE per filing exhibit and manual (5 mm). Grant text silent on RF exposure.
- [GRANT] 2021-11-24; 2402–2480 MHz **0.002 W**; Single Modular. "Modular Approval. Power output listed is conducted. This grant is valid only when the module is sold to OEM integrators and must be installed by the OEM or OEM integrators. **The antennas used for this transmitter as shown in this filing must not be co-located or operating in conjunction with any other antenna or transmitter.** End-users may not be provided with the module installation instructions. OEM integrators and end-users must be provided with transmitter operating conditions for satisfying RF exposure compliance."
- RF exhibit (SGS E2/2021/A0102) [EXHIBIT] has "RF EXPOSURE EVALUATION FOR PORTABLE CONDITIONS" and an antenna table: MDBT53 chip −0.39 dBi **Portable**; MDBT53-P PCB −2.32 dBi **Portable**; YAGEO ANTX100ETHAB24553 2.00 dBi Portable; YAGEO ANTX100P011B24003 2.20 dBi Portable; ARISTOTLE RFA-02-5 5.00 dBi Mobile; YAGEO ANTX100P111B24003 3.30 dBi Mobile.
- Manual [EXHIBIT]: "This transmitter module is authorized only for use in device where the antenna may be installed such that 5mm may be maintained between the antenna and users." Label "Contains FCC ID: SH6MDBT53". Antennas: MDBT53 chip −0.39 dBi; MDBT53-P PCB −2.32 dBi; MDBT53-U u.FL 5 dBi.
- **The grant's no-co-location sentence is strict.** A host with a second simultaneously transmitting radio (e.g. HaLow) would need multi-transmitter evaluation. The grant says "must not be co-located", with no "except in accordance with..." clause.

#### u-blox NINA-B3 (nRF52840) → **XPYNINAB31** (NINA-B31x, u-connect) / **XPYNINAB30** (NINA-B30x open CPU) — PORTABLE ALLOWED (≥ 10 mm; one 2022 C2PC says 5 mm)
- [GRANT] u-blox AG. B31: original 2018-09-11; C2PCs 2019-03-20 and 2022-09-26; 2402–2480 MHz 0.007 W (max peak conducted); 2405–2475 MHz 0.007 W.
- Original condition: "Output power listed is max peak conducted. **This modular transmitter is approved for use in fixed/mobile configurations and meets SAR test exclusion for host applications, where the radiating part is at least 10 mm away from the human body.** This module can only be used with a host antenna circuit trace layout design in strict compliance with the OEM instructions provided. This module is also approved with a fixed onboard antenna. Only those antenna(s) tested and documented with this device or similar antenna types with equal or lesser gain ... may be used ... The antenna used for this transmitter module must not transmit simultaneously with any other antenna or transmitter, except in accordance with FCC multi-transmitter product procedures. The integrator is responsible for the final compliance of the end-product..."
- 2022-09-26 C2PC: "Class II Permissive Change to add new host portable host 109M2380/109M2390 with using NINA-B316 with integrated antenna. ... meets SAR test exclusion for host applications, where the radiating part is **at least 5 mm** away from the human body." Whether the 5 mm applies generally or only to that host is not stated clearly. The general system integration manual still says 10 mm.
- NINA-B30x: same 10 mm text, but "**The integration of this modular approved transmitter in this Open CPU version into any end-product is strictly limited to the grantee himself. Integration by any other party than the grantee requires first a change in identification filing according to §2.933.**" So NINA-B30x is not usable on SDoC by a third party. Use NINA-B31x.
- Manual (NINA-B3 SIM) [EXHIBIT]: "Having a separation distance of minimum 10 mm between the user and/or bystander and the antenna and/or radiating element ensures that max output power of NINA-B3 is below the SAR test exclusion limits presented in KDB 447498 D01v06." Antennas listed +2 to +3 dBi (external list) plus an integrated PCB antenna variant (NINA-B312/B316).

#### u-blox NINA-B4 (nRF52833) → **XPYNINAB4** — PORTABLE per manual (≥ 5 mm). Grant text silent on RF exposure.
- [GRANT] Original 2020-12-16; C2PCs 2021-11-17, 2023-05-26, 2024-05-07, 2026-04-28. 2402–2480 MHz 0.00815 W; 2405–2480 MHz 0.00371 W. Single Modular. Condition: "The output power listed is conducted. Co-location of this module with other transmitters that operate simultaneously are required to be evaluated using the FCC multi-transmitter procedures. The module grantee is responsible for providing the documentation to the system integrator on restrictions of use ... should refer to guidance in KDB 996369." There is **no 20 cm or mobile restriction** in the grant.
- RF exhibit [EXHIBIT]: "The exposure safety distance is less than 5mm. ... (8.15mW /5mm)·[√2.48(GHz)]= 2.56<3.0 ... The SAR evaluation is not required."
- Certification app note UBX-20037320 (filed as the user manual) [EXHIBIT] §2.3.3: "NINA-B4 modules are **approved for installation into mobile and/or portable host platforms** and must not be co-located or operating in conjunction with any other antenna or transmitter – except in accordance with FCC multi-transmitter guidelines. ... customer applications integrating the NINA-B4 modules must include a separation distance of **at least 5 mm** between the user (or bystander) and the antenna (or radiating element)." Also: "⚠ NINA-B4 series modules are intended for OEM integrators only. End-products that include u-blox modules must be professionally installed in such a way that only the authorized antennas listed included in the Pre-approved antennas list can be used." Label: "Contains FCC ID: XPYNINAB4" plus the Part 15 two-condition statement plus the "Changes or modifications..." statement. Antennas +2 to +3 dBi external; integrated PCB antenna variant NINA-B406.

#### u-blox ANNA-B4 (nRF52833 SiP) → **XPYANNAB4** — PORTABLE (0–5 mm per exhibit and manual). Grant text silent on RF exposure.
- [GRANT] 2022-04-21; 2402–2480 MHz 0.0054 W / 0.0048 W; 2405–2475 MHz 0.0054 W; Single Modular. "Output power listed is maximum conducted power. OEM integrators must be provided with antenna installation instructions. The OEM integrators must be instructed to ensure that the end user has no manual instructions to remove or install the device. OEM integrators and end-users must be provided with transmitter operation conditions for satisfying RF exposure compliance. Only those antennas tested with the device or similar antennas with equal or lesser gain may be used with this transmitter."
- RF exhibit [EXHIBIT]: "(5.41mW / 5mm)·[√2.480GHz)]=1.70<3.0 ... The SAR evaluation is not required."
- System integration manual [EXHIBIT] §7.3.2.2: "**The maximum output power of ANNA-B4 is below the SAR test exclusion limits presented in KDB 447498 D01v06 applicable for separation distances between 0 mm and 5 mm. Therefore, SAR evaluation is not needed.**" Integrated antenna: "The ANNA-B4 System in Package (SiP) module has an integrated antenna" ("Max radiated output power with internal antenna (EIRP) +9 dBm"). External antennas +0.5 to +5.0 dBi listed. KDB 996369 D03 §2.4 and §2.5 are "not applicable".

### (d) LoRa

#### RAKwireless RAK3172 → **2AF6B-RAK3172** — MOBILE ONLY
- [GRANT] Original **2021-10-19**; 15C; FHSS 902.3–914.9 MHz **0.1153 W**; DTS 903.0–914.2 MHz **0.2559 W**; Single Modular. C2PCs 2025-01-23 (grant text "unavailable" on mirror; the exhibit shows it was for RAK2470 host with a PCB antenna).
- "Power output listed is conducted. Single modular approval. The antenna(s) used for this transmitter must be installed to provide a separation distance of at least 20 cm from all persons and must not be co-located or operating in conjunction with any other antenna or transmitter, except in accordance with FCC multi-transmitter evaluation procedures as documented in this filing. The host integrator must follow the integration instructions provided by the module manufacturer and ensure that the composite system end product complies with the FCC requirements by a technical assessment or evaluation to the FCC rules and to KDB Publication 996369."
- Manual [EXHIBIT]: "Antenna type: IPEX Antenna; Antenna gain: 2.3dBi"; "This Transmitter must be installed to provide a separation distance of at least 20 cm"; label "Contains FCC ID: 2AF6B-RAK3172".

#### Seeed Wio-E5 (= LoRa-E5) → **Z4T-LORA-E5**; Wio-E5-LE → **Z4T-WIO-E5-LE** — MOBILE ONLY
- Naming: Seeed renamed LoRa-E5 to Wio-E5 [MEMORY/SECONDARY; the 2026 C2PCs still say "LoRa-E5"].
- [GRANT] Z4T-LORA-E5 original 2020-12-01, C2PCs 2026-04-23; FHSS 902.3–914.9 MHz 0.03784 W; DTS 903.0–914.2 MHz 0.03999 W; Single Modular. "Output power listed is conducted power. The antenna used with this transmitter must be installed to provide a minimum separation distance of at least 20 cm from all persons and must not be co-located or operating in conjunction with any other antenna or transmitter, except in accordance with FCC multi- transmitter product procedures. End-users must be provided with operating procedures for satisfying RF exposure compliance. Single Modular Approval OEM integrators must be provided with antenna installation instructions. ... Only the antenna tested with the device or similar antennas with equal or lesser gain may be used with this transmitter."
- Z4T-WIO-E5-LE 2023-07-25: 0.02004 W / 0.01986 W; same 20 cm text.
- Manual [EXHIBIT]: label "Contains transmitter module FCC ID: Z4T-LORA-E5"; "...including portable configuration with respect to Part 2.1093 and different antenna..." (separate approval needed).

#### Ebyte E22-900M22S (SX1262) → **2ALPH-E22900M22S** — YES, it has an FCC ID — MOBILE ONLY, and granted at low power
- [GRANT] Chengdu Ebyte Electronic Technology Co., Ltd.; **2021-10-29**; 15C DTS; 903.0–927.5 MHz; **0.0076 W** (7.6 mW conducted); Single Modular.
- "Single Modular Approval. Power output listed is conducted. The module grantee is responsible for providing the documentation to the system integrator on restrictions of use, for continuing compliance of the module. The integrator installing this module into their product must ensure that the final composite product complies with the FCC requirements by a technical assessment or evaluation to the FCC rules, including the transmitter operation and should refer to guidance in KDB 996369. **Separate approval is required for all other operating configurations, including portable configurations with respect to 2.1093** and different antenna configurations."
- RF exhibit [EXHIBIT]: "LORA Conducted Average Power 8.76 dBm; Maximum Tune-up 9.00 dBm; 0.0032 mW/cm²; ... The maximum antenna gain is 3dBi; The exposure evaluation safety distance is 20cm." **The module is sold as a 22 dBm part, but the grant covers about 9 dBm.** Higher power falls outside the grant (§2.1043 / the grant's output listing).
- Manual [EXHIBIT]: "Host product manufacturers that they need to provide a **physical or e-label** stating, 'Contains FCC ID:2ALPH-E22900M22S'". "Only those antennas with same type and lesser gain filed under this FCC ID can be used". Antenna listed: ZIISOR TX915-XP-100 sucker antenna 3 dBi.

### Summary table

| Module | FCC ID | Grant (orig.) | Max out (grant) | Modular | RF-exposure condition |
|---|---|---|---|---|---|
| MM6108-MF08651 (3.3 V FEM) | 2A74O-628C73 | 2024-01-22 | 0.5129 W | Single | **20 cm only** |
| MM6108-MF08651 (4.3 V FEM) | 2A74O-DB3F2B | 2024-09-10 | 0.9638 W | Single | **20 cm only** |
| AzureWave AW-HM593 / HM593W | TLZ-HM593 / TLZ-HM593W | 2024-04-16 / 2025-02-07 (CII) | 0.5129 / 0.9638 W | Single | **20 cm only** |
| MM6108-MF08251 | 2A74O-8A7DD6 | 2022-09-12 | 0.122 W | Single | **"for mobile RF Exposure conditions", 20 cm, ≤1.0 dBi** |
| Quectel FGH100M | XMR2023FGH100M | 2023-12-11 | 0.13996 W | Single | **"for mobile RF Exposure conditions", 20 cm** |
| MM8108-MF15457 | 2A74O-737B5B | 2025-05-11 | 0.885 W | Single | **20 cm**; portable only in Morse USB dongles via C2PC (SAR 1.58 W/kg) |
| MM6108-MF16858 | 2A74O-B075FC | 2025-08-26 | 0.6281 W | Single | 20 cm |
| MM8108-M20-US | 2A74O-ED502A | 2026-03-30 | 0.718 W | Single | 20 cm |
| ESP32-C6-MINI-1 | 2AC7Z-ESPC6MINI1 | 2023-09-04 | 0.5297 W (Wi-Fi) | Single | **20 cm** |
| ESP32-C3-MINI-1 | 2AC7Z-ESPC3MINI1 | 2021-06-16 | 0.071 W | Single | **mobile/fixed only, 20 cm** |
| ESP32-S3-MINI-1 | 2AC7Z-ESPS3MINI1 | 2022-02-28 | 0.3365 W | Single | **portable needs separate approval** |
| ESP32-PICO-MINI-02 | 2AC7Z-ESPPICOMINI | 2022-01-26 | 0.049 W | Single | **mobile/fixed only, 20 cm** |
| Murata 1DX | VPYLB1DX | 2016-04-27 | 0.174 W | **Limited** | 20 cm; professional install; not for general public |
| Sterling-LWB | TFB-1003 | 2016-05-27 | 0.2519 W | Single→Limited | **portable OK at min. distance in filing = 29 mm** |
| Sterling-LWB+ | SQG-LWBPLUS | 2021-12-21 | 0.428 W | Single | 20 cm; professional install |
| Fn-Link 6223A-SRD (RTL8723DS) | 2AATL-6223ASRD | 2017-12-08 | 0.0495 W | Single | 20 cm |
| BL-M8723DS1 (RTL8723DS) | 2AV5VBL-M8723DS1 | 2020-05-07 | 0.0483 W pk | Limited | 20 cm, ≤2.0 dBi |
| Raytac MDBT50Q | SH6MDBT50Q | 2018-07-26 | 0.0066 W | Single (Limited in 2020 C2PC) | **"This is a portable device"; 5 mm** |
| Raytac MDBT53 / 53V | SH6MDBT53 / SH6MDBT53V | 2021-11-24 | 0.002 W | Single | **portable per exhibit (chip/PCB ant.), 5 mm; no co-location** |
| u-blox NINA-B31x | XPYNINAB31 | 2018-09-11 | 0.007 W pk | Single | **≥10 mm (5 mm in 2022 C2PC)** |
| u-blox NINA-B30x | XPYNINAB30 | 2018-09-11 | 0.007 W pk | Single | ≥10 mm, but integration limited to grantee (needs change in ID) |
| u-blox NINA-B4 | XPYNINAB4 | 2020-12-16 | 0.00815 W | Single | **mobile and/or portable, ≥5 mm (manual)** |
| u-blox ANNA-B4 | XPYANNAB4 | 2022-04-21 | 0.0054 W | Single | **0–5 mm exempt (manual/exhibit)** |
| RAK3172 | 2AF6B-RAK3172 | 2021-10-19 | 0.2559 W | Single | 20 cm |
| Seeed LoRa-E5 / Wio-E5 | Z4T-LORA-E5 | 2020-12-01 | 0.03999 W | Single | 20 cm |
| Seeed Wio-E5-LE | Z4T-WIO-E5-LE | 2023-07-25 | 0.02004 W | Single | 20 cm |
| Ebyte E22-900M22S | 2ALPH-E22900M22S | 2021-10-29 | **0.0076 W** | Single | 20 cm; portable needs separate approval |

---

## 3. (f) Electronic labelling

[eCFR] §2.935 (current):
> (a) Any radiofrequency device equipped with an integrated electronic display screen, or a radiofrequency device without an integrated screen that can only operate in conjunction with a device that has an electronic display screen, may display on the electronic display the FCC Identifier, any warning statements, or other information that the Commission's rules would otherwise require to be shown on a physical label attached to the device.
> (b) ... Users must be provided with prominent instructions on how to access the information ...
> (c) ... must permit access to the information without requiring special codes, accessories or permissions and the access to this information must not require more than three steps from the device setting menu. ...
> (e) The necessary label information must be programmed by the responsible party and must be secured in such a manner that third-parties cannot modify it.
> (f) Devices displaying their FCC Identifier, warning statements, or other information electronically must also be labeled, either on the device or its packaging, with the FCC Identifier or other information (such as a model number and identification of a Web page that hosts the relevant regulatory information) that permits the devices to be identified at the time of importation, marketing, and sales ... Devices can be labeled with a stick-on label, printing on the packaging, a label on a protective bag, or by similar means.

Module grantee documents [EXHIBIT] say this explicitly for the "Contains FCC ID" statement: Espressif (C6/S3/PICO/C3-1U) "Host product manufacturers need to provide a **physical or e-label** stating 'Contains FCC ID: ...'"; Ebyte E22-900M22S says the same. Some others (Morse/AzureWave/Raytac) say "external, visible, permanent marking or label" or "labeled in a visible area". On those, e-labelling of the module ID rests on §2.935 and KDB 784748. I could not read KDB 784748 D01/D02 itself (apps.fcc.gov blocked) [MEMORY: KDB 784748 D02 e-labelling guidance applies §2.935 to modular hosts and allows the "Contains FCC ID" to be e-labelled when the host has a screen; the SDoC compliance statement (§2.1077) may also be provided electronically].

---

## 4. (g) Hearing-aid compatibility for a Wi-Fi/HaLow VoIP handset

[eCFR] §20.19(a), current (incorporating the 2024 "100 %" order):
> *Digital mobile service* refers to a terrestrial mobile service that enables two-way real-time voice communications among members of the public or a substantial portion of the public, including both interconnected and non-interconnected voice over internet protocol (VoIP) services, to the extent that such service is provided over frequencies specified in the 2007 ANSI standard, 2011 ANSI standard, or the 2019 ANSI standard.
> *2019 ANSI standard* refers to the technical standard for hearing aid compatibility applicable to frequencies between 614 MHz and 6 GHz as set forth in ANSI C63.19-2019.
> *Handset* refers to a device used in delivery of digital mobile service in the United States that contains a built-in speaker and is typically held to the ear in any of its ordinary uses.
> *Handset manufacturer* refers to a manufacturer of handset models that are used in delivery of digital mobile service, as defined in this section, in the United States.

[eCFR] §20.19(e)(4): "**Beginning December 14, 2026, handset manufacturers may no longer claim de minimis status** under the terms of this section." §20.19(c)(2): after 14 Dec 2026, "(i) One hundred (100) percent of these handset models must meet the 2019 ANSI standard's acoustic coupling requirements ... (iv) One hundred (100) percent of these handset models must meet at least two forms of coupling" (acoustic plus telecoil, or acoustic plus Bluetooth), "(v) All new handset models ... must meet the 2019 ANSI Standard's volume control requirements". §20.19(b)(2) sets the certification test requirements for "A handset model submitted for equipment certification".

Scope history [primary, Federal Register 81 FR 2016-01-05, 2015-32757 summary of FCC 15-155]:
> "...the expanded scope will cover handsets that enable voice communications through VoIP software applications installed by the manufacturer or service provider regardless of whether the calling functionality provides interconnection to the public switched telephone network. ... Unlike the current scope, **the expanded scope will also apply to a voice communications service over Wi-Fi** that does not utilize an in-network switching facility that enables reuse of frequencies and seamless hand-off."
> "...the Commission further clarifies that the incorporation of a VoIP functionality operating over Wi-Fi in a public safety or private enterprise device does not bring the device under the expanded scope of the rule. Rather, The expanded scope will cover only devices used with the provision of a service available to the public or a substantial portion of the public."
> "...cordless telephones remain subject to section 68.4 of the Commission's rules ... and are not affected by the change in scope."

**Conclusion.** A held-to-ear handheld making VoIP calls over Wi-Fi (2.4 GHz) or HaLow (902–928 MHz, inside 614 MHz–6 GHz) to a service open to the public falls within "Handset" / "digital mobile service". This holds whether or not the service is interconnected and whether or not there is any cellular radio. The only carve-out in the order text is devices used exclusively with public-safety or private-enterprise (non-public) networks.

Two practical points:
1. **Interaction with SDoC.** §20.19(b) is written around a handset model "submitted for equipment certification". A host that is only SDoC'd (no own FCC ID) is in an untested position. §20.19(c) obliges the *manufacturer's offered handset models* regardless. I did not find FCC text resolving how a module-only, SDoC host shows HAC. This is a reason to expect that a voice handset ends up with its own FCC ID.
2. **Handset-plus-base cordless designs.** If the product is a handset-plus-base cordless phone rather than a "mobile handset", Part 68 applies instead. [eCFR] §68.4(a)(1): "Every cordless telephone manufactured in the United States ... or imported ... after August 16, 1991, must be hearing aid compatible, as defined in § 68.316." §68.3 now also defines "ACS telephonic CPE": "Customer premises equipment used with advanced communications services that is designed to provide 2-way voice communication via a built-in speaker intended to be held to the ear in a manner functionally equivalent to a telephone, except for mobile handsets." Either way, a held-to-ear voice product has a HAC obligation.

---

## 5. What a host maker must do when relying on a modular grant (common to all grants above)
[GRANT/EXHIBIT/FCC-DOC]
- Stay within every grant condition: power, antenna type and gain (or the exact trace or reference design), separation distance, co-location, and OEM-only installation. End-user manuals must not explain how to remove or install the module.
- Label "Contains FCC ID: <ID>" (or "Contains TX FCC ID" / "Contains transmitter module FCC ID" per the grantee's wording). Use a physical label or, under §2.935, an e-label on the host's screen plus the ID on packaging.
- Put the grantee's required end-user statements in the host manual: the Part 15 two-condition statement, "changes or modifications" caution and RF-exposure statement. For 20 cm modules: "installed and operated with a minimum distance 20cm between the radiator and your body". **That statement cannot truthfully be made for a handheld or wrist device.**
- Host Part 15 Subpart B: SDoC (§2.906 / §2.938 records). "The final host product still requires Part 15 Subpart B compliance testing with the modular transmitter installed." KDB 996369 D04 recommends spot-checking transmitter emissions in the composite host.
- Co-location: if more than one radio transmits at once, evaluate under §1.1307(b)(3)(ii) and KDB 447498. Some grants (MDBT53, NINA-B3 "must not transmit simultaneously ... except in accordance with FCC multi-transmitter product procedures") make that a condition. The April 2021 FCC workshop says Class I applies only when the "∑ of MPE ratios ≤ 1.0" (mobile).

---

## 6. Gaps and uncertainties
- FCC EAS and KDB servers refused automated access. Grant texts come from fccid.io's reproduction of the FCC/TCB grant pages. KDB 447498 D04, KDB 996369 D02/D03/D04 v02 and KDB 784748 were not read directly. KDB 996369 D04 v01 was read from a third-party mirror.
- Not checked for this report: stock or EOL status (Sterling-LWB in particular), and the 2026 C2PC exhibits for ESP32-C3-MINI-1U / NINA-B4 beyond the grant text.
- The §1.1307(b)(3)(i)(B) thresholds above use "available maximum time-averaged power or ERP, whichever is greater". For antennas with gain > 0 dBd, ERP governs.
