__author__ = 'andrew.willis'

#Constellation Render Setup - Console UI

#import module
import sys, time, datetime
import crSetupCore

class constellationRenderConsoleClass:
    def __init__(self):
        #Welcome message
        self.statPrint('Constellation Render Manager 3.0')
        self.statPrint('Setup Console')
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
        rendererVar=raw_input('enter renderer name >> ')
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
            allRendererLis=crSetupCore.listRenderer()
            for chk in allRendererLis:
                self.statPrint(chk)
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
        return

    def printHelp(self):
        self.statPrint('-+ Constellation Render Manager Setup Help +-')
        self.statPrint('setup - setup constellation render manager dependencies')
        self.statPrint('addRdrr - add new renderer')
        self.statPrint('listRdrr - list all recorded renderer')
        self.statPrint('delRdrr - delete recorded renderer')
        self.statPrint('exit - exit setup')
        self.statPrint('help - view help menu')
        return

    def statPrint(self,textVar):
        time.sleep(0.2)
        nowVar=datetime.datetime.now()
        timeVar=str(nowVar.hour)+':'+str(nowVar.minute)+':'+str(nowVar.second)+' '+str(nowVar.year)+'/'+\
                                                            str(nowVar.month)+'/'+str(nowVar.day)
        #Print to screen output
        print '[SETUP - '+str(timeVar)+'] '+str(textVar)
        return

constellationRenderConsoleClass()