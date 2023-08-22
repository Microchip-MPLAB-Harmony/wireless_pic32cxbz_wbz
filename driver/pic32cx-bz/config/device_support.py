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

"""
REQUIRES_APP_IDLE_TASK contains a list H3 component IDs and their
corresponding boolean symbol IDs.  These boolean symbols are used to track
whether or not the H3 component has been loaded.  The booleans are used both
in this script and in the ftl templates.
"""
pic32cx_bz2_family = {'PIC32CX1012BZ25048',
                      'PIC32CX1012BZ25032',
                      'PIC32CX1012BZ24032',
                      'WBZ451',
                      'WBZ450',
                      }

pic32cx_bz2_48pin_family = {'PIC32CX1012BZ25048',
                            'WBZ451',
                            }

pic32cx_bz3_family = {'PIC32CX5109BZ31048',
                      'PIC32CX5109BZ31032',
                      'WBZ351',
                      'WBZ350',
                      }

pic32cx_bz3_48pin_family = {'PIC32CX5109BZ31048',
                            'WBZ351',
                           }

global deviceName
deviceName = Variables.get("__PROCESSOR")

REQUIRES_APP_IDLE_TASK = {
        'BLE_STACK_LIB': 'BLESTACK_LOADED',
        'pdsSystem': 'PDS_LOADED',
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
        'ZIGBEE_MACWSNTESTER': 'ZIGBEESTACK_LOADED',
        'ZIGBEE_GPD_SENSOR': 'ZIGBEESTACK_LOADED',
        'ZIGBEE_ZAPPSI': 'ZIGBEESTACK_LOADED',
        'OPEN_THREAD': 'THREADSTACK_LOADED',
        'IEEE_802154_PHY': '802154_PHY_LOADED'}


REQUIRES_RTC_SUPPORT = {}
REQUIRES_WSSENABLE_MODE = {}

RADIOSTACK_COMPONENTS = [
        'BLE_STACK_LIB',
        'ZIGBEE_COLOR_SCENE_CONTROLLER',
        'ZIGBEE_MULTI_SENSOR',
        'ZIGBEE_COMBINED_INTERFACE',
        'ZIGBEE_THERMOSTAT',
        'ZIGBEE_IAS_ACE',
        'ZIGBEE_ON_OFF_LIGHT',
        'ZIGBEE_DIMMABLE_LIGHT',
        'ZIGBEE_COLOR_LIGHT',
        'ZIGBEE_EXTENDED_COLOR_LIGHT',
        'ZIGBEE_TEMPERATURE_COLOR_LIGHT',
        'ZIGBEE_CUSTOM',
        'ZIGBEE_MACWSNTESTER',
        'ZIGBEE_GPD_SENSOR',
        'ZIGBEE_ZAPPSI',
        'OPEN_THREAD',
        'IEEE_802154_PHY'
        ]

activeComponents = Database.getActiveComponentIDs()


def configWSSEnable(component, targetID, connected):
    """
    This functions sets the WSSEnable mode based on which radio stacks are loaded
    """
    # Debug information
    Log.writeInfoMessage('device_support:configWSSEnable: component = {} target = {}, connected = {}'.
            format(component.getID(), targetID, str(connected)))

    wssEnable_t = {
                    'none': 'WSS_ENABLE_NONE',
                    'ble_only': 'WSS_ENABLE_BLE',
                    'zigbee_only': 'WSS_ENABLE_ZB',
                    'ble_zigbee': 'WSS_ENABLE_BLE_ZB',
                  }

    ####################################################################
    # if a radio stack was connected or disconnected record it here
    ####################################################################
    if targetID in RADIOSTACK_COMPONENTS:
        REQUIRES_WSSENABLE_MODE[targetID] = connected

        # if any modules in REQUIRES_WSSENABLE_MODE are True then radioStackLoaded is True
        radioStackLoaded = not all(required==False for required in REQUIRES_WSSENABLE_MODE.values())

        # Get the WSS_ENABLE_MODE symbols
        wssEnableSymbol = component.getSymbolByID('WSS_ENABLE_MODE')

        if radioStackLoaded:
            ble_loaded = False
            # check for the BLE stack component
            if 'BLE_STACK_LIB' in REQUIRES_WSSENABLE_MODE.keys():
                ble_loaded = REQUIRES_WSSENABLE_MODE['BLE_STACK_LIB']

            zigbee_loaded = False
            # check for any Zigbee stack component
            for stackName in REQUIRES_WSSENABLE_MODE:
                Log.writeInfoMessage('device_support:configWSSEnable:   stackName = {} connected = {}'.
                        format(stackName, str(REQUIRES_WSSENABLE_MODE[stackName])))

                if 'ZIGBEE' in stackName and REQUIRES_WSSENABLE_MODE[stackName]:
                    zigbee_loaded = True
                    
                if 'IEEE802154_PHY' in stackName and REQUIRES_WSSENABLE_MODE[stackName]:
                    zigbee_loaded = True

                if 'OPEN_THREAD' in stackName and REQUIRES_WSSENABLE_MODE[stackName]:
                    zigbee_loaded = True

            if ble_loaded and zigbee_loaded:
                wssEnableMode = wssEnable_t['ble_zigbee']
            elif ble_loaded:
                wssEnableMode = wssEnable_t['ble_only']
            elif zigbee_loaded:
                wssEnableMode = wssEnable_t['zigbee_only']

        else:
            wssEnableMode = wssEnable_t['none']

        Log.writeInfoMessage('device_support:configWSSEnable: setting WSS_ENABLE_MODE to {}'.format(wssEnableMode))
        wssEnableSymbol.setValue(wssEnableMode)



def configAppIdleTask(component, targetID, connected):
    """
    This function must only be called when the targetID exists as a key in the
    REQUIRES_APP_IDLE_TASK dictionary.

    The boolean symbol tracking the H3 component is set or cleared based on the
    whether the H3 module is loaded or unloaded.

    If connected is True, then the app_idle_task files need to be generated.

    If connected is False and all the boolean symbols in
    REQUIRES_APP_IDLE_TASK are False, then the app_idle_task file should not
    be generated.
    """
    # Debug information
    Log.writeInfoMessage('device_support:configAppIdleTask: component = {} target = {}, connected = {}'.
            format(component.getID(), targetID, str(connected)))


    ####################################################################
    # Collect the information required to process this connection event
    ####################################################################
    APP_IDLE_FILE_SYMBOL_IDS = ['APP_IDLE_TASK_H', 'APP_IDLE_TASK_C', 'APP_USER_EDITS_C']

    # Collect the app_idle_task file symbols
    appIdleFileSymbols = [component.getSymbolByID(s) for s in APP_IDLE_FILE_SYMBOL_IDS]
    # Log.writeInfoMessage('device_support:configAppIdleTask: appIdleFileSymbols={}'.format(appIdleFileSymbols))

    # Debug information
    for fs in appIdleFileSymbols:
        Log.writeInfoMessage('device_support:configAppIdleTask: file = {}'.format(fs.getOutputName()))

    # Collect all the boolean symbol IDs related to the app_idle_task H3 modules
    boolSymbolIDs = set( val for val in REQUIRES_APP_IDLE_TASK.values())

    # # Debug information
    # for boolID in boolSymbolIDs:
    #     Log.writeInfoMessage('device_support:configAppIdleTask: {} entry value: {}'.format(boolID, component.getSymbolByID(boolID).getValue()))

    # Get the boolean symbol related to this event
    boolSymbolID = REQUIRES_APP_IDLE_TASK[targetID]
    boolSymbol = component.getSymbolByID(boolSymbolID)
    if boolSymbol == None:
        Log.writeErrorMessage('device_support:configAppIdleTask boolSymbol "{}" NOT found'.format(boolSymbolID))


    ####################################################################
    # Process the event
    ####################################################################
    if connected:
        # Enable generation of all of the app_idle_task files
        for fileSymbol in appIdleFileSymbols:
            Log.writeInfoMessage('device_support:configAppIdleTask: setEnabled(True) "{}"'.format(fileSymbol.getID()))
            fileSymbol.setEnabled(True)

        # Set the boolean associated with this H3 component
        boolSymbol.setValue(True)

        # Set the FreeRTOS idle hook symbol
        Database.setSymbolValue("FreeRTOS", "FREERTOS_IDLE_HOOK", True)

        Log.writeInfoMessage('device_support:configAppIdleTask: app_idle_task required')

    else:
        # Clear the boolean associated with this H3 component
        boolSymbol.setValue(False)

        # Check if other H3 components still require the app_idle_task files
        required = False
        for boolID in boolSymbolIDs:

            # # Debug information
            # Log.writeInfoMessage('device_support:configAppIdleTask: checking {}'.format(boolID))

            required |= component.getSymbolByID(boolID).getValue()
            if required:

                # Debug information
                Log.writeInfoMessage('device_support:configAppIdleTask: app_idle_task REQUIRED - {} = {}'.format(
                    boolID, component.getSymbolByID(boolID).getValue()))

                break

        if not required:
            # Disable generation of all of the app_idle_task files
            for fileSymbol in appIdleFileSymbols:
                Log.writeInfoMessage('device_support:configAppIdleTask: setEnabled(False) "{}"'.format(fileSymbol.getID()))
                fileSymbol.setEnabled(False)

            # Clear the FreeRTOS idle hook symbol
            Database.setSymbolValue("FreeRTOS", "FREERTOS_IDLE_HOOK", False)        

            Log.writeInfoMessage('device_support:configAppIdleTask: app_idle_task NOT required')



    # Debug information
    for boolID in boolSymbolIDs:
        Log.writeInfoMessage('device_support:configAppIdleTask: {} exit value: {}'.format(boolID, str(component.getSymbolByID(boolID).getValue())))


