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

#!/usr/bin/python

"""
progctrl.py
"""
import serial.tools.list_ports
import array as cmd
import time
import numpy as np

# Program Executive Command Set
PE_CMD_ROW_PGM				= 0x00
PE_CMD_READ					= 0x01
PE_CMD_PGM 					= 0x02
PE_CMD_WORD_PGM				= 0x03
PE_CMD_CHIP_ERASE 			= 0x04
PE_CMD_PAGE_ERASE 			= 0x05
PE_CMD_BLANK_CHECK 			= 0x06
PE_COMMAND_EXEC_VERSION 	= 0x07
PE_CMD_GET_CRC 				= 0x08
PE_CMD_PGM_CLUSTER 			= 0x09
PE_CMD_GET_DEVICEID         = 0x0A
PE_CMD_CHANGE_CFG 			= 0x0B
PE_CMD_GET_CSUM 			= 0x0C
PE_CMD_PGM_CLUSTER_VERIFY 	= 0x11

PROG_CLUSTER_SIZE = 4096
ERASE_PAGE_SIZE = 4096

INITIAL_REMAINDER = 0xFFFF
 # An array containing the pre-computed intermediate result for each
 # possible byte of input.  This is used to speed up the computation.
crcTable = cmd.array('I',[ \
	0x0000,0x1021,0x2042,0x3063,0x4084,0x50A5,0x60C6,0x70E7,0x8108,\
    0x9129,0xA14A,0xB16B,0xC18C,0xD1AD,0xE1CE,0xF1EF,0x1231,0x0210,0x3273, \
    0x2252,0x52B5,0x4294,0x72F7,0x62D6,0x9339,0x8318,0xB37B,0xA35A,0xD3BD, \
    0xC39C,0xF3FF,0xE3DE,0x2462,0x3443,0x0420,0x1401,0x64E6,0x74C7,0x44A4, \
    0x5485,0xA56A,0xB54B,0x8528,0x9509,0xE5EE,0xF5CF,0xC5AC,0xD58D,0x3653, \
    0x2672,0x1611,0x0630,0x76D7,0x66F6,0x5695,0x46B4,0xB75B,0xA77A,0x9719, \
    0x8738,0xF7DF,0xE7FE,0xD79D,0xC7BC,0x48C4,0x58E5,0x6886,0x78A7,0x0840, \
    0x1861,0x2802,0x3823,0xC9CC,0xD9ED,0xE98E,0xF9AF,0x8948,0x9969,0xA90A, \
    0xB92B,0x5AF5,0x4AD4,0x7AB7,0x6A96,0x1A71,0x0A50,0x3A33,0x2A12,0xDBFD, \
    0xCBDC,0xFBBF,0xEB9E,0x9B79,0x8B58,0xBB3B,0xAB1A,0x6CA6,0x7C87,0x4CE4, \
    0x5CC5,0x2C22,0x3C03,0x0C60,0x1C41,0xEDAE,0xFD8F,0xCDEC,0xDDCD,0xAD2A, \
    0xBD0B,0x8D68,0x9D49,0x7E97,0x6EB6,0x5ED5,0x4EF4,0x3E13,0x2E32,0x1E51, \
    0x0E70,0xFF9F,0xEFBE,0xDFDD,0xCFFC,0xBF1B,0xAF3A,0x9F59,0x8F78,0x9188, \
    0x81A9,0xB1CA,0xA1EB,0xD10C,0xC12D,0xF14E,0xE16F,0x1080,0x00A1,0x30C2, \
    0x20E3,0x5004,0x4025,0x7046,0x6067,0x83B9,0x9398,0xA3FB,0xB3DA,0xC33D, \
    0xD31C,0xE37F,0xF35E,0x02B1,0x1290,0x22F3,0x32D2,0x4235,0x5214,0x6277, \
    0x7256,0xB5EA,0xA5CB,0x95A8,0x8589,0xF56E,0xE54F,0xD52C,0xC50D,0x34E2, \
    0x24C3,0x14A0,0x0481,0x7466,0x6447,0x5424,0x4405,0xA7DB,0xB7FA,0x8799, \
    0x97B8,0xE75F,0xF77E,0xC71D,0xD73C,0x26D3,0x36F2,0x0691,0x16B0,0x6657, \
    0x7676,0x4615,0x5634,0xD94C,0xC96D,0xF90E,0xE92F,0x99C8,0x89E9,0xB98A, \
    0xA9AB,0x5844,0x4865,0x7806,0x6827,0x18C0,0x08E1,0x3882,0x28A3,0xCB7D, \
    0xDB5C,0xEB3F,0xFB1E,0x8BF9,0x9BD8,0xABBB,0xBB9A,0x4A75,0x5A54,0x6A37, \
    0x7A16,0x0AF1,0x1AD0,0x2AB3,0x3A92,0xFD2E,0xED0F,0xDD6C,0xCD4D,0xBDAA, \
	0xAD8B,0x9DE8,0x8DC9,0x7C26,0x6C07,0x5C64,0x4C45,0x3CA2,0x2C83,0x1CE0, \
	0x0CC1,0xEF1F,0xFF3E,0xCF5D,0xDF7C,0xAF9B,0xBFBA,0x8FD9,0x9FF8,0x6E17, \
	0x7E36,0x4E55,0x5E74,0x2E93,0x3EB2,0x0ED1,0x1EF0])

