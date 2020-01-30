import logging
import serial
import time
"""
class to control Tenma power supply through RS-232 coms protocol.
Written by Catherine Hogh - summer student at NBI.
"""
log = logging.getLogger(__name__)

############################################################################
class Tenma(object):
    
    """ Remote control interface to TENMA 72-2930 """
    def __init__(self, name, port, timeout=1.0):
        
        self.__name = name
        self.__port = port
        self.__ser = serial.Serial()
        self.__ser.timeout = timeout
    
    def open(self):
        """ open serial port """
        self.__ser.port = self.__port
        try:
            self.__ser.open()
            self.__ser.write("*IDN?")
            log.debug("successfully connected device on port: " + self.__port)
            log.debug("device:" + self.__ser.readline())
        except serial.SerialException:
            log.error("failed to connect to a device on port: " + self.__port)
    
    def close(self):
        """ close serial port """
        self.__ser.close()
    
    def write(self, cmd):
        """ write command to tenma """
        x = self.__ser.write(cmd)
        time.sleep(1)
        return x
    
    def read(self):
        """ read output from tenma """
        return self.__ser.readline()
    
    # properties ----------------------------------------------------------#
    @property
    def name(self):
        return self.__name
    
    @property
    def port(self):
        return self.__port
    #----------------------------------------------------------------------#
    @property
    def out(self):
        return None
    
    @out.setter
    def out(self, X):
        return self.write("OUT" + str(X))
    
    @property
    def vset(self):
        self.write("VSET1?")
        return self.read()
    
    @vset.setter
    def vset(self, V):
        return self.write("VSET1:" + str(V))
    
    @property
    def vout(self):
        self.write("VOUT1?")
        return self.read()
############################################################################
