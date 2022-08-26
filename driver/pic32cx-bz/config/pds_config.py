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
                      'WBZ435',
                      }

def isOTAEnabled(symbol, event):
    if ((event["value"] == True)):
        symbol.setValue(True)
    else:
        symbol.setValue(False)

processor = Variables.get('__PROCESSOR')
print('processor={}'.format(processor))

############################################################################
### Add pds_config.h - File
############################################################################
pds_configHeaderFile = libPDS.createFileSymbol(None, None)
pds_configHeaderFile.setSourcePath('driver/pic32cx-bz/templates/pds/pds_config.h.ftl')
pds_configHeaderFile.setOutputName('pds_config.h')
pds_configHeaderFile.setDestPath('driver/pds/include')
pds_configHeaderFile.setProjectPath('config/' + configName + '/driver/pds/include/')
pds_configHeaderFile.setType('HEADER')
pds_configHeaderFile.setOverwrite(True)
pds_configHeaderFile.setMarkup(True)


############################################################################
### Add logic for adding BLE stack 
############################################################################
# This boolean is controlled in:
#   onAttachmentConnected and onAttachmentDisconnected
bleStackLoaded = libPDS.createBooleanSymbol("BLESTACK_LOADED", None)
bleStackLoaded.setDefaultValue('BLE_STACK_LIB' in Database.getActiveComponentIDs())
bleStackLoaded.setVisible(False)

############################################################################
### Add logic for adding Zigbee stack
############################################################################
# This boolean is controlled in:
#   onAttachmentConnected and onAttachmentDisconnected
zigbeeStackLoaded = libPDS.createBooleanSymbol("ZIGBEESTACK_LOADED", None)
zigbeeStackLoaded.setDefaultValue(['ZIGBEE_COLOR_SCENE_CONTROLLER' or 'ZIGBEE_MULTI_SENSOR' or 'ZIGBEE_COMBINED_INTERFACE' or 
                                  'ZIGBEE_THERMOSTAT' or 'ZIGBEE_IAS_ACE' or 'ZIGBEE_ON_OFF_LIGHT' or 'ZIGBEE_DIMMABLE_LIGHT' or 
                                  'ZIGBEE_COLOR_LIGHT' or 'ZIGBEE_EXTENDED_COLOR_LIGHT' or 'ZIGBEE_TEMPERATURE_COLOR_LIGHT' or 
                                  'ZIGBEE_CUSTOM' or 'ZIGBEE_GPD_SENSOR' or 'ZIGBEE_ZAPPSI'] in Database.getActiveComponentIDs())
zigbeeStackLoaded.setVisible(False)

############################################################################
### Add logic for adding OTA as part of Linker file
############################################################################
otaEnabled = libPDS.createBooleanSymbol("OTA_ENABLED", None)
otaEnabled.setDefaultValue(False)
otaEnabled.setVisible(False)
otaEnabled.setDependencies(isOTAEnabled, ["BootloaderServices:OTA_ENABLE"])

otaFwSignVerify = libPDS.createBooleanSymbol("OTA_FW_SIGN_VERIFY", None)
otaFwSignVerify.setDefaultValue(False)
otaFwSignVerify.setVisible(False)
otaFwSignVerify.setDependencies(isOTAEnabled, ["BootloaderServices:APP_FW_SIGN_VERIFY"])
############################################################################
### Create Application configuration items for PDS
############################################################################
PDS_DisplayApps = libPDS.createIntegerSymbol("PDS_APPS_ITEM_IDS", None)
PDS_DisplayApps.setDefaultValue(0)
PDS_DisplayApps.setMax(10)
PDS_DisplayApps.setMin(0)
PDS_DisplayApps.setVisible(True)
PDS_DisplayApps.setReadOnly(False)

PDS_DisplayApps1 = libPDS.createIntegerSymbol("PDS_APPS_DIRECTORY_IDS", None)
PDS_DisplayApps1.setDefaultValue(0)
PDS_DisplayApps1.setMax(10)
PDS_DisplayApps1.setMin(0)
PDS_DisplayApps1.setVisible(True)
PDS_DisplayApps1.setReadOnly(False)


############################################################################
### Linker File OverWrite - Yog( workaround for PDS)
############################################################################
pdsLinkerFile = libPDS.createFileSymbol("PDS_LINKER_FILE", None)
if (processor in pic32cx_bz2_family):
    pdsLinkerFile.setSourcePath("driver/pic32cx-bz/templates/PIC32CX1012BZ25048.ld.ftl")
elif (processor in pic32cx_bz3_family):
    pdsLinkerFile.setSourcePath("driver/pic32cx-bz/templates/pds/pic32cx_bz3_pds.ld")


pdsLinkerFile.setOutputName("{0}.ld".format(processor))
pdsLinkerFile.setMarkup(True)
pdsLinkerFile.setOverwrite(True)
pdsLinkerFile.setType("LINKER")

