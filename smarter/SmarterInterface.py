# -*- coding: utf-8 -*-

import socket
import os
import sys
import codecs

reload(sys)  
sys.setdefaultencoding('utf8')

import random
import time
import datetime
import logging
import logging.handlers
import platform
import urllib
from operator import itemgetter

try:
    import win_inet_pton
except Exception:
    pass
    
from ConfigParser import *

import traceback
import threading

from SmarterProtocol import *

#------------------------------------------------------
# SMARTER CLIENT INTERFACE
#
# Python interface to Smarter Appliances
#
# https://github.com/Tristan79/iBrew
#
# Copyright © 2017 Tristan (@monkeycat.nl). All Rights Reserved
#
# The Dream Tea
#------------------------------------------------------


def _threadsafe_function(fn):
    """decorator making sure that the decorated function is thread safe"""
    lock = threading.Lock()
    def new(*args, **kwargs):
        
        lock.acquire()
        try:
            r = fn(*args, **kwargs)
        except Exception as e:
            #s = traceback.format_exc()
            #logging.debug(s)
            #logging.debug(e)
            raise e
        finally:
            lock.release()
        return r
        
    # This fixes the pydoc when used
    new.__name__=fn.__name__
    new.__doc__=fn.__doc__
    return new


#------------------------------------------------------
# iKettle LEGACY CLIENT INTERFACE CLASS
#------------------------------------------------------



class SmarterInterfaceLegacy():

    def __init(self):
        self.temperature        = SmarterLegacy.status100c
        self.temperatureSelect  = False
        self.keepwarm           = SmarterLegacy.statusWarm10m
        self.keepwarmSelect     = False
        self.heaterOn           = False
        self.keepwarmOn         = False
        self.onBase             = False
        self.keepwarmFinished   = False
        self.heatingFinished    = False
        self.overheated         = False
    
    def __init__(self,host=SmarterLegacy.DirectHost,port=SmarterLegacy.Port):
        self.port = port
        self.host = host
        self.dump = False
        self.connected = False
    
        self.__init()
   
        self.simTemperature     = SmarterLegacy.status100c
        self.simTemperatureSelect = False
        self.simKeepwarm        = SmarterLegacy.statusWarm10m
        self.simKeepwarmSelect  = False
        self.simHeaterOn        = False
        self.simKeepwarmOn      = False
        self.simOnBase          = False
        self.simKeepwarmFinished= False
        self.simHeatingFinished = False
        self.simOverheated      = False


        self.emuTemperature     = SmarterLegacy.status100c
        self.emuTemperatureSelect = False
        self.emuKeepwarm        = SmarterLegacy.statusWarm10m
        self.emuKeepwarmSelect  = False
        self.emuHeaterOn        = False
        self.emuKeepwarmOn      = False
        self.emuOnBase          = False
        self.emuKeepwarmFinished= False
        self.emuHeatingFinished = False
        self.emuOverheated      = False
        
        self.simulation         = False
        self.emulation          = False
        self.bridge             = False
        
        self.relay              = False
        self.relayHost         = ''
        self.relayPort         = SmarterLegacy.Port
    
        self.socket             = None
    
        self.__clients          = dict()
    

    def trash(self):
        self.relay_stop()
        self.disconnect()
    
     #------------------------------------------------------
    # CLIENT CONNECTION
    #------------------------------------------------------


    
    def __monitor_device(self):
        if self.dump:
            logging.info("[" + self.host + "] Monitor Running")
        
        monitorCount = 0
   
        timeout = 60
        self.monitor_run = True
        while self.monitor_run:
            try:
                self.__read()
                monitorCount += 1
            except Exception, e:
                print str(e)
            try:
                    if monitorCount % timeout == timeout - 9:
                        self.status()
 
                    if monitorCount % timeout == timeout - 19:
                        self.status()
                    
                    if monitorCount % timeout == timeout - 29:
                        self.status()
                    
                    if monitorCount % timeout == timeout - 39:
                        self.status()
                    
                    if monitorCount % timeout == timeout - 49:
                        self.status()
                    
                    if monitorCount % timeout == timeout - 50:
                        self.status()
                
            except Exception, e:
                print str(e)

        if self.dump:
            logging.info("[" + self.host + "] Monitor Stopped")
 

    def normal(self):
        self.relay_stop()
        self.emulation = False
        self.simulation = False
    
    
    def simulate(self,host="",port=SmarterLegacy.Port):
        self.simulation = True
        self.relay_stop()
        self.disconnect()
        self.host = "simulation"
        self.port = SmarterLegacy.Port
        self.relay_start(host,port)


    def bridge(self,iKettle2,host="",port=SmarterLegacy.Port):
        self.relay_stop()
        self.disconnect()
        self.emulation = True
        self.simulation = False
        self.iKettle2 = iKettle2
        self.emuOnBase = iKettle2.onBase
        self.emuHeaterOn = iKettle2.heaterOn
        self.emuKeepwarmOn = iKettle2.keepWarmOn
        self.relay_start(host,port)
    
    
    def connect(self,monitor=False):
        
        self.disconnect()

        if self.emulation and self.dump:
            logging.debug("[" + self.host + ":" + str(self.port) + "] Connecting emulation")
            return

        if self.simulation and self.dump:
            logging.debug("[" + self.host + ":" + str(self.port) + "] Connecting simulation")
            return


        if self.dump:
            logging.debug("[" + self.host + ":" + str(self.port) + "] Connecting")
        
        if self.simulation:
            return
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # settimeout at least 2
            self.socket.settimeout(10)
            self.socket.connect((self.host,self.port))
        except socket.timeout:
            raise SmarterErrorOld("Could not connect to " + self.host + ":" +  str(self.port))
        except socket.error:
            raise SmarterErrorOld("Could not connect to " + self.host + ":" +  str(self.port))
        

        try:
            self.socket.send(SmarterLegacy.commandHandshake+"\n")
            #data = self.send(SmarterLegacy.commandHandshake)
            data =  self.__read() #self.socket.recv(len(SmarterLegacy.commandHandshake)+1)
        except socket.timeout:
            raise SmarterErrorOld("No kettle found at " + self.host + ":" +  str(self.port))
            self.disconnect()
        except socket.error:
            raise SmarterErrorOld("No kettle found at " + self.host + ":" +  str(self.port))
            self.disconnect()

        if len(data) < 8:
            self.disconnect()
            raise SmarterErrorOld("No kettle found at " + self.host + ":" +  str(self.port))
        if data[0:8] != SmarterLegacy.responseHandshake[0:8]:
            self.disconnect()
            raise SmarterErrorOld("No kettle found at " + self.host + ":" +  str(self.port))
        self.connected = True


    def disconnect(self):
        if self.connected and self.dump:
            logging.debug("[" + self.host + ":" + str(self.port) + "] Disconnecting")
        self.__init()
        self.connected = False
        if self.socket:
            self.socket.close()


    def __read(self):
        try:
            d = self.socket.recv(1)
            data = d
            while d != '\r':
                d = self.socket.recv(1)
                data += d
            self.__decode_response(data)
        except socket.timeout:
            data = None
        #print "READ: " + data
        return data[:-1]

    def send(self,command):
        if self.emulation:
            response = self.emu_response(command)
            for data in response:
                self.__decode_response(data)
        elif self.simulation:
            response = self.sim_response(command)
            for data in response:
                self.__decode_response(data)
        else:

            if not self.connected:
                print self.connected
                self.connect()

            if self.dump:
                logging.debug("[" + self.host + ":" + str(self.port) + "] Sending: " + SmarterLegacy.command_to_commandText(command) + " [" + command + "]")
            try:
                self.socket.send(command+"\n")
            except socket.error:
                self.disconnect()
                raise SmarterErrorOld("[" + self.host + ":" + str(self.port) + "] Connection timed out")
            response = []
            try:
                m = 2
                if command == SmarterLegacy.commandHandshake:
                    m = 1
                for i in range(0,m):
                    data = self.__read()
                    if data is None:
                        break;
                    response += [data]
                    if self.dump:
                        s = SmarterLegacy.string_response(data)
                        logging.debug("[" + self.host + ":" + str(self.port) + "] Received: " + s + " [" + data + "]")

            except Exception, e:
                pass #raise SmarterErrorOld("[" + self.host + ":" + str(self.port) + "] Connection timed out")
        return response
    

    def __decode_responseStatus(self,status):

        def is_set(x, n):
            return x & 2**n != 0

        if len(SmarterLegacy.responseStatus) == len(status):
            self.temperatureSelect = False
            self.keepwarmSelect = False
            self.keepwarmFinished = False
            self.heatingFinished = False
            self.onBase = True
            self.keepwarmOn = False
            self.heaterOn = False
            self.overheated = False
            return

        statusdata = Smarter.raw_to_number(status[len(SmarterLegacy.responseStatus)])

        if is_set(statusdata,0):
            self.heatingFinished = False
            self.keepwarmFinished = False
            self.onBase = True
            self.keepwarmOn = False
            self.heaterOn = True
            self.overheated = False
        if is_set(statusdata,1):
            self.keepwarmFinished = False
            self.onBase = True
            self.heaterOn = False
            self.keepwarmOn = True
            self.overheated = False
            self.heatingFinished = False
        if is_set(statusdata,2):
            self.temperatureSelect = True
            self.temperature = SmarterLegacy.status65c
        if is_set(statusdata,3):
            self.temperatureSelect = True
            self.temperature = SmarterLegacy.status80c
        if is_set(statusdata,4):
            self.temperatureSelect = True
            self.temperature = SmarterLegacy.status95c
        if is_set(statusdata,5):
            self.temperatureSelect = True
            self.temperature = SmarterLegacy.status100c
        #if is_set(statusdata,6):
        #    pass
        #if is_set(statusdata,7):
        #    pass


    def __decode_response(self,status):
        if status[0:len(SmarterLegacy.responseStatus)] == SmarterLegacy.responseStatus:
            self.__decode_responseStatus(status)
        elif status == SmarterLegacy.status100c:
            self.temperatureSelect = True
            self.temperature = SmarterLegacy.status100c
        elif status == SmarterLegacy.status95c:
            self.temperatureSelect = True
            self.temperature = SmarterLegacy.status95c
        elif status == SmarterLegacy.status80c:
            self.temperatureSelect = True
            self.temperature = SmarterLegacy.status80c
        elif status == SmarterLegacy.status65c:
            self.temperatureSelect = True
            self.temperature = SmarterLegacy.status65c
        elif status == SmarterLegacy.statusWarm:
            self.keepwarmFinished = False
            self.onBase = True
            self.heaterOn = False
            self.keepwarmOn = True
            self.overheated = False
            self.heatingFinished = False
        elif status == SmarterLegacy.statusWarmFinished:
            self.onBase = True
            self.keepwarmOn = False
            self.heaterOn = False
            self.keepwarmFinished = True
            self.overheated = False
            self.heatingFinished = False
        elif status == SmarterLegacy.statusHeating:
            self.heatingFinished = False
            self.keepwarmFinished = False
            self.onBase = True
            self.keepwarmOn = False
            self.heaterOn = True
            self.overheated = False
        elif status == SmarterLegacy.statusReady:
            self.keepwarmFinished = False
            self.heatingFinished = False
            self.onBase = True
            self.keepwarmOn = False
            self.heaterOn = False
            self.overheated = False
        elif status == SmarterLegacy.statusWarm5m:
            self.keepwarmSelect = True
            self.keepwarm = SmarterLegacy.statusWarm5m
        elif status == SmarterLegacy.statusWarm10m:
            self.keepwarmSelect = True
            self.keepwarm = SmarterLegacy.statusWarm10m
        elif status == SmarterLegacy.statusWarm20m:
            self.keepwarmSelect = True
            self.keepwarm = SmarterLegacy.statusWarm20m
        elif status == SmarterLegacy.statusHeated:
            self.keepwarmFinished = False
            self.onBase = True
            self.keepwarmOn = False
            self.heaterOn = True
            self.overheated = False
            self.heatingFinished = True
        elif status == SmarterLegacy.statusOverheat:
            self.keepwarmFinished = False
            self.keepwarmOn = False
            self.onBase = True
            self.heaterOn = False
            self.overheated = True
            self.heatingFinished = False
        elif status == SmarterLegacy.statusKettleRemoved:
            self.keepwarmFinished = False
            self.overheated = False
            self.heaterOn = False
            self.keepwarmOn = False
            self.onBase = False
            self.heatingFinished = False
        elif status == SmarterLegacy.responseHandshake:
            pass
        else:
            raise SmarterErrorOld("Unknown status! Help! Please post an issues on GitHub" + str([status]))

    #------------------------------------------------------
    # EMULATION: iKettle
    #------------------------------------------------------
    # From iKettle 2.0


    def emu_passthrough(self,command):
        if self.dump:
            logging.debug("[" + self.host + ":" + str(self.port) + "] Passthrough command: " + SmarterLegacy.command_to_string(command))
        if command == SmarterLegacy.commandStop:
            self.iKettle2.kettle_stop()
        elif command == SmarterLegacy.commandHeat:
            keepwarm = 0
            if self.emuKeepwarmSelect:
                if self.emuKeepwarm == SmarterLegacy.statusWarm5m:
                    keepwarm = 5
                elif self.emuKeepwarm == SmarterLegacy.statusWarm10m:
                    keepwarm = 10
                elif self.emuKeepwarm == SmarterLegacy.statusWarm20m:
                    keepwarm = 20
            if self.emuTemperatureSelect:
                if self.emuTemperature == SmarterLegacy.status65c:
                    temperature = 65
                elif self.emuTemperature == SmarterLegacy.status80c:
                    temperature = 80
                elif self.emuTemperature == SmarterLegacy.status95c:
                    temperature = 95
                elif self.emuTemperature == SmarterLegacy.status100c:
                    temperature = 100
            else:
                temperature = 100
            self.iKettle2.kettle_heat(temperature,keepwarm)
        elif command == SmarterLegacy.commandHandshake:
            pass
        elif command == SmarterLegacy.commandStatus:
            pass
        elif command == SmarterLegacy.command65c or command == SmarterLegacy.command80c or command == SmarterLegacy.command95c or command == SmarterLegacy.command100c:
            if command == SmarterLegacy.command65c:     self.emuTemperature = SmarterLegacy.status65c
            if command == SmarterLegacy.command80c:     self.emuTemperature = SmarterLegacy.status80c
            if command == SmarterLegacy.command95c:     self.emuTemperature = SmarterLegacy.status95c
            if command == SmarterLegacy.command100c:    self.emuTemperature = SmarterLegacy.status100c
            self.emuTemperatureSelect = True
        elif command == SmarterLegacy.commandWarm:
            pass
        elif command == SmarterLegacy.commandWarm5m or command == SmarterLegacy.commandWarm10m or command == SmarterLegacy.commandWarm20m:
            if command == SmarterLegacy.commandWarm5m:      self.emuKeepwarm = SmarterLegacy.statusWarm5m
            if command == SmarterLegacy.commandWarm10m:     self.emuKeepwarm = SmarterLegacy.statusWarm10m
            if command == SmarterLegacy.commandWarm20m:     self.emuKeepwarm = SmarterLegacy.statusWarm20m
            self.emuKeepwarmSelect = True
        else:
            raise SmarterErrorOld("Legacy passthrough of command " + command + " not implemented")
        return self.emu_response(command)
    
    def emu_response(self,command):
        if self.dump:
            logging.debug("[" + self.host + ":" + str(self.port) + "] Emulating command: " + SmarterLegacy.command_to_string(command))

        if   command == SmarterLegacy.commandStop:          response = self.__emu_stop()
        elif command == SmarterLegacy.commandHeat:          response = self.__emu_heat()
        elif command == SmarterLegacy.commandHandshake:     response = [SmarterLegacy.responseHandshake]
        elif command == SmarterLegacy.commandStatus:        response = self.__emu_status()
        elif command == SmarterLegacy.command65c or command == SmarterLegacy.command80c or command == SmarterLegacy.command95c or command == SmarterLegacy.command100c:
                                                            response = self.__emu_temperature(command)
        elif command == SmarterLegacy.commandWarm:  response = self.__emu_warm()
        elif command == SmarterLegacy.commandWarm5m or command == SmarterLegacy.commandWarm10m or command == SmarterLegacy.commandWarm20m:
                                                response = self.__emu_keepwarm_minutes()
                                                self.simKeepwarmSelect = True
        else:
            raise SmarterErrorOld("Legacy emulation of command " + command + " not implemented")
        return response

    def __emu_stop(self):
        return [SmarterLegacy.statusReady]

    def __emu_heat(self):
        return [SmarterLegacy.statusHeating] + [self.emuTemperature]
    
    def __emu_status(self):
        return self.__encode_status(self.emuTemperature,self.emuHeaterOn,self.emuKeepwarmOn,self.emuTemperatureSelect)
    
    def __emu_temperature(self):
        return [self.emuTemperature]

    def __emu_warm(self):
        return [self.emuKeepwarm]

    def __emu_keepwarm_minutes(self):
        return [self.emuKeepwarm]
    
  
    
    #------------------------------------------------------
    # EMULATION TRIGGERS: iKettle
    #------------------------------------------------------
    # From iKettle 2.0


    def emu_trigger_warm(self,warm):
        if self.dump:
            logging.debug("[" + self.host + ":" + str(self.port) + "] Emulation Trigger keepwarm " + str(warm))
        self.emuKeepwarmOn = warm


    def emu_trigger_onbase(self,onbase):
        if self.dump:
            logging.debug("[" + self.host + ":" + str(self.port) + "] Emulation trigger onbase " + str(onbase))
        self.emuOnBase = onbase


    def emu_trigger_heating(self,heater):
        if self.dump:
            logging.debug("[" + self.host + ":" + str(self.port) + "] Emulation trigger heater " + str(heater))
        self.emuHeaterOn = heater


    def emu_trigger_temperature(self,temperature):
        self.emuTemperatureSelect = True
        if temperature < 73:
            self.emuTemperature = SmarterLegacy.status65c
        elif temperature < 88:
            self.emuTemperature = SmarterLegacy.status80c
        elif temperature < 97:
            self.emuTemperature = SmarterLegacy.status95c
        else:
            self.emuTemperature = SmarterLegacy.status100c
        if self.dump:
            logging.debug("[" + self.host + ":" + str(self.port) + "] Emulation trigger command temperature " + str(temperature) + " [" + self.emuTemperature + "]")


    def emu_trigger_stop(self):
        if self.dump:
            logging.debug("[" + self.host + ":" + str(self.port) + "] Emulation trigger command stop ")
        self.emuKeepwarmFinished = False
        self.emuHeatingFinished = True
        self.emuKeepwarmOn = False
        self.emuOverheated = False
        self.emuTemperatureSelect = False


    #------------------------------------------------------
    # SIMULATION: iKettle
    #------------------------------------------------------

    def sim_response(self,command):
        if self.dump:
            logging.debug("[" + self.host + ":" + str(self.port) + "] Simulating command: " + SmarterLegacy.command_to_string(command))

        if command == SmarterLegacy.commandStop:    response = self.__sim_stop()
        elif command == SmarterLegacy.commandHeat:  response = self.__sim_heat()
        elif command == SmarterLegacy.commandHandshake:  response = [SmarterLegacy.responseHandshake]
        elif command == SmarterLegacy.commandStatus:response = self.__sim_status()
        elif command == SmarterLegacy.command65c or command == SmarterLegacy.command80c or command == SmarterLegacy.command95c or command == SmarterLegacy.command100c:
                                                response = self.__sim_temperature(command)
                                                self.simTemperatureSelect = True
        elif command == SmarterLegacy.commandWarm:  response = self.__sim_warm()
        elif command == SmarterLegacy.commandWarm5m or command == SmarterLegacy.commandWarm10m or command == SmarterLegacy.commandWarm20m:
                                                response = self.__sim_keepwarm_minutes(command)
                                                self.simKeepwarmSelect = True
        else:
            raise SmarterErrorOld("Legacy simulation of command " + command + " not implemented")
        return response


    def __sim_heat(self):
        self.simHeaterOn = True
        return [SmarterLegacy.statusHeating] + [self.simTemperature]


    def __sim_status(self):
        return self.__encode_status(self.simTemperature,self.simHeaterOn,self.simKeepwarmOn,self.simTemperatureSelect)


    def __encode_status(self,temperature,heaterOn,keepwarmOn,temperatureSelect):
        if not heaterOn and not keepwarmOn and not temperatureSelect: # and not self.simKeepwarmSelect:
            return [SmarterLegacy.responseStatus]
        status = 0
        if heaterOn:                                    status += 1
        if keepwarmOn:                                  status += 2
        if temperature == SmarterLegacy.status65c:      status += 4
        if temperature == SmarterLegacy.status80c:      status += 8
        if temperature == SmarterLegacy.status95c:      status += 16
        if temperature == SmarterLegacy.status100c:     status += 32
        return [SmarterLegacy.responseStatus + Smarter.number_to_raw(status)]


    def __sim_stop(self):
        self.simHeaterOn = False
        self.simKeepwarmOn = False
        return [SmarterLegacy.statusReady]


    def __sim_temperature(self,command):
        if command == SmarterLegacy.command65c:
            self.simTemperature = SmarterLegacy.status65c
        elif command == SmarterLegacy.command80c:
            self.simTemperature = SmarterLegacy.status80c
        elif command == SmarterLegacy.command95c:
            self.simTemperature = SmarterLegacy.status95c
        elif command == SmarterLegacy.command100c:
            self.simTemperature = SmarterLegacy.status100c
        return [self.simTemperature]


    def __sim_keepwarm_minutes(self,command):
        if command == SmarterLegacy.commandWarm5m:
            self.simKeepwarm = SmarterLegacy.statusWarm5m
        elif command == SmarterLegacy.commandWarm10m:
            self.simKeepwarm = SmarterLegacy.statusWarm10m
        elif command == SmarterLegacy.commandWarm20m:
            self.simKeepwarm = SmarterLegacy.statusWarm20m
        return [self.simKeepwarm]


    def __sim_warm(self):
        self.simKeepwarmOn = True
        return [self.simKeepwarm]


    #------------------------------------------------------
    # SERVER CONNECTION
    #------------------------------------------------------

    def __relayHandler(self,clientsock,addr):
        logging.info("[" + self.relayHost + ":" + str(self.relayPort) + "] [" + addr[0] + ":" + str(addr[1]) + "] Legacy client connected")

        while self.relay:
            #try:
            command = clientsock.recv(40)
            if not command:
                break
            #except:
            #    continue
            command = command[:-1]

            logging.debug("[" + self.host + ":" + str(self.port)  + "] [" + self.relayHost + ":" + str(self.relayPort) + "] [" + addr[0] + ":" + str(addr[1]) + "] Legacy command relay [" + command + "] " + SmarterLegacy.command_to_string(command))

            self.__clients[(clientsock, addr)].acquire()

            if self.simulation:
                responses = self.sim_response(command)
            if self.emulation:
                responses = self.emu_passthrough(command)
            else:
                try:
                    responses = self.send(command)
                except Exception, e:
                    self.disconnect()
                    print str(e)
                    raise SmarterErrorOld("Could not send command to device")
            
            for r in responses:
                logging.debug("[" + self.host + ":" + str(self.port)  + "] [" + self.relayHost + ":" + str(self.relayPort) + "] [" + addr[0] + ":" + str(addr[1]) + "] Legacy response relay [" + r + "] " + SmarterLegacy.string_response(r))
                clientsock.send(r+"\r")

                

            self.__clients[(clientsock, addr)].release()
        logging.info("[" + self.relayHost + ":" + str(self.relayPort) + "] [" + addr[0] + ":" + str(addr[1]) + "] Legacy client disconnected")
        clientsock.close()



    def __relay(self):
        self.relay_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.relay_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # settimeout at least 2
        self.relay_socket.settimeout(5)
        try:
            self.relay_socket.bind((self.relayHost,self.relayPort))
            self.relay_socket.listen(20)
        except socket.error, e:
            self.relay = False
            logging.debug("[" + self.host + ":" + str(self.port)  + "] " + str(e))
            logging.warning("[" + self.host + ":" + str(self.port)  + "] Legacy relay server failed (" + self.relayHost + ":" + str(self.relayPort) + ")")
            return
        except Exception:
            logging.warning("[" + self.host + ":" + str(self.port)  + "] Legacy relay server failed (" + self.relayHost + ":" + str(self.relayPort) + ")")
            self.relay = False
            return

        logging.info("[" + self.host + ":" + str(self.port)  + "] Legacy relay server (" + self.relayHost + ":" + str(self.relayPort) + ")")
        
        while self.relay:
            try:
                clientsock, addr = self.relay_socket.accept()
                # setblocking for OSX NEEDED!
                clientsock.setblocking(1)
                self.__clients[(clientsock, addr)] = threading.Lock()
                try:
                    r = threading.Thread(target=self.__relayHandler,args=(clientsock,addr))
                    r.start()
                except Exception, e:
                    print str(e)
            except socket.error:
                continue


    def relay_start(self,host="",port=SmarterLegacy.Port):
        self.connect()
        self.relayHost = host
        self.relayPort = port
        self.relay = True
        self.relayServer = threading.Thread(target=self.__relay)
        self.relayServer.start()


    def relay_stop(self):
        if self.relay and self.dump:
            logging.info("[" + self.host + ":" + str(self.port) +"] Legacy relay server terminate (" + self.relayHost + ":" + str(self.relayPort) + ")")
        self.relay = False


    #------------------------------------------------------
    # COMMANDS: iKettle
    #------------------------------------------------------

    def status(self):
        return self.send(SmarterLegacy.commandStatus)


    def keepwarm(self):
        return self.send(SmarterLegacy.commandWarm)


    def stop(self):
        return self.send(SmarterLegacy.commandStop)


    def selectKeepwamr20min(self):
        return self.send(SmarterLegacy.commandWarm20m)


    def selectKeepwamr10min(self):
        return self.send(SmarterLegacy.commandWarm10m)


    def selectKeepwamr5min(self):
        return self.send(SmarterLegacy.commandWarm5m)


    def selectTemperature65(self):
        return self.send(SmarterLegacy.command65c)


    def selectTemperature80(self):
        return self.send(SmarterLegacy.command80c)


    def selectTemperature95(self):
        return self.send(SmarterLegacy.command95c)


    def selectTemperature100(self):
        return self.send(SmarterLegacy.command100c)


    def boil(self):
        return self.send(SmarterLegacy.command100c) + self.send(SmarterLegacy.commandHeat)


    def heat(self):
        return self.send(SmarterLegacy.commandHeat)


    def heat_temp(self,temperature=100):
        #Smarter.check_temperature(temperature)
        if temperature < 73:
            response = self.send(SmarterLegacy.command65c)
        elif temperature < 88:
            response = self.send(SmarterLegacy.command80c)
        elif temperature < 97:
            response = self.send(SmarterLegacy.command95c)
        else:
            response = self.send(SmarterLegacy.command100c)
        return response + self.send(SmarterLegacy.commandHeat)