def processPDSLoadUnload(source, value):
    Log.writeInfoMessage('device_support:processPDSLoadUnload({}, {})'.format(source.getID(), value))
    remoteComponent = 'pdsSystem'
    if value:
        source.setDependencyEnabled('PDS_Module', True)
        if remoteComponent not in Database.getActiveComponentIDs():
            Database.activateComponents(['pdsSystem'])
    else:
        source.setDependencyEnabled('PDS_Module', False)


def pdsLoadUnload(symbol, event):
    Log.writeInfoMessage('device_support:pdsLoadUnload({}, {})'.format(symbol.getID(), event["value"]))
    processPDSLoadUnload(event["source"], event["value"])


def getCorePFMWS():
    pfmws = int(Database.getSymbolValue("core", "CONFIG_CHECON_PFMWS"))
    return pfmws


def updatePFMWS(symbol, event):
    # print("pic32cx_bz2_sysservice: CONFIG_CHECON_PFMWS changed")
    symbol.setValue(getCorePFMWS())


def getCorePREFEN():
    return int(Database.getSymbolValue("core", "CONFIG_CHECON_PREFEN"))


def updatePREFEN(symbol, event):
    # print("pic32cx_bz2_sysservice: updatePREFEN called")
    symbol.setValue(getCorePREFEN())


def antGainEnable(symbol, event):
    Log.writeInfoMessage('device_support:antGainEnable(symbolID:{}, eventID:{}, eventValue:{})'.format(symbol.getID(), event["id"], event["value"]))
    if('CUSTOM_ANT_ENABLE' == event["id"]):
        symbol.setVisible(event["value"])

    sendAntMessage(event["id"], event["value"])


def antGainChanged(symbol, event):
    Log.writeInfoMessage('device_support:antGainChanged(symbolID:{}, eventID:{}, eventValue:{})'.format(symbol.getID(), event["id"], event["value"]))
    sendAntMessage(event["id"], event["value"])


def sendAntMessage(id, value):
    # This message function shares custom antenna configuration information with RADIOSTACK_COMPONENTS
    for client in RADIOSTACK_COMPONENTS:
        if client in Database.getActiveComponentIDs():
            Log.writeInfoMessage('{:<17}: Sending  - target={} ID={} Value={}'.format('device_support', client, id, value))
            Database.sendMessage(client, "ANTENNA_GAIN_CHANGE", {'target': client, id:value})

def getBLEStackLibDsadven():
    components = Database.getActiveComponentIDs()
    if('BLE_STACK_LIB' in components):
        dsadvSetting = Database.getSymbolValue("BLE_STACK_LIB", "GAP_DSADV_EN")
        return dsadvSetting
    return False

def getDeepSleepState():
    if (deepSleepEnable.getValue()):
        return True
    return False

def computeRetentionRAMRequirements():
    global stackRequirements
    print('computing Retention RAM Requirements')
    stackRequirements = 0
    components = Database.getActiveComponentIDs()
    if('BLE_STACK_LIB' in components):
        stackRequirements = 616
    if any("ZIGBEE" in s for s in components):
        stackRequirements = stackRequirements + 2048
    return stackRequirements

def computeMaxAppRetentionRAM():
    appRequirements = 0
    if (deviceName in pic32cx_bz2_family):
        appRequirements = (8192 - stackRetentionRAM.getValue())
    elif (deviceName in pic32cx_bz3_family):
        appRequirements = (32768 - stackRetentionRAM.getValue())
    return appRequirements

