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
flash_load.py
"""

import optparse
import sys
import time
from progctrlOptimized import ProgController

if __name__ == '__main__':
	Help = "eg. python flash_interface -c COM4 -o program -f HellowWorld.hex"
	parser = optparse.OptionParser()
	parser.add_option("-i", dest="filename", default="", help="hex file to burn flash")
	parser.add_option("-v", dest="verbose", default=False, help="Enable debug prints.")	
	
	timeout = int(0)
	timeoutVerify = int(0)
	
	while True:
		print(" **** Reset the board to boot in DFU Mode at startup**** ")
		#print(str(timeout) + " seconds")
		if timeout >= 30:
			sys.exit()
		start = time.time()
		(options, args) = parser.parse_args()
		if options.filename =='':
			print("ERROR: missing hex/bin file:\n" + Help)
			sys.exit()	
			
		progCtrl = ProgController()
		
		if progCtrl == 0:
			print("ERROR: Failed to create Programming controller")
			sys.exit()	

		progCtrl.debug_enable(options.verbose)	
		
		if progCtrl.F32EnterTMOD0() == True:
			startTimeVerify = time.time()
			if progCtrl.F32ProgClusterVerify(options.filename, 0x01080000, progCtrl.PE_USE_CHECKSUM) == True:
				progCtrl.debug_print("F32ProgClusterVerify: success")
				sys.exit()
			else:
				print("F32ProgClusterVerify: failed")
			endTimeVerify = time.time()
			timeoutVerify += (end - start)
			#print(str(timeoutVerify) + " seconds")
		end = time.time()
		timeout += (end - start)