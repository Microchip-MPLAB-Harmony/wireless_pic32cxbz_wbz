# coding: utf-8
"""*****************************************************************************
* Copyright (C) 2022 Microchip Technology Inc. and its subsidiaries.
*
* Subject to your compliance with these terms, you may use Microchip software
* and any derivatives exclusively with Microchip products. It is your
* responsibility to comply with third party license terms applicable to your
* use of third party software (including open source software) that may
* accompany Microchip software.
*
* THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER
* EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY IMPLIED
* WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A
* PARTICULAR PURPOSE.
*
* IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE,
* INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY KIND
* WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF MICROCHIP HAS
* BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO THE
* FULLEST EXTENT ALLOWED BY LAW, MICROCHIP'S TOTAL LIABILITY ON ALL CLAIMS IN
* ANY WAY RELATED TO THIS SOFTWARE WILL NOT EXCEED THE AMOUNT OF FEES, IF ANY,
* THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR THIS SOFTWARE.
*****************************************************************************"""

print('Load Module: Harmony Wireless PIC32CX-BZ Bootloader')

## pic32cx_bz2_bootloader   - standalone
initBootloaderStandalone = Module.CreateComponent('Bootloader', 'Bootloader', '/Wireless/Drivers/PIC32CX-BZ System Services', 'driver/pic32cx-bz/config/bootloader_standalone.py')
initBootloaderStandalone.setDisplayType('PIC32CX-BZ2 Bootloader')
initBootloaderStandalone.addDependency("Bootloader_usart", "UART", None, False, True)
initBootloaderStandalone.addDependency("Bootloader_timer", "TMR", None, False, True)
initBootloaderStandalone.addDependency("Bootloader_nvm", "MEMORY", None, False, True)
initBootloaderStandalone.addDependency("Bootloader_crypto", "LIB_CRYPTO", None, True, True)
initBootloaderStandalone.addDependency("Bootloader_WolfCrypt_Dependency", "LIB_WOLFCRYPT", None, False, True)