def instantiateComponent(libBTZBCore):
    print('PIC32CX-BZ BTZB_Common')
    configName = Variables.get('__CONFIGURATION_NAME')

    libBTZBCore.addDependency('PDS_Module', 'PDS_SubSystem', None, True, True)
    libBTZBCore.addDependency('RTC_Module', 'TMR', 'RTC', False, False)
    libBTZBCore.addDependency("harmony_RTOS_dependency", "RTOS", True, False)

    ############################################################################
    ### Deactivate unsued components
    ############################################################################
    # deactivate unused components
    # unusedComponents = ['evsys']
    unusedComponents = []
    for u in unusedComponents:
        if u in activeComponents:
            print("found component '{}' - deactivating it".format(u))
            res = Database.deactivateComponents([u])


    ############################################################################
    ### Activate dependencies
    ############################################################################
    # activate required components
    requiredComponents = ['HarmonyCore']
    for r in requiredComponents:
        if r not in activeComponents:
            print("require component '{}' - activating it".format(r))
            res = Database.activateComponents([r])


    ############################################################################
    #### System Code Generation ####
    ############################################################################

    # Add include files to definitions.h
    libBTZBCoreSystemDefFile = libBTZBCore.createFileSymbol('LIB_BTZB_PIC32CX-BZ_DEF', None)
    libBTZBCoreSystemDefFile.setType('STRING')
    libBTZBCoreSystemDefFile.setOutputName('core.LIST_SYSTEM_DEFINITIONS_H_INCLUDES')
    libBTZBCoreSystemDefFile.setSourcePath('driver/pic32cx-bz/templates/system/system_definitions.h.ftl')
    libBTZBCoreSystemDefFile.setMarkup(True)

    # Add Library data to initialization.c
    libBTZBCoreSystemInitDataFile = libBTZBCore.createFileSymbol('LIBBTZBCORE_SYS_INIT_DATA', None)
    libBTZBCoreSystemInitDataFile.setType('STRING')
    libBTZBCoreSystemInitDataFile.setOutputName('core.LIST_SYSTEM_INIT_C_LIBRARY_INITIALIZATION_DATA')
    libBTZBCoreSystemInitDataFile.setSourcePath('driver/pic32cx-bz/templates/system/system_initialize_data.c.ftl')
    libBTZBCoreSystemInitDataFile.setMarkup(True)

    # Add initialization code to SYSTEM_INITIALIZATION in initialization.c
    libBTZBCoreSystemInitStartFile = libBTZBCore.createFileSymbol('LIBBTZBCORE_SYSTEM_INITIALIZATION', None)
    libBTZBCoreSystemInitStartFile.setType('STRING')
    libBTZBCoreSystemInitStartFile.setOutputName('core.LIST_SYSTEM_INIT_C_SYSTEM_INITIALIZATION')
    libBTZBCoreSystemInitStartFile.setSourcePath('driver/pic32cx-bz/templates/system/system_initialize_initialization.c.ftl')
    libBTZBCoreSystemInitStartFile.setMarkup(True)

    # Add initializer to SYS_INITIALIZE_START in initialization.c
    libBTZBCoreSystemInitStartFile = libBTZBCore.createFileSymbol('LIBBTZBCORE_SYS_INIT_START', None)
    libBTZBCoreSystemInitStartFile.setType('STRING')
    libBTZBCoreSystemInitStartFile.setOutputName('core.LIST_SYSTEM_INIT_C_SYS_INITIALIZE_START')
    libBTZBCoreSystemInitStartFile.setSourcePath('driver/pic32cx-bz/templates/system/system_initialize_start.c.ftl')
    libBTZBCoreSystemInitStartFile.setMarkup(True)

    # Add initializer and initialization code to SYS_Initialize in initialization.c
    libBTZBCoreSystemInitDriverFile = libBTZBCore.createFileSymbol('LIBBTZBCORE_SYS_INIT_DRIVERS', None)
    libBTZBCoreSystemInitDriverFile.setType('STRING')
    libBTZBCoreSystemInitDriverFile.setOutputName('core.LIST_SYSTEM_INIT_C_SYS_INITIALIZE_DRIVERS')
    libBTZBCoreSystemInitDriverFile.setSourcePath('driver/pic32cx-bz/templates/system/system_initialize_drivers.c.ftl')
    libBTZBCoreSystemInitDriverFile.setMarkup(True)

    # # FIXME: Remove this!  This is a stop-gap workaround until H3 csp is updated
    # pche_checon_workaround = libBTZBCore.createFileSymbol('LIBBTZBCORE_SYS_INIT_CORE', None)
    # pche_checon_workaround.setType('STRING')
    # pche_checon_workaround.setOutputName('core.LIST_SYSTEM_INIT_C_SYS_INITIALIZE_CORE')
    # pche_checon_workaround.setSourcePath('driver/pic32cx-bz/templates/system/system_initialize_core.c.ftl')
    # libBTZBCoreSystemInitDriverFile.setMarkup(True)


    ############################################################################
    #### Code Generation ####
    ############################################################################

    ############################################################################
    ### Add pic32cx-bz2 device_support library files
    ############################################################################

    # Add pic32cx_bz2_device_support.a library
    sys_service_a = libBTZBCore.createLibrarySymbol(None, None)
    sys_service_a.setDestPath('driver/device_support')
    if (deviceName in pic32cx_bz2_family):
        sys_service_a.setSourcePath('driver/pic32cx-bz/src/src_bz2/device_support/pic32cx_bz2_device_support.a')
        sys_service_a.setOutputName('pic32cx_bz2_device_support.a')
    elif (deviceName in pic32cx_bz3_family):
        sys_service_a.setSourcePath('driver/pic32cx-bz/src/src_bz3/device_support/pic32cx_bz3_device_support.a')
        sys_service_a.setOutputName('pic32cx_bz3_device_support.a')


    ############################################################################
    ### Add pic32cx-bz static header files
    ############################################################################

    # Add rf_system.h file
    rfSysInitializeHeaderFile = libBTZBCore.createFileSymbol(None, None)
    if (deviceName in pic32cx_bz2_family):
        rfSysInitializeHeaderFile.setSourcePath('driver/pic32cx-bz/src/src_bz2/device_support/rf_system.h')
    elif (deviceName in pic32cx_bz3_family):
        rfSysInitializeHeaderFile.setSourcePath('driver/pic32cx-bz/src/src_bz3/device_support/rf_system.h')
    rfSysInitializeHeaderFile.setOutputName('rf_system.h')
    rfSysInitializeHeaderFile.setOverwrite(True)
    rfSysInitializeHeaderFile.setDestPath('driver/device_support/include')
    rfSysInitializeHeaderFile.setProjectPath('config/' + configName + '/driver/device_support/include/')
    rfSysInitializeHeaderFile.setType('HEADER')
    rfSysInitializeHeaderFile.setEnabled(True)

    # Add pmu_system.h file
    pmuSystemHeaderFile = libBTZBCore.createFileSymbol(None, None)
    if (deviceName in pic32cx_bz2_family):
        pmuSystemHeaderFile.setSourcePath('driver/pic32cx-bz/src/src_bz2/device_support/pmu_system.h')
    elif (deviceName in pic32cx_bz3_family):
        pmuSystemHeaderFile.setSourcePath('driver/pic32cx-bz/src/src_bz3/device_support/pmu_system.h')
    pmuSystemHeaderFile.setOutputName('pmu_system.h')
    pmuSystemHeaderFile.setOverwrite(True)
    pmuSystemHeaderFile.setDestPath('driver/device_support/include')
    pmuSystemHeaderFile.setProjectPath('config/' + configName + '/driver/device_support/include/')
    pmuSystemHeaderFile.setType('HEADER')
    pmuSystemHeaderFile.setEnabled(True)
    
    # Add info_block.h file
    infoBlockHeaderFile = libBTZBCore.createFileSymbol(None, None)
    if (deviceName in pic32cx_bz2_family):
        infoBlockHeaderFile.setSourcePath('driver/pic32cx-bz/src/src_bz2/device_support/info_block.h')
    elif (deviceName in pic32cx_bz3_family):
        infoBlockHeaderFile.setSourcePath('driver/pic32cx-bz/src/src_bz3/device_support/info_block.h')
    infoBlockHeaderFile.setOutputName('info_block.h')
    infoBlockHeaderFile.setOverwrite(True)
    infoBlockHeaderFile.setDestPath('driver/device_support/include')
    infoBlockHeaderFile.setProjectPath('config/' + configName + '/driver/device_support/include/')
    infoBlockHeaderFile.setType('HEADER')
    infoBlockHeaderFile.setEnabled(True)
    
    # Add sleep_system.h file
    sleepSystemHeaderFile = libBTZBCore.createFileSymbol(None, None)
    if (deviceName in pic32cx_bz2_family):
        sleepSystemHeaderFile.setSourcePath('driver/pic32cx-bz/src/src_bz2/device_support/sleep_system.h')
    elif (deviceName in pic32cx_bz3_family):
        sleepSystemHeaderFile.setSourcePath('driver/pic32cx-bz/src/src_bz3/device_support/sleep_system.h')
    sleepSystemHeaderFile.setOutputName('sleep_system.h')
    sleepSystemHeaderFile.setOverwrite(True)
    sleepSystemHeaderFile.setDestPath('driver/device_support/include')
    sleepSystemHeaderFile.setProjectPath('config/' + configName + '/driver/device_support/include/')
    sleepSystemHeaderFile.setType('HEADER')
    sleepSystemHeaderFile.setEnabled(True)
    
    # Add framework_defs.h
    HeaderFile = libBTZBCore.createFileSymbol(None, None)
    if (deviceName in pic32cx_bz2_family):
        HeaderFile.setSourcePath('driver/pic32cx-bz/src/src_bz2/app_fw/framework_defs.h')
    elif (deviceName in pic32cx_bz3_family):
        HeaderFile.setSourcePath('driver/pic32cx-bz/src/src_bz3/app_fw/framework_defs.h')
    HeaderFile.setOutputName('framework_defs.h')
    HeaderFile.setOverwrite(True)
    HeaderFile.setDestPath('')
    HeaderFile.setProjectPath('config/' + configName)
    HeaderFile.setType('HEADER')
    HeaderFile.setEnabled(True)

    # Add osal_freertos_extend.h
    HeaderFile = libBTZBCore.createFileSymbol(None, None)
    if (deviceName in pic32cx_bz2_family):
        HeaderFile.setSourcePath('driver/pic32cx-bz/src/src_bz2/app_fw/osal_freertos_extend.h')
    elif (deviceName in pic32cx_bz3_family):
        HeaderFile.setSourcePath('driver/pic32cx-bz/src/src_bz3/app_fw/osal_freertos_extend.h')
    HeaderFile.setOutputName('osal_freertos_extend.h')
    HeaderFile.setOverwrite(True)
    HeaderFile.setDestPath('/osal')
    HeaderFile.setProjectPath('config/' + configName + '/osal/')
    HeaderFile.setType('HEADER')
    HeaderFile.setEnabled(True)

    # Add osal_freertos.h
    HeaderFile = libBTZBCore.createFileSymbol(None, None)
    if (deviceName in pic32cx_bz2_family):
        HeaderFile.setSourcePath('driver/pic32cx-bz/src/src_bz2/app_fw/osal_freertos.h')
    elif (deviceName in pic32cx_bz3_family):
        HeaderFile.setSourcePath('driver/pic32cx-bz/src/src_bz3/app_fw/osal_freertos.h')
    HeaderFile.setOutputName('osal_freertos.h')
    HeaderFile.setOverwrite(True)
    HeaderFile.setDestPath('/osal')
    HeaderFile.setProjectPath('config/' + configName + '/osal/')
    HeaderFile.setType('HEADER')
    HeaderFile.setEnabled(True)

    # Add osal.h
    HeaderFile = libBTZBCore.createFileSymbol(None, None)
    if (deviceName in pic32cx_bz2_family):
        HeaderFile.setSourcePath('driver/pic32cx-bz/src/src_bz2/app_fw/osal.h')
    elif (deviceName in pic32cx_bz3_family):
        HeaderFile.setSourcePath('driver/pic32cx-bz/src/src_bz3/app_fw/osal.h')
    HeaderFile.setOutputName('osal.h')
    HeaderFile.setOverwrite(True)
    HeaderFile.setDestPath('/osal')
    HeaderFile.setProjectPath('config/' + configName + '/osal/')
    HeaderFile.setType('HEADER')
    HeaderFile.setEnabled(True)


    ############################################################################
    ### Add pic32cx-bz static source files
    ############################################################################

    # Add osal_freertos_extend.c
    SourceFile = libBTZBCore.createFileSymbol(None, None)
    if (deviceName in pic32cx_bz2_family):
        SourceFile.setSourcePath('driver/pic32cx-bz/src/src_bz2/app_fw/osal_freertos_extend.c')
    elif (deviceName in pic32cx_bz3_family):
        SourceFile.setSourcePath('driver/pic32cx-bz/src/src_bz3/app_fw/osal_freertos_extend.c')
    SourceFile.setOutputName('osal_freertos_extend.c')
    SourceFile.setOverwrite(True)
    SourceFile.setDestPath('/osal')
    SourceFile.setProjectPath('config/' + configName + '/osal/')
    SourceFile.setType('SOURCE')
    SourceFile.setEnabled(True)

   
    # Add osal_freertos.c
    SourceFile = libBTZBCore.createFileSymbol(None, None)
    if (deviceName in pic32cx_bz2_family):
        SourceFile.setSourcePath('driver/pic32cx-bz/src/src_bz2/app_fw/osal_freertos.c')
    elif (deviceName in pic32cx_bz3_family):
        SourceFile.setSourcePath('driver/pic32cx-bz/src/src_bz3/app_fw/osal_freertos.c')
    SourceFile.setOutputName('osal_freertos.c')
    SourceFile.setOverwrite(True)
    SourceFile.setDestPath('/osal')
    SourceFile.setProjectPath('config/' + configName + '/osal/')
    SourceFile.setType('SOURCE')
    SourceFile.setEnabled(True)

    # generate path for FreeRTOSConfig.h
    hooksPathString = libBTZBCore.createStringSymbol("FREERTOS_CONFIG_PATH", None)
    hooksPathString.setValue('config/' + configName + '/FreeRTOSConfig.h/')
    hooksPathString.setVisible(False)



    ############################################################################
    ### Add pic32cx-bz generated header files
    ############################################################################

    # Add app.h
    HeaderFile = libBTZBCore.createFileSymbol(None, None)
    HeaderFile.setSourcePath('driver/pic32cx-bz/templates/app.h.ftl')
    HeaderFile.setOutputName('app.h')
    HeaderFile.setOverwrite(True)
    HeaderFile.setDestPath('../../')
    HeaderFile.setProjectPath('')
    HeaderFile.setType('HEADER')
    HeaderFile.setMarkup(True)
    HeaderFile.setEnabled(True)

    # Application definitions from BLE
    dsAppBleMsgIdList = libBTZBCore.createListSymbol("LIST_DS_BLE_MSG_ID_H", None)

    # Add app_idle_task.h
    freertosidleTaskHeaderFile = libBTZBCore.createFileSymbol("APP_IDLE_TASK_H", None)
    if (deviceName in pic32cx_bz2_family):
        freertosidleTaskHeaderFile.setSourcePath("driver/pic32cx-bz/src/src_bz3/app_fw/app_idle_task.h")
    elif (deviceName in pic32cx_bz3_family):
        freertosidleTaskHeaderFile.setSourcePath("driver/pic32cx-bz/src/src_bz3/app_fw/app_idle_task.h")
    freertosidleTaskHeaderFile.setOutputName("app_idle_task.h")
    freertosidleTaskHeaderFile.setDestPath('../../')
    freertosidleTaskHeaderFile.setProjectPath('')
    freertosidleTaskHeaderFile.setType("HEADER")
    freertosidleTaskHeaderFile.setMarkup(False)
    # setEnabled is controlled in configAppIdleTask
    freertosidleTaskHeaderFile.setEnabled(False)


    ############################################################################
    ### Add pic32cx-bz generated source files
    ############################################################################

    # Add app.c
    SourceFile = libBTZBCore.createFileSymbol("DEVICE_APP_C", None)
    SourceFile.setSourcePath('driver/pic32cx-bz/templates/app.c.ftl')
    SourceFile.setOutputName('app.c')
    SourceFile.setOverwrite(True)
    SourceFile.setDestPath('../../')
    SourceFile.setProjectPath('')
    SourceFile.setType('SOURCE')
    SourceFile.setEnabled(True)
    SourceFile.setMarkup(True)

    # Application codes from BLE
    dsAppBleIncludeList = libBTZBCore.createListSymbol("LIST_DS_BLE_INCLUDE_C", None)
    dsAppBleDataList = libBTZBCore.createListSymbol("LIST_DS_BLE_DATA_C", None)
    dsAppBleInitList = libBTZBCore.createListSymbol("LIST_DS_BLE_INIT_C", None)
    dsAppBleTaskEntryList = libBTZBCore.createListSymbol("LIST_DS_BLE_TASK_ENTRY_C", None)

    # Add app_idle_task.c
    freertosidleTaskSourceFile = libBTZBCore.createFileSymbol("APP_IDLE_TASK_C", None)
    freertosidleTaskSourceFile.setSourcePath("driver/pic32cx-bz/templates/app_idle_task.c.ftl")
    freertosidleTaskSourceFile.setOutputName("app_idle_task.c")
    freertosidleTaskSourceFile.setDestPath('../../')
    freertosidleTaskSourceFile.setProjectPath('')
    freertosidleTaskSourceFile.setType("SOURCE")
    freertosidleTaskSourceFile.setMarkup(True)
    # setEnabled is controlled in configAppIdleTask
    freertosidleTaskSourceFile.setEnabled(False)

    # Add app_user_edits.c
    appUserEditsSourceFile = libBTZBCore.createFileSymbol("APP_USER_EDITS_C", None)
    appUserEditsSourceFile.setSourcePath("driver/pic32cx-bz/templates/app_user_edits.c.ftl")
    appUserEditsSourceFile.setOutputName("app_user_edits.c")
    appUserEditsSourceFile.setDestPath('../../')
    appUserEditsSourceFile.setProjectPath('')
    appUserEditsSourceFile.setType("SOURCE")
    appUserEditsSourceFile.setMarkup(True)
    # setEnabled is controlled in configAppIdleTask
    appUserEditsSourceFile.setEnabled(False)

    # Add device_deep_sleep.h
    global deviceDeepSleepHeaderFile
    deviceDeepSleepHeaderFile = libBTZBCore.createFileSymbol("DEVICE_DEEP_SLEEP_H", None)
    if (deviceName in pic32cx_bz2_family):
        deviceDeepSleepHeaderFile.setSourcePath("driver/pic32cx-bz/src/src_bz2/app_fw/device_deep_sleep.h")
    elif (deviceName in pic32cx_bz3_family):
        deviceDeepSleepHeaderFile.setSourcePath("driver/pic32cx-bz/src/src_bz3/app_fw/device_deep_sleep.h")
    deviceDeepSleepHeaderFile.setOutputName("device_deep_sleep.h")
    deviceDeepSleepHeaderFile.setDestPath('')
    deviceDeepSleepHeaderFile.setProjectPath('config/' + configName)
    deviceDeepSleepHeaderFile.setType("HEADER")
    deviceDeepSleepHeaderFile.setMarkup(True)
    #setEnabled is controlled in handleDeepSleepEnable
    deviceDeepSleepHeaderFile.setEnabled(False)

    # Add device_deep_sleep.c
    global deviceDeepSleepSourceFile
    deviceDeepSleepSourceFile = libBTZBCore.createFileSymbol("DEVICE_DEEP_SLEEP_C", None)

    deviceDeepSleepSourceFile.setSourcePath("driver/pic32cx-bz/templates/low_power/device_deep_sleep.ftl")
    deviceDeepSleepSourceFile.setOutputName("device_deep_sleep.c")
    deviceDeepSleepSourceFile.setDestPath('')
    deviceDeepSleepSourceFile.setProjectPath('config/' + configName)
    deviceDeepSleepSourceFile.setType("SOURCE")
    deviceDeepSleepSourceFile.setMarkup(True)
    #setEnabled is controlled in handleDeepSleepEnable
    deviceDeepSleepSourceFile.setEnabled(False)


    # Add device_sleep.h
    global deviceSleepHeaderFile
    deviceSleepHeaderFile = libBTZBCore.createFileSymbol("DEVICE_SLEEP_H", None)
    if (deviceName in pic32cx_bz2_family):
        deviceSleepHeaderFile.setSourcePath("driver/pic32cx-bz/src/src_bz2/app_fw/device_sleep.h")
    elif (deviceName in pic32cx_bz3_family):
        deviceSleepHeaderFile.setSourcePath("driver/pic32cx-bz/src/src_bz3/app_fw/device_sleep.h")
    deviceSleepHeaderFile.setOutputName("device_sleep.h")
    deviceSleepHeaderFile.setDestPath('')
    deviceSleepHeaderFile.setProjectPath('config/' + configName)
    deviceSleepHeaderFile.setType("HEADER")
    deviceSleepHeaderFile.setMarkup(True)
    #setEnabled is controlled in handleRTC_Support
    deviceSleepHeaderFile.setEnabled(False)

    # Add device_sleep.c
    global deviceSleepSourceFile
    deviceSleepSourceFile = libBTZBCore.createFileSymbol("DEVICE_SLEEP_C", None)
    if (deviceName in pic32cx_bz2_family):
        deviceSleepSourceFile.setSourcePath("driver/pic32cx-bz/templates/low_power/device_sleep_bz2.ftl")
    elif (deviceName in pic32cx_bz3_family):
        deviceSleepSourceFile.setSourcePath("driver/pic32cx-bz/templates/low_power/device_sleep_bz3.ftl")
    deviceSleepSourceFile.setOutputName("device_sleep.c")
    deviceSleepSourceFile.setDestPath('')
    deviceSleepSourceFile.setProjectPath('config/' + configName)
    deviceSleepSourceFile.setType("SOURCE")
    deviceSleepSourceFile.setMarkup(True)
    #setEnabled is controlled in handleRTC_Support
    deviceSleepSourceFile.setEnabled(False)

    ############################################################################
    ### Add ROM API Security Headers if BZ3 family is used
    ############################################################################
    if (deviceName in pic32cx_bz3_family):
        rom_apiAPIHeaders = [
            ('api_table.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/', 'driver/security/'),

            ('adapter_api.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/silexpk/', 'driver/security/silexpk/'),
            ('cmddefs_api.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/silexpk/', 'driversecurity/silexpk/'),
            ('core_api.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/silexpk/', 'driver/security/silexpk/'),
            ('dsa_api.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/silexpk/', 'driver/security/silexpk/'),
            ('ec_curves_api.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/silexpk/', 'driver/security/silexpk/'),
            ('eccweierstrass_api.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/silexpk/', 'driver/security/silexpk/'),
            ('ecjpake.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/silexpk/', 'driver/security/silexpk/'),
            ('ed448_api.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/silexpk/', 'driver/security/silexpk/'),
            ('ed25519_api.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/silexpk/', 'driver/security/silexpk/'),
            ('impl.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/silexpk/', 'driver/security/silexpk/'),
            ('inputslots.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/silexpk/', 'driver/security/silexpk/'),
            ('internal.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/silexpk/', 'driver/security/silexpk/'),
            ('iomem.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/silexpk/', 'driver/security/silexpk/'),
            ('montgomery_api.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/silexpk/', 'driver/security/silexpk/'),
            ('rsa.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/silexpk/', 'driver/security/silexpk/'),
            ('statuscodes_api.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/silexpk/', 'driver/security/silexpk/'),
            ('sxbufop.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/silexpk/', 'driver/security/silexpk/'),
            ('version.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/silexpk/', 'driver/security/silexpk/'),

            ('aead_api.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/sxsymcrypt/', 'driver/security/sxsymcrypt/'),
            ('blkcipher_api.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/sxsymcrypt/', 'driver/security/sxsymcrypt/'),
            ('cmac_api.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/sxsymcrypt/', 'driver/security/sxsymcrypt/'),
            ('cmmask_api.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/sxsymcrypt/', 'driver/security/sxsymcrypt/'),
            ('hash_api.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/sxsymcrypt/', 'driver/security/sxsymcrypt/'),
            ('hmac_api.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/sxsymcrypt/', 'driver/security/sxsymcrypt/'),
            ('internal.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/sxsymcrypt/', 'driver/security/sxsymcrypt/'),
            ('interrupts_api.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/sxsymcrypt/', 'driver/security/sxsymcrypt/'),
            ('keyref_api.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/sxsymcrypt/', 'driver/security/sxsymcrypt/'),
            ('mac_api.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/sxsymcrypt/', 'driver/security/sxsymcrypt/'),
            ('sha1_api.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/sxsymcrypt/', 'driver/security/sxsymcrypt/'),
            ('sha2_api.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/sxsymcrypt/', 'driver/security/sxsymcrypt/'),
            ('sm3_api.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/sxsymcrypt/', 'driver/security/sxsymcrypt/'),
            ('statuscodes.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/sxsymcrypt/', 'driver/security/sxsymcrypt/'),
            ('trng_api.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/sxsymcrypt/', 'driver/security/sxsymcrypt/'),
            ('trnginternal.h', 'driver/pic32cx-bz/src/src_bz3/rom_api/sxsymcrypt/', 'driver/security/sxsymcrypt/'),
            ]

        for incFile, srcPath,dstPath in rom_apiAPIHeaders:
            incFileSym = libBTZBCore.createFileSymbol(None, None)
            incFileSym.setSourcePath(srcPath + incFile)
            incFileSym.setOutputName(incFile)
            incFileSym.setOverwrite(True)
            incFileSym.setDestPath(dstPath)
            incFileSym.setProjectPath('config/' + configName + '/' + dstPath)
            incFileSym.setType('HEADER')
            incFileSym.setEnabled(True)

    ############################################################################
    ### Add logic for adding BLE stack to app.c
    ############################################################################
    # This boolean is controlled configAppIdleTask called by:
    #   onAttachmentConnected or onAttachmentDisconnected
    bleStackLoaded = libBTZBCore.createBooleanSymbol('BLESTACK_LOADED', None)
    bleStackLoaded.setDefaultValue('BLE_STACK_LIB' in activeComponents)
    bleStackLoaded.setVisible(False)


    ############################################################################
    ### Add logic for adding Zigbee stack to app.c
    ############################################################################
    # This boolean is controlled configAppIdleTask called by:
    #   onAttachmentConnected or onAttachmentDisconnected
    zigbeeStackLoaded = libBTZBCore.createBooleanSymbol('ZIGBEESTACK_LOADED', None)
    zigbeeStackLoaded.setDefaultValue(['ZIGBEE_COLOR_SCENE_CONTROLLER' or 'ZIGBEE_MULTI_SENSOR' or 'ZIGBEE_COMBINED_INTERFACE' or 
                                      'ZIGBEE_THERMOSTAT' or 'ZIGBEE_IAS_ACE' or 'ZIGBEE_ON_OFF_LIGHT' or 'ZIGBEE_DIMMABLE_LIGHT' or 
                                      'ZIGBEE_COLOR_LIGHT' or 'ZIGBEE_EXTENDED_COLOR_LIGHT' or 'ZIGBEE_TEMPERATURE_COLOR_LIGHT' or 
                                      'ZIGBEE_CUSTOM' or 'ZIGBEE_MACWSNTESTER' or 'ZIGBEE_GPD_SENSOR' or 'ZIGBEE_ZAPPSI'] in activeComponents)
    zigbeeStackLoaded.setVisible(False)
    
    ############################################################################
    ### Add logic for adding Thread stack to app.c
    ############################################################################
    # This boolean is controlled configAppIdleTask called by:
    #   onAttachmentConnected or onAttachmentDisconnected
    threadStackLoaded = libBTZBCore.createBooleanSymbol('THREADSTACK_LOADED', None)
    threadStackLoaded.setDefaultValue('OPEN_THREAD' in activeComponents)
    threadStackLoaded.setVisible(False)

    ############################################################################
    ### Add logic for adding PHY to app.c
    ############################################################################
    # This boolean is controlled configAppIdleTask called by:
    #   onAttachmentConnected or onAttachmentDisconnected
    phyLoaded = libBTZBCore.createBooleanSymbol('802154_PHY_LOADED', None)
    phyLoaded.setDefaultValue('IEEE_802154_PHY' in activeComponents)
    phyLoaded.setVisible(False)

    ############################################################################
    ### Add logic for setting wssEnable_t mode
    ############################################################################
    # This string is controlled by configWSSEnable called by:
    #   onAttachmentConnected or onAttachmentDisconnected
    wssEnableMode = libBTZBCore.createStringSymbol('WSS_ENABLE_MODE', None)
    wssEnableMode.setValue('WSS_ENABLE_NONE')
    wssEnableMode.setVisible(False)


    ############################################################################
    ### Add logic for boolean for PDS loaded
    ############################################################################
    # This boolean is controlled configAppIdleTask called by:
    #   onAttachmentConnected or onAttachmentDisconnected
    pdsSystemLoaded = libBTZBCore.createBooleanSymbol('PDS_LOADED', None)
    pdsSystemLoaded.setDefaultValue('pdsSystem' in activeComponents)
    pdsSystemLoaded.setVisible(False)


    ############################################################################
    ### Add logic for adding Zigbee/Thread stack to app.c
    ############################################################################
    global uartEnable
    uartEnable = libBTZBCore.createBooleanSymbol("ENABLE_CONSOLE", None)
    uartEnable.setLabel("Enable Console")
    uartEnable.setDefaultValue(False)
    uartEnable.setVisible(False)
    uartEnable.setDependencies(isConsoleUartEnabled, ["ZIGBEE_COLOR_SCENE_CONTROLLER:APP_ENABLE_CONSOLE", "ZIGBEE_MULTI_SENSOR:APP_ENABLE_CONSOLE", "ZIGBEE_COMBINED_INTERFACE:APP_ENABLE_CONSOLE", "ZIGBEE_THERMOSTAT:APP_ENABLE_CONSOLE",
                                                   "ZIGBEE_IAS_ACE:APP_ENABLE_CONSOLE", "ZIGBEE_ON_OFF_LIGHT:APP_ENABLE_CONSOLE", "ZIGBEE_DIMMABLE_LIGHT:APP_ENABLE_CONSOLE", "ZIGBEE_COLOR_LIGHT:APP_ENABLE_CONSOLE",
                                                   "ZIGBEE_EXTENDED_COLOR_LIGHT:APP_ENABLE_CONSOLE","ZIGBEE_TEMPERATURE_COLOR_LIGHT:APP_ENABLE_CONSOLE","ZIGBEE_CUSTOM:APP_ENABLE_CONSOLE","ZIGBEE_RUNNER:APP_ENABLE_CONSOLE","OPEN_THREAD:OPEN_THREAD_UART_SERVICE"])

    ############################################################################
    ### Add idle task configuration items
    ############################################################################
    idleTaskMenu = libBTZBCore.createMenuSymbol('IDLE_TASK_MENU', None)
    idleTaskMenu.setLabel('App Idle Task')
    idleTaskMenu.setDescription('App Idle Task Configuration')
    idleTaskMenu.setVisible(True)

    idleTaskCal = libBTZBCore.createBooleanSymbol('IDLE_TASK_CAL', idleTaskMenu)
    idleTaskCal.setLabel('Include RF cal in Idle Task')
    idleTaskCal.setDefaultValue(True)


    ############################################################################
    ### Add PDS_SubSystem auto activation
    ############################################################################
    pdsAutoLoadBool = libBTZBCore.createBooleanSymbol('AUTO_LOAD_PDS', None)
    pdsAutoLoadBool.setLabel('Auto load PDS_SubSystem')
    pdsAutoLoadBool.setValue(True)
    # initial call for pdsLoadUnload()
    processPDSLoadUnload(libBTZBCore, {"value": pdsAutoLoadBool.getValue()})

    pdsLoadAction = libBTZBCore.createBooleanSymbol('LOAD_PDS_ACTION', None)
    pdsLoadAction.setVisible(False)
    pdsLoadAction.setDependencies(pdsLoadUnload, ["AUTO_LOAD_PDS"])

    ############################################################################
    ### Add logic for adding Deep Sleep to app.c
    ############################################################################
    global deepSleepEnable
    deepSleepEnable = libBTZBCore.createBooleanSymbol("ENABLE_DEEP_SLEEP", None)
    deepSleepEnable.setLabel("Enable Deep Sleep (Retention RAM)")
    deepSleepEnable.setDefaultValue(getBLEStackLibDsadven())
    deepSleepEnable.setVisible(True)
    deepSleepEnable.setDependencies(enableRetentionRAMSetting, ["BLE_STACK_LIB:GAP_DSADV_EN", "ENABLE_DEEP_SLEEP"])

    ############################################################################
    ### Add logic for retention RAM menu item - Stack Requirements
    ############################################################################
    global stackRetentionRAM
    stackRetentionRAM = libBTZBCore.createIntegerSymbol('STACK_RETENTION_RAM', deepSleepEnable)
    stackRetentionRAM.setLabel("Stack Retention RAM Size (bytes)")
    stackRetentionRAM.setVisible(getDeepSleepState())
    stackRetentionRAM.setDefaultValue(computeRetentionRAMRequirements())
    stackRetentionRAM.setDependencies(enableStackRetentionRAM, ["ENABLE_DEEP_SLEEP"])

    ############################################################################
    ### Add logic for retention RAM menu item - App Requirements
    ############################################################################
    global appRetentionRAM
    appRetentionRAM = libBTZBCore.createIntegerSymbol('APP_RETENTION_RAM', deepSleepEnable)
    appRetentionRAM.setLabel("Application Retention RAM Size (bytes)")
    appRetentionRAM.setVisible(getDeepSleepState())
    appRetentionRAM.setDefaultValue(0)
    appRetentionRAM.setMin(0) 
    appRetentionRAM.setMax(computeMaxAppRetentionRAM())
    appRetentionRAM.setDependencies(enableAppRetentionRAM, ["STACK_RETENTION_RAM"])

    ############################################################################
    ### Add logic for retention RAM option
    ############################################################################
    global totalRetentionRAM
    totalRetentionRAM = libBTZBCore.createBooleanSymbol('TOTAL_RETENTION_RAM', deepSleepEnable)
    totalRetentionRAM.setVisible(False)
    totalRetentionRAM.setDefaultValue(False)
    totalRetentionRAM.setDependencies(enable32KRetentionRAM, ["APP_RETENTION_RAM", "STACK_RETENTION_RAM"])

    ############################################################################
    ### Add logic for retention RAM option
    ############################################################################
    global totalRetentionRAMBytes
    totalRetentionRAMBytes = libBTZBCore.createIntegerSymbol('TOTAL_RETENTION_RAM_BYTES', deepSleepEnable)
    totalRetentionRAMBytes.setVisible(False)
    totalRetentionRAMBytes.setDefaultValue(0)

    ############################################################################
    ### Add Custom Antenna Region
    ############################################################################
    #customAntennaRegion = libBTZBCore.createComboSymbol('CUSTOM_ANT_REGION', None, ['ETSI', 'FCC', 'ETSI_FCC'])
    customAntennaRegion = libBTZBCore.createMenuSymbol('CUSTOM_ANT_REGION', None)
    customAntennaRegion.setLabel('Regulatory Region')
    customAntennaRegion.setVisible(True)
    
    ############################################################################
    ### Add logic for adding ResetToFN in device_deep_sleep.c
    ############################################################################
    global resetToFNEnable
    resetToFNEnable = libBTZBCore.createBooleanSymbol("ENABLE_RESET_TO_FN", None)
    resetToFNEnable.setDefaultValue(False)
    resetToFNEnable.setVisible(False)

    #ETSI/UK
    etsiAntennaRegion = libBTZBCore.createBooleanSymbol("ETSI_REGION", customAntennaRegion)
    etsiAntennaRegion.setLabel("ETSI/UK")
    etsiAntennaRegion.setDefaultValue(True)
    etsiAntennaRegion.setVisible(True)
    etsiAntennaRegion.setReadOnly(False)

    #FCC/IC
    fccAntennaRegion = libBTZBCore.createBooleanSymbol("FCC_REGION", customAntennaRegion)
    fccAntennaRegion.setLabel("FCC/IC")
    fccAntennaRegion.setDefaultValue(False)
    fccAntennaRegion.setVisible(True)
    fccAntennaRegion.setReadOnly(False)

    #JAPAN
    japanAntennaRegion = libBTZBCore.createBooleanSymbol("JAPAN_REGION", customAntennaRegion)
    japanAntennaRegion.setLabel("JAPAN")
    japanAntennaRegion.setDefaultValue(False)
    japanAntennaRegion.setVisible(True)
    japanAntennaRegion.setReadOnly(False)

    #KOREA
    koreaAntennaRegion = libBTZBCore.createBooleanSymbol("KOREA_REGION", customAntennaRegion)
    koreaAntennaRegion.setLabel("KOREA")
    koreaAntennaRegion.setDefaultValue(False)
    koreaAntennaRegion.setVisible(True)
    koreaAntennaRegion.setReadOnly(False)

    #CHINA
    chinaAntennaRegion = libBTZBCore.createBooleanSymbol("CHINA_REGION", customAntennaRegion)
    chinaAntennaRegion.setLabel("CHINA")
    chinaAntennaRegion.setDefaultValue(False)
    chinaAntennaRegion.setVisible(True)
    chinaAntennaRegion.setReadOnly(False)

    #TAIWAN
    taiwanAntennaRegion = libBTZBCore.createBooleanSymbol("TAIWAN_REGION", customAntennaRegion)
    taiwanAntennaRegion.setLabel("TAIWAN")
    taiwanAntennaRegion.setDefaultValue(False)
    taiwanAntennaRegion.setVisible(True)
    taiwanAntennaRegion.setReadOnly(False)

    ############################################################################
    ### Add Custom Antenna Gain Enable
    ############################################################################
    customAntennaGainEnable = libBTZBCore.createBooleanSymbol('CUSTOM_ANT_ENABLE', None)
    customAntennaGainEnable.setLabel('Enable Custom Antenna Gain')
    customAntennaGainEnable.setValue(False)
    customAntennaGainEnable.setDependencies(antGainChanged, ["CUSTOM_ANT_GAIN", "ETSI_REGION", "FCC_REGION", "JAPAN_REGION", "KOREA_REGION", "CHINA_REGION", "TAIWAN_REGION"])


    ############################################################################
    ### Add Custom Antenna Gain
    ############################################################################
    customAntennaGain = libBTZBCore.createIntegerSymbol('CUSTOM_ANT_GAIN', customAntennaGainEnable)
    customAntennaGain.setLabel('Custom Antenna Gain (dBm)')
    if( deviceName == 'WBZ450' ):
        customAntennaGain.setDefaultValue(5)
    else:
        customAntennaGain.setDefaultValue(3)

    customAntennaGain.setMin(-5)
    customAntennaGain.setMax(6)
    customAntennaGain.setVisible(False)
    customAntennaGain.setDependencies(antGainEnable, ["CUSTOM_ANT_ENABLE"])


    ############################################################################
    ### Add PCHE_REG values
    ############################################################################
    prefenInt = libBTZBCore.createIntegerSymbol("DEVICE_CHECON_PREFEN", None)
    prefenInt.setReadOnly(True)
    prefenInt.setLabel("Predictive Prefetch Configuration")
    prefenInt.setDefaultValue(getCorePREFEN())
    prefenInt.setDependencies(updatePREFEN, ["core.CONFIG_CHECON_PREFEN"])
    prefenInt.setVisible(False)

    pfmwsInt = libBTZBCore.createIntegerSymbol("DEVICE_CHECON_PFMWS", None)
    pfmwsInt.setReadOnly(True)
    pfmwsInt.setLabel("Program Flash memory Wait states")
    pfmwsInt.setDefaultValue(getCorePFMWS())
    pfmwsInt.setDependencies(updatePFMWS, ["core.CONFIG_CHECON_PFMWS"])
    pfmwsInt.setVisible(False)


    ############################################################################
    ### Add Sleep support for radio stacks
    ############################################################################
    sleepSupportEnable = libBTZBCore.createBooleanSymbol("SLEEP_SUPPORTED", None)
    sleepSupportEnable.setReadOnly(True)
    sleepSupportEnable.setLabel("Sleep support required by radio stack")
    # This value is controlled by handleRTC_Support():
    sleepSupportEnable.setDefaultValue(False)
    sleepSupportEnable.setVisible(False)


    ############################################################################
    ### Configure XC32 compiler settings
    ############################################################################
    c32TentativeDefinitions = libBTZBCore.createSettingSymbol('C32_TENTATIVE_DEFINITIONS', None) 
    c32TentativeDefinitions.setCategory('C32')
    c32TentativeDefinitions.setKey('tentative-definitions')
    c32TentativeDefinitions.setValue('-fcommon')

    ############################################################################
    ### Enable PMU Mode
    ############################################################################
    pmuModeSettingEnable = libBTZBCore.createBooleanSymbol("SYSTEM_ENABLE_PMUMODE_SETTING", None)
    pmuModeSettingEnable.setLabel("Enable PMU Mode Setting")
    pmuModeSettingEnable.setDefaultValue(False)
    pmuModeSettingEnable.setVisible(True)

    ############################################################################
    ### Configure PMU Mode
    ############################################################################    
    pmuModeSelection = libBTZBCore.createComboSymbol('SYSTEM_PMU_MODE', pmuModeSettingEnable, ['PMU_MODE_MLDO', 'PMU_MODE_BUCK_PWM', 'PMU_MODE_BUCK_PSM'])
    pmuModeSelection.setLabel('PMU Mode')
    pmuModeSelection.setDefaultValue('PMU_MODE_BUCK_PWM')
    pmuModeSelection.setVisible((pmuModeSettingEnable.getValue() == True))
    pmuModeSelection.setDependencies(enablePMUModeSettingOption, ["SYSTEM_ENABLE_PMUMODE_SETTING"])

    ############################################################################
    ### PIC32CX-BZ2 family Identification symbol
    ############################################################################
    # This boolean identifies the device is PIC32CX-BZ2 family device
    pic32cxbzDevice = libBTZBCore.createBooleanSymbol('PIC32CX_BZ2_DEVICE', None)
    pic32cxbzDevice.setDefaultValue(deviceName in pic32cx_bz2_family)
    pic32cxbzDevice.setVisible(False)

    # This boolean identifies the device is PIC32CX-BZ2 48 or 32 pin device
    pic32cxbzPinDevice = libBTZBCore.createBooleanSymbol('PIC32CX_BZ2_48PIN_DEVICE', None)
    pic32cxbzPinDevice.setDefaultValue(deviceName in pic32cx_bz2_48pin_family)
    pic32cxbzPinDevice.setVisible(False)

    ############################################################################
    ### PIC32CX-BZ3 family Identification symbol
    ############################################################################
    # This boolean identifies the device is PIC32CX-BZ3 family device
    pic32cxbznDevice = libBTZBCore.createBooleanSymbol('PIC32CX_BZ3_DEVICE', None)
    pic32cxbznDevice.setDefaultValue(deviceName in pic32cx_bz3_family)
    pic32cxbznDevice.setVisible(False)

    # This boolean identifies the device is PIC32CX-BZ2 48 or 32 pin device
    pic32cxbznPinDevice = libBTZBCore.createBooleanSymbol('PIC32CX_BZ3_48PIN_DEVICE', None)
    pic32cxbznPinDevice.setDefaultValue(deviceName in pic32cx_bz3_48pin_family)
    pic32cxbznPinDevice.setVisible(False)

