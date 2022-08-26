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

import struct
from javax.swing import JPanel, JLabel, JFrame, JTextField, BoxLayout, JCheckBox, JButton,JFileChooser
from javax.swing import JOptionPane, GroupLayout, JComboBox, JFormattedTextField, JSeparator
from java.awt import BorderLayout
from java.text import DecimalFormat
import commands
import sys
import os.path
from os import path
from intelhex import IntelHex
import array
import hashlib
import binascii

from javax.crypto import Cipher
from javax.crypto.spec import IvParameterSpec, SecretKeySpec
from javax.swing.text import MaskFormatter
from java.awt.event import MouseAdapter
from javax.swing import ImageIcon


bsOpt = None
g_confName = None
zotaOpt = None

global_header_start_address = 0x1000000
global_header_size = 0x200
global_crop_start_address =   0x1000200
global_crop_end_address = 0x1080000  

g_private_key_file = ''
#g_signed_fw_file = 'fw_image.bin'
g_encrypt_fw_file = 'image_with_header.img'
g_project_fw_file = ' '

g4_seq_num = 0x01
g1_md_rev = 1
g1_cont_idx = 1
g4_identifier = 'PHCM'
g1_auth_mthd = 0
g1_auth_key = 0
gl_dec_mthd = 0
gl_dec_key = 0
g2_len = 116 

g4_fw_img_rev = bytearray(b'\x01\x00\x00\x00')
g4_fw_img_len = 0
g1_fw_img_dec_mthd = 0
g1_fw_img_dec_key = 0
g96_fw_img_signature = bytearray(b'\x00') * 96

g284_filler = bytearray(b'\x00') * 284
g96_md_signature = bytearray(b'\x00') * 96

g_metaheader = bytearray(b'\x00') * 512

g_cfg_seq = 0xFFEEDDBB
g_cfg_auth = 'None'
g_cfg_fw_rev = '00000001'
g_aes_key = bytearray(b'\xe5\x46\x37\x28') * 4
g_iv = bytearray(b'\x00') * 16
g_cfg_outputfiletypes = 'Signed Binary'

g_img_src_addr = 0
g_img_dst_addr = 0

g_img_bytes = None


g_zota_header = bytearray(b'\x00')*69
g_zota_file_identifier = 0x0BEEF11E
g_zota_header_version = '0x0100'
g_zota_header_length = 56
g_zota_field_control = 0
g_zota_manufacture_code = '0xFFFF'
g_zota_image_type = '0xFFFF'
g_zota_file_version = '0x00000000'
g_zota_zigbee_stack_version = '0x0002'
g_zota_header_string = 'MCHP'
g_zota_total_image_size = 0
g_zota_security_credential_version = '0x00'
g_zota_security_credential_version_check = False
g_zota_upgrade_file_destination = '0x0000000000000000'
g_zota_upgrade_file_destination_check = False
g_zota_minimum_hardware_version = '0x0000'
g_zota_maximum_hardware_version = '0x0000'
g_zota_hardware_version_check = False

g_cfg_outputfile = 'OTAPackage.bin'
g_cfg_outputfiletypes = 'BLE OTA File'
g_cfg_outputEncryption = 'Encrypted'


g_bota_header = bytearray(b'\x00')*16
g_bota_header_ver = 1
g_bota_encryption = 1
g_bota_checksum = 0
g_bota_file_type = 1



gframe = None

def header_copyright():
    print("Header GUI v1.01 (c) 12/1/2021 Microchip Technology All Rights Reserved")
def ota_copyright():
    print("Over The Air Package Maker GUI v1.01 (c) 12/1/2021 Microchip Technology All Rights Reserved")
    

# given a binary_value integer between 0:255, return
# the equivalent negative number
def from_unsigned_to_signed_byte(unsigned_value):
  if unsigned_value  > 127:
    return unsigned_value  - 256
  return unsigned_value

# given a signed_value between -128:127, return
# the equivalent positive number
def from_signed_to_unsigned_byte(signed_value):
  if signed_value  < 0:
    return signed_value  + 256
  return signed_value
   
# transform a list of unsigned values to a list of signed values 
def from_unsigned_list_to_signed(list_of_unsigned_values):
  return [from_unsigned_to_signed_byte(i) for i in list_of_unsigned_values]

# transform a list of signed values to a list of unsigned values 
def from_signed_list_to_unsigned(list_of_signed_values):
  return [from_signed_to_unsigned_byte(i) for i in list_of_signed_values]
    

def read_config_file():
    global g_cfg_seq 
    global g_cfg_auth
    global g_cfg_fw_rev
    global g_private_key_file
    global g_img_src_addr
    global g_img_dst_addr
    global g4_seq_num
    global g1_auth_mthd
    global g4_fw_img_rev
    global g_cfg_outputfiletypes
    global g_cfg_outputfile
    global g_cfg_outputEncryption
    
    global g_zota_file_identifier 
    global g_zota_header_version
    global g_zota_header_length
    global g_zota_field_control
    global g_zota_manufacture_code
    global g_zota_image_type
    global g_zota_file_version
    global g_zota_zigbee_stack_version
    global g_zota_header_string
    global g_zota_total_image_size
    global g_zota_security_credential_version
    global g_zota_upgrade_file_destination
    global g_zota_minimum_hardware_version
    global g_zota_maximum_hardware_version
    global g_zota_security_credential_version_check
    global g_zota_upgrade_file_destination_check
    global g_zota_hardware_version_check
    
    g_cfg_seq = settings.getString("configuration.header.sequence", '0x00000002')
    data = g_cfg_seq[:10]
    g4_seq_num = int(data,16) 
    if( (g4_seq_num == 0) or (g4_seq_num>=0xFFFFFFFF) ):
        dialog("Invalid Sequence Number", True)
        return 1
    g_cfg_auth = settings.getString("configuration.header.auth", 'None')
    if( 'None' in g_cfg_auth ):
        g1_auth_mthd = 0
    if( 'ECDSA p256+SHA256' in g_cfg_auth ):
        g1_auth_mthd = 1
    if( 'ECDSA p384+SHA384' in g_cfg_auth ):
        g1_auth_mthd = 2
    g_cfg_fw_rev = settings.getString("configuration.header.fw_rev", "1.0")
    rev = [int(x) for x in g_cfg_fw_rev.split('.')]
    g4_fw_img_rev = bytearray(b'\x00') * 4
    if (len(rev) > 4 ):
        revlen = 4
    else:
        revlen = len(rev)
    g4_fw_img_rev[0:revlen] = rev[0:revlen]
    g4_fw_img_rev.reverse()
    g_private_key_file = settings.getString("configuration.header.key_file", None)
    #g_signed_fw_file = settings.getString("configuration.header.signed_fw_file", 'fw_image.bin')
    aes_key_str = settings.getString("configuration.header.aes_key", '0xaabbccddeeff00112233445566778899')
    g_aes_key = bytearray.fromhex(aes_key_str[2:])
    iv_str = settings.getString("configuration.header.iv", '0x00000000000000000000000000000000')
    g_iv = bytearray.fromhex(iv_str[2:])

    g_img_src_addr = 0x01000200
    g_img_dst_addr = 0x01000200
    
    g_cfg_outputfile = settings.getString("configuration.header.outputfilename", 'OTAPackage.bin')
    g_cfg_outputfiletypes = settings.getString("configuration.header.outputfiletypes", 'BLE OTA File')
    g_cfg_outputEncryption = settings.getString("configuration.header.outputEncryption", 'Unencrypted')
    g_zota_manufacture_code = settings.getString("configuration.header.zota_manufacture_code", '0xFFFF')
    g_zota_image_type = settings.getString("configuration.header.zota_image_type", '0xFFFF')
    g_zota_file_version = settings.getString("configuration.header.zota_file_version", '0x00000000')
    g_zota_zigbee_stack_version = settings.getString("configuration.header.zota_zigbee_stack_version", '0x0002')
    g_zota_header_string = settings.getString("configuration.header.zota_header_string", None)
    if (g_zota_header_string == None):
        g_zota_header_string = bytearray(b'\x00')*32
        g_zota_header_string[0:4] = 'MCHP'
    g_zota_security_credential_version = settings.getString("configuration.header.zota_security_credential_version", '0x00')
    g_zota_security_credential_version_check = False
    security_credential_version_check = settings.getString("configuration.header.zota_security_credential_version_check", 'False')
    if ('True' in security_credential_version_check):
        g_zota_security_credential_version_check = True
    g_zota_upgrade_file_destination = settings.getString("configuration.header.zota_upgrade_file_destination", '0x0000000000000000')
    g_zota_upgrade_file_destination_check = False
    upgrade_file_destination_check = settings.getString("configuration.header.zota_upgrade_file_destination_check", 'False')
    if ('True' in upgrade_file_destination_check):
        g_zota_upgrade_file_destination_check = True
    g_zota_minimum_hardware_version = settings.getString("configuration.header.zota_minimum_hardware_version", '0x0000')
    g_zota_maximum_hardware_version = settings.getString("configuration.header.zota_maximum_hardware_version", '0x0000')
    g_zota_hardware_version_check = False
    hardware_version_check = settings.getString("configuration.header.zota_hardware_version_check", 'False')
    if ('True' in hardware_version_check ):
        g_zota_hardware_version_check = True
    
    

def write_header_config_file():
    global bsOpt

    data = bsOpt.seqTxt.getText()
    data = data[:10]
    settings.setString("configuration.header.sequence", data)
    settings.setString("configuration.header.auth", bsOpt.AuthMethodList.getSelectedItem())
    settings.setString("configuration.header.fw_rev", bsOpt.FWRevTxt.getText())
    settings.setString("configuration.header.key_file", bsOpt.PrivateKeyTxt.getText())


def write_ota_config_file():
    global zotaOpt

    settings.setString("configuration.header.outputfilename", zotaOpt.OutputFileTxt.getText())
    settings.setString("configuration.header.outputfiletypes", zotaOpt.OutputFileTypesList.getSelectedItem())
    settings.setString("configuration.header.outputEncryption", zotaOpt.OutputEncryptionList.getSelectedItem())
    
    settings.setString("configuration.header.zota_manufacture_code", zotaOpt.manuCodeTxt.getText())
    settings.setString("configuration.header.zota_image_type", zotaOpt.imageTypeTxt.getText())
    settings.setString("configuration.header.zota_file_version", zotaOpt.fileVersionTxt.getText())
    settings.setString("configuration.header.zota_zigbee_stack_version", zotaOpt.zigbeeStackVersionTxt.getText())
    settings.setString("configuration.header.zota_header_string", zotaOpt.headerStringTxt.getText())
    if zotaOpt.security_credential_version_checkbox.isSelected():
        settings.setString("configuration.header.zota_security_credential_version", zotaOpt.securityCredentialVersionTxt.getText())
    settings.setString("configuration.header.zota_security_credential_version_check", str(zotaOpt.security_credential_version_checkbox.isSelected()))
    if zotaOpt.upgrade_file_destination_checkbox.isSelected():
        settings.setString("configuration.header.zota_upgrade_file_destination", zotaOpt.upgradeFileDestinationTxt.getText())
    settings.setString("configuration.header.zota_upgrade_file_destination_check", str(zotaOpt.upgrade_file_destination_checkbox.isSelected()))
    if zotaOpt.hardware_version_checkbox.isSelected():  
        settings.setString("configuration.header.zota_minimum_hardware_version", zotaOpt.minimumHardwareVersionTxt.getText())
        settings.setString("configuration.header.zota_maximum_hardware_version", zotaOpt.maximumHardwareVersionTxt.getText())
    settings.setString("configuration.header.zota_hardware_version_check", str(zotaOpt.hardware_version_checkbox.isSelected()))
    settings.setString("configuration.header.aes_key", zotaOpt.AESKeyTxt.getText())
    settings.setString("configuration.header.iv", zotaOpt.IVTxt.getText())  

    
