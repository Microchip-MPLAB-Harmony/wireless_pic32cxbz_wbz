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

def instantiateComponent(libOta):
    print('PIC32CX-BZ OTA')
    processor = Variables.get('__PROCESSOR')
    print('processor={}'.format(processor))
    configName = Variables.get('__CONFIGURATION_NAME')
    listV = Variables.getNames()
    for element in listV:
        print('"{}" value is "{}"'.format(element, Variables.get(element)))
        
    fileDestPath = '../../../' + Variables.get('__PROJECT_FOLDER_NAME') + '/'
    print('fileDestPath = "{}" '.format(fileDestPath))

    # Enable support for Firmware Signature Validation
    fwSignCheckbox = libOta.createBooleanSymbol("APP_FW_SIGN_VERIFY", None)
    fwSignCheckbox.setLabel("Use Firmware Signature Verifcation API in Bootloader")
    fwSignCheckbox.setDescription("This option can be used to validate OTA image's Signature. Need to increase 3.5KB Stack Size of FreeRTOS Configuration")
    fwSignCheckbox.setDefaultValue(False)
    fwSignCheckbox.setVisible(True)
    fwSignCheckbox.setReadOnly(False)
    fwSignCheckbox.setDependencies(fwSignVerifyDependency, ["APP_FW_SIGN_VERIFY"])
    
    Database.setSymbolValue("core", "ADD_LINKER_FILE", False)
    
    #Add OTA_Enable boolean symbol for using with linker ftl file
    global otaEnable
    otaEnable = libOta.createBooleanSymbol("OTA_ENABLE", None)
    otaEnable.setDefaultValue(True)
    otaEnable.setVisible(False)
    otaEnable.setReadOnly(True)

    ############################################################################
    ### Add linker - File
    ############################################################################

    #Linker File OverWrite
    otaLinkerFile = libOta.createFileSymbol("OTA_LINKER_FILE", None)
    otaLinkerFile.setSourcePath("driver/pic32cx-bz/templates/PIC32CX1012BZ25048_ota_nopds.ld.ftl")
    otaLinkerFile.setOutputName("{0}.ld".format(processor))
    otaLinkerFile.setMarkup(True)
    otaLinkerFile.setOverwrite(True)
    otaLinkerFile.setType("LINKER")
    otaLinkerFile.setEnabled(Database.getComponentByID("pdsSystem") == None)
    otaLinkerFile.setDependencies(enableFwSign, ["APP_FW_SIGN_VERIFY", "OTA_ENABLE"])


    ############################################################################
    ### Add autoload.py - File
    ############################################################################

    autoloadPythonScriptFile = libOta.createFileSymbol(None, None)
    autoloadPythonScriptFile.setSourcePath('utilities/pic32cx-bz/autoload.py')
    autoloadPythonScriptFile.setOutputName('autoload.py')
    autoloadPythonScriptFile.setOverwrite(True)
    autoloadPythonScriptFile.setDestPath(fileDestPath)
    autoloadPythonScriptFile.setProjectPath('')
    autoloadPythonScriptFile.setType('IMPORTANT')
    autoloadPythonScriptFile.setEnabled(True)

    ############################################################################
    ### Add key pem - File
    ############################################################################

    javaKeyPemFile = libOta.createFileSymbol(None, None)
    javaKeyPemFile.setSourcePath('utilities/pic32cx-bz/java_friendly_private_key.pem')
    javaKeyPemFile.setOutputName('java_friendly_private_key.pem')
    javaKeyPemFile.setOverwrite(True)
    javaKeyPemFile.setDestPath(fileDestPath)
    javaKeyPemFile.setProjectPath('')
    javaKeyPemFile.setType('IMPORTANT')
    javaKeyPemFile.setEnabled(True)

    


#If the checkbox for re-using FW Image Signature validation is enabled, cannot use the default linker script
def fwSignVerifyDependency(symbol, event):
    print('PIC32CX-BZ OTA Application - Support FW Image Signature Verification - Linker modification')
    localComponent = symbol.getComponent()
    componentId = localComponent.getID()
    print('OTA componentId = "{}" '.format(componentId))
    # Increase the stack size to 5KB if enabled, set to default value if disabled
    if (event["value"] == True):
        Database.setSymbolValue("HarmonyCore", "GEN_APP_RTOS_TASK_0_SIZE", 5120)
    else:
        Database.clearSymbolValue("HarmonyCore", "GEN_APP_RTOS_TASK_0_SIZE")

#Dependency callback once firmware Signature verification in enabled in the application
def enableFwSign(symbol, event):
    symbol.setEnabled(event["value"])


def onAttachmentConnected(source, target):
    print('OTA component - onAttachmentConnected event')
    otaEnable.setValue(True)

def onAttachmentDisconnected(source, target):
    print('OTA component - onAttachmentDisconnected event')
    otaEnable.setValue(False)

