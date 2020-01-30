import serial
import time
"""
Simple script to log temp and humidity from two small sensor boxes put together by 
Jan Oeschle. The read-out didnt work in a stable an consistent manner, acording to Jan
due to the use of some less than optimal drivers for the sensor boxes.
Written by Jonas Steentoft
myname2810@hotmail.com
"""

starttime = time.time()

T0 = serial.Serial('/dev/ttyACM0',9600,serial.EIGHTBITS,serial.PARITY_NONE,serial.STOPBITS_ONE)
T0.timeout = 1.1
# T0.xonxoff = 1

if T0.isOpen():
	print(T0.name) # check which port was reaserPort

T1 = serial.Serial('/dev/ttyACM1',9600,serial.EIGHTBITS,serial.PARITY_NONE,serial.STOPBITS_ONE)
T1.timeout = 1.1
# T1.xonxoff = 1
# T1.rtscts = True
if T1.isOpen():
	print(T1.name) # check which port was reaserPort

quit = 0
data = []
timedata = []
data1 = []
iterator = 0
while quit != 1:
	try:
		print "iterator = ", iterator
		iterator += 1
		b = T1.readline()
		a = T0.readline()
		print "T0:  ", a
		print "T1:  ",b
		data.append(a)
		data1.append(b)
		timedata.append((time.time()-starttime)/60.)
		print timedata[-1],"\n"
	except(KeyboardInterrupt):
		quit = 1


# T0.close()
T1.close()

filename = "temp-read-ARDUINO-0-081119-cycle204020.txt"
with open(filename,"w+") as file:

	file.write("\n\n\nTid[min, RH, Temp[C]")
	for i in range(len(data)):
		file.write("%.2f    "%timedata[i] + data[i])


filename = "temp-read-ARDUINO-1-081119-cycle204020.txt"
with open(filename,"w+") as file:
	file.write("\n\n\nTid[min, RH, Temp[C]")
	for i in range(len(data1)):
		file.write("%.2f    "%timedata[i] + data1[i])		

