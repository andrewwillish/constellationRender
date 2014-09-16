__author__ = 'andrew.willis'

#Constellation Render Setup - Console UI

#import module
import sys, time, datetime
import crSetupCore

class constellationRenderConsoleClass:
    def __init__(self):
        #Welcome message
        print 'Constellation Render Manager 4.0 - Setup Console'
        print ''
        #invoking main menu looping around to keep asking for new order
        while True:
            commandVar=raw_input('Insert Command >> ')

            #Parsing command
            if commandVar=='exit':
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
                self.statPrint('invalid command')
            print ''
        return

    def deleteRdrrFun(self):
        self.listRdrrFun()
        self.statPrint('type x to cancel deleting file')
        rendererVar=raw_input('enter renderer name >> ')
        if rendererVar != 'x':
            if rendererVar=='':
                self.statPrint('empty renderer specified')
            try:
                crSetupCore.deleteRenderer(rendererVar)
                self.statPrint(str(rendererVar)+' renderer removed')
            except Exception as e:
                self.statPrint('error : '+str(e))
        return

    def listRdrrFun(self):
        try:
            self.statPrint('available renderer:')
            allRendererLis=crSetupCore.listRenderer()
            for chk in allRendererLis:
                print chk
        except Exception as e:
            self.statPrint(str(e))
        return

    def addRdrrFun(self):
        try:
            newNameVar=raw_input('enter new renderer type (read documentation for renderer detail) >> ')
            newPathVar=raw_input('enter new renderer path >> ')
            crSetupCore.addRenderer(nameVar=newNameVar,pathVar=newPathVar)
            self.statPrint('new renderer registered')
        except Exception as e:
            self.statPrint('error : '+str(e))
        return

    def setupFun(self):
        repVar=crSetupCore.setupJobTable()
        if repVar==1:
            self.statPrint('job table created')
        else:
            self.statPrint('failed to create job table')
        repVar=crSetupCore.setupClientTable()
        if repVar==1:
            self.statPrint('client table created')
        else:
            self.statPrint('failed to create client job table')
        repVar=crSetupCore.setupRenderer()
        if repVar==1:
            self.statPrint('renderer list created')
        else:
            self.statPrint('failed to create renderer list')
        repVar=crSetupCore.setupConfiguration()
        if repVar==1:
            self.statPrint('Config file created')
        else:
            self.statPrint('failed to create config file')
        return

    def printHelp(self):
        print 'Constellation Render Manager 4.0 - Setup Console Help'
        print ''
        print 'setup\t\t- setup constellation render manager dependencies'
        print 'addRdrr\t\t- add new renderer'
        print 'listRdrr\t- list all recorded renderer'
        print 'delRdrr\t\t- delete recorded renderer'
        print 'exit\t\t- exit setup'
        print 'help\t\t- view help menu'
        return

    def statPrint(self,textVar):
        time.sleep(0.2)
        nowVar=datetime.datetime.now()
        timeVar=str(nowVar.hour)+':'+str(nowVar.minute)+':'+str(nowVar.second)+' '+str(nowVar.year)+'/'+\
                                                            str(nowVar.month)+'/'+str(nowVar.day)
        #Print to screen output
        print '['+str(timeVar)+'] '+str(textVar)
        return

constellationRenderConsoleClass()