def set_global_metadata_header_config():
    global bsOpt
    global g4_seq_num
    global g4_identifier
    global g1_auth_mthd
    global g4_fw_img_rev
    global g_private_key_file
    #global g_signed_fw_file
    #global g_encrypt_fw_file
    
    data = bsOpt.seqTxt.getText()
    data = data[:10]
    g4_seq_num = int(data,16) 
    if( (g4_seq_num == 0) or (g4_seq_num>=0xFFFFFFFF) ):
        dialog("Invalid Sequence Number", True)
        return 1
    
    g1_auth_mthd = bsOpt.AuthMethodList.getSelectedIndex()
    
    data = bsOpt.FWRevTxt.getText()
    rev = [int(x) for x in data.split('.')]
    g4_fw_img_rev = bytearray(b'\x00') * 4
    if (len(rev) > 4 ):
        revlen = 4
    else:
        revlen = len(rev)
    g4_fw_img_rev[0:revlen] = rev[0:revlen]
    g4_fw_img_rev.reverse()
    g_private_key_file = bsOpt.PrivateKeyTxt.getText()
    #g_signed_fw_file = bsOpt.SignedFWTxt.getText()
    return 0

    

class HeaderPane():
    
    def __init__(self):
        self.panel = JPanel()
        self.panel.setLayout(BorderLayout())
        
        self.pane = JPanel()
        self.initUI()

    def initUI(self):
        global g_cfg_seq 
        global g_cfg_auth
        global g_cfg_fw_rev
        global g_aes_key
        global g_iv
        global g_private_key_file
        global gframe
        
        header_copyright()
		
        gframe = JFrame("Help Info")
        gframe.setLocation(100,100)
        gframe.setSize(400,300)
        gframe.setLocationRelativeTo(None)
        gframe.setLayout(BorderLayout())
        
        layout = GroupLayout(self.pane)
        self.pane.setLayout(layout)
        layout.setAutoCreateGaps(True)
        layout.setAutoCreateContainerGaps(True)

        read_config_file()

        path   = ide.expandProjectMacrosEx("${ProjectName}", g_confName, "${ProjectDir}", False)
        infoImg = ImageIcon(path + "\\info-16.png")
        
        seqLabel = JLabel("MD_SEQ_NUM:")
        seqLabel.setHorizontalTextPosition(JLabel.LEADING)
        seqLabel.setIcon(infoImg)
        seqLabel.addMouseListener(seqMouseListener())
        Hexformat1 = MaskFormatter('0xHHHHHHHH')
        Hexformat1.setValidCharacters('0123456789abcdefABCDEF-h')
        self.seqTxt = JFormattedTextField(Hexformat1)
        self.seqTxt.setText(g_cfg_seq)
        
        AuthMethodLabel = JLabel("AUTH_MTHD:")
        AuthMethodLabel.setHorizontalTextPosition(JLabel.LEADING)
        AuthMethodLabel.setIcon(infoImg)
        AuthMethodLabel.addMouseListener(AuthMethodMouseListener())
        self.AuthMethod_items = ("None", "ECDSA p256+SHA256", "ECDSA p384+SHA384")
        self.AuthMethodList = JComboBox(self.AuthMethod_items)
        self.AuthMethodList.setSelectedItem(g_cfg_auth)
        self.AuthMethodList.addItemListener(self.AuthMethodListListener)

        FWRevLabel = JLabel("FW_IMG_REV:")
        FWRevLabel.setHorizontalTextPosition(JLabel.LEADING)
        FWRevLabel.setIcon(infoImg)
        FWRevLabel.addMouseListener(FWRevMouseListener())
        self.FWRevTxt = JTextField()
        self.FWRevTxt.setText(g_cfg_fw_rev)
        
        self.PrivateKeyLabel = JLabel("Private Key File:")
        self.PrivateKeyLabel.setHorizontalTextPosition(JLabel.LEADING)
        self.PrivateKeyLabel.setIcon(infoImg)
        self.PrivateKeyLabel.addMouseListener(PrivateKeyMouseListener())
        self.PrivateKeyTxt = JTextField()
        self.PrivateKeyTxt.setText(g_private_key_file)
        self.PrivateKeyBut = JButton('Select Key File',actionPerformed=self.selectkeyfile)
        if( 'None' in g_cfg_auth ):
            self.PrivateKeyLabel.setVisible(False)
            self.PrivateKeyTxt.setVisible(False)
            self.PrivateKeyBut.setVisible(False)
        else:
            self.PrivateKeyLabel.setVisible(True)
            self.PrivateKeyTxt.setVisible(True)
            self.PrivateKeyBut.setVisible(True)
            
        emptyLabel = JLabel(" ")
        
        layout.setHorizontalGroup(layout.createSequentialGroup()
            .addGroup(layout.createParallelGroup()
                .addComponent(seqLabel)
                .addComponent(AuthMethodLabel)
                .addComponent(FWRevLabel)
                .addComponent(self.PrivateKeyLabel)
                .addComponent(emptyLabel)
                )
            .addGroup(layout.createParallelGroup()
                .addComponent(self.seqTxt)
                .addComponent(self.AuthMethodList)
                .addComponent(self.FWRevTxt)
                .addComponent(self.PrivateKeyTxt)
                )
            .addGroup(layout.createParallelGroup()
                .addComponent(self.PrivateKeyBut)
                )
        )
        
        layout.setVerticalGroup(layout.createSequentialGroup()
            .addGroup(layout.createParallelGroup()
                .addComponent(seqLabel)
                .addComponent(self.seqTxt, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE,GroupLayout.PREFERRED_SIZE)
            )
            .addGroup(layout.createParallelGroup()
                .addComponent(AuthMethodLabel)
                .addComponent(self.AuthMethodList, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE,GroupLayout.PREFERRED_SIZE)
            )
            .addGroup(layout.createParallelGroup()
                .addComponent(FWRevLabel)
                .addComponent(self.FWRevTxt, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE,GroupLayout.PREFERRED_SIZE)
            )
            .addGroup(layout.createParallelGroup()
                .addComponent(self.PrivateKeyLabel)
                .addComponent(self.PrivateKeyTxt, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE,GroupLayout.PREFERRED_SIZE)
                .addComponent(self.PrivateKeyBut, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE,GroupLayout.PREFERRED_SIZE)
            )
            .addGroup(layout.createParallelGroup()
                .addComponent(emptyLabel)
            )
        )
        self.panel.add(self.pane,BorderLayout.CENTER)

    def getPanel(self):
        return self.panel

    def selectkeyfile(self,event):
        global g_private_key_file
        
        directory = ide.expandProjectMacrosEx("${ProjectName}", None, "${ProjectDir}", False)
        choseFile = JFileChooser(directory)
        choseFile.setDialogTitle('Select Private Key file for signing the firmware/metadata')
        ret = choseFile.showSaveDialog(self.panel)
        if ret == JFileChooser.APPROVE_OPTION:
            g_private_key_file = choseFile.getSelectedFile().getAbsolutePath()
            self.PrivateKeyTxt.setText(g_private_key_file)
    
    def AuthMethodListListener(self, event):
        selectedItem = self.AuthMethodList.getSelectedItem()
        if( 'None' in selectedItem ):
            self.PrivateKeyLabel.setVisible(False)
            self.PrivateKeyTxt.setVisible(False)
            self.PrivateKeyBut.setVisible(False)
        else:
            self.PrivateKeyLabel.setVisible(True)
            self.PrivateKeyTxt.setVisible(True)
            self.PrivateKeyBut.setVisible(True)
        return
 
    def signFW(self, event):
        global g_confName
        global g_cfg_outputfiletypes
        
        write_header_config_file()
        read_config_file()
        
        if ( 0 == set_global_metadata_header_config() ) :
            ret = create_signed_image(g_confName)
        if (ret == 0):
            if( "Encrypted" in g_cfg_outputfiletypes ):
                create_encrypt_image(g_confName)
                dialog_text = "Encrypted Signed binary file " + g_project_fw_file + ".encrypt.signed.bin was Created Successfully"
            elif( "Hex" in g_cfg_outputfiletypes ):
                create_hex_file(g_confName)
                dialog_text = "Signed hex file " + g_project_fw_file + ".signed.hex was Created Successfully"
            else:
                dialog_text = "Signed binary file " + g_project_fw_file + ".signed.bin was Created Successfully"
                
        dialog(dialog_text, False)

        return

def mplab_configure_Header(confName):
    global bsOpt

    if bsOpt == None:
        bsOpt=HeaderPane()
        g_confName = confName

    return bsOpt.getPanel()


def save_mplab_configure_Header(confName):
    global bsOpt
    
    if bsOpt == None:
        return

    write_header_config_file()
    return

class seqMouseListener(MouseAdapter):
    def mousePressed(self, event):
        JOptionPane.showMessageDialog(gframe, 
                              "Sequence Number in 64bit Hex format, range from 0x00000001 to 0xFFFFFFFE", 
                              "Sequence Number Help", 
                              JOptionPane.INFORMATION_MESSAGE)

class AuthMethodMouseListener(MouseAdapter):
    def mousePressed(self, event):
        JOptionPane.showMessageDialog(gframe, 
                              "Authentication Method, choose from None, ECDSA p256+SHA256 and ECDSA p384+SHA384", 
                              "Authentication Method Help", 
                              JOptionPane.INFORMATION_MESSAGE)

class FWRevMouseListener(MouseAdapter):
    def mousePressed(self, event):
        JOptionPane.showMessageDialog(gframe, 
                              "Firmware Revision in the format of x.x.x.x, where x is value in range 0-255", 
                              "Firmware Revision Help", 
                              JOptionPane.INFORMATION_MESSAGE)

class PrivateKeyMouseListener(MouseAdapter):
    def mousePressed(self, event):
        JOptionPane.showMessageDialog(gframe, 
                              "Choose the Private Key File in PKCS#8 fromat for ECDSA authentication", 
                              "Private Key File Selection Help", 
                              JOptionPane.INFORMATION_MESSAGE)








