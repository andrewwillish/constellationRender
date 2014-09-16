__author__ = 'andrew.willis'

#Constellation Render Manager - Client Service Module
#Andrew Willis 2014

#import standard module
import os, shutil, sys, sqlite3, imp, time, threading, thread
import hashlib, datetime, socket, subprocess
from multiprocessing import Process
import xml.etree.cElementTree as ET
from threading import Thread

#import renderer module
import crRendererMayaMray

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
def startService():
    #Check if the client has been registered to the database
    allClientLis=connectionVar.execute("SELECT * FROM constellationClientTable")
    templis=[]
    for chk in allClientLis:
        templis.append(chk[1])
    if clientName not in templis:
        raise StandardError, 'error : client has not been registered'

    #check local workspace made
    if os.path.isdir(systemRootVar+'/crClient')==False:
        os.makedirs(systemRootVar+'/crClient')
        os.makedirs(systemRootVar+'/crClient/tempRender')

    #set client to enabled
    connectionVar.execute("UPDATE constellationClientTable SET"\
        " clientBlocked='ENABLED' WHERE clientName='"+str(clientName)+"'")

    #Executing instruction function
    while True:
        instructionFunc()
    return

#continue with render job tackling algorithm. lets go we can do this. damn im super tired.

#This function contain all the render instruction. Customized render procedure here.
#Render instruction command : <mayaDir> -rl <layer> -s <startFrame> -e <endFrame> <filePath>
def instructionFunc():
    #Fetch client setting from database
    clientSetting=(connectionVar.execute("SELECT * FROM constellationClientTable WHERE clientName='"\
                                        +str(socket.gethostname())+"'").fetchall())
    if len(clientSetting)!=1:
        raise StandardError, 'error : database respond anomaly'
    clientSetting=clientSetting[0]

    #Check client activation status
    if clientSetting[3]=='ENABLED':
        #Fetch all job array
        allJobLis=connectionVar.execute("SELECT * FROM constellationJobTable WHERE jobBlocked='ENABLED' "\
            "AND jobStatus='QUEUE'").fetchall()

        #Check if array result is empty. Empty list mean there are neither ENABLED or QUEUE job in database
        if allJobLis!=[]:
            #HAIL====================================================================

            #HAIL====================================================================

            #GET NEW JOB=============================================================
            #Filter job to get the highest priority
            highestPrior=0
            tempLis=[]
            for jobRecord in allJobLis:
                if int(jobRecord[13])>highestPrior:
                    highestPrior=int(jobRecord[13])

            #Based on the highest priority searched, get the latest job in database
            jobToRender=None
            for jobRecord in reversed(allJobLis):
                if int(jobRecord[13])==highestPrior:
                    jobToRender=jobRecord
            #GET NEW JOB=============================================================

            #find job renderer and pass the job to each individual renderer
            if jobToRender[4]=='maya-mray':
                crRendererMayaMray.render(clientSetting,jobToRender)
            elif jobToRender[4]=='maya-vray':
                vrayRenderer(clientSetting,jobToRender)
    return

startService()