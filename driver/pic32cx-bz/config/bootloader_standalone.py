
def finalizeComponent(bootloaderComponent):
    # Deactivate FreeRTOS if added
    result = Database.deactivateComponents(['FreeRTOS'])
    # Connect the NVM, WolfCrypt, Crypto, SysTime dependencies with the component dependencies
    result = Database.connectDependencies([['Bootloader', 'Bootloader_nvm', 'nvm', 'NVM_MEMORY']])
    result = Database.connectDependencies([['lib_crypto', 'LIB_CRYPTO_WOLFCRYPT_Dependency', 'lib_wolfcrypt', 'lib_wolfcrypt']])
    result = Database.connectDependencies([['Bootloader', 'Bootloader_WolfCrypt_Dependency', 'lib_wolfcrypt', 'lib_wolfcrypt']])
    result = Database.connectDependencies([['sys_time', 'sys_time_TMR_dependency', 'tc3', 'TC3_TMR']])

def instantiateComponent(libBootloader):
    print('PIC32CX-BZ Bootloader')
    configName = Variables.get('__CONFIGURATION_NAME')

    # Disable UART and Timer Dependencies since by DFU and CONSOLE is not enabled 
    libBootloader.setDependencyEnabled("Bootloader_usart", False)
    libBootloader.setDependencyEnabled("Bootloader_timer", False)

    # Enable DFU CheckBox in MHC - By default it is disabled
    global enableDfuCheckbox
    enableDfuCheckbox = libBootloader.createBooleanSymbol("BOOTLOADER_DFU_ENABLE", None)
    enableDfuCheckbox.setLabel("Enable Bootloader UART DFU")
    enableDfuCheckbox.setDescription("This option can be used to update device firmware using UART interface")
    enableDfuCheckbox.setDefaultValue(False)
    enableDfuCheckbox.setVisible(True)
    enableDfuCheckbox.setReadOnly(False)
    enableDfuCheckbox.setDependencies(modifyDfuDependency, ["BOOTLOADER_DFU_ENABLE"])

    # DFU Mode Keyvalue symbol in MHC for selecting the GPIO Trigger DFU mode or Timer Based Trigger mode 
    global DfuMode
    DfuMode = libBootloader.createKeyValueSetSymbol("BOOTLOADER_DFU_MODE", enableDfuCheckbox)
    DfuMode.setLabel("DFU Mode")
    DfuMode.addKey("GPIO_TRIGGER", "GPIO_TRIGGER", "GPIO Trigger")
    DfuMode.addKey("TIMER_BASED_TRIGGER", "TIMER_BASED_TRIGGER", "Timer Based Trigger")
    DfuMode.setDefaultValue(0)
    DfuMode.setDisplayMode("Description")
    DfuMode.setOutputMode("Key")
    DfuMode.setVisible((enableDfuCheckbox.getValue() == True))
    DfuMode.setDependencies(enableDfuModeOption, ["BOOTLOADER_DFU_ENABLE"])

    # GPIO Port Selection which will be used in GPIO Trigger DFU Mode
    gpioPortSelection = libBootloader.createKeyValueSetSymbol("BOOTLOADER_GPIO_PORT", enableDfuCheckbox)
    gpioPortSelection.setLabel("GPIO Port")
    gpioPortSelection.addKey("PORT_A", "PORT_A", "PORT_A")
    gpioPortSelection.addKey("PORT_B", "PORT_B", "PORT_B")
    gpioPortSelection.setDefaultValue(1)#PORT_B
    gpioPortSelection.setDisplayMode("Description")
    gpioPortSelection.setOutputMode("Key")
    gpioPortSelection.setVisible((enableDfuCheckbox.getValue() == True) and(DfuMode.getValue()== 0))
    gpioPortSelection.setDependencies(enableGPIOPortPin, ["BOOTLOADER_DFU_MODE","BOOTLOADER_DFU_ENABLE"])

    # GPIO Pin Selection which will be used in GPIO Trigger DFU Mode
    gpioPortPinSelection = libBootloader.createIntegerSymbol("BOOTLOADER_GPIO_PIN", enableDfuCheckbox)
    gpioPortPinSelection.setLabel("GPIO Pin")
    gpioPortPinSelection.setDefaultValue(4)
    gpioPortPinSelection.setMin(0)
    gpioPortPinSelection.setMax(31)
    gpioPortPinSelection.setVisible((enableDfuCheckbox.getValue() == True) and (DfuMode.getValue()== 0))
    gpioPortPinSelection.setDependencies(enableGPIOPortPin, ["BOOTLOADER_DFU_MODE","BOOTLOADER_DFU_ENABLE"])

    # DFU Time Interval in MHC - The interval where bootloader will be in DFU mode before jumping to application in Timer based DFU Mode
    global DfuTimeBasedInterval
    DfuTimeBasedInterval = libBootloader.createFloatSymbol("BOOTLOADER_DFU_TIMER_INTERVAL", enableDfuCheckbox)
    DfuTimeBasedInterval.setLabel("DFU Wait Time in MillSeconds")
    DfuTimeBasedInterval.setDefaultValue(400.0)
    DfuTimeBasedInterval.setMin(200.0)
    DfuTimeBasedInterval.setMax(15000.0)
    DfuTimeBasedInterval.setVisible(DfuMode.getValue()== 1)
    DfuTimeBasedInterval.setDependencies(enableWaitTimeIntervalOptionAndModifyDependancy, ["BOOTLOADER_DFU_MODE"])

    # Symbol used to set the Timer TC0 values upon dfuTimeUpdate dependency callback 
    DfuTimeIntervalUpdate = libBootloader.createFloatSymbol("BOOTLOADER_DFU_TIMER_INTERVAL_UPDATE", enableDfuCheckbox)
    DfuTimeIntervalUpdate.setVisible(False)
    DfuTimeIntervalUpdate.setDependencies(dfuTimeUpdate, ["BOOTLOADER_DFU_TIMER_INTERVAL"])

    # Enable Console CheckBox in MHC - By Default it is disabled.
    enableConsoleCheckbox = libBootloader.createBooleanSymbol("BOOTLOADER_CONSOLE_ENABLE", None)
    enableConsoleCheckbox.setLabel("Enable Console")
    enableConsoleCheckbox.setDescription("This option can be used to enable console prints")
    enableConsoleCheckbox.setDefaultValue(False)
    enableConsoleCheckbox.setVisible(True)
    enableConsoleCheckbox.setReadOnly(False)
    enableConsoleCheckbox.setDependencies(modifyConsoleDependency, ["BOOTLOADER_CONSOLE_ENABLE"])

    # ECC Public key
    eccPublicKey = libBootloader.createStringSymbol("ECC_PUBLIC_KEY", None)
    eccPublicKey.setLabel("ECC Public Key")
    eccPublicKey.setVisible(True)
    eccPublicKey.setDefaultValue('0xc2,0x81,0x8f,0xbb,0x28,0x61,0x47,0x8b,0xa2,0x53,0x37,0x79,0xd4,0x63,0x18,0x7c,0x8b,0x41,0x59,0xa9,0x5f,0x0b,0x6b,0x94,0x4e,0xb9,0x57,0xa1,0x03,0xfe,0x20,0xbf,0x2b,0xb8,0x14,0x2a,0x64,0xb5,0xae,0x4a,0x83,0x80,0xdd,0xe6,0xee,0x29,0x89,0xdd,0xa0,0x9a,0xc7,0xda,0x82,0xeb,0x56,0x62,0x90,0x5d,0x66,0xc5,0xbc,0x30,0x3c,0x84')
    eccPublicKey.setDescription("Public Key used for ECC")

    #Authentication Method - Menu
    authenticationMethodMenu = libBootloader.createMenuSymbol("APPCONFIG_MENU", None)
    authenticationMethodMenu.setLabel("Supported Authentication Methods")
    authenticationMethodMenu.setVisible(True)

    # Authentication Method - None Support
    authenticationMethodNone = libBootloader.createBooleanSymbol("BOOTLOADER_AUTH_METHOD_NONE_ENABLE", authenticationMethodMenu)
    authenticationMethodNone.setLabel("None")
    authenticationMethodNone.setDescription("This option is used to enable None authentication method in bootloader")
    authenticationMethodNone.setDefaultValue(True)
    authenticationMethodNone.setVisible(True)
    authenticationMethodNone.setReadOnly(False)

    # Authentication Method - SHA256 Support
    authenticationMethodSHA256 = libBootloader.createBooleanSymbol("BOOTLOADER_AUTH_METHOD_SHA256_ENABLE", authenticationMethodMenu)
    authenticationMethodSHA256.setLabel("SHA256")
    authenticationMethodSHA256.setDescription("This option is used to enable SHA256 authentication method in bootloader")
    authenticationMethodSHA256.setDefaultValue(True)
    authenticationMethodSHA256.setVisible(True)
    authenticationMethodSHA256.setReadOnly(False)

    # Authentication Method - ECDSA256 Support
    authenticationMethodECDSA256 = libBootloader.createBooleanSymbol("BOOTLOADER_AUTH_METHOD_ECDSA256_ENABLE", authenticationMethodMenu)
    authenticationMethodECDSA256.setLabel("ECDSA256")
    authenticationMethodECDSA256.setDescription("This option is used to enable ECDSA256 authentication method in bootloader")
    authenticationMethodECDSA256.setDefaultValue(True)
    authenticationMethodECDSA256.setVisible(True)
    authenticationMethodECDSA256.setReadOnly(False)

    # Symbol which holds the SERCOM Instance number - It is updated upon connection of a sercom
    global DfuSercomInstanceNum
    DfuSercomInstanceNum = libBootloader.createIntegerSymbol("BOOTLOADER_DFU_SERCOM_INSTANCE_NUM", enableDfuCheckbox)
    DfuSercomInstanceNum.setLabel("DFU SERCOM Instance Number")
    DfuSercomInstanceNum.setDefaultValue(-1)
    DfuSercomInstanceNum.setVisible(False)
    ############################################################################
    ### Activate dependencies
    ############################################################################

    #Activate Required Components
    res = Database.activateComponents(['HarmonyCore', 'lib_crypto', 'lib_wolfcrypt', 'nvm', 'sys_time','tc3'])

    processor = Variables.get('_PROCESSOR')
    print('processor={}'.format(processor))

    ############################################################################
    #### Code Generation ####
    ############################################################################
    # Add mem_interface.h file
    booloaderMemIntHeaderFile = libBootloader.createFileSymbol(None, None)
    booloaderMemIntHeaderFile.setSourcePath('driver/pic32cx-bz/src/btl/mem_interface.h')
    booloaderMemIntHeaderFile.setOutputName('mem_interface.h')
    booloaderMemIntHeaderFile.setOverwrite(True)
    booloaderMemIntHeaderFile.setDestPath('bootloader')
    booloaderMemIntHeaderFile.setProjectPath('config/' + configName + '/bootloader')
    booloaderMemIntHeaderFile.setType('HEADER')
    booloaderMemIntHeaderFile.setEnabled(True)

    # Add application.h file
    booloaderMemIntHeaderFile = libBootloader.createFileSymbol(None, None)
    booloaderMemIntHeaderFile.setSourcePath('driver/pic32cx-bz/src/btl/application.h')
    booloaderMemIntHeaderFile.setOutputName('application.h')
    booloaderMemIntHeaderFile.setOverwrite(True)
    booloaderMemIntHeaderFile.setDestPath('bootloader')
    booloaderMemIntHeaderFile.setProjectPath('config/' + configName + '/bootloader')
    booloaderMemIntHeaderFile.setType('HEADER')
    booloaderMemIntHeaderFile.setEnabled(True)

    # Add flash.c file
    booloaderConfigSrcFile = libBootloader.createFileSymbol(None, None)
    booloaderConfigSrcFile.setSourcePath('driver/pic32cx-bz/src/btl/flash.c')
    booloaderConfigSrcFile.setOutputName('flash.c')
    booloaderConfigSrcFile.setOverwrite(True)
    booloaderConfigSrcFile.setDestPath('bootloader')
    booloaderConfigSrcFile.setProjectPath('config/' + configName + '/bootloader')
    booloaderConfigSrcFile.setType('SOURCE')
    booloaderConfigSrcFile.setEnabled(True)

    # Add crc.h file
    booloaderDfuHeaderFile = libBootloader.createFileSymbol(None, None)
    booloaderDfuHeaderFile.setSourcePath('driver/pic32cx-bz/src/btl/dfu/include/crc.h')
    booloaderDfuHeaderFile.setOutputName('crc.h')
    booloaderDfuHeaderFile.setOverwrite(True)
    booloaderDfuHeaderFile.setDestPath('bootloader/dfu/include')
    booloaderDfuHeaderFile.setProjectPath('config/' + configName + '/bootloader/dfu/include/')
    booloaderDfuHeaderFile.setType('HEADER')
    booloaderDfuHeaderFile.setEnabled(enableDfuCheckbox.getValue() == True)
    booloaderDfuHeaderFile.setDependencies(enableDfuFn, ["BOOTLOADER_DFU_ENABLE"])

    # Add progexec.h file
    booloaderDfuHeaderFile = libBootloader.createFileSymbol(None, None)
    booloaderDfuHeaderFile.setSourcePath('driver/pic32cx-bz/src/btl/dfu/include/progexec.h')
    booloaderDfuHeaderFile.setOutputName('progexec.h')
    booloaderDfuHeaderFile.setOverwrite(True)
    booloaderDfuHeaderFile.setDestPath('bootloader/dfu/include')
    booloaderDfuHeaderFile.setProjectPath('config/' + configName + '/bootloader/dfu/include/')
    booloaderDfuHeaderFile.setType('HEADER')
    booloaderDfuHeaderFile.setEnabled(enableDfuCheckbox.getValue() == True)
    booloaderDfuHeaderFile.setDependencies(enableDfuFn, ["BOOTLOADER_DFU_ENABLE"])

    # Add uart.h file - will be removed later
    booloaderDfuHeaderFile = libBootloader.createFileSymbol(None, None)
    booloaderDfuHeaderFile.setSourcePath('driver/pic32cx-bz/src/btl/dfu/include/uart.h')
    booloaderDfuHeaderFile.setOutputName('uart.h')
    booloaderDfuHeaderFile.setOverwrite(True)
    booloaderDfuHeaderFile.setDestPath('bootloader/dfu/include')
    booloaderDfuHeaderFile.setProjectPath('config/' + configName + '/bootloader/dfu/include/')
    booloaderDfuHeaderFile.setType('HEADER')
    booloaderDfuHeaderFile.setEnabled(enableDfuCheckbox.getValue() == True)
    booloaderDfuHeaderFile.setDependencies(enableDfuFn, ["BOOTLOADER_DFU_ENABLE"])

    # Add crc.c file
    booloaderDfuSourceFile = libBootloader.createFileSymbol(None, None)
    booloaderDfuSourceFile.setSourcePath('driver/pic32cx-bz/src/btl/dfu/src/crc.c')
    booloaderDfuSourceFile.setOutputName('crc.c')
    booloaderDfuSourceFile.setOverwrite(True)
    booloaderDfuSourceFile.setDestPath('bootloader/dfu/src')
    booloaderDfuSourceFile.setProjectPath('config/' + configName + '/bootloader/dfu/src/')
    booloaderDfuSourceFile.setType('SOURCE')
    booloaderDfuSourceFile.setEnabled(enableDfuCheckbox.getValue() == True)
    booloaderDfuSourceFile.setDependencies(enableDfuFn, ["BOOTLOADER_DFU_ENABLE"])

    # Add progexec.c file
    booloaderDfuSourceFile = libBootloader.createFileSymbol(None, None)
    booloaderDfuSourceFile.setSourcePath('driver/pic32cx-bz/templates/btl/progexec.c.ftl')
    booloaderDfuSourceFile.setOutputName('progexec.c')
    booloaderDfuSourceFile.setOverwrite(True)
    booloaderDfuSourceFile.setDestPath('bootloader/dfu/src')
    booloaderDfuSourceFile.setProjectPath('config/' + configName + '/bootloader/dfu/src/')
    booloaderDfuSourceFile.setType('SOURCE')
    booloaderDfuSourceFile.setMarkup(True)
    booloaderDfuSourceFile.setEnabled(enableDfuCheckbox.getValue() == True)
    booloaderDfuSourceFile.setDependencies(enableDfuFn, ["BOOTLOADER_DFU_ENABLE"])

    booloaderDfuSourceFile = libBootloader.createFileSymbol(None, None)
    booloaderDfuSourceFile.setSourcePath('driver/pic32cx-bz/templates/btl/uart.c.ftl')
    booloaderDfuSourceFile.setOutputName('uart.c')
    booloaderDfuSourceFile.setOverwrite(True)
    booloaderDfuSourceFile.setDestPath('bootloader/dfu/src')
    booloaderDfuSourceFile.setProjectPath('config/' + configName + '/bootloader/dfu/src/')
    booloaderDfuSourceFile.setType('SOURCE')
    booloaderDfuSourceFile.setEnabled(enableDfuCheckbox.getValue() == True)
    booloaderDfuSourceFile.setMarkup(True)
    booloaderDfuSourceFile.setDependencies(enableDfuFn, ["BOOTLOADER_DFU_ENABLE"])

    # Add app.c
    SourceFile = libBootloader.createFileSymbol(None, None)
    SourceFile.setSourcePath('driver/pic32cx-bz/templates/btl/app.c.ftl')
    SourceFile.setOutputName('app.c')
    SourceFile.setOverwrite(True)
    SourceFile.setDestPath('../../')
    SourceFile.setProjectPath('')
    SourceFile.setType('SOURCE')
    SourceFile.setEnabled(True)
    SourceFile.setMarkup(True)

    # Add Bootlooader Inc path
    incPathSym = libBootloader.createSettingSymbol('BOOTLOADER_INC_PATH', None)
    incPathSym.setValue('../src/config/' + configName + '/bootloader' + ';')
    incPathSym.setCategory('C32')
    incPathSym.setKey('extra-include-directories')
    incPathSym.setAppend(True, ';')
    incPathSym.setEnabled(True)

    # Warning to errors as False in Compiler settings
    warningerr = libBootloader.createSettingSymbol('WARNINGG_ERR', None)
    warningerr.setValue('false')
    warningerr.setCategory('C32')
    warningerr.setKey('make-warnings-into-errors')

    # Enable Report Memory Usage in Linker
    reportMemUsage = libBootloader.createSettingSymbol('REPORT_MEM_USAGE', None)
    reportMemUsage.setValue('true')
    reportMemUsage.setCategory('C32-LD')
    reportMemUsage.setKey('report-memory-usage')

    # Add initialization code to SYSTEM_INITIALIZATION in initialization.c
    SystemInitStartFile = libBootloader.createFileSymbol('BOOTLOADER_SYSTEM_INITIALIZATION', None)
    SystemInitStartFile.setType('STRING')
    SystemInitStartFile.setOutputName('core.LIST_SYSTEM_INIT_C_SYSTEM_INITIALIZATION')
    SystemInitStartFile.setSourcePath('driver/pic32cx-bz/templates/system/system_initialize_initialization_btl.c.ftl')
    SystemInitStartFile.setMarkup(True)

    # Add initializer to SYS_INITIALIZE_START in initialization.c
    SystemInitStartFile = libBootloader.createFileSymbol('BOOTLOADER_SYS_INIT_START', None)
    SystemInitStartFile.setType('STRING')
    SystemInitStartFile.setOutputName('core.LIST_SYSTEM_INIT_C_SYS_INITIALIZE_START')
    SystemInitStartFile.setSourcePath('driver/pic32cx-bz/templates/system/system_initialize_start_btl.c.ftl')
    SystemInitStartFile.setMarkup(True)

    # Add include files to definitions.h
    SystemInitStartFile = libBootloader.createFileSymbol('BOOTLOADER_PIC32CX-BZ_DEF', None)
    SystemInitStartFile.setType('STRING')
    SystemInitStartFile.setOutputName('core.LIST_SYSTEM_DEFINITIONS_H_INCLUDES')
    SystemInitStartFile.setSourcePath('driver/pic32cx-bz/templates/system/system_definitions_btl.h.ftl')
    SystemInitStartFile.setMarkup(True)

    # Harmony Core Settings if not set
    if Database.getSymbolValue('HarmonyCore', 'ENABLE_APP_FILE') == False: 
        Database.setSymbolValue('HarmonyCore', 'ENABLE_APP_FILE', True)

    if Database.getSymbolValue('HarmonyCore', 'ENABLE_SYS_COMMON') == False: 
        Database.setSymbolValue('HarmonyCore', 'ENABLE_SYS_COMMON', True)

    if Database.getSymbolValue('HarmonyCore', 'ENABLE_SYS_INT') == False: 
        Database.setSymbolValue('HarmonyCore', 'ENABLE_SYS_INT', True)

    if Database.getSymbolValue('HarmonyCore', 'ENABLE_OSAL') == False: 
        Database.setSymbolValue('HarmonyCore', 'ENABLE_OSAL', True)

    # Setting the required heap size for the application
    Database.sendMessage("core", "HEAP_SIZE", {"heap_size":2048})

    # Disable Default linker script
    Database.setSymbolValue("core", "ADD_LINKER_FILE", False)

    # Enable Clock of PUKCC - Public Key Cryptography Controller and ICM - Integrity Check Monitor
    # Needed for WolfCrypt SHA256
    Database.setSymbolValue("core", "PUKCC_CLOCK_ENABLE", True)
    Database.setSymbolValue("core", "ICM_CLOCK_ENABLE", True)

    # Add Custom linker script
    booloaderLinkerFile = libBootloader.createFileSymbol("BOOTLOADER_LINKER_FILE", None)
    booloaderLinkerFile.setSourcePath("/driver/pic32cx-bz/templates/btl/PIC32CX1012BZ25048.ld")
    booloaderLinkerFile.setOutputName("PIC32CX1012BZ25048.ld")
    booloaderLinkerFile.setMarkup(True)
    booloaderLinkerFile.setOverwrite(True)
    booloaderLinkerFile.setType("LINKER")