class OTAPane():
    
    def __init__(self):
        self.panel = JPanel()
        self.panel.setLayout(BorderLayout())
        
        self.pane = JPanel()
        self.initUI()

    def initUI(self):
        global g_zota_file_identifier
        global g_zota_header_version
        global g_zota_header_length
        global g_zota_field_control
        global g_zota_manufacture_code
        global g_zota_image_type
        global g_zota_file_version
        global g_zota_zigbee_stack_version
        global g_zota_header_string
        global g_zota_total_image_size
        global g_zota_security_credential_version
        global g_zota_upgrade_file_destination
        global g_zota_minimum_hardware_version
        global g_zota_maximum_hardware_version
        global g_zota_security_credential_version_check
        global g_zota_upgrade_file_destination_check
        global g_zota_hardware_version_check
        global g_cfg_outputfiletypes
        global g_cfg_outputEncryption
        
        ota_copyright()
        
        layout = GroupLayout(self.pane)
        self.pane.setLayout(layout)
        layout.setAutoCreateGaps(True)
        layout.setAutoCreateContainerGaps(True)

        read_config_file()
        
        path   = ide.expandProjectMacrosEx("${ProjectName}", g_confName, "${ProjectDir}", False)
        infoImg = ImageIcon(path + "\\info-16.png")
        
        OutputFileLabel = JLabel("Output File Name:")
        OutputFileLabel.setHorizontalTextPosition(JLabel.LEADING)
        OutputFileLabel.setIcon(infoImg)          
        OutputFileLabel.addMouseListener(OutputFileMouseListener())
        self.OutputFileTxt = JTextField()
        self.OutputFileTxt.setText(g_cfg_outputfile)
        
        OutputTypeLabel = JLabel("Output File Type:")
        OutputTypeLabel.setHorizontalTextPosition(JLabel.LEADING)
        OutputTypeLabel.setIcon(infoImg)         
        OutputTypeLabel.addMouseListener(OutputTypeMouseListener())
        self.OutputFileTypes_items = ("BLE OTA File", "Zigbee OTA File", "Combo OTA File")
        self.OutputFileTypesList = JComboBox(self.OutputFileTypes_items)
        self.OutputFileTypesList.setSelectedItem(g_cfg_outputfiletypes)
        self.OutputFileTypesList.addItemListener(self.OutputFileTypesListListener)        
        
        OutputEncryptionLabel = JLabel("Output File Encryption:")
        OutputEncryptionLabel.setHorizontalTextPosition(JLabel.LEADING)
        OutputEncryptionLabel.setIcon(infoImg)          
        OutputEncryptionLabel.addMouseListener(OutputEncryptionMouseListener())
        self.OutputEncryption_items = ("Unencrypted", "Encrypted")
        self.OutputEncryptionList = JComboBox(self.OutputEncryption_items)
        self.OutputEncryptionList.setSelectedItem(g_cfg_outputEncryption)
        self.OutputEncryptionList.addItemListener(self.OutputEncryptionListListener)
        
        zigbee_header = False
        if( "Zigbee" in g_cfg_outputfiletypes ):
            zigbee_header = True
        image_encryption = True
        if( "Unencrypted" in g_cfg_outputEncryption):
            image_encryption = False

        Hexformat8 = MaskFormatter('0xHH')
        Hexformat8.setValidCharacters('0123456789abcdefABCDEF-h')
        Hexformat16 = MaskFormatter('0xHHHH')
        Hexformat16.setValidCharacters('0123456789abcdefABCDEF-h')
        Hexformat32 = MaskFormatter('0xHHHHHHHH')
        Hexformat32.setValidCharacters('0123456789abcdefABCDEF-h')
        Hexformat64 = MaskFormatter('0xHHHHHHHHHHHHHHHH')
        Hexformat64.setValidCharacters('0123456789abcdefABCDEF-h')
        Hexformat128 = MaskFormatter('0xHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH')
        Hexformat128.setValidCharacters('0123456789abcdefABCDEF-h')
        
        self.manu_code_Label = JLabel("Manufacture Code:")
        self.manu_code_Label.setHorizontalTextPosition(JLabel.LEADING)
        self.manu_code_Label.setIcon(infoImg)           
        self.manu_code_Label.addMouseListener(manuCodeMouseListener())
        self.manuCodeTxt = JFormattedTextField(Hexformat16)
        self.manuCodeTxt.setText(g_zota_manufacture_code[2:])
        if zigbee_header:
            self.manu_code_Label.setVisible(True)
            self.manuCodeTxt.setVisible(True)
        else:
            self.manu_code_Label.setVisible(False)
            self.manuCodeTxt.setVisible(False)
            
        self.image_type_Label = JLabel("Image Type:")
        self.image_type_Label.setHorizontalTextPosition(JLabel.LEADING)
        self.image_type_Label.setIcon(infoImg)          
        self.image_type_Label.addMouseListener(imageTypeMouseListener())
        self.imageTypeTxt = JFormattedTextField(Hexformat16)
        self.imageTypeTxt.setText(g_zota_image_type)
        if zigbee_header:
            self.image_type_Label.setVisible(True)
            self.imageTypeTxt.setVisible(True)
        else:
            self.image_type_Label.setVisible(False)
            self.imageTypeTxt.setVisible(False)
        
        self.file_version_Label = JLabel("File Version:")
        self.file_version_Label.setHorizontalTextPosition(JLabel.LEADING)
        self.file_version_Label.setIcon(infoImg)          
        self.file_version_Label.addMouseListener(fileVersionMouseListener())
        self.fileVersionTxt = JFormattedTextField(Hexformat32)
        self.fileVersionTxt.setText(g_zota_file_version)
        if zigbee_header:
            self.file_version_Label.setVisible(True)
            self.fileVersionTxt.setVisible(True)
        else:
            self.file_version_Label.setVisible(False)
            self.fileVersionTxt.setVisible(False)
        
        self.zigbee_stack_version_Label = JLabel("Zigbee Stack Version:")
        self.zigbee_stack_version_Label.setHorizontalTextPosition(JLabel.LEADING)
        self.zigbee_stack_version_Label.setIcon(infoImg)          
        self.zigbee_stack_version_Label.addMouseListener(zigbeeStackVersionMouseListener())
        self.zigbeeStackVersionTxt = JFormattedTextField(Hexformat16)
        self.zigbeeStackVersionTxt.setText(g_zota_zigbee_stack_version)
        if zigbee_header:
            self.zigbee_stack_version_Label.setVisible(True)
            self.zigbeeStackVersionTxt.setVisible(True)
        else:
            self.zigbee_stack_version_Label.setVisible(False)
            self.zigbeeStackVersionTxt.setVisible(False)

        self.header_string_Label = JLabel("Header String:")
        self.header_string_Label.setHorizontalTextPosition(JLabel.LEADING)
        self.header_string_Label.setIcon(infoImg)         
        self.header_string_Label.addMouseListener(headerStringMouseListener())
        self.headerStringTxt = JTextField()
        self.headerStringTxt.setText(str(g_zota_header_string))
        if zigbee_header:
            self.header_string_Label.setVisible(True)
            self.headerStringTxt.setVisible(True)
        else:
            self.header_string_Label.setVisible(False)
            self.headerStringTxt.setVisible(False)
        
        self.security_credential_version_Label = JLabel("Security Credential Version:")
        self.security_credential_version_Label.setHorizontalTextPosition(JLabel.LEADING)
        self.security_credential_version_Label.setIcon(infoImg)          
        self.security_credential_version_Label.addMouseListener(securityCredentialVersionMouseListener())
        self.securityCredentialVersionTxt = JFormattedTextField(Hexformat8)
        self.securityCredentialVersionTxt.setText(g_zota_security_credential_version)
        self.security_credential_version_checkbox = JCheckBox()
        self.security_credential_version_checkbox.setSelected(g_zota_security_credential_version_check)
        self.security_credential_version_checkbox.addActionListener(self.security_credential_version_listener)
        if zigbee_header:
            self.security_credential_version_Label.setVisible(True)
            self.security_credential_version_checkbox.setVisible(True)
            self.securityCredentialVersionTxt.setVisible(True)
            if g_zota_security_credential_version_check:
                self.securityCredentialVersionTxt.setEnabled(True)
            else:
                self.securityCredentialVersionTxt.setEnabled(False)
        else:
            self.security_credential_version_Label.setVisible(False)
            self.securityCredentialVersionTxt.setVisible(False)
            self.security_credential_version_checkbox.setVisible(False)
        
        self.upgrade_file_destination_Label = JLabel("Upgrade File Destination:")
        self.upgrade_file_destination_Label.setHorizontalTextPosition(JLabel.LEADING)
        self.upgrade_file_destination_Label.setIcon(infoImg)         
        self.upgrade_file_destination_Label.addMouseListener(upgradeFileDestinationMouseListener())
        self.upgradeFileDestinationTxt = JFormattedTextField(Hexformat64)
        self.upgradeFileDestinationTxt.setText(g_zota_upgrade_file_destination)
        self.upgrade_file_destination_checkbox = JCheckBox()
        self.upgrade_file_destination_checkbox.setSelected(g_zota_upgrade_file_destination_check)
        self.upgrade_file_destination_checkbox.addActionListener(self.upgrade_file_destination_listener)
        if zigbee_header:
            self.upgrade_file_destination_Label.setVisible(True)
            self.upgrade_file_destination_checkbox.setVisible(True)
            self.upgradeFileDestinationTxt.setVisible(True)
            if g_zota_upgrade_file_destination_check:
                self.upgradeFileDestinationTxt.setEnabled(True)
            else:
                self.upgradeFileDestinationTxt.setEnabled(False)
        else:
            self.upgrade_file_destination_Label.setVisible(False)
            self.upgrade_file_destination_checkbox.setVisible(False)
            self.upgradeFileDestinationTxt.setVisible(False)
        
        self.hardware_version_checkbox = JCheckBox()
        self.hardware_version_checkbox.setSelected(g_zota_hardware_version_check)
        self.hardware_version_checkbox.addActionListener(self.hardware_version_listener)
        if zigbee_header:
            self.hardware_version_checkbox.setVisible(True)
        else:
            self.hardware_version_checkbox.setVisible(False)
            
        self.min_hardware_version_Label = JLabel("Min Hardware Version:")
        self.min_hardware_version_Label.setHorizontalTextPosition(JLabel.LEADING)
        self.min_hardware_version_Label.setIcon(infoImg)          
        self.min_hardware_version_Label.addMouseListener(minHardwareVersionMouseListener())
        self.minimumHardwareVersionTxt = JFormattedTextField(Hexformat16)
        self.minimumHardwareVersionTxt.setText(g_zota_minimum_hardware_version)
        if g_zota_hardware_version_check:
            self.minimumHardwareVersionTxt.setEnabled(True)
        else:
            self.minimumHardwareVersionTxt.setEnabled(False)
        if zigbee_header:
            self.min_hardware_version_Label.setVisible(True)
            self.minimumHardwareVersionTxt.setVisible(True)
        else:
            self.min_hardware_version_Label.setVisible(False)
            self.minimumHardwareVersionTxt.setVisible(False)
        
        self.max_hardware_version_Label = JLabel("Max Hardware Version:")
        self.max_hardware_version_Label.setHorizontalTextPosition(JLabel.LEADING)
        self.max_hardware_version_Label.setIcon(infoImg)          
        self.max_hardware_version_Label.addMouseListener(maxHardwareVersionMouseListener())
        self.maximumHardwareVersionTxt = JFormattedTextField(Hexformat16)
        self.maximumHardwareVersionTxt.setText(g_zota_maximum_hardware_version)
        if g_zota_hardware_version_check:
            self.maximumHardwareVersionTxt.setEnabled(True)
        else:
            self.maximumHardwareVersionTxt.setEnabled(False)
        if zigbee_header:
            self.max_hardware_version_Label.setVisible(True)
            self.maximumHardwareVersionTxt.setVisible(True)
        else:
            self.max_hardware_version_Label.setVisible(False)
            self.maximumHardwareVersionTxt.setVisible(False)
        
        emptyLabel = JLabel(" ")
        
        self.AESKeyLabel = JLabel("AES Key:")
        self.AESKeyLabel.setHorizontalTextPosition(JLabel.LEADING)
        self.AESKeyLabel.setIcon(infoImg)  
        self.AESKeyLabel.addMouseListener(AESKeyMouseListener())
        self.AESKeyTxt = JFormattedTextField(Hexformat128)
        g_aes_key_txt = binascii.hexlify(g_aes_key)
        self.AESKeyTxt.setText(g_aes_key_txt.zfill(33))
        if image_encryption:
            self.AESKeyLabel.setVisible(True)
            self.AESKeyTxt.setVisible(True)
        else:
            self.AESKeyLabel.setVisible(False)
            self.AESKeyTxt.setVisible(False)
            
        self.IVLabel = JLabel("Init Vector:")
        self.IVLabel.setHorizontalTextPosition(JLabel.LEADING)
        self.IVLabel.setIcon(infoImg)  
        self.IVLabel.addMouseListener(IVMouseListener())
        self.IVTxt = JFormattedTextField(Hexformat128)
        g_iv_text = binascii.hexlify(g_iv)
        self.IVTxt.setText(g_iv_text.zfill(33))
        if image_encryption:
            self.IVLabel.setVisible(True)
            self.IVTxt.setVisible(True)
        else:
            self.IVLabel.setVisible(False)
            self.IVTxt.setVisible(False)
        
        
        self.CreateFileBut = JButton('Create OTA File', actionPerformed=self.CreateOTAFile)
        
        
        layout.setHorizontalGroup(layout.createSequentialGroup()
            .addGroup(layout.createParallelGroup()
                .addComponent(self.manu_code_Label)
                .addComponent(self.image_type_Label)
                .addComponent(self.file_version_Label)
                .addComponent(self.zigbee_stack_version_Label)
                .addComponent(self.header_string_Label)
                .addComponent(self.security_credential_version_Label)
                .addComponent(emptyLabel)
                .addComponent(self.upgrade_file_destination_Label)
                .addComponent(self.min_hardware_version_Label)
                .addComponent(self.max_hardware_version_Label)
                .addComponent(OutputTypeLabel)
                .addComponent(OutputEncryptionLabel)
                .addComponent(self.AESKeyLabel)
                .addComponent(self.IVLabel)
                .addComponent(OutputFileLabel)
                )
            .addGroup(layout.createParallelGroup()
                .addComponent(self.security_credential_version_checkbox)
                .addComponent(self.upgrade_file_destination_checkbox)
                .addComponent(self.hardware_version_checkbox)
                )
            .addGroup(layout.createParallelGroup()
                .addComponent(self.manuCodeTxt)
                .addComponent(self.imageTypeTxt)
                .addComponent(self.fileVersionTxt)
                .addComponent(self.zigbeeStackVersionTxt)
                .addComponent(self.headerStringTxt)
                .addComponent(self.securityCredentialVersionTxt)
                .addComponent(self.upgradeFileDestinationTxt)
                .addComponent(self.minimumHardwareVersionTxt)
                .addComponent(self.maximumHardwareVersionTxt)
                .addComponent(self.OutputFileTypesList)
                .addComponent(self.OutputEncryptionList)
                .addComponent(self.AESKeyTxt)
                .addComponent(self.IVTxt)
                .addComponent(self.OutputFileTxt)
                .addComponent(self.CreateFileBut)
                )
        )
        
        layout.setVerticalGroup(layout.createSequentialGroup()
            .addGroup(layout.createParallelGroup()
                .addComponent(OutputFileLabel)
                .addComponent(self.OutputFileTxt, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE,GroupLayout.PREFERRED_SIZE)
            )
            .addGroup(layout.createParallelGroup()
                .addComponent(emptyLabel)
            )
            .addGroup(layout.createParallelGroup()
                .addComponent(OutputEncryptionLabel)
                .addComponent(self.OutputEncryptionList, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE,GroupLayout.PREFERRED_SIZE)
            )
            .addGroup(layout.createParallelGroup()
                .addComponent(self.AESKeyLabel)
                .addComponent(self.AESKeyTxt, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE,GroupLayout.PREFERRED_SIZE)
            )
            .addGroup(layout.createParallelGroup()
                .addComponent(self.IVLabel)
                .addComponent(self.IVTxt, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE,GroupLayout.PREFERRED_SIZE)
            )
            .addGroup(layout.createParallelGroup()
                .addComponent(emptyLabel)
            )
            .addGroup(layout.createParallelGroup()
                .addComponent(OutputTypeLabel)
                .addComponent(self.OutputFileTypesList, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE,GroupLayout.PREFERRED_SIZE)
            )
            .addGroup(layout.createParallelGroup()
                .addComponent(self.manu_code_Label)
                .addComponent(self.manuCodeTxt, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE,GroupLayout.PREFERRED_SIZE)
            )
            .addGroup(layout.createParallelGroup()
                .addComponent(self.image_type_Label)
                .addComponent(self.imageTypeTxt, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE,GroupLayout.PREFERRED_SIZE)
            )
            .addGroup(layout.createParallelGroup()
                .addComponent(self.file_version_Label)
                .addComponent(self.fileVersionTxt, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE,GroupLayout.PREFERRED_SIZE)
            )
            .addGroup(layout.createParallelGroup()
                .addComponent(self.zigbee_stack_version_Label)
                .addComponent(self.zigbeeStackVersionTxt, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE,GroupLayout.PREFERRED_SIZE)
            )
            .addGroup(layout.createParallelGroup()
                .addComponent(self.header_string_Label)
                .addComponent(self.headerStringTxt, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE,GroupLayout.PREFERRED_SIZE)
            )
            .addGroup(layout.createParallelGroup()
                .addComponent(self.security_credential_version_Label)
                .addComponent(self.security_credential_version_checkbox, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE,GroupLayout.PREFERRED_SIZE)
                .addComponent(self.securityCredentialVersionTxt, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE,GroupLayout.PREFERRED_SIZE)
            )
            .addGroup(layout.createParallelGroup()
                .addComponent(self.upgrade_file_destination_Label)
                .addComponent(self.upgrade_file_destination_checkbox, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE,GroupLayout.PREFERRED_SIZE)
                .addComponent(self.upgradeFileDestinationTxt, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE,GroupLayout.PREFERRED_SIZE)
            )
            .addGroup(layout.createParallelGroup()
                .addComponent(self.min_hardware_version_Label)
                .addComponent(self.hardware_version_checkbox, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE,GroupLayout.PREFERRED_SIZE)
                .addComponent(self.minimumHardwareVersionTxt, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE,GroupLayout.PREFERRED_SIZE)
            )
            .addGroup(layout.createParallelGroup()
                .addComponent(self.max_hardware_version_Label)
                .addComponent(self.maximumHardwareVersionTxt, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE,GroupLayout.PREFERRED_SIZE)
            )
            .addGroup(layout.createParallelGroup()
                .addComponent(emptyLabel)
            )            
            .addGroup(layout.createParallelGroup()
                .addComponent(emptyLabel)
            )
            .addGroup(layout.createParallelGroup()
                .addComponent(self.CreateFileBut, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE,GroupLayout.PREFERRED_SIZE)
            )
        )
        self.panel.add(self.pane,BorderLayout.CENTER)


    def getPanel(self):
        return self.panel
    

    
    def security_credential_version_listener(self, event):
        global g_zota_security_credential_version_check
        
        g_zota_security_credential_version_check = self.security_credential_version_checkbox.isSelected()
        if( g_zota_security_credential_version_check == True ):
            self.securityCredentialVersionTxt.setEnabled(True)
        else:
            self.securityCredentialVersionTxt.setEnabled(False)
        return
        
    def upgrade_file_destination_listener(self, event):
        global g_zota_upgrade_file_destination_check
        
        g_zota_upgrade_file_destination_check = self.upgrade_file_destination_checkbox.isSelected()
        if( g_zota_upgrade_file_destination_check == True ):
            self.upgradeFileDestinationTxt.setEnabled(True)
        else:
            self.upgradeFileDestinationTxt.setEnabled(False)
        return
    
    def hardware_version_listener(self, event):
        global g_zota_hardware_version_check
        
        g_zota_hardware_version_check = self.hardware_version_checkbox.isSelected()
        if( g_zota_hardware_version_check == True ):
            self.minimumHardwareVersionTxt.setEnabled(True)
            self.maximumHardwareVersionTxt.setEnabled(True)
        else:
            self.minimumHardwareVersionTxt.setEnabled(False)
            self.maximumHardwareVersionTxt.setEnabled(False)
        return
    
    def OutputFileTypesListListener(self, event):
        selectedItem = self.OutputFileTypesList.getSelectedItem()
        if( 'Zigbee' in selectedItem or 'Combo' in selectedItem ):
            self.manu_code_Label.setVisible(True)
            self.manuCodeTxt.setVisible(True)
            self.image_type_Label.setVisible(True)
            self.imageTypeTxt.setVisible(True)
            self.file_version_Label.setVisible(True)
            self.fileVersionTxt.setVisible(True)
            self.zigbee_stack_version_Label.setVisible(True)
            self.zigbeeStackVersionTxt.setVisible(True)
            self.header_string_Label.setVisible(True)
            self.headerStringTxt.setVisible(True)
            self.security_credential_version_Label.setVisible(True)
            if( g_zota_security_credential_version_check ):
                self.upgradeFileDestinationTxt.setEnabled(True)
            else:
                self.upgradeFileDestinationTxt.setEnabled(False)
            self.security_credential_version_checkbox.setVisible(True)
            self.upgrade_file_destination_Label.setVisible(True)
            if( g_zota_upgrade_file_destination_check ):
                self.upgradeFileDestinationTxt.setEnabled(True)
            else:
                self.upgradeFileDestinationTxt.setEnabled(False)
            self.upgrade_file_destination_checkbox.setVisible(True)
            self.hardware_version_checkbox.setVisible(True)
            self.min_hardware_version_Label.setVisible(True)
            self.max_hardware_version_Label.setVisible(True)
            self.minimumHardwareVersionTxt.setVisible(True)
            self.maximumHardwareVersionTxt.setVisible(True)
            if (g_zota_hardware_version_check ):
                self.minimumHardwareVersionTxt.setEnabled(True)
                self.maximumHardwareVersionTxt.setEnabled(True)
            else:
                self.minimumHardwareVersionTxt.setEnabled(False)
                self.maximumHardwareVersionTxt.setEnabled(False)
            
        else:
            self.manu_code_Label.setVisible(False)
            self.manuCodeTxt.setVisible(False)
            self.image_type_Label.setVisible(False)
            self.imageTypeTxt.setVisible(False)
            self.file_version_Label.setVisible(False)
            self.fileVersionTxt.setVisible(False)
            self.zigbee_stack_version_Label.setVisible(False)
            self.zigbeeStackVersionTxt.setVisible(False)
            self.header_string_Label.setVisible(False)
            self.headerStringTxt.setVisible(False)
            self.security_credential_version_Label.setVisible(False)
            self.security_credential_version_checkbox.setVisible(False)
            self.securityCredentialVersionTxt.setVisible(False)
            self.upgrade_file_destination_Label.setVisible(False)
            self.upgradeFileDestinationTxt.setVisible(False)
            self.upgrade_file_destination_checkbox.setVisible(False)
            self.hardware_version_checkbox.setVisible(False)
            self.min_hardware_version_Label.setVisible(False)
            self.minimumHardwareVersionTxt.setVisible(False)
            self.max_hardware_version_Label.setVisible(False)
            self.maximumHardwareVersionTxt.setVisible(False)
            
        return

    def OutputEncryptionListListener(self, event):
        selectedItem = self.OutputEncryptionList.getSelectedItem()
        if( 'Unencrypted' in selectedItem ):
            self.AESKeyLabel.setVisible(False)
            self.AESKeyTxt.setVisible(False)
            self.IVLabel.setVisible(False)
            self.IVTxt.setVisible(False)
        else:
            self.AESKeyLabel.setVisible(True)
            self.AESKeyTxt.setVisible(True)
            self.IVLabel.setVisible(True)
            self.IVTxt.setVisible(True)
        return
    
    def CreateOTAFile(self, event):
        global bsOpt
        global g1_md_auth_mthd
        global g4_fw_img_len
        global g1_auth_mthd
        global g_signed_fw_file
        global g_metaheader
        global g_img_bytes
        global g_project_fw_file
        global g_cfg_outputfile
        global g_cfg_outputfiletypes
        global g_cfg_outputEncryption
        global g_zota_header
        global g_zota_total_image_size
        global g_confName
        global g_aes_key
        global g_iv
        global g96_fw_img_signature
        global g96_md_signature
        global g_img_src_addr
        global g1_fw_img_dec_mthd
        global g_bota_header
        global g_bota_encryption
        global g_bota_file_type
        global g_bota_checksum
        
        write_ota_config_file()
        read_config_file()
        
        exe_file_prod   = ide.expandProjectMacrosEx("${ProjectName}", g_confName, "${ProjectDir}/${ImagePath}", False)
        if( False == path.exists(exe_file_prod) ):
            dialog("Hex file " + exe_file_prod + " not found", True)
            return 1
        if( len(g_cfg_outputfile.strip()) == 0 ):
            dialog("Output file name not set", True)
            return 1

        g1_fw_img_dec_mthd = 1
        if( 'Unencrypted' in g_cfg_outputEncryption ):
            g1_fw_img_dec_mthd = 0

        ih = IntelHex(exe_file_prod)
        cropped_end_address = get_end_address_cropped(ih, global_crop_start_address, global_crop_end_address)
        #this will save only an area of the data
        ih.padding = 0xFF
        #ih.tobinfile(bin_file, start = global_crop_start_address, end = cropped_end_address)
        g4_fw_img_len = cropped_end_address - global_crop_start_address + 1
        fw = ih.tobinarray(start = global_crop_start_address, size = g4_fw_img_len)
        bin_bytes = bytearray(fw)

        g96_fw_img_signature[0:96] = bytearray(b'\x00') * 96
        g96_md_signature[0:96] = bytearray(b'\x00') * 96

        if( g1_auth_mthd > 2 ):
            dialog("Invalid Authentication Method", True)
            return 1
        
        if( g1_auth_mthd == 1):
            if False == path.exists(g_private_key_file):
                dialog("Private key file " + g_private_key_file + " not found", True)
                return 1

            prk_file = g_private_key_file
            pr = utils.readPrivateKey("EC", prk_file) 

            key_bytes = pr.getEncoded()
            if len(key_bytes) != 138:
                dialog("Incorrect format of private key file " + prk_file, True)
                return 1

            sign = bytearray(b'\x00') * 72
            sign = utils.computeSignatureFromHash(bin_bytes,  "SHA256withECDSA", pr, None)
            reformat = reformat_signature(sign, 32)
            for i in range(64):
                g96_fw_img_signature[i] = reformat[i]
                
            tmp_src = g_img_src_addr
            g_img_src_addr = 0
            fw_dec_mthd = g1_fw_img_dec_mthd
            g1_fw_img_dec_mthd = 0
            fill_header()
            file_bytes = g_metaheader[16:132]
            g_img_src_addr = tmp_src
            g1_fw_img_dec_mthd = fw_dec_mthd
            
            sign = bytearray(b'\x00') * 72
            sign = utils.computeSignatureFromHash(file_bytes,  "SHA256withECDSA", pr, None)
            reformat = reformat_signature(sign, 32)
            for i in range(64):
                g96_md_signature[i] = reformat[i]
            
                
        if( g1_auth_mthd == 2):
            if False == path.exists(g_private_key_file):
                dialog("Private key file " + g_private_key_file + " not found", True)
                return 1
            prk_file = g_private_key_file
            pr = utils.readPrivateKey("EC", prk_file) 
            key_bytes = pr.getEncoded()
            if len(key_bytes) != 185:
                dialog("Incorrect format of private key file " + prk_file, True)
                return 1

            sign = bytearray(b'\x00') * 104
            sign = utils.computeSignatureFromHash(bin_bytes,  "SHA384withECDSA", pr, None)
            reformat = reformat_signature(sign, 48)
            for i in range(96):
                g96_fw_img_signature[i] = reformat[i]
            
            tmp_src = g_img_src_addr
            g_img_src_addr = 0
            fw_dec_mthd = g1_fw_img_dec_mthd
            g1_fw_img_dec_mthd = 0
            fill_header()

            file_bytes = g_metaheader[16:132]
            g_img_src_addr = tmp_src
            g1_fw_img_dec_mthd = fw_dec_mthd
            
            sign = bytearray(b'\x00') * 104
            sign = utils.computeSignatureFromHash(file_bytes,  "SHA384withECDSA", pr, None)
            reformat = reformat_signature(sign, 48)
            for i in range(96):
                g96_md_signature[i] = reformat[i]

        fill_header()

        with open(g_cfg_outputfile, "wb") as fb:
            if( g1_fw_img_dec_mthd == 0 ):
                g_bota_encryption = 0
                for i in range(len(bin_bytes)):
                    g_bota_checksum += bin_bytes[i]
                for i in range(512):
                    g_bota_checksum += g_metaheader[i]
                
                if( 'Combo' in g_cfg_outputfiletypes ):
                    g_bota_file_type = 2
                    g_zota_total_image_size = g4_fw_img_len + 512
                    if fill_zota_header() != 0:
                        fb.close()
                        return
                    for i in range(len(g_zota_header)):
                        g_bota_checksum += g_zota_header[i]
                    g_bota_checksum = g_bota_checksum+g_bota_header_ver+g_bota_encryption+g4_fw_img_rev[0]+g4_fw_img_rev[1]+g4_fw_img_rev[2]+g4_fw_img_rev[3]+g_bota_file_type
                    g_bota_checksum = 0xFFFF - (g_bota_checksum&0x0000FFFF) + 1
                    fill_bota_header()
                    fb.write(g_bota_header)
                    fb.write(g_zota_header)
                    
                elif( 'Zigbee' in g_cfg_outputfiletypes ):
                    g_zota_total_image_size = g4_fw_img_len + 512 
                    if fill_zota_header() != 0:
                        fb.close()
                        return
                    fb.write(g_zota_header)
                    
                elif( 'BLE' in g_cfg_outputfiletypes ):
                    g_bota_file_type = 1
                    g_bota_checksum = g_bota_checksum+g_bota_header_ver+g_bota_encryption+g4_fw_img_rev[0]+g4_fw_img_rev[1]+g4_fw_img_rev[2]+g4_fw_img_rev[3]+g_bota_file_type
                    g_bota_checksum = 0xFFFF - (g_bota_checksum&0x0000FFFF) + 1
                    fill_bota_header()
                    fb.write(g_bota_header)
                    
                fb.write(g_metaheader)
                fb.write(bin_bytes)
            else:
                tobeEncrypt = bytearray(g_metaheader)
                tobeEncrypt.extend(bin_bytes)
                plain = bytearray(tobeEncrypt)

                plain_list = list(plain)
                iv_list = list(g_iv)
                key_list = list(g_aes_key)

                plain = from_unsigned_list_to_signed(plain_list)
                iv = from_unsigned_list_to_signed(iv_list)
                key = from_unsigned_list_to_signed(key_list)

                ivSpec = IvParameterSpec(iv)
                skeySpec = SecretKeySpec(key, "AES");

                cipher = Cipher.getInstance("AES/CBC/PKCS5Padding")
                cipher.init(Cipher.ENCRYPT_MODE, skeySpec, ivSpec);
                encrypted = cipher.doFinal(plain);

                encrypted_unsigned = from_signed_list_to_unsigned(encrypted)
                
                encrypted_bin = bytearray(encrypted_unsigned)
                
                for i in range(len(encrypted_bin)):
                    g_bota_checksum += encrypted_bin[i]
                g_bota_encryption = 1
                
                if( 'Combo' in g_cfg_outputfiletypes ):
                    g_bota_file_type = 2
                    g_zota_total_image_size = len(encrypted_bin)
                    if fill_zota_header() != 0:
                        fb.close()
                        return
                    for i in range(len(g_zota_header)):
                        g_bota_checksum += g_zota_header[i]
                    g_bota_checksum = g_bota_checksum+g_bota_header_ver+g_bota_encryption+g4_fw_img_rev[0]+g4_fw_img_rev[1]+g4_fw_img_rev[2]+g4_fw_img_rev[3]+g_bota_file_type
                    g_bota_checksum = 0xFFFF - (g_bota_checksum&0x0000FFFF) + 1
                    fill_bota_header()
                    fb.write(g_bota_header)
                    fb.write(g_zota_header)
                    
                if( 'Zigbee' in g_cfg_outputfiletypes ):
                    g_zota_total_image_size = len(encrypted_bin) + 512
                    if fill_zota_header() != 0:
                        fb.close()
                        return
                    fb.write(g_zota_header)
                    
                elif( 'BLE' in g_cfg_outputfiletypes ):
                    g_bota_file_type = 1
                    g_bota_checksum = g_bota_checksum+g_bota_header_ver+g_bota_encryption+g4_fw_img_rev[0]+g4_fw_img_rev[1]+g4_fw_img_rev[2]+g4_fw_img_rev[3]+g_bota_file_type
                    g_bota_checksum = 0xFFFF - (g_bota_checksum&0x0000FFFF) + 1
                    fill_bota_header()
                    fb.write(g_bota_header)
                    
                fb.write(encrypted_bin)
            fb.flush()
            fb.close()

        dialog("OTA image file " + g_cfg_outputfile + " was Created Successfully!", False)
        return
    
