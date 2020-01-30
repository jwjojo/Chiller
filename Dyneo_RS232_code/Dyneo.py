import serial
import logging
"""class to control DYNEO DD 1000F chiller, heavily inspired by the Warwick code to control their GRANT chiller.
Created by Jonas Steentoft as part of M.SC project at NBI
myname2810@hotmail.com
"""

class Dyneo(object):
	def __init__(self,port,timeout=1.0):
		self.port = port
		self.timeout = timeout
		logging.info("Created Dyneo object")

	def open(self):
		# Open serial port to the chiller
		logging.info("Opening serial port to DYNEO chilller")
		try:
			self.serPort = serial.Serial(self.port,
				  4800,
				  serial.SEVENBITS,
				  serial.PARITY_EVEN,
				  serial.STOPBITS_ONE,
				  self.timeout)

			if self.serPort.isOpen():
				addr = self.serPort.name
				logging.info("Serial port to GRANT chiller opened at address " + addr) 
			self.serPort.reset_input_buffer()
			self.serPort.reset_output_buffer()   

		except serial.SerialException :
			logging.critical("Failed to open and/or configure device on port %s",self.port)
			self.serPort = None

			
	def close(self) :
		# Check serial port was opened before proceeding
		if self.serPort is None :
			logging.critical("Serial port not opened. No port to close")
			return 

		# Flush input/output buffer and discard contents
		self.serPort.reset_input_buffer()  
		self.serPort.reset_output_buffer()

		# Close port
		self.serPort.close()
		logging.info("Serial port to GRANT closed")



	def read(self) :
		# Method to read messages from DYNEO chiller
		# Check serial port was opened before proceeding
		if self.serPort is None :
			logging.critical("Serial port not opened. Cannot read any message")
			return None
		else:
			logging.info("Reading message from GRANT")
			data_str = self.serPort.readline()
			logging.info(data_str)
			return data_str


	def write(self,message_type="",message_data=""):
		# Check serial port was opened before proceeding
		if self.serPort is None :
			logging.critical("Serial port not opened. Cannot write any message")
			return
		if len(message_data) == 0:
			message = message_type + "\r"
		else:
			message = message_type + " " + message_data + '\r'
		
		logging.info("Sending message: \"%s\"",message)

		try :
			self.serPort.write(message)            
		except serial.SerialTimeoutException :
			logging.error("Timeout Error while writing")
		except serial.SerialException :
			logging.error("Serial Port Exception...is the port open ?")
		except :
			logging.error("Error with Pyserial")
			
		return


	def fluidTemp(self): ## current temp of cooling fluid
		logging.info("Reading out current coolant temperature")
		self.write("in_pv_00")
		data_str = self.read()
		TT = float( data_str.strip() )
		return TT


	def SetTemp(self,T): ## sets temp of cooling fluid
		logging.info("Setting coolant target temperature")
		# self.write("in_sp_00",str(T))
		self.write("out_sp_00",str(T))
		return 



	def start(self):##start the chiller
		self.write("out_mode_05","1")
		return

	def stop(self):## stop the chiller
		self.write("out_mode_05","0")
		return