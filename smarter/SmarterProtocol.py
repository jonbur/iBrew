# -*- coding: utf-8 -*-

import traceback
import struct
import string
import socket
import datetime
import os
import sys

from operator import itemgetter

#------------------------------------------------------
# SMARTER PROTOCOL INTERFACE
#
# Python protocol interface to Smarter Appliances
#
# https://github.com/Tristan79/iBrew
#
# Copyright © 2017 Tristan (@monkeycat.nl). All Rights Reserved
#
# The Dream Tea
#------------------------------------------------------

# In the end I should have made classes of the types... split the simulator, firewall, etc,
# And yes, i know i really made a mess of it, it was a good learning experience.
# How divide and conquers wins, but it's HOW you divide! Should have build it differently, o well, next time!

class SmarterProtocolLegacy:

    #------------------------------------------------------
    # LEGACY
    #------------------------------------------------------


    def protocol(self):
        rj = 27
        print
        print "Commands".rjust(rj-1)
        print "".rjust(rj-1,"_")
        print ("[" + self.commandHandshake + "\\n] ").rjust(rj) + self.textGetHandshake
        print ("[" + self.commandStatus + "\\n] ").rjust(rj) + self.textGetStatus
        print ("[" + self.commandWarm5m + "\\n] ").rjust(rj) + self.textSelectWarm5m
        print ("[" + self.commandWarm10m + "\\n] ").rjust(rj) + self.textSelectWarm10m
        print ("[" + self.commandWarm20m + "\\n] ").rjust(rj) + self.textSelectWarm20m
        print ("[" + self.commandWarm + "\\n] ").rjust(rj) + self.textWarm
        print ("[" + self.command65c + "\\n] ").rjust(rj) + self.textSelect65c
        print ("[" + self.command80c + "\\n] ").rjust(rj) + self.textSelect80c
        print ("[" + self.command95c + "\\n] ").rjust(rj) + self.textSelect95c
        print ("[" + self.command100c + "\\n] ").rjust(rj) + self.textSelect100c
        print ("[" + self.commandHeat + "\\n] ").rjust(rj) + self.textHeat
        print ("[" + self.commandStop + "\\n] ").rjust(rj) + self.textStop
        print
        print
        print "Responses".rjust(rj-1)
        print "".rjust(rj-1,"_")
        print ("[" + self.responseHandshake + "\\r] ").rjust(rj) + self.textHandshake
        print ("[" + self.responseStatus + "\\r] ").rjust(rj) + self.textStatus
        print ("[" + self.status65c + "\\r] ").rjust(rj) + self.text65c
        print ("[" + self.status80c + "\\r] ").rjust(rj) + self.text80c
        print ("[" + self.status95c + "\\r] ").rjust(rj) + self.text95c
        print ("[" + self.status100c + "\\r] ").rjust(rj) + self.text100c
        print ("[" + self.statusWarm5m + "\\r] ").rjust(rj) + self.textWarm5m
        print ("[" + self.statusWarm10m + "\\r] ").rjust(rj) + self.textWarm10m
        print ("[" + self.statusWarm20m + "\\r] ").rjust(rj) + self.textWarm20m
        print ("[" + self.statusReady + "\\r] ").rjust(rj) + self.textReady
        print ("[" + self.statusHeating + "\\r] ").rjust(rj) + self.textHeating
        print ("[" + self.statusHeated + "\\r] ").rjust(rj) + self.textHeated
        print ("[" + self.statusOverheat + "\\r] ").rjust(rj) + self.textOverheat
        print ("[" + self.statusWarmFinished + "\\r] ").rjust(rj) + self.textWarmFinished
        print ("[" + self.statusWarm + "\\r] ").rjust(rj) + self.textWarm
        print ("[" + self.statusKettleRemoved + "\\r] ").rjust(rj) + self.textKettleRemoved
        print
        print "Default 192.168.4.1:2000"
        print
        print "The protocol build up a connection by sending an offer hand command, and receiving the handshake response"
        print "After that you can send commands and you will receive asynchronious status updates if the kettle changes state"
        print
        print "Send HELLOKETTLE\\n receive HELLOAPP\\r"
        print
        print
        print "You might receive other HELLOAPP commands at later points as other apps on the network connect to the kettle."
    
    Port       = 2000
    DirectHost = "192.168.4.1"

    commandHandshake    = "HELLOKETTLE"
    responseHandshake   = "HELLOAPP"

    # Command messages
    commandStatus       = "get sys status"
    commandHeat         = "set sys output 0x4"
    command65c          = "set sys output 0x200"
    command80c          = "set sys output 0x4000"
    command95c          = "set sys output 0x2"
    command100c         = "set sys output 0x80"
    commandWarm5m       = "set sys output 0x8005"
    commandWarm10m      = "set sys output 0x8010"
    commandWarm20m      = "set sys output 0x8020"
    commandWarm         = "set sys output 0x8"
    commandStop         = "set sys output 0x0"

    # Command text
    textHeat            = "Start heating water"
    textStartWarm         = "Start keep water warm"
    textStop            = "Stop heating water"
    textStatus          = "Status"
    textHandshake       = "Handshake"
    textGetHandshake    = "Offer hand"

    # Shared between status and command
    text100c            = "100°C selected"
    text95c             = "95°C selected"
    text80c             = "80°C selected"
    text65c             = "65°C selected"
    textWarm            = "Keep water warm" # for 30 minutes???
    textWarm5m          = "Keep water warm timer is set to 5 minutes"
    textWarm10m         = "Keep water warm timer is set to 10 minutes"
    textWarm20m         = "Keep water warm timer is set to 20 minutes"

    textGetStatus          = "Get status"
    textSelect100c      = "Select 100°C"
    textSelect95c       = "Select 95°C"
    textSelect80c       = "Select 80°C"
    textSelect65c       = "Select 65°C"
    textSelectWarm5m    = "Select keep water warm timer is set to 5 minutes"
    textSelectWarm10m   = "Select keep water warm timer is set to 10 minutes"
    textSelectWarm20m   = "Select keep water warm timer is set to 20 minutes"

    # Status text
    textHeating         = "Heating water"
    textReady           = "Ready"
    textHeated          = "Water heated"
    textOverheat        = "Kettle overheated"
    textKettleRemoved   = "Kettle removed"
    textWarmFinished    = "Keep water warm finished"

    # Status messages
    status100c          = "sys status 0x100"
    status95c           = "sys status 0x95"
    status80c           = "sys status 0x80"
    status65c           = "sys status 0x65"
    statusWarm          = "sys status 0x11"
    statusWarmFinished  = "sys status 0x10"
    statusHeating       = "sys status 0x5"
    statusReady         = "sys status 0x0"
    statusWarm5m        = "sys status 0x8005"
    statusWarm10m       = "sys status 0x8010"
    statusWarm20m       = "sys status 0x8020"
    statusHeated        = "sys status 0x3"
    statusOverheat      = "sys status 0x2"
    statusKettleRemoved = "sys status 0x1"
    
    responseStatus      = "sys status key="

    def string_responseStatus(self,status):

        def is_set(x, n):
            return x & 2**n != 0

        if len(self.responseStatus) == len(status):
            return self.textReady

        statusdata = Smarter.raw_to_number(status[len(self.responseStatus)])

        statustext = ""
        if is_set(statusdata,0):
            statustext += self.textHeating + " "
        if is_set(statusdata,1):
            statustext += self.textWarm + " "
        if is_set(statusdata,2):
            statustext += self.text65c + " "
        if is_set(statusdata,3):
            statustext += self.text80c + " "
        if is_set(statusdata,4):
            statustext += self.text95c + " "
        if is_set(statusdata,5):
            statustext += self.text100c + " "
        if is_set(statusdata,6):
            statustext += "Unknown kettle status 6! Help! Please post an issues on GitHub" + str([status]) + " "
        if is_set(statusdata,7):
            statustext += "Unknown kettle status 7! Help! Please post an issues on GitHub" + str([status]) + " "
        return statustext.strip()

    def string_response(self,status):
        if status[0:len(self.responseStatus)] == self.responseStatus:
            return self.string_responseStatus(status)
        elif status == self.status100c:
            return self.text100c
        elif status == self.status95c:
            return self.text95c
        elif status == self.status80c:
            return self.text80c
        elif status == self.status65c:
            return self.text65c
        elif status == self.statusWarm:
            return self.textWarm
        elif status == self.statusWarmFinished:
            return self.textWarmFinished
        elif status == self.statusHeating:
            return self.textHeating
        elif status == self.statusReady:
            return self.textReady
        elif status == self.statusWarm5m:
            return self.textWarm5m
        elif status == self.statusWarm10m:
            return self.textWarm10m
        elif status == self.statusWarm20m:
            return self.textWarm20m
        elif status == self.responseHandshake:
            return self.textHandshake
        elif status == self.statusHeated:
            return self.textHeated
        elif status == self.statusOverheat:
            return self.textOverheat
        elif status == self.statusKettleRemoved:
            return self.textKettleRemoved
        else:
            return "Unknown status! Help! Please post an issues on GitHub" + str([status])

    def command_to_string(self,command):
        if SmarterLegacy.commandStop == command:      return "Stop"
        elif SmarterLegacy.command65c == command:     return "65"
        elif SmarterLegacy.command80c == command:     return "80"
        elif SmarterLegacy.command95c == command:     return "95"
        elif SmarterLegacy.command100c == command:    return "100"
        elif SmarterLegacy.commandWarm == command:    return "Warm"
        elif SmarterLegacy.commandHeat == command:    return "Heat"
        elif SmarterLegacy.commandWarm5m == command:  return "5"
        elif SmarterLegacy.commandWarm10m == command: return "10"
        elif SmarterLegacy.commandWarm20m == command: return "20"
        elif SmarterLegacy.commandStatus == command:  return "Status"
        elif SmarterLegacy.commandHandshake == command:return "Handshake"
        else:
            raise SmarterErrorOld("Unknown command: (%s)" % command)

    def string_to_command(self,string):
        action = string.lower()
        if action == "stop":                        return SmarterLegacy.commandStop
        elif action == "heat" or action == "start": return SmarterLegacy.commandHeat
        elif action == "status":                    return SmarterLegacy.commandStatus
        elif action == "65":                        return SmarterLegacy.command65c
        elif action == "80":                        return SmarterLegacy.command80c
        elif action == "95":                        return SmarterLegacy.command95c
        elif action == "100":                       return SmarterLegacy.command100c
        elif action == "handshake":                 return SmarterLegacy.commandHandshake
        elif action == "warm":                      return SmarterLegacy.commandWarm
        elif action == "5":                         return SmarterLegacy.commandWarm5m
        elif action == "10":                        return SmarterLegacy.commandWarm10m
        elif action == "20":                        return SmarterLegacy.commandWarm20m
        else:
            raise SmarterErrorOld("Unknown command: (%s)" % action)

    def command_to_commandText(self,command):
        return self.string_to_commandText(self.command_to_string(command))

    def string_to_commandText(self,string):
        action = string.lower()
        if action == "stop":                        return SmarterLegacy.textStop
        elif action == "heat" or action == "start": return SmarterLegacy.textHeat
        elif action == "status":                    return SmarterLegacy.textGetStatus
        elif action == "65":                        return SmarterLegacy.textSelect65c
        elif action == "80":                        return SmarterLegacy.textSelect80c
        elif action == "95":                        return SmarterLegacy.textSelect95c
        elif action == "handshake":                 return SmarterLegacy.textGetHandshake
        elif action == "100":                       return SmarterLegacy.text100c
        elif action == "warm":                      return SmarterLegacy.textStartWarm
        elif action == "5":                         return SmarterLegacy.textSelectWarm5m
        elif action == "10":                        return SmarterLegacy.textSelectWarm10m
        elif action == "20":                        return SmarterLegacy.textSelectWarm20m
        else:
            raise SmarterErrorOld("Unknown command: (%s)" % action)



#------------------------------------------------------
# EXCEPTION CLASS
#------------------------------------------------------


KettleNoMachineHeat             = 30
KettleNoMachineOff              = 31
KettleNoMachineSettings         = 32
KettleNoMachineStoreSettings    = 33
KettleNoMachineHistory          = 34
CoffeeNoMachineStrength         = 50
CoffeeNoMachineGrinder          = 51
CoffeeNoMachineCups             = 52
CoffeeNoMachineHotplateOn       = 53
CoffeeNoMachineHotplateOff      = 54
CoffeeNoMachinesBrew            = 55
CoffeeNoMachineOff              = 56
CoffeeNoMachineSettings         = 57
CoffeeNoMachineStoreSettings    = 58
CoffeeNoMachineHistory          = 59
CoffeeNoMachineCup              = 60
CoffeeNoMachineCarafe           = 61
KettleFailedStoreSettings       = 70
CoffeeFailedStoreSettings       = 90

ConvertRawNumber                = 110
ConvertNumberRaw                = 111
ConvertCodeNumber               = 112
ConvertNumberCode               = 113

WebServerListen                = 100
WebServerStartFailed           = 101

WebServerStopMonitor           = 102
WebServerStopMonitorWeb        = 103
WebServerStopWeb               = 104

SmarterInterfaceFailedStop        = 105
SmarterInterfaceFailedStopThread  = 106

class SmarterError(Exception):

    def __init__(self, err, msg):
        print(traceback.format_exc())
        print str(msg)
        self.msg = msg
        self.err = err


class SmarterErrorOld(Exception):
    def __init__(self, msg):
        print str(msg)
        print(traceback.format_exc())
        self.msg = msg