def mplab_configure_OTA(confName):
    global zotaOpt

    if zotaOpt == None:
        zotaOpt=OTAPane()
        g_confName = confName

    return zotaOpt.getPanel()

def save_mplab_configure_OTA(confName):
    global zotaOpt
    
    if zotaOpt == None:
        return

    write_ota_config_file()
    return



class OutputFileMouseListener(MouseAdapter):
    def mousePressed(self, event):
        JOptionPane.showMessageDialog(gframe, 
                              "Choose Output File Name for the OTA package in binary format", 
                              "Output File Name Help", 
                              JOptionPane.INFORMATION_MESSAGE)
 
class OutputTypeMouseListener(MouseAdapter):
    def mousePressed(self, event):
        JOptionPane.showMessageDialog(gframe, 
                              "Choose Output File Type, choose among BLE, Zigbee or Combo OTA operation", 
                              "Output File Type Help", 
                              JOptionPane.INFORMATION_MESSAGE)

class OutputEncryptionMouseListener(MouseAdapter):
    def mousePressed(self, event):
        JOptionPane.showMessageDialog(gframe, 
                              "Choose whether to Encrypt the OTA package", 
                              "Output File Encryption Help", 
                              JOptionPane.INFORMATION_MESSAGE)

class manuCodeMouseListener(MouseAdapter):
    def mousePressed(self, event):
        JOptionPane.showMessageDialog(gframe, 
                              "16-bit manufacturer identifier used to match supported devices. Defaults to 0xFFFF (match all).", 
                              "Manufacture Code Help", 
                              JOptionPane.INFORMATION_MESSAGE)