def finalizeComponent(libBTZBCore):
    print('Finalizing: libBTZBCore')

    # Enable "Enable OSAL" option in MHC
    print("Enabling 'Enable OSCAL'")
    Database.sendMessage("HarmonyCore", "ENABLE_OSAL", {"isEnabled":True})

    # Enable "Enable FREERTOS_USE_QUEUE_SETS" option in MHC
    useQueueSets = Database.getSymbolValue("FreeRTOS", "FREERTOS_USE_QUEUE_SETS")
    print('useQueueSets = {}'.format(str(useQueueSets)))
    if (useQueueSets == False):
        Database.setSymbolValue("FreeRTOS", "FREERTOS_USE_QUEUE_SETS", True)

    print("Enabling 'Generate Harmony Application Files'")
    Database.sendMessage("HarmonyCore", "ENABLE_DRV_COMMON", {"isEnabled":True})
    Database.sendMessage("HarmonyCore", "ENABLE_SYS_COMMON", {"isEnabled":True})

    print("Setting 'Minimal Stack Size' to 256")
    Database.setSymbolValue("FreeRTOS", "FREERTOS_MINIMAL_STACK_SIZE", 256)
    
    Database.setSymbolValue("FreeRTOS", "FREERTOS_INCLUDE_XTASKABORTDELAY", True)

    print("Setting 'Memory Management Type' to 'Heap_4'")
    remoteComponent = Database.getComponentByID("FreeRTOS")
    if (remoteComponent):
        memoryManagementChoice = remoteComponent.getSymbolByID("FREERTOS_MEMORY_MANAGEMENT_CHOICE")
        memoryManagementChoice.setValue('Heap_4')
        
