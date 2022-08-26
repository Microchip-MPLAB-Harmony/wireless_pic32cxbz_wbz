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

print('Load Module: Harmony Wireless PIC32CX-BZ Device Support')

## Device Support
initDeviceSupport = Module.CreateComponent('pic32cx_bz3_devsupport', 'Device_Support', '/Wireless/Drivers/PIC32CX-BZ System Services', 'driver/pic32cx-bz/config/device_support.py')
initDeviceSupport.setDisplayType('PIC32CX-BZ3 Device Support')
initDeviceSupport.addCapability('Device_Support_Capability', 'Device_Support', True)
initDeviceSupport.addDependency('HarmonyCoreDependency', 'Core Service', 'Core Service', True, True)


# TODO remove this exploritory code and all associated files
# print('Load Module: Harmony Wireless Xample content')
# 
# deviceXampleComponent = Module.CreateComponent('deviceXample', 'Xample', '/Wireless Xample', 'xample/config/xample.py')
# deviceXampleComponent.setDisplayType('Xample H3 Device')