###############################################################################
### Process dependency connections to determine which clients are loaded
###############################################################################

REQUIRES_BOOTLOADER = {}
def onAttachmentConnected(source, target):
    connectID = source["id"]
    Log.writeInfoMessage('Bootloader:onAttachmentConnected: source = {} remote = {}'.format(source["component"].getID(), target["component"].getID()))
    if target["component"].getID() in REQUIRES_BOOTLOADER.keys():
        boolSymbol = source["component"].getSymbolByID(REQUIRES_BOOTLOADER[target["component"].getID()])
        Log.writeInfoMessage('Bootloader:onAttachmentConnected: setting {} to True'.format(boolSymbol.getID()))
        boolSymbol.setValue(True)
    # Upon Connection of Bootloader_usart dependency, get the SERCOM Instance number and set it in DfuSercomInstanceNum
    # And Set the Operating Mode as Ring Buffer Mode and TX RING BUFFER SIZE & RX RING BUFFER SIZE as 5120 which is common
    # requirement for any SERCOM UART
    if (connectID == "Bootloader_usart"):
        remoteComponent = target["component"]
        remoteID = remoteComponent.getID()
        DfuSercomInstanceNum.setValue(int(remoteID[-1]))
        Database.setSymbolValue("sercom"+remoteID[-1], "USART_OPERATING_MODE", 2)#2 - Ring buffer mode
        Database.setSymbolValue("sercom"+remoteID[-1], "USART_TX_RING_BUFFER_SIZE", 5120)
        Database.setSymbolValue("sercom"+remoteID[-1], "USART_RX_RING_BUFFER_SIZE", 5120)

    # Upon Connection of Wolfcrypt dependency, update the required settings in Wolfcrypt
    elif (connectID == "Bootloader_WolfCrypt_Dependency"):
        print("onAttachmentConnected configuring lib_wolfcrypt")
        Database.setSymbolValue("lib_wolfcrypt", "wolfcrypt_hw", True)
        Database.setSymbolValue("lib_wolfcrypt", "wolfcrypt_md5", False)
        Database.setSymbolValue("lib_wolfcrypt", "wolfcrypt_sha1", False)
        Database.setSymbolValue("lib_wolfcrypt", "wolfcrypt_sha256", True)
        Database.setSymbolValue("lib_wolfcrypt", "wolfcrypt_sha224", False)
        Database.setSymbolValue("lib_wolfcrypt", "wolfcrypt_sha264_hw", True)
        Database.setSymbolValue("lib_wolfcrypt", "wolfcrypt_hmac", False)
        Database.setSymbolValue("lib_wolfcrypt", "wolfcrypt_tdes", False)
        Database.setSymbolValue("lib_wolfcrypt", "wolfcrypt_aes", False)
        Database.setSymbolValue("lib_wolfcrypt", "wolfcrypt_ecc_hw", True)
        Database.setSymbolValue("lib_wolfcrypt", "wolfcrypt_rsa", False)
        Database.setSymbolValue("lib_wolfcrypt", "wolfcrypt_oaep", False)
        Database.setSymbolValue("lib_wolfcrypt", "wolfcrypt_random", True)
    # Upon connection of Bootloader_timer dependency, set the Timer 0 symbols for the DfuTimeBasedInterval time for Timer based trigger
    # DFU mode- Configuring millisecond timer for DfuTimeBasedInterval time.
    elif (connectID == "Bootloader_timer"):
        print("onAttachmentConnected configuring Timer 0")
        Database.setSymbolValue("tc0", "TC_CTRLA_MODE", 2)
        Database.setSymbolValue("tc0", "TC_CTRLA_PRESCALER", 5)
        Database.setSymbolValue("tc0", "TC_TIMER_CTRLBSET_ONESHOT", True)
        Database.getComponentByID("tc0").getSymbolByID("TC_TIMER_TIME_MS").setValue(DfuTimeBasedInterval.getValue())