class SmarterInterface:
    """
    
    Class variables:
    
 
    Please look at __init() and __init__() in the source
    

    """
    
    
    def __init(self):
    
        self.__simulation_default()
        
        # still try to read if in fast mode...
        self.__read_triggers()
        self.__read_block()
        
    
    
        # device
        self.historySuccess             = 0
        
        # device info
        self.heaterOn                   = False
        
        # unknown status byte
        self.unknown                    = 0
    
        # kettle
        self.waterSensorBase            = 974
        
        self.waterSensor                = 2010
        self.waterSensorStable          = 2010

        # status
        self.kettleStatus               = Smarter.KettleReady
        
        # sensors
        self.onBase                     = True
        
        self.keepWarmOn                 = False
        self.formulaCoolingOn           = False
        self.temperature                = 24
        self.temperatureStable          = 24
        
        # 'default' user settings
        self.defaultTemperature         = 100
        self.defaultKeepWarmTime        = 0
        self.defaultFormula             = False
        self.defaultFormulaTemperature  = 75
        
  
        # coffee
        self.waterLevel                 = Smarter.CoffeeWaterFull

        # machine user settings
        self.cups                       = 1
        self.strength                   = Smarter.CoffeeMedium
        self.hotPlate                   = 0
        self.grind                      = False

        # 'default' user settings
        self.defaultCups                = 1
        self.defaultStrength            = Smarter.CoffeeMedium
        self.defaultGrind               = False
        self.defaultHotPlate            = 0

        # coffee modes
        self.mode                       = False
        self.carafeRequired             = False

        # coffee status
        self.cupsBrew                   = 0
        self.waterEnough                = False
        self.carafe                     = True
        self.timerEvent                 = False
        self.ready                      = True
        self.hotPlateOn                 = False
        self.grinderOn                  = False
        self.working                    = False
        
        self.busy                       = False
        
        # Wifi
        self.Wifi                       = []
        self.WifiFirmware               = ""
        isDirect                        = False

        self.__monitorLock              = threading.Lock()
        self.__readLock                 = threading.Lock()
    

        # already written to total from session
        self.__deltaSendCount             = 0
        self.__deltaReadCount             = 0
        self.__deltaReadBytesCount        = 0
        self.__deltaSendBytesCount        = 0
        self.__deltaCountCarafeRemove     = 0
        self.__deltaCountCupsBrew         = 0
        self.__deltaCountGrinderOn        = 0
        self.__deltaCountHotPlateOn       = 0
        self.__deltaCountKettleRemoved    = 0
        self.__deltaCountHeater           = 0
        self.__deltaCountFormulaCooling   = 0
        self.__deltaCountKeepWarm         = 0
        self.__deltaSessionCount          = 0

        # session
        self.commandCount               = dict()
        self.responseCount              = dict()
    
        self.sendCount                  = 0
        self.readCount                  = 0
        self.sendBytesCount             = 0
        self.readBytesCount             = 0

        self.countHeater                = 0
        self.countFormulaCooling        = 0

        # coffee session counters
        self.countCarafeRemoved         = 0
        self.countCupsBrew              = 0
        self.countGrinderOn             = 0
        self.countHotPlateOn            = 0
    
        # kettle session counters
        self.countKeepWarm              = 0
        self.countKettleRemoved         = 0
    
        self.remoteRelayHost           = ""
        self.remoteRelayVersion        = 0
        self.remoteRelay               = False
        self.remoteRulesIn             = []
        self.remoteRulesOut            = []
   
   
    
    def __init__(self,setting_path=""):
        """
        Initializing SmarterInterface
        """

        # format Name,Active,Bool format
        self.triggersGroups = []
        
        # format {(group,sensorid,command),...(group,sensorid,command)}
        self.triggersKettle = self.__initTriggers()
        self.triggersCoffee = self.__initTriggers()
 
        self.settingsPath                 = setting_path
        self.events                     = False
        self.relayHost                 = ''
        self.relayPort                 = Smarter.Port
        self.isKettle                   = False
        self.isCoffee                   = False
        
        # total for device
        self.totalSendCount             = 0
        self.totalReadCount             = 0
        self.totalReadBytesCount        = 0
        self.totalSendBytesCount        = 0
        
        
        self.totalCountCarafeRemoved         = 0
        self.totalCountCupsBrew              = 0
        self.totalCountGrinderOn             = 0
        self.totalCountHotPlateOn            = 0
        self.totalCountKettleRemoved         = 0
        self.totalCountHeater                = 0
        self.totalCountFormulaCooling        = 0
        self.totalCountKeepWarm              = 0
        self.totalSessionCount               = 0
        
        
       # network
        self.port                       = Smarter.Port
         
        self.host                       = Smarter.DirectHost
        self.dump_status                = True
        self.dump                       = False
        #set this to try is you want to connect send receive and don't care about the new status or other messages the about the out come, its disconnect afterwards....
        self.fast                       = False
        #set this to try is you want to connect send and really do not care about the about the out come, its disconnect afterwards....
        self.shout                      = False
        
        self.device                     = "None"
        self.deviceId                   = 0
        self.version                    = 0
        
        self.sessionCount               = 0

        
        # Threading info
        self.__monitorLock                = threading.Lock()
        self.__readLock                   = threading.Lock()
        self.__sendLock                   = threading.Lock()
        self.connected                    = False
        self.monitor                      = None
        self.__socket                     = None
        
        self.__clients                    = dict()
        
        # monitor run
        self.monitor_run                  = False
        self.simulator_run                = False
        self.__utp_ResponseDeviceInfo     = False
        self.relay                        = False
        self.relayVersion                 = 1
        
        self.simulate                   = False
        self.bridge                     = False

        # firewall or message blocking rules
        self.rulesIn                 = Smarter.MessagesDebug + Smarter.MessagesRest
        self.rulesOut                = Smarter.MessagesDebug + Smarter.MessagesRest + Smarter.MessagesWifi + Smarter.MessagesDeviceInfo + Smarter.MessagesCalibrateOnly # use only after setup so speed up ... + Smarter.MessagesGet + Smarter.MessagesModesGet


        self.patchTemperatureLimitValue = 70
        self.patchTemperatureLimit      = False
        self.patchChildProtectionValue  = 45
        self.patchChildProtection       = False
        """
        self.patchHotplateMinutes       = 80
        self.extendedHotplate           = 0
        self.extendedHotplateLeft       = 0
        self.patchHotplate              = True
        """
        
        self.__init()

        self.iKettle                      = SmarterInterfaceLegacy()
        self.emulate                      = False


        try:
            self.simulator = threading.Thread(target=self.__simulate_device)
            self.simulator.start()
        except threading.ThreadError, e:
            s = traceback.format_exc()
            logging.debug(s)
            loggins.debug(e)
            logging.error("[" + self.host + "] Could not start simulator")
            raise SmarterError(0,"Could not start simulator")


    def trash(self):
        self.iKettle.trash()
        self.simulator_run = False
        self.relay_stop()
        self.disconnect()
    

    @_threadsafe_function
    def setHost(self,host):
        self.host = host
        self.__read_block()
        self.__read_triggers()
        self.__write_stats()

    def emulate(self):
        self.simulate = True
        self.iKettle.dump = True
        self.iKettle.bridge(self)
        self.iKettle.emu_trigger_heating(self.heaterOn)
        self.iKettle.emu_trigger_temperature(False)
        self.iKettle.emu_trigger_onbase(self.onBase)
        self.emulate = True

    def simulate(self):
        self.simulate = True
        self.setHost("simulation")
                
    #------------------------------------------------------
    # STATS
    #------------------------------------------------------


    @_threadsafe_function
    def __write_stats(self):
       
        section = self.host + "." + str(self.port) + ".statistics"
        
        if self.isKettle:
            section += ".kettle"
        elif self.isCoffee:
            section += ".coffee"
        else:
            return
        config = SafeConfigParser()
        
        
        if not os.path.exists(self.settingsPath):
                os.makedirs(self.settingsPath)
        
        config.read(self.settingsPath+'ibrew.conf')
        
        try:
            config.add_section(section)
        except DuplicateSectionError:
            pass


        ### THESE EXCEPTIONS NEED TO BE CHANGED FIX
        try:
            self.totalSendCount = int(config.get(section, 'send')) + self.sendCount - self.__deltaSendCount
            self.__deltaSendCount += self.sendCount - self.__deltaSendCount
            config.set(section, 'send', str(self.totalSendCount))
        except Exception:
            config.set(section, 'send', str(self.sendCount))
        
        try:
            self.totalReadCount = int(config.get(section, 'read')) + self.readCount - self.__deltaReadCount
            self.__deltaReadCount += self.readCount - self.__deltaReadCount
            config.set(section, 'read', str(self.totalReadCount))
        except Exception:
            config.set(section, 'read', str(self.readCount))

        try:
            self.totalReadBytesCount = int(config.get(section, 'readbytes')) + self.readBytesCount - self.__deltaReadBytesCount
            self.__deltaReadBytesCount += self.readBytesCount - self.__deltaReadBytesCount
            config.set(section, 'readbytes', str(self.totalReadBytesCount))
        except Exception:
            config.set(section, 'readbytes', str(self.readBytesCount))

        try:
            self.totalSendBytesCount = int(config.get(section, 'sendbytes')) + self.sendBytesCount - self.__deltaSendBytesCount
            self.__deltaSendBytesCount += self.sendBytesCount - self.__deltaSendBytesCount
            config.set(section, 'sendbytes', str(self.totalSendBytesCount))
        except Exception:
            config.set(section, 'sendbytes', str(self.sendBytesCount))

        try:
            self.totalCountHeater = int(config.get(section, 'heater')) + self.countHeater - self.__deltaCountHeater
            self.__deltaCountHeater += self.countHeater - self.__deltaCountHeater
            config.set(section, 'heater', str(self.totalCountHeater))
        except Exception:
            config.set(section, 'heater', str(self.countHeater))



        if self.isKettle:
            try:
                self.totalCountFormulaCooling = int(config.get(section, 'formulacooling')) + self.countFormulaCooling - self.__deltaCountFormulaCooling
                self.__deltaCountFormulaCooling += self.countFormulaCooling - self.__deltaCountFormulaCooling
                config.set(section, 'formulacooling', str(self.totalCountFormulaCooling))
            except Exception:
                config.set(section, 'formulacooling', str(self.countFormulaCooling))
            
            try:
                self.totalCountKettleRemoved = int(config.get(section, 'kettleremoved')) + self.countKettleRemoved - self.__deltaCountKettleRemoved
                self.__deltaCountKettleRemoved += self.countKettleRemoved - self.__deltaCountKettleRemoved
                config.set(section, 'kettleremoved', str(self.totalCountKettleRemoved))
            except Exception:
                config.set(section, 'kettleremoved', str(self.countKettleRemoved))

            try:
                self.totalCountKeepWarm = int(config.get(section, 'keepwarm')) + self.countKeepWarm - self.__deltaCountKeepWarm
                self.__deltaCountKeepWarm += self.countKeepWarm - self.__deltaCountKeepWarm
                config.set(section, 'keepwarm', str(self.totalCountKeepWarm))
            except Exception:
                config.set(section, 'keepwarm', str(self.countKeepWarm))
                
                
        if self.isCoffee:
            try:
                self.totalCountCarafeRemoved = int(config.get(section, 'caraferemoved')) + self.countCarafeRemoved - self.__deltaCountCarafeRemoved
                self.__deltaCountCarafeRemoved += self.countCarafeRemoved - self.__deltaCountCarafeRemoved
                config.set(section, 'caraferemoved', str(self.totalCountCarafeRemoved))
            except Exception:
                config.set(section, 'caraferemoved', str(self.countCarafeRemoved))

            try:
                self.totalCountGrinderOn = int(config.get(section, 'grinder')) + self.countGrinderOn - self.__deltaCountGrinderOn
                self.__deltaCountGrinderOn += self.countGrinderOn - self.__deltaCountGrinderOn
                config.set(section, 'grinder', str(self.totalCountGrinderOn))
            except Exception:
                config.set(section, 'grinder', str(self.countGrinderOn))

            try:
                self.totalCountHotPlateOn = int(config.get(section, 'hotplate')) + self.countHotPlateOn - self.__deltaCountHotPlateOn
                self.__deltaCountHotPlateOn += self.countHotPlateOn - self.__deltaCountHotPlateOn
                config.set(section, 'hotplate', str(self.totalCountHotPlateOn))
            except Exception:
                config.set(section, 'hotplate', str(self.countHotPlateOn))

        try:
            self.totalSessionCount = int(config.get(section, 'sessions')) + self.sessionCount - self.__deltaSessionCount
            self.__deltaSessionCount += self.sessionCount - self.__deltaSessionCount
            config.set(section, 'sessions', str(self.totalSessionCount))
        except Exception:
            config.set(section, 'sessions', str(self.sessionCount))

        
      #  with open(self.settingsPath+'ibrew.conf', 'w') as f:
        with codecs.open(self.settingsPath+'ibrew.conf','wb+','utf-8') as f:
            config.write(f)
            f.close()
        
        #if self.dump:
        #    self.print_stats()


    #------------------------------------------------------
    # DEVICE INFO UDP
    #------------------------------------------------------


    def __broadcast_device(self):
        self.__utp_ResponseDeviceInfo = True
        while self.__utp_ResponseDeviceInfo:
            try:
                message, address  = self.udp.recvfrom(1024)
            except socket.error:
                continue
            # so what happens....
            logging.info("Received UDP " + address[0] + ":" + str(address[1]))
            command = Smarter.number_to_raw(Smarter.ResponseDeviceInfo) + Smarter.number_to_raw(self.deviceId) + Smarter.number_to_raw(self.version) + Smarter.number_to_raw(Smarter.MessageTail)
            if self.connected:
                commandRelay = Smarter.number_to_raw(Smarter.ResponseRelayInfo) + Smarter.number_to_raw(self.relayVersion) + Smarter.text_to_raw(self.host) + Smarter.number_to_raw(Smarter.MessageTail)
            else:
                commandRelay = Smarter.number_to_raw(Smarter.ResponseRelayInfo) + Smarter.number_to_raw(self.relayVersion) + Smarter.number_to_raw(Smarter.MessageTail)
            
            if message[0] == Smarter.number_to_raw(Smarter.CommandDeviceInfo) and message[1] == Smarter.number_to_raw(Smarter.MessageTail):
                self.udp.sendto(command, address)
                self.udp.sendto(commandRelay, address)



    def __broadcast_device_stop(self):
        if self.dump and self.__utp_ResponseDeviceInfo:
            logging.info("Stopping UDP (" + self.relayHost + ":" + str(self.relayPort) + ")")
        self.__utp_ResponseDeviceInfo = False



    def __broadcast_device_start(self):
        if not self.__utp_ResponseDeviceInfo:
            try:
                self.udp=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.udp.settimeout(1)
                self.udp.bind((self.relayHost,self.relayPort))
                
                self.broadcast = threading.Thread(target=self.__broadcast_device)
                self.broadcast.start()
                logging.info("Starting UDP (" + self.relayHost + ":" + str(self.relayPort) + ")")
            except socket.error, e:
                print str(e)
            except threading.ThreadError:
                print str(e)
        else:
            raise SmarterError(0,"UPD Response Appliance Info already started")



    #------------------------------------------------------
    # SERVER CONNECTION
    #------------------------------------------------------



    def __relayMonitor(self,clientsock,addr):
        while self.relay:
            time.sleep(1)
            if  not self.__clients[(clientsock, addr)].locked():
                self.__clients[(clientsock, addr)].acquire()
                
                # BLOCKING HERE FIX
                if self.isKettle:
                    if Smarter.ResponseKettleStatus in self.rulesOut:
                        logging.debug("Blocked relay kettle status")
                        r = self.__simulate_KettleStatus()
                    else:
                        r = self.__encode_KettleStatus(self.kettleStatus,self.temperature,self.waterSensor, self.onBase, self.unknown)
                elif self.isCoffee:
                    if Smarter.ResponseCoffeeStatus in self.rulesOut:
                        logging.debug("Blocked relay coffee status")
                        r = self.__simulate_CoffeeStatus()
                    else:
                        r = self.__encode_CoffeeStatus(self.cups,self.strength,self.cupsBrew,self.waterLevel,self.waterEnough,self.carafe, self.grind, self.ready, self.grinderOn, self.heaterOn, self.hotPlateOn,self.working,self.timerEvent)
                clientsock.send(r[0])
                self.__clients[(clientsock, addr)].release()
                logging.info(addr[0] + ":" + str(addr[1]) + " Status [" + Smarter.message_to_codes(r[0]) + "]")



    def __relayHandler(self,clientsock,addr):
        logging.info(addr[0] + ":" + str(addr[1]) + " Client connected")
        while self.relay:
            data = clientsock.recv(1024)
            if not data:
                break

            self.__clients[(clientsock, addr)].acquire()

            command = Smarter.raw_to_number(data[0])

            logging.info(addr[0] + ":" + str(addr[1]) + " Command message received relay [" + Smarter.number_to_code(command) +"] ["+ Smarter.message_description(command) + "] [" + Smarter.message_to_codes(data) + "]")
  
            if command in self.rulesOut:
                logging.debug("Blocked relay command: " + Smarter.number_to_code(command))
                response = self.__block_command(data)
            else:
                # relay
                
                if command == Smarter.CommandRelayInfo:
                    if self.connected:
                        response = self.__encode_RelayInfo(self.relayVersion,self.host)
                    else:
                        response = self.__encode_RelayInfo(self.relayVersion,Smarter.DirectHost)
                elif command == Smarter.CommandRelayModifiersInfo:
                    response = self.__encode_RelayModifiersInfo(self.string_block())
                elif command == Smarter.CommandRelayBlock or command == Smarter.CommandRelayPatch:
                    #print Smarter.raw_to_text(data[0:])
                    self.__modifiers(Smarter.raw_to_text(data[0:]))
                    response = self.__encode_RelayModifiersInfo(self.string_block())
                elif command == Smarter.CommandRelayUnblock:
                    #FIX
                    #print Smarter.raw_to_text(data[0:])
                    self.__unmodifiers(Smarter.raw_to_text(data[0:]))
                    response = self.__encode_RelayModifiersInfo(self.string_block())
                else:
                    response = self.__send(data)
         
            if command == Smarter.CommandWifiJoin or command == Smarter.CommandWifiLeave:
                break
 
            clientsock.send("".join(response))
            self.__clients[(clientsock, addr)].release()
            logging.info(addr[0] + ":" + str(addr[1]) + " Relay send [" + Smarter.message_to_codes("".join(response)) + "]")
    
        logging.info(addr[0] + ":" + str(addr[1]) + " Client disconnected")
        clientsock.close()



    def __relay(self):
        self.relay_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.relay_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # settimeout at least 2
        self.relay_socket.settimeout(2)
        try:
            self.relay_socket.bind((self.relayHost,self.relayPort))
            self.relay_socket.listen(20)
        except socket.error:
            return
        except Exception:
            return
 
        self.__broadcast_device_start()

        logging.info("[" + self.host + "] Relay Server (" + self.relayHost + ":" + str(self.relayPort) + ")")
        
        while self.relay:
            try:
                clientsock, addr = self.relay_socket.accept()
                clientsock.setblocking(1)
                self.__clients[(clientsock, addr)] = threading.Lock()
                try:
                    r = threading.Thread(target=self.__relayHandler,args=(clientsock,addr))
                    s = threading.Thread(target=self.__relayMonitor,args=(clientsock,addr))
                    r.start()
                    s.start()
                except Exception, e:
                    print str(e)
            except socket.error:
                continue



    def relay_start(self):
        self.relay = True
        self.relayServer = threading.Thread(target=self.__relay)
        self.relayServer.start()



    def relay_stop(self):
        if self.relay and self.dump:
            logging.info("[" + self.host + "] Stopping Relay (" + self.relayHost + ":" + str(self.relayPort) + ")")
        self.__broadcast_device_stop()
        self.relay = False



    #------------------------------------------------------
    # CLIENT CONNECTION
    #------------------------------------------------------


    
    def __monitor_device(self):
        if self.dump:
            logging.info("[" + self.host + "] Monitor Running")
        
        previousResponse = ""
        previousWaterSensor = self.waterSensor
        
        prevPreviousTemperature = self.temperature
        previousTemperature = self.temperature
        previousAverage = self.temperature
        
        self.waterSensorStable  = self.waterSensor
        self.temperatureStable  = self.temperature
        
        monitorCount = 0
   
        timeout = 60
        self.monitor_run = True
        while self.monitor_run:
                try:
                    self.__sendLock.acquire()
                    self.__monitorLock.acquire()
                except threading.ThreadError, e:
                    if not self.monitor_run:
                        break
                    s = traceback.format_exc()
                    logging.debug(s)
                    logging.debug(e)
                    logging.error("[" + self.host + "] ERROR")
                    self.disconnect()
                    break
                    raise SmarterError(0,"Monitor Error")
                try:
                    response = self.__read()
                    monitorCount += 1
                    if previousResponse != response:
                        previousResponse = response
                        # call monitor function
                        # ...else got one! yeah! print it!
  
                except SmarterError, e:
                    if not self.monitor_run:
                        break
                    
                    s = traceback.format_exc()
                    logging.debug(s)
                    logging.debug(e)
                    logging.error("[" + self.host + "] ERROR")

                    if self.__sendLock.locked():
                        self.__sendLock.release()
                    if self.__monitorLock.locked():
                        self.__monitorLock.release()
                    self.disconnect()
                    break
                    raise SmarterError(0,"Monitor Error")
    
                if self.__monitorLock.locked():
                    self.__monitorLock.release()
                if self.__sendLock.locked():
                    self.__sendLock.release()
                
                dump = self.dump
                
                if self.dump_status:
                    self.dump = True;
                else:
                    self.dump = False;

                if not self.__sendLock.locked():
                    try:
                        if monitorCount % timeout == timeout - 9:
                            if self.isKettle:   self.kettle_calibrate_base()
                            if self.isCoffee:   self.coffee_carafe_required()
                            self.__read_triggers()
     
                        if monitorCount % timeout == timeout - 19:
                            if self.isCoffee:   self.coffee_mode()
     
                        if monitorCount % timeout == timeout - 29:
                            self.device_settings()
     
                        if monitorCount % timeout == timeout - 39:
                            self.__write_stats()
                        
                        if monitorCount % timeout == timeout - 49:
                            pass #self.coffee_timers()
                            self.relay_info()
                        
                        if monitorCount % timeout == timeout - 50:
                            # we did not init it to speed up boot time... so init it
                            if self.WifiFirmware == "":
                                self.wifi_firmware()
                            pass #self.device_history()
                            self.__read_block()
                            
                    except SmarterError, e:
                        if not self.monitor_run:
                            break
                        s = traceback.format_exc()
                        logging.debug(s)
                        logging.debug(e)
                        logging.error("[" + self.host + "] ERROR")
                        self.disconnect()
                        self.dump = dump
                        
                        break
                        raise SmarterError(0,"Monitor Error")


                self.dump = dump


                if previousWaterSensor - 3 > self.waterSensor or previousWaterSensor + 3 < self.waterSensor:
                    if self.waterSensorStable != self.waterSensor:
                        self.__trigger(Smarter.triggerWaterSensorStable,self.waterSensorStable,self.waterSensor)
                        self.waterSensorStable = self.waterSensor
            
                    previousWaterSensor = self.waterSensor
                
                average = int(round(float((float(previousTemperature) + float(prevPreviousTemperature) + float(self.temperature))/3),0))

                if previousAverage != average:
                    if self.temperatureStable != average:
                        self.__trigger(Smarter.triggerTemperatureStable,self.temperatureStable,average)
                        self.temperatureStable = average
                    previousAverage = average

                prevPreviousTemperature = previousTemperature
                previousTemperature = self.temperature
        if self.dump:
            logging.info("[" + self.host + "] Monitor Stopped")
 
    #------------------------------------------------------
    # TRANSMISSION
    #------------------------------------------------------


    # MESSAGE READ
    def __read_message(self):
        if self.connected:
            try:
                message = ""
                raw = self.__socket.recv(1)
                id = Smarter.raw_to_number(raw)
                # debug
                #print "[" + Smarter.number_to_code(id) + "]",
                minlength = Smarter.message_response_length(id)
                i = 1
                while raw != Smarter.number_to_raw(Smarter.MessageTail) or (minlength > 0 and raw == Smarter.number_to_raw(Smarter.MessageTail) and i < minlength):
                    message += raw

                    raw = self.__socket.recv(1)
                    
                    # debug
                    #print "[" + Smarter.raw_to_code(raw) + "]" + str(raw)
                    i += 1
            
                message += raw
                
                self.readCount += 1
                self.readBytesCount += i
                if id in self.responseCount:
                    self.responseCount[id] += 1
                else:
                    self.responseCount[id] = 1
     
                return message
            except socket.error, msg:
                raise SmarterError(0,"Could not read message") # (" + msg + ")")
            except AttributeError, msg:
                raise SmarterError(0,"Disconnected")
        raise SmarterError(0,"Disconnected")





    # MESSAGE READ PROTOCOL
    def __read(self):
        if not self.connected:
             raise SmarterError(0,"Could not read message not connected")
   
        try:
            self.__readLock.acquire()
        except threading.ThreadError:
            #logging.debug(str(e))
            #logging.debug(traceback.format_exc())
            raise SmarterError(0,"Could not read message (lock)")
    
        if self.connected:
            message = self.__read_message()
            id = Smarter.raw_to_number(message[0])
            
            if id in self.rulesIn:
                if self.dump and self.dump_status:
                    logging.debug("Blocked Response: " + Smarter.number_to_code(id))
                message = self.__block_response(message)[0]
    
            # patches here....
            
            if not self.connected:
                # added such that the monitor thread will quit without errors
                return
            
            try:
                self.__decode(message)
            except SmarterError, e:
                #logging.debug(str(e))
                #logging.debug(traceback.format_exc())
                raise SmarterError(0,"Could not read message (convert failure)")

            if self.unknown != 0:
                logging.debug("***********************")
                logging.debug("*                     *")
                logging.debug("* Unknown byte is set *")
                logging.debug("*                     *")
                logging.debug("***********************")
                logging.debug("")
                logging.debug(Smarter.number_to_code(self.unknown) + "-" + str(self.unknown))
            
            self.__readLock.release()
            return message
        else:
            self.__readLock.release()
            raise SmarterError(0,"Could not read message disconnected")


    # MESSAGE SEND
    def __send_message(self,message):
        if len(message) == 0:
            raise SmarterError(0,"Cannot send an empty message")
    
        try:
            self.__socket.send(message)
        except socket.error, e:
            logging.debug(str(e))
            logging.debug(traceback.format_exc())
            raise SmarterError(0,"Could not send message")

        self.sendBytesCount += len(message)
    
        id = Smarter.raw_to_number(message[0])
        self.sendCount += 1
        if id in self.commandCount:
            self.commandCount[id] += 1
        else:
            self.commandCount[id] = 1

        if self.dump:
            self.print_message_send(message)



    # MESSAGE SEND PROTOCOL



    def __send_command(self,id,arguments=""):
        x = Smarter.message_connection(id)
        if len(x) != 0:
            # that whole fast thing should be fixed.
            if x[0] != Smarter.ResponseCommandStatus:
                self.fast = False
        else:
            self.fast = False
        self.__send(Smarter.number_to_raw(id) + arguments + Smarter.number_to_raw(Smarter.MessageTail))



    def __send(self,message):
        responses = []
        
        command = Smarter.raw_to_number(message[0])
        if command in self.rulesIn:
            if self.dump and self.dump_status:
                logging.debug("Blocked command: " + Smarter.number_to_code(command))
            responses = self.__block_command(message)
            for message in responses:
                self.__decode(message)
            return responses
        
        
        if not self.connected:
            raise SmarterError(0,"Could not write message not connected")
        try:
            self.__monitorLock.acquire()
        except threading.ThreadError, e:
            logging.debug(str(e))
            logging.debug(traceback.format_exc())
            raise SmarterError(0,"Could not write message")

        if self.connected:
            command = Smarter.raw_to_number(message[0])
            if command in self.rulesIn:
                self.__monitorLock.release()
                if self.dump and self.dump_status:
                    logging.debug("Blocked command: " + Smarter.number_to_code(command))
                response = self.__block_command(message)
                for message in response:
                    self.__decode(message)
                return responses
            else:
                try:
                    self.__send_message(message)
                except SmarterError:
                    self.__monitorLock.release()
                    self.disconnect()
                    raise SmarterError(0,"Could not send message")
            
                if self.shout:
                    self.__monitorLock.release()
                    # we do not care about result only speed..
                    return self.__block_command(message)

                try:
                    message_read = self.__read()
                    data = Smarter.raw_to_number(message_read[0])
                except SmarterError, e:
                    self.disconnect()
                    logging.debug(str(e))
                    logging.debug(traceback.format_exc())
                    raise SmarterError(0,"Could not write message (no response)")
                if (data != Smarter.ResponseKettleStatus) and (data != Smarter.ResponseCoffeeStatus):
                    responses += [message_read]
                
                while (data == Smarter.ResponseKettleStatus) or (data == Smarter.ResponseCoffeeStatus):
                    try:
                        message_read = self.__read()
                        data = Smarter.raw_to_number(message_read[0])
                        if (data != Smarter.ResponseKettleStatus) and (data != Smarter.ResponseCoffeeStatus):
                            responses += [message_read]
                    except SmarterError, e:
                        logging.debug(str(e))
                        logging.debug(traceback.format_exc())
                        self.__monitorLock.release()
                        self.disconnect()
                        raise SmarterError(0,"Could not write message (no response)")
        
                if self.fast or data == Smarter.ResponseCommandStatus or len(Smarter.message_connection(Smarter.raw_to_number(message[0]))) == 1:
                    self.__monitorLock.release()
                    return responses
                
                try:
                    message_read = self.__read()
                    data = Smarter.raw_to_number(message_read[0])


                except SmarterError,e:
                    logging.debug(str(e))
                    logging.debug(traceback.format_exc())
                    self.disconnect()
                    self.__monitorLock.release()
                    raise SmarterError(0,"Could not write message (no response)")

                if (data != Smarter.ResponseKettleStatus) and (data != Smarter.ResponseCoffeeStatus):
                        responses += [message_read]
 
                while (data != Smarter.ResponseKettleStatus) and (data != Smarter.ResponseCoffeeStatus):
                    try:
                        message_read = self.__read()
                        data = Smarter.raw_to_number(message_read[0])
                        if (data != Smarter.ResponseKettleStatus) and (data != Smarter.ResponseCoffeeStatus):
                            responses += [message_read]
                    except SmarterError, e:
                        logging.debug(str(e))
                        logging.debug(traceback.format_exc())
                        self.disconnect()
                        self.__monitorLock.release()
                        raise SmarterError(0,"Could not write message (no response)")
        else:
            self.__monitorLock.release()
            raise SmarterError(0,"Could not read message disconnected")
        self.__monitorLock.release()
        return responses
     
    
    
    @_threadsafe_function
    def connect(self):
        """
        Connect device
        """
        if self.dump:
            print "[" + self.host +  ":" + '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()) + "] Connecting appliance"
        self.__init()
        self.__write_stats()
        
        if self.host == "":
            self.setHost(Smarter.DirectHost)
        
        if self.host == Smarter.DirectHost:
            if platform.system() == "Darwin" or platform.system() == "Linux":
                # yeah, it only accept one wifi...

                # loop over interfaces.. interfaces()
                from wireless import Wireless
                wireless = Wireless()
                wirelessname = wireless.current()
                if wirelessname is not None:
                    if (wirelessname[0:14] == Smarter.DeviceStringCoffee or wirelessname[0:11] == Smarter.DeviceStringKettle) and self.host == Smarter.DirectHost:
                        self.isDirect = True
                    else:
                        self.isDirect = False
                else:
                    self.isDirect = False
            elif platform.system() == "Windows":
                self.isDirect = False
                # Netsh WLAN show interfaces grep it contains "iKettle 2.0" or "Smarter...
            else:
                self.isDirect = False
        else:
            self.isDirect = False
        
        try:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.settimeout(12)
            self.__socket.connect((self.host, self.port))
            self.connected = True
            self.sessionCount = 1
        except socket.error, msg:
            s = traceback.format_exc()
            logging.debug(s)
            logging.debug(msg)
            logging.error("[" + self.host + "] Could not connect to + " + self.host)
            raise SmarterError(0,"Could not connect to + " + self.host)


        if not self.fast:
            try:
                self.monitor = threading.Thread(target=self.__monitor_device)
                self.monitor.start()
            except threading.ThreadError, e:
                s = traceback.format_exc()
                logging.debug(s)
                loggins.debug(e)
                logging.error("[" + self.host + "] Could not start monitor")
                raise SmarterError(0,"Could not start monitor")



    @_threadsafe_function
    def disconnect(self):
        """
        Disconnect device
        """
 
        self.monitor_run = False

        if self.connected:
            
            self.__write_stats()
        
            if self.dump:
                x = self.device
                if x == "Unknown": x = "appliance"
                print "[" + self.host +  ":" + '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()) + "] Disconnecting " + x
        
            self.connected = False
            
            try:
                if self.monitor:
                    if self.__monitorLock.locked():
                        self.__monitorLock.release()
                    if self.__readLock.locked():
                        self.__readLock.release()
            except threading.ThreadError:
                raise SmarterError(SmarterInterfaceFailedStopThread,"Could not disconnect from " + self.host)

            self.monitor = None

            try:
                if self.__socket:
                    self.__socket.close()
                    self.__socket = None
            # FIX: Also except thread exceptions..
            except socket.error, msg:
                self.__socket = None
                raise SmarterError(SmarterInterfaceFailedStop,"Could not disconnect from " + self.host + " (" + msg[1] + ")")
            self.__socket = None





    #------------------------------------------------------
    # iBrew: iKettle 2.0 and Smarter Coffee Firewall
    #------------------------------------------------------
    #
    # History:
    # v0.1 Hot Chocolade Engine
    #------------------------------------------------------
    

    @_threadsafe_function
    def __write_block(self):

        if self.simulate:
            return
        
        section = self.host + "." + str(self.port)
        if self.isKettle:
            section += ".kettle"
        elif self.isCoffee:
            section += ".coffee"
        else:
            return

        config = SafeConfigParser()

        if not os.path.exists(self.settingsPath):
                os.makedirs(self.settingsPath)
        
        config.read(self.settingsPath+'ibrew.conf')

        try:
            config.add_section(section)
        except DuplicateSectionError:
            pass
        
        try:
            config.set(section, "blocks", self.string_block())
        except Exception:
            pass
        
        with codecs.open(self.settingsPath+'ibrew.conf','wb+','utf-8') as f:
            config.write(f)
            f.close()
        #with open(self.settingsPath+'ibrew.conf', 'w') as f:
        #    config.write(f)


    @_threadsafe_function
    def __read_block(self):
    
        if self.simulate:
            return
       
        section = self.host + "." + str(self.port)
        if self.isKettle:
            section += ".kettle"
        elif self.isCoffee:
            section += ".coffee"
        else:
            return

        config = SafeConfigParser()

        if not os.path.exists(self.settingsPath):
                os.makedirs(self.settingsPath)
        
        config.read(self.settingsPath+'ibrew.conf')
        
        try:
            config.add_section(section)
        except DuplicateSectionError:
            pass

        try:
            s = config.get(section, "blocks")
            d, r, p  = self.__splitrules(s)
            did = Smarter.groupsListDecode(d)
            rid = Smarter.groupsListDecode(r)
            
            self.rulesIn = []
            self.rulesOut = []
            self.rulesIn = Smarter.idsAdd(self.rulesIn,did)
            self.rulesOut = Smarter.idsAdd(self.rulesOut,rid)
        
        except Exception:
            pass
            
        
    def __splitrules(self,string):
        s = string.lower().split(",")
        a = []
        r = []
        p = []
        for i in s:
            if i[0:3] == "in:":
                a += [i[3:]]
            if i[0:4] == "out:":
                r += [i[4:]]
            if i[0:4] == "mod:":
                p += [i[4:]]
        return (a,r,p)


    def string_rules(self,rules):
        groups, ids = Smarter.idsListEncode(rules)
        return Smarter.groupsString(groups) + " " + Smarter.ids_to_string(ids)


    def string_block(self):
        groups, ids = Smarter.idsListEncode(self.rulesOut)
        outids = ",".join(["out:" + Smarter.number_to_code(i) for i in ids])
        outgroups = ",".join(["out:" + s.upper() for s in Smarter.groupsList(groups)])
        groups, ids = Smarter.idsListEncode(self.rulesIn)
        inids = ",".join(["in:" + Smarter.number_to_code(i) for i in ids])
        ingroups = ",".join(["in:" + s.upper() for s in Smarter.groupsList(groups)])
        return ",".join([ingroups,inids,outgroups,outids])


    #------------------------------------------------------
    # Firewall Rules Printers
    #------------------------------------------------------
    

    def print_patches_short(self):
        pass


    def print_patches(self):
        pass


    def print_remote_patches_short(self):
        pass


    def print_remote_patches(self):
        pass
    
    
    def print_rules_short(self):
        print "Appliance blocks (in): " + self.string_rules(self.rulesIn)
        print "Relay blocks (out): " + self.string_rules(self.rulesOut)
 

    def print_remote_rules_short(self):
        print "Remote appliance blocks (in): " + self.string_rules(self.remoteRulesIn)
        print "Remote relay blocks (out): " + self.string_rules(self.remoteRulesOut)
 

    def print_rules(self):
        print
        print "Appliance blocks (in): " + self.string_rules(self.rulesIn)
        print
        print "    ID Description"
        print "    ___________________________________________"
        print
        for id in sorted(self.rulesIn):
            print "    " + Smarter.number_to_code(id) + " " + Smarter.message_description(id)
        print
        print
        print "Relay blocks (out):  " + self.string_rules(self.rulesOut)
        print
        print "    ID Description"
        print "    ___________________________________________"
        print
        for id in sorted(self.rulesOut):
            print "    " + Smarter.number_to_code(id) + " " + Smarter.message_description(id)
        print


    def print_remote_rules(self):
        print
        print "Remote appliance blocks (in): " + self.string_rules(self.remoteRulesIn)
        print
        print "    ID Description"
        print "    ___________________________________________"
        print
        for id in sorted(self.remoteRulesIn):
            print "    " + Smarter.number_to_code(id) + " " + Smarter.message_description(id)
        print
        print
        print "Remote relay blocks (out):  " + self.string_rules(self.remoteRulesOut)
        print
        print "    ID Description"
        print "    ___________________________________________"
        print
        for id in sorted(self.remoteRulesOut):
            print "    " + Smarter.number_to_code(id) + " " + Smarter.message_description(id)
        print

    #------------------------------------------------------
    # Firewall Interface
    #------------------------------------------------------
    

    def patch(self,string):
        self.__modifiers(string)
        if self.dump:
            self.print_patches_short()


    def block(self,string):
        self.__modifiers(string)
        if self.dump:
            self.print_rules_short()


    def unblock(self,string):
        self.__unmodifiers(string)
        if self.dump:
            self.print_rules_short()


    def __modifiers(self,string):
        """
        Block messages from the list of ids
        """
        d, r, p = self.__splitrules(string)
        did = Smarter.groupsListDecode(d)
        rid = Smarter.groupsListDecode(r)

        self.rulesIn = Smarter.idsAdd(self.rulesIn,did)
        self.rulesOut = Smarter.idsAdd(self.rulesOut,rid)
        
        if did != []:
            logging.info("Blocked: " + " ".join(d).upper())
        if rid != []:
            logging.info("Blocked relay: " + " ".join(r).upper())

        self.__write_block()

        """
        patches:
        childprotection
        temperaturelimit
        """
    
    def __unmodifiers(self,string):
        """
        Block messages from the list of ids
        """
        d, r, p  = self.__splitrules(string.upper())
        did = Smarter.groupsListDecode(d)
        rid = Smarter.groupsListDecode(r)
        
        self.rulesIn = Smarter.idsRemove(self.rulesIn,did)
        self.rulesOut = Smarter.idsRemove(self.rulesOut,rid)
        if did != []:
            logging.info("Unblocked: " + " ".join(d))
        if rid != []:
            logging.info("Unblocked relay: " + " ".join(r))
        if self.dump:
            self.print_rules_short()

        self.__write_block()



    #------------------------------------------------------
    # Firewall Simulate Messages
    #------------------------------------------------------


    def __block_command(self,message):
        """
        Returns list of reply messages and preform sim action if needed of bot command and response messages.
        """
        
        
        id = Smarter.raw_to_number(message[0])
        if id == Smarter.CommandDeviceInfo:             response = self.__simulate_DeviceInfo()
        elif id == Smarter.Command20:                   response = self.__simulate_20()
        elif id == Smarter.Command22:                   response = self.__simulate_22()
        elif id == Smarter.Command23:                   response = self.__simulate_23()
        elif id == Smarter.Command30:                   response = self.__simulate_30()
        elif id == Smarter.CommandUpdate:               response = self.__simulate_Update()
        elif id == Smarter.Command69:                   response = self.__simulate_69()
        elif id == Smarter.CommandWifiFirmware:         response = self.__simulate_WifiFirmware()
        elif id == Smarter.CommandWifiNetwork:          response = self.__simulate_WifiNetwork()
        elif id == Smarter.CommandWifiPassword:         response = self.__simulate_WifiPassword()
        elif id == Smarter.CommandWifiJoin:             response = self.__simulate_WifiJoin()
        #elif id == Smarter.CommandWifiLeave:            response = self.__simulate_WifiLeave()
        elif id == Smarter.CommandWifiScan:             response = self.__simulate_WifiScan()
        elif id == Smarter.CommandKettleHistory:        response = self.__simulate_KettleHistory()
        elif id == Smarter.CommandCoffeeHistory:        response = self.__simulate_CoffeeHistory()
        elif id == Smarter.CommandSetMode:              response = self.__simulate_SetMode(message)
        elif id == Smarter.CommandMode:                 response = self.__simulate_Mode()
        elif id == Smarter.CommandBase:                 response = self.__simulate_Base()
        elif id == Smarter.CommandCalibrate:            response = self.__simulate_Calibrate()
        elif id == Smarter.CommandStoreBase:            response = self.__simulate_StoreBase(message)
        elif id == Smarter.CommandSetCarafe:            response = self.__simulate_SetCarafe(message)
        elif id == Smarter.CommandCarafe:               response = self.__simulate_Carafe()
        elif id == Smarter.CommandKettleSettings:       response = self.__simulate_KettleSettings()
        elif id == Smarter.CommandCoffeeSettings:       response = self.__simulate_CoffeeSettings()
        elif id == Smarter.CommandKettleStoreSettings:  response = self.__simulate_KettleStoreSettings(message)
        elif id == Smarter.CommandCoffeeStoreSettings:  response = self.__simulate_CoffeeStoreSettings(message)
        elif id == Smarter.CommandStrength:             response = self.__simulate_Strength(message)
        elif id == Smarter.CommandCups:                 response = self.__simulate_Cups(message)
        elif id == Smarter.CommandGrinder:              response = self.__simulate_Grinder()
        elif id == Smarter.CommandHotplateOn:           response = self.__simulate_HotplateOn(message)
        elif id == Smarter.CommandHotplateOff:          response = self.__simulate_HotplateOff()
        elif id == Smarter.CommandDeviceTime:           response = self.__simulate_DeviceTime(message)
        elif id == Smarter.CommandResetSettings:        response = self.__simulate_ResetSettings()
        
        elif id == Smarter.CommandBrew:                 response = self.__simulate_Brew(message)
        elif id == Smarter.CommandCoffeeStop:           response = self.__simulate_CoffeeStop()
        elif id == Smarter.CommandBrewDefault:          response = self.__simulate_BrewDefault()
        elif id == Smarter.CommandHeatFormula:          response = self.__simulate_HeatFormula(message)
        elif id == Smarter.CommandHeat:                 response = self.__simulate_Heat(message)
        elif id == Smarter.CommandHeatDefault:          response = self.__simulate_HeatDefault()
        elif id == Smarter.CommandKettleStop:           response = self.__simulate_KettleStop()
        
        elif id == Smarter.CommandStoreTimer:           response = self.__simulate_StoreTimer(message)
        elif id == Smarter.CommandTimers:               response = self.__simulate_Timers(message)
        elif id == Smarter.CommandDisableTimer:         response = self.__simulate_DisableTimer(message)
        else:                                           response = self.__encode_CommandStatus(Smarter.StatusInvalid)
        return response


    def __block_response(self,message):
        """
        Returns list of reply messages and preform sim action if needed of blocked response messages.
        """
        id = Smarter.raw_to_number(message[0])
        # blocking the other way....
        if id == Smarter.ResponseCommandStatus:         response = self.__encode_CommandStatus(Smarter.StatusSucces)
        elif id == Smarter.ResponseWirelessNetworks:    response = self.__simulate_WifiScan()
        elif id == Smarter.ResponseDeviceInfo:          response = self.__simulate_DeviceInfo()
        elif id == Smarter.ResponseCoffeeSettings:      response = self.__simulate_CoffeeSettings()
        elif id == Smarter.ResponseKettleSettings:      response = self.__simulate_KettleSettings()
        elif id == Smarter.ResponseKettleStatus:        response = self.__simulate_KettleStatus()
        elif id == Smarter.ResponseCoffeeStatus:        response = self.__simulate_CoffeeStatus()
        elif id == Smarter.ResponseWifiFirmware:        response = self.__encode_WifiFirmware()
        elif id == Smarter.ResponseKettleHistory:       response = self.__enable_KettleHistory()
        elif id == Smarter.ResponseCoffeeHistory:       response = self.__encode_CoffeeHistory()
        elif id == Smarter.ResponseTimers:              response = self.__encode_Timers()
        elif id == Smarter.ResponseCarafe:              response = self.__encode_Carafe(self.sim_carafeRequired)
        elif id == Smarter.ResponseMode:                response = self.__encode_Mode(self.sim_mode)
        elif id == Smarter.ResponseBase:                response = self.__encode_Base(self.sim_waterSensorBase)
        else:                                           response = self.__encode_CommandStatus(Smarter.StatusInvalid)
        return response



    #------------------------------------------------------
    # iBrew: iKettle 2.0 and Smarter Coffee Simulator
    #------------------------------------------------------
    #
    # History:
    # v0.1 Black Water Engine
    # v0.2 iSmarter.am Engine
    #------------------------------------------------------

    def __simulation_default(self):


        self.sim_heaterOn               = False
        self.sim_unknown                = 0
        
        self.sim_waterSensorBase        = 974
        self.sim_waterSensor            = 2010
        self.sim_kettleStatus           = Smarter.KettleReady
        self.sim_onBase                 = True
        self.sim_keepWarmOn             = False
        self.sim_formulaCoolingOn          = False
        self.sim_temperature            = 24
        
        self.sim_defaultTemperature     = 100
        self.sim_defaultKeepWarmTime    = 0
        self.sim_defaultFormula         = False
        self.sim_defaultFormulaTemperature = 75
        
        self.sim_waterLevel             = Smarter.CoffeeWaterFull
        self.sim_strength               = Smarter.CoffeeMedium
        self.sim_cups                   = 1
        self.sim_hotPlate               = 0
        self.sim_grind                  = False
        
        self.sim_defaultCups            = 1
        self.sim_defaultStrength        = Smarter.CoffeeMedium
        self.sim_defaultGrind           = False
        self.sim_defaultHotPlate        = 0
        
        self.sim_mode                   = False
        self.sim_carafeRequired         = False
        self.sim_cupsBrew               = 0
        
        self.sim_waterEnough            = True
        self.sim_carafe                 = True
        self.sim_timerEvent             = False
        self.sim_ready                  = True
        self.sim_hotPlateOn             = False
        self.sim_grinderOn              = False
        self.sim_working                = False
        
        self.sim_WifiFirmware           = "6b41542b474d520d0d0a41542076657273696f6e3a392e34302e302e302841756720203820323031352031343a34353a3538290d0a53444b2076657273696f6e3a312e332e300d0a636f6d70696c652074696d653a41756720203820323031352031373a31393a33380d0a4f4b7e"

        # internal data kettle variable
        self.sim_setTemperature         = 100
        self.sim_setKeepWarmTime        = 0
        self.sim_setFormulaTemperature  = 75
        self.sim_setFormula             = False
        
        self.sim_keepwarm_timeout       = 0
        self.sim_cooling_timer          = 0
        self.sim_cooling_timeout        = 20
        self.sim_onbase_timer           = 0
        self.sim_onbase_timeout1        = 50
        self.sim_onbase_timeout2        = 30
        self.sim_onbase_timeout3        = 10
        
        # constants
        self.sim_rangeTemperature       = 20
        self.sim_roomTemperature        = 21
        self.sim_waterSensorEmpty       = 1975
        self.sim_waterSensorFull        = 2100
        self.sim_waterSensorCup         = 50
        self.sim_wiggleSmallWaterSensor = 5
        self.sim_wiggleLargeWaterSensor = 20
        self.sim_wiggleTemperature      = 5
        self.sim_coolTemperature        = 11
        self.sim_lowestTemperature      = 10
        self.sim_chance                 = 3
        
        
        # internal data coffee machine variable
        self.sim_waterLevelCups         = 10
        self.sim_useHotPlate            = False
        self.sim_hotPlate_timout        = 0
        self.sim_grinder_timeout        = 5
        self.sim_heating_timeout        = 15
        self.sim_heating_cup_timeout    = 3
        self.sim_grinder_timer          = 0
        self.sim_heating_timer          = 0
        self.sim_setCups                = 1
        self.sim_setStrength            = Smarter.CoffeeMedium
        self.sim_setGrind               = False
        self.sim_setHotPlate            = 0

    
    
    
    def __simulate_device(self):
        self.simulator_run = True
        time.sleep(0.25)
        if self.dump:
            logging.info("[" + self.host + "] Simulation Running")
        while self.simulator_run:
            if self.deviceId == Smarter.DeviceKettle:
            
                self.sim_cooling_timer += 1
                self.sim_onbase_timer += 1
                
                # take kettle off base
                if (self.sim_heaterOn and self.sim_onbase_timer % self.sim_onbase_timeout1) and (not self.sim_heaterOn and self.sim_onbase_timer % self.sim_onbase_timeout2) and self.sim_onBase and 1 != random.randint(1,self.sim_chance):
                    
                    if self.dump and self.dump_status:
                        logging.debug("Simulation kettle ready and off base")
                    self.sim_onBase = False
                    self.sim_heaterOn = False
                    self.sim_kettleStatus = Smarter.KettleReady
                    self.sim_keepWarmOn = False
                    self.sim_formulaCoolingOn = False
                    self.sim_keepwarm_timeout = 0
                
                # water lever up when almost empty... or else if heated enough one cup
                elif self.sim_onbase_timer % self.sim_onbase_timeout3 and not self.sim_onBase:
                    self.sim_onBase = True
                    
                    if self.dump and self.dump_status:
                        logging.debug("Simulation kettle on base")
                    if self.sim_heaterOn and self.sim_setTemperature < self.sim_rangeTemperature + self.sim_temperature:
                        self.sim_waterSensor -= self.sim_waterSensorCup + random.randint(-self.sim_wiggleSmallWaterSensor,self.sim_wiggleSmallWaterSensor)
                        if self.sim_waterSensorEmpty > self.sim_waterSensor:
                            self.sim_waterSensor = self.sim_waterSensorEmpty + random.randint(-self.sim_wiggleSmallWaterSensor,self.sim_wiggleSmallWaterSensor)
                    if self.sim_waterSensor < self.sim_waterSensorEmpty + self.sim_waterSensorCup + random.randint(-self.sim_wiggleSmallWaterSensor,self.sim_wiggleSmallWaterSensor):
                        self.sim_waterSensor = self.sim_waterSensorFull - random.randint(0,self.sim_wiggleLargeWaterSensor)
                    # and water is cooling off base!!!
                    self.sim_temperature -= random.randint(0,self.sim_coolTemperature)
                    if self.sim_temperature < self.sim_lowestTemperature:
                        self.sim_temperature = self.sim_roomTemperature
        
                # heatin water time
                elif self.sim_heaterOn:
                    self.sim_temperature += 1
                    if self.sim_setTemperature <= self.sim_temperature or 100 == self.sim_temperature:
                        if self.sim_setFormula:
                            self.sim_kettleStatus = Smarter.KettleFormulaCooling
                            self.sim_formulaCoolingOn  = True
                            self.sim_keepwarm_timeout = 0
                            if self.dump and self.dump_status:
                                logging.debug("Simulation kettle formula cooling")
                        elif self.sim_setKeepWarmTime > 0:
                            if self.dump and self.dump_status:
                                logging.debug("Simulation kettle keepwarm")
                            self.sim_keepWarmOn = True
                            self.sim_keepwarm_timeout = time.time() + (self.sim_setKeepWarmTime * 60)
                            self.sim_kettleStatus = Smarter.KettleKeepWarm
                        else:
                            if not self.dump:
                                logging.debug("Simulation kettle ready")
                            self.sim_kettleStatus = Smarter.KettleReady
                            self.sim_keepwarm_timeout = 0
                        self.sim_heaterOn = False



                # keepwarm time
                if (time.time() > self.sim_keepwarm_timeout) and self.sim_keepWarmOn:
                    if self.dump and self.dump_status:
                        logging.debug("Simulation kettle ready")
                    self.sim_keepWarmOn = False
                    self.sim_kettleStatus = Smarter.KettleReady
                    self.sim_keepwarm_timeout = 0
                

            
                # cooling down water time
                if not self.sim_heaterOn and not self.sim_keepWarmOn and self.sim_cooling_timer % self.sim_cooling_timeout and self.sim_temperature > self.sim_roomTemperature:
                    self.sim_temperature -= 1
                    
                # formula cooling down water trigger time
                if self.sim_formulaCoolingOn and self.sim_temperature <= self.sim_setFormulaTemperature:
                    if self.sim_setKeepWarmTime > 0:
                        if self.dump and self.dump_status:
                            logging.debug("Simulation kettle keepwarm")
                        self.sim_keepWarmOn = True
                        self.sim_keepwarm_timeout = time.time() + (self.sim_setKeepWarmTime * 60)
                        self.sim_kettleStatus = Smarter.KettleKeepWarm
                    else:
                        if self.dump and self.dump_status:
                            logging.debug("Simulation kettle ready")
                        self.sim_kettleStatus = Smarter.KettleReady
                        self.sim_keepwarm_timeout = 0
                    self.sim_formulaCoolingOn = False

                
            elif self.deviceId == Smarter.DeviceCoffee:
            
                if self.sim_grinderOn:
                    #print "Grinding"
                    if (self.sim_grinder_timeout * self.sim_setStrength) <= self.sim_grinder_timer:
                        self.sim_grinderOn = False
                        self.sim_grinder_timer = 0
                        self.sim_heaterOn = True
                    else:
                        self.sim_grinder_timer += 1
                    
                elif self.sim_heaterOn:
                    #print "Heating"
                    if (self.sim_heating_timeout + self.sim_heating_cup_timeout * self.sim_setCups) <= self.sim_heating_timer:
                        self.sim_heaterOn = False
                        self.sim_heating_timer = 0
                        self.sim_ready = True
                        
                        self.sim_waterLevelCups -= self.sim_cupsBrew
                        self.sim_waterLevel = self.sim_waterLevelCups / 4
                        self.sim_waterEnough = (self.sim_cups <= self.sim_waterLevelCups)
                        
                        if self.sim_useHotPlate:
                            self.sim_hotPlateOn = True
                            self.sim_useHotPlate = False
                            self.sim_hotPlate_timout = time.time() + (self.sim_setHotPlate * 60)
                        else:
                            self.sim_working = False
                    else:
                        self.sim_heating_timer += 1
                    
                elif self.sim_hotPlateOn:
                     if (time.time() > self.sim_hotPlate_timout):
                        self.sim_hotPlateOn = False
                        self.sim_working = False
                        self.sim_hotPlate_timout = 0
                
            time.sleep(1)

            
        if self.dump:
            logging.info("[" + self.host + "] Simulation Stopped")

    
    #------------------------------------------------------
    # MESSAGE SIMULATE RESPONSES
    #------------------------------------------------------



    def __simulate_KettleStatus(self):
        return self.__encode_KettleStatus(self.sim_kettleStatus,self.sim_temperature, self.sim_waterSensor + random.randint(-self.sim_wiggleTemperature,self.sim_wiggleTemperature), self.sim_onBase, self.sim_unknown)
        


    def __simulate_CoffeeStatus(self):
        return self.__encode_CoffeeStatus(self.sim_cups,self.sim_strength, self.sim_cupsBrew, self.sim_waterLevel, self.sim_waterEnough, self.sim_carafe, self.sim_grind, self.sim_ready, self.sim_grinderOn, self.sim_heaterOn, self.sim_hotPlateOn, self.sim_working, self.sim_timerEvent, self.sim_unknown)
    


    def __simulate_DeviceTime(self,message):
        """
        Simulate response on command DeviceTime
        FIX not finished...
        """
        return self.__encode_CommandStatus(Smarter.StatusSucces)
        
       
         
    def __simulate_ResetSettings(self):
        """
        Simulate response on command ResetSettings
        """
        self.__simulation_default()
        return self.__encode_CommandStatus(Smarter.StatusSucces)
        
       
       
    def __simulate_Brew(self,message):
        """
        Simulate response on command Brew
        """

        if self.sim_carafeRequired and not self.sim_carafe:
            return self.__encode_CommandStatus(Smarter.StatusNoCarafe)
        
        

        if self.sim_heaterOn or self.sim_grinderOn:
            return self.__encode_CommandStatus(Smarter.StatusBusy)
        
        try:
            self.sim_setCups         = Smarter.raw_to_cups(message[1])
            self.sim_setKeepWarmTime = Smarter.raw_to_strength(message[2])
            self.sim_setHotPlate     = Smarter.raw_to_hotplate(message[3],self.version)
            self.sim_setGrind        = Smarter.raw_to_bool(message[4])
        except SmarterError:
            return self.__encode_CommandStatus(Smarter.StatusFailed)

        if self.sim_cups > self.sim_waterLevelCups:
            return self.__encode_CommandStatus(Smarter.StatusNoWater)
        
        self.sim_waterEnough = (self.sim_cups <= self.sim_waterLevelCups)
        
        self.sim_ready = False
        self.sim_working = True
        self.sim_grinderOn = (Smarter.CoffeeBeans == self.sim_setGrind)

        if self.sim_setHotPlate != 0:
            self.sim_useHotPlate = True

        if not self.sim_grinderOn:
            self.sim_heaterOn = True

        self.sim_cupsBrew = self.sim_setCups
        return self.__encode_CommandStatus(Smarter.StatusSucces)
        
        
        
    def __simulate_CoffeeStop(self):
        """
        Simulate response on command CoffeeStop
        """
        
        if self.sim_heaterOn:
            self.sim_waterLevelCups -= self.sim_cupsBrew
            self.sim_waterLevel = self.sim_waterLevelCups / 4
            self.sim_waterEnough = (self.sim_cups <= self.sim_waterLevelCups)

        self.sim_heaterOn               = False
        self.sim_ready                  = True
        self.sim_hotPlateOn             = False
        self.sim_grinderOn              = False
        self.sim_working                = False
        self.sim_hotPlate_timout        = 0
        self.sim_grinder_timer          = 0
        self.sim_heating_timer          = 0
        self.sim_useHotPlate            = False
        return self.__encode_CommandStatus(Smarter.StatusSucces)
        
        
        
    def __simulate_BrewDefault(self):
        """
        Simulate response on command BrewDefault
        """
        
        if self.sim_carafeRequired and not self.sim_carafe:
            return self.__encode_CommandStatus(Smarter.StatusNoCarafe)
        
        if self.sim_heaterOn or self.sim_grinderOn:
            return self.__encode_CommandStatus(Smarter.StatusBusy)
        
        if self.sim_cups > self.sim_waterLevelCups:
            return self.__encode_CommandStatus(Smarter.StatusNoWater)
        
        self.sim_setStrength = self.sim_strength
        self.sim_setHotPlate = self.sim_hotPlate
        self.sim_setCups = self.sim_cups
        self.sim_waterEnough = (self.sim_setCups <= self.sim_waterLevelCups)
        self.sim_ready = False
        self.sim_working = True
        self.sim_grinderOn = (Smarter.CoffeeBeans == self.sim_grind)
        
        if self.sim_setHotPlate != 0:
            self.sim_useHotPlate = True
        
        if not self.sim_grinderOn:
            self.sim_heaterOn = True
        
        self.sim_cupsBrew = self.sim_setCups
        return self.__encode_CommandStatus(Smarter.StatusSucces)
        
        
    
    def __simulate_HotplateOn(self,message):
        """
        Simulate response on command HotplateOn
        """
        
        if self.sim_heaterOn or self.sim_grinderOn:
            return self.__encode_CommandStatus(Smarter.StatusBusy)
        
        # assumption, mother of all f.. ups, hope it works like this...
        if not self.sim_carafe or self.sim_mode:
            return self.__encode_CommandStatus(Smarter.StatusNoCarafe)
        
        
        # if no message then use default.
        if message[1] == Smarter.MessageTail:
            self.sim_hotPlate = self.sim_defaultHotPlate
        else:
            try:
                hotPlate = Smarter.raw_to_hotplate(message[1],self.version)
            except SmarterError:
                return self.__encode_CommandStatus(Smarter.StatusFailed)
        
        if hotPlate == 0:
            self.sim_hotPlateOn = False
            if not self.sim_heaterOn and not self.sim_grinderOn:
                self.sim_working = False
        else:
            self.sim_hotPlateOn = True
            self.sim_working = True
            self.sim_hotPlate_timout = time.time() + (hotPlate * 60)
        return self.__encode_CommandStatus(Smarter.StatusSucces)
    
    
    
    def __simulate_HotplateOff(self):
        """
        Simulate response on command HotplateOff
        """
        if not self.sim_heaterOn and not self.sim_grinderOn:
            self.sim_working = False
        self.sim_hotPlateOn = False
        self.sim_hotPlate_timout = 0
        return self.__encode_CommandStatus(Smarter.StatusSucces)



    def __simulate_StoreTimer(self,message):
        """
        Simulate response on command StoreTimer
        FIX
        """
        return self.__encode_CommandStatus(Smarter.StatusSucces)



    def __simulate_Timers(self,message):
        """
        Simulate response on command GetTimers
        FIX index 0...  type... aaagh....
        """
        if message[1] == Smarter.MessageTail:
            return self.__encode_GetTimers(0)
        else:
            return self.__encode_GetTimers(Smarter.raw_to_number(message[1]))



    def __simulate_DisableTimer(self,message):
        """
        Simulate response on command DisableTimer
        FIX! raw_to_number -> raw_to_index
        """
        return self.__encode_CommandStatus(Smarter.StatusSucces)



    def __simulate_Heat(self,message):
        """
        Simulate response on command Heat
        """
        try:
            self.sim_setTemperature  = Smarter.raw_to_temperature(message[1])
            self.sim_setKeepWarmTime = Smarter.raw_to_keepwarm(message[2])
        except SmarterError:
            return self.__encode_CommandStatus(Smarter.StatusFailed)
        self.sim_setFormula      = False
        self.sim_heaterOn        = True
        self.sim_kettleStatus    = Smarter.KettleHeating
        return self.__encode_CommandStatus(Smarter.StatusSucces)



    def __simulate_KettleStop(self):
        """
        Simulate response on command KettleStop
        """
        self.sim_heaterOn = False
        self.sim_keepWarmOn = False
        self.sim_setTemperature = 24
        self.sim_kettleStatus = Smarter.KettleReady
        return self.__encode_CommandStatus(Smarter.StatusSucces)



    def __simulate_HeatFormula(self,message):
        """
        Simulate response on command HeatFormula
        """
        try:
            self.sim_setFormulaTemperature = Smarter.raw_to_temperature(message[1])
            self.sim_setKeepWarmTime = Smarter.raw_to_keepwarm(message[2])
        except SmarterError:
            return self.__encode_CommandStatus(Smarter.StatusFailed)
        self.sim_setTemperature = 100
        self.sim_setFormula = True
        self.sim_heaterOn = True
        self.sim_kettleStatus = Smarter.KettleHeating
        return self.__encode_CommandStatus(Smarter.StatusSucces)



    def __simulate_HeatDefault(self):
        """
        Simulate response on command HeatDefault
        """
        self.sim_setFormulaTemperature = self.sim_defaultFormulaTemperature
        self.sim_setTemperature = self.sim_defaultTemperature
        self.setFormula = self.sim_defaultFormula
        self.sim_setKeepWarmTime = self.sim_defaultKeepWarmTime
        self.sim_heaterOn = True
        self.sim_kettleStatus = Smarter.KettleHeating
        return self.__encode_CommandStatus(Smarter.StatusSucces)



    def __simulate_DeviceInfo(self):
        """
        Simulate response on command DeviceInfo
        """
        return self.__encode_DeviceInfo(self.deviceId,self.version)



    def __simulate_KettleStoreSettings(self,message):
        """
        Simulate response on command Kettle Store Settings
        """
        try:
            self.sim_defaultTemperature         = Smarter.raw_to_temperature(message[2])
            self.sim_defaultFormula             = Smarter.raw_to_bool(message[3])
            self.sim_defaultFormulaTemperature  = Smarter.raw_to_temperature(message[4])
            self.sim_defaultKeepWarmTime        = Smarter.raw_to_keepwarm(message[1])
        except SmarterError:
            return self.__encode_CommandStatus(Smarter.StatusFailed)
        return self.__encode_CommandStatus(Smarter.StatusSucces)
    
    
    def __simulate_KettleSettings(self):
        """
        Simulate response on command Kettle Get Settings
        """
        return self.__encode_KettleGetSettings(self.sim_defaultTemperature,self.sim_defaultKeepWarmTime,self.sim_defaultFormulaTemperature)
    
    
    
    def __simulate_CoffeeSettings(self):
        """
        Simulate response on command Coffee Get Settings
        """
        return self.__encode_CoffeeGetSettings(self.sim_defaultCups,self.sim_defaultStrength,self.sim_defaultGrind,self.sim_defaultHotPlate)
    
    
    
    def __simulate_CoffeeStoreSettings(self,message):
        """
        Simulate response on command Coffee Store Settings
        """
        try:
            self.sim_defaultHotPlate    = Smarter.raw_to_hotplate(message[4],self.version)
            self.sim_defaultCups        = Smarter.raw_to_cups(message[2])
            self.sim_defaultStrength    = Smarter.raw_to_strength(message[1])
            self.sim_defaultGrind       = Smarter.raw_to_bool(message[3])
        except SmarterError:
            return self.__encode_CommandStatus(Smarter.StatusFailed)
        return self.__encode_CommandStatus(Smarter.StatusSucces)



    def __simulate_Grinder(self):
        """
        Simulate response on command Grinder
        """
        self.sim_grind = not self.sim_grind
        return self.__encode_CommandStatus(Smarter.StatusSucces)
    
    
    
    def __simulate_Strength(self,message):
        """
        Simulate response on command Strength
        """
        try:
            self.sim_strength = Smarter.raw_to_strength(message[1])
        except SmarterError:
            return self.__encode_CommandStatus(Smarter.StatusFailed)
        return self.__encode_CommandStatus(Smarter.StatusSucces)
    
    
    
    def __simulate_Cups(self,message):
        """
        Simulate response on command Cups
        """
        try:
            cups = Smarter.raw_to_cups(message[1])
        except SmarterError:
            return self.__encode_CommandStatus(Smarter.StatusFailed)

        if self.sim_mode and cups > 3:
            return self.__encode_CommandStatus(Smarter.StatusFailed)

        self.sim_cups = cups

        self.sim_waterEnough = (self.sim_cups <= self.sim_waterLevelCups)
        # if cup mode no more then 3? FIX
        return self.__encode_CommandStatus(Smarter.StatusSucces)
    
    

    def __simulate_Carafe(self):
        """
        Simulate response on command Carafe
        """
        return self.__encode_GetCarafe(self.sim_carafeRequired)
    


    def __simulate_SetCarafe(self,message):
        """
        Simulate response on command SetCarafe
        """
        try:
            self.sim_carafeRequired = Smarter.raw_to_bool(message[1])
        except SmarterError:
            return self.__encode_CommandStatus(Smarter.StatusFailed)
        return self.__encode_CommandStatus(Smarter.StatusSucces)



    def __simulate_Mode(self):
        """
        Simulate response on command Mode
        """
        return self.__encode_GetMode(self.sim_mode)
    


    def __simulate_SetMode(self,message):
        """
        Simulate response on command SetMode
        """
        try:
            self.sim_mode = Smarter.raw_to_bool(message[1])
        except SmarterError:
            return self.__encode_CommandStatus(Smarter.StatusFailed)
        if self.sim_mode and self.sim_cups > 3:
            self.sim_cups = 3
        return self.__encode_CommandStatus(Smarter.StatusSucces)



    def __simulate_Base(self):
        """
        Simulate response on command GetBase
        """
        return self.__encode_GetBase(self.sim_waterSensorBase)



    def __simulate_Calibrate(self):
        """
        Simulate response on command Calibrate
        """
        self.sim_waterSensorBase = random.randint(975,999)
        return self.__encode_Calibrate(self.sim_waterSensorBase)



    def __simulate_StoreBase(self,message):
        """
        Simulate response on command StoreBase
        """
        try:
            self.sim_waterSensorBase = Smarter.raw_to_watersensor(message[1],message[2])
        except SmarterError:
            return self.__encode_CommandStatus(Smarter.StatusFailed)
        return self.__encode_CommandStatus(Smarter.StatusSucces)



    def __simulate_KettleHistory(self):
        """
        Simulate response on commandkettle history, no history
        """
        return self.__encode_KettleHistory()



    def __simulate_CoffeeHistory(self):
        """
        Simulate response on commandcoffee history, no history
        """
        return self.__encode_CoffeeHistory()



    def __simulate_WifiFirmware(self):
        """
        Simulate response on commandWifiFirmware encode simulated wifi firmware response message (note: changes version number for relay detection)
        """
        return self.__encode_WifiFirmware(self.sim_WifiFirmware)



    def __simulate_WifiScan(self):
        """
        Simulate response on commandWifiScan encode simulated one wifi access point with random dBm response message
        """
        return self.__encode_WifiScan('iBrew Relay: ('+self.host+':'+str(self.port)+'),-'+str(random.randint(70,90))+'}')



    def __simulate_WifiJoin(self):
        """
        Simulate response on commandWifiJoin (probably just should disconnect or send nothing FIX)
        """
        return self.__encode_CommandStatus(Smarter.StatusSucces)



    def __simulate_WifiPassword(self):
        """
        Simulate response on commandset wifi password
        And yes we can snoop here on wifi network names & password... (not implemented. do not care)
        """
        return self.__encode_CommandStatus(Smarter.StatusSucces)



    def __simulate_Network(self):
        """
        Simulate response on commandset wireless network name
        """
        return self.__encode_CommandStatus(Smarter.StatusSucces)



    def __simulate_Update(self):
        """
        Simulate response on command Update
        """
        return self.__encode_CommandStatus(Smarter.StatusSucces)



    def __simulate_69(self):
        """
        Simulate response on command 69
        """
        return self.__encode_CommandStatus(Smarter.StatusSucces)



    def __simulate_20(self):
        """
        Simulate response on command 20
        """
        return self.__encode_CommandStatus(Smarter.StatusSucces)



    def __simulate_22(self):
        """
        Simulate response on command 22
        """
        return self.__encode_CommandStatus(Smarter.StatusSucces)



    def __simulate_23(self):
        """
        Simulate response on command 23
        """
        return self.__encode_CommandStatus(Smarter.StatusSucces)



    def __simulate_30(self):
        """
        Simulate response on command 30
        """
        return self.__encode_CommandStatus(Smarter.StatusSucces)



    #------------------------------------------------------
    # MESSAGE RESPONSE ENCODERS
    #------------------------------------------------------


    def __encode_KettleStatus(self,status,temperature,watersensor,onbase,unknown=0):
        """
        Encode kettle status response message
        """
        return [Smarter.number_to_raw(Smarter.ResponseKettleStatus) + Smarter.number_to_raw(status) + Smarter.temperaturemerged_to_raw(temperature,onbase) + Smarter.watersensor_to_raw(watersensor) + Smarter.number_to_raw(unknown) + Smarter.number_to_raw(Smarter.MessageTail)]



    def __encode_CoffeeStatus(self,cups,strenght,cupsbrew,waterlevel,waterenough,carafe,grind,ready,grinder,heater,hotplate,working,timer,unknown=0):
        """
        Encode coffee machine status response message
        """
        coffeestatus = Smarter.coffeeStatus_to_raw(carafe,grind,ready,grinder,heater,hotplate,working,timer)
        cupsmerged   = Smarter.cupsmerged_to_raw(cups,cupsbrew)
        watermerged  = Smarter.waterlevel_to_raw(waterlevel,waterenough)
        return [Smarter.number_to_raw(Smarter.ResponseCoffeeStatus) + coffeestatus + watermerged + Smarter.number_to_raw(unknown) + Smarter.strength_to_raw(strenght) + cupsmerged + Smarter.number_to_raw(Smarter.MessageTail)]



    def __encode_Timers(self):
        """
        Encode Timers response message
        FIX NOT IMPLEMENTED
        """
        return self.__encode_CommandStatus(Smarter.StatusSucces)



    def __encode_GetTimers(self,index):
        """
        Encode Get Timers response message
        FIX NOT IMPLEMENTED
        """
        return self.__encode_Timers() + self.__encode_CommandStatus(Smarter.StatusSucces)



    def __encode_DeviceInfo(self,type,version):
        """
        Encode device info response message
        """
        return [Smarter.number_to_raw(Smarter.ResponseDeviceInfo) + Smarter.number_to_raw(type) + Smarter.number_to_raw(version) + Smarter.number_to_raw(Smarter.MessageTail)]



    def __encode_RelayInfo(self,version,ip):
        """
        Encode relay device info response message
        """
        return [Smarter.number_to_raw(Smarter.ResponseRelayInfo) + Smarter.number_to_raw(version) + Smarter.text_to_raw(ip) + Smarter.number_to_raw(Smarter.MessageTail)]



    def __encode_RelayModifiersInfo(self,modifiers):
        """
        Encode relay device info response message
        """
        return [Smarter.number_to_raw(Smarter.ResponseRelayModifiersInfo) + Smarter.text_to_raw(modifiers) + Smarter.number_to_raw(Smarter.MessageTail)]



    def __encode_CommandStatus(self,status):
        """
        Encode commandstatus response message
        """
        return [Smarter.number_to_raw(Smarter.ResponseCommandStatus) + Smarter.number_to_raw(status) + Smarter.number_to_raw(Smarter.MessageTail)]



    def __encode_KettleSettings(self,temperature,keepwarm,formulatemperature):
        """
        Encode Kettle Settings response message
        """
        response =  Smarter.number_to_raw(Smarter.ResponseKettleSettings) + Smarter.temperature_to_raw(temperature) + Smarter.keepwarm_to_raw(keepwarm) + Smarter.temperature_to_raw(formulatemperature) + Smarter.number_to_raw(Smarter.MessageTail)
        # emulate bug in v22
        response += Smarter.number_to_raw(0)
        return [response]



    def __encode_KettleGetSettings(self,temperature,keepwarm,formulatemperature):
        """
        Encode Kettle Get Settings response messages
        """
        return self.__encode_KettleSettings(temperature,keepwarm,formulatemperature) + self.__encode_CommandStatus(Smarter.StatusSucces)



    def __encode_CoffeeGetSettings(self,cups,strength,grind,hotplate):
        """
        Encode coffee machine get settings response messages
        """
        return self.__encode_CoffeeSettings(cups,strength,grind,hotplate) + self.__encode_CommandStatus(Smarter.StatusSucces)



    def __encode_CoffeeSettings(self,cups,strength,grind,hotplate):
        """
        Encode coffee machine settings response message
        """
        return [Smarter.number_to_raw(Smarter.ResponseCoffeeSettings) + Smarter.cups_to_raw(cups) + Smarter.strength_to_raw(strength) + Smarter.bool_to_raw(grind) + Smarter.hotplate_to_raw(hotplate,self.version) + Smarter.number_to_raw(Smarter.MessageTail)]



    def __encode_GetCarafe(self,carafeRequired):
        """
        Encode coffee machine carafe mode response messages
        """
        return  self.__encode_Carafe(carafeRequired) + self.__encode_CommandStatus(Smarter.StatusSucces)
  
  
  
    def __encode_Carafe(self,carafeRequired):
        """
        Encode coffee machine mode response message
        """
        return [Smarter.number_to_raw(Smarter.ResponseCarafe) + Smarter.bool_to_raw(carafeRequired) + Smarter.number_to_raw(Smarter.MessageTail)]



    def __encode_GetMode(self,mode):
        """
        Encode coffee machine mode response messages
        """
        return self.__encode_Mode(mode) + self.__encode_CommandStatus(Smarter.StatusSucces)
    


    def __encode_Mode(self,mode):
        """
        Encode coffee machine mode response message
        """
        return [Smarter.number_to_raw(Smarter.ResponseMode) + Smarter.bool_to_raw(mode) + Smarter.number_to_raw(Smarter.MessageTail)]



    def __encode_Base(self,base):
        """
        Encode kettle base response message
        """
        return [Smarter.number_to_raw(Smarter.ResponseBase) + Smarter.watersensor_to_raw(base) + Smarter.number_to_raw(Smarter.MessageTail)]



    def __encode_GetBase(self,base):
        """
        Encode base command response messages
        """
        return self.__encode_Base(base) + self.__encode_CommandStatus(Smarter.StatusSucces)


    
    def __encode_Calibrate(self,base):
        """
        Encode kettle calibrate base respons message
        """
        
        return self.__encode_Base(base)



    def __encode_KettleHistory(self,history=""):
        """
        Encode no kettle history response message
        FIX Should be a list of history as input...
        """
        return [Smarter.number_to_raw(Smarter.ResponseKettleHistory) + Smarter.number_to_raw(0) + Smarter.number_to_raw(Smarter.MessageTail)]
 
 
 
    def __encode_CoffeeHistory(self,history=""):
        """
        Encode no coffee history response message
        FIX Should be a list of history as input...
        """
        return [Smarter.number_to_raw(Smarter.ResponseCoffeeHistory) + Smarter.number_to_raw(0) + Smarter.number_to_raw(Smarter.MessageTail)]



    def __encode_WifiFirmware(self,wifi="6b41542b474d520d0d0a41542076657273696f6e3a302e34302e302e302841756720203820323031352031343a34353a3538290d0a53444b2076657273696f6e3a312e332e300d0a636f6d70696c652074696d653a41756720203820323031352031373a31393a33380d0a4f4b7e"):
        """
        Encode simulated wifi firmware response message
        """
        return [Smarter.codes_to_message(wifi)]



    def __encode_WifiScan(self,list):
        """
        Encode wifi access point response message (FIX should take a list of networks))
        """
        return [Smarter.number_to_raw(Smarter.ResponseWirelessNetworks) + Smarter.text_to_raw(list) + Smarter.number_to_raw(Smarter.MessageTail)]


    #------------------------------------------------------
    # TRIGGERS
    #------------------------------------------------------


    @_threadsafe_function
    def __write_triggers(self):
    
        self.print_groups()
        self.print_triggers()
        
        if self.dump:
            logging.debug("Write Triggers: [" + self.host + ":" + str(self.port) + "]" )
        section = self.host + "." + str(self.port) + ".triggers"

        #if self.isKettle:
        #    section += ".kettle"
        #elif self.isCoffee:
        #    section += ".coffee"
        #else:
        #    return

        config = SafeConfigParser()

        if not os.path.exists(self.settingsPath):
                os.makedirs(self.settingsPath)
        
        config.read(self.settingsPath+'ibrew.conf')
        
        try:
            config.add_section(section)
        except DuplicateSectionError:
            pass


        try:
            g = []
            for i in self.triggersGroups:
                g += [i[0]]
            
            config.set(section, "groups", ','.join(g))
        except Exception:
            pass

        for i in g:
            try:
                config.add_section(section+"."+i)
            except DuplicateSectionError:
                pass
            try:
                config.set(section+"."+i, "Active", str(self.triggersGroups[self.__findGroup(i)][1]))
                config.set(section+"."+i, "State", str(self.triggersGroups[self.__findGroup(i)][2][0]))
            except Exception:
                pass # logging.warning("Error reading triggers " + str(e))

            #if self.isKettle:
            for j in Smarter.triggersKettle:
                try:
                    config.set(section+"."+i, Smarter.triggerName(j),self.triggerGet(i,Smarter.triggerName(j)))
                except Exception, e:
                    pass # logging.warning("Error reading triggers " + str(e))


            #if self.isCoffee:
            for j in Smarter.triggersCoffee:
                try:
                    config.set(section+"."+i, Smarter.triggerName(j),self.triggerGet(i,Smarter.triggerName(j)))
                except Exception:
                    pass # logging.warning("Error reading triggers " + str(e))
    
        with codecs.open(self.settingsPath+'ibrew.conf','wb+','utf-8') as f:
            config.write(f)
            f.close()
        #with open(self.settingsPath+'ibrew.conf', 'w') as f:
        #    config.write(f)


    def __initTriggers(self):
        self.triggersKettle = {
    
            # Operational sensors (boolean)
            Smarter.triggerBusyKettle                   : [],
            Smarter.triggerKeepWarm                     : [],
            Smarter.triggerHeaterKettle                 : [],
            Smarter.triggerFormulaCooling               : [],
            Smarter.triggerOnBase                       : [],
            
            # Data sensors
            Smarter.triggerWaterSensorBase              : [],
            Smarter.triggerDefaultKeepWarmTime          : [],
            Smarter.triggerDefaultTemperature           : [],
            Smarter.triggerDefaultFormulaTemperature    : [],
            Smarter.triggerTemperature                  : [],
            Smarter.triggerTemperatureStable            : [],
            Smarter.triggerWaterSensor                  : [],
            Smarter.triggerWaterSensorStable            : [],
            Smarter.triggerUnknownKettle                : []
        }

        self.triggersCoffee = {
            # Operational sensors (boolean)
            Smarter.triggerGrinder                      : [],
            Smarter.triggerTimerEvent                   : [],
            Smarter.triggerBusyCoffee                   : [],
            Smarter.triggerReady                        : [],
            Smarter.triggerWorking                      : [],
            Smarter.triggerHotPlate                     : [],
            Smarter.triggerHeaterCoffee                 : [],

            # Data sensors
            Smarter.triggerCarafeRequired               : [],
            Smarter.triggerMode                         : [],
            Smarter.triggerGrind                        : [],
            Smarter.triggerWaterEnough                  : [],
            Smarter.triggerCarafe                       : [],
            Smarter.triggerWaterLevel                   : [],
            Smarter.triggerStrength                     : [],
            Smarter.triggerCups                         : [],
            Smarter.triggerCupsBrew                     : [],
            Smarter.triggerUnknownCoffee                : [],
            Smarter.triggerDefaultStrength              : [],
            Smarter.triggerDefaultCups                  : [],
            Smarter.triggerDefaultGrind                 : [],
            Smarter.triggerDefaultHotplate              : []
        }

        self.triggersGroups = []

    
    @_threadsafe_function
    def __read_triggers(self):
        if self.dump:
            logging.debug("Read Triggers: [" + self.host + ":" + str(self.port) + "]" )
        section = self.host + "." + str(self.port) + ".triggers"
        #if self.isKettle:
        #    section += ".kettle"
        #elif self.isCoffee:
        #    section += ".coffee"
        #else:
        #    return


        self.__initTriggers()
        
        config = SafeConfigParser()

        if not os.path.exists(self.settingsPath):
            os.makedirs(self.settingsPath)
        
        config.read(self.settingsPath+'ibrew.conf')
        
        try:
            config.add_section(section)
        except DuplicateSectionError:
            pass


        try:
            g = config.get(section, "groups").split(",")

            for i in g:
                print i
        
                try:
                    a = config.get(section+"."+i, "Active")
                    s = config.get(section+"."+i, "State")
                except:
                    pass # logging.warning("Error reading triggers " + str(e))
                
                if not self.isTriggersGroup(i):
                    self.triggersGroups += [[i,Smarter.string_to_bool(a),Smarter.triggerCheckBooleans(s)]]
             
                for j in Smarter.triggersKettle:
                    try:
                        s = config.get(section+"."+i, Smarter.triggerName(j))
                        
                        if s != "":
                            self.triggersKettle[j] = [(i,s)]
                    except Exception:
                        pass # logging.warning("Error reading triggers " + str(e))
                
                for j in Smarter.triggersCoffee:
                    try:
                        s = config.get(section+"."+i, Smarter.triggerName(j))
                        if s != "":
                            self.triggersCoffee[j] = [(i,s)]
                    except Exception:
                        pass # logging.warning("Error reading triggers " + str(e))

        except Exception, e:
            pass # logging.warning("Error reading triggers " + str(e))


    def triggerAdd(self,group,trigger,action):
        if not self.isTriggersGroup(group):
            self.triggersGroups += [(group,True,"1")]
        self.triggerSet(group,trigger.upper(),action)
        if self.dump:
            logging.debug("Trigger " + trigger.upper() + " added to group " + group + " with action " + action )
        self.__write_triggers()


    def triggerGroupDelete(self,group):
        if self.dump:
            logging.debug("Deleting trigger group: " + group )
        for k in Smarter.triggersKettle:
            self.__triggerDelete(group,Smarter.triggersKettle[k][0])
        for c in Smarter.triggersCoffee:
             self.__triggerDelete(group,Smarter.triggersCoffee[c][0])
        
        for i in range(0,len(self.triggersGroups)):
            if group == self.triggersGroups[i][0]:
                del self.triggersGroups[i]
                break
        self.__write_triggers()
    

    def __triggerDelete(self,group,trigger):
        if self.dump:
            logging.debug("Deleting trigger " + trigger.upper() + " from group: " + group )
        id = Smarter.triggerID(trigger.upper())
        if self.isTriggersGroup(group):
            if id in self.triggersKettle:
                if len(self.triggersKettle[id]) != 0:
                    for i in range(0,len(self.triggersKettle[id])):
                        if self.triggersKettle[id][i][0] == group:
                            del self.triggersKettle[id][i]
            if id in self.triggersCoffee:
                if len(self.triggersCoffee[id]) != 0:
                    for i in range(0,len(self.triggersCoffee[id])):
                        if self.triggersCoffee[id][i][0] == group:
                            del self.triggersCoffee[id][i]
        else:
            raise SmarterErrorOld("Trigger group not found")


    def triggerDelete(self,group,trigger):
        if self.dump:
            logging.debug("Deleting trigger: " + trigger.upper() + " from group " + group )
        self.__triggerDelete(group,trigger)
        self.__write_triggers()

    
    def triggerGet(self,group,trigger):
        id = Smarter.triggerID(trigger)
        if id in self.triggersKettle:
            if self.triggersKettle[id] is not None:
                for i in self.triggersKettle[id]:
                    if i[0] == group: return i[1]
        if id in self.triggersCoffee:
            if self.triggersCoffee[id] is not None:
                for i in self.triggersCoffee[id]:
                    if i[0] == group: return i[1]
        return ""


    def __triggerHeartBeats(self):
        for j in Smarter.triggersKettle:
            self.__triggerHeartBeat(j)
        for j in Smarter.triggersCoffee:
            self.__triggerHeartBeat(j)

    def __triggerHeartBeat(self,triggerID):
        def fire(triggerID,x): self.__trigger(triggerID,x,x)
        
        # Kettle
        if triggerID == Smarter.triggerTemperatureStable:            fire(triggerID,self.temperatureStable)
        if triggerID == Smarter.triggerWaterSensorStable:            fire(triggerID,self.waterSensorStable)
        if triggerID == Smarter.triggerBusyKettle:                   fire(triggerID,self.busy)
        if triggerID == Smarter.triggerDefaultTemperature:           fire(triggerID,self.defaultTemperature)
        if triggerID == Smarter.triggerDefaultFormulaTemperature:    fire(triggerID,self.defaultFormulaTemperature)
        if triggerID == Smarter.triggerDefaultKeepWarmTime:          fire(triggerID,self.defaultKeepWarmTime)
        if triggerID == Smarter.triggerWaterSensorBase:              fire(triggerID,self.waterSensorBase)
        if triggerID == Smarter.triggerKeepWarm:                     fire(triggerID,self.keepWarmOn)
        if triggerID == Smarter.triggerHeaterKettle:                 fire(triggerID,self.heaterOn)
        if triggerID == Smarter.triggerFormulaCooling:               fire(triggerID,self.formulaCoolingOn)
        if triggerID == Smarter.triggerTemperature:                  fire(triggerID,self.temperature)
        if triggerID == Smarter.triggerWaterSensor:                  fire(triggerID,self.waterSensor)
        if triggerID == Smarter.triggerOnBase:                       fire(triggerID,self.onBase)
        if triggerID == Smarter.triggerUnknownKettle:                fire(triggerID,self.unknown)

        # Coffee
        if triggerID == Smarter.triggerMode:                         fire(triggerID,self.mode)
        if triggerID == Smarter.triggerDefaultStrength:              fire(triggerID,self.defaultStrength)
        if triggerID == Smarter.triggerDefaultCups:                  fire(triggerID,self.defaultCups)
        if triggerID == Smarter.triggerDefaultGrind:                 fire(triggerID,self.defaultGrind)
        if triggerID == Smarter.triggerDefaultHotplate:              fire(triggerID,self.defaultHotPlate)
        if triggerID == Smarter.triggerGrind:                        fire(triggerID,self.grind)
        if triggerID == Smarter.triggerReady:                        fire(triggerID,self.ready)
        if triggerID == Smarter.triggerWorking:                      fire(triggerID,self.working)
        if triggerID == Smarter.triggerTimerEvent:                   fire(triggerID,self.timerEvent)
        if triggerID == Smarter.triggerWaterLevel:                   fire(triggerID,self.waterLevel)
        if triggerID == Smarter.triggerWaterEnough:                  fire(triggerID,self.waterEnough)
        if triggerID == Smarter.triggerStrength:                     fire(triggerID,self.strength)
        if triggerID == Smarter.triggerCups:                         fire(triggerID,self.cups)
        if triggerID == Smarter.triggerCupsBrew:                     fire(triggerID,self.cupsBrew)
        if triggerID == Smarter.triggerUnknownCoffee:                fire(triggerID,self.unknown)
        if triggerID == Smarter.triggerCarafe:                       fire(triggerID,self.carafe)
        if triggerID == Smarter.triggerGrinder:                      fire(triggerID,self.grinderOn)
        if triggerID == Smarter.triggerHotPlate:                     fire(triggerID,self.hotPlateOn)
        if triggerID == Smarter.triggerHeaterCoffee:                 fire(triggerID,self.heaterOn)
        if triggerID == Smarter.triggerCarafeRequired:               fire(triggerID,self.carafeRequired)
        if triggerID == Smarter.triggerBusyCoffee:                   fire(triggerID,self.busy)
    
    
    def triggerSet(self,group,trigger,action):
        id = Smarter.triggerID(trigger.upper())
        if id in Smarter.triggersKettle:
            if len(self.triggersKettle[id]) != 0:
                for i in range(0,len(self.triggersKettle[id])):
                    if self.triggersKettle[id][i][0] == group:
                        del self.triggersKettle[id][i]
            self.triggersKettle[id] += [(group,action)]
            # it should be the trigger of the group only.. FU!
            self.__triggerHeartBeat(id)
    
        if id in Smarter.triggersCoffee:
            if len(self.triggersCoffee[id]) != 0:
                for i in range(0,len(self.triggersCoffee[id])):
                    if self.triggersCoffee[id][i][0] == group:
                        del self.triggersCoffee[id][i]

            self.triggersCoffee[id] += [(group,action)]
            # it should be the trigger of the group only.. FU!
            self.__triggerHeartBeat(id)
        self.__write_triggers()


    def isTriggersGroup(self,group):
        for i in self.triggersGroups:
            if i[0] == group:
                return True
        return False

    def getGroup(self,group):
        return self.triggersGroups[self.__findGroup(group)]

    def __findGroup(self,group):
        for i in range(0,len(self.triggersGroups)):
            if self.triggersGroups[i][0] == group:
                return i
        raise SmarterErrorOld("Trigger group not found")
        

    def enableGroup(self,group):
        if self.isTriggersGroup(group):
            print "Trigger group enabled " + group
            self.getGroup(group)[1] = True
            self.__write_triggers()
            return
        raise SmarterErrorOld("Trigger group not found")


    def disableGroup(self,group):
        if self.isTriggersGroup(group):
            print "Trigger group disabled " + group
            self.getGroup(group)[1] = False
            self.__write_triggers()
            return
        raise SmarterErrorOld("Trigger group not found")

     
    
    def boolsGroup(self,group,bools):
        if self.isTriggersGroup(group):
            print "Trigger group " + group + " setting state type " + "/".join(Smarter.triggerCheckBooleans(bools))
            self.getGroup(group)[2] = Smarter.triggerCheckBooleans(bools)
            self.__write_triggers()
            return
        raise SmarterErrorOld("Trigger group not found")
                

    
    def print_groups(self):
        print "Trigger Groups"
        print
        print "Name".rjust(18,' ') + "        Boolean State"
        print "".rjust(18,'_') + "_____________________"
        for i in self.triggersGroups:
            s = ""
            if i[1]: s = "Active "
            else: s = "       "
            print i[0].rjust(18,' ') + " " + s + ":".join(i[2])
        print


    def print_group(self,group):
        print "Trigger Group"
        print
        print "Name".rjust(18,' ') + "        Boolean State"
        print "".rjust(18,'_') + "_____________________"
        for i in self.triggersGroups:
            if i[0] == group:
                s = ""
                if i[1]: s = "Active "
                else: s = "       "
                print i[0].rjust(18,' ') + " " + s + ":".join(i[2])
                print
                return
        raise SmarterErrorOld("Trigger action group not found")


    def print_triggers(self):
        print
        
        for j in self.triggersGroups:
            print "Triggers " + j[0]
            print "_".rjust(25, "_")
            for i in Smarter.triggersKettle:
                s = self.triggerGet(j[0],Smarter.triggersKettle[i][0].upper())
                if s != "":
                    print Smarter.triggersKettle[i][0].rjust(25,' ') + " " + s
            for i in Smarter.triggersCoffee:
                s = self.triggerGet(j[0],Smarter.triggersCoffee[i][0].upper())
                if s != "":
                    print Smarter.triggersCoffee[i][0].rjust(25,' ') + " " + s
            print
            print
        
    @_threadsafe_function
    def __trigger(self,triggerID,old,new):
        if not self.events: return
        logging.debug("JB: running trigger handler") 
        #if self.dump and self.dump_status:
        #    if self.isKettle:
        #        logging.debug("Trigger: " + Smarter.triggersKettle[trigger][0] + " - old:" + str(old) + " new:" + str(new))
                
        #    if self.isCoffee:
        #        logging.debug("Trigger: " + Smarter.triggersCoffee[trigger][0] + " - old:" + str(old) + " new:" + str(new))

        for i in self.triggerGroups:
            if i[1]:
                s = self.triggerGet(i[0],Smarter.triggerName(triggerID))
                if s != "":
                    s = s.replace("§O",str(old)).replace("§N",str(new))
                    
                    # replace False, True with boolean.. FIX
                    
                    if s[0:4] == "http":
                        try:
                            response = urllib.urlopen(s)
            
                        except Exception, e:
                            print str(e)
                    else:
                        r = os.popen(s).read()
                        if self.dump:
                            print r
                
                    if self.dump and self.dump_status:
                        logging.debug("Trigger: " + Smarter.triggersKettle[triggerID][0] + " - old:" + str(old) + " new:" + str(new) + " " + i[0] + " " + s)



    #------------------------------------------------------
    # MESSAGE RESPONSE DECODERS
    #------------------------------------------------------


    def __decode(self,message):
        """
        Decode incoming response message
        """
        
        id = Smarter.raw_to_number(message[0])
        
        # Switch if needed to the right type of appliance
        if Smarter.message_kettle(id) and not Smarter.message_coffee(id):
            self.switch_kettle_device()
        elif Smarter.message_coffee(id) and not Smarter.message_kettle(id):
            self.switch_coffee_device()
        
        try:
            if   id == Smarter.ResponseKettleStatus:    self.__decode_KettleStatus(message)
            elif id == Smarter.ResponseCoffeeStatus:    self.__decode_CoffeeStatus(message)
            elif id == Smarter.ResponseCommandStatus:   self.__decode_CommandStatus(message)
            elif id == Smarter.ResponseBase:            self.__decode_Base(message)
            elif id == Smarter.ResponseTimers:          self.__decode_Timers(message)
            elif id == Smarter.ResponseCarafe:          self.__decode_Carafe(message)
            elif id == Smarter.ResponseMode:            self.__decode_Mode(message)
            elif id == Smarter.ResponseKettleHistory:   self.__decode_KettleHistory(message)
            elif id == Smarter.ResponseCoffeeHistory:   self.__decode_CoffeeHistory(message)
            elif id == Smarter.ResponseKettleSettings:  self.__decode_KettleSettings(message)
            elif id == Smarter.ResponseCoffeeSettings:  self.__decode_CoffeeSettings(message)
            elif id == Smarter.ResponseDeviceInfo:      self.__decode_DeviceInfo(message)
            elif id == Smarter.ResponseRelayInfo:       self.__decode_RelayInfo(message)
            elif id == Smarter.ResponseRelayModifiersInfo:  self.__decode_RelayModifiersInfo(message)
            elif id == Smarter.ResponseWifiFirmware:    self.__decode_WifiFirmware(message)
            elif id == Smarter.ResponseWirelessNetworks:self.__decode_WirelessNetworks(message)
        
        except SmarterError, e:
            # FIX ERROR HANDLING
            logging.debug(str(e))
            logging.debug(traceback.format_exc())
            raise SmarterError(0,"Could not decode message")

        if self.dump:
            if self.dump_status:
                self.print_message_read(message)
            else:
                #FIX (but what?)
                if id != Smarter.ResponseCoffeeStatus and id != Smarter.ResponseKettleStatus:
                    self.print_message_read(message)
                    
                    

    def __decode_KettleSettings(self,message):
        v = Smarter.raw_to_number(message[2])
        if v != self.defaultKeepWarmTime:
            self.__trigger(Smarter.triggerDefaultKeepWarmTime,self.defaultKeepWarmTime,v)
            self.defaultKeepWarmTime = v
        
        v = Smarter.raw_to_temperature(message[1])
        if v != self.defaultTemperature:
            self.__trigger(Smarter.triggerDefaultTemperature,self.defaultTemperature,v)
            self.defaultTemperature = v
        
        v = Smarter.raw_to_number(message[3])
        if v != self.defaultFormulaTemperature:
            self.__trigger(Smarter.triggerDefaultFormulaTemperature,self.defaultFormulaTemperature,v)
            self.defaultFormulaTemperature = v



    def __decode_CoffeeSettings(self,message):
        v = Smarter.raw_to_cups(message[1])
        if v != self.defaultCups:
            self.__trigger(Smarter.triggerDefaultCups,self.defaultCups,v)
            self.defaultCups = v
        
        v = Smarter.raw_to_strength(message[2])
        if v != self.defaultStrength:
            self.__trigger(Smarter.triggerDefaultStrength,self.defaultStrength,v)
            self.defaultStrength = v
        
        v = Smarter.raw_to_bool(message[3])
        if v != self.defaultGrind:
            self.__trigger(Smarter.triggerDefaultGrind,self.defaultGrind,v)
            self.defaultGrind  = v
        
        v =  Smarter.raw_to_hotplate(message[4],self.version)
        if v != self.defaultHotPlate:
            self.__trigger(Smarter.triggerDefaultHotplate,self.defaultHotPlate,v)
            self.defaultHotPlate = v



    def __decode_KettleStatus(self,message):
        self.kettleStatus = Smarter.raw_to_number(message[1])
            
        if self.kettleStatus == Smarter.KettleHeating:
            if not self.heaterOn:
                self.__trigger(Smarter.triggerHeaterKettle,False,True)
                if self.emulate:
                    self.iKettle.emu_trigger_heating(True)
                heaterOn = True
            if self.keepWarmOn == True:
                self.keepWarmOn = False
                if self.emulate:
                    self.iKettle.emu_trigger_warm(False)
                self.__trigger(Smarter.triggerKeepWarm,True,False)
                self.countKeepWarm += 1
            if self.formulaCoolingOn == True:
                self.formulaCoolingOn = False
                self.__trigger(Smarter.triggerFormulaCooling,True,False)
                self.countFormulaCooling+= 1
            if not self.busy:
                self.__trigger(Smarter.triggerBusyKettle,False,True)
                self.busy = True

        elif self.kettleStatus == Smarter.KettleFormulaCooling:
            if not self.formulaCoolingOn:
                self.formulaCoolingOn = True
                self.__trigger(Smarter.triggerFormulaCooling,False,True)
            if self.heaterOn == True:
                self.__trigger(Smarter.triggerHeaterKettle,True,False)
                if self.emulate:
                    self.iKettle.emu_trigger_heating(False)
                self.heaterOn = False
                self.countHeater += 1
            if self.keepWarmOn == True:
                self.keepWarmOn = False
                if self.emulate:
                    self.iKettle.emu_trigger_warm(False)
                self.__trigger(Smarter.triggerKeepWarm,True,False)
                self.countKeepWarm += 1
            if not self.busy:
                self.__trigger(Smarter.triggerBusyKettle,False,True)
                self.busy = True
        
        elif self.kettleStatus == Smarter.KettleKeepWarm:
            if not self.keepWarmOn:
                self.keepWarmOn = True
                if self.emulate:
                    self.iKettle.emu_trigger_warm(True)
                self.__trigger(Smarter.triggerKeepWarm,False,True)
            if self.heaterOn == True:
                self.__trigger(Smarter.triggerHeaterKettle,True,False)
                self.heaterOn = False
                if self.emulate:
                    self.iKettle.emu_trigger_heating(False)
                self.countHeater += 1
            if self.formulaCoolingOn == True:
                self.formulaCoolingOn = False
                self.__trigger(Smarter.triggerFormulaCooling,True,False)
                self.countFormulaCooling+= 1
            if self.busy:
                self.__trigger(Smarter.triggerBusyKettle,True,False)
                self.busy = False
        else:
            if self.keepWarmOn == True:
                self.__trigger(Smarter.triggerKeepWarm,True,False)
                if self.emulate:
                    self.iKettle.emu_trigger_warm(False)
                self.keepWarmOn = False
                self.countKeepWarm += 1
            if self.heaterOn == True:
                self.heaterOn = False
                if self.emulate:
                    self.iKettle.emu_trigger_heating(False)
                self.__trigger(Smarter.triggerHeaterKettle,True,False)
                self.countHeater+= 1
            if self.formulaCoolingOn == True:
                self.formulaCoolingOn = False
                self.__trigger(Smarter.triggerFormulaCooling,True,False)
                self.countFormulaCooling+= 1
            if self.busy:
                self.__trigger(Smarter.triggerBusyKettle,True,False)
                self.busy = False

        v = Smarter.raw_to_temperature(message[2])
        if v != self.temperature:
        
            self.__trigger(Smarter.triggerTemperature,self.temperature,v)
            
            # patch!
            if self.heaterOn:
                if self.patchTemperatureLimit and self.patchTemperatureLimitValue > v:
                    self.kettle_stop()
                if self.patchChildProtection and self.patchChildProtectionValue > v:
                    self.kettle_stop()
            
            self.temperature = v
            
        v = Smarter.raw_to_watersensor(message[3],message[4])
        if v != self.waterSensor:
            self.__trigger(Smarter.triggerWaterSensor,self.waterSensor,v)
            self.waterSensor = v

        v = Smarter.is_on_base(message[2])
        if self.onBase != v:
            if self.onBase:
                self.countKettleRemoved += 1
            if self.emulate:
                    self.iKettle.emu_trigger_onbase(v)
            self.__trigger(Smarter.triggerOnBase,self.onBase,v)
            self.onBase = v
            
        v = Smarter.raw_to_number(message[5])
        if v != self.unknown:
            self.__trigger(Smarter.triggerUnknownKettle,self.unknown,v)
            self.unknown = v



    def __decode_CoffeeStatus(self,message):
        
        def is_set(x, n):
            return x & 2**n != 0
        
        coffeeStatus = Smarter.raw_to_number(message[1])

        v = is_set(coffeeStatus,2)
        if v != self.ready:
            self.__trigger(Smarter.triggerReady,self.ready,v)
            self.ready = v

        v = is_set(coffeeStatus,1)
        if v != self.grind :
            self.__trigger(Smarter.triggerGrind,self.grind ,v)
            self.grind  = v

        v = is_set(coffeeStatus,5)
        if v != self.working:
            self.__trigger(Smarter.triggerWorking,self.working,v)
            self.working = v

        v = is_set(coffeeStatus,7)
        if v != self.timerEvent:
            self.__trigger(Smarter.triggerTimerEvent,self.timerEvent,v)
            self.timerEvent = v

        v = Smarter.raw_to_waterlevel(message[2])
        if v != self.waterLevel:
            self.__trigger(Smarter.triggerWaterLevel,self.waterLevel,v)
            self.waterLevel = v

        v = Smarter.raw_to_waterlevel_bit(message[2])
        if v != self.waterEnough:
            self.__trigger(Smarter.triggerWaterEnough,self.waterEnough,v)
            self.waterEnough = v

        v = Smarter.raw_to_strength(message[4])
        if v != self.strength:
            self.__trigger(Smarter.triggerStrength,self.strength,v)
            self.strength = v

        v = Smarter.raw_to_cups(message[5])
        if v != self.cups:
            self.__trigger(Smarter.triggerCups,self.cups,v)
            self.cups = v

        v = Smarter.raw_to_cups_brew(message[5])
        if v != self.cupsBrew:
            self.__trigger(Smarter.triggerCupsBrew,self.cupsBrew,v)
            self.cupsBrew = v

        v = Smarter.raw_to_number(message[3])
        if v != self.unknown:
            self.__trigger(Smarter.triggerUnknownCoffee,self.unknown,v)
            self.unknown = v

        v = is_set(coffeeStatus,0)
        if self.carafe != v:
            if not self.carafe:
                 self.countCarafeRemoved += 1
            self.__trigger(Smarter.triggerCarafe,self.carafe,v)
            self.carafe = v

        v = is_set(coffeeStatus,4)
        if self.heaterOn != v:
            if not self.heaterOn:
                self.countHeater += 1
            else:
                # what happens when it fails?? or stopped
                self.countCupsBrew += self.cupsBrew
            self.__trigger(Smarter.triggerHeaterCoffee,self.heaterOn,v)

            if self.busy and not v:
                self.__trigger(Smarter.triggerBusyCoffee,True,False)
                self.busy = False

            if not self.busy and v:
                self.__trigger(Smarter.triggerBusyCoffee,False,True)
                self.busy = True
            
            self.heaterOn = v

        v = is_set(coffeeStatus,6)
        if self.hotPlateOn != v:
            if not self.hotPlateOn:
                self.countHotPlateOn += 1
            """
            else:
                # patch!
                if self.patchHotplate:
                    if self.extendedHotplateLeft == 0 and self.extendedHotplate != 0:
                        self.extendedHotplate = 0

                    if self.extendedHotplate == 0:
                        self.extendedHotplateLeft = self.patchHotplateMinutes
                    # assume old firmware
                    if self.extendedHotplateLeft > 35:
                        if self.extendedHotplateLeft > 40:
                            self.extendedHotplate = 35
                            self.extendedHotplateLeft -= 35
                        else:
                            self.extendedHotplate = 30
                            self.extendedHotplateLeft -= 30
                    else:
                        self.extendedHotplate = self.extendedHotplateLeft
                        self.extendedHotplateLeft = 0
                    
                    self.coffee_hotplate_on(self.extendedHotplate)
            """
            self.__trigger(Smarter.triggerHotPlate,self.hotPlateOn,v)
            self.hotPlateOn = v

        v = is_set(coffeeStatus,3)
        if self.grinderOn != v:
            if not self.grinderOn:
                self.countGrinderOn += 1
            self.__trigger(Smarter.triggerGrinder,self.grinderOn,v)

            if self.busy and not v:
                self.__trigger(Smarter.triggerBusyCoffee,True,False)
                self.busy = False

            if not self.busy and v:
                self.__trigger(Smarter.triggerBusyCoffee,False,True)
                self.busy = True
            
            self.grinderOn = v
            


    def __decode_DeviceInfo(self,message):
        
        self.isCoffee = False
        self.isKettle = False
        self.deviceId = Smarter.raw_to_number(message[1])
        self.version = Smarter.raw_to_number(message[2])

        if self.deviceId == Smarter.DeviceKettle:
            self.switch_kettle_device()
        if self.deviceId == Smarter.DeviceCoffee:
            self.switch_coffee_device()


    def __decode_RelayInfo(self,message):
        self.remoteRelay = True
        self.remoteRelayVersion = Smarter.raw_to_number(message[1])
        self.remoteRelayHost = Smarter.raw_to_text(message[1:])



    def __decode_RelayModifiersInfo(self,message):
        d, r, p = self.__splitrules(Smarter.raw_to_text(message[0:]).upper())
        did = Smarter.groupsListDecode(d)
        rid = Smarter.groupsListDecode(r)
        self.remoteRulesIn = []
        self.remoteRulesOut = []
        self.remoteRulesIn = Smarter.idsAdd(self.remoteRulesIn,did)
        self.remoteRulesOut = Smarter.idsAdd(self.remoteRulesOut,rid)



    def __decode_Base(self,message):
        v = Smarter.raw_to_watersensor(message[1],message[2])
        if v != self.waterSensorBase:
            # trigger
            self.__trigger(Smarter.triggerWaterSensorBase,self.waterSensorBase,v)
            self.waterSensorBase = v
        


    def __decode_Carafe(self,message):
        v = not Smarter.raw_to_bool(message[1])
        if v != self.carafeRequired:
            # trigger
            self.__trigger(Smarter.triggerCarafeRequired,self.carafeRequired,v)
            self.carafeRequired = v
  


    def __decode_Mode(self,message):
        v = Smarter.raw_to_bool(message[1])
        if v != self.mode:
            # trigger
            self.__trigger(Smarter.triggerMode,self.mode,v)
            self.mode = v



    def __decode_CommandStatus(self,message):
        self.commandStatus = Smarter.raw_to_number(message[1])



    def __decode_WifiFirmware(self,message):
        self.WifiFirmware = Smarter.raw_to_text(message[1:])



    def __decode_Timers(self,message):
        pass



    def __decode_WirelessNetworks(self,message):
        a = ""
        w = []
        db = False
        for i in range(1,len(message)-1):
            x = str(message[i])
            if x == ',':
               db = True
               d = ""
               continue
            elif x == '}':
               db = False
               w += [(a,int(d))]
               a = ""
               continue
            elif not db and x in string.printable:
                a += x
            elif db and x in string.printable:
                d += x
    
        # most powerfull wifi on top
        self.Wifi = sorted(w,key=itemgetter(1),reverse=True)



    def __decode_CoffeeHistory(self,message):
        counter = Smarter.raw_to_number(message[1])
        if counter > 0:
            for i in range(0,counter):
                self.historySuccess = Smarter.raw_to_bool(message[i*32+13])
        else:
            pass
  


    def __decode_KettleHistory(self,message):
        """
        Decode kettle history response message
        """
        counter = Smarter.raw_to_number(message[1])
        if counter > 0:
            for i in range(0,counter):
                # read 32 bytes payload
                # queue!!!!
                self.historyTemperature = Smarter.raw_to_temperature(message[i*32+1+2])
                self.historyKeepWarmTime = Smarter.raw_to_keepwarm(message[i*32+2+2])
                self.historyFormulaTemperature = Smarter.raw_to_temperature(message[i*32+3+2])
                self.historyHours   = Smarter.raw_to_temperature(message[i*32+6+2])
                self.historyMinutes = Smarter.raw_to_temperature(message[i*32+7+2])
                self.historyDay     = Smarter.raw_to_temperature(message[i*32+8+2])
                self.historyMonth   = Smarter.raw_to_temperature(message[i*32+9+2])
                self.historyYear    = Smarter.raw_to_temperature(message[i*32+10+2])+1980
                
    
                # CHECK THIS
                
                #print str(self.historyHours) + ":" + str(self.historyMinutes)
                #print str(self.historyDay) + "-" + str(self.historyMonth) + "-" + str(self.historyYear)
                self.historySuccess = Smarter.raw_to_bool(message[i*32+13])
        else:
            self.historyTemperature = 0
            self.historyFormulaTemperature = 0
            self.historySuccess = False
            self.historyKeepWarmTime = 0



    #------------------------------------------------------
    # COMMANDS: iKettle 2.0 & Smarter Coffee 
    #------------------------------------------------------



    def switch_kettle_device(self):
        if not self.isKettle:
            self.__write_stats()
            if self.version == 0 or self.isCoffee:
                self.version = 19
            self.isKettle = True
            self.isCoffee = False
            self.__write_stats()
            # self.__read_triggers()
            self.__read_block()
            self.deviceId = Smarter.DeviceKettle
            self.device = Smarter.device_to_string(Smarter.DeviceKettle)
    

    def switch_coffee_device(self):
        if not self.isCoffee:
            self.__write_stats()
            if self.version == 0 or self.isKettle:
                self.version = 22
            self.isKettle = False
            self.isCoffee = True
            self.__write_stats()
            # self.__read_triggers()
            self.__read_block()
            self.deviceId = Smarter.DeviceCoffee
            self.device = Smarter.device_to_string(Smarter.DeviceCoffee)



    def device_all_settings(self):
        """
        Retreive the default values
        """
        
        self.__sendLock.acquire()
        try:
            self.fast = False
            self.shout = False
            self.device_info()
            if self.isKettle:
                self.kettle_settings()
                self.kettle_calibrate_base()
            elif self.isCoffee:
                self.coffee_settings()
                self.hotPlate = self.defaultHotPlate
                self.coffee_mode()
                self.coffee_carafe_required()
            #self.wifi_firmware()
            self.relay_info()
            self.__triggerHeartBeats()
        except SmarterError, e:
            raise e
        finally:
            self.__sendLock.release()



    def device_raw(self,code):
        """
        Send raw codes to device
        
        code is string with hex numbers it can include spaces seperating the hex
        """
        dump = self.dump
        self.dump = True
        self.__send(Smarter.codes_to_message(code))
        self.dump = dump
 
 

    def relay_info(self):
        """
        Retrieve remote relay info
        """
        self.__send_command(Smarter.CommandRelayInfo)
    
    

    def relay_modifiers_info(self):
        """
        Retrieve remote relay message block info
        """
        self.__send_command(Smarter.CommandRelayModifiersInfo)
    


    def relay_block(self,block):
        """
        Set remote relay message block
        """
        self.__send_command(Smarter.CommandRelayBlock,block)
    


    def relay_unblock(self,unblock):
        """
        Set remote relay message unblock
        """
        self.__send_command(Smarter.CommandRelayUnblock,unblock)
    


    def relay_patch(self,patch):
        """
        Set remote relay message block
        """
        self.__send_command(Smarter.CommandRelayPatch,patch)
    


    def device_info(self):
        """
        Retrieve device info
        """
        self.__send_command(Smarter.CommandDeviceInfo)



    def __device_check(self):
        if not self.isKettle and not self.isCoffee:
            self.fast = False
            self.device_info()



    def device_store_settings(self,v1,v2,v3,v4):
        """
        Store the 'default' user settings of the device
        
        Wrapper all input are string and are converted to the right types

        """
        self.__device_check()
        if self.isKettle:
            try:
                b = Smarter.string_to_mode(v3)
            except SmarterErrorOld, e:
                b = Smarter.string_to_bool(v3)
            self.kettle_store_settings(Smarter.string_to_temperature(v1),Smarter.string_to_keepwarm(v2),b,Smarter.string_to_temperature(v4))
        elif self.isCoffee:
            try:
                b = Smarter.string_to_grind(v3)
            except SmarterErrorOld, e:
                b = Smarter.string_to_bool(v3)
            self.coffee_store_settings(Smarter.string_to_cups(v1),Smarter.string_to_hotplate(v2),b,Smarter.string_to_strength(v4))



    def device_settings(self):
        """
        Get the 'default' user settings of the device
        """
        self.__device_check()
        if self.isKettle:   self.kettle_settings()
        elif self.isCoffee: self.coffee_settings()



    def device_history(self):
        """
        Gets history off the device
        """
        
        self.__device_check()
        if   self.isKettle: self.kettle_history()
        elif self.isCoffee: self.coffee_history()
    


    def device_stop(self):
        """
        Stop device
        """
        self.__device_check()
        if self.isKettle:   self.kettle_stop()
        elif self.isCoffee: self.coffee_stop()



    def device_start(self):
        """
        Start device with current selected settings
        """
        self.__device_check()
        if self.isKettle:   self.kettle_heat_settings()
        elif self.isCoffee: self.coffee_brew_settings()



    def device_default(self):
        """
        Store the system default settings in the default settings
        """
        self.__device_check()
        if self.isKettle:   self.kettle_store_settings()
        elif self.isCoffee: self.coffee_store_settings()



    def device_reset(self):
        """
        Resets device
        
        On coffee machine the default value's are not erased.
        """
        self.__send_command(Smarter.CommandResetSettings)
        defaultFormulaTemperature = 0
        defaultFormula = 0
        defaultKeepWarmTime = 0
        defaultTemperature = 100
   
 
 
    def device_update(self):
        """
        Enters update mode (do not use)
        """
        self.__send_command(Smarter.CommandUpdate)



    def device_time_now(self):
        """
        Set the time of the device to now
        """
        d = datetime.datetime.now()
        sefl.device_time(self,d.second,d.minute,d.hour,0,d.day,d.month,d.year / 1000,d.year % 1000)



    def device_time(self,second = 0,minute = 0,hour = 12,unknown = 0,day = 17, month=1, century = 20,year = 16):
        """
        Set the time of the device
        """
        self.__send_command(Smarter.CommandDeviceTime,Smarter.number_to_raw(second) + Smarter.number_to_raw(minute) + Smarter.number_to_raw(hour) + Smarter.number_to_raw(unknown) + Smarter.number_to_raw(day) + Smarter.number_to_raw(month) + Smarter.number_to_raw(century) + Smarter.number_to_raw(year))





    #------------------------------------------------------
    # COMMANDS: Wifi
    #------------------------------------------------------


    def wifi_firmware(self):
        """
        Retrieve Wifi firmware of device
        """
        self.__send_command(Smarter.CommandWifiFirmware)



    def wifi_scan(self):
        """
        Scan for Wireless networks
        """
        self.__send_command(Smarter.CommandWifiScan)



    def wifi_direct(self):
        """
        Go to direct mode
        
        This opens up the device access point which you can join
        """
        if not self.isDirect:
            self.__send_command(Smarter.CommandWifiLeave)

        else:
            logging.warning("[" + self.host + "] You are already in direct mode")



    def wifi_rejoin(self):
        """
        Rejoins wireless network
        
        Usefull to get new ip from dhcp server
        """
        if not self.isDirect:
            self.__send_command(Smarter.CommandWifiJoin)
        else:
            logging.warning("[" + self.host + "] Nothing to rejoin, you are in direct mode")



    def wifi_join(self,network,password=""):
        """
        Joins wireless network
        """
        self.fast = False
        self.__sendLock.acquire()
        self.__send_command(Smarter.CommandWifiNetwork,Smarter.text_to_raw(network))
        self.__send_command(Smarter.CommandWifiPassword,Smarter.text_to_raw(password))
        self.__send_command(Smarter.CommandWifiJoin)
        self.__sendLock.release()




    #------------------------------------------------------
    # COMMANDS: iKettle 2.0
    #------------------------------------------------------


 
    def kettle_store_settings(self, temperature = 100, timer = 0, formulaOn = False, formulaTemperature = 75):
        """
        Store default user settings
        """
        if self.fast or self.isKettle:
            self.__send_command(Smarter.CommandKettleStoreSettings, Smarter.keepwarm_to_raw(timer) + Smarter.temperature_to_raw(temperature) + Smarter.bool_to_raw(formulaOn) + Smarter.temperature_to_raw(formulaTemperature))
            if self.commandStatus == Smarter.StatusSucces:
                self.defaultKeepWarmTime        = timer
                self.defaultFormula             = formulaOn
                self.defaultFormulaTemperature  = formulaTemperature
                self.defaultTemperature         = temperature
            else:
               raise SmarterError(KettleFailedStoreSettings,"Could not store kettle machine settings")
        else:
            raise SmarterError(KettleNoMachineStoreSettings,"You need a Kettle machine to store settings")



    def kettle_settings(self):
        """
        Retrieve kettle 'default' user settings
        """
        if self.fast or self.isKettle:
            self.__send_command(Smarter.CommandKettleSettings)
        else:
            raise SmarterError(KettleNoMachineSettings,"You need a Kettle machine to get its settings")



    def kettle_heat(self,temperature=100,keepwarm=-1):
    
        """
        Heat water
        
        Keepwarm can be 0 or the keepwarm time or -1 'meaning use 'default' user setting
        """
        if keepwarm == -1:  kw = self.defaultKeepWarmTime
        else:               kw = keepwarm
        
        # patch!
        if self.patchTemperatureLimit and self.patchTemperatureLimitValue <= temperature:
            t = self.patchTemperatureLimitValue
        elif self.patchChildProtection and self.patchChildProtectionValue <= temperature:
            t = self.patchChildProtectionValue
        else:
            t = temperature

        if self.fast or self.isKettle:
            #if self.virtual:
            #    self.iKettle.heat_temp(t)
            if self.emulate:
                self.iKettle.emu_trigger_temperature(t)
            self.__send_command(Smarter.CommandHeat,Smarter.temperature_to_raw(t)+Smarter.keepwarm_to_raw(kw))
        else:
            raise SmarterError(KettleNoMachineHeat,"You need a kettle to heat it")


    def kettle_heat_milk(self):
        """
        Heat water to temperature right for warming milk
        """
        self.kettle_heat(65)



    def kettle_heat_black_tea(self):
        """
        Heat water to temperature right for black tea
        """
        self.kettle_heat(100)



    def kettle_heat_green_tea(self):
        """
        Heat water to temperature right for green tea
        """
        self.kettle_heat(65)



    def kettle_heat_white_tea(self):
        """
        Heat water to temperature right for white tea
        """
        self.kettle_heat(80)



    def kettle_heat_oelong_tea(self):
        """
        Heat water to temperature right for oelong tea
        """
        self.kettle_heat(90)



    def kettle_heat_coffee(self):
        """
        Heat water to temperature right for coffee
        """
        self.kettle_heat(95)



    def kettle_boil(self):
        """
        Boil water
        """
        self.kettle_heat(100)


    
    def kettle_heat_default(self):
        """
        Heat water to 'default' user setting stored on the kettle temperature and keepwarm
        """
        self.kettle_heat(self.defaultTemperature,self.defaultKeepWarmTime)



    def kettle_heat_settings(self):
        """
        Heat water to 'default' user setting stored on the kettle temperature and keepwarm
        
        Unknown if this one works...
        """
        if self.fast or self.isKettle:
            if self.emulate:
                self.iKettle.emu_trigger_temperature(self.defaultTemperature)
            #if self.virtual:
            #    self.iKettle.heat_temp(self.defaultTemperature)
            self.__send_command(Smarter.CommandHeatDefault)
        else:
            raise SmarterError(KettleNoMachineHeat,"You need a kettle to heat it")



    def kettle_formula_heat(self, formulaTemperature = 75, keepwarm = 0):
        """
        Heat water and then cool down to formula mode
        
        keepwarm can be 0 or the keepwarm time [0..30] or -1 'meaning use 'default' user setting
        """
        if keepwarm == -1:  kw = self.defaultKeepWarmTime
        else:               kw = keepwarm

        # patch!
        if self.patchTemperatureLimit and self.patchTemperatureLimitValue <= formulaTemperature :
            t = self.patchTemperatureLimitValue
        elif self.patchChildProtection and self.patchChildProtectionValue <= formulaTemperature :
            t = self.patchChildProtectionValue
        else:
            t = formulaTemperature
        
        if self.fast or self.isKettle:
            if self.emulate:
                self.iKettle.emu_trigger_temperature(t)
            #if self.virtual:
            #    self.iKettle.heat_temp(t)
            self.__send_command(Smarter.CommandHeatFormula,Smarter.temperature_to_raw(t)+Smarter.keepwarm_to_raw(kw))
        else:
            raise SmarterError(KettleNoMachineHeatFormula,"You need a kettle to heat in formula mode")



    def kettle_stop(self):
        """ 
        Stop heating water
        """
        if self.fast or self.isKettle:
            if self.emulate:
                self.iKettle.emu_trigger_stop()
            #if self.virtual:
            #    self.iKettle.stop()
            self.__send_command(Smarter.CommandKettleStop)
        else:
            raise SmarterError(KettleNoMachineStop,"You need a kettle to stop heating")



    def kettle_history(self):
        """
        Retrieve kettle history
        """
        if self.fast or self.isKettle:
            self.__send_command(Smarter.CommandKettleHistory)
        else:
            raise SmarterError(KettleNoMachineHistory,"You need a kettle machine to get its history")



    #------------------------------------------------------
    # COMMANDS: Kettle Calibrate
    #------------------------------------------------------


    def kettle_calibrate(self):
        """
        Calibrate kettle
        
        Please use kettle_calibrate_offbase()
        """
        if self.fast or self.isKettle:
            self.__send_command(Smarter.CommandCalibrate)
        else:
            raise SmarterError(KettleNoMachineSettings,"You need a Kettle to calibrate")


    def kettle_calibrate_offbase(self):
        """
        Calibrate kettle with check on off base
        """
        if self.fast or self.isKettle:
            if self.onBase:
                self.__send_command(Smarter.CommandCalibrate)
            else:
                raise SmarterError(0,"Can not calibrate with the kettle off the base, please place it on the base")
        else:
            raise SmarterError(KettleNoMachineSettings,"You need a Kettle to calibrate")



    def kettle_calibrate_base(self):
        """
        Get calibration base value
        """
        if self.fast or self.isKettle:
            self.__send_command(Smarter.CommandBase)
        else:
            raise SmarterError(KettleNoMachineSettings,"You need a Kettle to get its calibration base value")



    def kettle_calibrate_store_base(self,base = 1000):
        """
        Store calibration base value
        
        Please use kettle_calibrate_offbase()
        """
        if self.fast or self.isKettle:
            self.__send_command(Smarter.CommandStoreBase,Smarter.watersensor_to_raw(base))
            self.waterSensorBase = base
        else:
            raise SmarterError(KettleNoMachineSettings,"You need a Kettle to set its calibration base value")



    #------------------------------------------------------
    # COMMANDS: Smarter Coffee 
    #------------------------------------------------------


    def coffee_settings(self):
        """
        Retrieve 'default' user settings
        """
        if self.fast or self.isCoffee:
            self.__send_command(Smarter.CommandCoffeeSettings)
        else:
            raise SmarterError(CoffeeNoMachineSettings,"You need a coffee machine to get its settings")



    def coffee_history(self):
        """
        Retreive history of actions
        """
        if self.fast or self.isCoffee:
            self.__send_command(Smarter.CommandCoffeeHistory)
        else:
            raise SmarterError(CoffeeNoMachineHistory,"You need a coffee machine to get its history")



    def coffee_stop(self):
        """
        Stop brewing
        """
        if self.fast or self.isCoffee:
            self.__send_command(Smarter.CommandCoffeeStop)
        else:
            raise SmarterError(CoffeeNoMachineStop,"You need a coffee machine to stop brewing coffee")



    def coffee_mode(self):
        """
        Retreive cup or carafe mode selected
        """
        if self.fast or self.isCoffee:
            self.__send_command(Smarter.CommandMode)
        else:
            raise SmarterError(CoffeeNoMachineCup,"You need a coffee machine to get its mode")



    @_threadsafe_function
    def coffee_mode_toggle(self):
        """
        Toggle cup/carafe mode
        """
        if self.fast or self.isCoffee:
            self.__send_command(Smarter.CommandSetMode,not self.mode)
            self.mode = not self.mode
        else:
            raise SmarterError(CoffeeNoMachineCup,"You need a coffee machine to toggle its mode")



    @_threadsafe_function
    def coffee_cup_mode(self):
        """
        Select cup mode
        """
        if self.fast or self.isCoffee:
            self.__send_command(Smarter.CommandSetMode,Smarter.bool_to_raw(True))
            self.mode = True
        else:
            raise SmarterError(CoffeeNoMachineCup,"You need a coffee machine to set cup mode")


    @_threadsafe_function
    def coffee_carafe_mode(self):
        """
        Select carafe mode
        """
        if self.fast or self.isCoffee:
            self.__send_command(Smarter.CommandSetMode,Smarter.bool_to_raw(False))
            self.mode = False
        else:
            raise SmarterError(CoffeeNoMachineCup,"You need a coffee machine to set carafe mode")



    def coffee_carafe_required(self):
        """
        Retreive carafe required
        """
        if self.fast or self.isCoffee:
            self.__send_command(Smarter.CommandCarafe)
        else:
            raise SmarterError(CoffeeNoMachineCarafe,"You need a coffee machine to get its carafe required status")



    @_threadsafe_function
    def coffee_carafe_required_toggle(self):
        """
        Carafe required toggle
        """
        if self.fast or self.isCoffee:
            self.__send_command(Smarter.CommandSetCarafe,self.carafeRequired)
            self.carafeRequired = not self.carafeRequired
        else:
            raise SmarterError(CoffeeNoMachineCarafe,"You need a coffee machine to set carafe required on")



    @_threadsafe_function
    def coffee_carafe_required_on(self):
        """
        Carafe required on
        """
        if self.fast or self.isCoffee:
            self.__send_command(Smarter.CommandSetCarafe,Smarter.bool_to_raw(False))
            self.carafeRequired = True
        else:
            raise SmarterError(CoffeeNoMachineCarafe,"You need a coffee machine to set carafe required on")



    @_threadsafe_function
    def coffee_carafe_required_off(self):
        """
        Carafe required off
        """
        if self.fast or self.isCoffee:
            self.__send_command(Smarter.CommandSetCarafe,Smarter.bool_to_raw(True))
            self.carafeRequired = False
        else:
            raise SmarterError(CoffeeNoMachineCarafe,"You need a coffee machine to set carafe required off")



    @_threadsafe_function
    def coffee_store_settings(self, cups = 1, hotplate = 0, grind = True, strength = 1):
        """
        Store 'default' user settings on the coffee machine
        """
        if self.fast or self.isCoffee:
            self.__send_command(Smarter.CommandCoffeeStoreSettings,Smarter.strength_to_raw(strength)+Smarter.cups_to_raw(cups)+Smarter.bool_to_raw(grind)+Smarter.hotplate_to_raw(hotplate,self.version))

            if self.commandStatus == Smarter.StatusSucces:
                self.defaultCups = cups
                self.defaultStrength = strength
                self.defaultGrind = grind
                self.defaultHotPlate = hotplate
            else:
                raise SmarterError(CoffeeFailedStoreSettings,"Could not store coffee machine settings")

        else:
            raise SmarterError(CoffeeNoMachineStoreSettings,"You need a coffee machine to store settings")
    


    def coffee_brew_default(self):
        """
        Brew coffee with 'default' user settings from the coffee machine
        """
        self.coffee_brew(self.defaultCups,self.defaultStrength,self.defaultHotPlate,self.defaultGrind)



    def coffee_brew_settings(self):
        """
        Brew coffee with settings on the machine
        """
        #  cups strength hotplate grind
        if self.fast or self.isCoffee:
            self.__send_command(Smarter.CommandBrewDefault)
        else:
            raise SmarterError(CoffeeNoMachineBrew,"You need a coffee machine to brew coffee")



    def coffee_brew(self, cups = 1, hotplate = 0, grind = True, strength = 1):
        """
        Brew coffee with settings
        """
        #  cups strength hotplate grind
        if self.fast or self.isCoffee:
            self.__send_command(Smarter.CommandBrew,Smarter.cups_to_raw(cups)+Smarter.strength_to_raw(strength)+Smarter.hotplate_to_raw(hotplate,self.version)+Smarter.bool_to_raw(grind))
        else:
            raise SmarterError(CoffeeNoMachineBrew,"You need a coffee machine to brew coffee")



    def coffee_descale(self):
        """
        Descale coffee machine
        """
        if self.fast or self.isCoffee:
            if self.waterLevel == Smarter.CoffeeWaterFull:
                try:
                    self.coffee_brew(12,0,False,Smarter.CoffeeWeak)
                except:
                    raise SmarterError(CoffeeNoMachineBrew,"Descaling failed")
            raise SmarterError(CoffeeNoMachineBrew,"Not enough water, please fill to full")
        raise SmarterError(CoffeeNoMachineBrew,"You need a coffee machine to descale it")
    
    
    @_threadsafe_function
    def coffee_hotplate_off(self):
        """
        Turns the hotplate off
        """
        if self.fast or self.isCoffee:
            self.__send_command(Smarter.CommandHotplateOff)
            self.hotPlate = self.defaultHotPlate
        else:
            raise SmarterError(CoffeeNoMachineHotplateOff,"You need a coffee machine to turn off the hotplate")



    @_threadsafe_function
    def coffee_hotplate_on(self, hotplate=-1):
        """
        Turns the hotplate on
        """
        
        if hotplate == -1:  minutes = self.defaultHotPlate
        else:               minutes = hotplate
       
        if self.fast or self.isCoffee:
            if minutes == 0:
                self.__send_command(Smarter.CommandHotplateOff)
                self.hotPlate = self.defaultHotPlate
            else:
                self.__send_command(Smarter.CommandHotplateOn,Smarter.hotplate_to_raw(minutes,self.version))
                self.hotPlate = minutes
        else:
            raise SmarterError(CoffeeNoMachineHotplateOn,"You need a coffee machine to turn on the hotplate")



    def coffee_timers(self,index=0):
        """
        Get timers
        
        FIX
        """
        if self.isCoffee and self.grind:
            self.__send_command(Smarter.CommandTimers)
        else:
            raise SmarterError(CoffeeNoMachineGrinder,"You need a coffee machine to use timers")



    def coffee_timer_disable(self,index=0):
        """
        Disable timer or set that we processed the timer
        
        FIX
        """
        if self.isCoffee and self.grind:
            pass #self.__send_command(Smarter.CommandDisableTimer)
        else:
            raise SmarterError(CoffeeNoMachineGrinder,"You need a coffee machine to use timers")



    def coffee_timer_store(self,index=0,time=None):
        """
        Store a timer
        
        FIX
        """
        if self.isCoffee and self.grind:
            pass #self.__send_command(Smarter.CommandStoreTimer)
        else:
            raise SmarterError(CoffeeNoMachineGrinder,"You need a coffee machine to use timers")



    @_threadsafe_function
    def coffee_cups(self,cups=1):
        """
        Set the number of cups to brew
        """
        if self.fast or self.isCoffee:
            self.__send_command(Smarter.CommandCups,Smarter.cups_to_raw(cups))
            self.cups = cups
        else:
            raise SmarterError(CoffeeNoMachineCups,"You need a coffee machine to select the number of cups to brew")



    @_threadsafe_function
    def coffee_grinder_toggle(self):
        """
        Toggle grinder on/off

        Please use: coffee_pregrind() coffee_weak() coffee_medium() or coffee_strong for coffee type selection
        """
        if self.fast or self.isCoffee:
            self.__send_command(Smarter.CommandGrinder)
            self.grind = not self.grind
        else:
            raise SmarterError(CoffeeNoMachineGrinder,"You need a coffee machine to toggle the grinder")



    def coffee_grinder_off(self):
        """
        Select filter for coffee
        
        Same as coffee_pregrind(), coffee_filter()
        Only here because on the display it says beans/filter
        Please use: coffee_pregrind() coffee_weak() coffee_medium() or coffee_strong for coffee type selection
        """
        self.coffee_filter()



    def coffee_grinder_on(self):
        """
        Select beans for coffee
        
        Same as coffee_beans()
        
        Only here because on the display it says beans/filter
        Please use: coffee_pregrind() coffee_weak() coffee_medium() or coffee_strong for coffee type selection
        """
        self.coffee_beans()



    @_threadsafe_function
    def coffee_beans(self):
        """
        Select beans for coffee
        
        Same as coffee_grinder_on()
        
        Only here because on the display it says beans/filter
        Please use: coffee_pregrind() coffee_weak() coffee_medium() or coffee_strong for coffee type selection
        """
        if self.isCoffee:
            if not self.grind:
                self.__send_command(Smarter.CommandGrinder)
                self.grind = True
        else:
            raise SmarterError(CoffeeNoMachineGrinder,"You need a coffee machine to use the grinder to grind the beans")



    @_threadsafe_function
    def coffee_filter(self):
        """
        Select pregrind beans for coffee
        
        Same as coffee_pregrind(), coffee_grinder_off()
        Only here because on the display it says beans/filter
        Please use: coffee_pregrind() coffee_weak() coffee_medium() or coffee_strong for coffee type selection
        """
        if self.isCoffee:
            if self.grind:
                self.__send_command(Smarter.CommandGrinder)
                self.grind = False
        else:
            raise SmarterError(CoffeeNoMachineGrinder,"You need a coffee machine to use the pre grind beans in the filter")



    @_threadsafe_function
    def coffee_strength(self,strength=Smarter.CoffeeMedium):
        """
        Set the coffee strength
        """
        if self.fast or self.isCoffee:
            self.__send_command(Smarter.CommandStrength ,Smarter.strength_to_raw(strength))
            self.strength = strength
        else:
            raise SmarterError(CoffeeNoMachineStrength,"You need a coffee machine to select the coffee strength")



    def coffee_pregrind(self):
        """
        Select pregrind beans for coffee

        Same as coffee_filter(), coffee_grinder_off()
        Please use: coffee_pregrind() coffee_weak() coffee_medium() or coffee_strong for coffee type selection
        """
        self.coffee_filter()



    def coffee_weak(self):
        """
        Set the coffee strength to weak
        
        This also changes using beans instead of the filter
        Or using the grinder instead of pregrind
        """
        try:
            self.coffee_beans()
            self.coffee_strength(Smarter.CoffeeWeak)
        except:
            raise SmarterError(0,"Could not set to weak")
            

    def coffee_medium(self):
        """
        Set the coffee strength to weak
        
        This also changes using beans instead of the filter
        Or using the grinder instead of pregrind
        """
        self.coffee_beans()
        self.coffee_strength(Smarter.CoffeeMedium)



    def coffee_strong(self):
        """
        Set the coffee strength to strong
        
        This also changes using beans instead of the filter
        Or using the grinder instead of pregrind
        """
        self.coffee_beans()
        self.coffee_strength(Smarter.CoffeeStrong)



    #------------------------------------------------------
    # STRING/PRINT SMARTER INFO
    #------------------------------------------------------


    def print_info_device(self):
        print Smarter.device_info(self.deviceId,self.version)


    def print_info_relay(self):
        if self.remoteRelay:
            print "Remote relay version " + str(self.remoteRelayVersion) + " (" + self.remoteRelayHost + ")"
        else:
            print "No remote relay"


    def print_mode(self):
        if self.mode:
            print "Cup mode"
        else:
            print "Carafe mode"


    def print_carafe_required(self):
        if self.carafeRequired:
            print "Can brew without carafe"
        else:
            print "Carafe needed for brewing"


    def print_watersensor_base(self):
        print "Watersensor calibration base value: " + str(self.waterSensorBase)


    def print_wireless_networks(self):
        print
        print "         Signal   Wireless Network"
        for i in range(0,len(self.Wifi)):
            
            quality = Smarter.dbm_to_quality(self.Wifi[i][1])
            
            s = ""
            for x in range(quality / 10,10):
                s += " "
            for x in range(0,quality / 10):
                s += "█"

            print "     " + s + "   " + self.Wifi[i][0]
        print


    def print_wifi_firmware(self):
        print
        print self.WifiFirmware
        print
    
    
    def print_settings(self):
        if self.isKettle:
            self.print_kettle_settings()
        elif self.isCoffee:
            self.print_coffee_settings()
            
            
    def print_coffee_settings(self):
        print Smarter.string_coffee_settings(self.defaultCups, self.defaultStrength, self.defaultGrind, self.defaultHotPlate)


    def print_kettle_settings(self):
        print Smarter.string_kettle_settings(self.defaultTemperature, self.defaultFormula, self.defaultFormulaTemperature, self.defaultKeepWarmTime)


    def print_timers(self):
        # fix this
        print "Not yet implemented"


    def print_coffee_history(self):
        # fix this THIS IS SO WRONG
        if not self.historySuccess:
            print "No history available"
            return
        print "Not yet implemented"


    def print_history(self):
        if self.isKettle:
            self.print_kettle_history()
        elif self.isCoffee:
            self.print_coffee_history()


    def print_kettle_history(self):
        # fix this
        if not self.historySuccess:
            print "No history available"
            return
        print "Not yet implemented"



    def print_short_kettle_status(self):
        if self.busy: s = "busy "
        else: s = ""
        print s + Smarter.string_kettle_status(self.onBase,self.kettleStatus,self.temperature,self.waterSensor)


    def print_short_status(self):
        self.__read()
        if self.isKettle:
            self.print_short_kettle_status()
        elif self.isCoffee:
            self.print_short_coffee_status()


    def print_kettle_status(self):
        if self.busy: s = "busy "
        else: s = ""
        if self.onBase:
            print "Status           " + s + Smarter.status_kettle_description(self.kettleStatus)
            print "Temperature      " + Smarter.temperature_to_string(self.temperature)
            print "Water sensor     " + str(self.waterSensor) + " (calibration base " + str(self.waterSensorBase) + ")"
        else:
            print "Status           " + s + "off base"
        print "Default heating  " + Smarter.string_kettle_settings(self.defaultTemperature,self.defaultFormula, self.defaultFormulaTemperature,self.defaultKeepWarmTime)



    def print_short_coffee_status(self):
        if self.busy: s = "busy "
        else: s = ""
        print s + Smarter.string_coffee_status(self.ready, self.cupsBrew, self.working, self.heaterOn, self.hotPlateOn, self.carafe, self.grinderOn) + ", water " + Smarter.waterlevel(self.waterLevel) + ", setting: " + Smarter.string_coffee_settings(self.cups, self.strength, self.grind, self.hotPlate) + Smarter.string_coffee_bits(self.carafeRequired,self.mode,self.waterEnough,self.timerEvent)



    def print_coffee_status(self):
        if self.busy: s = "busy "
        else: s = ""
        print "Status           " + s + Smarter.string_coffee_status(self.ready, self.cupsBrew, self.working, self.heaterOn, self.hotPlateOn, self.carafe, self.grinderOn) + Smarter.string_coffee_bits(self.carafeRequired,self.mode,self.waterEnough,self.timerEvent)
        print "Water level      " + Smarter.waterlevel(self.waterLevel)
        print "Setting          " + Smarter.string_coffee_settings(self.cups, self.strength, self.grind, self.hotPlate)
        print "Default brewing  " + Smarter.string_coffee_settings(self.defaultCups, self.defaultStrength, self.defaultGrind, self.defaultHotPlate)



    def print_status(self):
        print
        if self.isKettle:
            self.print_kettle_status()
        elif self.isCoffee:
            self.print_coffee_status()
        print



    def string_connect_status(self):
        if self.connected:
            s = ""
            if self.isDirect:
                s = " directly"
            return "Connected" + s + " to [" + self.host + "] " + Smarter.device_info(self.deviceId,self.version)
        return "Not connected"



    def print_connect_status(self):
        print self.string_connect_status()
    

    def print_stats(self):
        print
        print "  Stats "+ self.host
        print "  ______"+ "_"*len(self.host)
        print
        print
        print "  " + str(self.totalSendCount).rjust(9, ' ')   + "  Commands ("  + Smarter.bytes_to_human(self.totalSendBytesCount) + ")"
        print "  " + str(self.totalReadCount).rjust(9, ' ')   + "  Responses (" + Smarter.bytes_to_human(self.totalReadBytesCount) + ")"
        if self.totalSessionCount != 0:
            print "  " + str(self.totalSessionCount).rjust(9, ' ') + "  " + "Sessions"
        print
        print
        if self.isCoffee:
            print "  " + str(self.totalCountCarafeRemoved).rjust(9, ' ') + "  Carafe removed"
            print "  " + str(self.totalCountCupsBrew).rjust(9, ' ') + "  Cups brew"
            print "  " + str(self.totalCountHeater).rjust(9, ' ') + "  Heater on"
            print "  " + str(self.totalCountHotPlateOn).rjust(9, ' ') + "  Hotplate on"
            print "  " + str(self.totalCountGrinderOn).rjust(9, ' ') + "  Grinder on"
        elif self.isKettle:
            print "  " + str(self.totalCountKettleRemoved).rjust(9, ' ') + "  Kettle removed"
            print "  " + str(self.totalCountHeater).rjust(9, ' ') + "  Water Heated"
            print "  " + str(self.totalCountFormulaCooling).rjust(9, ' ') + "  Formula cooling"
            print "  " + str(self.totalCountKeepWarm).rjust(9, ' ') + "  Kept warm"
        print
        print
        if self.sendCount != 0 or self.readCount != 0:
            print "  Current session"
            print
        #    print "  " + str(self.sessionCount).rjust(10, ' ') + "  Connected"
            print "  " + str(self.sendCount).rjust(9, ' ')   + "  Commands ("  + Smarter.bytes_to_human(self.sendBytesCount) + ")"
            print "  " + str(self.readCount).rjust(9, ' ')   + "  Responses (" + Smarter.bytes_to_human(self.readBytesCount) + ")"
            print
            
            for id in sorted(self.commandCount):
                print "  " + str(self.commandCount[id]).rjust(9, ' ') + "  [" + Smarter.number_to_code(id) + "] " + Smarter.message_description(id)
            print
            
            for id in sorted(self.responseCount):
                print "  " + str(self.responseCount[id]).rjust(9, ' ') + "  [" + Smarter.number_to_code(id) + "] "  + Smarter.message_description(id)
            print
            if self.isCoffee:
                print "  " + str(self.countCarafeRemoved).rjust(9, ' ') + "  Carafe removed"
                print "  " + str(self.countCupsBrew).rjust(9, ' ') + "  Cups brew"
                print "  " + str(self.countHeater).rjust(9, ' ') + "  Heater on"
                print "  " + str(self.countHotPlateOn).rjust(9, ' ') + "  Hotplate on"
                print "  " + str(self.countGrinderOn).rjust(9, ' ') + "  Grinder on"
            elif self.isKettle:
                print "  " + str(self.countKettleRemoved).rjust(9, ' ') + "  Kettle removed"
                print "  " + str(self.countHeater).rjust(9, ' ') + "  Water Heated"
                print "  " + str(self.countFormulaCooling).rjust(9, ' ') + "  Formula cooling"
                print "  " + str(self.countKeepWarm).rjust(9, ' ') + "  Kept warm"
            print



    def print_message_send(self,message):
        print "[" + self.host +  ":" + '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()) + "] Message Send     [" + Smarter.message_description(Smarter.raw_to_number(message[0])) + "] [" + Smarter.message_to_codes(message) + "]"



    def print_message_read(self,message):
        id = Smarter.raw_to_number(message[0])
        print "[" + self.host +  ":" + '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()) + "] Message Received [" + Smarter.message_description(id) + "] [" + Smarter.message_to_codes(message) + "]"
        if   id == Smarter.ResponseCommandStatus:   print "Command replied: " + Smarter.status_command(self.commandStatus)
        elif id == Smarter.ResponseWirelessNetworks: self.print_wireless_networks()
        elif id == Smarter.ResponseWifiFirmware:    self.print_wifi_firmware()
        elif id == Smarter.ResponseKettleHistory:   self.print_kettle_history()
        elif id == Smarter.ResponseCoffeeHistory:   self.print_coffee_history()
        elif id == Smarter.ResponseKettleSettings:  self.print_kettle_settings()
        elif id == Smarter.ResponseCoffeeSettings:  self.print_coffee_settings()
        elif id == Smarter.ResponseCarafe:          self.print_carafe_required()
        elif id == Smarter.ResponseMode:            self.print_mode()
        elif id == Smarter.ResponseDeviceInfo:      self.print_info_device()
        elif id == Smarter.ResponseRelayInfo:       self.print_info_relay()
        elif id == Smarter.ResponseRelayModifiersInfo:  self.print_remote_rules_short()
        elif id == Smarter.ResponseBase:            self.print_watersensor_base()
        elif id == Smarter.ResponseKettleStatus:    self.print_short_kettle_status()
        elif id == Smarter.ResponseCoffeeStatus:    self.print_short_coffee_status()
        elif id == Smarter.ResponseTimers:          self.print_timers()
        else:                                       print "Unknown Reply Message"