class imageTypeMouseListener(MouseAdapter):
    def mousePressed(self, event):
        JOptionPane.showMessageDialog(gframe, 
                              "16-bit image type. Defaults to 0xFFFF (match all)", 
                              "Image Type Help", 
                              JOptionPane.INFORMATION_MESSAGE)

class fileVersionMouseListener(MouseAdapter):
    def mousePressed(self, event):
        JOptionPane.showMessageDialog(gframe, 
                              "32-bit integer representing the file version. Can be in the recommended format (8-bit app release, 8-bit app build, 8 bit stack release, 8-bit stack build), simple increasing version, or an unsupported version format. If in an unsupported version format the OTA Cluster will not be able to compare file versions. Defaults to 0x0000.", 
                              "File Version Help", 
                              JOptionPane.INFORMATION_MESSAGE)
 
class zigbeeStackVersionMouseListener(MouseAdapter):
    def mousePressed(self, event):
        JOptionPane.showMessageDialog(gframe, 
                              "16-bit identifier of the zigbee stack version. Defaults to 0x02 for ZigBee Pro.", 
                              "Zigbee Stack Version Help", 
                              JOptionPane.INFORMATION_MESSAGE)

class headerStringMouseListener(MouseAdapter):
    def mousePressed(self, event):
        JOptionPane.showMessageDialog(gframe, 
                              "32-byte string used by each manufacturer as they see fit but recommended to be human readable.", 
                              "Header String Help", 
                              JOptionPane.INFORMATION_MESSAGE)

