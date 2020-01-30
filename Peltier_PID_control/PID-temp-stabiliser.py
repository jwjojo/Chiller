import re
import time
import serial
from tenma import Tenma
import logging
import datetime
import os

""" 
Basic PID control script, to stabilise temperature of coldjig, through a feedback loop with the Peltier elements.
we use a normalised error signal based on the deviation between temperature setpoint and input for temperature sensor.
Only P and I feedback is currently implemented, because the system response is so slow that D was deemed unnecessary.
The feedback constants have yet to be properly tuned:

Currently the script is written for the purpose of calibrating the feedback constant:
T_target is the hardcoded setpoint temperature, you then run the script continously, and can, at any time press "ctrl+c" 
to pause the feedback loop and provide new values for the P and I constants - after which the feedback loop.

Ideally one should be able to update the proportionality constants without ever pausing the feedback loop. 
This could be done if you, for each iteration of the loop, loaded these values from a txt file, 
and then used a different script to update this txt file - whenever you please.

How one should go about actually chosing values for the proportionality constant is a matter of physical intution along 
with trial&error.

Bear in mind, this codebse is a work in progress, bugs might be found.

Written by Jonas Steentoft, M.Sc. at NBI.
myname2810@hotmail.com
"""


# test = ["0.55    Humidity(%RH): 33.38     Temperature(C): 2.84",
# 	"0.63    Humidity(%RH): 33.46     Temperature(C): 1.92",
# 	"0.70    Humidity(%RH): 33.63     Temperature(C): 1.03",
	# "0.78    Humidity(%RH): 33.83     Temperature(C): 0.32",
	# "0.86    Humidity(%RH): 34.11     Temperature(C): -0.30",
# 	"0.94    Humidity(%RH): 34.50     Temperature(C): -0.86",
# 	"1.01    Humidity(%RH): 35.06     Temperature(C): -1.33",
# 	"1.09    Humidity(%RH): 35.58     Temperature(C): -1.75"]

def getUserInput(whatToAskFor):
	## takes user input, checks for float or int type and ask for new input in case of wrong type
	UserInput = raw_input(whatToAskFor)
	while type(UserInput) != float:
		try:
			UserInput = float(UserInput)
		except ValueError:
			UserInput = raw_input("Input has wrong format, please input a proper float\n")
	return UserInput


def number_extractor(input_string):
    rr = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", input_string)
    for i in range(len(rr)):
    	rr[i] = float(rr[i])
    return rr
   
# for string in test:
# 	abe = number_extractor(string)
# 	print string
# 	print abe
# 	print
    
starttime = time.time()
now = datetime.datetime.now() # creating a timestamp to use as unique name of logfile
timestamp = "%d.%d.%d--%d.%d"%(now.day,now.month,now.year,now.hour,now.minute)


T0 = serial.Serial('/dev/ttyACM0',9600,serial.EIGHTBITS,serial.PARITY_NONE,serial.STOPBITS_ONE)
if T0.isOpen():
	print(T0.name) # check which port was reaserPort



# quit = 0
# while quit !=1:
# 	try:
# 		print
# 		a = T0.readline()
# 		print a
# 		output = number_extractor(a)
# 		for i in range(10000):
# 			a = 2+4+23+2+3+1235+12+3+123+12+3+123+125+12+4+6+56+124+246+1+34
# 		# print type(output), output

# 	except(KeyboardInterrupt):
# 		quit = 1



logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s", datefmt="%H:%M:%S", level=logging.DEBUG)

PS = Tenma("PS-1","/dev/ttyUSB0")
PS.open() # open device port
print PS.port


quit = 0
T_data = []
V_data = []
time_data = []
error_list = []
target_list = []

K_P_list = []
K_I_list = []

################# PID PARAMETERS ##################
T_target = -30.0
K_P = -1.5
K_I = -0.0
print "attempting to stabilise at T = %.1f Celsius"%(T_target)
## power supply configuration:
V_max = 15.7
V_min = 0.0
V_prior = V_max*0.8
PS.vset = V_prior # set initial voltage
PS.out = 1 # turn output on

