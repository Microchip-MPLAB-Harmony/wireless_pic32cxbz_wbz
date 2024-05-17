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

################################################################################
######################### PDS Configurations ###################################
################################################################################


################################################################################
################################# Component ####################################
################################################################################
def finalizeComponent(pdsComponent):
    res = Database.activateComponents(["nvm"])
    result = Database.connectDependencies([['pdsSystem', 'NVM_Dependency', 'nvm', 'NVM_MEMORY']])

def instantiateComponent(libPDS):
    print('PDS')
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
    global deviceName
    deviceName = Variables.get("__PROCESSOR")
    configName = Variables.get('__CONFIGURATION_NAME')

    execfile(Module.getPath() +"/driver/pic32cx-bz/config/pds_interface.py")

    ############################################################################
    ### Activate dependencies
    ############################################################################
    res = Database.activateComponents(["nvm"])

    execfile(Module.getPath() +"/driver/pic32cx-bz/config/pds_config.py")

    ############################################################################
    #### System Code Generation ####
    ############################################################################

    # Add include files to definitions.h
    libBTZBCoreSystemDefFile = libPDS.createFileSymbol('PDS_SYS_BZ_DEF', None)
    libBTZBCoreSystemDefFile.setType('STRING')
    libBTZBCoreSystemDefFile.setOutputName('core.LIST_SYSTEM_DEFINITIONS_H_INCLUDES')
    libBTZBCoreSystemDefFile.setSourcePath('driver/pic32cx-bz/templates/pds/system/system_definitions.h.ftl')
    libBTZBCoreSystemDefFile.setMarkup(True)

    # Add Library data to initialization.c
    libBTZBCoreSystemInitDataFile = libPDS.createFileSymbol('PDS_SYS_INIT_DATA', None)
    libBTZBCoreSystemInitDataFile.setType('STRING')
    libBTZBCoreSystemInitDataFile.setOutputName('core.LIST_SYSTEM_INIT_C_LIBRARY_INITIALIZATION_DATA')
    libBTZBCoreSystemInitDataFile.setSourcePath('driver/pic32cx-bz/templates/pds/system/system_initialize_data.c.ftl')
    libBTZBCoreSystemInitDataFile.setMarkup(True)

    # Add initializer and initialization code to SYS_Initialize in initialization.c
    libBTZBCoreSystemInitDriverFile = libPDS.createFileSymbol('PDS_SYS_INIT', None)
    libBTZBCoreSystemInitDriverFile.setType('STRING')
    libBTZBCoreSystemInitDriverFile.setOutputName('core.LIST_SYSTEM_INIT_C_SYS_INITIALIZE_DRIVERS')
    libBTZBCoreSystemInitDriverFile.setSourcePath('driver/pic32cx-bz/templates/pds/system/system_initialize.c.ftl')
    libBTZBCoreSystemInitDriverFile.setMarkup(True)


    ############################################################################
    ### Add pds library files
    ############################################################################

    # Add pds.a library
    pds_a = libPDS.createLibrarySymbol(None, None)
    pds_a.setDestPath('driver/pds')
    if (deviceName in pic32cx_bz2_family):
        pds_a.setSourcePath('driver/pic32cx-bz/src/src_bz2/pds/pds_bz2.a')
    elif (deviceName in pic32cx_bz3_family):
        pds_a.setSourcePath('driver/pic32cx-bz/src/src_bz3/pds/pds_bz3.a')
    pds_a.setOutputName('pds.a')

    ############################################################################
    ### Add pic32cx-bz static header files
    ############################################################################

    # Add pds.h file
    pdsHeaderFile = libPDS.createFileSymbol(None, None)
    if (deviceName in pic32cx_bz2_family):
        pdsHeaderFile.setSourcePath('driver/pic32cx-bz/src/src_bz2/pds/pds.h')
    elif (deviceName in pic32cx_bz3_family):
        pdsHeaderFile.setSourcePath('driver/pic32cx-bz/src/src_bz3/pds/pds.h')
    pdsHeaderFile.setOutputName('pds.h')
    pdsHeaderFile.setOverwrite(True)
    pdsHeaderFile.setDestPath('driver/pds/include')
    pdsHeaderFile.setProjectPath('config/' + configName + '/driver/pds/include/')
    pdsHeaderFile.setType('HEADER')
    pdsHeaderFile.setEnabled(True)


###############################################################################
### Process dependency connections to determine which PDS clients are loaded
###############################################################################
"""
REQUIRES_PDS contains a list H3 component IDs and their
corresponding boolean symbol IDs.  These boolean symbols are used to track
whether or not the H3 component has been loaded.  The booleans are used both
in this script and in the ftl templates.
"""
REQUIRES_PDS = {'BLE_STACK_LIB': 'BLESTACK_LOADED',
                'ZIGBEE_COLOR_SCENE_CONTROLLER': 'ZIGBEESTACK_LOADED',
                'ZIGBEE_MULTI_SENSOR': 'ZIGBEESTACK_LOADED',
                'ZIGBEE_COMBINED_INTERFACE': 'ZIGBEESTACK_LOADED',
                'ZIGBEE_THERMOSTAT': 'ZIGBEESTACK_LOADED',
                'ZIGBEE_IAS_ACE': 'ZIGBEESTACK_LOADED',
                'ZIGBEE_ON_OFF_LIGHT': 'ZIGBEESTACK_LOADED',
                'ZIGBEE_DIMMABLE_LIGHT': 'ZIGBEESTACK_LOADED',
                'ZIGBEE_COLOR_LIGHT': 'ZIGBEESTACK_LOADED',
                'ZIGBEE_EXTENDED_COLOR_LIGHT': 'ZIGBEESTACK_LOADED',
                'ZIGBEE_TEMPERATURE_COLOR_LIGHT': 'ZIGBEESTACK_LOADED',
                'ZIGBEE_CUSTOM': 'ZIGBEESTACK_LOADED',
                'ZIGBEE_GPD_SENSOR': 'ZIGBEESTACK_LOADED',
                'ZIGBEE_ZAPPSI': 'ZIGBEESTACK_LOADED',
                'OPEN_THREAD': 'THREADSTACK_LOADED'
               }

def onAttachmentConnected(source, target):
    Log.writeInfoMessage('pds_subsystem:onAttachmentConnected: source = {} remote = {}'.format(source["component"].getID(), target["component"].getID()))
    if target["component"].getID() in REQUIRES_PDS.keys():
        boolSymbol = source["component"].getSymbolByID(REQUIRES_PDS[target["component"].getID()])
        Log.writeInfoMessage('pds_subsystem:onAttachmentConnected: setting {} to True'.format(boolSymbol.getID()))
        boolSymbol.setValue(True)

def onAttachmentDisconnected(source, target):
    Log.writeInfoMessage('pds_subsystem:onAttachmentDisconnected: source = {} remote = {}'.format(source["component"].getID(), target["component"].getID()))
    if target["component"].getID() in REQUIRES_PDS.keys():
        boolSymbol = source["component"].getSymbolByID(REQUIRES_PDS[target["component"].getID()])
        Log.writeInfoMessage('pds_subsystem:onAttachmentConnected: setting {} to False'.format(boolSymbol.getID()))
        boolSymbol.setValue(False)
