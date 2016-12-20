# -*- coding: utf-8 -*-
import os
import sys
import platform

#------------------------------------------------------
# iBrew
#
# Default folder locations
#
# https://github.com/Tristan79/iBrew
#
# Copyright © 2017 Tristan (@monkeycat.nl). All Rights Reserved
#
# The Dream Tea
#------------------------------------------------------

appname = 'iBrew'

class AppFolders():
    
    @staticmethod
    def makeFolders():
        def make(folder):
            if not os.path.exists(folder):
                os.makedirs(folder)
        make(AppFolders.logs())
        make(AppFolders.settings())
        make(AppFolders.appData())

    @staticmethod
    def runningAtRoolLevel():
        if platform.system() == "Windows":
            return True
        else:
            return os.geteuid() == 0
    
    @staticmethod
    def windowsAppDataFolder():
        return os.environ['APPDATA']

    @staticmethod
    def userFolder():
        
        filename_encoding = sys.getfilesystemencoding()

        if platform.system() == "Windows":
            folder = os.path.join( AppFolders.windowsAppDataFolder(), appname )
        elif platform.system() == "Darwin":
            folder = os.path.join( os.path.expanduser('~') , 'Library/Application Support/'+appname)
        else:
            folder = os.path.join( os.path.expanduser('~') , '.'+appname)
            
        if folder is not None:
            folder = folder.decode(filename_encoding)
        return folder
        
    @staticmethod
    def appBase():
        encoding = sys.getfilesystemencoding()
        if getattr(sys, 'frozen', None):
            if platform.system() == "Darwin":
                return sys._MEIPASS
            else: # Windows
                return os.path.dirname( os.path.abspath( unicode(sys.executable, encoding) ) )
        else:
            return os.path.dirname( os.path.abspath(unicode(__file__, encoding)) )

    @staticmethod
    def logs():
        if AppFolders.runningAtRoolLevel():
            if platform.system() == "Windows":
                folder = os.path.join( AppFolders.windowsAppDataFolder(), appname )
            else:
                folder = "/var/log"
                #folder = "/var/log/"+appname
        else:
            folder = os.path.join(AppFolders.userFolder(), "logs")
        return folder
    
    @staticmethod
    def settings():
        if AppFolders.runningAtRoolLevel():
            if platform.system() == "Windows":
                folder = os.path.join( AppFolders.windowsAppDataFolder(), appname )
            elif platform.system() == "Darwin":
                folder = os.path.join( '/Library/Application Support/'+appname)
            else:
                folder = "/etc"
                #folder = "/etc/"+appname
        else:
            folder = os.path.join(AppFolders.userFolder())
        return folder
    
    @staticmethod
    def appData():
        if AppFolders.runningAtRoolLevel():
            if platform.system() == "Windows":
                folder = os.path.join( AppFolders.windowsAppDataFolder(), appname )
            elif platform.system() == "Darwin":
                folder = os.path.join( '/Library/Application Support/'+appname)
            else:
                folder = "/var/lib/"+appname
        else:
            folder = os.path.join(AppFolders.userFolder())
        return folder
    
    @staticmethod
    def iconsPath(filename):
        return os.path.join(AppFolders.appBase(), "resources", "icons", filename)
    
