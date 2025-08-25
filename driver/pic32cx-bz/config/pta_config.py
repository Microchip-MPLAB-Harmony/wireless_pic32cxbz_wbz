# coding: utf-8
"""*****************************************************************************
* Copyright (C) 2024 Microchip Technology Inc. and its subsidiaries.
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
import time

pic32cx_bz2_family = {'PIC32CX1012BZ25048',
                      'PIC32CX1012BZ25032',
                      'PIC32CX1012BZ24032',
                      'WBZ451',
                      'WBZ450',
                      'WBZ451H',
                      'PIC32WM_BW1',
                      }

pic32cx_bz3_family = {'PIC32CX5109BZ31048',
                      'PIC32CX5109BZ31032',
                      'WBZ351',
                      'WBZ350',
                      }
pic32cx_bz36_family = {'PIC32CX5109BZ36048',
                       'PIC32CX5109BZ36032',
                       'PIC32WM_BZ3601',
                       'PIC32WM_BZ3602',
                      }
pic32cx_bz6_family = {'PIC32CX2051BZ62132',
                      'PIC32CX2051BZ62064',
                      'PIC32CX2051BZ66048',
                      'WBZ653',
                      'WBZ652',
                      'WBZ651',
                      'PIC32WM_BZ6204',
                      'PIC32WM_BZ6203',
                      'PIC32WM_BZ6602',
                     }

global pta_symbols
pta_symbols = []

global ptaFileSymbls
ptaFileSymbls = []

global PTA_PIN_CONFIG
PTA_PIN_CONFIG = {"PTA_REQ_PIN"      : "",
                  "PTA_PRIO_PIN"     : "",
                  "WLAN_ACTIVE_PIN"  : ""
                  }

global handlePTA_Symbols

def handlePTA_Symbols(ptaEnabled):    
    global EnablePta
    global phyPTASupportEnable
    global blePTASupportEnable
    global ptaInterface
    
    if ptaEnabled == True:
        for symbl in pta_symbols:
           symbl.setVisible(True)
        for file in ptaFileSymbls:
           file.setEnabled(True)
        try:
            handlePtaReqPinSetting(PTA_PIN_CONFIG["PTA_REQ_PIN"])
        except:
            pass
        try:
            handlePtaPrioPinSetting(PTA_PIN_CONFIG["PTA_PRIO_PIN"])
        except:
            pass
        try:
            handlePtaWlanActiveSetting(PTA_PIN_CONFIG["WLAN_ACTIVE_PIN"])
        except:
            pass
    else:
        for symbl in pta_symbols:
            symbl.setVisible(False)
        for file in ptaFileSymbls:
            file.setEnabled(False)
        clearPtaPinSetting(PTA_PIN_CONFIG["PTA_REQ_PIN"],"PTA_REQ")
        clearPtaPinSetting(PTA_PIN_CONFIG["PTA_PRIO_PIN"],"PTA_PRIO")
        clearPtaPinSetting(PTA_PIN_CONFIG["WLAN_ACTIVE_PIN"],"WLAN_ACTIVE")
    


global handlePTA_Support

def handlePTA_Support(symbol,event):
    symbolID = event["id"]
    value = event["value"]
    
    global EnablePta
    global phyPTASupportEnable
    global blePTASupportEnable
    global ptaInterface
    
    if (deviceName in pic32cx_bz2_family):
        devsupport_component = "pic32cx_bz2_devsupport"
    elif ((deviceName in pic32cx_bz3_family) or (deviceName in pic32cx_bz36_family)):
        devsupport_component = "pic32cx_bz3_devsupport"
    elif (deviceName in pic32cx_bz6_family):
        devsupport_component = "pic32cx_bz6_devsupport"
    
    if symbolID == "BLESTACK_LOADED":
        if value == True:
            if (EnablePta.getValue() == True): #and (blePTASupportEnable.getValue() == False):
                blePTASupportEnable.setValue(True)
                Database.sendMessage("BLE_STACK_LIB", "PTA_SUPPORT_ENABLE", {"target": "BLE_STACK_LIB",
                                                            "source": devsupport_component,"isEnabled":True})
                ptaInterface.setValue(0)
                # ptaInterface.setReadOnly(True)
                                                            
            elif EnablePta.getValue() == False:
                blePTASupportEnable.setValue(False)
                # ptaInterface.setReadOnly(False)
                Database.sendMessage("BLE_STACK_LIB", "PTA_SUPPORT_ENABLE", {"target": "BLE_STACK_LIB",
                                                       "source": devsupport_component,"isEnabled":False})
        else:
            blePTASupportEnable.setValue(False)
            # ptaInterface.setReadOnly(False)
            
    
    elif symbolID == "IEEE_802154_PHY_LOADED":
        if value == True:
            if EnablePta.getValue() == True:
                phyPTASupportEnable.setValue(True)
                Database.sendMessage("IEEE_802154_PHY", "PTA_SUPPORT_ENABLE", {"target": "IEEE_802154_PHY",
                                                            "source": devsupport_component,"isEnabled":True})
                                                            
            elif EnablePta.getValue() == False:
                phyPTASupportEnable.setValue(False)
                Database.sendMessage("IEEE_802154_PHY", "PTA_SUPPORT_ENABLE", {"target": "IEEE_802154_PHY",
                                                        "source": devsupport_component,"isEnabled":False})
        else:
            phyPTASupportEnable.setValue(False)
            
            

global sort_alphanumeric

def sort_alphanumeric(l):
    import re
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)
    

global clearPtaPinSetting

def clearPtaPinSetting(ptaPin,pinType):
    print("clearPtaPinSetting",ptaPin,pinType)
    if ptaPin != "":
        pinName = Database.getSymbolValue("core",ptaPin + "_FUNCTION_NAME")
        if (("PTA_REQ" in pinName) and (pinType=="PTA_REQ")) or (("PTA_PRIO" in pinName) and pinType=="PTA_PRIO") or (("WLAN_ACTIVE" in pinName) and (pinType=="WLAN_ACTIVE")):
            Database.clearSymbolValue("core", ptaPin + "_FUNCTION_TYPE")
            Database.clearSymbolValue("core", ptaPin + "_FUNCTION_NAME")
            Database.clearSymbolValue("core", ptaPin + "_DIR")
            Database.clearSymbolValue("core", ptaPin + "_PD")
            Database.clearSymbolValue("core", ptaPin + "_CN")

global handlePtaReqPinSetting
     
def handlePtaReqPinSetting(ptaReqPin):
    # print("handlePtaReqPinSetting")
    if ptaReqPin != "":
        # print("ptaReqPin:",ptaReqPin)
        # if Database.getSymbolValue("core",ptaReqPin + "_FUNCTION_NAME") == "":
        clearPtaPinSetting(ptaReqPin,"PTA_REQ")
        funcType = ptaReqPin + "_FUNCTION_TYPE"
        # print("funcType:",funcType)
        Database.setSymbolValue("core",funcType , "GPIO")
        Database.setSymbolValue("core", ptaReqPin + "_FUNCTION_NAME", "PTA_REQ")
        Database.setSymbolValue("core", ptaReqPin + "_DIR", "Out")
        Database.clearSymbolValue("core", ptaReqPin + "_LAT")
        Database.clearSymbolValue("core", ptaReqPin + "_OD")
        Database.clearSymbolValue("core", ptaReqPin + "_CN")
        Database.clearSymbolValue("core", ptaReqPin + "_PU")
        Database.setSymbolValue("core", ptaReqPin + "_PD", "True")
        Database.clearSymbolValue("core", ptaReqPin + "_SR")
            
global handlePtaPrioPinSetting
def handlePtaPrioPinSetting(ptaPrioPin):
    # print("PrioPinSetting:",ptaPrioPin) 
    if ptaPrioPin != "":
        # if Database.getSymbolValue("core",ptaPrioPin + "_FUNCTION_NAME") == "":
        clearPtaPinSetting(ptaPrioPin,"PTA_PRIO")
        funcType = ptaPrioPin + "_FUNCTION_TYPE"
        # print("funcType:",funcType)
        Database.setSymbolValue("core", funcType, "GPIO")
        Database.setSymbolValue("core", ptaPrioPin + "_FUNCTION_NAME", "PTA_PRIO")
        Database.setSymbolValue("core", ptaPrioPin + "_DIR", "Out")
        Database.clearSymbolValue("core", ptaPrioPin + "_LAT")
        Database.clearSymbolValue("core", ptaPrioPin + "_OD")
        Database.clearSymbolValue("core", ptaPrioPin + "_CN")
        Database.clearSymbolValue("core", ptaPrioPin + "_PU")
        Database.setSymbolValue("core", ptaPrioPin + "_PD", "True")
        Database.clearSymbolValue("core", ptaPrioPin + "_SR")
            
global handlePtaWlanActiveSetting
def handlePtaWlanActiveSetting(wlanActivePin):
    # print("PrioPinSetting:",wlanActivePin) 
    if wlanActivePin != "":
        # if Database.getSymbolValue("core",wlanActivePin + "_FUNCTION_NAME") == "":
        clearPtaPinSetting(wlanActivePin,"WLAN_ACTIVE")
        funcType = wlanActivePin + "_FUNCTION_TYPE"
        # print("funcType:",funcType)
        Database.setSymbolValue("core", funcType, "GPIO")
        Database.setSymbolValue("core", wlanActivePin + "_FUNCTION_NAME", "WLAN_ACTIVE")
        Database.clearSymbolValue("core", wlanActivePin + "_DIR")
        Database.clearSymbolValue("core", wlanActivePin + "_OD")
        Database.clearSymbolValue("core", wlanActivePin + "_MODE")
        Database.setSymbolValue("core", wlanActivePin + "_CN", "True")
        Database.clearSymbolValue("core", wlanActivePin + "_PU")
        Database.setSymbolValue("core", wlanActivePin + "_PD", "True")
        Database.clearSymbolValue("core", wlanActivePin + "_SR")

def ptaConfigurationCallback(symbol,event):
    symbolID = event["id"]
    value = event["value"]
    if (deviceName in pic32cx_bz2_family):
        devsupport_component = "pic32cx_bz2_devsupport"
    elif ((deviceName in pic32cx_bz3_family) or (deviceName in pic32cx_bz36_family)):
        devsupport_component = "pic32cx_bz3_devsupport"
    elif (deviceName in pic32cx_bz6_family):
        devsupport_component = "pic32cx_bz6_devsupport"
    
    if symbolID == "PTA_ENABLE":
        if value == True:
            handlePTA_Symbols(True)
            handlePtaReqPinSetting(PTA_PIN_CONFIG["PTA_REQ_PIN"])
            handlePtaPrioPinSetting(PTA_PIN_CONFIG["PTA_PRIO_PIN"])
            handlePtaWlanActiveSetting(PTA_PIN_CONFIG["WLAN_ACTIVE_PIN"])
            if ((phyLoaded.getValue() == True) and (phyPTASupportEnable.getValue() == False)):
                phyPTASupportEnable.setValue(True)
                Database.sendMessage("IEEE_802154_PHY", "PTA_SUPPORT_ENABLE", {"target": "IEEE_802154_PHY",
                                                        "source":devsupport_component ,"isEnabled":True})
            if ((bleStackLoaded.getValue() == True) and (blePTASupportEnable.getValue() == False)):
                blePTASupportEnable.setValue(True)
                Database.sendMessage("BLE_STACK_LIB", "PTA_SUPPORT_ENABLE", {"target": "BLE_STACK_LIB",
                                                        "source": devsupport_component,"isEnabled":True})
        else:
            handlePTA_Symbols(False)
            if (phyLoaded.getValue() == True):
                phyPTASupportEnable.setValue(False)
                Database.sendMessage("IEEE_802154_PHY", "PTA_SUPPORT_ENABLE", {"target": "IEEE_802154_PHY",
                                                        "source":devsupport_component ,"isEnabled":False})
            if (bleStackLoaded.getValue() == True): 
                blePTASupportEnable.setValue(False)
                Database.sendMessage("BLE_STACK_LIB", "PTA_SUPPORT_ENABLE", {"target": "BLE_STACK_LIB",
                                                        "source": devsupport_component,"isEnabled":False})
            
    elif symbolID == "PTA_INTERFACE":
        if value == 0:
            ptaReqPin.setVisible(True)
            handlePtaReqPinSetting(PTA_PIN_CONFIG["PTA_REQ_PIN"])
            ptaPriorityPin.setVisible(True)
            ptaWlanActivePin.setVisible(True)
        elif value == 1:
            clearPtaPinSetting(PTA_PIN_CONFIG["PTA_REQ_PIN"],"PTA_REQ")
            ptaReqPin.setVisible(False)
            ptaPriorityPin.setVisible(True)
            ptaWlanActivePin.setVisible(True)
            
    elif symbolID == "PTA_REQ_PIN":
        clearPtaPinSetting(PTA_PIN_CONFIG["PTA_REQ_PIN"],"PTA_REQ")
        pin_num = symbol.getKeyValue(value)
        print('ptaReq:',pin_num)
        if pin_num != '':
            ptareq = 'BSP_PIN_'+str(pin_num)
            PTA_PIN_CONFIG.update({"PTA_REQ_PIN":ptareq})
            print("ptaReq:",PTA_PIN_CONFIG["PTA_REQ_PIN"])
            handlePtaReqPinSetting(ptareq)
        else:
            PTA_PIN_CONFIG.update({"PTA_REQ_PIN": ''})
        
    elif symbolID == "PTA_PRIORITY_PIN":
        clearPtaPinSetting(PTA_PIN_CONFIG["PTA_PRIO_PIN"],"PTA_PRIO")
        pin_num = symbol.getKeyValue(value)
        print('ptaPrio:',pin_num)
        if pin_num != '':
            ptaprio = 'BSP_PIN_'+str(pin_num)
            PTA_PIN_CONFIG.update({"PTA_PRIO_PIN":ptaprio}) 
            print("ptaPrio:",PTA_PIN_CONFIG["PTA_PRIO_PIN"])
            #set the pin config
            handlePtaPrioPinSetting(ptaprio)
        else:
            PTA_PIN_CONFIG.update({"PTA_PRIO_PIN": ''})
        
    elif symbolID == "PTA_WLAN_ACTIVE_PIN":
        clearPtaPinSetting(PTA_PIN_CONFIG["WLAN_ACTIVE_PIN"],"WLAN_ACTIVE")
        pin_num = symbol.getKeyValue(value)
        print('wlanActive:',pin_num)
        if pin_num != '':
            wlanactive = 'BSP_PIN_'+str(pin_num)
            PTA_PIN_CONFIG.update({"WLAN_ACTIVE_PIN":wlanactive}) 
            print("WlanActive:",PTA_PIN_CONFIG["WLAN_ACTIVE_PIN"])
            #set the pin config
            handlePtaWlanActiveSetting(wlanactive)
        else:
            PTA_PIN_CONFIG.update({"WLAN_ACTIVE_PIN": ''})
               

global phyPTASupportEnable
phyPTASupportEnable = libBTZBCore.createBooleanSymbol("PHY_PTA_SUPPORTED", None)
phyPTASupportEnable.setReadOnly(True)
phyPTASupportEnable.setLabel("PTA Support Required for 802.15.4 PHY Stack")
phyPTASupportEnable.setDefaultValue(False)
phyPTASupportEnable.setVisible(False)
phyPTASupportEnable.setDependencies(handlePTA_Support,["IEEE_802154_PHY_LOADED"])

global blePTASupportEnable
blePTASupportEnable = libBTZBCore.createBooleanSymbol("BLE_PTA_SUPPORTED", None)
blePTASupportEnable.setReadOnly(True)
blePTASupportEnable.setLabel("PTA Support Required for BLE Stack")
blePTASupportEnable.setDefaultValue(False)
blePTASupportEnable.setVisible(False)
phyPTASupportEnable.setDependencies(handlePTA_Support,["BLESTACK_LOADED"])

global EnablePta
EnablePta = libBTZBCore.createBooleanSymbol("PTA_ENABLE",None)
EnablePta.setLabel("Enable PTA CoEx")
EnablePta.setVisible(True)
EnablePta.setDefaultValue(False)

global ptaInterface
ptaInterface = libBTZBCore.createKeyValueSetSymbol("PTA_INTERFACE",EnablePta)
ptaInterface.setLabel("PTA Interface")
ptaInterface.addKey("3-Wire", "3-Wire", "3-Wire")
ptaInterface.addKey("2-Wire", "2-Wire", "2-Wire")
ptaInterface.setDefaultValue(0)
ptaInterface.setOutputMode("Value")
ptaInterface.setDisplayMode("Description")
ptaInterface.setDescription("PHY PTA Interface Line")
ptaInterface.setVisible(False)
ptaInterface.setReadOnly(True)
ptaInterface.setDependencies(ptaConfigurationCallback,["PTA_ENABLE","PTA_INTERFACE"])

pta_symbols.append(ptaInterface)

availablePinDictionary = {}

# Send message to core to get available pins
availablePinDictionary = Database.sendMessage("core", "PIN_LIST", availablePinDictionary)

global ptaReqPin
ptaReqPin = libBTZBCore.createKeyValueSetSymbol("PTA_REQ_PIN",EnablePta)
ptaReqPin.setVisible(False)
ptaReqPin.setLabel("PTA_Req Pin")
ptaReqPin.setOutputMode("Key")
ptaReqPin.setDisplayMode("Description")
ptaReqPin.addKey("", "", "")
# ptaReqPin.setDefaultValue(0)
ptaReqPin.setDependencies(ptaConfigurationCallback,["PTA_REQ_PIN"])

pta_symbols.append(ptaReqPin)


global ptaPriorityPin
ptaPriorityPin = libBTZBCore.createKeyValueSetSymbol("PTA_PRIORITY_PIN",EnablePta)
ptaPriorityPin.setVisible(False)
ptaPriorityPin.setLabel("PTA_Priority Pin")
ptaPriorityPin.setOutputMode("Key")
ptaPriorityPin.setDisplayMode("Description")
ptaPriorityPin.addKey("", "", "")
# ptaPriorityPin.setDefaultValue(0)
ptaPriorityPin.setDependencies(ptaConfigurationCallback,["PTA_PRIORITY_PIN"])

pta_symbols.append(ptaPriorityPin)


global ptaWlanActivePin
ptaWlanActivePin = libBTZBCore.createKeyValueSetSymbol("PTA_WLAN_ACTIVE_PIN",EnablePta)
ptaWlanActivePin.setVisible(False)
ptaWlanActivePin.setLabel("WLAN_Active Pin")
ptaWlanActivePin.setOutputMode("Key")
ptaWlanActivePin.setDisplayMode("Description")
ptaWlanActivePin.addKey("", "", "")
# ptaWlanActivePin.setDefaultValue(0)
ptaWlanActivePin.setDependencies(ptaConfigurationCallback,["PTA_WLAN_ACTIVE_PIN"])

pta_symbols.append(ptaWlanActivePin)

print("availablePinDictionary",availablePinDictionary)

iter = 0
for pad in sort_alphanumeric(availablePinDictionary.values()):
    iter+=1
    key = pad
    # print("key:",key)
    value = list(availablePinDictionary.keys())[list(availablePinDictionary.values()).index(pad)]
    # print("Value:",value)
    description = pad
    ptaReqPin.addKey(key, value, description)
    ptaWlanActivePin.addKey(key, value, description)
    ptaPriorityPin.addKey(key, value, description)

    if deviceName == 'PIC32WM_BW1':
        if value == '40':
            ptaReqPin.setDefaultValue(iter)
            PTA_PIN_CONFIG.update({"PTA_REQ_PIN":'BSP_PIN_17'})
        if value == '42':
            ptaPriorityPin.setDefaultValue(iter)
            PTA_PIN_CONFIG.update({"PTA_PRIO_PIN":'BSP_PIN_16'})
        if value == '43':
            ptaWlanActivePin.setDefaultValue(iter)
            PTA_PIN_CONFIG.update({"WLAN_ACTIVE_PIN":'BSP_PIN_30'})
    elif (deviceName in pic32cx_bz2_family):
        if value == '34':
            ptaReqPin.setDefaultValue(iter)
            PTA_PIN_CONFIG.update({"PTA_REQ_PIN":'BSP_PIN_34'})
        if value == '33':
            ptaPriorityPin.setDefaultValue(iter)
            PTA_PIN_CONFIG.update({"PTA_PRIO_PIN":'BSP_PIN_33'})
        if value == '4':
            ptaWlanActivePin.setDefaultValue(iter)
            PTA_PIN_CONFIG.update({"WLAN_ACTIVE_PIN":'BSP_PIN_4'})        
    elif ((deviceName in pic32cx_bz3_family)or (deviceName in pic32cx_bz36_family)):
        if value == '36':
            ptaReqPin.setDefaultValue(iter)
            PTA_PIN_CONFIG.update({"PTA_REQ_PIN":'BSP_PIN_36'})
        if value == '30':
            ptaPriorityPin.setDefaultValue(iter)
            PTA_PIN_CONFIG.update({"PTA_PRIO_PIN":'BSP_PIN_30'})
        if value == '29':
            ptaWlanActivePin.setDefaultValue(iter)
            PTA_PIN_CONFIG.update({"WLAN_ACTIVE_PIN":'BSP_PIN_29'})
    elif (deviceName in pic32cx_bz6_family):
        if value == '40':
            ptaReqPin.setDefaultValue(iter)
            PTA_PIN_CONFIG.update({"PTA_REQ_PIN":'BSP_PIN_40'})
        if value == '22':
            ptaPriorityPin.setDefaultValue(iter)
            PTA_PIN_CONFIG.update({"PTA_PRIO_PIN":'BSP_PIN_22'})
        if value == '30':
            ptaWlanActivePin.setDefaultValue(iter)
            PTA_PIN_CONFIG.update({"WLAN_ACTIVE_PIN":'BSP_PIN_30'})

# handlePtaReqPinSetting(PTA_PIN_CONFIG["PTA_REQ_PIN"])
# handlePtaPrioPinSetting(PTA_PIN_CONFIG["PTA_PRIO_PIN"])
# handlePtaWlanActiveSetting(PTA_PIN_CONFIG["PTA_PRIO_PIN"])



global ptaSourceFile
ptaSourceFile = libBTZBCore.createFileSymbol('PTA_C_FILE',None)
ptaSourceFile.setSourcePath("/driver/pic32cx-bz/templates/pta/pta.c.ftl")
ptaSourceFile.setOutputName("pta.c")
ptaSourceFile.setDestPath('driver/pta')
ptaSourceFile.setProjectPath('config/'+configName+'/driver/pta/pta.c')
ptaSourceFile.setType("SOURCE")
ptaSourceFile.setOverwrite(True)
ptaSourceFile.setMarkup(True)
ptaSourceFile.setEnabled(False)

ptaFileSymbls.append(ptaSourceFile)

global ptaHeaderFile
ptaHeaderFile = libBTZBCore.createFileSymbol('PTA_H_FILE',None)
ptaHeaderFile.setSourcePath("/driver/pic32cx-bz/templates/pta/pta.h.ftl")
ptaHeaderFile.setOutputName("pta.h")
ptaHeaderFile.setDestPath('driver/pta')
ptaHeaderFile.setProjectPath('config/'+configName+'/driver/pta/pta.h')
ptaHeaderFile.setType("HEADER")
ptaHeaderFile.setOverwrite(True)
ptaHeaderFile.setMarkup(True)
ptaHeaderFile.setEnabled(False)

ptaFileSymbls.append(ptaHeaderFile)

global ptaFilePathC
ptaFilePathC = libBTZBCore.createSettingSymbol("PTA_FILE_PATH_C", None)
ptaFilePathC.setValue("../src/config/" + configName + "/driver/pta;")
ptaFilePathC.setCategory("C32")
ptaFilePathC.setKey("extra-include-directories")
ptaFilePathC.setAppend(True, ";")
ptaFilePathC.setEnabled(False)

ptaFileSymbls.append(ptaFilePathC)

global ptaFilePathCPP
ptaFilePathCPP = libBTZBCore.createSettingSymbol("PTA_FILE_PATH_CPP", None)
ptaFilePathCPP.setValue("../src/config/" + configName + "/driver/pta;")
ptaFilePathCPP.setCategory("C32PP")
ptaFilePathCPP.setKey("extra-include-directories")
ptaFilePathCPP.setAppend(True, ";")
ptaFilePathCPP.setEnabled(False)

ptaFileSymbls.append(ptaFilePathCPP)
