#Essential changes for each release
releaseVersion = "PDS v1.0.0"
releaseYear    = "2021"
deviceNameBZ2  = "PIC32CX1012BZ250XX"
Function = "PERSISTENT DATA STORAGE"

global getDeviceName
getDeviceName = libPDS.createStringSymbol("DEVICE_NAME", None)
getDeviceName.setDefaultValue(deviceNameBZ2)
getDeviceName.setVisible(True)
getDeviceName.setReadOnly(True)

getStackComponent = libPDS.createStringSymbol("FUNCTIONALITY", None)
getStackComponent.setDefaultValue(Function)
getStackComponent.setVisible(True)
getStackComponent.setReadOnly(True)