class securityCredentialVersionMouseListener(MouseAdapter):
    def mousePressed(self, event):
        JOptionPane.showMessageDialog(gframe, 
                              "Optional 8-bit identifier of the Security Credential Version. Defaults to not included.", 
                              "Security Credential Version Help", 
                              JOptionPane.INFORMATION_MESSAGE)
                              
class upgradeFileDestinationMouseListener(MouseAdapter):
    def mousePressed(self, event):
        JOptionPane.showMessageDialog(gframe, 
                              "Optional 64-bit extended address of the device to which this image is specific. Defaults to not include, image is available to all devices.", 
                              "Upgrade File Destination Help", 
                              JOptionPane.INFORMATION_MESSAGE)
                              
class minHardwareVersionMouseListener(MouseAdapter):
    def mousePressed(self, event):
        JOptionPane.showMessageDialog(gframe, 
                              "Optional 0/16-bit integer representing the earliest hardware platorm this image can be used on.", 
                              "Minimum Hardware Version Help", 
                              JOptionPane.INFORMATION_MESSAGE)
                              
class maxHardwareVersionMouseListener(MouseAdapter):
    def mousePressed(self, event):
        JOptionPane.showMessageDialog(gframe, 
                              "Optional 16-bit integer representing the latest hardware platorm this image can be used on.", 
                              "Maximum Hardware Version Help", 
                              JOptionPane.INFORMATION_MESSAGE)                              

class AESKeyMouseListener(MouseAdapter):
    def mousePressed(self, event):
        JOptionPane.showMessageDialog(gframe, 
                              "128bit AES key to encrypt the OTA pacakge with AES-CBC-128", 
                              "AES Key Help", 
                              JOptionPane.INFORMATION_MESSAGE)    
                              
class IVMouseListener(MouseAdapter):
    def mousePressed(self, event):
        JOptionPane.showMessageDialog(gframe, 
                              "128bit Initial Vector to encrypt the OTA pacakge with AES-CBC-128", 
                              "Initial Vector Help", 
                              JOptionPane.INFORMATION_MESSAGE)  


















def dialog(e, error):
    frame = JFrame("End of Build")
    frame.setLocation(100,100)
    frame.setSize(400,300)
    frame.setLayout(BorderLayout())
    
    if (error == True):
        JOptionPane.showMessageDialog(frame,e, "Error", JOptionPane.ERROR_MESSAGE)
    else:
        JOptionPane.showMessageDialog(frame,e)
    

def fill_bota_header():
    global g_bota_header_ver
    global g_bota_encryption
    global g_bota_checksum
    global g_bota_file_type
    global g4_fw_img_rev
    global g_bota_header

    g_bota_header = bytearray(b'\x00')*16
    
    g_bota_header[0:1] = bytearray(struct.pack("<B", g_bota_header_ver))
    g_bota_header[1:2] = bytearray(struct.pack("<B", g_bota_encryption))
    g_bota_header[2:4] = bytearray(struct.pack("<H", g_bota_checksum))
    g_bota_header[4:8] = g4_fw_img_rev
    g_bota_header[8:9] = bytearray(struct.pack("<B", g_bota_file_type))
    
    
def fill_zota_header():
    global g_zota_file_identifier
    global g_zota_header_version
    global g_zota_header_length
    global g_zota_field_control
    global g_zota_manufacture_code
    global g_zota_image_type
    global g_zota_file_version
    global g_zota_zigbee_stack_version
    global g_zota_header_string
    global g_zota_total_image_size
    global g_zota_security_credential_version
    global g_zota_upgrade_file_destination
    global g_zota_minimum_hardware_version
    global g_zota_maximum_hardware_version
    global g_zota_security_credential_version_check
    global g_zota_upgrade_file_destination_check
    global g_zota_hardware_version_check
    global g_zota_header

    g_zota_field_control = 0
    g_zota_header_length = 56
    if g_zota_security_credential_version_check:
        text = (g_zota_security_credential_version[:4]).strip()
        security_credential_version = 0
        if len(text) == 4:
            g_zota_field_control |= 0x01
            g_zota_header_length += 1
            security_credential_version = int(text, 16)
        else:
            dialog("Security Credential Version NOT Set Correctly", True)
            return 1
        
    if g_zota_upgrade_file_destination_check:
        upgrade_file_destination = bytearray(b'\x00')*8
        text = (g_zota_upgrade_file_destination[:18]).strip()
        if len(text) == 18:
            g_zota_field_control |= 0x02
            g_zota_header_length += 8
            upgrade_file_destination = bytearray.fromhex(text[2:])
        else:
            dialog("Upgrade File Destination Not Set Correctly", True)
            return 1
    
    if g_zota_hardware_version_check:
        minimum_hardware_version = 0
        maximum_hardware_version = 0
        text = (g_zota_minimum_hardware_version[:6]).strip()
        text2 = (g_zota_maximum_hardware_version[:6]).strip()
        if ((len(text)==6) and (len(text2)==6)):
            g_zota_field_control |= 0x04
            g_zota_header_length += 4
            minimum_hardware_version = int(text, 16)
            maximum_hardware_version = int(text2, 16)
        else:
            dialog("Hardware Versions Not Set Correctly", True)
            return 1

    g_zota_header[0:4] = bytearray(struct.pack("<L", g_zota_file_identifier))
    text = (g_zota_header_version[:6]).strip()
    data = int(text, 16)
    g_zota_header[4:6] = bytearray(struct.pack("<H", data))
    g_zota_header[6:8] = bytearray(struct.pack("<H", g_zota_header_length))
    g_zota_header[8:10] = bytearray(struct.pack("<H", g_zota_field_control))
    text = (g_zota_manufacture_code[:6]).strip()
    data = int(text, 16)
    g_zota_header[10:12] = bytearray(struct.pack("<H", data))
    text = (g_zota_image_type[:6]).strip()
    data = int(text, 16)
    g_zota_header[12:14] = bytearray(struct.pack("<H", data))
    text = (g_zota_file_version[:10]).strip()
    data = int(text, 16)
    g_zota_header[14:18] = bytearray(struct.pack("<L", data))
    text = (g_zota_zigbee_stack_version[:6]).strip()
    data = int(text, 16)
    g_zota_header[18:20] = bytearray(struct.pack("<H", data))
    text = (g_zota_header_string[:32]).strip()
    g_zota_header[20:52] = bytearray(b'\x00')*32
    g_zota_header[20:52] = bytearray(struct.pack("<32s", text))
    g_zota_header[52:56] = bytearray(struct.pack("<L", (g_zota_total_image_size+g_zota_header_length)))
    header_index = 56
    if( (g_zota_field_control & 0x01) > 0 ):
        g_zota_header[header_index:(header_index+1)] = bytearray(struct.pack("<B", security_credential_version))
        header_index += 1
    if( (g_zota_field_control & 0x02) > 0 ):
        g_zota_header[header_index:(header_index+8)] = upgrade_file_destination
        header_index += 8
    if( (g_zota_field_control & 0x04) > 0 ):
        g_zota_header[header_index:(header_index+2)] = bytearray(struct.pack("<H", minimum_hardware_version))
        g_zota_header[(header_index+2):(header_index+4)] = bytearray(struct.pack("<H", maximum_hardware_version))
        header_index += 4
    
    g_zota_header = g_zota_header[:header_index]
    return 0
    