class ProgController(object):

	#CFG methods
	PE_USE_NONE					= 0x0
	PE_USE_CHECKSUM				= 0x1
	PE_USE_CRC					= 0x2

	def __init__(self):
		self.UartIntf = 0
		self._debug = False

	def _HIWORD(self, w):
		return (w >> 16)
		
	def _LOWORD(self, w):
		return (w & 0xffff)

	def _set_hiword(self, w, hw):
		w  &=  0x0000ffff
		w |= hw << 16
		return w
		
	def _set_loword(self, w, lw):
		w  &=  0xffff0000
		w |= lw	
		return w

	# Print iterations progress
	def _printProgressBar (self, iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
		"""
		Call in a loop to create terminal progress bar
		@params:
			iteration   - Required  : current iteration (Int)
			total       - Required  : total iterations (Int)
			prefix      - Optional  : prefix string (Str)
			suffix      - Optional  : suffix string (Str)
			decimals    - Optional  : positive number of decimals in percent complete (Int)
			length      - Optional  : character length of bar (Int)
			fill        - Optional  : bar fill character (Str)
			printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
		"""
		percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
		filledLength = int(length * iteration // total)
		bar = fill * filledLength + '-' * (length - filledLength)
		print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
		# Print New Line on Complete
		if iteration == total: 
			print()			
		
	def _send_command(self, Cmd32):
		if self.UartIntf == 0:
			print("Error:Uart interface is not initialized")
			sys.exit()
		Cmd32Res = cmd.array('I', [0xFFFFFFFF])
		#self.debug_print(Cmd32.tobytes())
		self.UartIntf.write(Cmd32.tobytes())
		self.UartIntf.flush()	
		nAttempts = 0
		time.sleep(0.01)
		ResBuff = self.UartIntf.read(self.UartIntf.inWaiting())
		while nAttempts < 10:
			ResBuff += self.UartIntf.read(self.UartIntf.inWaiting())	
			if len(ResBuff) >= 4:
				break
			time.sleep(0.05)
			nAttempts += 1
		if len(ResBuff) >= 4:	
			ResponseHeader = ResBuff[0:4]
			ResBuff = ResBuff[4:]
			Cmd32Res.remove(0xFFFFFFFF)
			Cmd32Res.frombytes(ResponseHeader)
			self.debug_print(Cmd32Res.tobytes())
		else:
			print("Error: No response")
		return Cmd32Res, ResBuff

	def _CRC16_Calculate(self, bufferToCRC):
		remainder = INITIAL_REMAINDER

		NumberOfBytesToCRC = len(bufferToCRC)
		self.debug_print("CRC: No. of bytes : %d " % NumberOfBytesToCRC)
		# ensure 32bits
		if(NumberOfBytesToCRC % 4):
			status = FALSE		
		else:
			Index = 0
			while(Index < NumberOfBytesToCRC):
				# Now calculate the CRC with the last data
				short = np.uint16(ord(bufferToCRC[Index]))
				short  = 0x00ff & short
				tmp = (np.uint16(remainder) >> 8) ^ np.uint16(short)
				remainder = np.uint16((np.uint16(remainder) << 8) ^ crcTable[tmp])	
				Index += 1

		return (remainder)	
		
	def _Checksum_Calculate(self, bufferToChecksum):
		NumberOfBytesToCRC = len(bufferToChecksum)
		self.debug_print("Checksum: No. of bytes : %d " % NumberOfBytesToCRC)
		# ensure 32bits
		U32Checksum = 0
		if(NumberOfBytesToCRC % 4):
			status = FALSE		
		else:
			Index = 0
			while(Index < NumberOfBytesToCRC):
				# Now calculate the CRC with the last data
				U32Checksum += np.uint32(ord(chr(bufferToChecksum[Index])))
				Index += 1

		return (U32Checksum)		

	def debug_enable(self, debug_enable_flag):
		self._debug = debug_enable_flag

	def debug_print(self, print_string):
		if self._debug:
			print(print_string)
		
	def F32PETest(self, U32Cmd):
		Status = False
		
		Cmd32 = cmd.array('I', [])
		retval = 0
		#set exec command
		U32Data = 0
		U32Data = self._set_hiword(U32Data, U32Cmd)
		U32Data = self._set_loword(U32Data, 0x1)	
		Cmd32.append(U32Data)
		
		#Execute command
		(Cmd32Res, ResBuff) = self._send_command(Cmd32)
		
		if self._HIWORD(Cmd32Res[0]) == U32Cmd:
			Status = True
			retval = self._LOWORD(Cmd32Res[0])		
		return retval		
		
	def F32GetPEVersion(self):
		Status = False
		
		Cmd32 = cmd.array('I', [])
		PEVersion = 0
		#set exec command
		U32Data = 0
		U32Data = self._set_hiword(U32Data, PE_COMMAND_EXEC_VERSION)
		U32Data = self._set_loword(U32Data, 0x1)	
		Cmd32.append(U32Data)
		
		#Execute command
		(Cmd32Res, ResBuff) = self._send_command(Cmd32)
		
		self.debug_print('F32GetPEVersion:: %s' % Cmd32Res.tobytes())	
		if self._HIWORD(Cmd32Res[0]) == PE_COMMAND_EXEC_VERSION:
			Status = True
			PEVersion = self._LOWORD(Cmd32Res[0])		
		return PEVersion

	def ResetDevice(self):
		Status = False
		Cmd32 = cmd.array('I', [])
		PEVersion = 0
		U32Data = 0
		U32Data = self._set_hiword(U32Data, PE_CMD_RESET_DEVICE)
		U32Data = self._set_loword(U32Data, 0x1)	
		Cmd32.append(U32Data)
		(Cmd32Res, ResBuff) = self._send_command(Cmd32)
		print('Reset Command Sent')
		return Status
	def F32GetDevID(self):
		Status = False
		
		Cmd32 = cmd.array('I', [])
		
		#set exec command
		U32Data = 0
		U32Data = self._set_hiword(U32Data, PE_CMD_GET_DEVICEID)
		U32Data = self._set_loword(U32Data, 0x1)	
		Cmd32.append(U32Data)
		
		#Execute command
		(Cmd32Res, ResBuff) = self._send_command(Cmd32)
		DevID = 0
		self.debug_print('F32GetDevID:: %s' % Cmd32Res.tobytes())	
		if self._HIWORD(Cmd32Res[0]) == PE_CMD_GET_DEVICEID:
			Status = True
			U32DevID = cmd.array('I', [])
			U32DevID.frombytes(ResBuff[0:4])
			DevID = self._HIWORD(U32DevID[0]) << 16 | self._LOWORD(U32DevID[0])
			self.debug_print(hex(DevID))
		return DevID		

	def F32EnterTMOD0(self):
		#Yet to implement TMOD0 pattern sequence		
		####################################

		comlist = serial.tools.list_ports.comports()
		for element in comlist:
			try:
				self.UartIntf = serial.Serial(element.device, 115200)		
				if self.F32GetPEVersion() > 0:
					self.debug_print("Connected COM ports: " + str(element.device) + str(self.F32GetPEVersion()))
					return True
			except serial.SerialException:
				self.debug_print("Not Connected COM ports: " + str(element.device))
				pass
		self.UartIntf = 0
		return False

	def F32BlankCheck(self, StartingAddress, Size):
		Status = False
		Cmd32 = cmd.array('I', [])

		#set exec command
		U32Data = 0
		U32Data = self._set_hiword(U32Data, PE_CMD_BLANK_CHECK)
		U32Data = self._set_loword(U32Data, 0x1)	
		Cmd32.append(U32Data)

		# send out the address
		U32Data = self._set_hiword(U32Data, self._HIWORD(StartingAddress))
		U32Data = self._set_loword(U32Data, self._LOWORD(StartingAddress))		
		Cmd32.append(U32Data)
		
		# send out the length
		U32Data = self._set_hiword(U32Data, self._HIWORD(Size))
		U32Data = self._set_loword(U32Data, self._LOWORD(Size))
		Cmd32.append(U32Data)
		
		#Execute command
		(Cmd32Res, ResBuff) = self._send_command(Cmd32)
		
		self.debug_print('F32BlankCheck:: %s' % Cmd32Res.tobytes())	
		if self._HIWORD(Cmd32Res[0]) != PE_CMD_BLANK_CHECK or self._LOWORD(Cmd32Res[0]):
			Status = False
		else:
			Status = True
		return Status

	def F32Erase(self, StartingAddress, U32Size):
		Status = True
		QueueLoc = 0
		Cmd32 = cmd.array('I', [])
		
		# send out opcode
		U32Data = int(U32Size / PROG_CLUSTER_SIZE)
		if (U32Size % PROG_CLUSTER_SIZE > 0):
			U32Data += 1
		U32Data = self._set_hiword(U32Data, PE_CMD_CHIP_ERASE)
		Cmd32.append(U32Data)
		QueueLoc += 1

		# send out the address
		Cmd32.append(StartingAddress)	
		QueueLoc += 1	

		#Execute command
		(Cmd32Res, ResBuff) = self._send_command(Cmd32)

		# make sure the response is the command and there is no errors
		if (self._HIWORD(Cmd32Res[0]) != PE_CMD_CHIP_ERASE or self._LOWORD(Cmd32Res[0])):
			Status = False
		else:
			Status = True
	  
		return Status

	def F32PageErase(self, StartingAddress, U32Size):
		Status = True
		QueueLoc = 0
		Cmd32 = cmd.array('I', [])
		
		# send out opcode
		U32Data = int(U32Size / ERASE_PAGE_SIZE)
		if (U32Size % ERASE_PAGE_SIZE > 0):
			U32Data += 1
		U32Data = self._set_hiword(U32Data, PE_CMD_PAGE_ERASE)
		Cmd32.append(U32Data)
		QueueLoc += 1

		# send out the address
		Cmd32.append(StartingAddress)	
		QueueLoc += 1	

		#Execute command
		(Cmd32Res, ResBuff) = self._send_command(Cmd32)

		# make sure the response is the command and there is no errors
		if (self._HIWORD(Cmd32Res[0]) != PE_CMD_PAGE_ERASE or self._LOWORD(Cmd32Res[0])):
			Status = False
		else:
			Status = True
	  
		return Status

	def _F32PgmRangeNonPage(self, FileData, StartingAddress, U32Size, U16CFGMethod):
		Status = True
		U32BlockSize = 0
		QueueLoc = 0
		Cmd32 = cmd.array('I', [])	
		i = 0;
		self.debug_print("_F32PgmRangeNonPage size = %d" % U32Size)
		# make sure it divides
		if U32Size % 4:
			Status = False
			self.debug_print("Problem with Size")
		else:
			while (U32Size > 0 and Status == True):
				# Takes bytes
				if U32Size < PROG_CLUSTER_SIZE:
					U32BlockSize = U32Size
				else:
					U32BlockSize = PROG_CLUSTER_SIZE

				U32Size -= U32BlockSize
					# send out opcode
				QueueLoc = 0
				U32Data = 0
				U32Data = self._set_hiword(U32Data, PE_CMD_PGM_CLUSTER_VERIFY)
				U32Data = self._set_loword(U32Data, U16CFGMethod)				
				Cmd32.append(U32Data)
				QueueLoc += 1
				
				# send out the address
				U32Data = self._set_hiword(U32Data, self._HIWORD(StartingAddress))
				U32Data = self._set_loword(U32Data, self._LOWORD(StartingAddress))		
				Cmd32.append(U32Data)
				QueueLoc += 1
				
				# send out the length
				U32Data = self._set_hiword(U32Data, self._HIWORD(U32BlockSize))
				U32Data = self._set_loword(U32Data, self._LOWORD(U32BlockSize))
				Cmd32.append(U32Data)
				QueueLoc += 1
				
				# send out the checksum val
				if U16CFGMethod == self.PE_USE_CRC:
					U32Checksum = self._CRC16_Calculate(FileData[i:int(i+U32BlockSize)])
				else:
					U32Checksum = self._Checksum_Calculate(FileData[i:int(i+U32BlockSize)])
				self.debug_print(U32Checksum)
				U32Data = self._set_hiword(U32Data, self._HIWORD(U32Checksum))
				U32Data = self._set_loword(U32Data, self._LOWORD(U32Checksum))
				Cmd32.append(U32Data)
				QueueLoc += 1
				
				# Update the address for the next rotation
				StartingAddress += U32BlockSize
				
				while (i < U32BlockSize):
					U32Data = FileData[i:int(i+4)]
					Cmd32.frombytes(U32Data)
					i += 4

				#Execute command
				(Cmd32Res, ResBuff) = self._send_command(Cmd32)

				# make sure the response is the command and there is no errors
				if (self._HIWORD(Cmd32Res[0]) != PE_CMD_PGM_CLUSTER_VERIFY or self._LOWORD(Cmd32Res[0])):
					print("F32PgmRangeNonPage:: Failed")
					Status = False
				else:
					Status = True
				del Cmd32[:]
		return Status

	def _F32PgmRangeFullRows(self, FileData, StartingAddress, U32Size, U16CFGMethod):
		# convert to locations
		Status = True
		i = 0;
		Cmd32 = cmd.array('I', [])
		U32BlockSize = PROG_CLUSTER_SIZE
		# Initial call to print 0% progress
		loop = 0
		U32Iterations = U32Size/U32BlockSize
		self._printProgressBar(loop, U32Iterations, prefix = 'Progress:', suffix = 'Complete', length = 50)
		k = U32BlockSize
		# Now do what we need to do
		while (U32Size > 0 and Status==True):
			QueueLoc = 0
			U32Data = 0
			U32Data = self._set_hiword(U32Data, PE_CMD_PGM_CLUSTER_VERIFY)
			U32Data = self._set_loword(U32Data, U16CFGMethod)				
			Cmd32.append(U32Data)
			QueueLoc += 1
			
			# send out the address
			U32Data = self._set_hiword(U32Data, self._HIWORD(StartingAddress))
			U32Data = self._set_loword(U32Data, self._LOWORD(StartingAddress))		
			Cmd32.append(U32Data)
			QueueLoc += 1
			
			# send out the length
			U32Data = self._set_hiword(U32Data, self._HIWORD(U32BlockSize))
			U32Data = self._set_loword(U32Data, self._LOWORD(U32BlockSize))
			Cmd32.append(U32Data)
			QueueLoc += 1
			
			# send out the checksum val
			if U16CFGMethod == self.PE_USE_CRC:
				U32Checksum = self._CRC16_Calculate(FileData[i:int(i+U32BlockSize)])
			else:
				U32Checksum = self._Checksum_Calculate(FileData[i:int(i+U32BlockSize)])
			self.debug_print(U32Checksum)
			#self.debug_print(U32Checksum)
			U32Data = self._set_hiword(U32Data, self._HIWORD(U32Checksum))
			U32Data = self._set_loword(U32Data, self._LOWORD(U32Checksum))
			Cmd32.append(U32Data)
			QueueLoc += 1
			
			# Update the address for the next rotation
			StartingAddress += U32BlockSize
			U32Size -= U32BlockSize
			csum = 0
			
			while (i < k):
				U32Data = FileData[i:int(i+4)]
				Cmd32.frombytes(U32Data)
				csum += (Cmd32[QueueLoc] >> 24) & 0xff
				csum += (Cmd32[QueueLoc] >> 16) & 0xff		
				csum += (Cmd32[QueueLoc] >> 8) & 0xff
				csum += (Cmd32[QueueLoc]) & 0xff				
				QueueLoc += 1
				i += 4
			k += U32BlockSize
			self.debug_print("Computed csum = %d" % csum)
			#Execute command
			(Cmd32Res, ResBuff) = self._send_command(Cmd32)

			# make sure the response is the command and there is no errors
			if (self._HIWORD(Cmd32Res[0]) != PE_CMD_PGM_CLUSTER_VERIFY or self._LOWORD(Cmd32Res[0])):
				print("F32PgmRangeFullRows:: Failed %d" % U32Size)
				Status = False
			else:
				Status = True
			del Cmd32[:]
			loop += 1
			self._printProgressBar(loop, U32Iterations, prefix = 'Progress:', suffix = 'Complete', length = 50)
				
		return Status
		
	def F32ProgClusterVerify(self, ImageFile, StartingAddress, U16CFGMethod):
		Status = True
		self.debug_print("Opening flash image.")
		
		# Read hexfile content	
		fd = open(ImageFile, 'rb')
		FileData = fd.read()
		U32Size = len(FileData)
	
		if self.F32PageErase(StartingAddress, U32Size) == True:
			self.debug_print("Erasing Flash...success")
		else:
			self.debug_print("Erasing Flash...failed")
			return False

		U32StartIndex = 0
		U32BlockSize = 0
		print('Loading Image ...(Size: %d)' % U32Size)		
		if StartingAddress % PROG_CLUSTER_SIZE:
			U32BlockSize = PROG_CLUSTER_SIZE - (StartingAddress % PROG_CLUSTER_SIZE)
			self.debug_print("startIndex =%d blocksize =%d Size =%d" % (startIndex, U32BlockSize, U32Size))
			if U32BlockSize > U32Size:
				U32BlockSize = U32Size
			U32Size -= U32BlockSize
			Status = self._F32PgmRangeNonPage(FileData, StartingAddress, U32BlockSize, U16CFGMethod)
			StartingAddress += U32BlockSize
			FileData += U32BlockSize
		
		if U32Size==0 or not(Status):
			return Status

		# make sure it divides
		if (U32Size % PROG_CLUSTER_SIZE):
			self.debug_print("blocksize =%d Size =%d BLOCK_SIZE =%d" % (U32BlockSize, U32Size,PROG_CLUSTER_SIZE))	
			U32BlockSize = int(U32Size / PROG_CLUSTER_SIZE) * PROG_CLUSTER_SIZE
			if U32BlockSize > 0:
				U32Size -= U32BlockSize
				self.debug_print("blocksize =%d Size =%d" % (U32BlockSize, U32Size))
				Status = self._F32PgmRangeFullRows(FileData, StartingAddress, U32BlockSize, U16CFGMethod)
				StartingAddress += U32BlockSize
				FileData = FileData[U32BlockSize:]
			
			if Status:
				Status = self._F32PgmRangeNonPage(FileData, StartingAddress, U32Size, U16CFGMethod)
		else:
			Status = self._F32PgmRangeFullRows(FileData, StartingAddress, U32Size, U16CFGMethod)
		if Status== True:
			self.ResetDevice()
			
		return Status