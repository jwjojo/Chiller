import logging
from tenma import Tenma
"""
Test script for the Temna power supply RS232 coms protocol
Written by Catherine Hogh - summer student at NBI.
"""

logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s", datefmt="%H:%M:%S", level=logging.DEBUG)

PS = Tenma("PS-1","/dev/ttyUSB0")
PS.open() # open device port

print PS.port

PS.vset = 0 # set voltage to 0.00 V before turning on the output (to avoid any surprises)
PS.out = 1 # turn output on

inpt = ""
while inpt != "q":
	inpt = raw_input("enter Voltage 0-15V or q for quit\n")
	if inpt != "q":
		PS.vset = float(inpt)
		print("setting voltage to %s V" % float(inpt))       # set voltage
		print("current voltage is %s V" % PS.vset) # get voltage
	
	
	

PS.out = 0 # turn output off
PS.close() # close device port
