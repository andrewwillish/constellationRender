__author__ = 'Andrewwillish'

#Constellation Render Manager - Client Console
#Andrew Willis 2014

import crControllerCore, os, time, sys, datetime, socket

#Determining client name
clientName=str(socket.gethostname())

#Determining root path
rootPathVar=os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

class crClientConsoleClass:
    def __init__(self):
        #Welcome message
        print 'Constellation Render Manager 4.0 - Client Console'
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
            elif commandVar=='changeClass':
                self.changeClassFun()
            elif commandVar=='startClient':
                self.startClientFun()
            elif commandVar=='stopClient':
                self.stopClientFun()
            else:
                self.statPrint('invalid command')
            print ''
        return

    def printHelp(self, *args):
        print 'Constellation Render Manager 4.0 - Client Console Help'
        print ''
        print 'help\t\t- Show this help menu'
        print 'setup\t\t- Setup client in this computer'
        print 'changeClass\t- Change current client classification'
        print 'startClient\t- Start client rendering service (separate instruction will be executed)'
        print 'stopClient\t- Stop client rendering service'
        print 'exit\t\t- Close this console'
        return

    def stopClientFun(self,*args):
        crControllerCore.changeClientStatus(clientName=str(clientName),blockClient='OFFLINE',clientJob='')
        self.statPrint('client has been instructed to go offline but will finish the job already assigned to it')
        return

    def startClientFun(self,*args):
        #start client service externally without waiting for error
        #error watching will be between client service and the renderer

        #temporarily client service will be started directly during development
        #stage for ease of debuggin (damn I'm tired)
        os.startfile(rootPathVar+'/crClientServiceLaunch.bat')
        return

    def setupFun(self,*args):
        classVar=raw_input('Enter client classification (single alphabet) >> ')
        if len(classVar)==1:
            try:
                crControllerCore.setupClient(client=str(clientName),classification=classVar)
                self.statPrint('client registered to database')
            except Exception as e:
                self.statPrint(str(e))
                self.statPrint('client registration failed')
        else:
            self.statPrint('invalid classification input')
        return

    def changeClassFun(self,*args):
        classVar=raw_input('Enter client new classification (single alphabet) >> ')
        if len(classVar)==1:
            try:
                crControllerCore.changeClass(client=clientName,classification=classVar)
                self.statPrint('client classification changed')
            except Exception as e:
                self.statPrint(str(e))
        else:
            self.statPrint('invalid classification input')
        return

    def statPrint(self,textVar):
        time.sleep(0.2)
        nowVar=datetime.datetime.now()
        timeVar=str(nowVar.hour)+':'+str(nowVar.minute)+':'+str(nowVar.second)+' '+str(nowVar.year)+'/'+\
                                                            str(nowVar.month)+'/'+str(nowVar.day)
        #Print to screen output
        print '['+str(timeVar)+'] '+str(textVar)
        return

crClientConsoleClass()