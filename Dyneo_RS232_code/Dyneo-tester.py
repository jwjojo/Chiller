import logging
import time
import Dyneo
"""
Test script to demonstrate communicating the DYNEO chiller.
Created by Jonas Steentoft as part of M.SC project at NBI
myname2810@hotmail.com

make sure cable is connected to chiller, before turning on the machine
but NOT connected to the pc, otherwise it wont make a
succesful connection.

Also, the chiller needs to be configured to remote control operation,
this is done using hte display on the chiller and the manual.
"""

logging.basicConfig(level=logging.DEBUG) 

coldbox = Dyneo.Dyneo("/dev/ttyACM0")

coldbox.open()

# Tbath = coldbox.fluidTemp()
# print Tbath
coldbox.SetTemp(-13.3)

# coldbox.start()
# # raw_input("press ENTER to continue")


# coldbox.stop()

coldbox.close()