def fill_header():
    global g_metaheader
    global g_filler1
    global g_filler2
    global g_filler3
    global g4_identifier
    global g4_seq_num
    global g1_md_rev
    global g1_cont_idx
    global g1_auth_mthd
    global g1_auth_key
    global gl_dec_mthd
    global gl_dec_key
    global g2_len
    global g4_fw_img_rev
    global g4_fw_img_len
    global g1_fw_img_dec_mthd
    global g1_fw_img_dec_key
    global g96_fw_img_signature
    global g284_filler
    global g96_md_signature
    global g_img_src_addr
    global g_img_dst_addr
    
    g_metaheader[0:4] = bytearray(struct.pack("<L", g4_seq_num))
    g_metaheader[4:5] = bytearray(struct.pack("B", g1_md_rev))
    g_metaheader[5:6] = bytearray(struct.pack("B", g1_cont_idx))
    g_metaheader[6:10] = bytearray(struct.pack("<4s", g4_identifier))
    if( g1_auth_mthd == 0 ):
        g_metaheader[10:11] = bytearray(struct.pack("B", g1_auth_mthd))
    else:
        g_metaheader[10:11] = bytearray(struct.pack("B", (g1_auth_mthd+1)))
    g_metaheader[11:12] = bytearray(struct.pack("B", g1_auth_key))
    g_metaheader[12:13] = bytearray(struct.pack("B", gl_dec_mthd))
    g_metaheader[13:14] = bytearray(struct.pack("B", gl_dec_key))
    g_metaheader[14:16] = bytearray(struct.pack("<H", g2_len))
    g_metaheader[16:20] = g4_fw_img_rev
    g_metaheader[20:24] = bytearray(struct.pack("<L", g_img_src_addr))
    g_metaheader[24:28] = bytearray(struct.pack("<L", g_img_dst_addr))
    g_metaheader[28:32] = bytearray(struct.pack("<L", g4_fw_img_len))
    if( g1_auth_mthd == 0 ):
        g_metaheader[32:33] = bytearray(struct.pack("B", g1_auth_mthd))
    else:
        g_metaheader[32:33] = bytearray(struct.pack("B", (g1_auth_mthd+1)))
    g_metaheader[33:34] = bytearray(struct.pack("B", g1_auth_key))
    g_metaheader[34:35] = bytearray(struct.pack("B", g1_fw_img_dec_mthd))
    g_metaheader[35:36] = bytearray(struct.pack("B", g1_fw_img_dec_key))
    g_metaheader[36:132] = g96_fw_img_signature
    g_metaheader[132:228] = g96_md_signature
    g_metaheader[228:512] = g284_filler

def get_file_bytes(file):
    with open(file, "rb") as fb:
        exe_content = bytearray(fb.read())
    fb.close()
    return exe_content 

def signfile(file):
    global g_private_key_file
    
    log.setShowOutput(True)
    file_bytes = get_file_bytes(file)
    prk_file = g_private_key_file
    pr = utils.readPrivateKey("EC", prk_file) 
    sign = bytearray(b'\x00') * 72
    sign = utils.computeSignatureFromHash(file_bytes,  "SHA256withECDSA", pr, None)
    return sign


def shafile(file):
    file_bytes = get_file_bytes(file)
    engine = hashlib.sha256()
    engine.update(bytes(file_bytes))
    data_hash = engine.digest()
    return data_hash
    
    
def signbytes(data_bytes):
    global g_private_key_file
    
    prk_file = g_private_key_file
    pr = utils.readPrivateKey("EC", prk_file) 
    sign2 = bytearray(b'\x00') * 72
    sign2 = utils.computeSignatureFromHash(data_bytes,  "SHA256withECDSA", pr, None)
    return sign2

def shabytes(data_bytes):
    engine = hashlib.sha256()
    engine.update(bytes(data_bytes))
    data_hash = engine.digest()
    return data_hash

def get_end_address_cropped(ih, crop_start_address, crop_end_address):
    # see what the largest address from the intel hex object is:
    max_address = ih.maxaddr()
    if max_address > crop_end_address:
        max_address = crop_end_address
    size = max_address - crop_start_address
    size = size + 1
    padlen = 4096 - (size % 4096)
    if padlen == 4096:
        return crop_start_address + size
    else:
        return crop_start_address + size + padlen

def reformat_signature(sign, sig_sz):
        
    reformat = bytearray(b'\x00') * (sig_sz * 2)
    idx = 4
    if( (sign[idx] == 0) and (sign[idx+1] > 0x7F) ):
        idx = 5
    
    for i in range(sig_sz):
        reformat[i] = sign[idx+i]
    
    idx += sig_sz
    if( sign[idx] != 0x02 ):
        print 'wrong format'
        print str(sign[idx]) + ' ' + str(idx)
        return None
        
    idx += 2
    if( (sign[idx] == 0) and (sign[idx+1] > 0x7F) ):
        idx += 1
    for i in range(sig_sz):
        reformat[sig_sz+i] = sign[idx+i]
        
    return reformat
        
    
    
    
def create_signed_image(e):
    global bsOpt
    global g96_md_signature
    global g1_auth_mthd
    global g96_fw_img_signature
    global g4_fw_img_len
    global g_signed_fw_file
    global g_metaheader
    global g_img_bytes
    global g_private_key_file
    global g96_md_signature
    global g_img_src_addr
    global g_project_fw_file

    read_config_file()

    exe_file_prod   = ide.expandProjectMacrosEx("${ProjectName}", e, "${ProjectDir}/${ImagePath}", False)
    #exe_file_debug  = ide.expandProjectMacrosEx("${ProjectName}", e, "${ProjectDir}/${ImagePath}", True)
    if False == path.exists(exe_file_prod):
        dialog("Hex file " + exe_file_prod + " not found", True)
        return 1
    g_project_fw_file = exe_file_prod[:(len(exe_file_prod)-4)]

    ih = IntelHex(exe_file_prod)
    bin_file = exe_file_prod + ".bin"
    cropped_end_address = get_end_address_cropped(ih, global_crop_start_address, global_crop_end_address)
    #this will save only an area of the data
    ih.padding = 0xff
    ih.tobinfile(bin_file, start = global_crop_start_address, end = (cropped_end_address-1))

    g4_fw_img_len = cropped_end_address - global_crop_start_address

    g96_fw_img_signature[0:96] = bytearray(b'\x00') * 96
    g96_md_signature[0:96] = bytearray(b'\x00') * 96

    if( g1_auth_mthd > 2 ):
        dialog("Invalid Authentication Method", True)
        return 1

    if( g1_auth_mthd == 1):
        if False == path.exists(g_private_key_file):
            dialog("Private key file " + g_private_key_file + " not found", True)
            return 1

        prk_file = g_private_key_file
        pr = utils.readPrivateKey("EC", prk_file) 

        key_bytes = pr.getEncoded()
        if len(key_bytes) != 138:
            dialog("Incorrect format of private key file " + prk_file, True)
            return 1

        img_bytes = get_file_bytes(bin_file)
        img_bytes = img_bytes[:g4_fw_img_len]
        sign = bytearray(b'\x00') * 72
        sign = utils.computeSignatureFromHash(img_bytes,  "SHA256withECDSA", pr, None)
        reformat = reformat_signature(sign, 32)
        for i in range(64):
            g96_fw_img_signature[i] = reformat[i]
        
        tmp_src = g_img_src_addr
        g_img_src_addr = 0
        fill_header()
        file_bytes = g_metaheader[16:132]
        g_img_src_addr = tmp_src
        sign = bytearray(b'\x00') * 72
        sign = utils.computeSignatureFromHash(file_bytes,  "SHA256withECDSA", pr, None)
        reformat = reformat_signature(sign, 32)
        for i in range(64):
            g96_md_signature[i] = reformat[i]
    
    if( g1_auth_mthd == 2):
        if False == path.exists(g_private_key_file):
            dialog("Private key file " + g_private_key_file + " not found", True)
            return 1
        prk_file = g_private_key_file
        pr = utils.readPrivateKey("EC", prk_file) 
        key_bytes = pr.getEncoded()
        if len(key_bytes) != 185:
            dialog("Incorrect format of private key file " + prk_file, True)
            return 1

        img_bytes = get_file_bytes(bin_file)
        img_bytes = img_bytes[:g4_fw_img_len]
        sign = bytearray(b'\x00') * 104
        sign = utils.computeSignatureFromHash(img_bytes,  "SHA384withECDSA", pr, None)
        
        reformat = reformat_signature(sign, 48)
        for i in range(96):
            g96_fw_img_signature[i] = reformat[i]
        
        tmp_src = g_img_src_addr
        g_img_src_addr = 0
        fill_header()
        file_bytes = g_metaheader[16:132]
        g_img_src_addr = tmp_src
    
        sign = bytearray(b'\x00') * 104
        sign = utils.computeSignatureFromHash(file_bytes,  "SHA384withECDSA", pr, None)
        reformat = reformat_signature(sign, 48)
        for i in range(96):
            g96_md_signature[i] = reformat[i]

    fill_header()

    #if (len(g_signed_fw_file.strip()) == 0):
    #    dialog("Signed Firmware Image File Name NOT Set", True)
    #    return 1

    g_signed_fw_file = g_project_fw_file + ".signed.bin"
    with open(g_signed_fw_file, "wb") as fb:
        fb.write(g_metaheader)
        g_img_bytes = bytearray(g_metaheader)
        file_bytes = get_file_bytes(bin_file)
        file_bytes = file_bytes[:g4_fw_img_len]
        if( len(file_bytes) % 4 > 0 ):
            appends = bytearray(b'\x00\x00')
            file_bytes.extend(appends)
        g_img_bytes.extend(file_bytes)
        fb.write(file_bytes)
        fb.close()
    
    return 0


def create_encrypt_image(e): 
    global bsOpt
    global g_signed_fw_file
    global g_img_bytes
    global g_project_fw_file
    
    encrypt_fw_file = g_project_fw_file + ".encrypt.signed.bin"
    with open(encrypt_fw_file, "wb") as fb:
        keytxt = bsOpt.AESKeyTxt.getText()
        key = bytearray.fromhex(keytxt[2:])
        ivtxt = bsOpt.IVTxt.getText()
        iv = bytearray.fromhex(ivtxt[2:])
        
        plain = bytearray(g_img_bytes)
        plain_list = list(plain)
        iv_list = list(iv)
        key_list = list(key)
        
        plain = from_unsigned_list_to_signed(plain_list)
        iv = from_unsigned_list_to_signed(iv_list)
        key = from_unsigned_list_to_signed(key_list)
        
        ivSpec = IvParameterSpec(iv)
        skeySpec = SecretKeySpec(key, "AES")

        cipher = Cipher.getInstance("AES/CBC/PKCS5Padding")
        cipher.init(Cipher.ENCRYPT_MODE, skeySpec, ivSpec)
        encrypted = cipher.doFinal(plain)
        
        encrypted_unsigned = from_signed_list_to_unsigned(encrypted)
        
        fb.write(bytearray(encrypted_unsigned))

        fb.flush()
        fb.close()
    return
        