iterator = 0
############################################
while quit != 1:
	try:
		iterator +=1
		if len(error_list) > 600: ## we only want the latest N data points, eg to not bias based on previous values of K_I
			del(error_list[0])

		probe_output = T0.readline()
		print "\n", probe_output
		if iterator < 10: ##because ARDUINO sends weird non-data stuff initially
			continue
		output = number_extractor(probe_output)

		if len(output) != 2: 
		## just to reduce the frequency of updating the feedback loop- since system response, 
		## temperature propagation through coldjig, is quite slow.
			continue
		else:
			# print
			time_data.append(time.time()-starttime)
			T_data.append(output)
			K_P_list.append(K_P)
			K_I_list.append(K_I)
			target_list.append(T_target)
			try:
				error = (T_target - output[1])/(T_target + output[1]) ## normalised error signal
			except(ZeroDivisionError):
				print "ZeroDivisionError occured, using abs(T_tar) + abs(T_meas) for normalisation of error signal instead"
				## seems like reality of the code is disagreeing with the print statement?

			error_list.append(error)
			int_error = sum(error_list)/len(error_list)

			print "K_P , K_I , Temp , norm_error , integrated_error"
			print "%.2f , %.2f , %.2f ,   %.2f ,   %.2f"%(K_P, K_I, output[1], error, int_error)



			Volt = V_prior + K_P*error + K_I*int_error ## V_max is the initial voltage applied, used for maximal cooling/heating
			
			if V_min <= Volt and Volt <= V_max:
				PS.vset = Volt
				print("setting voltage to %s V" % Volt)       # set voltage
				V_data.append(Volt)
				V_prior = Volt

			if Volt < V_min:
				PS.vset = V_min
				print "Setting V = V_min = %.1f - since V = %.1f is lower than V_min"%(V_min,Volt)
				V_data.append(V_min)
				V_prior = V_min

			if V_max < Volt:
				PS.vset = V_max
				print "Setting V = V_max = %.1f - since V = %.1f is larger than V_max"%(V_max,Volt)
				V_data.append(V_max)
				V_prior = V_max

	except(KeyboardInterrupt):
		choice = raw_input("press \"q\" to quit or \"p\" to alter PID PARAMETERS and Target temp\n")
		if choice == "q":
			quit = 1

		elif choice == "p":
			K_P = getUserInput("Enter new value of K_P\n")
			K_I = getUserInput("Enter new value of K_I\n")
			T_target = getUserInput("Enter new value of T_target\n")




""""
This section is related to logfiling, it auto-generates a logfile with all relevant data, if ShouldWeCreateFile = "y"
overwrite protection wrt filename is included.
If anyhting goes wrong in filewriting, we ensure power supply is still properly turned off.
"""

onlyName = "PID-log" + timestamp
namestring = "PID-log" + timestamp + "-0"

try:
	error_log = []
	for i in range(len(T_data)):
		bae = ( target_list[i] - T_data[i][1] )/(target_list[i] + T_data[i][1])
		error_log.append(bae) ## normalised error signal
	
	ShouldWeCreateFile = "y"

	if ShouldWeCreateFile == "y" or ShouldWeCreateFile == "cus":
		if not os.path.isfile("%s.txt"%(namestring) ):

			print len(time_data) , len(K_P_list) , len(K_I_list) , len(T_data) ,len(error_log) ,len(V_data)
			nfile = open("%s.txt"%(namestring),"w+")
			nfile.write("time[s], K_P , K_I , Temp [C] , norm_error_sig, Volt[V], RH[%]")
			for i in range(len(T_data)):
				try:
					nfile.write("%.2f %.3f %.3f %.2f %.3f %.2f %.2f\n"%(time_data[i], K_P_list[i],K_I_list[i],T_data[i][1],error_log[i],V_data[i], T_data[i][0]))
				except(IndexError):
					nfile.write("IndexError occured")
			nfile.close()
		
		else:
			dummy = 0
			newName = onlyName + "-" + str(dummy)

			while os.path.isfile(newName+".txt"): ##finding unoccupied filename
				dummy +=1
				newName = onlyName + "-" + str(dummy)

			print len(time_data) , len(K_P_list) , len(K_I_list) , len(T_data) ,len(error_log) ,len(V_data)
			nfile = open(newName + ".txt","w+")
			nfile.write("time[s], K_P , K_I , Temp [C] , norm_error_sig, Volt[V]")
			for i in range(len(T_data)):
				try:
					nfile.write("%.2f %.3f %.3f %.2f %.3f %.2f %.2f\n"%(time_data[i], K_P_list[i],K_I_list[i],T_data[i][1],error_log[i],V_data[i], T_data[i][0]))
				except(IndexError):
					nfile.write("IndexError occured")
			nfile.close()
			print "%s is done"%(newName)

except:	
	PS.vset = 0.0 # set output to 0
	PS.out = 0 # turn output off
	PS.close() # close device port
	T0.close()	# close temp sensor port
	raise






PS.vset = 0.0
PS.out = 0 # turn output off
PS.close() # close device port
T0.close()	