def onAttachmentDisconnected(source, target):
    Log.writeInfoMessage('Bootloader:onAttachmentDisconnected: source = {} remote = {}'.format(source["component"].getID(), target["component"].getID()))
    if target["component"].getID() in REQUIRES_BOOTLOADER.keys():
        boolSymbol = source["component"].getSymbolByID(REQUIRES_BOOTLOADER[target["component"].getID()])
        Log.writeInfoMessage('Bootloader:onAttachmentConnected: setting {} to False'.format(boolSymbol.getID()))
        boolSymbol.setValue(False)

# Dependency callback called upon DFU checkbox is selected in MHC.
# This function enables Bootloader_usart dependency for connection to sercom
def modifyDfuDependency(symbol, event):
    print('PIC32CX-BZ Bootloader-modifyDfuDependency')
    localComponent = symbol.getComponent()
    if event["value"] == True:
        localComponent.setDependencyEnabled("Bootloader_usart", True) 
        print('Set Bootloader_usart dependency = True; modifyDfuDependency')
    else:
        consoleSymbol = localComponent.getSymbolByID("BOOTLOADER_CONSOLE_ENABLE")
        if (consoleSymbol.getValue() == False):
            localComponent.setDependencyEnabled("Bootloader_usart", False)
            print('Set Bootloader_usart dependency = False; modifyDfuDependency')
        else:
            print('Set Bootloader_usart dependency = True; modifyDfuDependency')
        