#------------------------------------------------------
# PROTOCOL CLASS
#------------------------------------------------------

class SmarterProtocol:

    #------------------------------------------------------
    # DEFAULT CONSTANTS
    #------------------------------------------------------


    DirectHost = "192.168.4.1"
    Port       = 2081
    Fahrenheid = False


    #------------------------------------------------------
    # MESSAGES CONSTANTS
    #------------------------------------------------------


    MessageTail               = 0x7e
    MessagePayloadTail        = 0x7d
    MessageOffBase            = 0x7f


    #------------------------------------------------------
    # MESSAGE INFO
    #------------------------------------------------------


    # device
    CommandDeviceTime         = 0x02
    CommandResetSettings      = 0x10
    CommandDeviceInfo         = 0x64
    CommandUpdate             = 0x6d
    Command69                 = 0x69

    # wifi
    CommandWifiNetwork        = 0x05
    CommandWifiPassword       = 0x07
    CommandWifiJoin           = 0x0c
    CommandWifiScan           = 0x0d
    CommandWifiLeave          = 0x0f
    CommandWifiFirmware       = 0x6a

    
    # coffee
    CommandBrew               = 0x33
    CommandCoffeeStop         = 0x34
    CommandStrength           = 0x35
    CommandCups               = 0x36
    CommandBrewDefault        = 0x37
    CommandCoffeeSettings     = 0x48
    CommandCoffeeStoreSettings = 0x38
    CommandGrinder            = 0x3c
    CommandHotplateOn         = 0x3e
    CommandCoffeeHistory      = 0x46
    CommandHotplateOff        = 0x4a
    CommandCarafe             = 0x4c
    CommandSetCarafe          = 0x4b
    CommandMode                 = 0x4f
    CommandSetMode              = 0x4e
    CommandStoreTimer         = 0x40
    CommandTimers             = 0x41
    CommandDisableTimer       = 0x43
 
    # kettle
    CommandHeat               = 0x15
    CommandKettleStop         = 0x16
    CommandHeatFormula        = 0x19
    CommandHeatDefault        = 0x21
    Command20                 = 0x20
    Command22                 = 0x22
    Command23                 = 0x23
    Command30                 = 0x30
    CommandKettleStoreSettings = 0x1f
    CommandKettleHistory      = 0x28
    CommandKettleSettings     = 0x2e
    CommandStoreBase          = 0x2a
    CommandBase               = 0x2b
    CommandCalibrate          = 0x2c
    
    # Relay
    CommandRelayInfo      = 0x70
    CommandRelayBlock     = 0x72
    CommandRelayUnblock   = 0x73
    CommandRelayModifiersInfo = 0x74
    CommandRelayPatch     = 0x76


    # device
    ResponseCommandStatus     = 0x03
    ResponseWirelessNetworks  = 0x0e
    ResponseKettleHistory     = 0x29
    ResponseDeviceInfo        = 0x65
    ResponseRelayInfo         = 0x71
    ResponseRelayModifiersInfo = 0x75
    ResponseWifiFirmware      = 0x6b

    # coffee
    ResponseCoffeeSettings    = 0x49
    ResponseCoffeeStatus      = 0x32
    ResponseTimers            = 0x42
    ResponseCoffeeHistory     = 0x47
    ResponseCarafe            = 0x4d
    ResponseMode              = 0x50
    
    # kettle
    ResponseKettleStatus      = 0x14
    ResponseBase              = 0x2d
    ResponseKettleSettings    = 0x2f
    
    # format kettle? coffee? response to command, description
    CommandMessages = {
        CommandRelayInfo        : (True,True,[ResponseRelayInfo],"Get iBrew relay info"),
        CommandRelayModifiersInfo   : (True,True,[ResponseRelayModifiersInfo],"Get iBrew relay message block info"),
        CommandRelayBlock       : (True,True,[ResponseRelayModifiersInfo],"iBrew block relay message"),
        CommandRelayUnblock     : (True,True,[ResponseRelayModifiersInfo],"iBrew unblock relay message"),
        CommandRelayPatch       : (True,True,[ResponseRelayModifiersInfo],"iBrew patch relay message"),
        CommandDeviceTime       : (True,True,[ResponseCommandStatus],"Set appliance time"),
        CommandWifiNetwork      : (True,True,[ResponseCommandStatus],"Set wireless network name"),
        CommandWifiPassword     : (True,True,[ResponseCommandStatus],"Set wireless network password"),
        CommandWifiJoin         : (True,True,[],"Join wireless network"),
        CommandWifiScan         : (True,True,[ResponseWirelessNetworks],"Scan for wireless networks"),
        CommandWifiLeave        : (True,True,[],"Wireless network direct mode"),
        CommandResetSettings    : (True,True,[ResponseCommandStatus],"Reset default user settings"),
        CommandHeat             : (True,False,[ResponseCommandStatus],"Heat kettle"),
        CommandKettleStop       : (True,False,[ResponseCommandStatus],"Stop heating water"),
        CommandHeatFormula      : (True,False,[ResponseCommandStatus],"Heat kettle using formula mode"),
        CommandKettleStoreSettings : (True,False,[ResponseCommandStatus],"Set kettle default user settings"),
        Command20               : (True,False,[ResponseCommandStatus],"Working unknown command (turn on?)"),
        CommandHeatDefault      : (True,False,[ResponseCommandStatus],"Heat kettle with default settings"),
        Command22               : (True,False,[ResponseCommandStatus],"Working unknown command (turn on?)"),
        Command23               : (True,False,[ResponseCommandStatus],"Working unknown command (turn on?)"),
        CommandKettleHistory    : (True,False,[ResponseKettleHistory],"Get kettle history"),
        CommandStoreBase        : (True,False,[ResponseCommandStatus],"Set water sensor base value"),
        CommandBase             : (True,False,[ResponseBase,ResponseCommandStatus],"Get water sensor base value"),
        CommandCalibrate        : (True,False,[ResponseBase,ResponseCommandStatus],"Calibrate water sensor"),
        CommandKettleSettings   : (True,False,[ResponseKettleSettings],"Get default kettle user settings"),
        Command30               : (True,False,[ResponseCommandStatus],"Working unknown command"),
        CommandBrew             : (False,True,[ResponseCommandStatus],"Start coffee brewing"),
        CommandCoffeeStop       : (False,True,[ResponseCommandStatus],"Stop coffee brewing"),
        CommandStrength         : (False,True,[ResponseCommandStatus],"Set strength of the coffee to brew"),
        CommandCups             : (False,True,[ResponseCommandStatus],"Set number of cups to brew"),
        CommandBrewDefault      : (False,True,[ResponseCommandStatus],"Start coffee brewing using machine settings"),
        CommandCoffeeStoreSettings : (False,True,[ResponseCommandStatus],"Set coffee machine default user settings"),
        CommandGrinder          : (False,True,[ResponseCommandStatus],"Toggle grinder"),
        CommandHotplateOn       : (False,True,[ResponseCommandStatus],"Turn on hotplate"),
        CommandCarafe           : (False,True,[ResponseCarafe,ResponseCommandStatus],"Get coffee carafe required"),
        CommandMode             : (False,True,[ResponseMode,ResponseCommandStatus],"Get mode"),
        CommandStoreTimer       : (False,True,[ResponseCommandStatus],"Store timer"),
        CommandTimers           : (False,True,[ResponseTimers,ResponseCommandStatus],"Get timers"),
        CommandDisableTimer     : (False,True,[ResponseCommandStatus],"Timer event handled"),
        CommandSetCarafe        : (False,True,[ResponseCommandStatus],"Set coffee carafe required"),
        CommandSetMode          : (False,True,[ResponseCommandStatus],"Set mode"),
        CommandCoffeeSettings   : (False,True,[ResponseCoffeeSettings,ResponseCommandStatus],"Get default coffee machine user settings"),
        CommandCoffeeHistory    : (False,True,[ResponseCoffeeHistory],"Get coffee machine history"),
        CommandHotplateOff      : (False,True,[ResponseCommandStatus],"Turn off hotplate"),
        CommandDeviceInfo       : (True,True,[ResponseDeviceInfo],"Get appliance info"),
        Command69               : (True,True,[ResponseCommandStatus],"Working unknown command"),
        CommandWifiFirmware     : (True,True,[ResponseWifiFirmware],"Get wifi firmware info"),
        CommandUpdate           : (True,True,[],"Appliance firmware update")
    }



    def __con(self,coffee,kettle):
        if coffee and kettle:
            return [self.DeviceKettle,self.DeviceCoffee]
        if coffee and not kettle:
            return [self.DeviceCoffee]
        if not coffee and kettle:
            return [self.DeviceKettle]
        else:
            return []


    def CommandToJSON(self):
        json = dict()
        for command in self.CommandMessages:
            message = self.CommandMessages[command]
            json[command] = { 'appliance' : self.__con(message[0],message[1]), 'description' : self.message_description(command) }
        return json

    def ResponseToJSON(self):
        json = dict()
        for response in self.ResponseMessages:
            if self.message_is_response(response):
                message = self.ResponseMessages[response]
                json[response] = { 'appliance' : self.__con(message[0],message[1]), 'description' : self.message_description(response) }
        return json


    def StatusToJSON(self):
        return { self.ResponseKettleStatus : { 'appliance' : [self.DeviceKettle], 'description' : self.message_description(self.ResponseKettleStatus) },
                 self.ResponseCoffeeStatus : { 'appliance' : [self.DeviceCoffee], 'description' : self.message_description(self.ResponseCoffeeStatus) }
                }


    # format: kettle?, coffee? (None is unnknown), minimal length (0 = variable), response to command, description
    ResponseMessages = {
        #incomplete? ... chech the first one...
        ResponseCommandStatus   : (True,True,3,[CommandDeviceTime,CommandWifiNetwork,CommandWifiPassword,CommandResetSettings,CommandHeat,CommandKettleStop,CommandHeatFormula,CommandKettleStoreSettings,Command20,CommandHeatDefault,Command22,Command23,CommandBase,CommandCalibrate,Command69,CommandStoreTimer,CommandTimers,CommandDisableTimer,Command30,CommandSetCarafe,CommandSetMode,CommandStrength,CommandCups,CommandGrinder,CommandHotplateOn,CommandMode,CommandCarafe,CommandHotplateOff,CommandCoffeeSettings,CommandBrew,CommandCoffeeStop,CommandBrewDefault],"Command status",[]),
        ResponseWirelessNetworks: (True,True,0,[CommandWifiScan],"Wireless networks list",[]),
        ResponseKettleHistory   : (True,False,0,[CommandKettleHistory],"Kettle history",[]),
        ResponseCoffeeHistory   : (False,True,0,[CommandCoffeeHistory],"Coffee machine history",[]),
        ResponseBase            : (True,False,4,[CommandBase,CommandCalibrate],"Water sensor base value",[]),
        ResponseKettleSettings  : (True,False,9,[CommandKettleSettings],"Default kettle user settings",[]),
        ResponseKettleStatus    : (True,False,7,[],"Kettle status",[]),
        ResponseDeviceInfo      : (True,True,4,[CommandDeviceInfo],"Appliance info",[]),
        ResponseRelayInfo       : (True,True,0,[CommandRelayInfo],"iBrew remote relay info",[]),
        ResponseRelayModifiersInfo  : (True,True,0,[CommandRelayModifiersInfo,CommandRelayBlock,CommandRelayUnblock,CommandRelayPatch],"iBrew relay rules block messages info",[]),
        ResponseWifiFirmware    : (True,True,0,[CommandWifiFirmware],"Wifi firmware info",[]),
        ResponseCarafe          : (False,True,3,[CommandCarafe],"Carafe required",[]),
        ResponseCoffeeStatus    : (False,True,7,[],"Coffee machine status",[]),
        ResponseCoffeeSettings  : (False,True,6,[CommandCoffeeSettings],"Default coffee machine user settings",[]),
        ResponseMode   : (False,True,3,[CommandMode],"Mode",[]),
        ResponseTimers          : (False,True,0,[CommandTimers],"Stored timers",[])

    }


    def message_response_length(self,id):
        if self.message_is_response(id) or self.message_is_status(id):
            return self.ResponseMessages[id][2]
        return 0
    
    
    def message_description(self,id):
        if self.message_is_response(id) or self.message_is_status(id):
            return self.ResponseMessages[id][4]
        elif self.message_is_command(id):
            return self.CommandMessages[id][3]
        else:
            return "Unknown message"


    def message_connection_type(self,id):
        if self.message_is_response(id):
            return "Command"
        elif self.message_is_command(id):
            return "Response"
        else:
            return ""

    def message_connection(self,id):
        if self.message_is_response(id):
            x = self.ResponseMessages[id][3]
            if x: x.sort()
            return x
        elif self.message_is_command(id):
            x = self.CommandMessages[id][2]
            if x: x.sort()
            return x
        else:
            return []


    def message_is_known(self,id):
        return self.message_is_response(id) or self.message_is_command(id) or self.message_is_status(id)


    def message_is_response(self,id):
        if id != self.ResponseKettleStatus and id != self.ResponseCoffeeStatus:
            return self.ResponseMessages.has_key(id)
        return False


    def message_is_status(self,id):
        if id == self.ResponseKettleStatus or id == self.ResponseCoffeeStatus:
            return True
        return False


    def message_is_command(self,id):
        return self.CommandMessages.has_key(id)


    def message_is_type(self,id):
        if self.message_is_command(id):
            return "Command"
        elif id == self.ResponseKettleStatus or id == self.ResponseCoffeeStatus:
            return "Status"
        else:
            return "Response"

    # internal use here only
    def message_supported(self,state):
        if state is None:
            return "?"
        if state:
            return "✓"
        else:
            return "✕"


    def message_kettle(self,id):
        if self.message_is_command(id):
            return self.CommandMessages[id][0]
        if self.message_is_response(id) or self.message_is_status(id):
            return self.ResponseMessages[id][0]


    def message_kettle_supported(self,id):
        return self.message_supported(self.message_kettle(id))


    def message_coffee_supported(self,id):
        return self.message_supported(self.message_coffee(id))


    def message_coffee(self,id):
        if self.message_is_command(id):
            return self.CommandMessages[id][1]
        if self.message_is_response(id) or self.message_is_status(id):
            return self.ResponseMessages[id][1]


    #------------------------------------------------------
    # MESSAGE GROUPS INFO
    #------------------------------------------------------
    #
    # Fire wall blocking rules and online help tags will use this
    #

    GroupWifi           = 1
    MessagesWifi        = [CommandWifiJoin,CommandWifiLeave,CommandWifiNetwork,CommandWifiPassword,CommandWifiFirmware,CommandWifiScan,ResponseWifiFirmware,ResponseWirelessNetworks]
    GroupCalibrateOnly  = 39
    MessagesCalibrateOnly  = [CommandStoreBase,CommandCalibrate]
    GroupCalibrate      = 2
    MessagesCalibrate   = MessagesCalibrateOnly + [CommandBase,ResponseBase]
    GroupUnknown        = 3
    GroupUnknownKettle  = 26
    MessagesUnknownKettle = [Command20,Command22,Command23,Command30]
    MessagesUnknown     = MessagesUnknownKettle + [Command69]
    GroupTimers         = 4
    MessagesTimers      = [CommandStoreTimer,CommandTimers,CommandDisableTimer,ResponseTimers]
    GroupHistory        = 5
    GroupCoffeeHistory  = 29
    GroupKettleHistory  = 30
    MessagesKettleHistory = [CommandKettleHistory,ResponseKettleHistory]
    MessagesCoffeeHistory = [CommandCoffeeHistory,ResponseCoffeeHistory]
    MessagesHistory     = MessagesCoffeeHistory + MessagesKettleHistory
    GroupTime           = 6
    MessagesTime        = [CommandDeviceTime]
    GroupGet            = 7
    GroupCoffeeGet      = 27
    GroupKettleGet      = 28
    MessagesKettleGet  = [CommandKettleSettings,ResponseKettleSettings]
    MessagesCoffeeGet  = [CommandCoffeeSettings,ResponseCoffeeSettings]
    MessagesGet         = MessagesCoffeeGet + MessagesKettleGet
    GroupStore          = 8
    GroupCoffeeStore    = 31
    GroupKettleStore    = 32
    MessagesKettleStore = [CommandKettleStoreSettings]
    MessagesCoffeeStore = [CommandCoffeeStoreSettings]
    MessagesStore       = MessagesCoffeeStore + MessagesKettleStore
    GroupAll            = 9
    GroupKettleAll      = 33
    GroupCoffeeAll      = 34
    MessagesCoffeeAll   = MessagesCoffeeStore + MessagesCoffeeGet
    MessagesKettleAll   = MessagesKettleStore + MessagesKettleGet
    MessagesAll         = MessagesStore + MessagesGet
    GroupKettleControl = 10
    __MessagesKettle    = [CommandHeat,CommandHeatFormula,CommandHeatDefault,CommandKettleStop]
    MessagesKettleControl      = __MessagesKettle + [ResponseKettleStatus]
    GroupMaintenance         = 11
    MessagesMaintenance      = [CommandUpdate] + [CommandResetSettings]
    GroupDeviceInfo         = 12
    MessagesDeviceInfo      = [CommandDeviceInfo, ResponseDeviceInfo]
    GroupCoffeeControl         = 13
    __MessagesCoffee    = [CommandBrew,CommandBrewDefault,CommandCoffeeStop,CommandCups,CommandStrength,CommandGrinder,CommandHotplateOn,CommandHotplateOff]
    MessagesCoffeeControl      = __MessagesCoffee + [ResponseCoffeeStatus]
    
    MessagesControl     = MessagesCoffeeControl + MessagesKettleControl
    GroupControl        = 36
    GroupModes          = 14
    MessagesModesStore  = [CommandSetMode,CommandSetCarafe]
    MessagesModesGet    = [CommandMode,CommandCarafe,ResponseMode,ResponseCarafe]
    MessagesModes       = MessagesModesGet + MessagesModesStore
    GroupDebug          = 15
    MessagesDebug       = MessagesUnknown + MessagesTime + MessagesTimers + MessagesHistory + MessagesMaintenance
    GroupSetup          = 16
    MessagesSetup       = MessagesWifi + MessagesCalibrate + MessagesStore + MessagesModes
    GroupNormal         = 17
    MessagesNormal      = MessagesCoffeeControl + MessagesKettleControl + MessagesGet + MessagesDeviceInfo + [ResponseCommandStatus]
    GroupUser           = 18
    MessagesUser        = MessagesNormal

    GroupRelay         = 40
    MessagesRelay      = [CommandRelayInfo, ResponseRelayInfo, CommandRelayPatch, CommandRelayBlock, CommandRelayUnblock, CommandRelayModifiersInfo, ResponseRelayModifiersInfo]

    GroupAdmin          = 19
    MessagesAdmin       = MessagesSetup + MessagesNormal + MessagesRelay
    GroupGod            = 20
    MessagesGod         = MessagesAdmin + MessagesDebug
    
    GroupReadOnly       = 21
    MessagesReadOnly    = MessagesDebug + MessagesSetup +  __MessagesCoffee + __MessagesKettle + MessagesGet + MessagesDeviceInfo
    
    GroupModeGet        = 22
    GroupModeStore      = 23
  
    GroupKettle         = 24
    GroupRest         = 37
    GroupShared       = 35
    MessagesShared    = MessagesWifi + MessagesTime + [Command69] + MessagesDeviceInfo + MessagesMaintenance + [ResponseCommandStatus]

    MessagesKettle      = MessagesKettleControl + MessagesCalibrate + MessagesShared + MessagesKettleHistory + MessagesUnknownKettle + MessagesKettleStore + MessagesKettleGet
    GroupCoffee         = 25
    MessagesCoffee      = MessagesCoffeeControl + MessagesTimers + MessagesModes + MessagesShared + MessagesCoffeeStore + MessagesCoffeeGet +  MessagesCoffeeHistory
    
    GroupStatus  = 38
    MessagesStatus = [ResponseCommandStatus] + [ResponseCoffeeStatus] + [ResponseKettleStatus]


    
    def __init__(self):
        l = []
        c = []
        r = []
        for i in range(0,255):
            l += [i]
        for i in self.CommandMessages:
            c += [i]
        for i in self.ResponseMessages:
            r += [i]
        
        self.MessagesRest = list(set(l).difference(set(c).union(set(r))))
        self.MessagesReadOnly += self.MessagesRest
        self.MessagesGod += self.MessagesRest
        self.Groups[self.GroupRest] = ("Rest",list(set(l).difference(set(c).union(set(r)))))

            
    
    Groups = {
        GroupStatus      : ("Status",MessagesStatus),
        GroupWifi        : ("Wifi",MessagesWifi),
        GroupCalibrate   : ("Calibration",MessagesCalibrate),
        GroupCalibrateOnly  : ("CalibrationBase",MessagesCalibrateOnly),
        GroupModes       : ("Modes",MessagesModes),
        GroupUnknown     : ("Unknown",MessagesUnknown),
        GroupKettleControl : ("KettleControls",MessagesKettleControl),
        GroupCoffeeControl : ("CoffeeControls",MessagesCoffeeControl),
        GroupControl    : ("Controls",MessagesControl),
        GroupUnknownKettle : ("UnknownKettle",MessagesUnknownKettle),
        GroupMaintenance : ("Maintenance",MessagesMaintenance),

        # Kinda duplicate... of the other protocol table with commands... (o well :)
        GroupKettle : ("Kettle",MessagesKettle),
        GroupCoffee : ("Coffee",MessagesCoffee),
        
        GroupTime        : ("Time",MessagesTime),
        GroupTimers      : ("Timers",MessagesTimers),
        GroupHistory     : ("History",MessagesHistory),
        GroupKettleHistory     : ("KettleHistory",MessagesKettleHistory),
        GroupCoffeeHistory     : ("CoffeeHistory",MessagesCoffeeHistory),
        GroupDeviceInfo  : ("ApplianceInfo",MessagesDeviceInfo),
        GroupStore       : ("SettingsStore",MessagesStore),
        GroupRelay       : ("Relay",MessagesRelay),
        GroupGet         : ("SettingsGet",MessagesGet),
        GroupAll         : ("Settings",MessagesAll),
        GroupKettleStore : ("KettleStore",MessagesKettleStore),
        GroupKettleGet   : ("KettleGet",MessagesKettleGet),
        GroupCoffeeStore : ("CoffeeStore",MessagesCoffeeStore),
        GroupCoffeeGet   : ("CoffeeGet",MessagesCoffeeGet),
        GroupCoffeeAll   : ("CoffeeSettings",MessagesCoffeeAll),
        GroupKettleAll   : ("KettleSettings",MessagesKettleAll),
        GroupModeGet     : ("ModesGet",MessagesModesGet),
        GroupModeStore   : ("ModesStore",MessagesModesStore),
        GroupShared      : ("Shared",MessagesShared),
        
        # Users
        GroupUser        : ("User",MessagesUser),
        GroupAdmin       : ("Admin",MessagesAdmin),
        GroupGod         : ("God",MessagesGod),

        # Modes
        GroupDebug       : ("Debug",MessagesDebug),
        GroupNormal      : ("Normal",MessagesNormal),
        GroupSetup       : ("Setup",MessagesSetup),
        GroupReadOnly    : ("ReadOnly",MessagesReadOnly),
    
    }
    
    def groupsCommand(self,id):
        """
        Return a list of groups in which the message id is present
        """
        l = []
        for g in self.Groups:
            if id in self.Groups[g][1]:
                l += [g]
        return l

    def hasGroup(self,group):
        """
        Check if groupid actually exists
        """
        return self.Groups.has_key(group)
    
    
    def isGroup(self,string):
        """
        Check if string is a group
        """
        try:
            self.string_to_group(string)
        except SmarterError:
            return False
        return True
        

    def groupsList(self,groups):
        """
        Return group names as a list
        """
        s = []
        for g in groups:
            s += [self.Groups[g][0]]
        return sorted(s)

    def groupsString(self,groups):
        """
        Return group names as a string seperated with spaces
        """
        return " ".join(self.groupsList(groups)).upper()
    
    
    def string_to_group(self,string):
        """
        string name to group id
        """
        for g in self.Groups:
            if self.Groups[g][0].lower() == string.lower().strip():
                return g
        raise SmarterError(0,"Group not available")
    
    def group_to_string(self,group):
        """
        group id to string name
        """
        if self.hasGroup(group):
            return self.Groups[group][0].upper()
        else:
            raise SmarterError(0,"Group not available")


    def idsMin(self,ids):
        return list(set(ids))

    def idsRemove(self,ids,removeids):
        x = set(ids)
        return list(set(ids).difference(set(removeids)))

    def idsAdd(self,ids,addids):
        return self.idsMin(ids + addids)

    def ids_to_string(self,ids):
        return " ".join([Smarter.number_to_code(i) for i in ids])

    def groupsListDecode(self,list):
        """
        Return a list of message ID's from a list of string
        The list can contain either message ID or Group names sperated with a comma:
        """
        ids = []
        for i in list:
            if i in [j.lower() for j in self.groupsList(self.Groups.keys())]:
                ids += self.Groups[self.string_to_group(i)][1]
            else:
                try:
                    message = self.code_to_number(i)
                except SmarterError:
                    raise SmarterError(0,"Could not decode group or message id")
                else:
                    ids += [message]
        return self.idsMin(ids)

    def idsListEncode(self,ids):
        """
        Neat function that procuces a tupple of a list of groups and a list of ids not in those groups
        """
        idsleft = set(ids)
        l = []
        for g in self.Groups:
            found = True
            for i in self.Groups[g][1]:

                messages = set(self.Groups[g][1])
                if not messages.difference(set(ids)):
                    l += [g]
                    idsleft = idsleft.difference(messages)
                    break
        return (l,idsleft)

    #------------------------------------------------------
    # RAW <-> BASIC TYPE
    #------------------------------------------------------

    def raw_to_number(self,raw):
        try:
            return struct.unpack('B',raw)[0]
        except Exception:
            # DEBUG LEN RAW!!! (probably tornado)
            raise SmarterError(ConvertRawNumber,"Could not convert raw data to number" + str(len(raw)))

    def number_to_raw(self,number):
        try:
            i = int(number)
        except Exception:
            raise SmarterError(ConvertNumberRaw,"Could not convert number to raw data")
        
        if number < 0 or number > 256:
            raise SmarterError(ConvertNumberRaw,"Could not to convert number " + str(number) + " to raw data, because it is out of range [0..255]")
        try:
            return struct.pack('B',number)
        except Exception:
            raise SmarterError(ConvertNumberRaw,"Could not convert number to raw data: " + str(number))


    def raw_to_code(self,raw):
        return self.number_to_code(self.raw_to_number(raw))


    def code_to_raw(self,code):
        return self.number_to_raw(self.code_to_number(code))


    def code_to_number(self,code):
        try:
            return int(code,16)
        except Exception:
            raise SmarterError(ConvertCodeNumber,"Could not convert code to number: " + code )


    def number_to_code(self,number):
        try:
            code = hex(number)[2:4]
        except Exception:
            raise SmarterError(ConvertNumberCode,"Could not convert number to code: " + str(number))
        if number < 16:
            return '0' + code
        return code


    def text_to_raw(self,text):
        return text
    
    def raw_to_text(self,raw):
        #TEXT ENDS WITH MessageTail 7E then 7E is removed
        # FIX ERROR CHECKING + CODE
        s = ""
        for i in range(1,len(raw)-1):
            x = str(raw[i])
            if x in string.printable:
                s += x
        if raw[-1] != Smarter.number_to_raw(self.MessageTail):
            if raw[-1] in string.printable:
                s += x
        return s

    #------------------------------------------------------
    # RAW HEX STRING <-> RAW
    #------------------------------------------------------

    # Convert raw data to hex string without 0x seperated by spaces
    def message_to_codes(self,message,space = False):
        raw = ""
        for i in range(0,len(message)):
            try:
                raw += self.raw_to_code(message[i])
            except Exception:
                raise SmarterErrorOld("Could not decode message at position: " + str(i))
            if space and i != len(message)-1:
                raw += " "
        return raw


    # Convert hex string without 0x input maybe seperated by spaces or not
    def codes_to_message(self,string):
        message = ""
        code = string.strip()
        
        if len(code) <= 2:
            return self.code_to_raw(code)
        
        if len(code) % 2 == 0 and code[2] != " ":
            for i in range(0,len(code) / 2):
                try:
                    message += self.code_to_raw(code[i*2]+code[i*2+1])
                except Exception:
                    raise SmarterErrorOld("Could not encode code \'" + code + "\' at position: " + str(i*2+1))
 
        elif len(code) % 3 == 2:
            for i in range(0,(len(code) / 3)+1):
                if i > 0:
                    if code[i*3-1] != ' ':
                        raise SmarterErrorOld("Expected space character in code  \'" + code + "\' at position: " + str(i*3)+1)
                try:
                    message += self.code_to_raw(code[i*3]+code[i*3+1])
                except Exception:
                    raise SmarterErrorOld("Could not encode code \'" + code + "\' at position: " + str(i*3+1))
    
        else:
            raise SmarterErrorOld("Missing character in code \'" + code + "\'  at position: " + str(len(code)+1))

        return message
    

    #------------------------------------------------------
    # RAW <-> TYPE
    #------------------------------------------------------


    #------------------------------------------------------
    # DEVICE & FIRMWARE ARGUMENT WRAPPER
    #------------------------------------------------------


    DeviceKettle              = 0x01
    DeviceCoffee              = 0x02

    DeviceStringKettle        = "iKettle 2.0"
    DeviceStringCoffee        = "Smarter Coffee"

    KettleFirmwareVerified    = [19]
    CoffeeFirmwareVerified    = [20,22]
 
    WifiStringKettleUpdate    = DeviceStringKettle + " Update"
    WifiStringCoffeeUpdate    = DeviceStringCoffee + " Update"
    WifiStringKettleDirect    = DeviceStringKettle + ":c0"
    WifiStringCoffeeDirect    = DeviceStringCoffee + ":c1"
    
    
    FirmWareReleaseNotes = {
        22 : "Increases keep warm time up to 40 minutes as default.",
        19 : "Reduces kettle overboiling. Improved temperature accuracy."
    }
    
    
    def is_kettle(self,device):
        return device == self.DeviceKettle


    def is_kettle_verified(self,firmware):
        return firmware in self.KettleFirmwareVerified
    
    
    def is_coffee_verified(self,firmware):
        return firmware in self.CoffeeFirmwareVerified
    
    
    def is_coffee(self,device):
        return device == self.DeviceCoffee


    def firmware_verified(self,device,firmware):
        if (device == self.DeviceCoffee and self.is_coffee_verified(firmware)) or (device == self.DeviceKettle and self.is_kettle_verified(firmware)):
            return "iBrew certified firmware"
        return "Unsupported firmware"


    def device_to_string(self,device):
        if self.is_kettle(device):
            return self.DeviceStringKettle
        elif self.is_coffee(device):
            return self.DeviceStringCoffee
        else:
            return "Unknown"


    def device_info(self,device,firmware):
        return self.device_to_string(device)  + " (" + self.firmware_verified(device,firmware) + " v" + str(firmware) + ")"


    #------------------------------------------------------
    # STRENGTH ARGUMENT WRAPPER
    #------------------------------------------------------


    CoffeeWeak                = 0x00
    CoffeeMedium              = 0x01
    CoffeeStrong              = 0x02
    
    CoffeeStringWeak          = "weak"
    CoffeeStringMedium        = "medium"
    CoffeeStringStrong        = "strong"

    # approx measure it?
    CoffeeGramsStrong         = 200
    CoffeeGramsMedium         = 150 #???
    CoffeeGramsWeak           = 100 #???


    def check_strength(self,strength):
        if strength == self.CoffeeMedium or strength == self.CoffeeStrong or strength == self.CoffeeWeak:
            return strength
        else:
            raise SmarterErrorOld("Invalid coffee strength ["+self.CoffeeStringWeak+", "+self.CoffeeStringMedium+", "+self.CoffeeStringStrong +"]: " + strength)


    def strength_to_raw(self,strength):
        return self.number_to_raw(self.check_strength(strength))


    def raw_to_strength(self,raw):
        return self.check_strength(self.raw_to_number(raw))
    
    def strength_to_string(self,number):
        if self.CoffeeWeak == number:
            return self.CoffeeStringWeak
        elif self.CoffeeMedium == number:
            return self.CoffeeStringMedium
        elif self.CoffeeStrong == number:
            return self.CoffeeStringStrong
        else:
            raise SmarterErrorOld("Invalid coffee strength ["+self.CoffeeStringWeak+", "+self.CoffeeStringMedium+", "+CoffeeStringStrong +"] " + self.number_to_code(strength))

    def string_to_strength(self,strength):
        if strength.strip().lower() == self.CoffeeStringWeak:
            return self.CoffeeWeak
        elif strength.strip().lower() == self.CoffeeStringMedium:
            return self.CoffeeMedium
        elif strength.strip().lower() == self.CoffeeStringStrong:
            return self.CoffeeStrong
        else:
            raise SmarterErrorOld("Invalid coffee strength ["+self.CoffeeStringWeak+", "+self.CoffeeStringMedium+", "+self.CoffeeStringStrong +"] " + strength)


    #------------------------------------------------------
    # TEMPERATURE ARGUMENT WRAPPER
    #------------------------------------------------------

    def is_on_base(self,raw):
        return self.raw_to_number(raw) != self.MessageOffBase
 
 
    def string_base_on_off(self,onbase):
        if onbase:
            return "On"
        else:
           return "Off"
           
    def celsius_to_fahrenheid(self,temperature):
        return ((temperature * 9) / 5) + 32
    
    
    def fahrenheid_to_celsius(self,temperature):
        return ((temperature - 32) * 5) / 9
    
    
    #
    #  PLEASE CHECK THESE TWO FUNCTIONS OUT>>> THEIR DANCING, .... WEAR AGUN
    #
    #
    #
    
    
    def check_temperature_celsius(self,temperature):
        # if fahrenheid then converto...
        # if self.Fahrenheid
        if temperature < 0 or temperature > 100 and not self.is_on_base(self.number_to_raw(temperature)):
            if self.Fahrenheid:
                raise SmarterErrorOld("Temperature out of range ["+self.celsius_to_fahrenheid(0)+".."+self.celsius_to_fahrenheid(100)+"] ºK: " + str(temperature))
            else:
                raise SmarterErrorOld("Temperature out of range [0..100] ºC: " + str(temperature))
        return temperature
    
    
    def check_temperature(self,temperature):
        if self.Fahrenheid:
            t = self.fahrenheid_to_celsius(temperature)
        else:
            t = temperature
        if t > 100 or t < 0:
            raise SmarterErrorOld("Temperature out of range [0..100] ºC ")
        return t


    def raw_to_temperature(self,raw):
        if self.is_on_base(raw):
            return self.check_temperature_celsius(self.raw_to_number(raw))
        return 0


    def temperature_to_raw(self,temperature):
        return self.number_to_raw(self.check_temperature_celsius(temperature))


    def temperaturemerged_to_raw(self,temperature,onbase):
        if onbase:
            return Smarter.temperature_to_raw(temperature)
        else:
            return Smarter.number_to_raw(Smarter.MessageOffBase)
  
  
    def temperature_to_string(self,temperature):
        if self.Fahrenheid:
            return str(temperature)+" ºF"
        else:
            return str(temperature)+" ºC"


    def temperature_symbol_to_string(self):
        if self.Fahrenheid:
            return "ºF"
        else:
            return "ºC"

    def temperature_metric_to_string(self):
        if self.Fahrenheid:
            return "fahrenheid"
        else:
            return "celsius"

    def string_to_temperature(self,temperature):
        try:
            t = int(temperature)
            return self.check_temperature(t)
        # FIX THIS INTO TWO DIFFERENT EXCEPTION INT & TEMPCHECK
        except Exception, e:
            raise SmarterErrorOld("Temperature is not a number: " + temperature)


    #------------------------------------------------------
    # HOTPLATE KEEPWARM ARGUMENT WRAPPER
    #------------------------------------------------------

    def string_to_hotplate(self,string):
        try:
            return self.check_hotplate(int(string))
        except Exception:
            # FIX exception
            raise SmarterErrorOld("Hotplate timer is not a number: " + string)


    # added new firmware v22 which has a hotplate range till 40...
    def check_hotplate(self,timer,version=20):
        if version < 22 and timer != 0 and (timer < 5 or timer > 35):
            raise SmarterErrorOld("Hotplate timer out of range [0=Off] or [5..35] minutes: " + str(timer))
        if version >= 22 and timer != 0 and (timer < 5 or timer > 40):
            raise SmarterErrorOld("Hotplate timer out of range [0=Off] or [5..40] minutes: " + str(timer))
        return timer

    def check_hotplate_on(self,timer):
        if timer > 0: return True
        else: return False

    def raw_to_hotplate(self,raw,version=20):
        return self.check_hotplate(self.raw_to_number(raw),version)


    def hotplate_to_raw(self,timer,version=20):
        return self.number_to_raw(self.check_hotplate(timer,version))


    #------------------------------------------------------
    # KEEPWARM ARGUMENT WRAPPER
    #------------------------------------------------------

    def string_to_keepwarm(self,string):
        try:
            return self.check_keepwarm(int(string))
        except Exception:
            # FIX exception
            raise SmarterErrorOld("Keepwarm timer is not a number: " + string)


    def check_keepwarm(self,timer):
        if timer != 0 and (timer < 1 or timer > 30):
            raise SmarterErrorOld("Kettle keep warm timer out of range [0=Off] or [5..30] minutes: " + str(timer))
        return timer


    def check_keepwarm_on(self,timer):
        if timer > 0: return True
        else: return False
    
    
    def raw_to_keepwarm(self,raw):
        return self.check_keepwarm(self.raw_to_number(raw))


    def keepwarm_to_raw(self,timer):
        return self.number_to_raw(self.check_keepwarm(timer))


    #------------------------------------------------------
    # WATERSENSOR ARGUMENT WRAPPER
    #------------------------------------------------------

    def check_watersensor(self, watersensor):
        if watersensor < 0 or watersensor > 4095:
            raise SmarterErrorOld("Watersensor out of range [0..4095]")
        return watersensor
        
    def raw_to_watersensor(self,raw_low,raw_high):
        return self.check_watersensor(self.raw_to_number(raw_low) * 256 + self.raw_to_number(raw_high))


    def watersensor_to_raw(self,watersensor):
        return self.number_to_raw(watersensor / 256) + self.number_to_raw(watersensor % 256)

    def string_to_watersensor(self,string):
        try:
            watersensor = int(string)
        except Exception:
            raise SmarterErrorOld("Not a watersensor value")
        return self.check_watersensor(watersensor)
 
 
 
    #------------------------------------------------------
    # TIMER ARGUMENT WRAPPER
    #------------------------------------------------------

    TimerAll = 0x00
    Timer1 = 0x01
    Timer2 = 0x02
    Timer3 = 0x03
    Timer4 = 0x04
    
    Timer = {
        TimerAll : "Timer All",
        Timer1 : "Timer 1",
        Timer2 : "Timer 2",
        Timer3 : "Timer 3",
        Timer4 : "Timer 4"
    }
    
    #------------------------------------------------------
    # BOOLEAN ARGUMENT WRAPPER
    #------------------------------------------------------

    def raw_to_bool(self,raw):
        bool = self.raw_to_number(raw)
        if bool > 1:
            raise SmarterErrorOld("Not a boolean value: " + str(int))
        if bool == 1:
            return True
        return False
 
 
    def bool_to_raw(self,boolean):
        return self.number_to_raw(boolean)


    def string_to_bool(self,boolean):
        if boolean.lower() == "on" or boolean.lower() == "true" or boolean.lower() == "1" or boolean.lower() == "enabled" or boolean.lower() == "active" or boolean.lower() == "yes":
            return True
        if boolean.lower() == "off" or boolean.lower() == "false" or boolean.lower() == "0" or boolean.lower() == "disabled" or boolean.lower() == "not" or boolean.lower() == "no":
            return False
        else:
            raise SmarterErrorOld("Unknown boolean [true,false 1,0 on,off enabled,disabled yes,no]: " + str(boolean))

    #------------------------------------------------------
    # CUPS ARGUMENT WRAPPER
    #------------------------------------------------------

    def check_cups(self,cups_raw):
        cups = cups_raw % 16
        if cups < 1 or cups > 12:
            raise SmarterErrorOld("Unknown coffee cups [1..12]: " + str(cups))
        return cups

    def check_cups_brew(self,cups_raw):
        cups = cups_raw % 16
        if cups < 0 or cups > 12:
            raise SmarterErrorOld("Unknown brew(ed) coffee cups [0..12]: " + str(cups))
        return cups

    def raw_to_cups_brew(self,cups_raw):
        return self.check_cups_brew(self.raw_to_number(cups_raw) / 16)


    def raw_to_cups(self,raw):
        return self.check_cups(self.raw_to_number(raw))


    def cups_to_raw(self,cups):
        return self.number_to_raw(self.check_cups(cups))

    def cupsmerged_to_raw(self,cups,cupsbrew):
        self.check_cups(cups)
        self.check_cups_brew(cupsbrew)
        return self.number_to_raw(cups + (cupsbrew * 16))
    

    def string_to_cups(self,string):
        try:
            cups = self.check_cups(int(string))
        # FIX EXCEPTION
        except Exception:
            raise SmarterErrorOld("Unknown coffee cups [1..12]: " + string)
        return cups


    def cups_to_string(self,cups):
        if cups == 1:
            return "a cup"
        else:
            return str(cups) + " cups"


    #------------------------------------------------------
    # WATERLEVEL ARGUMENT WRAPPER
    #------------------------------------------------------


    CoffeeWaterEmpty = 0x00
    CoffeeWaterLow   = 0x01
    CoffeeWaterHalf  = 0x02
    CoffeeWaterFull  = 0x03

    WaterLevel = {
        CoffeeWaterEmpty : "empty",
        CoffeeWaterLow   : "low",
        CoffeeWaterHalf  : "half",
        CoffeeWaterFull  : "full"
    }

    def waterlevel(self,level):
        if self.WaterLevel.has_key(level):
            return self.WaterLevel[level]
        else:
            return "unknown water level [0..3]: " + self.number_to_code(level)


    def check_waterlevel(self,waterlevel_raw):
        water = waterlevel_raw % 16
        if water < 0 or water > 3:
            raise SmarterErrorOld("Unknown waterlevel [0..3]: " + str(water))
        return water


    def raw_to_waterlevel(self,raw):
        return self.check_waterlevel(self.raw_to_number(raw))


    def raw_to_waterlevel_bit(self,raw):
        return self.raw_to_number(raw) / 16
    
    def waterlevel_to_raw(self,waterlevel,waterenough):
        return self.number_to_raw(waterlevel + (waterenough << 4))

   
    #------------------------------------------------------
    # COMMAND STATUS INFO WRAPPER
    #------------------------------------------------------


    StatusSucces              = 0x00
    StatusBusy                = 0x01
    StatusNoCarafe            = 0x02
    StatusNoWater             = 0x03
    StatusFailed              = 0x04
    StatusNoCarafeUnknown     = 0x05
    StatusNoWaterUnknown      = 0x06
    StatusNoWaterAborted      = 0x07
    StatusInvalidTimer        = 0x0d
    StatusErrorWifi           = 0x68
    StatusInvalid             = 0x69
 
    StatusCommand = {
        StatusSucces           : "success",
        StatusBusy             : "busy",
        StatusNoCarafe         : "no carafe",
        StatusNoWater          : "no water",
        StatusFailed           : "failed",
        StatusNoCarafeUnknown  : "no carafe",  # which one?
        StatusNoWaterUnknown   : "no water",   # which one?
        StatusNoWaterAborted   : "low water could not finish",
        StatusInvalidTimer     : "timer error",
        StatusErrorWifi        : "wifi error",
        StatusInvalid          : "invalid command"
    }


    def is_status_command(self,status):
        return self.StatusCommand.has_key(status)



    def status_command(self,status):
        if self.is_status_command(status):
            return self.StatusCommand[status]
        else:
            return "Unknown Command Status " + self.number_to_code(status)


    #------------------------------------------------------
    # KETTLE STATUS INFO WRAPPER
    #------------------------------------------------------


    KettleReady               = 0x00
    KettleHeating             = 0x01
    KettleKeepWarm            = 0x02
    KettleCycleFinished       = 0x03
    KettleFormulaCooling         = 0x04

    StatusKettle = {
        KettleReady             : "ready",
        KettleHeating           : "heating",
        KettleKeepWarm          : "keep warm",
        KettleCycleFinished     : "cycle finished",
        KettleFormulaCooling       : "baby cooling"
    }


    def status_kettle_description(self,status):
        if self.StatusKettle.has_key(status):
            return self.StatusKettle[status]
        else:
            return "Unknown Kettle Status " + self.number_to_code(status)


    def string_kettle_settings(self, temperature,  formula, formulatemperature, keepwarmtime):
        message = "Heat water to " + str(temperature) +  "ºC"
        if formula:
            sep = ""
            if keepwarmtime > 0:
                sep = ","
            else:
                sep = " and"
            message = message + sep + " let it cool down to " + self.temperature_to_string(formulatemperature)
        if keepwarmtime > 0:
            message = message + " and keep it warm for " + str(keepwarmtime) + " minutes"
        return message


    def string_kettle_status(self,onbase,kettlestatus,temperature,watersensor):
        if onbase:
            return self.status_kettle_description(kettlestatus) + " on base: temperature " + self.temperature_to_string(temperature) + ", watersensor " + str(watersensor)
        else:
            return self.status_kettle_description(kettlestatus) + " off base"


    KettleModeNormal = "normal"
    KettleModeFormula  = "formula"


    def string_to_mode(self,mode):
        s = mode.lower()
        if s == self.KettleModeFormula:
            return True
        elif s == self.KettleModeNormal:
            return False
        else:
           raise SmarterErrorOld("Unknown kettle mode ["+self.KettleModeNormal+"/"+self.KettleModeFormula+"] " + mode)


    #------------------------------------------------------
    # COFFEE STATUS INFO WRAPPER
    #------------------------------------------------------


    CoffeeStringFilter = "filter"
    CoffeeStringBeans  = "beans"

    CoffeeBeans  = True
    CoffeeFilter = False


    def coffeeStatus_to_raw(self,carafe,grind,ready,grinder,heater,hotplate,working,timer):
        return Smarter.number_to_raw((carafe << 0) + (grind << 1) + (ready << 2) + (grinder << 3) + (heater << 4) + (hotplate << 6) + (working << 5) + (timer << 7))

    def grind_to_string(self,grind):
        s = self.CoffeeStringFilter
        if grind:
            s = self.CoffeeStringBeans
        return s


    def string_to_grind(self,grind):
        s = grind.lower()
        if s == self.CoffeeStringBeans:
            return True
        elif s == self.CoffeeStringFilter:
            return False
        else:
           raise SmarterErrorOld("Unknown grind ["+self.CoffeeStringBeans+"/"+self.CoffeeStringFilter+"] " + grind)



    CoffeeCupMode = True
    CoffeeCarafeMode = False


    def string_coffee_settings(self, cups, strength, grind, hotplate):
        s = ""
        if hotplate >= 5 and hotplate <= 40:
            s = " and keep hotplate warm for " + str(hotplate) + " minutes"
        t = " " + self.grind_to_string(grind) + " coffee"
        if grind:
            t = " " + self.strength_to_string(strength) + t
        return "brew " + self.cups_to_string(cups) + " of" + t + s



    def string_coffee_status(self,ready,cups,working,heating,hotPlateOn,carafe,grinderOn):
        s = ""
        if working:
            s += "working "
        if heating:
            s += "brewing " + self.cups_to_string(cups) + " "
        if hotPlateOn:
            s += "hotplate warming "
        if grinderOn:
            s += "grinding "
        if ready:
            s += "ready "
        if carafe:
            s+= "carafe on base"
        else:
            s+= "no carafe"
        return s



    def string_coffee_bits(self,caraferequired,mode,waterenough,timerevent):
        s = ""
        if not caraferequired:
            s += ", carafe required"
        if mode:
            s += ", cup mode"
        else:
            s += ", carafe mode"
        if not waterenough:
            s += ", not enough water to brew"
        if timerevent:
            s += ", timer triggered"
        return s


    #------------------------------------------------------
    # TYPE -> TYPE
    #------------------------------------------------------

    def watersensor_to_level(self,watersensor):
        # Fix Check value's
        #   calibrate nokettlebase:       1120     measure: kettle off: 2010 kettle empty: 2070 kettle full: 2140  (div 890 950 1020)
        #   calibrate emptykettlebase:    1070     measure: kettle off: 1975 kettle empty: 2020 kettle full: 2085  (div 905 950 1015)
        #   calibrate fullkettlebase:     1010     measure: kettle off: 1875 kettle empty: 1950 kettle full: 2015  (div 865 940 1005)
        # div = measure - base
        # need temperature in calclation...
        #   1.8l
        # is this accurate??? nope...
        # sometimes if placed on base it gives wrong levels
        if isKettle:
            waterlevel = (1.800/72) * (watersensor - self.watersensorBase - 1000)
            if waterlevel < 0:
                return 0.0
            if waterlevel > 2:
                return 1.8
            else:
                return waterlevel
        elif self.isCoffee:
            return 0


    def dbm_to_quality(self,dBm):
        # takes as input a dBm string (e.g. "-23")
        # quality = 2 * (dBm + 100)  where dBm: [-100 to -50]
        # dBm = (quality / 2) - 100  where quality: [0 to 100]
        try:
            if dBm <= -100:
                return 0
            elif dBm >= -50:
                return 100
            else:
                return 2 * (dBm + 100)
        except Exception:
            raise SmarterErrorOld("Unknown Wifi signal (dBm) strength: " + str(dBm))


    def bytes_to_human(self,size_bytes):
        
        # format a size in bytes into a 'human' file size, e.g. bytes, KB, MB, GB, TB, PB
        # Note that bytes/KB will be reported in whole numbers but MB and above will have greater precision
        # e.g. 1 byte, 43 bytes, 443 KB, 4.3 MB, 4.43 GB, etc
        
        if size_bytes == 1:
            # because I really hate unnecessary plurals
            return "1 byte"

        suffixes_table = [('bytes',0),('KB',0),('MB',1),('GB',2),('TB',2), ('PB',2)]

        num = float(size_bytes)
        for suffix, precision in suffixes_table:
            if num < 1024.0:
                break
            num /= 1024.0

        if precision == 0:
            formatted_size = "%d" % num
        else:
            formatted_size = str(round(num, ndigits=precision))

        return "%s %s" % (formatted_size, suffix)


    #------------------------------------------------------
    # UDP Find Devices
    #------------------------------------------------------

    def find_devices(self,port):
        """
        Find devices using udp
        """
        devices = []
        relay = []
        try:
            cs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            cs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            cs.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            command = self.number_to_raw(self.CommandDeviceInfo) + self.number_to_raw(self.MessageTail)
            #command = '\x64\x7e'

            cs.sendto(command, ('255.255.255.255', port))
            cs.settimeout(2)

            # support up to 100 devices
            for i in range (0,100):
                message, server = cs.recvfrom(1024)
                # '0x64 type version 0x7e
                if self.raw_to_number(message[0]) == self.ResponseDeviceInfo and self.raw_to_number(message[3]) == self.MessageTail:
                    devices.append((server[0],self.raw_to_number(message[1]),self.raw_to_number(message[2])))
                if self.raw_to_number(message[0]) == self.ResponseRelayInfo:
                    relay.append((server[0],self.raw_to_number(message[1]),self.raw_to_text(message[1:])))
        except socket.error, e:
            # FIX
            pass #print 'iBrew:' + str(e)
        finally:
            cs.close()
        return devices, relay

    def print_devices_found(self,devices,relay):
        for i in range(0,len(devices)):
            s = ""
            for j in range(0,len(relay)):
                if devices[i][0] == relay[j][0]:
                    s = "Relay v" + str(relay[j][1]) + " (" + relay[j][2] + ") "
            print "[" + devices[i][0] +  ":" + '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()) + "] Found " + s + Smarter.device_info(devices[i][1],devices[i][2])
        if len(devices) == 0:
            print "No coffee machine or kettle found"


    #------------------------------------------------------
    # TRIGGERS
    #------------------------------------------------------


    # Kettle
    triggerTemperatureStable            = 7
    triggerWaterSensorStable            = 8
    triggerBusyKettle                   = 9
    triggerDefaultTemperature           = 10
    triggerDefaultFormulaTemperature    = 11
    triggerDefaultKeepWarmTime          = 12
    triggerWaterSensorBase              = 13
    triggerKeepWarm                     = 14
    triggerHeaterKettle                 = 15
    triggerFormulaCooling               = 16
    triggerTemperature                  = 17
    triggerWaterSensor                  = 18
    triggerOnBase                       = 19
    triggerUnknownKettle                = 20

    # Coffee
    triggerMode                         = 21
    triggerDefaultStrength              = 22
    triggerDefaultCups                  = 23
    triggerDefaultGrind                 = 24
    triggerDefaultHotplate              = 25
    triggerGrind                        = 26
    triggerReady                        = 27
    triggerWorking                      = 28
    triggerTimerEvent                   = 29
    triggerWaterLevel                   = 30
    triggerWaterEnough                  = 31
    triggerStrength                     = 32
    triggerCups                         = 33
    triggerCupsBrew                     = 34
    triggerUnknownCoffee                = 35
    triggerCarafe                       = 36
    triggerGrinder                      = 37
    triggerHotPlate                     = 38
    triggerHeaterCoffee                 = 39
    triggerCarafeRequired               = 40
    triggerBusyCoffee                   = 41

    
    # format {(group,sensorid,command),...(group,sensorid,command)}
    triggersKettle = {
    
        # Operational sensors (boolean)
        triggerBusyKettle                   : ["KettleBusy","STATE true if either heater or formula cooling"],
        triggerKeepWarm                     : ["KeepWarm","STATE"],
        triggerHeaterKettle                 : ["KettleHeater","STATE"],
        triggerFormulaCooling               : ["FormulaCooling","STATE"],
        triggerOnBase                       : ["OnBase","STATE"],
        
        # Data sensors
        triggerWaterSensorBase              : ["Base","NUMBER"],
        triggerDefaultKeepWarmTime          : ["DefaultKeepWarm","NUMBER"],
        triggerDefaultTemperature           : ["DefaultTemperature","NUMBER (0..100)"],
        triggerDefaultFormulaTemperature    : ["DefaultFormulaTemperature","NUMBER (0..100)"],
        triggerTemperature                  : ["TemperatureRaw","NUMBER"],
        triggerWaterSensor                  : ["WaterSensorRaw","NUMBER"],
        triggerTemperatureStable            : ["Temperature","NUMBER"],
        triggerWaterSensorStable            : ["WaterSensor","NUMBER"],
        triggerUnknownKettle                : ["KettleUnknown","NUMBER"]
    }
    
    triggersCoffee = {
        # Operational sensors (boolean)
        triggerGrinder                      : ["Grinder","STATE"],
        triggerTimerEvent                   : ["Timer","STATE"],
        triggerBusyCoffee                   : ["CoffeeBusy","STATE"],
        triggerReady                        : ["Ready","STATE"],
        triggerWorking                      : ["Working","STATE"],
        triggerHotPlate                     : ["Hotplate","STATE"],
        triggerHeaterCoffee                 : ["CoffeeHeater","STATE"],

        # Data sensors
        triggerCarafeRequired               : ["Carafe required","STATE: if carafe is needed"],
        triggerMode                         : ["Mode","STATE false is carafe mode, true is cup mode"],
        triggerGrind                        : ["Grind","STATE false is filter, true if beans"],
        triggerWaterEnough                  : ["EnoughWater","STATE if there is enough water"],
        triggerCarafe                       : ["Carafe","STATE if carafe is present"],
        triggerWaterLevel                   : ["Waterlevel","NUMBER (0..3) representing empty .. full"],
        triggerStrength                     : ["Strength","NUMBER (0..2) representing (weak,normal,strong)"],
        triggerCups                         : ["Cups","NUMBER (1..12) or (1..3) in cup mode"],
        triggerCupsBrew                     : ["CupsBrew","NUMBER"],
        triggerUnknownCoffee                : ["CoffeeUnknown","NUMBER"],
        triggerDefaultStrength              : ["DefaultStrength","NUMBER (0..2) representing (weak,normal,strong)"],
        triggerDefaultCups                  : ["DefaultCups","NUMBER (1..12)"],
        triggerDefaultGrind                 : ["DefaultGrind","STATE false is filter, true if beans"],
        triggerDefaultHotplate              : ["DefaultHotplate","NUMBER 0,5-35 minutes in v21 and below or 0,5-40 minutes in v22"]
    }

    def triggerID(self,trigger):
        for i in self.triggersCoffee.keys():
            if trigger.upper() == self.triggersCoffee[i][0].upper():
                return i
        for i in self.triggersKettle.keys():
            if trigger.upper() == self.triggersKettle[i][0].upper():
                return i
        raise SmarterErrorOld("Trigger does not exists")


    def triggerName(self,trigger):
        if trigger in self.triggersKettle:
            return self.triggersKettle[trigger][0].upper()
        if trigger in self.triggersCoffee:
            return self.triggersCoffee[trigger][0].upper()
        raise SmarterErrorOld("Trigger does not exists")

    def triggerDescription(self,trigger):
        if trigger in self.triggersKettle:
            return self.triggersKettle[trigger][1]
        if trigger in self.triggersCoffee:
            return self.triggersCoffee[trigger][1]
        raise SmarterErrorOld("Trigger does not exists")


    triggerBooleans = [("ON","OFF"),("On","Off"),("on","off"),("1","0"),("TRUE","FALSE"),("True","False"),("true","false"),("ENABLED","DISABLED"),("Enabled,Disabled"),("enabled","disabled")]
    
    
    def triggerCheckBooleans(self,boolean):
        try:
            self.string_to_bool(boolean)
        except:
            SmarterErrorOld("Trigger state not recognized")
        for i in self.triggerBooleans:
            if i[0] == boolean or i[1] == boolean:
                return i
        

    def print_triggers(self):
        print
        print "Trigger actions"
        print
        print "Smarter Coffee Trigger".rjust(25, ' ') + " Sensor Description"
        print "______________________".rjust(25, ' ') + "___________________"
        for i in self.triggersCoffee:
            print self.triggersCoffee[i][0].upper().rjust(25, ' ') + " " + self.triggersCoffee[i][1]
        print
        print "iKettle 2.0 Trigger".rjust(25, ' ') + " Sensor Description"
        print "___________________".rjust(25, ' ') + "___________________"
        for i in self.triggersKettle:
            print self.triggersKettle[i][0].upper().rjust(25, ' ') + " " + self.triggersKettle[i][1]
        print


    def print_states(self):
        print
        print "State types for trigger actions"
        print
        for i in self.triggerBooleans:
            print i[0] + ": (" + i[0] + "," + i[1] + ")"
        print
        
    #------------------------------------------------------
    #
    # Protocol Information
    #
    # kinda a real, mess ;-)
    #------------------------------------------------------



    
    # merge and payload not finished...

    ArgCups       = 1000
    ArgStrength   = 1001
    ArgPassword   = 1002
    ArgSSID       = 1003
    ArgGrind      = 1004
    ArgTemperature= 1005
    ArgKeepWarm   = 1006
    ArgHotPlate   = 1007
    ArgFormulaTemperature= 1008
    ArgCommandStatus= 1009
    ArgFormula      = 1010
    ArgOffBase      = 1011
    ArgState        = 1012
    ArgMinute       = 1013
    ArgHour         = 1014
    ArgDay          = 1015
    ArgMonth        = 1016
    ArgSecond       = 1017
    ArgCentury      = 1020
    ArgHotPlateOn   = 1021
    ArgYear         = 1018
    ArgUnknown      = 1019
    ArgKettleStatus = 1022
    ArgVersion      = 1024
    ArgDevice       = 1025
    ArgWaterSensorLo= 1034
    ArgWaterSensorHi= 1035
    ArgIndex        = 1036
    ArgRequired     = 1037
    ArgMode    = 1038
    ArgCounter      = 1027
    ArgDB           = 1032
    ArgCoffeeStatus = 1023
    ArgWaterLevel   = 1040
    ArgWaterEnough  = 1041
    ArgWaterLevelRaw= 1048
    ArgCupsCombi    = 1049
    ArgWorking      = 1042
    ArgHeater       = 1043
    ArgReady        = 1044
    ArgGrinder      = 1047
    ArgCarafe       = 1046
    ArgTimerEvent   = 1045
    ArgCupsBrew     = 1050
    ArgKeepWarmOn   = 1051
    ArgKeepWarmCombi= 1054
    ArgTemperatureCombi= 1052
    ArgHotplateCombi   = 1053
    ArgWifiFirmware    = 1055

    ArgRelayVersion   = 1056
    ArgRelayHost = 1057
    ArgRelayModifiers = 1058

    ArgPayloadTimer            = 1026
    ArgPayloadCoffeeHistory    = 1028
    ArgPayloadKettleHistory    = 1029
    ArgPayloadWifiScan         = 1039
    ArgWater  = 1033
    
    # NOT ADDED
    ArgSubList        = 1030
    ArgList           = 1031
    ArgValueOther = -1
    
    # ArgIndex needs combines with 0 index...???
    
    
    ArgType = {
        ResponseWirelessNetworks    : ('PROTOCOL',[ArgPayloadWifiScan],"416972476c6f772c2d38347d486f6d65576966692c2d37327d54502d4c494e4b5f3344443245362c2d39337d","List containing the wireless networks found with scanning"),
        ResponseKettleHistory       : ('PROTOCOL',[ArgPayloadKettleHistory],"020164000006001927250c1901000000000000000000000000000000000000007d\n015f000001001902260c1901000000000000000000000000000000000000007d",""),
        ResponseTimers              : ('PROTOCOL',[ArgCounter,ArgPayloadTimer],"000f0f01010114147d01030701010114137d01020501010114127d01010101010114117d",""),
        ResponseCoffeeHistory       : ('PROTOCOL',[ArgCounter,ArgPayloadCoffeeHistory],"03010000020200000b01010000000000000000000000000000000000000000007d\n010000020200012001010000000000000000000000000000000000000000007d\n010010010101000401010014000000000000000000000000000000000000007d",""),
        ResponseBase                : ('PROTOCOL',[ArgWater],"044c","Calibration base value, the base value in relation to the watersensor and temperature is unknown"),

        ArgPayloadTimer             : ('PAYLOAD',"PAYLOADTIMER",MessagePayloadTail,[]),
        ArgPayloadCoffeeHistory     : ('PAYLOAD',"PAYLOADHISTORYKETTLE",MessagePayloadTail,[]),
        ArgPayloadKettleHistory     : ('PAYLOAD',"PAYLOADHISTORYCOFFEE",MessagePayloadTail,[]),
        ArgPayloadWifiScan          : ('PAYLOAD',"PAYLOADWIFI",MessagePayloadTail,[]),
        
        ArgSubList                  : ('PAYLOAD',"TUPLE",",",[]),
        ArgList                     : ('PAYLOAD',"LIST","}",[]),


        ResponseRelayInfo          : ('PROTOCOL',[ArgRelayVersion,ArgRelayHost],"0131302e302e302e3939","Get the version of the firmware of relay connected to (if connected) It is used for auto discovery over UDP broadcast by iBrew. This fails on some routers, which don't propagate UDP broadcasts."),

        ResponseRelayModifiersInfo          : ('PROTOCOL',[ArgRelayModifiers],"","[in:|out:|mod]rule(,[in:|out:|mod:]rule)* where rule: message id, group name or in: and out: and rule is a patch for mod:"),

        ResponseCarafe              : ('PROTOCOL',[ArgCarafe],"00",""),
        ResponseMode       : ('PROTOCOL',[ArgMode],"01",""),
        ResponseCommandStatus       : ('PROTOCOL',[ArgCommandStatus],"04",""),
        ResponseDeviceInfo          : ('PROTOCOL',[ArgDevice,ArgVersion],"0113","Get the type of the appliance connected to and it's firmware. It is used for auto discovery over UDP broadcast. This fails on some routers, which don't propagate UDP broadcasts."),
        ResponseWifiFirmware        : ('PROTOCOL',[ArgWifiFirmware],"41542b474d525c6e41542076657273696f6e3a302e34302e302e302841756720203820323031352031343a34353a3538295c6e53444b2076657273696f6e3a312e332e305c6e636f6d70696c652074696d653a41756720203820323031352031373a31393a33385c6e4f4b5c6e",""),
        ResponseCoffeeSettings      : ('PROTOCOL',[ArgStrength,ArgCups,ArgGrind,ArgHotPlate],"01020005",""),
        ResponseCoffeeStatus        : ('PROTOCOL',[ArgCoffeeStatus,ArgWaterLevelRaw,ArgUnknown,ArgStrength,ArgCupsCombi],"0500000021",""),
        ResponseKettleStatus        : ('PROTOCOL',[ArgKettleStatus,ArgTemperatureCombi,ArgWater,ArgUnknown],"007f07d700",""),
        ResponseKettleSettings      : ('PROTOCOL',[ArgTemperature,ArgKeepWarmCombi,ArgFormulaTemperature],"641400","It sends a 0 between this response and the command status succes. (BUG)"),
        CommandDeviceTime           : ('PROTOCOL',[ArgSecond,ArgMinute,ArgHour,ArgUnknown,ArgDay,ArgMonth,ArgCentury,ArgYear],"1213030105021410",
                                        "Set the time on the appliance, is used in history and in the coffee scheduled timers messages. Unknown is Day of week index?"),
        CommandResetSettings        : ('PROTOCOL',[],"","For the kettle these are the default user settings: keepwarm 0 minutes, temperature 100ºC, formula mode off and formula temperature 75ºC. The Smarter Coffee does nothing."),
    
        CommandDeviceInfo           : ('PROTOCOL',[],"",""),
        CommandRelayInfo            : ('PROTOCOL',[],"",""),
        CommandRelayModifiersInfo       : ('PROTOCOL',[],"",""),
        CommandRelayBlock           : ('PROTOCOL',[ArgRelayModifiers],"","[in:|out:]rule(,[in:|out:]rule)* where rule: message id, group name"),
        CommandRelayUnblock         : ('PROTOCOL',[ArgRelayModifiers],"","[in:|out:]rule(,[in:|out:]rule)* where rule: message id, group name"),
        CommandRelayPatch           : ('PROTOCOL',[ArgRelayModifiers],"","[mod:]rule(,[mod:]rule)* where rule is a patch"),

        CommandUpdate               : ('PROTOCOL',[],"","Disables wifi and creates a 'iKettle Update' wireless network and opens port 6000. A hard appliance reset (hold power button for 10 seconds) is sometimes required to fix this state, or just unplug the power for a moment."),
        Command69                   : ('PROTOCOL',[ArgUnknown],"00",""),  #REPEAT?

    # wifi
        CommandWifiNetwork          : ('PROTOCOL',[ArgSSID],"416363657373506f696e74",""),
        CommandWifiPassword         : ('PROTOCOL',[ArgPassword],"7040737377307264",""),
        CommandWifiJoin             : ('PROTOCOL',[],"","Sending this command without previous SSID/password commands will reset it to direct mode. Do not wait between sending the network name, the password and the join command, or else it will fail to join the wireless network. The apps actually sends: 0c7e000000000000."),
        CommandWifiScan             : ('PROTOCOL',[],"",""),
        CommandWifiLeave            : ('PROTOCOL',[],"","Leaves wireless network and reset wifi to direct mode. The app also send a firmware update command."),
        CommandWifiFirmware         : ('PROTOCOL',[],"","The firmware of the wifi module is in text, with control chars as new line."),

        # coffee
        CommandBrew                 : ('PROTOCOL',[ArgCups,ArgStrength,ArgHotplateCombi,ArgGrind],"04020001",""),
        CommandCoffeeStop           : ('PROTOCOL',[],"",""),
        CommandStrength             : ('PROTOCOL',[ArgStrength],"01","Sets the strength of the coffee to be brewed. Use command 37 to brew."),
        CommandCups                 : ('PROTOCOL',[ArgCups],"03","Select the number of cups to be brewed. Use command 37 to brew."),
        CommandBrewDefault          : ('PROTOCOL',[],"","Uses the settings not the default user settings."),
        CommandCoffeeSettings       : ('PROTOCOL',[ArgCups,ArgStrength,ArgGrind,ArgHotplateCombi],"03010100","Also return 00 message in an unconfigured state.??? CHECK"),
        CommandCoffeeStoreSettings  : ('PROTOCOL',[ArgStrength,ArgCups,ArgGrind,ArgHotplateCombi],"02050010",""),
        CommandGrinder              : ('PROTOCOL',[],"",""),
        CommandHotplateOn           : ('PROTOCOL',[ArgHotPlate],"05","Sets on the hotplate, you can specify how many minutes before it switch off. Argument is optional. If no value it uses the stored user default settings. "),
        CommandCoffeeHistory        : ('PROTOCOL',[],"","When called will erase this history."),
        CommandHotplateOff          : ('PROTOCOL',[],"",""),
        CommandCarafe               : ('PROTOCOL',[],"",""),
        CommandSetCarafe            : ('PROTOCOL',[ArgCarafe],"00",""),
        CommandMode                 : ('PROTOCOL',[],"",""),
        CommandSetMode              : ('PROTOCOL',[ArgMode],"01",""),
        CommandStoreTimer           : ('PROTOCOL',[ArgIndex,ArgMinute,ArgHour,ArgUnknown,ArgDay,ArgMonth,ArgCentury,ArgYear],"0401010101011411","Store time in timer schedule"),
        CommandTimers               : ('PROTOCOL',[ArgIndex],"00","Get scheduled timers. If index is not all timers it gets the first timer to go off."),
        CommandDisableTimer         : ('PROTOCOL',[ArgIndex],"00","Clear time event bit in timers schedule??? It beeps that's all then it brews, it needs investigating..."),
     
        # kettle
        CommandHeat                 : ('PROTOCOL',[ArgTemperature,ArgKeepWarmCombi],"3210",""),
        CommandKettleStop           : ('PROTOCOL',[],"",""),
        CommandHeatFormula          : ('PROTOCOL',[ArgFormulaTemperature,ArgKeepWarmCombi],"3219","Heats water to (default user temperature) and cool until the formula temperature and then keep it warm."),
        CommandHeatDefault          : ('PROTOCOL',[],"","Check arguments with wireshark"),
        Command20                   : ('PROTOCOL',[],"","This setting ignores the user setting and heats untill the tempeature is 100ºC"),
        Command22                   : ('PROTOCOL',[],"",""),
        Command23                   : ('PROTOCOL',[],"",""),
        Command30                   : ('PROTOCOL',[ArgUnknown],"",""),
        CommandKettleStoreSettings  : ('PROTOCOL',[ArgKeepWarmCombi,ArgTemperature,ArgFormula,ArgFormulaTemperature],"1f196401227e","Default user defaults message is [1f0064004b7e]. I think the correct message in v18 is without formula, since that value can take values up to 100 and nothing is returned for the 4th value. <[FORMULA]>, I think this is a bug in smarter ios app."),
        CommandKettleHistory        : ('PROTOCOL',[],"","When called will erase this history."),
        CommandKettleSettings       : ('PROTOCOL',[],"","Also return 00 message in an unconfigured state.??? CHECK"),
        CommandStoreBase            : ('PROTOCOL',[ArgWater],"044c",""),
        CommandBase                 : ('PROTOCOL',[],"",""),
        CommandCalibrate            : ('PROTOCOL',[],"","Calibrates the base, only do this when the kettle is off base"),
 
 
        ArgWorking        : ('OPTION',"Working",[(0,"?"),(1,"?")]),
        ArgReady          : ('OPTION',"Ready",[(0,"Ready to brew"),(1,"Busy")]),
        ArgGrinder        : ('OPTION',"Grinder",[(0,"Grinder on"),(1,"Hotplate off")]),
        ArgCarafe         : ('OPTION',"Carafe",[(0,"Carafe on base"),(1,"Carafe off base or door open")]),
        ArgTimerEvent     : ('OPTION',"Timer",[(0,"Timer event tiggered"),(1,"No timer event")]),
        ArgHeater         : ('OPTION',"Heater",[(0,"Heater on"),(1,"Heater off")]),
        ArgWaterEnough    : ('OPTION',"WaterEnough",[(0,"Not enough to brew with this cups settings"),(1,"Enough water to brew  (WATERLEVEL*0.25*2)/CUPS)")]),
        ArgWaterLevel     : ('OPTION',"WaterLevel",[(CoffeeWaterEmpty,WaterLevel[CoffeeWaterEmpty]),
                                    (CoffeeWaterLow,WaterLevel[CoffeeWaterLow]),
                                    (CoffeeWaterHalf,WaterLevel[CoffeeWaterHalf]),
                                    (CoffeeWaterFull,WaterLevel[CoffeeWaterFull])]),
        ArgCoffeeStatus   : ('BIT',"CoffeeStatus",[(0,1,ArgCarafe),(1,1,ArgGrind),(2,1,ArgReady),(3,1,ArgGrinder),
                                                        (4,1,ArgHeater),(5,1,ArgWorking),(6,1,ArgHotPlateOn),(7,1,ArgTimerEvent)]),
        ArgWaterLevelRaw  : ('BIT',"WaterLevelAndEnough",[(0,4,ArgWaterLevel),(4,1,ArgWaterEnough)]),
        ArgCups           : ('NUMBER',"Cups",(1,12),"number of cups selected [1..12]"),
        ArgCupsBrew       : ('NUMBER',"CupsBrew",(1,12),"number of cups brew(ed) [1..12]"),
        ArgCupsCombi      : ('BIT',"CupsSettingAndBrew",[(0,4,ArgCups),(4,4,ArgCupsBrew)]),


        ArgWaterSensorHi     : ('NUMBER',"WaterSensorHigh",(0,16),""),
        ArgWaterSensorLo     : ('NUMBER',"WaterSensorLow",(0,255),""),
        ArgCounter           : ('NUMBER',"Counter",(0,8),""),
        ArgMinute            : ('NUMBER',"Minute",(0,60),""),
        ArgSecond            : ('NUMBER',"Second",(0,60),""),
        ArgHour              : ('NUMBER',"Hour",(0,24),""),
        ArgDay               : ('NUMBER',"Day",(1,32),""),
        ArgIndex             : ('OPTION',"Index",[
                                    (TimerAll,Timer[TimerAll]),
                                    (Timer1,Timer[Timer1]),
                                    (Timer2,Timer[Timer2]),
                                    (Timer3,Timer[Timer3]),
                                    (Timer4,Timer[Timer4])
                                ]
                              ),
        ArgMonth             : ('NUMBER',"Month",(1,12),""),
        ArgYear              : ('NUMBER',"Year",(0,99),""),
        ArgCentury           : ('NUMBER',"Century",(19,21),""),
        ArgUnknown           : ('NUMBER',"Unknown",(0,255),"Unknown number"),
        ArgVersion           : ('OPTION',"Version",[(18,"iKettle 2.0"),
                                    (20,DeviceStringCoffee),
                                    (22,DeviceStringCoffee),
                                    (19,DeviceStringKettle)
                                    ]
                              ),
        ArgRelayVersion      : ('OPTION',"Version",[(1,"iBrew Relay Snow Tea")
                                    ]
                              ),
        ArgDevice            : ('OPTION',"Appliance",[(DeviceCoffee,DeviceStringCoffee),(DeviceKettle,DeviceStringKettle)]),
        ArgKettleStatus      : ('OPTION',"KettleStatus",[
                                (KettleReady, StatusKettle[KettleReady]),
                                (KettleHeating, StatusKettle[KettleHeating]),
                                (KettleKeepWarm, StatusKettle[KettleKeepWarm]),
                                (KettleCycleFinished, StatusKettle[KettleCycleFinished]),
                                (KettleFormulaCooling, StatusKettle[KettleFormulaCooling])
                            ]),
        ArgTemperature        : ('NUMBER',"Temperature",(0,100),"temperature in celcius [0ºC..100ºC]"),
        ArgFormulaTemperature : ('NUMBER',"FormulaTemperature",(0,100),"formula temperature in celcius [0ºC..100ºC]"),
        ArgKeepWarm           : ('NUMBER',"Keepwarm",(5,35),"kettle keep warm time in minutes [5..35]"),
        ArgKeepWarmOn         : ('OPTION',"KeepwarmOn",[(0,"Keepwarm off"),(1,"Keepwarm on")]),

        ArgHotPlate           : ('NUMBER',"Hotplate",(5,30),"hotplate keep warm time in minutes [5..30]"),
        ArgFormula            : ('OPTION',"Formula",[(0,"Disabled"),(1,"Enabled")]),
        ArgOffBase            : ('OPTION',"Base",[(0,"Kettle on base"),(MessageOffBase,"Kettle off base")]),
        ArgRequired           : ('OPTION',"Required",[(0,"Carafe Required"),(1,"Can brew without carafe")]),
        ArgMode          : ('OPTION',"Mode",[(0,"Carafe mode"),(1,"Cup mode")]),

        ArgHotPlateOn         : ('OPTION',"HotplateOn",[(0,"Hotplate on"),(1,"Hotplate off")]),

        ArgState              : ('OPTION',"State",[(0,"Failed"),(1,"Succes")]),
        ArgStrength       : ('OPTION',"Strength",[(CoffeeWeak,CoffeeStringWeak),
                                    (CoffeeMedium,CoffeeStringMedium),
                                    (CoffeeStrong,CoffeeStringStrong)]
                            ),
        ArgPassword       : ('TEXT',"Password","wireless network password"),
        ArgRelayHost      : ('TEXT',"Host","Host of the appliance connected with the relay, empty if not connected"),
        ArgRelayModifiers     : ('TEXT',"Block","FIX"),
        ArgDB             : ('TEXT',"DB","in dBm"),
        ArgWifiFirmware   : ('TEXT',"WifiFirmware","wifi firmware string"),
        ArgSSID           : ('TEXT',"SSID","wireless network name"),
        ArgGrind          : ('OPTION',"Grind",[(CoffeeFilter,CoffeeStringFilter),(CoffeeBeans,CoffeeStringBeans)]),
       
       
        ArgKeepWarmCombi    : ('RANGE',"KeepWarmMerged",ArgKeepWarm,ArgKeepWarmOn,0),
        ArgHotplateCombi    : ('RANGE',"HotplateMerged",ArgHotPlate,ArgHotPlateOn,0),
        ArgTemperatureCombi : ('RANGE',"TemperatureMerged",ArgTemperature,ArgOffBase,MessageOffBase),
        ArgWater            : ('INT',"WaterSensor",ArgWaterSensorHi,ArgWaterSensorLo),
       
        ArgCommandStatus  : ('OPTION',"CommandStatus",[
                            (StatusSucces,StatusCommand[StatusSucces]),
                            (StatusBusy,StatusCommand[StatusBusy]),
                            (StatusNoCarafe,StatusCommand[StatusNoCarafe]),
                            (StatusNoWater,StatusCommand[StatusNoWater]),
                            (StatusFailed,StatusCommand[StatusFailed]),
                            (StatusNoCarafeUnknown,StatusCommand[StatusNoCarafeUnknown]),
                            (StatusNoWaterUnknown,StatusCommand[StatusNoWaterUnknown]),
                            (StatusNoWaterAborted,StatusCommand[StatusNoWaterAborted]),
                            (StatusInvalidTimer,StatusCommand[StatusInvalidTimer]),
                            (StatusInvalid,StatusCommand[StatusInvalid])

                            ])
    }
    

    def message_example(self,id):
        return self.number_to_code(id) + self.ArgType[id][2] + self.number_to_code(self.MessageTail)

    def message_notes(self,id):
        return self.ArgType[id][3]

    # nice printab;e protocol info...
    

    def argument_messages(self,id):
        d = []
        for b in self.ArgType:
            if self.ArgType[b][0] == 'PROTOCOL':
                if id in self.ArgType[b][1]:
                    d += [b]
        return d

    
    def message_arguments(self,id):
        a = list()
        for b in self.ArgType[id][1]:
            a += [(b,self.ArgType[b][1].upper())]
        return a
        
        
    def message_protocol_arguments(self):
        a = list()
        for b in self.ArgType:
            if self.ArgType[b][0] == "PROTOCOL":
                a += self.ArgType[b][1]
    
        z = list()
        for x in a:
            
            z += [(x,self.ArgType[x][1])]
        z = set(z)
        a = list(z)
        z = sorted(a, key=lambda tup: tup[1])

        return [item[0] for item in z]

    #------------------------------------------------------
    #
    # Protocol Information Printers
    #
    # kinda a real, mess ;-)
    #------------------------------------------------------

    def string_int(self,argument):
        s = ""
        s += "    <" + self.ArgType[argument[2]][1].upper() + ">" + " + "
        s += "<" + self.ArgType[argument[3]][1].upper() + ">" + "\n"
        s += self.string_argument(argument[2])
        s +=  self.string_argument(argument[3])
        return s


    def string_option(self,argument):
        s = ""
        for (x,y) in argument[2]:
                s += "  " + self.number_to_code(x).rjust(4, ' ') + "        " + y + "\n"
        return s + ""
    
    def string_combined(self,argument):
        s = ""
        for (x,y,z) in argument[2]:
            if y == 1:
                range = " bit " + str(x)
            if y > 1:
                range = "bits " + str(x) + ".." + str(x+y-1)
            s += ("    " + range).ljust(13, ' ') + " “" + self.ArgType[z][1].upper() + "”\n"
        for (x,y,z) in argument[2]:
            s += self.string_argument(z,True)
        return s + ""
            

    def string_range(self,argument):
        s = ""
        s += ("    Merged byte <" + self.ArgType[argument[2]][1].upper() + ">").ljust(15, ' ')  + "<"
        s += self.ArgType[argument[3]][1].upper() + ">"  + "\n"
        s += self.string_argument(argument[2])
        s += self.string_argument(argument[3])
        return s + ""
 
    def string_text(self,argument):
            return "    TEXT      " + argument[2] + "\n"

    def string_protocol(self,argument,id):
        
        s = ""
        s += "\n"
        s += "  " + self.message_is_type(id) + " Message " + self.number_to_code(id) + ": " + self.message_description(id) + "\n"
        s +=  "  ─────────────────────────────────────────────────────────────────────────\n"
        d = ""
        if self.message_is_known(id):
            for i, iid in enumerate(self.message_connection(id)):
                d = d + "[" + self.number_to_code(iid) + "," + self.message_description(iid) + "] "
            if self.message_connection(id):
                if self.message_is_response(id):
                    s += "  Response to command messages: " + d + "\n"
                elif self.message_is_command(id):
                    s += "  Response messages: " + d + "\n"
            s += "\n  " + self.message_kettle_supported(id) + " " + self.DeviceStringKettle +  " " + self.message_coffee_supported(id) + " " + self.DeviceStringCoffee + "\n"
            if self.message_is_response(id) or self.message_is_status(id):
                length = self.message_response_length(id)
                if length > 0:
                    s += "\n  Message size: " + str(length) + " bytes\n"
            
        if argument[3] != "":
            s += "\n  " + argument[3] + "\n"
        
        if len(argument[1]) != 0:
            
            s += "\n\n  Arguments: "
            
            for a in argument[1]:
                s += "<" + self.ArgType[a][1].upper() + ">"
            s += "\n"
            for a in argument[1]:
                s += "\n" + self.string_argument(a)


    
        s += "\n\n  Example: [" + self.number_to_code(id) + argument[2] + self.number_to_code(self.MessageTail) + "]"
        return s + "\n\n"

    def string_number(self,argument):
        return "    " + self.number_to_code(argument[2][0]) + ".." + self.number_to_code(argument[2][1]) + "    " + argument[3] + "\n"

    
    def string_argument(self,argument,bit=False):
        if self.ArgType.has_key(argument):
            s = ""
            a = self.ArgType[argument]
            if a[0] == 'PROTOCOL':
                return self.string_protocol(a,argument)
        
            if bit:
                s += "\n  “" + a[1].upper() + "”\n"
            else:
                s += "\n  <" + a[1].upper() + ">\n"
            if a[0] == 'OPTION':
                s += ""
                s += self.string_option(a)
            elif a[0] == 'TEXT':
                s += self.string_text(a)
            elif a[0] == 'NUMBER':
                s += self.string_number(a)
            elif a[0] == 'BIT':
                s += self.string_combined(a)
            elif a[0] == 'INT':
                s += self.string_int(a)
            elif a[0] == 'RANGE':
                s += self.string_range(a)
            else:
                print "AAAAARRGGHHH"
            
        else:
            s = "No information on: " + self.number_to_code(argument)
        return s + ""


    def groups(self):
        s = "\n"
        s += "  Groups\n"
        s += "  ___________________________________________\n"
        
 
        # i really hate python....
        for g in sorted(self.Groups.items(),key=itemgetter(1)):
            s += "  " + g[1][0].upper() + "\n"
        s += "\n"
        return s


    def group(self,group):
        
        s = "\n"
        s += "  Group: " + Smarter.group_to_string(group).upper() + "\n\n"
        s += "    ID  Message Description\n"
        s += "    ___________________________________________\n"
        
        for id in sorted(self.Groups[group][1]):
            s += "    " + Smarter.number_to_code(id) + " " + Smarter.message_description(id) + "\n"
        return s + "\n"
        
    def groups_all(self):
        s = ""
        for g in sorted(self.Groups.items(),key=itemgetter(1)):
            s += self.group(g[0])
        return s
        
    def messages_all(self):
        s = ""
        for id in range(0,255):
            if self.message_is_known(id):
                s += self.string_argument(id)
        return s


    def message(self,id):
        return self.string_argument(id)


    def messages(self,coffee=True,kettle=True):
        s = ""
        if coffee:

            s +=  "\n\n    ID Coffee Machine Command Message\n"
            s +=  "    ___________________________________________\n"
            for id in range(0,255):
                if Smarter.message_is_command(id) and Smarter.message_coffee(id): # and not Smarter.message_kettle(id):
                    s +=  "    " + Smarter.number_to_code(id) + " " + Smarter.message_description(id) + "\n"

            s +=  "\n    ID Coffee Machine Response Message\n"
            s +=  "    ___________________________________________\n"
            for id in range(0,255):
                if Smarter.message_is_response(id) and Smarter.message_coffee(id): # and not Smarter.message_kettle(id):
                    s += "    " + Smarter.number_to_code(id) + " " + Smarter.message_description(id) + "\n"

            s += "\n    ID Coffee Machine Status Message\n"
            s += "    ___________________________________________\n"
            for id in range(0,255):
                if Smarter.message_is_status(id) and Smarter.message_coffee(id):
                    s +=  "    " + Smarter.number_to_code(id) + " " + Smarter.message_description(id) + "\n"

        if kettle:

            s += "\n\n    ID Kettle Command Message\n"
            s += "    ___________________________________________\n"
            for id in range(0,255):
                if Smarter.message_is_command(id) and Smarter.message_kettle(id):
                    s += "    " + Smarter.number_to_code(id) + " " + Smarter.message_description(id) + "\n"

            s += "\n    ID Kettle Response Message\n"
            s += "    ___________________________________________\n"
            for id in range(0,255):
                if Smarter.message_is_response(id) and Smarter.message_kettle(id):
                    s +=  "    " + Smarter.number_to_code(id) + " " + Smarter.message_description(id) + "\n"


            s +=  "\n    ID Kettle Status Message\n"
            s +=  "    ___________________________________________\n"
            for id in range(0,255):
                if Smarter.message_is_status(id) and Smarter.message_kettle(id):
                    s +=  "    " + Smarter.number_to_code(id) + " " + Smarter.message_description(id) + "\n"

        return s + "\n"

    def protocol(self):
        return self.structure() + self.groups() + self.messages() + self.all() + self.notes()

    def structure(self):
        return """
       
       
  Smarter iKettle 2.0 & Smarter Coffee  Protocol
  _____________________________________________

    Smarter uses a binary message protocol

    Messages use the syntax:

     <ID>[ARGUMENTS]<TAIL>

    Payloads use the syntax
    
      ([ARGUMENTS]<PAYLOADTAIL>){0..*}

    Arguments use this syntax:

      <ARGUMENT>     is a single mandatory byte
      <[ARGUMENT]>   is a single optional byte
      <ARGUMENT>{x}  is mandatory, between 1 and x bytes
      ''             is a single bit
      
    The tail is always 7e or ~ in ASCII, everything else are ASCII literals
    The tail payload is always 7d or } in ASCII, everything else are ASCII literals
    
    There are some value's like the watersensor that can contains the tail
    so check the length of the response message!
    
               """
    
    def notes(self):
        return """


  Smarter iKettle 2.0 & Smarter Coffee  Notes
  __________________________________________
    
  WaterSensor Calibration:

    If the kettle is on the base during calibration, the numbers change to be higher,
    but the differences between levels seem the same. This means that the water level
    detection is probably weight based and that calibration is done at the base,
    which then remembers the weight for \'off base\'. To detect an empty kettle,
    the connecting client must account for the weight of the kettle. Also the weight of
    the kettle is more to the handle, that why you have to choose between left and right
    handle use, it gives different results.
    
    (yeah, not! the watersensor becomes higher if the temperature becomes higher...)


  Wireless Network:

    If the appliance is configured to access a wifi access point which is not available
    It will try to connect to it every so minutes. If it tries to connect it beeps three
    times the wifi access point of the appliance will remain active but unreachable,
    if it fails to access the access point it beeps once, and it opens up its own default
    open unencrypted wifi access point.access

    If connected to the kettle tcp 192.168.4.1:2081 is the default connection.

    The iKettle 2.0 creates an access point with the name iKettle 2.0:c0 where c0 is part
    of the mac address of the kettle. When connected directly to the kettle its connection is very flacky.


  Appliance Detection:
  
    To detect a appliance, broadcast an appliance info command (message 64) on UDP. It will reply
    if the router permits it with an appliance info response (message 65) and being UDP
    with its IP address!
    
    
  Capturing the protocol using WireShark:

     OSX:  (Home Network Only)
           Step 1: Download wireshark (https://www.wireshark.org/) for mac and install it.
           Step 2: Setup your kettle or coffee machine to use your home network.
           Step 3: Connect you mac to your network NOT using the build in wifi adapter.
                   Use either a cable (ethernet recommended) or a second wifi adapter.
           Step 4: Enable and setup internet sharing in system preferences, sharing.
           Step 5: Connect with your phone to the internet sharing wireless access point.
           Step 6: Run wiresharp it and select your build in wifi adapter and start the capture.
           Step 7: Look for connection with messages ending in 7e

    iOS & OSX: (Home network & Direct mode)
           Step 1: Connect your iOS device to your Mac via USB.
           Step 2: Get the <udid> for the connected device from iTunes (click on the serial).
           Step 3: Open terminal in your Mac and run the following commands, which creates a virtual network
                   adapter mirroring the iOS network, which we can dump and inspect:
           Step 4: rvictl -s <udid>
           Step 5: tcpdump -i rvi0 -w ~/Desktop/output.pcap
           Step 6: Connect to kettle's wifi network (or your home network if already setup) on the iOS device.
           Step 7: Run setup for smarter appliance setup, or any commands
           Step 8: When done, or the appliance setup disconnected to switch to your home network, disconnect with ctrl-c
           Step 9: rvictl -x <udid>
           Step A: Download wireshark (https://www.wireshark.org/) for mac and install it.
           Stap B: Open ~/Desktop/output.pcap with Wireshark
           Step C: Look for connection with messages ending in 7e
 

  Security:

    iKettle 2.0:
         *  It will heat up empty, making the lights bulbs to flikker.
         *  You can easily knock out it's connection to the wireless network,
            if it fails to connect it creates an default open unencrypted wifi access point 
            (check!, could be that wifi was not connecting, then this is rubbish ;-) (FIX).

            Attack Vectors
            1. Repeat sending heat to 100ºC temperature commands, if we're lucky
               there is no water and it will heat up empty, if not it will take a while.
               plus the kettle will get warmer and warmer. If you do not expect that when touching.
            2. Alternating heat and stop commands.
            3. (Check) Wait until the owner of the kettle log in on the kettle, since its an
               open access point and the password are send in the open you can read it.
            4. Repeat scan for wifi commands, it will crash the wifi esp module.


  Water Heating:
  
    From smarter website the temperature that can be set is between 20 and 100. We still need to read lower 
    values for cold water in the kettle. This should be tested (FIX)
     
 
               """

    def license(self):
        return """
Copyright (c) 2016, Tristan Crispijn
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. You may not use source, binary forms or derivative work, with or without modification, for commercial purposes. 

4. Written consent of the iBrew creator Tristan Crispijn with original authentic signature on paper.


THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. YOU AGREE TO NOT USE THIS SOFTWARE IN ANY WAY. SMARTER EMPLOYEES OR SMARTER AFFILIATED PEOPLE ARE NOT ALLOWED TO USE THIS SOFTWARE OR DERIVATIVE WORK. YOU AGREE THAT THE SOFTWARE CAN MONITOR THE USAGE OF THE SOFTWARE ITSELF AND OR THE APPLIANCES ATTACHED TO THE SOFTWARE, AND SEND IT BACK TO A MONITOR SERVER FOR BETTER SUPPORT. ENJOY!
               """

Smarter = SmarterProtocol()
SmarterLegacy = SmarterProtocolLegacy()
