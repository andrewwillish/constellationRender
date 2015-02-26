__author__ = 'andrew.willis'

import socket
import os
import sys
import sqlite3
import crControllerCore

rootPathVar = os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

socketObj = socket.socket()
hostName = socket.gethostname()
portNum = None
for clientelle in crControllerCore.listAllClient():
    if clientelle[1] == hostName: portNum = 1991 + int(clientelle[0])

if portNum is not None:
    socketObj.bind((hostName, portNum))
    socketObj.listen(5)
    while True:
        socketVar, addr = socketObj.accept()
        recData = socketVar.recv(1024)
        print recData
        if str(recData) == 'wakeUp' and os.path.isfile('_crClientService.bat'):
            os.startfile('_crClientService.bat')
        socketVar.close()
else:
    sys.exit(0)