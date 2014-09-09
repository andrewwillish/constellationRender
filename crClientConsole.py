__author__ = 'Andrewwillish'

#Constellation Render Manager - Client Console
#Andrew Willis 2014

import crClientCore, os

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
            else:
                self.statPrint('invalid command')
            print ''
        return

    def startClientFun(self,*args):
        #start client service externally without waiting for error
        #error watching will be betwee client service and the renderer
        os.startfile()
        return

    def setupFun(self,*args):
        classVar=raw_input('Enter client classification (single alphabet) >> ')
        if len(classVar)==1:
            try:
                crClientCore.setupClient(classification=classVar)
            except Exception as e:
                self.statPrint(str(e))
        else:
            self.statPrint('invalid classification input')
        return

    def changeClassFun(self,*args):
        classVar=raw_input('Enter client new classification (single alphabet) >> ')
        if len(classVar)==1:
            try:
                crClientCore.changeClass(classification=classVar)
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