def destroyComponent(libBTZBCore):
    Database.sendMessage("HarmonyCore", "ENABLE_DRV_COMMON", {"isEnabled":False})
    Database.sendMessage("HarmonyCore", "ENABLE_SYS_COMMON", {"isEnabled":False})
    
def onAttachmentConnected(source, target):
    targetID = target["component"].getID()
    sourceID = source["component"].getID()
    Log.writeInfoMessage('device_support:onAttachmentConnected: source = {} remote = {}'.
            format(sourceID, targetID))

    configWSSEnable(source["component"], targetID, True)

    if targetID in REQUIRES_APP_IDLE_TASK.keys():
        configAppIdleTask(source["component"], targetID, True)

    # send initial Custom Antenna values to clients
    if targetID in RADIOSTACK_COMPONENTS:
        # Log.writeInfoMessage('device_support:onAttachmentConnected: CUSTOM_ANT_ENABLE symbol: {}'.format(source["component"].getSymbolByID("CUSTOM_ANT_ENABLE").getID()))
        sendAntMessage('CUSTOM_ANT_ENABLE', source["component"].getSymbolByID("CUSTOM_ANT_ENABLE").getValue())
        sendAntMessage('CUSTOM_ANT_GAIN', source["component"].getSymbolByID("CUSTOM_ANT_GAIN").getValue())
        sendAntMessage('ETSI_REGION', source["component"].getSymbolByID("ETSI_REGION").getValue())
        sendAntMessage('FCC_REGION', source["component"].getSymbolByID("FCC_REGION").getValue())
        sendAntMessage('JAPAN_REGION', source["component"].getSymbolByID("JAPAN_REGION").getValue())
        sendAntMessage('KOREA_REGION', source["component"].getSymbolByID("KOREA_REGION").getValue())
        sendAntMessage('CHINA_REGION', source["component"].getSymbolByID("CHINA_REGION").getValue())
        sendAntMessage('TAIWAN_REGION', source["component"].getSymbolByID("TAIWAN_REGION").getValue())



    if targetID == 'rtc':
        Database.setSymbolValue("rtc", "RTC_MODE0_INTENSET_CMP0_ENABLE", True)
        Database.setSymbolValue("rtc", "RTC_MODE0_EVCTRL_CMPEO0_ENABLE", True)

    if targetID == 'FreeRTOS':
        Database.setSymbolValue(targetID, "FREERTOS_TICKLESS_IDLE_CHOICE", "Tickless_Idle")
        Database.setSymbolValue(targetID, "FREERTOS_EXPECTED_IDLE_TIME_BEFORE_SLEEP", 5)
        Database.setSymbolValue(targetID, "FREERTOS_TICK_HOOK", True)

