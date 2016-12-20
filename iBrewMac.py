# -*- coding: utf-8 -*-

import rumps
from iBrewFolders import AppFolders

from PyObjCTools import AppHelper

import webbrowser

#------------------------------------------------------
# iBrew
#
# Taskbar Launcher MacOS
#
# https://github.com/Tristan79/iBrew
#
# Copyright © 2017 Tristan (@monkeycat.nl). All Rights Reserved
#
# The Dream Tea
#------------------------------------------------------

rumps.debug_mode(False)  # turn on command line logging information for development - default is off

class MacGui(rumps.App):
    def __init__(self, apiServer):
        super(MacGui, self).__init__("iBrew", icon= AppFolders.iconsPath("logo.png"), quit_button=None)
        self.apiServer = apiServer
        self.menu = [
            'Interface',
  #          None,
  #          'Tea',
            None
        ]         

  #  @rumps.clicked("Tea")
  #  def tea(self, sender):
  #      self.apiServer.clients['10.0.0.99'].kettle_oelong_tea()


    @rumps.clicked("Interface")
    def web(self, sender):
        webbrowser.open("http://localhost:{0}".format(2080), new=0)

    @rumps.clicked("Quit")
    def quit(self, sender):
        if self.apiServer:
            self.apiServer.kill()
        AppHelper.stopEventLoop()
        rumps.quit_application()
        sys.exit()
    
    @rumps.notifications
    def notifications(self, notification):  # function that reacts to incoming notification dicts
        print notification
    
    def onebitcallback(self, sender):  # functions don't have to be decorated to serve as callbacks for buttons
        print 4848484            # this function is specified as a callback when creating a MenuItem below

