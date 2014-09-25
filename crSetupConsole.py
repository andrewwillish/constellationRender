__author__ = 'andrew.willis'

#Constellation Render Setup - Console UI

#import module
import sys, time, datetime
import crSetupCore, os

os.system("cls")

class constellationRenderConsoleClass:
    def __init__(self):
        #Welcome message
        print 'Constellation Render Manager 4.0 - Setup Console'
        print ''
        #invoking main menu looping around to keep asking for new order
        while True:
            commandVar=raw_input('Insert Command >> ')

            os.system('cls')

            print 'Constellation Render Manager 4.0 - Client Console'
            print ''
            #Parsing command
            if commandVar=='exit':
                print 'bye bye'
                time.sleep(2)
                sys.exit(0)
            elif commandVar=='':
                pass
            elif commandVar=='help':
                self.printHelp()
            elif commandVar=='setup':
                self.setupFun()
            elif commandVar=='addRdrr':
                self.addRdrrFun()
            elif commandVar=='listRdrr':
                self.listRdrrFun()
            elif commandVar=='delRdrr':
                self.deleteRdrrFun()
            else:
                print ('invalid command')
            print ''
        return

    def deleteRdrrFun(self):
        self.listRdrrFun()
        print ('type x to cancel deleting file')
        rendererVar=raw_input('enter renderer name >> ')
        if rendererVar != 'x':
            if rendererVar=='':
                print ('empty renderer specified')
            try:
                crSetupCore.deleteRenderer(rendererVar)
                print (str(rendererVar)+' renderer removed')
            except Exception as e:
                print ('error : '+str(e))
        return

    def listRdrrFun(self):
        try:
            print ('available renderer:')
            allRendererLis=crSetupCore.listRenderer()
            for chk in allRendererLis:
                print chk
        except Exception as e:
            print (str(e))
        return

    def addRdrrFun(self):
        try:
            newNameVar=raw_input('enter new renderer type (read documentation for renderer detail) >> ')
            newPathVar=raw_input('enter new renderer path >> ')
            crSetupCore.addRenderer(nameVar=newNameVar,pathVar=newPathVar)
            print ('new renderer registered')
        except Exception as e:
            print ('error : '+str(e))
        return

    def setupFun(self):
        repVar=crSetupCore.setupJobTable()
        if repVar==1:
            print ('job table created')
        else:
            print ('failed to create job table')
        repVar=crSetupCore.setupClientTable()
        if repVar==1:
            print ('client table created')
        else:
            print ('failed to create client job table')
        repVar=crSetupCore.setupLogTable()
        if repVar==1:
            print ('log table created')
        else:
            print ('failed to log client job table')
        repVar=crSetupCore.setupRenderer()
        if repVar==1:
            print ('renderer list created')
        else:
            print ('failed to create renderer list')
        repVar=crSetupCore.setupConfiguration()
        if repVar==1:
            print ('Config file created')
        else:
            print ('failed to create config file')
        return

    def printHelp(self):
        print 'setup\t\t- setup constellation render manager dependencies'
        print 'addRdrr\t\t- add new renderer'
        print 'listRdrr\t- list all recorded renderer'
        print 'delRdrr\t\t- delete recorded renderer'
        print 'exit\t\t- exit setup'
        print 'help\t\t- view help menu'
        return

constellationRenderConsoleClass()