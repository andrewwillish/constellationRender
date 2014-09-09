__author__ = 'andrew.willis'

#Constellation Render Manager - Client Service Module
#Andrew Willis 2014

#Module import
import os, shutil, sys, sqlite3, imp, time, threading, thread
import hashlib, time, datetime, socket, subprocess
from multiprocessing import Process
import xml.etree.cElementTree as ET
from threading import Thread

#Determining root path
rootPathVar=os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

#Connect to database
if os.path.isfile(rootPathVar+'/constellationDatabase.db')==False:
    raise StandardError, 'error : constellation database non-exists'
connectionVar=sqlite3.connect('constellationDatabase.db')

#Determining client name
clientName=str(socket.gethostname())

#Determining system root
systemRootVar = str(os.environ['WINDIR']).replace('\\Windows','')

#This function start cyclic process only in client module.
def setupClient(classification=None):
    #validate classification
    if classification==None:
        raise StandardError, 'error : client classification not specified'

    #Register client to database
    try:
        connectionVar.execute("INSERT INTO constellationClientTable "\
            "("\
            "clientName,clientBlocked,clientMemory,clientThread,clientWorkMemory,clientWorkThread,clientStatus,clientClassification)"\
            "VALUES ("\
            "'"+str(clientName)+"',"\
            "'DISABLED',"\
            "'-1',"\
            "'-1',"\
            "'-1',"\
            "'-1',"\
            "'OFFLINE',"\
            "'"+str(classification)+"')")
        connectionVar.commit()
    except Exception as e:
        raise StandardError, str(e)

    #create local workspace
    try:
        if os.path.isdir(rootPathVar+'/crClient/renderTemp')==False:
            os.makedirs(rootPathVar+'/crClient/renderTemp')
    except Exception as e:
        raise StandardError, str(e)
    return

def changeClass(classification=None):
    #validate classification
    if classification==None:
        raise StandardError, 'error : client classification not specified'

    try:
        connectionVar.execute("UPDATE constellationClientTable "\
            "SET clientClassification='"+str(classification)+"' WHERE clientName='"+str(clientName)+"'")
        connectionVar.commit()
    except Exception as e:
        raise StandardError, str(e)
    return