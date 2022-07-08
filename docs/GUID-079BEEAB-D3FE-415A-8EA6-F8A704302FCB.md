# DFU Functionality - Serial image bootloader

DFU, the device firmware upgrade in bootloader is used to load new image which is received from host over serial interface and writes into the flash\(Slot 1\). The host may be python script or pc tool.

There are two possible ways the device bootloader can be put into DFU mode

-   **GPIO trigger DFU Mode**

    By holding GPIO pin/button and resetting the board helps to enter DFU mode

-   **Timer based trigger DFU Mode**

    Upon boot, bootloader enters into DFU mode and will be in DFU mode for the defined time for example: 600ms, then upon timeout, control jumps to application. So the host application/script should be sending messages to load the new image very frequently so that when reset is triggered, it loads the new image since the bootloader will be in DFU mode


**Parent topic:**[PIC32CX-BZ2 Standalone Bootloader Component Help](GUID-A04B5B1F-202B-4944-B18F-13E4857CC3CD.md)

