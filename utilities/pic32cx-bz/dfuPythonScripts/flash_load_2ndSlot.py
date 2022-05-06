#!/usr/bin/python

"""
flash_load.py
"""

import optparse
import sys
from progctrl import ProgController

if __name__ == '__main__':
	Help = "eg. python flash_interface -c COM4 -o program -f HellowWorld.hex"
	parser = optparse.OptionParser()
	parser.add_option("-i", dest="filename", default="", help="hex file to burn flash")
	parser.add_option("-v", dest="verbose", default=False, help="Enable debug prints.")	
	
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
		if progCtrl.F32ProgClusterVerify(options.filename, 0x01080000, progCtrl.PE_USE_CHECKSUM) == True:
			progCtrl.debug_print("F32ProgClusterVerify: success")
		else:
			print("F32ProgClusterVerify: failed")