def create_hex_file(e):
    global bsOpt
    global g_signed_fw_file
    global g_img_bytes
    global g_project_fw_file
    
    hex_file_name = g_project_fw_file + ".signed.hex"
    
    h=IntelHex()
    h.frombytes(g_img_bytes, 0x01000000)
    h.tofile(hex_file_name,"hex")
    
    '''
    # following is convert back to bin and check if it matches
    ih = IntelHex(hex_file_name)
    cropped_end_address = get_end_address_cropped(ih, 0x1000000, 0x1080000)
    #this will save only an area of the data
    ih.padding = 0xff
    ih.tobinfile("dup.bin", start = (global_crop_start_address-0x200), end = (cropped_end_address-1))
    '''
    return
        
def on_pre_program():
    global bsOpt
    global g96_md_signature
    global g1_auth_mthd
    global g96_fw_img_signature
    global g4_fw_img_len
    global g_signed_fw_file
    global g_metaheader
    global g_private_key_file
    global g96_md_signature
    global g_img_src_addr

    read_config_file()

    code_buffer = bytearray(global_crop_end_address - global_crop_start_address)
    mem.ReadBlock(mem.MemType.ProgramMemory, global_crop_start_address, 0, len(code_buffer), code_buffer )

    memblocks = mem.GetUsedAreas(mem.MemType.ProgramMemory, global_crop_start_address, global_crop_end_address)
    
    mblock = memblocks[0]
    g4_fw_img_len = (mblock[1]-mblock[0]+1)
    
    padlen = 4096 - (g4_fw_img_len % 4096)
    if padlen < 4096:
        g4_fw_img_len += padlen
    img_bytes = code_buffer[:g4_fw_img_len]
    
    g96_fw_img_signature[0:96] = bytearray(b'\x00') * 96
    g96_md_signature[0:96] = bytearray(b'\x00') * 96
        
    if( g1_auth_mthd == 0):
        fill_header()
        mem.WriteBlock(mem.MemType.ProgramMemory, global_header_start_address, 0, len(g_metaheader), g_metaheader)
        return 0
 
    if( g1_auth_mthd == 1):
        
        prk_file = g_private_key_file
        pr = utils.readPrivateKey("EC", prk_file) 
        key_bytes = pr.getEncoded()
        if len(key_bytes) != 138:
            dialog("Incorrect format of P256r1 private key file " + prk_file, True)
            return 1

        img_bytes = code_buffer[:g4_fw_img_len]
        sign = bytearray(b'\x00') * 72
        sign = utils.computeSignatureFromHash(img_bytes,  "SHA256withECDSA", pr, None)
        reformat = reformat_signature(sign, 32)
        for i in range(64):
            g96_fw_img_signature[i] = reformat[i]
        
        tmp_src = g_img_src_addr
        g_img_src_addr = 0
        fill_header()
        file_bytes = g_metaheader[16:132]
        g_img_src_addr = tmp_src
    
        sign = bytearray(b'\x00') * 72
        sign = utils.computeSignatureFromHash(file_bytes,  "SHA256withECDSA", pr, None)
        reformat = reformat_signature(sign, 32)
        for i in range(64):
            g96_md_signature[i] = reformat[i]

        fill_header()
        
        mem.WriteBlock(mem.MemType.ProgramMemory, global_header_start_address, 0, len(g_metaheader), g_metaheader)
        return 0
    
    
    if( g1_auth_mthd == 2):
        
        prk_file = g_private_key_file
        pr = utils.readPrivateKey("EC", prk_file) 
        key_bytes = pr.getEncoded()
        if len(key_bytes) != 185:
            dialog("Incorrect format of P384r1 private key file " + prk_file, True)
            return 1

        img_bytes = code_buffer[:g4_fw_img_len]
        sign = bytearray(b'\x00') * 104
        sign = utils.computeSignatureFromHash(img_bytes,  "SHA384withECDSA", pr, None)  
        reformat = reformat_signature(sign, 48)
        for i in range(96):
            g96_fw_img_signature[i] = reformat[i]
        
        tmp_src = g_img_src_addr
        g_img_src_addr = 0
        fill_header()
        file_bytes = g_metaheader[16:132]
        g_img_src_addr = tmp_src
    
        sign = bytearray(b'\x00') * 104
        sign = utils.computeSignatureFromHash(file_bytes,  "SHA384withECDSA", pr, None)
        reformat = reformat_signature(sign, 48)
        for i in range(96):
            g96_md_signature[i] = reformat[i]

        fill_header()
        mem.WriteBlock(mem.MemType.ProgramMemory, global_header_start_address, 0, len(g_metaheader), g_metaheader)
        return 0

    return 1

def on_project_load_done(confName): 
    global g96_md_signature
    global g1_auth_mthd
    global g96_fw_img_signature
    global g4_fw_img_len
    global g_signed_fw_file
    global g_metaheader
    global g_private_key_file
    global g96_md_signature
    global g_img_src_addr
    global g_img_bytes
    
    #msg.print("on project load for conf {}\n".format(confName))
    #for i in load_list:
    #    msg.print("Load this {}\n".format(i))
    #    msg.print("Build is {}\n".format(is_debug_build))

    if( is_debug_build ):
        exe_file_debug  = ide.expandProjectMacrosEx("${ProjectName}", confName, "${ProjectDir}/${ImagePath}", True)
        g_project_fw_file = exe_file_debug[:(len(exe_file_debug)-4)]
        if( False == path.exists(exe_file_debug) ):
            dialog("Elf file " + exe_file_debug + " not found", True)
            return 1
    else:
        exe_file_prod   = ide.expandProjectMacrosEx("${ProjectName}", confName, "${ProjectDir}/${ImagePath}", False)
        g_project_fw_file = exe_file_prod[:(len(exe_file_prod)-4)]
        if( False == path.exists(exe_file_prod) ):
            dialog("Hex file " + exe_file_prod + " not found", True)
            return 1  

    read_config_file() 
        
    code_buffer = bytearray(global_crop_end_address - global_crop_start_address)
    mem.ReadBlock(mem.MemType.ProgramMemory, global_crop_start_address, 0, len(code_buffer), code_buffer )
    memblocks = mem.GetUsedAreas(mem.MemType.ProgramMemory, global_crop_start_address, global_crop_end_address)
    if( len(memblocks) > 1 ):
        return 1

    mblock = memblocks[0] 
    g4_fw_img_len = (mblock[1]-mblock[0]+1) 
    padlen = 4096 - (g4_fw_img_len % 4096)
    if padlen < 4096:
        g4_fw_img_len += padlen
    img_bytes = code_buffer[:g4_fw_img_len]
    
    g96_fw_img_signature[0:96] = bytearray(b'\x00') * 96
    g96_md_signature[0:96] = bytearray(b'\x00') * 96
    
    if( g1_auth_mthd > 2 ):
        dialog("Invalid Authentication Method", True)
        return 1
    
    if( g1_auth_mthd == 1):
        if False == path.exists(g_private_key_file):
            dialog("Private key file " + g_private_key_file + " not found", True)
            return 1

        prk_file = g_private_key_file
        pr = utils.readPrivateKey("EC", prk_file) 

        key_bytes = pr.getEncoded()
        if len(key_bytes) != 138:
            dialog("Incorrect format of private key file " + prk_file, True)
            return 1

        sign = bytearray(b'\x00') * 72
        sign = utils.computeSignatureFromHash(img_bytes,  "SHA256withECDSA", pr, None)
        reformat = reformat_signature(sign, 32)
        for i in range(64):
            g96_fw_img_signature[i] = reformat[i]
        
        tmp_src = g_img_src_addr
        g_img_src_addr = 0
        fill_header()
        file_bytes = g_metaheader[16:132]
        g_img_src_addr = tmp_src
        sign = bytearray(b'\x00') * 72
        sign = utils.computeSignatureFromHash(file_bytes,  "SHA256withECDSA", pr, None)
        reformat = reformat_signature(sign, 32)
        for i in range(64):
            g96_md_signature[i] = reformat[i]
    
    if( g1_auth_mthd == 2):
        if False == path.exists(g_private_key_file):
            dialog("Private key file " + g_private_key_file + " not found", True)
            return 1
        prk_file = g_private_key_file
        pr = utils.readPrivateKey("EC", prk_file) 
        key_bytes = pr.getEncoded()
        if len(key_bytes) != 185:
            dialog("Incorrect format of private key file " + prk_file, True)
            return 1

        sign = bytearray(b'\x00') * 104
        sign = utils.computeSignatureFromHash(img_bytes,  "SHA384withECDSA", pr, None)

        reformat = reformat_signature(sign, 48)
        for i in range(96):
            g96_fw_img_signature[i] = reformat[i]
        
        tmp_src = g_img_src_addr
        g_img_src_addr = 0
        fill_header()
        file_bytes = g_metaheader[16:132]
        g_img_src_addr = tmp_src
    
        sign = bytearray(b'\x00') * 104
        sign = utils.computeSignatureFromHash(file_bytes,  "SHA384withECDSA", pr, None)
        reformat = reformat_signature(sign, 48)
        for i in range(96):
            g96_md_signature[i] = reformat[i]

    fill_header()
    
    g_signed_fw_file = g_project_fw_file + ".signed.bin"
    with open(g_signed_fw_file, "wb") as fb:
        fb.write(g_metaheader)
        g_img_bytes = bytearray(g_metaheader)
        if is_debug_build == 0:
            g_img_bytes.extend(img_bytes)
        fb.write(img_bytes)
        fb.close()

    signed_fw_hex_file = g_project_fw_file + ".signed.hex"
    h=IntelHex()
    h.frombytes(g_img_bytes, 0x01000000)
    h.tofile(signed_fw_hex_file,"hex")
    
    
    header_hex_file = g_project_fw_file + ".header.hex"
    h = IntelHex()
    h.frombytes(g_metaheader, 0x01000000)
    h.tofile(header_hex_file, "hex")
    
    signed_fw_hex_file2 = g_project_fw_file + ".signed2.hex"
    fw_hex_file = g_project_fw_file + ".hex"
    print 'fw ' + fw_hex_file
    header_hex = IntelHex(header_hex_file)
    fw_hex = IntelHex(fw_hex_file)
    fw_hex.merge(header_hex, overlap='replace')
    fw_hex.tofile(signed_fw_hex_file2, "hex")
    
    
    unified_file = g_project_fw_file + ".unified.hex"
    if( path.exists(unified_file) ):
        unified_hex = IntelHex(unified_file)
        signed_hex = IntelHex(signed_fw_hex_file)
        unified_hex.merge(signed_hex, overlap='replace')
        signed_unified_file = g_project_fw_file + ".signed.unified.hex"
        unified_hex.tofile(signed_unified_file, "hex")
        
    return