def onAttachmentDisconnected(source, target):
    targetID = target["component"].getID()
    sourceID = source["component"].getID()
    Log.writeInfoMessage('device_support:onAttachmentDisconnected: source = {} remote = {}'.
            format(sourceID, targetID))

    configWSSEnable(source["component"], targetID, False)

    if targetID in REQUIRES_APP_IDLE_TASK.keys():
        configAppIdleTask(source["component"], targetID, False)

    # on disconnect it can be assumed that the RTC requirement is no longer needed
    if targetID in REQUIRES_RTC_SUPPORT.keys():
        handleRTC_Support({'source': targetID, 'target': sourceID, 'rtcRequired': False})


def isConsoleUartEnabled(symbol, event):
    if ((event["value"] == True)):
        symbol.setValue(True)
        print("isConsoleUartEnabled setting True")
    else:
        symbol.setValue(False)
        print("isConsoleUartEnabled setting False")

def handleRTC_Support(args):
    Log.writeInfoMessage('device_support:handleRTC_Support')
    for arg in args:
        Log.writeInfoMessage("    arg['{:>12}'] = '{}'".format(arg, str(args[arg])))

    # Update REQUIRES_RTC_SUPPORT dictionary with the new value
    rtcRequested = args['rtcRequired']
    REQUIRES_RTC_SUPPORT[args['source']] = rtcRequested

    # locate the SLEEP_SUPPORTED symbols in the Database
    localComponent = Database.getComponentByID(args['target'])
    if (localComponent):
        localComponentID = localComponent.getID()
        rtcRequiredSymbol = (localComponent.getSymbolByID('SLEEP_SUPPORTED') or localComponent.getSymbolByID('ENABLE_DEEP_SLEEP'))

    Log.writeInfoMessage('device_support:handleRTC_Support target ID = {}'.format(localComponentID))

    # if any entries in REQUIRES_RTC_SUPPORT are True then rtcRequired is True
    rtcRequired = not all(required==False for required in REQUIRES_RTC_SUPPORT.values())
    rtcRequiredSymbol.setValue(rtcRequired)

    global deviceSleepHeaderFile
    global deviceSleepSourceFile

    # if any entries in REQUIRES_RTC_SUPPORT are True load the RTC
    if rtcRequired:
        activateRTC = Database.activateComponents(["rtc"])
        connectRTC = Database.connectDependencies([[localComponentID, 'RTC_Module', 'rtc', 'RTC_TMR']])
        deviceSleepHeaderFile.setEnabled(True)
        deviceSleepSourceFile.setEnabled(True)

    elif "rtc" in Database.getActiveComponentIDs():
        deactivateRTC = Database.deactivateComponents(["rtc"])
        deviceSleepHeaderFile.setEnabled(False)
        deviceSleepSourceFile.setEnabled(False)


