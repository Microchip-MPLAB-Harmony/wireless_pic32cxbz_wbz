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
print('Load Module: Harmony Wireless PIC32CX-BZ PDS Support')

## PDS Support
initPDSComponent = Module.CreateComponent('pdsSystem', 'PDS_SubSystem', '/Wireless/Drivers/PIC32CX-BZ System Services', 'driver/pic32cx-bz/config/pds_subsystem.py')
initPDSComponent.setDisplayType('Persistant Data Storage')
initPDSComponent.addCapability('pds_Command_Capability', 'PDS_SubSystem', True)
if (deviceName in pic32cx_bz2_family):
    initPDSComponent.addDependency('PIC32CX_BZ2_DevSupport_Dependency', 'Device_Support', None, True, True)
elif (deviceName in pic32cx_bz3_family):
    initPDSComponent.addDependency('PIC32CX_BZ3_DevSupport_Dependency', 'Device_Support', None, True, True)
initPDSComponent.addDependency("NVM_Dependency", "MEMORY", None, False, True)

