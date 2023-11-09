![Microchip logo](https://raw.githubusercontent.com/wiki/Microchip-MPLAB-Harmony/Microchip-MPLAB-Harmony.github.io/images/microchip_logo.png)
![Harmony logo small](https://raw.githubusercontent.com/wiki/Microchip-MPLAB-Harmony/Microchip-MPLAB-Harmony.github.io/images/microchip_mplab_harmony_logo_small.png)

# MPLAB® Harmony 3 Wireless PIC32CX-BZ Family System Services

MPLAB® Harmony 3 is an extension of the MPLAB® ecosystem for creating embedded firmware solutions for Microchip 32-bit SAM and PIC® microcontroller and microprocessor devices.  Refer to the following links for more information.

- [Microchip 32-bit MCUs](https://www.microchip.com/design-centers/32-bit)
- [Microchip 32-bit MPUs](https://www.microchip.com/design-centers/32-bit-mpus)
- [Microchip MPLAB X IDE](https://www.microchip.com/mplab/mplab-x-ide)
- [Microchip MPLAB® Harmony](https://www.microchip.com/mplab/mplab-harmony)
- [Microchip MPLAB® Harmony Pages](https://microchip-mplab-harmony.github.io/)

This repository contains the MPLAB® Harmony 3 wireless system solutions. Quickly incorporate connectivity to your designs with wireless ICs, modules, software and development kits that make connecting effortless for your customers. Our comprehensive wireless portfolio has the technology to meet your range, data rate, interoperability, frequency and topology needs. Refer to the following links for release notes, training materials, and interface reference information.

- [Release Notes](./release_notes.md)
- [MPLAB® Harmony License](mplab_harmony_license.md)
- [MPLAB® Harmony 3 Wireless PIC32CXBZ Wiki](https://github.com/Microchip-MPLAB-Harmony/wireless_pic32cxbz_wbz/wiki)
- [MPLAB® Harmony 3 Wireless PIC32CXBZ API Help](https://microchip-mplab-harmony.github.io/wireless_pic32cxbz_wbz)

# Contents Summary

| Folder     | Description                                                                          |
| ---        | ---                                                                                  |
| config     | Wireless pic32cx-bz system services module configuration file                        |
| **[docs](docs/index.html)**       | Wireless pic32cx-bz system services help documentation-html, md and pdf              |
| drivers    | Driver/Firmware files of pic32cx-bz system services                                  |
| utilities  | Contains scripts and other utilities                                                 |

## System Services

|Service|	Description|
|---|---|
|**[Device Support Library](docs/GUID-2167300F-6A96-440E-83CA-FC9C0C259914.html)**	|This service provides help on the Device Support library that can be used as interface with RF System, PMU System, Info Block and Sleep System|
|**[Persistent Data Server Library](docs/GUID-D08C61D1-8CD6-4D2F-B74D-E58784C9042B.html)**	|	This service provides help on the PDS library that can be used for storing and restoring of important data in non-volatile memory using wear levelling mechanism|
|**[Standalone Bootloader](docs/GUID-A04B5B1F-202B-4944-B18F-13E4857CC3CD.html)**	|	This service provides help on the Standalone Bootloader component that can be used to upgrade firmware on a target device without the need for an external programmer or debugger|
|**[Bootloader Services](docs/GUID-E95D4418-FDD2-49A3-999F-6EFBA54DDA3D.html)**	|	This service provides help on the Bootloader Services that can be used to create signed firmware image for OTA with the provided header and OTA header information |

____

#License
Silex Public Key Cryptography API, included in this repository(for PIC32CXBZ3, WBZ35X) comes with the following BSD 3-Clause


Copyright (c) 2018-2020 Silex Insight sa
Copyright (c) 2018-2020 Beerten Engineering scs

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.


[![License](https://img.shields.io/badge/license-Harmony%20license-orange.svg)](https://github.com/Microchip-MPLAB-Harmony/wireless_pic32cxbz_wbz/blob/master/mplab_harmony_license.md)
[![Latest release](https://img.shields.io/github/release/Microchip-MPLAB-Harmony/wireless_pic32cxbz_wbz.svg)](https://github.com/Microchip-MPLAB-Harmony/wireless_pic32cxbz_wbz/releases/latest)
[![Latest release date](https://img.shields.io/github/release-date/Microchip-MPLAB-Harmony/wireless_pic32cxbz_wbz.svg)](https://github.com/Microchip-MPLAB-Harmony/wireless_pic32cxbz_wbz/releases/latest)
[![Commit activity](https://img.shields.io/github/commit-activity/y/Microchip-MPLAB-Harmony/wireless_pic32cxbz_wbz.svg)](https://github.com/Microchip-MPLAB-Harmony/wireless_pic32cxbz_wbz/graphs/commit-activity)
[![Contributors](https://img.shields.io/github/contributors-anon/Microchip-MPLAB-Harmony/wireless_pic32cxbz_wbz.svg)]()


THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS AS IS AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
____

[![Follow us on Youtube](https://img.shields.io/badge/Youtube-Follow%20us%20on%20Youtube-red.svg)](https://www.youtube.com/user/MicrochipTechnology)
[![Follow us on LinkedIn](https://img.shields.io/badge/LinkedIn-Follow%20us%20on%20LinkedIn-blue.svg)](https://www.linkedin.com/company/microchip-technology)
[![Follow us on Facebook](https://img.shields.io/badge/Facebook-Follow%20us%20on%20Facebook-blue.svg)](https://www.facebook.com/microchiptechnology/)
[![Follow us on Twitter](https://img.shields.io/twitter/follow/MicrochipTech.svg?style=social)](https://twitter.com/MicrochipTech)

[![](https://img.shields.io/github/stars/Microchip-MPLAB-Harmony/wireless_pic32cxbz_wbz.svg?style=social)]()
[![](https://img.shields.io/github/watchers/Microchip-MPLAB-Harmony/wireless_pic32cxbz_wbz.svg?style=social)]()