# Dependency callback called upon PMU Mode Setting is enabled
def enablePMUModeSettingOption(symbol, event):
    symbol.setVisible(event["value"])

def handleDeepSleepEnable(args):
    deepSleepEnable.setValue(args["isEnabled"])
    global deviceDeepSleepHeaderFile
    global deviceDeepSleepSourceFile
    if (args["isEnabled"] == True):
        deviceDeepSleepHeaderFile.setEnabled(True)
        deviceDeepSleepSourceFile.setEnabled(True)
        deepSleepEnable.setReadOnly(True)
        print("handleDeepSleepEnable setting True")
    else:
        deviceDeepSleepHeaderFile.setEnabled(False)
        deviceDeepSleepSourceFile.setEnabled(False)
        deepSleepEnable.setReadOnly(False)
        print("handleDeepSleepEnable setting False")

def enableRetentionRAMSetting(symbol, event):
    if ((event["value"] == True)):
        deepSleepEnable.setValue(True)
        if(event["source"] == "BLE_STACK_LIB:GAP_DSAVD_EN"):
            print("GAP_DSADV_EN enabled")
        else:
            print("enable deep sleep setting enabled")
            if (deviceName in pic32cx_bz2_family):
                handleRTC_Support({"target": "pic32cx_bz2_devsupport", "source": "pic32cx_bz2_devsupport", "rtcRequired": True})
                deviceDeepSleepHeaderFile.setEnabled(True)
                deviceDeepSleepSourceFile.setEnabled(True)
            elif (deviceName in pic32cx_bz3_family):
                handleRTC_Support({"target": "pic32cx_bz3_devsupport", "source": "pic32cx_bz3_devsupport", "rtcRequired": True})
                deviceDeepSleepHeaderFile.setEnabled(True)
                deviceDeepSleepSourceFile.setEnabled(True)
    else:
        deepSleepEnable.setValue(False)
        if(event["source"] == "BLE_STACK_LIB:GAP_DSAVD_EN"):
            print("GAP_DSADV_EN disabled")
        else:
            print("enable deep sleep setting disabled")
            if (deviceName in pic32cx_bz2_family):
                handleRTC_Support({"target": "pic32cx_bz2_devsupport", "source": "pic32cx_bz2_devsupport", "rtcRequired": False})
                deviceDeepSleepHeaderFile.setEnabled(False)
                deviceDeepSleepSourceFile.setEnabled(False)
            elif (deviceName in pic32cx_bz3_family):
                handleRTC_Support({"target": "pic32cx_bz3_devsupport", "source": "pic32cx_bz3_devsupport", "rtcRequired": False})
                deviceDeepSleepHeaderFile.setEnabled(False)
                deviceDeepSleepSourceFile.setEnabled(False)

