# coding: utf-8
##############################################################################
# Copyright (C) 2019-2020 Microchip Technology Inc. and its subsidiaries.
#
# Subject to your compliance with these terms, you may use Microchip software
# and any derivatives exclusively with Microchip products. It is your
# responsibility to comply with third party license terms applicable to your
# use of third party software (including open source software) that may
# accompany Microchip software.
#
# THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER
# EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY IMPLIED
# WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A
# PARTICULAR PURPOSE.
#
# IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE,
# INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY KIND
# WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF MICROCHIP HAS
# BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO THE
# FULLEST EXTENT ALLOWED BY LAW, MICROCHIP'S TOTAL LIABILITY ON ALL CLAIMS IN
# ANY WAY RELATED TO THIS SOFTWARE WILL NOT EXCEED THE AMOUNT OF FEES, IF ANY,
# THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR THIS SOFTWARE.
##############################################################################
pic32cx_bz2_family = {'PIC32CX1012BZ25048',
                      'PIC32CX1012BZ25032',
                      'PIC32CX1012BZ24032',
                      'WBZ451',
                      'WBZ450',
                      }

pic32cx_bz3_family = {'PIC32CX5109BZ31048',
                      'PIC32CX5109BZ31032',
                      'WBZ351',
                      'WBZ350',
                      }
global deviceName
deviceName = Variables.get("__PROCESSOR")

print('Load Module: Harmony Wireless PIC32CX-BZ Device Support')

## Device Support
if (deviceName in pic32cx_bz2_family):
    initDeviceSupport = Module.CreateComponent('pic32cx_bz2_devsupport', 'Device_Support', '/Wireless/Drivers/PIC32CX-BZ System Services', 'driver/pic32cx-bz/config/device_support.py')
    initDeviceSupport.setDisplayType('PIC32CX-BZ2 Device Support')
elif (deviceName in pic32cx_bz3_family):
    initDeviceSupport = Module.CreateComponent('pic32cx_bz3_devsupport', 'Device_Support', '/Wireless/Drivers/PIC32CX-BZ System Services', 'driver/pic32cx-bz/config/device_support.py')
    initDeviceSupport.setDisplayType('PIC32CX-BZ3 Device Support')
initDeviceSupport.addCapability('Device_Support_Capability', 'Device_Support', True)
initDeviceSupport.addDependency('HarmonyCoreDependency', 'Core Service', 'Core Service', True, True)
if (deviceName in pic32cx_bz2_family):
    initDeviceSupport.addDependency('PIC32CX_BZ2_BOOTLOADER_SERVICES', 'PIC32CX_BZ_BOOTLOADER_SERVICES', 'Bootloader Services', False, False)
