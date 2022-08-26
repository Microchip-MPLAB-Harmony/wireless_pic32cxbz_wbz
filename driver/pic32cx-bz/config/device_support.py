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

pic32cx_bz3_family = {'PIC32CX5109BZ31048',
                      'PIC32CX5109BZ31032',
                      'WBZ435',
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
        'ZIGBEE_ZAPPSI': 'ZIGBEESTACK_LOADED'}


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
        sys_service_a.setSourcePath('driver/pic32cx-bz/src/pic32cx_bz2_device_support.a')
        sys_service_a.setOutputName('pic32cx_bz2_device_support.a')
    elif (deviceName in pic32cx_bz3_family):
        sys_service_a.setSourcePath('driver/pic32cx-bz/src/pic32cx_bz3_device_support.a')
        sys_service_a.setOutputName('pic32cx_bz3_device_support.a')


    ############################################################################
    ### Add pic32cx-bz static header files
    ############################################################################

    # Add rf_system.h file
    rfSysInitializeHeaderFile = libBTZBCore.createFileSymbol(None, None)
    rfSysInitializeHeaderFile.setSourcePath('driver/pic32cx-bz/src/rf_system.h')
    rfSysInitializeHeaderFile.setOutputName('rf_system.h')
    rfSysInitializeHeaderFile.setOverwrite(True)
    rfSysInitializeHeaderFile.setDestPath('driver/device_support/include')
    rfSysInitializeHeaderFile.setProjectPath('config/' + configName + '/driver/device_support/include/')
    rfSysInitializeHeaderFile.setType('HEADER')
    rfSysInitializeHeaderFile.setEnabled(True)

    # Add pmu_system.h file
    pmuSystemHeaderFile = libBTZBCore.createFileSymbol(None, None)
    pmuSystemHeaderFile.setSourcePath('driver/pic32cx-bz/src/pmu_system.h')
    pmuSystemHeaderFile.setOutputName('pmu_system.h')
    pmuSystemHeaderFile.setOverwrite(True)
    pmuSystemHeaderFile.setDestPath('driver/device_support/include')
    pmuSystemHeaderFile.setProjectPath('config/' + configName + '/driver/device_support/include/')
    pmuSystemHeaderFile.setType('HEADER')
    pmuSystemHeaderFile.setEnabled(True)
    
    # Add info_block.h file
    infoBlockHeaderFile = libBTZBCore.createFileSymbol(None, None)
    infoBlockHeaderFile.setSourcePath('driver/pic32cx-bz/src/info_block.h')
    infoBlockHeaderFile.setOutputName('info_block.h')
    infoBlockHeaderFile.setOverwrite(True)
    infoBlockHeaderFile.setDestPath('driver/device_support/include')
    infoBlockHeaderFile.setProjectPath('config/' + configName + '/driver/device_support/include/')
    infoBlockHeaderFile.setType('HEADER')
    infoBlockHeaderFile.setEnabled(True)
    
    # Add sleep_system.h file
    sleepSystemHeaderFile = libBTZBCore.createFileSymbol(None, None)
    sleepSystemHeaderFile.setSourcePath('driver/pic32cx-bz/src/sleep_system.h')
    sleepSystemHeaderFile.setOutputName('sleep_system.h')
    sleepSystemHeaderFile.setOverwrite(True)
    sleepSystemHeaderFile.setDestPath('driver/device_support/include')
    sleepSystemHeaderFile.setProjectPath('config/' + configName + '/driver/device_support/include/')
    sleepSystemHeaderFile.setType('HEADER')
    sleepSystemHeaderFile.setEnabled(True)
    
    # Add framework_defs.h
    HeaderFile = libBTZBCore.createFileSymbol(None, None)
    HeaderFile.setSourcePath('driver/pic32cx-bz/src/framework_defs.h')
    HeaderFile.setOutputName('framework_defs.h')
    HeaderFile.setOverwrite(True)
    HeaderFile.setDestPath('')
    HeaderFile.setProjectPath('config/' + configName)
    HeaderFile.setType('HEADER')
    HeaderFile.setEnabled(True)

    # Add osal_freertos_extend.h
    HeaderFile = libBTZBCore.createFileSymbol(None, None)
    HeaderFile.setSourcePath('driver/pic32cx-bz/src/osal/osal_freertos_extend.h')
    HeaderFile.setOutputName('osal_freertos_extend.h')
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
    SourceFile.setSourcePath('driver/pic32cx-bz/src/osal/osal_freertos_extend.c')
    SourceFile.setOutputName('osal_freertos_extend.c')
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

    # Add app_idle_task.h
    freertosidleTaskHeaderFile = libBTZBCore.createFileSymbol("APP_IDLE_TASK_H", None)
    freertosidleTaskHeaderFile.setSourcePath("driver/pic32cx-bz/src/app_idle_task.h")
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
    SourceFile = libBTZBCore.createFileSymbol(None, None)
    SourceFile.setSourcePath('driver/pic32cx-bz/templates/app.c.ftl')
    SourceFile.setOutputName('app.c')
    SourceFile.setOverwrite(True)
    SourceFile.setDestPath('../../')
    SourceFile.setProjectPath('')
    SourceFile.setType('SOURCE')
    SourceFile.setEnabled(True)
    SourceFile.setMarkup(True)

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
    deviceDeepSleepHeaderFile.setSourcePath("driver/pic32cx-bz/src/deep_sleep/device_deep_sleep.h")
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
    deviceDeepSleepSourceFile.setSourcePath("driver/pic32cx-bz/src/deep_sleep/device_deep_sleep.c")
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
    deviceSleepHeaderFile.setSourcePath("driver/pic32cx-bz/src/sleep/device_sleep.h")
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
    deviceSleepSourceFile.setSourcePath("driver/pic32cx-bz/src/sleep/device_sleep.c")
    deviceSleepSourceFile.setOutputName("device_sleep.c")
    deviceSleepSourceFile.setDestPath('')
    deviceSleepSourceFile.setProjectPath('config/' + configName)
    deviceSleepSourceFile.setType("SOURCE")
    deviceSleepSourceFile.setMarkup(True)
    #setEnabled is controlled in handleRTC_Support
    deviceSleepSourceFile.setEnabled(False)


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
    ### Add logic for adding Zigbee stack to app.c
    ############################################################################
    global uartEnable
    uartEnable = libBTZBCore.createBooleanSymbol("ENABLE_CONSOLE", None)
    uartEnable.setLabel("Enable Console")
    uartEnable.setDefaultValue(False)
    uartEnable.setVisible(False)
    uartEnable.setDependencies(isConsoleUartEnabled, ["ZIGBEE_COLOR_SCENE_CONTROLLER:APP_ENABLE_CONSOLE", "ZIGBEE_MULTI_SENSOR:APP_ENABLE_CONSOLE", "ZIGBEE_COMBINED_INTERFACE:APP_ENABLE_CONSOLE", "ZIGBEE_THERMOSTAT:APP_ENABLE_CONSOLE",
                                                   "ZIGBEE_IAS_ACE:APP_ENABLE_CONSOLE", "ZIGBEE_ON_OFF_LIGHT:APP_ENABLE_CONSOLE", "ZIGBEE_DIMMABLE_LIGHT:APP_ENABLE_CONSOLE", "ZIGBEE_COLOR_LIGHT:APP_ENABLE_CONSOLE",
                                                   "ZIGBEE_EXTENDED_COLOR_LIGHT:APP_ENABLE_CONSOLE","ZIGBEE_TEMPERATURE_COLOR_LIGHT:APP_ENABLE_CONSOLE","ZIGBEE_CUSTOM:APP_ENABLE_CONSOLE","ZIGBEE_RUNNER:APP_ENABLE_CONSOLE"])

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
    deepSleepEnable.setLabel("Enable Deep Sleep")
    deepSleepEnable.setDefaultValue(False)
    deepSleepEnable.setVisible(False)

    ############################################################################
    ### Add Custom Antenna Region
    ############################################################################
    customAntennaRegion = libBTZBCore.createComboSymbol('CUSTOM_ANT_REGION', None, ['ETSI', 'FCC', 'ETSI_FCC'])
    customAntennaRegion.setLabel('Regulatory Region')
    customAntennaRegion.setVisible(True)


    ############################################################################
    ### Add Custom Antenna Gain Enable
    ############################################################################
    customAntennaGainEnable = libBTZBCore.createBooleanSymbol('CUSTOM_ANT_ENABLE', None)
    customAntennaGainEnable.setLabel('Enable Custom Antenna Gain')
    customAntennaGainEnable.setValue(False)
    customAntennaGainEnable.setDependencies(antGainChanged, ["CUSTOM_ANT_GAIN", "CUSTOM_ANT_REGION"])


    ############################################################################
    ### Add Custom Antenna Gain
    ############################################################################
    customAntennaGain = libBTZBCore.createIntegerSymbol('CUSTOM_ANT_GAIN', customAntennaGainEnable)
    customAntennaGain.setLabel('Custom Antenna Gain (dBm)')
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
    Database.sendMessage("HarmonyCore", "ENABLE_APP_FILE", {"isEnabled":True})

    print("Setting 'Minimal Stack Size' to 256")
    Database.setSymbolValue("FreeRTOS", "FREERTOS_MINIMAL_STACK_SIZE", 256)

    print("Setting 'Memory Management Type' to 'Heap_4'")
    remoteComponent = Database.getComponentByID("FreeRTOS")
    if (remoteComponent):
        memoryManagementChoice = remoteComponent.getSymbolByID("FREERTOS_MEMORY_MANAGEMENT_CHOICE")
        memoryManagementChoice.setValue('Heap_4')

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
        sendAntMessage('CUSTOM_ANT_REGION', source["component"].getSymbolByID("CUSTOM_ANT_REGION").getValue())

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
        rtcRequiredSymbol = localComponent.getSymbolByID('SLEEP_SUPPORTED')

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
        print("handleDeepSleepEnable setting True")
    else:
        deviceDeepSleepHeaderFile.setEnabled(False)
        deviceDeepSleepSourceFile.setEnabled(False)
        print("handleDeepSleepEnable setting False")    

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
