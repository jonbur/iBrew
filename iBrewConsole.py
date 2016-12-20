# -*- coding: utf-8 -*-

import sys
import time
import datetime
import logging

import locale
import platform
import codecs

import logging.handlers

from smarter.SmarterInterface import *
from smarter.SmarterProtocol import *

from iBrewWeb import *
from iBrewJokes import *
from iBrewFolders import AppFolders

import re
import random

import traceback

#------------------------------------------------------
# iBrew
#
# Console interface to Smarter Appliances
#
# https://github.com/Tristan79/iBrew
#
# Copyright © 2017 Tristan (@monkeycat.nl). All Rights Reserved
#
# The Dream Tea
#------------------------------------------------------



#------------------------------------------------------
# iBrew VERSION INFORMATION
#------------------------------------------------------


iBrewApp          = "iBrew - Smarter Appliances Interface"
iBrewInfo         = "The Dream Tea © 2017 Tristan Crispijn (tristan@monkeycat.nl). All Rights Reserved"
iBrewContribute   = "Please DONATE! Food, jokes, hugs and fun toys! To your favaroite cat!\n\nContribute any discoveries on https://github.com/Tristan79/iBrew/issues"

class iBrewConsole:

    #------------------------------------------------------
    # iBrew MONITOR
    #------------------------------------------------------
    # assume we're connected to a client! we're printing
    # every message received. you can stop the monitor by
    # pressing ctrl-c, the only messages we expect to
    # receive is a response message 14 (status appliance),
    # if there are any other messages we print them too!
    
    def monitor(self):
        print "iBrew: Press ctrl-c to stop"
        
        dump = self.client.dump
        self.client.dump_status = True
        self.client.dump = True
        
        while True:
            try:
                import time
                time.sleep(1)
            except KeyboardInterrupt:
                self.quit = True
                break
            except Exception, e:
                self.quit = True
                logging.debug(traceback.format_exc())
                logging.debug(str(e))
                break
        self.client.dump = dump
        self.client.dump_status = False
        print
   


    #------------------------------------------------------
    # iBrew WEB
    #------------------------------------------------------

    # assume we're connected to a client
    # you can stop the web server by pressing ctrl-c
    def web(self):
        
        webs = None
        try:
            if self.haveHost:
                self.web = iBrewWeb()
                self.web.events = self.client.events
                self.web.run(self.serverBind,self.serverPort,self.client.dump,self.client.host,self.client.port)
            else:
                self.web = iBrewWeb()
                self.web.events = self.client.events
                self.web.run(self.serverBind,self.serverPort,self.client.dump)
        
        except Exception, e:
            logging.debug(e)
            logging.info("iBrew: Failed to run Web Interface & REST API on port [" + self.serverBind + ":" + str(self.serverPort) + "]")
            return
        logging.info("iBrew: Starting Web Interface & REST API [" + self.serverBind + ":" + str(self.serverPort) + "]. Press ctrl-c to stop")
        self.monitor()
        self.web.kill()
        logging.info("iBrew: Stopped Web Interface & REST API [" + self.serverBind + ":" + str(self.serverPort) + "]")
 

    #------------------------------------------------------
    # iBrew SWEEP
    #------------------------------------------------------

    # assume we're connected to a client
    # you can stop the sweep by pressing ctrl-c
    def sweep(self,start=1):
        if int(start) <= 0 or start > 256:
            print 'iBrew: sweep start out of range [00..ff]'
            return

        dump = self.client.dump
        self.client.dump = True
        self.client.dump_status = False
        
        print
        print "DO NOT DO THIS IF YOU DO NOT KNOW WHAT YOU ARE DOING"
        print
        print "IT CAN RENDER THE " + Smarter.device_to_string(self.client.deviceId) + " COMPLETELY USELESS"
        print
        print "Are you really, really sure?"
        try:
            i = raw_input("Please enter YES if you are: ")
            if i != "YES":
                return
        except Exception:
            return
        print "iBrew: Press ctrl-c to stop"
 

        for id in range(int(start),256):
            try:
                # known command/message?
                known = False
                if self.client.isKettle:
                    known = Smarter.message_kettle(id)
                if self.client.isCoffee:
                    known = Smarter.message_coffee(id)
                # know command for other device except itself?
                if not known:
                
                    # add zero here...
                    print "iBrew: Probing command: " + Smarter.number_to_code(id)

                    # button pressed quit...
                    self.client.device_raw(Smarter.number_to_code(id))

                    # check if got also a ???status message... FIX
                    if self.client.commandStatus != Smarter.StatusInvalid:
                        print "iBrew: New command found: " + Smarter.number_to_code(id)
                    self.client.dump = False
                    self.client.device_stop()
                    self.client.dump = True
            except Exception:
                # was it ctrl-c or error???
                break;
        self.client.dump = dump



    #------------------------------------------------------
    # iBrew Console MAIN LOOP
    #------------------------------------------------------

    def is_valid_ipv4_address(self,address):
        try:
            socket.inet_pton(socket.AF_INET, address)
        except AttributeError:  # no inet_pton here, sorry
            try:
                socket.inet_aton(address)
            except socket.error:
                return False
            return address.count('.') == 3
        except socket.error:  # not a valid address
            return False
        return True


    def is_valid_ipv6_address(self,address):
        try:
            socket.inet_pton(socket.AF_INET6, address)
        except socket.error:  # not a valid address
            return False
        return True
        

    def check_license(self):
        self.username = "WebServer"
        
        if not os.path.isfile(AppFolders.settings() + '/.ibrew'):
            self.username = "NOT ACCEPTED"
            self.app_info()
            print
            print "PLEASE READ THE FOLLOWING VERY CAREFULLY"
            print
            print
            print "LICENSE " + iBrewApp
            print
            print Smarter.license()
            print
            print
            print "WARNING: YOU COULD BRICK YOUR APPLIANCE, USE AT YOUR OWN RISK"
            print
            print "NOTE: THIS IS OFFLINE! NO INFORMATION WILL BE SHARED WITH ANYONE!"
            print
            print
            print "LICENSING AGREEMENT"
            try:
                self.username = raw_input("Please enter your full name: ").strip()
                c = 0
                while not (' ' in self.username):
                    c += 1
                    if c > 2:
                        print "Forgot your full name?"
                        return False
                    print "That is not your full name!"
                    self.username = raw_input("Please enter your full name: ").strip()
                c = 0
                email = raw_input(self.username + ", please enter your email address: ").strip()
                while (not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",email)):
                    c += 1
                    if c > 2:
                        print "Forgot your email address?"
                        return False
                    print "Invalid email"
                    email = raw_input(self.username + ", please enter your email: ").strip()
                c = 0
                accept = raw_input("You accept the license? Please answer with YES or NO followed by pressing the ENTER key: ").strip()
                while (accept.upper() != "YES"):
                    if accept.upper() == "NO":
                        return False
                    c += 1
                    if c > 2:
                        print "You decided to not to agree!"
                        return False
                    email = raw_input("Please answer with YES or NO followed by pressing the ENTER key: ").strip()
            except Exception:
                print "You decided to not to agree!"
                return False
            print "Thank you, "+ self.username +" for accepting!"
            print
        
            config = SafeConfigParser()
            config.read(AppFolders.settings() + '/.ibrew')
        
            try:
                config.add_section('license')
            except Exception:
                pass

            config.set('license', 'accepted', 'true')
            config.set('license', 'name', self.username)
            config.set('license', 'email', email)
            with open(AppFolders.settings() + '/.ibrew', 'w') as f:
                config.write(f)
        else:
            config = SafeConfigParser()
            config.read(AppFolders.settings() + '/.ibrew')
            try:
                self.username =  config.get('license','name')
            except Exception:
                self.username = "NOT ACCEPTED"
        return True
        
    
    def execute(self,line):
    
        try:
            numarg = 0
            if len(line) == 0:
                if self.console:
                    if self.client.connected:
                        self.client.print_short_status()
                    else: print "iBrew: Not connected"
                    return
                else:
                    argument = line
                    command = "help"
            else:
                command = line[0].lower()
                numarg = len(line) - 1
                arguments = line[1:]


            if command == "exit" or command == "quit":
                self.client.run = False
                self.quit = True
                return


            #if command != "help" and command != "?" and command != "message" and command != "usage" and command != "commands" and command != "joke" and command != "license" and command != "protocol" and command != "structure" and command != "groups" and command != "group" and command != "notes" and command != "examples" and command != "messages":
            #if not self.check_license():
            #    print "NOT LICENSED"
            #    return
            self.username = "NOT LICENSED"


            if command == "dump":
                if numarg == 0 and not self.console:
                    print "iBrew: Do I look like a civet cat to you?"
                    return
                else:
                    if self.client.dump and numarg == 0:
                        self.client.dump = False
                        if self.console:
                            print "iBrew: Dump raw messages disabled"
                    else:
                        self.client.dump = True
                        if self.console:
                            print "iBrew: Dump raw messages enabled"
                    
                    if numarg > 0:
                        command = arguments[0].lower()
                        arguments = arguments[1:]
                        numarg -= 1
                    else:
                        return

            if command == "events":
                if self.console:
                    if self.client.events == False:
                        self.client.events = True
                        print "iBrew: Trigger events enabled"
                    else:
                        self.client.events = False
                        print "iBrew: Trigger events disabled"
                    return
                elif numarg != 0:
                    self.client.events = True
                    command = arguments[0].lower()
                    arguments = arguments[1:]
                    numarg -= 1
        
            self.haveHost = False
            self.serverBind = ""
            self.serverPort = Smarter.Port - 1
            
            if numarg > 0:
                if arguments[numarg-1] == "simulate":
                    self.client.setHost("simulation")
                else:
                    connection = str.split(arguments[numarg-1],':')
                    if self.is_valid_ipv4_address(connection[0]) or self.is_valid_ipv6_address(connection[0]) or (("server" in arguments or command == "server") and connection[0] == ""):
                        if command == "legacy":
                            self.client.iKettle.host = connection[0]
                        
                        else:
                            if "server" in arguments or command == "server" or "web" in arguments or command == "web":
                                self.serverBind = connection[0]
                            else:
                                self.client.setHost(connection[0])
                        try:
                            self.portfound = False
                            p = int(connection[1])
                            if command == "legacy":
                                self.client.iKettle.port = p
                            else:
                                
                                if "server" in arguments or command == "server" or "web" in arguments or command == "web":
                                    self.serverPort = connection[1]
                                    self.portfound = True
                                else:
                                    self.client.port = p
                        except ValueError:
                            pass
                        except IndexError:
                            pass
                        if "server" not in arguments and command != "server" and "web" not in arguments and command != "web":
                            self.haveHost = True
                        numarg -= 1
                        arguments = arguments[0:numarg]

                        if numarg > 0 and ("server" in arguments or command == "server" or "web" in arguments or command == "web"):
                            connection = str.split(arguments[numarg-1],':')
  
                            
                            noport = False
                            try:
                                p = int(connection[1])
                            
                            except ValueError:
                                noport = True
                            except IndexError:
                                noport = True

                            isvalid = self.is_valid_ipv4_address(connection[0]) or self.is_valid_ipv6_address(connection[0])
                            if not noport and (connection[0] == "" or isvalid):
                                if self.serverBind == "":
                                    self.client.setHost(Smarter.DirectHost)
                                else:
                                    self.client.setHost(self.serverBind)
                                if self.portfound:
                                    self.client.port = self.serverPort
                                else:
                                    self.client.port = Smarter.Port
                                
                                self.haveHost = True
                                self.serverPort = connection[1]
                                self.serverBind = connection[0]
                                numarg -= 1
                                arguments = arguments[0:numarg]
                            elif noport and isvalid:
                                if self.serverBind == "":
                                    self.client.setHost(Smarter.DirectHost)
                                else:
                                    self.client.setHost(self.serverBind)
                                if self.portfound:
                                    self.client.port = self.serverPort
                                else:
                                    self.client.port = Smarter.Port
                                self.haveHost = True
                                self.serverPort = Smarter.Port - 1
                                self.serverBind = connection[0]
                                numarg -= 1
                                arguments = arguments[0:numarg]


            if command == "legacy":
                if numarg == 0:
                    self.legacy()
                    self.legacy_commands()
                    return
                if numarg >= 1:
                    if self.client.isCoffee:
                        print "iBrew: iKettle != Coffee Machine"
                        #logging.warning("iBrew: iKettle != Coffee Machine")
              
                    if arguments[0] == "protocol":
                        SmarterLegacy.protocol()
                        
                    if arguments[0] == "simulate":
                        self.client.iKettle.simulate()
                        self.monitor()
                        return
                        
                    if arguments[0] == "relay":
                        if numarg >= 2:
                            if arguments[1] == "stop":
                                self.client.iKettle.relay_stop()
                                return
                            connection = str.split(arguments[1],':')
                            if self.is_valid_ipv4_address(connection[1]) or self.is_valid_ipv6_address(connection[0]):
                                self.client.iKettle.relayHost = connection[1]
                            try:
                                p = int(connection[1])
                                self.client.iKettle.relayPort = p
                            except ValueError:
                                pass
                            except IndexError:
                                pass
                        self.client.iKettle.connect()
                        self.client.iKettle.relay_start()
                        self.monitor()
                        return
                    
                    if numarg == 1:
                        self.client.iKettle.dump = self.client.dump
                        self.client.iKettle.normal()
                        try:
                            r = self.client.iKettle.send(SmarterLegacy.string_to_command(arguments[0]))
                            for i in r:
                                print "iBrew Legacy: " + SmarterLegacy.string_response(i)
                        except Exception:
                            print "iBrew: Unknown legacy command"
                        return
                    else:
                        print "iBrew: Unknown legacy command"


            if command == "shout":
                if self.console or numarg == 0:
                    print "iBrew: Can't hear you. Drinking tea at a dinner on the other side of the universe!"
                    return
                if numarg > 0:
                    command = arguments[0].lower()
                    arguments = arguments[1:]
                    numarg -= 1
                if not self.console:
                    self.client.shout      = True
                    self.client.isKettle   = True
                    self.client.isCoffee   = True
                else:
                    print "iBrew: \'shout\' not available in the console"


            if command == "slow":
                if self.console or numarg == 0:
                    print "iBrew: As you command, but it can take a while!"
                    return
                if numarg > 0:
                    command = arguments[0].lower()
                    arguments = arguments[1:]
                    numarg -= 1
                if not self.console:
                    self.client.fast = False
                else:
                    print "iBrew: \'kettle\' not available in the console"


            if command == "coffee":
                if numarg == 0:
                    print "iBrew: Nah, I want hot chocolade!"
                    return
                if numarg > 0:
                    command = arguments[0].lower()
                    arguments = arguments[1:]
                    numarg -= 1
                #if not self.console:
                self.client.switch_coffee_device()
                #else:
                #    print "iBrew: \'coffee\' not available in the console"


            if command == "kettle":
                if numarg == 0:
                
                    sim = ""
                    blubtext = "*blub*"
                    borreltext = "*borrel*"
                    for i in range(1,random.randint(0,42*42)):
                        if random.randint(0,1) == 0:
                            if random.randint(0,4) == 0:
                                sim += " ".rjust(random.randint(0,4)," ") + blubtext.upper()
                            else:
                                sim += " ".rjust(random.randint(0,4)," ") + blubtext

                        else:
                            if random.randint(0,5) == 0:
                                sim += " ".rjust(random.randint(0,4)," ") + borreltext.upper()
                            else:
                                sim += " ".rjust(random.randint(0,4)," ") + borreltext
                    print "iBrew: Starting simulation of boiling water!\n\n" + sim
                    return
                
                if numarg > 0:
                    command = arguments[0].lower()
                    arguments = arguments[1:]
                    numarg -= 1
                #if not self.console:
                self.client.switch_kettle_device()
                #else:
                #    print "iBrew: \'kettle\' not available in the console"


            if command == "fahrenheid":
                if numarg == 0 and not self.console:
                    print "iBrew: Kelvin, stop that!"
                    return
                else:
                    Smarter.fahrenheid = True
                    if numarg > 0:
                        command = arguments[0].lower()
                        arguments = arguments[1:]
                        numarg -= 1
                    if self.console:
                        print "iBrew: Temperature in fahrenheid"
                        return


            if command == "celsius":
                if numarg == 0 and not self.console:
                    print "iBrew: But i'm freezing and so confused. Please turn me on!"
                    return
                else:
                    Smarter.fahrenheid = False
                    if numarg > 0:
                        command = arguments[0].lower()
                        arguments = arguments[1:]
                        numarg -= 1
                    if self.console:
                        print "iBrew: Temperature in celsius"
                        return

            if command == "simulate":
                self.client.simulate()
                
                command = "relay"
                if self.client.isCoffee:
                    self.client.switch_coffee_device()
                    numarg = 1
                    arguments = ["in:GOD,out:32,out:relay"]
                else:
                    self.client.switch_kettle_device()
                    numarg = 1
                    arguments = ["in:GOD,out:14,out:relay"]

            if command == "console" or command == "connect":
                self.client.disconnect()
                
            if command == "disconnect":
                self.client.disconnect()
                return

            if command == "connect" or command == "console" or ((command == "relay" or command == "sweep" or command == "events" or command == "monitor" or command == "server" or command == "web") and not self.console):
                self.app_info()
                self.joke()


            if command == "monitor" or command == "events":
                self.client.fast = False

            if (command == "relay" and not self.console) or ((not self.client.connected or self.haveHost) and command != "help" and command != "?" and command != "list" and command != "message" and command != "usage" and command != "commands" and command != "server" and command != "joke" and command != "license" and command != "protocol" and command != "structure" and command != "notes" and command != "groups" and command != "group" and command != "examples" and command != "states" and command != "triggers" and command != "messages" and command != "rules" and command != "rule" and command != "web" and command != "legacy"  and command != "trigger"):


                if not self.haveHost and command != "relay":
                    devices, relay = Smarter.find_devices(self.client.port)
                    if self.client.dump:
                        Smarter.print_devices_found(devices,relay)
            
                    if len(devices) == 1:
                        self.client.setHost(devices[0][0])

                if command == "console" or command == "connect":
                    self.client.dump_status = False
                    self.client.fast = False
                    self.client.shout = False
                

                try:
                    if not self.client.dump:
                        print
                        print "  Starting please wait..."
                        print
                    if not (self.console and command == "relay") and not self.client.simulate:
                        self.client.connect()
                    
                    
                except Exception, e:
                    logging.debug(e)
                    logging.info("iBrew: Could not connect to [" + self.client.host + "]")
                    if command != "console" and command != "connect" and command != "relay":
                        return

                # FIX RELAY SHOULD NOT BE HERE
                if command == "console" or command == "connect":
                    self.console = True

                if command == "console" or command == "connect" or command == "relay":
                    if numarg >= 1:
                        if arguments[0][2] == ':' or arguments[0][3] == ':':
                            self.client.unblock("in:GOD,out:GOD")
                            self.client.block(arguments[0])
                            numarg -= 1
                            arguments = arguments[0:numarg]
                    if self.client.dump:
                        self.client.print_rules_short()
                
            if command == "status" and numarg > 0:
                self.client.fast = False
                try:
                    self.client.device_all_settings()
                except Exception, e:
                    #logging.debug(str(e))
                    #logging.debug(traceback.format_exc())
                    print "iBrew: Could not init values"
                    return

            if command == "connect" or command == "console" or ((command == "relay" or command == "sweep" or command == "monitor" or command == "events") and not self.console):
 
                try:
                    self.client.device_all_settings()
                except Exception, e:
                    logging.debug(str(e))
                    logging.debug(traceback.format_exc())
                    print "iBrew: Could not init values"
                    return
                self.client.print_connect_status()
                self.client.print_status()

            if command == "console" or command == "connect" or (command == "relay" and not self.console):
                self.intro()
            
            if command == "console" or command == "connect":
                return


            if command == "help" or command == "?":
                                            self.app_info()
                                            self.usage()
                                            self.commands()
            # shortstatus is legacy ibrew command
            elif command == "shortstatus" or (numarg == 0 and command == "status"):  self.client.print_short_status()
            elif command == "usage":        self.usage()
            elif command == "rules":
                                            if numarg >= 1:
                                                self.client.print_rules()
                                            else:
                                                self.client.print_rules_short()
            elif command == "patches":
                                            if numarg >= 1:
                                                self.client.print_patches()
                                            else:
                                                self.client.print_patches_short()
            elif command == "unblock":      self.client.unblock(arguments[0])
            elif command == "block":        self.client.block(arguments[0])
            elif command == "patch":        self.client.patch(arguments[0])
            elif command == "remote":
                                            if numarg == 1 and arguments[0] == "info":
                                                self.client.relay_info()
                                                if not self.client.dump: self.client.print_info_relay()
                                            elif numarg >= 1 and arguments[0] == "rules":
                                                self.client.relay_modifiers_info()
                                                if numarg == 2:
                                                    self.client.print_remote_rules()
                                                else:
                                                    if not self.client.dump: self.client.print_remote_rules_short()
                                            elif numarg >= 1 and arguments[0] == "patches":
                                                self.client.relay_modifiers_info()
                                                if numarg == 2:
                                                    self.client.print_remote_patches()
                                                else:
                                                    if not self.client.dump: self.client.print_remote_patches_short()
                                            elif numarg == 2 and arguments[0] == "patch":
                                                self.client.relay_patch(arguments[1])
                                                if not self.client.dump: self.client.print_remote_patches_short()
                                        
                                            elif numarg == 2 and arguments[0] == "block":
                                                self.client.relay_block(arguments[1])
                                                if not self.client.dump: self.client.print_remote_rules_short()
                                        
                                            elif numarg == 2 and arguments[0] == "unblock":
                                                self.client.relay_unblock(arguments[1])
                                                if not self.client.dump: self.client.print_remote_rules_short()
                                                
                                            else:
                                                print "iBrew: Use additional command: info, block or unblock"
            elif command == "triggers":     Smarter.print_triggers()
            elif command == "states":     Smarter.print_states()
            elif command == "trigger":
                                            if numarg == 0:
                                                self.client.print_triggers()
                                            else:
                                                if arguments[0] == "groups":
                                                    self.client.print_groups()
                                                elif arguments[0] == "add" and numarg == 4:
                                                    self.client.triggerAdd(arguments[1],arguments[2].upper(),arguments[3])
                                                    print "iBrew: Added trigger " + arguments[2].upper() + " to group " + arguments[1] + " with action " + arguments[3]
                                                elif arguments[0] == "add" and numarg != 4:
                                                    print "iBrew: Trigger add need a group name and a trigger action"
                                                elif arguments[0][0:3] == "del":
                                                    if numarg == 3 or numarg == 2:
                                                        if numarg == 2:
                                                            self.client.triggerGroupDelete(arguments[1])
                                                            print "iBrew: Trigger group " + arguments[1] + " deleted"
                                                        else:
                                                            self.client.triggerDelete(arguments[1],arguments[2].upper())
                                                            print "iBrew: Trigger " + arguments[2].upper() + " of group " + arguments[1] + " deleted"
                                                    else:
                                                        print "iBrew: Trigger delete need a group name or a group name and a trigger action"
                                                else:
                                                    if numarg == 1:
                                                        self.client.print_group(arguments[0])
                                                    elif numarg == 2:
                                                        if arguments[1] == "state":
                                                            print "iBrew: Missing arguments, which duality?"
                                                        else:
                                                            try:
                                                                state = Smarter.string_to_bool(arguments[1])
                                                                if state:
                                                                    self.client.enableGroup(arguments[0])
                                                                    print "iBrew: Trigger group " + arguments[0] + " enabled"
                                                                else:
                                                                    self.client.disableGroup(arguments[0])
                                                                    print "iBrew: Trigger group " + arguments[0] + " enabled"
                                                            except Exception, e:
                                                                print str(e)
                                                                print "iBrew: failed to get state"
                                                    elif arguments[1] == "state":
                                                        self.client.boolsGroup(arguments[0],arguments[2])
                                                        print "iBrew: Trigger group " + arguments[0] + " boolean state " + arguments[2]
                                                    else:
                                                        print "iBrew: missing arguments, about time for some peace and quite :-)"
                                                            
            elif command == "relay":
                                            if numarg >= 1:
                                                if arguments[0] == "stop":
                                                    self.client.relay_stop()
                                                # decode port and ip?
                                                else:
                                                    connection = str.split(arguments[0],':')
                                                    if self.is_valid_ipv4_address(connection[0]) or self.is_valid_ipv6_address(connection[0]):
                                                        self.client.relayHost = connection[0]
                                                    try:
                                                        p = int(connection[1])
                                                        self.client.relayPort = p
                                                    except ValueError:
                                                        pass
                                                    except IndexError:
                                                        pass
                                                    self.client.relay_start()
                                                    self.monitor()
                                                    
                                            else:
                                                self.client.relay_start()
                                                self.monitor()
            
            elif command == "commands":     self.commands()
            elif command == "protocol":     print Smarter.protocol()
            elif command == "structure":    print Smarter.structure()
            elif command == "notes":        print Smarter.notes()
            elif command == "license":
                                            if self.console and numarg == 1 and arguments[0] == "disagree":
                                                try:
                                                    os.remove(AppFolders.settings() + '/.ibrew')
                                                except:
                                                    pass 
                                            else:
                                                print Smarter.license()
            elif command == "examples":     self.examples()
            elif command == "groups":       print Smarter.groups()
            elif command == "messages":
                                            if numarg >= 1 or not self.console:
                                                print Smarter.messages()
                                            else:
                                                print Smarter.messages(self.client.isCoffee,self.client.isKettle)
            elif command == "message":
                                            if numarg >= 1:
                                                print Smarter.message(Smarter.code_to_number(arguments[0]))
                                            else:
                                                print Smarter.message_all()
            elif command == "group":
                                            if numarg >= 1:
                                                s = None
                                                try:
                                                    s = Smarter.group(Smarter.string_to_group(arguments[0]))
                                                except SmarterError:
                                                    print "iBrew: Group not available"
                                                else:
                                                    print s
                                            else:
                                                print Smarter.groups_all()
            elif command == "list":
                                            devices, relay = Smarter.find_devices(self.client.port)
                                            Smarter.print_devices_found(devices, relay)
            elif command == "joke" or command == "quote":
                                            print
                                            self.joke()
                                            print
            elif command == "stats":        self.client.print_stats()
            # web is legacy ibrew command
            elif command == "server" or command == "web":
                                            if not self.console:
                                                    self.web()
                                            else:
                                                print "iBrew: Not in console"

            # Kettle
            elif not self.client.connected: return
            elif command == "heat":
                                            if numarg >= 2:
                                                self.client.kettle_heat(Smarter.string_to_temperature(arguments[0]),Smarter.string_to_keepwarm(arguments[1]))
                                            elif numarg == 1:
                                                self.client.kettle_heat(Smarter.string_to_temperature(arguments[0]))
                                            else:
                                                self.client.kettle_heat_default()
                                    
            elif command == "milk":         self.client.kettle_milk()
            elif command == "tea":
                                            if numarg == 1:
                                                if arguments[0] == "white":
                                                    self.client.kettle_heat_white_tea()
                                                if arguments[0] == "black":
                                                    self.client.kettle_heat_black_tea()
                                                if arguments[0] == "green":
                                                    self.client.kettle_heat_green_tea()
                                                if arguments[0] == "oelong":
                                                    self.client.kettle_heat_oelong_tea()
                                                
            elif command == "boil":         self.client.kettle_boil()

            elif command == "kettlecoffee": self.client.kettle_heat_coffee()

            elif command == "formula":
                                            if numarg >= 2:
                                                self.client.kettle_formula_heat(Smarter.string_to_temperature(arguments[0]),Smarter.string_to_keepwarm(arguments[1]))
                                            elif numarg == 1:
                                                self.client.kettle_formula_heat(Smarter.string_to_temperature(arguments[0]),self.client.defaultKeepWarmTime)
                                            else:
                                                self.client.kettle_formula_heat(self.client.defaultFormulaTemperature,self.client.defaultKeepWarmTime)

            elif command == "default":      self.client.device_restore_default()
            elif command == "calibrate":
                                            if self.client.onBase:
                                                print "Please remove kettle for accurate calibration"
                                            self.client.kettle_calibrate()
            elif command == "base":
                                            if numarg == 0:
                                                self.client.kettle_calibrate_base()
                                                if not self.client.dump: self.client.print_watersensor_base()
                                            if numarg >= 1:
                                                self.client.kettle_calibrate_store_base(Smarter.string_to_watersensor(arguments[0]))
                                                if not self.client.dump: self.client.print_watersensor_base()

            # WiFi
            elif command == "firmware":
                                            self.client.wifi_firmware()
                                            if not self.client.dump: self.client.print_wifi_firmware()
            elif command == "direct":        self.client.wifi_direct()
            elif command == "scan":
                                            self.client.wifi_scan()
                                            if not self.client.dump: self.client.print_wireless_networks()
            elif command == "join":
                                            if numarg >= 1:
                                                password = ""
                                                network = arguments[0]
                                                if numarg >= 2:
                                                    password = arguments[1]
                                                self.client.wifi_join(network,password)
                                            else:
                                                print "iBrew: Need at least a wireless network name"
            elif command == "rejoin":
                                            if self.client.isDirect:
                                                print "iBrew: Can not rejoin if connected directly"
                                            else:
                                                self.client.wifi_rejoin()

            # Coffee
            elif command == "hotplate":
                                            if numarg >= 1:
                                                if arguments[0].lower() == "off":
                                                      self.client.coffee_hotplate_off()
                                                elif arguments[0].lower() == "on":
                                                    if numarg >= 2:
                                                            self.client.coffee_hotplate_on(Smarter.string_to_hotplate(arguments[1]))
                                                    else:
                                                        self.client.coffee_hotplate_on()
                                                else:
                                                    print "iBrew: hotplate missing [on/off] got " + arguments[0]
                                            else:
                                                print "iBrew: hotplate missing [on/off]"
            elif command == "carafe":
                                            if numarg >= 1:
                                                if arguments[0].lower() == "False":
                                                    self.client.coffee_carafe_required_off()
                                                elif arguments[0].lower() == "True":
                                                    self.client.coffee_carafe_required_on()
                                            else:
                                                self.client.coffee_carafe_required()
            elif command == "timers":        self.client.coffee_timers()
            elif command == "timer":
                                            if numarg >= 2:
                                                if arguments[0].lower() == "delete":
                                                    self.client.coffee_timer_disable(Smarter.string_to_number(arguments[1]))
                                                else:
                                                    self.client.coffee_timer_store(Smarter.string_to_number(arguments[1]))
 
                                                print "iBrew: Not yet implemented"
                                            else:
                                                print "iBrew: timer needs index (time or delete)"
            elif command == "mode":
                                            if numarg >= 1:
                                                if arguments[0].lower() == "carafe":
                                                    self.client.coffee_carafe_mode()
                                                elif arguments[0].lower() == "cup":
                                                    self.client.coffee_cup_mode()
                                            else:
                                                self.client.coffee_mode()
            elif command == "beans":
                                            if self.client.grind:
                                                print "iBrew: Beans already selected"
                                            else:
                                                self.client.coffee_beans()
                                                print "iBrew: Beans used"
            elif command == "filter" or command == "pregrind":
                                            if not self.client.grind:
                                                print "iBrew: Filter already selected"
                                            else:
                                                self.client.coffee_filter()
                                                print "iBrew: Filter used"
            elif command == "descale":
                                            try:
                                                self.client.coffee_descale()
                                            except Exception:
                                                # no water...?
                                                print "iBrew: Descaling failed"
            elif command == "brew":
                                            if numarg == 0:
                                                self.client.coffee_brew_settings()
                                            elif numarg == 1 and arguments[0].lower() == "default":
                                                self.client.coffee_brew_default()
                                            elif numarg == 1:
                                                self.client.coffee_brew(Smarter.string_to_cups(arguments[0]),self.client.hotPlate,self.client.grind,self.client.strength)
                                            elif numarg == 2:
                                                self.client.coffee_brew(Smarter.string_to_cups(arguments[0]),Smarter.string_to_hotplate(arguments[1]),self.client.grind,self.client.strength)
                                            elif numarg == 3:
                                                self.client.coffee_brew(Smarter.string_to_cups(arguments[0]),Smarter.string_to_hotplate(arguments[1]),Smarter.string_to_grind(arguments[2]),self.client.strength)
                                            elif numarg >= 4:
                                                self.client.coffee_brew(Smarter.string_to_cups(arguments[0]),Smarter.string_to_hotplate(arguments[1]),Smarter.string_to_grind(arguments[2]),Smarter.string_to_strength(arguments[3]))
            elif command == "strength":
                                            if numarg == 0:
                                                print "iBrew: specify strength [weak,medium,strong]"
                                            elif numarg >= 1:
                                                self.client.coffee_strength(Smarter.string_to_strength(arguments[0]))
            elif command == "weak":         self.client.coffee_weak()
            elif command == "medium":       self.client.coffee_medium()
            elif command == "strong":       self.client.coffee_strong()
            elif command == "cups":
                                            if numarg == 0:
                                                print "iBrew: specify cups [1..12]"
                                            elif numarg >= 1:
                                                self.client.coffee_cups(Smarter.string_to_cups(arguments[0]))

              # Console Commands
            elif command == "monitor":      self.monitor()
            elif command == "events":
                                            self.client.events = True
                                            self.monitor()
            elif command == "sweep":
                                            if numarg >= 1:
                                                 self.sweep(Smarter.code_to_number(arguments[0]))
                                            else:
                                                self.sweep()
            elif command == "settings":     # FAST fix need device... could default...
                                            if numarg == 0:
                                                self.client.device_settings()
                                                if not self.client.dump: self.client.print_settings()
                                            elif numarg == 0: print "iBrew: Could not store coffee settings, missing all arguments"
                                            elif numarg == 1 and self.client.isCoffee: print "iBrew: Could not store coffee settings, missing cups"
                                            elif numarg == 2 and self.client.isCoffee: print "iBrew: Could not store coffee settings, missing grinder"
                                            elif numarg == 3 and self.client.isCoffee: print "iBrew: Could not store coffee settings, missing hotplate"
                                            elif numarg == 1 and self.client.isKettle: print "iBrew: Could not store kettle settings, missing temperature"
                                            elif numarg == 2 and self.client.isKettle: print "iBrew: Could not store kettle settings, missing formula mode"
                                            elif numarg == 3 and self.client.isKettle: print "iBrew: Could not store kettle settings, missing formula temperature"
                                            elif numarg >= 4:
                                                self.client.device_store_settings(arguments[0],arguments[1],arguments[2],arguments[3])
                                                if not self.client.dump: self.client.print_settings()
            elif command == "stop" or command == "off":
                                            self.client.device_stop()
            elif command == "on" or command == "start":
                                            self.client.device_start()

            elif command == "reset":        self.client.device_reset()
            elif command == "info":
                                            self.client.device_info()
                                            if not self.client.dump: self.client.print_info_device()
            elif command == "history":
                                            self.client.device_history()
                                            if not self.client.dump: self.client.print_history()
            elif command == "time":
                                            print "not yet implemented"
                                            self.client.device_time()

            elif command == "status":       self.client.print_status() # status full, on check on keyword
            else:
                                            try:
                                                self.client.device_raw(command+''.join(arguments))
                                            except Exception:
                                                print "iBrew: Sending raw command message failed"
        except Exception,e:
            if not self.console:
                self.quit = True
            print str(e)
            print(traceback.format_exc())
            print "iBrew: Command Failed"
            
       
    def run(self,arguments):
        AppFolders.makeFolders()

        #Configure logging
        # root level        
        logger = logging.getLogger()    
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        log_file = os.path.join(AppFolders.logs(), "ibrew.log")
        
        fh = logging.handlers.RotatingFileHandler(log_file, maxBytes=1048576, backupCount=4, encoding="UTF8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
        # By default only do info level to console
        sh = logging.StreamHandler(sys.stdout)
        sh.setLevel(logging.INFO)
        sh.setFormatter(formatter)
        logger.addHandler(sh)


        sh.setLevel(logging.DEBUG)
        
        self.console = False
        self.quit = True
        
        try:
            self.client = SmarterInterface(AppFolders.settings() + "/")
            self.client.fast = True
            try:
                self.execute(arguments)
            except Exception, e:
                self.quit = True
                self.console = False
        
            if self.console:
                self.quit = False
            
            while not self.quit:
                try:
                    cursor = self.client.host + ":" + self.client.device + "$"
                    self.execute(raw_input(cursor).strip().split())
                except KeyboardInterrupt:
                    self.quit = True
                except Exception, e:
                    self.quit = True
                    logging.debug(traceback.format_exc())
                    logging.debug(str(e))
        except KeyboardInterrupt:
            pass
        
        #if self.client is not None:
        self.client.trash()
                
        
                     
#------------------------------------------------------
# iBrew Console PRINT
#------------------------------------------------------

    def app_info(self):
        print iBrewApp
        print iBrewInfo
        if self.username != "NOT ACCEPTED":
            print "iBrew: LICENSING AGREEMENT accepted by LICENSEE " + self.username
        print
        print iBrewContribute
        print

    def intro(self):
        print
        print "For list of commands type: help and press enter"
        print "Press enter for status update and press ctrl-c to quit"
        print

    def joke(self):
        joke = iBrewJokes().joke()
        if self.client is not None:
            if self.client.isCoffee:
                joke = iBrewJokes().coffee()
            elif self.client.isKettle:
                joke = iBrewJokes().kettle()
        print "\n      \'" + joke[0] + "\'\n                  -- " + joke[1] + "\n"


    def usage(self):
        print
        print "  iBrew Server"
        print "  ________________"
        print
        print "  Usage: ibrew (dump) (events) (fahrenheid) server (host:(port) (host:(port))"
#        print "  Usage: ibrew (energy) (dump) (fahrenheid) server (host:(port))"
        print
     #   print "    energy                 energy saver (stats not possible)"
        print "    dump                   dump message enabled"
        print "    events                 enable trigger events (monitor, relay, console)"
        print "    fahrenheid             use fahrenheid"
        print "    web                    start web interface & rest api"
        print "    port                   optional port number, default 2082"
        print "    rules                  blocking & patching rules"
        print "    host                   host address of the appliance (format: ip4, ip6, fqdn)"
        print "    port                   port of appliance, optional, only use if alternative port"
        print
        self.legacy()
        print
        print "  iBrew iKettle 2.0 & Smater Coffee Command Line"
        print "  ______________________________________________"
        print
        #print "  Usage: ibrew (energy) (dump) (bridge|emulate (host:(port)) (shout|slow) (coffee|kettle) (fahrenheid) [command] (host(:port))"
        print "  Usage: ibrew (dump) (events) (legacy [bridge|emulate] (host:(port))) (shout|slow) (coffee|kettle) (fahrenheid) [command] (host(:port))"
        print
        print "    bridge                 emulate iKettle 2.0 using legacy iKettle (NOT IMPlEMENTED)"
        print "    emulate (host:(port)   emulates legacy iKettle"
        print "    coffee                 assumes coffee machine"
        print "    command                action to take!"
        print "    dump                   dump message enabled"
        print "    events                 enable trigger events (monitor, relay, console)"
        print "    fahrenheid             PARTLY WORKING use fahrenheid"
        print "    host                   host address of the appliance (format: ip4, ip6, fqdn), only use if detection fails"
        #print "    energy                 NOT IMPLEMENTED energy saver (stats not possible)"
        print "    kettle                 assumes kettle"
        print "    port                   port of appliance, optional, only use if detection fails"
        print "    shout                  sends commands and quits not waiting for a reply"
        print "    slow                   fully inits everything before action"
        print
        print "  If you do not supply a host, it will try to connect to the first detected appliance"
        print "  Thus if you have more then one appliance supply a host (if its not in direct mode)"
        print

    def legacy(self):
        print
        print "  iBrew iKettle Legacy Command Line"
        print "  _________________________________"
        print
        print "  Usage: ibrew (dump) legacy command (host(:port))"
        print
        print "    command                iKettle command, action to take!"
        print "    host                   host address of the appliance (format: ip4, ip6, fqdn)"
        print "    port                   port of appliance, optional, only use if alternative port"
        print

    def legacy_commands(self):
        print
        print "  iKettle Commands"
        print "    heat                   " + SmarterLegacy.textHeat.lower()
        print "    stop                   " + SmarterLegacy.textStop.lower()
        print "    65                     " + SmarterLegacy.textSelect65c.lower()
        print "    80                     " + SmarterLegacy.textSelect80c.lower()
        print "    95                     " + SmarterLegacy.textSelect95c.lower()
        print "    100                    " + SmarterLegacy.textSelect100c.lower()
        print "    warm                   " + SmarterLegacy.textStartWarm.lower()
        print "    5                      " + SmarterLegacy.textSelectWarm5m.lower()
        print "    10                     " + SmarterLegacy.textSelectWarm10m.lower()
        print "    20                     " + SmarterLegacy.textSelectWarm20m.lower()
        print "    status                 " + SmarterLegacy.textGetStatus
        print
        print "    protocol               protocol information"
        print "    simulate               start kettle simulation"
        print "    relay ((ip:)port)      start relay"

        print
    
    def commands(self):
        print
        print "  Commands"
        print "  ________"
        self.legacy_commands()
        print "  iKettle 2.0 & Smarter Coffee Commands"
        print "    default                set default settings"
        print "    info                   appliance info"
        print "    list                   list detected appliances"
        print "    reset                  reset appliance to default"
        print "    start                  start the appliance"
        print "    status (full)          show status"
        print "    settings               show user settings"
        print "    stop                   stop the appliance"
        print
        print "  iKettle 2.0 Commands"
        print "    base                   show watersensor base value"
        print "    base [base]            store watersensor base value"
        print "    boil                   heat till 100°C"
        print "    calibrate              calibrates watersensor"
        print "    celsius                use celsius °C [console only]"
        print "    fahrenheid             use fahrenheid °F [console only]"
        print "    formula (temperature (keepwarm))] heat kettle in formula mode"
        print "    heat (temperature)(keepwarm))    heat kettle"
        print "    kettlecoffee           warms water for coffee 95°C"
        print "    milk                   warm  65°C"
        print "    settings [temperature] [keepwarm] [formula] [formulatemperature] store kettle user settings"
        print "    tea [green,white,oelong,black] warms water for tea 65°C,80°C,90°C,100°C"
        print
        print "  Smarter Coffee Commands"
        print "    beans                  use beans for coffee"
        print "    brew (cups (hotplate (grind (strength)))) brew coffee"
        print "    brew default           brew coffee with stored user default settings"
        print "    carafe                 returns if carafe is required"
        print "    carafe [state]         set carafe is required [true or false]"
        print "    cups [number]          set number of cups [1..12]"
        print "    descale                descale coffee machine"
        print "    filter                 use pregrind beans in filter for coffee"
        print "    hotplate off           turn hotplate off"
        
        # VERAMDER DEZE FIX (ON MAG WEG)
        print "    hotplate on (minutes)  turn hotplate on (time in minutes)"
        print "    mode                   return which mode: cup or carafe mode"
        print "    mode [mode]            set mode: [cup] or [carafe] mode"
        print "    pregrind               use pregrind beans in filter for coffee"
        print "    (strength) [strength]  set strength coffee [weak, medium or strong]"
        print "    settings [cups] [hotplate] [grind] [strength] store user settings"
        print
        print "  Wireless Network Commands"
        print "    direct                 enable direct mode access"
        print "    join [net] (pass)      connect to wireless network"
        print "    rejoin                 rejoins current wireless network [not in direct mode]"
        print "    scan                   scan wireless networks"
        print
        print "  Smarter Network Commands"
        print "    connect (host) (rules&modifiers) connect to appliance"
        print "    block [rules]          block messages with groups or ids"
        print "    disconnect             disconnect connected appliance"
        print "    events                 start trigger events only"
        print "    patch [rules]          patch messages"
        print "    relay ((ip:)port)      start relay"
        print "    relay stop             stop relay"
        print "    remote info            info on remote relay"
        print "    remote block [rules]   remote block messages with groups or ids"
        print "    remote patch [rules]   remote patch"
        print "    remote rules (full)    show remote blocking and patching rules"
        print "    remote unblock [rules] remote unblock messages groups or ids"
        print "    rules (full)           show blocking & patching rules"
        print "    stats                  show traffic statistics"
        print "    unblock [rules]        unblock messages groups or ids"
        print
        print "  Block Rules"
        print "    Consists of rules, in: is for outgoing connection to the appliance, out: is for incomming connection from relay client."
        print
        print "    [in:|out:]rule(,[in:|out:]RULE)*"
        print
        print "    RULE"
        print "      message id"
        print "      group name"
        print
        print "  Patch Rules"
        print "    Patches additional functionality"
        print
        print "    [mod:]VAR=VALUE(,[mod:]VAR=VALUE)*"
        print
        print "    VAR                VALUE"
        print "    temperaturelimit   STATE or [0..100]  kettle can not heat above VALUE degrees"
        print "    childprotection    STATE              kettle can not heat above 45 degrees"
        print
        print "  Triggers"
        print "    trigger add [group] [trigger] [action] add trigger to a group"
        print "    trigger delete [group] (trigger) delete trigger or group triggers"
        print "    trigger groups         show list of groups"
        print "    trigger [group]        show triggers of group"
        print "    trigger                show all triggers"
        print "    trigger [group] [bool] enabled/disable trigger group"
        print "    trigger [group] state [bool] set group state output"
        print
        print "  Actions can either be a path to a command or url"
        print
        print "  Trigger actions examples:"
        print "    C:\SCRIPTS\SENSOR.BAT §O §N"
        print "    /home/pi/iBrew/scripts/smarthome.sh Temperature §O §N"
        print "    http://smarthome.local/?idx=34&value=§N"
        print
        print "  Debug Commands"
        print "    time [time]            set the appliance time"
        print "    firmware               show firmware Wifi"
        print "    history                action history"
        print "    [hexdata]              send raw data to appliance (e.g. \'64 7e\')"
        print "    dump                   toggle \'dump raw messages\'"
        print "    monitor                monitor incomming traffic"
        print "    simulate               start kettle (or coffee simulation)"
        print "    sweep (id)             [developer only] try (all or start with id) unknown command codes"
        print
        """
        print "    version       [00..FF]               override appliance firmware version"
        print "    heater        disable                coffee machine or kettle heater disabled"
        print
        print "    base          [00..4000]             override default calibration base"
        print "    formula       [0..100]               override default formula temperature"
        print "    keepwarm      off or [5..?]          override default keepwarm time"
        print "    formula       disable/enabled        override formula mode"
        print
        print "    carafe        optional or required   override carafe detection"
        print "    cups          [1..12]                override default number of cups"
        print "    grind         beans or filter        override default grind"
        print "    hotplate      off or [5..?]          override default hotplate time"
        print "    mode          carafe or cup          override mode"
        print "    strength      weak, medium or strong override default strength"
        print "    water                                correct cups according to water level"
        print "    limit         [1..12]                limit the number of cups to be selected"
        print "    grinder       disable                force use of filter"
        print "    hotplate      disable                coffee machine hotplate disabled"
        print
        print
        print "  NOT IMPLEMENTED Debug Coffee Timer"
        print "    timer [index] (erase|[time]) set/erase timer"
        print "    timers                 show timers"
        print
        """
        
        print "  Help Commands"
        print "    examples               show examples of commands"
        print "    groups                 show all message groups"
        print "    group                  show messages in group"
        print "    messages               show all known protocol messages"
        print "    message [id]           show protocol message detail of message [id]"
        print "    notes                  show developer notes on the appliances"
        print "    protocol               show all protocol information available"
        print "    states                 show various forms of trigger states"
        print "    structure              show protocol structure information"
        print "    triggers               show triggers"
        print
        print "  iBrew Commands"
        print "    console (rules) (modifiers) start console [command line only]"
        print "    joke                   show joke"
        print "    license                show license"
        #print "    license disagree       stop using license [command line only]"
        print "    quit                   quit console [console only]"
        print


    def examples(self):
        print
        print "  Example command line:"
        print "    ibrew shout 21 30 05 7e  Send kettle raw heat without waiting for reply"
        print "    ibrew weak 10.0.0.1      Set coffee strength to weak"
        print "    ibrew strength weak      Set coffee strength to weak but do not toggle filter/beans"
        print "    ibrew dump coffee relay out:GOD,in:32 Simulates Smarter Coffee machine"
        print "    ibrew dump kettle relay out:GOD,in:14 Simulates iKettle 2.0"
        print
        print "  Example console:"
        print "    off                      Stop heating/brewing"
        print "    messages                 Show all protocol messages"
        print "    message 3e               Show protocol message 3a, turn hotplate on"
        print "    167E                     Send kettle raw stop"
        print "    21 30 05 7e              Send kettle raw heat"
        print "    weak                     Set coffee strength to weak"
        print "    strength weak            Set coffee strength to weak but do not toggle filter/beans"
        print "    cups 3                   Set number of cups to brew"
        print "    mode cup                 Set cup mode"
        print "    block in:wifi,in:02          Block wifi and [" + Smarter.message_description(02) + "] command to appliance"
        print "    brew 4 10 beans strong   Brew 4 cups of strong coffee using the beans keeping the hotplate on for 10 minutes"
        print "    join MyWifi p@ssw0rd     Joins MyWifi wireless network using p@ssw0rd as credential"
        print "    settings 100 20 On 75    Set default user settings for the kettle to..."
        print

