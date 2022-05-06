# PIC32CX-BZ2 Bootloader Services Component Help

The PIC32CX-BZ2 Bootloader Services is a utility which helps in creating signed firmware image for OTA with the provided header and OTA header information. Please follow MCC Project Graph and how to add Bootloader services component which is available in Device Resources - Libraries → Harmony → Wireless → Bootloader Services

**Bootloader services utility functional activities with Harmony 3 code generation**

-   Adds the autoload.py script which gets loaded in the project \(See Screenshot\) for getting the required information from user for creating signed Firmware

    ![](GUID-367DB95B-75B9-4698-805B-EF4D3C60F14C-low.jpg)

-   Embedding OTA header information as part of the signed firmware binary image.

    ![](GUID-8077391A-2F0D-4C87-BAA5-D2D061060380-low.jpg)


-   Generates linker script with the below memory layout

![](GUID-6F204CB4-2DD3-49A2-9F21-DDA8A1AD7762-low.png)

**Signing**

The complete image including firmware and meta header is signed by the below process

![](GUID-1F171B42-9FA9-4F72-9034-913CF80C3770-low.png)