def enableStackRetentionRAM(symbol, event):
    if(getDeepSleepState() and (deviceName in pic32cx_bz3_family)):
        stackRetentionRAM.setValue(computeRetentionRAMRequirements())
        stackRetentionRAM.setVisible(True)
        stackRetentionRAM.setReadOnly(True)
    else:
        stackRetentionRAM.setVisible(False)
        stackRetentionRAM.setReadOnly(False)

def enableAppRetentionRAM(symbol, event):
    if(getDeepSleepState() and (deviceName in pic32cx_bz3_family)):
        appRetentionRAM.setMax(computeMaxAppRetentionRAM())
        appRetentionRAM.setVisible(True)
    else:
        appRetentionRAM.setVisible(False)

def enable32KRetentionRAM(symbol, event):
    if(deviceName in pic32cx_bz3_family):
        appvalue = int(Database.getSymbolValue("pic32cx_bz3_devsupport", "APP_RETENTION_RAM"))
        configureRetentionRAM = int(appvalue + int(stackRetentionRAM.getValue()))
        totalRetentionRAMBytes.setValue(configureRetentionRAM)
        if((configureRetentionRAM > 16384) and (configureRetentionRAM < 32768)):
            totalRetentionRAM.setValue(True)
        else:
            totalRetentionRAM.setValue(False)


def handleMessage(messageID, args):
    '''
    message formats
        CONSOLE_ENABLE: specifies if drv_zigbee_lib.py requires UART
            payload:    {
                        'isEnabled': True/False
                        }
        RTC_SUPPORT:    specifies if RTC support is requred
            payload:    {
                        'target':       <this module>
                        'source':       <module name>,
                        'rtcRequired:   True/False,
                        }
    '''
    Log.writeInfoMessage("device_support:handleMessage ID='{}'".format(messageID))
    if (messageID == "CONSOLE_ENABLE"):
        uartEnable.setValue(args["isEnabled"])
    elif (messageID == "RTC_SUPPORT"):
        # for arg in args:
        #     Log.writeInfoMessage("    arg['{:>12}'] = '{}'".format(arg, args[arg]))
        handleRTC_Support(args)
    elif (messageID == "DEEP_SLEEP_ENABLE"):
        handleDeepSleepEnable(args)