# Dependency callback called upon console checkbox is selected in MHC.
# This function enables Bootloader_usart dependency for connection to sercom
def modifyConsoleDependency(symbol, event):
    print('PIC32CX-BZ Bootloader-modifyConsoleDependency')
    localComponent = symbol.getComponent()
    if event["value"] == True:
        localComponent.setDependencyEnabled("Bootloader_usart", True) 
        print('Set Bootloader_usart dependency = True; modifyConsoleDependency')
    else:
        dfuSymbol = localComponent.getSymbolByID("BOOTLOADER_DFU_ENABLE")
        if (dfuSymbol.getValue() == False):
            localComponent.setDependencyEnabled("Bootloader_usart", False)
            print('Set Bootloader_usart dependency = False; modifyConsoleDependency')
        else:
            print('Set Bootloader_usart dependency = True; modifyConsoleDependency')

# Dependency callback called upon DFU is enabled
def enableDfuFn(symbol, event):
    symbol.setEnabled(event["value"])

# Dependency callback called upon DFU Mode is enabled
def enableDfuModeOption(symbol, event):
    symbol.setVisible(event["value"])

# Dependency callback called upon GPIO trigger mode is selected.
def enableGPIOPortPin(symbol, event):
    if (enableDfuCheckbox.getValue() == True) and (DfuMode.getValue()== 0):
       symbol.setVisible(True)
    else:
       symbol.setVisible(False)

# Dependency callback called upon Timer based trigger mode is selected.
# This function activates the TC0, enables Bootloader_timer dependency and connect the dependencies
def enableWaitTimeIntervalOptionAndModifyDependancy(symbol, event):
    symbol.setVisible(event["value"]==1)
    print('PIC32CX-BZ Bootloader-modifyDfuModeDependency')
    localComponent = symbol.getComponent()
    #print(event["value"])
    if event["value"] == 1:#"TIMER_BASED_TRIGGER"
        localComponent.setDependencyEnabled("Bootloader_timer", True)
        result = Database.activateComponents(['tc0'])
        result = Database.connectDependencies([['Bootloader', 'Bootloader_timer', 'tc0', 'TC0_TMR']])
        print('Set Bootloader_timer dependency = True; modifyDfuModeDependency')
    else:
        localComponent.setDependencyEnabled("Bootloader_timer", False)
        print('Set Bootloader_timer dependency = False; modifyDfuModeDependency')

# Dependency callback to set Timer interval in Timer 0 component upon value change in DfuTimeBasedInterval
def dfuTimeUpdate(symbol, event):
    Database.getComponentByID("tc0").getSymbolByID("TC_TIMER_TIME_MS").setValue(DfuTimeBasedInterval.getValue())
