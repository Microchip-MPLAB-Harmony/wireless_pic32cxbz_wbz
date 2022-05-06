def instantiateComponent(signFW):
    print('PIC32CX-BZ3 SIGN FW')
    configName = Variables.get('__CONFIGURATION_NAME')
    listV = Variables.getNames()
    for element in listV:
        print('"{}" value is "{}"'.format(element, Variables.get(element)))
        
    fileDestPath = '../../../' + Variables.get('__PROJECT_FOLDER_NAME') + '/'
    print('fileDestPath = "{}" '.format(fileDestPath))

    # Enable support for Firmware Signature Validation
    fwSignCheckbox = signFW.createBooleanSymbol("APP_FW_SIGN_VERIFY", None)
    fwSignCheckbox.setLabel("Use Firmware Signature Verifcation API in Bootloader")
    fwSignCheckbox.setDescription("This option can be used to validate image's Signature")
    fwSignCheckbox.setDefaultValue(False)
    fwSignCheckbox.setVisible(True)
    fwSignCheckbox.setReadOnly(False)
    fwSignCheckbox.setDependencies(fwSignVerifyDependency, ["APP_FW_SIGN_VERIFY"])
    
    Database.setSymbolValue("core", "ADD_LINKER_FILE", False)
    
    #Add OTA_Enable boolean symbol for using with linker ftl file
    # global otaEnable
    # otaEnable = signFW.createBooleanSymbol("OTA_ENABLE", None)
    # otaEnable.setDefaultValue(True)
    # otaEnable.setVisible(False)
    # otaEnable.setReadOnly(True)

    ############################################################################
    ### Add linker - File
    ############################################################################

    #Linker File OverWrite - Need streamlined process that works for pds/ota components
    # otaLinkerFile = signFW.createFileSymbol("OTA_LINKER_FILE", None)
    # otaLinkerFile.setSourcePath("driver/pic32cx-bz/templates/PIC32CX1012BZ25048_ota_nopds.ld.ftl")
    # otaLinkerFile.setOutputName("PIC32CX1012BZ25048.ld")
    # otaLinkerFile.setMarkup(True)
    # otaLinkerFile.setOverwrite(True)
    # otaLinkerFile.setType("LINKER")
    # otaLinkerFile.setEnabled(Database.getComponentByID("pdsSystem") == None)
    # otaLinkerFile.setDependencies(enableFwSign, ["APP_FW_SIGN_VERIFY", "OTA_ENABLE"])


    ############################################################################
    ### Add autoload.py - File
    ############################################################################

    autoloadPythonScriptFile = signFW.createFileSymbol(None, None)
    autoloadPythonScriptFile.setSourcePath('utilities/pic32cx-bz/autoload_buckland.py')
    autoloadPythonScriptFile.setOutputName('autoload.py')
    autoloadPythonScriptFile.setOverwrite(True)
    autoloadPythonScriptFile.setDestPath(fileDestPath)
    autoloadPythonScriptFile.setProjectPath('')
    autoloadPythonScriptFile.setType('IMPORTANT')
    autoloadPythonScriptFile.setEnabled(True)

    ############################################################################
    ### Add key pem - File
    ############################################################################

    javaKeyPemFile = signFW.createFileSymbol(None, None)
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

#Dependency callback once firmware Signature verification in enabled in the application
def enableFwSign(symbol, event):
    symbol.setEnabled(event["value"])


# def onAttachmentConnected(source, target):
    # print('OTA component - onAttachmentConnected event')
    # otaEnable.setValue(True)

# def onAttachmentDisconnected(source, target):
    # print('OTA component - onAttachmentDisconnected event')
    # otaEnable.setValue(False)

