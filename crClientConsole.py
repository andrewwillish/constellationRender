__author__ = 'Andrewwillish'

#Constellation Render Manager - Client Console
#Andrew Willis 2014

import crControllerCore, os, time, sys, datetime, socket

os.system("cls")

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
            commandVar=raw_input('Insert Command >> ')\

            os.system('cls')

            print 'Constellation Render Manager 4.0 - Client Console'
            print ''
            #Parsing command
            if commandVar=='exit':
                print ('bye bye')
                time.sleep(2)
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
            elif commandVar=='enableClient':
                self.disableClientFun(mode='ENABLED')
            elif commandVar=='disableClient':
                self.disableClientFun(mode='DISABLED')
            elif commandVar=='clientStat':
                self.clientStat()
            elif commandVar=='setThread':
                self.setThread()
            elif commandVar=='setWorkThread':
                self.setWorkThread()
            elif commandVar=='setMemory':
                self.setMemory()
            elif commandVar=='setWorkMemory':
                self.setWorkMemory()
            else:
                print ('invalid command')
            print ''

        return

    def setWorkMemory(self):

        return

    def setWorkThread(self):

        return

    def setMemory(self):

        return

    def setThread(self):

        return

    def printHelp(self, *args):
        print 'help\t\t- Show this help menu'
        print 'setup\t\t- Setup client in this computer'
        print 'changeClass\t- Change current client classification'
        print 'startClient\t- Start client rendering service'
        print 'stopClient\t- Stop client rendering service'
        print 'enableClient\t- Enable client for rendering'
        print 'disableClient\t- Disable client for rendering'
        print 'clientStat\t- Get client current status'
        print 'setThread\t- Set client thread limit during non-work hour'
        print 'setWorkThread\t- Set client thread limit during work hour'
        print 'setMemory\t- Set client memory limit during non-work hour'
        print 'setWorkMemory\t- Set client memory limit durin work hour'
        print 'exit\t\t- Close this console'
        return

    def clientStat(self,*args):
        for chk in crControllerCore.listAllClient():
            if chk[1]==str(clientName):
                clientRec=chk
        print 'Client Name\t\t: '+clientRec[1]
        print 'Current Job\t\t: '+clientRec[2]
        print 'Block Status\t\t: '+clientRec[3]
        print 'Memory Limit\t\t: '+clientRec[4]
        print 'Thread Limit\t\t: '+clientRec[5]
        print 'Work Memory Limit\t: '+clientRec[6]
        print 'Thread Memory Limit\t: '+clientRec[7]
        print 'Client Class\t\t: '+clientRec[8]
        print 'Current Status\t\t: '+clientRec[9]
        return

    def stopClientFun(self,*args):
        crControllerCore.changeClientStatus(clientName=str(clientName),blockClient='OFFLINE',clientJob='')
        print ('client has been instructed to go offline.')
        return

    def startClientFun(self,*args):
        #start client service externally without waiting for error
        #error watching will be between client service and the renderer

        #temporarily client service will be started directly during development
        #stage for ease of debuggin (damn I'm tired)
        os.startfile(rootPathVar+'/_crClientServiceLaunch.bat')
        return

    def setupFun(self,*args):
        classVar=raw_input('Enter client classification (single alphabet) >> ')
        if len(classVar)==1:
            try:
                crControllerCore.setupClient(client=str(clientName),classification=classVar)
                print ('client registered to database')
            except Exception as e:
                print (str(e))
                print ('client registration failed')
        else:
            print ('invalid classification input')
        return

    def disableClientFun(self,mode):
        try:
            crControllerCore.changeClientStatus(clientName=str(clientName),\
                                                blockClient=str(mode))
            print ('client block status updated')
        except Exception as e:
            print (str(e))
        return

    def changeClassFun(self,*args):
        classVar=raw_input('Enter client new classification (A-Z) >> ')
        if len(classVar)==1:
            try:
                crControllerCore.changeClass(client=clientName,classification=classVar)
                print ('client classification changed')
            except Exception as e:
                print (str(e))
        else:
            print ('invalid classification input')
        return

crClientConsoleClass()