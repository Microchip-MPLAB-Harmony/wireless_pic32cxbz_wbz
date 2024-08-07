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

######################  Harmony wireless_pic32cxbz_wbz  ######################
def loadModule():
    print('Load Module: Harmony Wireless PIC32CXBZ_WBZ')

    pic32cx_bz2_family = {'PIC32CX1012BZ25048',
                          'PIC32CX1012BZ25032',
                          'PIC32CX1012BZ24032',
                          'WBZ451',
                          'WBZ450',
                          'WBZ451H',
                          }

    pic32cx_bz3_family = {'PIC32CX5109BZ31048',
                          'PIC32CX5109BZ31032',
                          'WBZ351',
                          'WBZ350',
                          }
    pic32cx_bz3_module_family = {'WBZ351',
                                }
    processor = Variables.get('__PROCESSOR')
    print('processor={}'.format(processor))

    if((processor in pic32cx_bz2_family) or (processor in pic32cx_bz3_family)):
        ## Device Support
        execfile(Module.getPath() + '/config/module_pic32cx_bz_device_support.py')
        ## Persistant Data Storage
        execfile(Module.getPath() + '/config/module_pic32cx_bz_pds.py')    
    
    if( processor in pic32cx_bz2_family):
        ## PIC32CX-BZ2 Bootloader
        execfile(Module.getPath() + '/config/module_pic32cx_bz2_bootloader.py')
        ## PIC32CX-BZ2 Bootloader services
        execfile(Module.getPath() + '/config/module_pic32cx_bz2_bootloaderServices.py')

    if( processor in pic32cx_bz3_module_family):
        ## PIC32CX-BZ3 Bootloader
        execfile(Module.getPath() + '/config/module_pic32cx_bz3_bootloader.py')

