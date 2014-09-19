__author__ = 'andrew.willis'

#Constellation Render Manager - Client Service Module
#Andrew Willis 2014

#import standard module
import os, shutil, sys, sqlite3, imp, time, threading, thread, socket
import hashlib, datetime, socket, subprocess
from multiprocessing import Process
import xml.etree.cElementTree as ET
from threading import Thread

#import renderer module
import crRendererMayaMray, crControllerCore

#Determining root path
rootPathVar=os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

#Connect to database
if os.path.isfile(rootPathVar+'/constellationDatabase.db')==False:
    raise StandardError, 'error : constellation database non-exists'
connectionVar=sqlite3.connect(rootPathVar+'/constellationDatabase.db')

#Determining client name
clientName=str(socket.gethostname())

#Determining system root
systemRootVar = str(os.environ['WINDIR']).replace('\\Windows','')

#This function start cyclic process only in client module.
def startService():
    statPrint('starting client service')
    #Check if the client has been registered to the database
    allClientLis=connectionVar.execute("SELECT * FROM constellationClientTable")
    templis=[]
    for chk in allClientLis:
        templis.append(chk[1])
    if clientName not in templis:
        statPrint(clientName+' is not registered as a client')
        raise StandardError, 'error : client has not been registered'

    #check local workspace made
    if os.path.isdir(systemRootVar+'/crClient')==False:
        os.makedirs(systemRootVar+'/crClient')
        os.makedirs(systemRootVar+'/crClient/tempRender')
        statPrint('local workspace created')

    #set client to enabled
    connectionVar.execute("UPDATE constellationClientTable SET"\
        " clientBlocked='ENABLED' WHERE clientName='"+str(clientName)+"'")

    #Fetch client setting from database
    clientSetting=(connectionVar.execute("SELECT * FROM constellationClientTable WHERE clientName='"\
                                        +str(socket.gethostname())+"'").fetchall())
    if len(clientSetting)!=1:
        statPrint('database respond anomaly')
        raise StandardError, 'error : database respond anomaly'
    clientSetting=clientSetting[0]

    #start hail server
    try:
        thread.start_new_thread(hailServer,(clientSetting,))
        statPrint('hail service started')
    except Exception as e:
        raise StandardError, str(e)

    #Executing instruction function
    print ''
    while True:
        statPrint('--render cycle start--')
        instructionFunc(clientSetting)
        statPrint('--render cycle end--')
        print ''
        time.sleep(3)
    return


#hail function service
def hailServer(clientSetting):
    socketVar=socket.socket()
    host=socket.gethostname()
    port=1989+int(clientSetting[0])
    socketVar.bind((host,port))

    socketVar.listen(5)
    while True:
        con, addr=socketVar.accept()
        messageVar=con.recv(1024)
        if messageVar=='stallCheck':
            con.send('ok')
        con.close()
    return

#This function contain all the render instruction. Customized render procedure here.
#Render instruction command : <mayaDir> -rl <layer> -s <startFrame> -e <endFrame> <filePath>
def instructionFunc(clientSetting):
    #Re-fetch client setting from database
    clientSetting=(connectionVar.execute("SELECT * FROM constellationClientTable WHERE clientName='"\
                                        +str(socket.gethostname())+"'").fetchall())
    if len(clientSetting)!=1:
        statPrint('database respond anomaly')
        raise StandardError, 'error : database respond anomaly'
    clientSetting=clientSetting[0]

    #Check client activatiqon status
    if clientSetting[3]=='ENABLED':
        #THREAD AND MEMORY==================================================================================================
        #work hour is not fullly developed therefore only the programmer can alter the value
        #default will be set to run full force starting 2200 until 0900 from monday to friday
        #given all weekend the render will running full. This working hour treatment will be different
        #between renderer

        #determining thread and memory limit for each client

        #get current time and data
        currentVar=time.strftime("%I%M%p")
        currentTime=currentVar[:-2]
        currentClock=currentVar[-2:]

        #read working time instruction
        if os.path.isfile(systemRootVar+'/crClient/data/workHour.xml'):
            tree=ET.parse(systemRootVar+'/crClient/data/workHour.xml')
            root=tree.getroot()

            if len(root)!=7:
                raise StandardError, 'error : corrupted work hour instruction data'

            dayData=root[int(time.strftime("%w"))]
            tempStart= dayData.get('workHourStart')
            startTime=tempStart[:-2]
            startClock=tempStart[-2:]
            tempEnd= dayData.get('workHourEnd')
            endTime=tempEnd[:-2]
            endClock=tempEnd[-2:]

            #check back if the workhour system failed
            if (int(currentTime>=int(startTime) and currentClock==startClock)or int(currentTime<=int(endTime) and currentClock==endClock)):
                #workhour thread and memory
                useThread=str(clientSetting[6])
                useMemory=str(clientSetting[7])
            else:
                #happyhour thread and memory
                useThread=str(clientSetting[4])
                useMemory=str(clientSetting[5])
        else:
            useThread='0'
            useMemory='0'
        #THREAD AND MEMORY==================================================================================================

        if not useThread=='-1' or not useMemory=='-1':
            jobToRender=None
            #HAIL==========================================================================================================
            #hail transfer stalled job from one system to another by
            #check all the client that is rendering but not responding.
            statPrint('starting hail routine')
            clientList=crControllerCore.listAllClient()
            for clientRow in clientList:
                if str(clientRow[9])=='RENDERING' and clientRow[1] != clientName:
                    statPrint('hailing '+clientRow[1])
                    hailCon=socket.socket()
                    hailHost=clientRow[1]
                    hailPort=1989+int(clientRow[0])
                    repVar=None
                    try:
                        hailCon.connect((hailHost, hailPort))
                        hailCon.send('stallCheck')
                        repVar=hailCon.recv(1024)
                        hailCon.close()
                    except:
                        pass
                    if repVar==None:
                        statPrint('stalled job detected jobId='+str(clientRow[2]))
                        allJob=crControllerCore.listAllJob()
                        for chk in allJob:
                            #compare if the id match and the classification match as well
                            if str(chk[0])==str(clientRow[2]) and str(chk[15])==str(clientSetting[8]):
                                jobToRender=chk
                                statPrint('taking over job '+str(jobToRender[1])+' from '+str(clientRow[2]))
            if jobToRender==None:
                statPrint('no stalled job')
            #HAIL==========================================================================================================

            #FETCH NEW=====================================================================================================
            #by this stage if jobToRender is still None means there are no stall system
            if jobToRender==None:
                #Fetch all job array
                allJobLis=connectionVar.execute("SELECT * FROM constellationJobTable WHERE jobBlocked='ENABLED' "\
                    "AND jobStatus='QUEUE' AND jobClassification='"+str(clientSetting[8])+"'").fetchall()

                #Check if array result is empty. Empty list mean there are neither ENABLED or QUEUE job in database
                if allJobLis!=[]:
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
            #FETCH NEW=====================================================================================================

            #RENDERER======================================================================================================
            if jobToRender!=None:
                #find job renderer and pass the job to each individual renderer
                if jobToRender[4]=='maya-mray':
                    crRendererMayaMray.render(clientSetting,jobToRender, useThread, useMemory, connectionVar)
                elif jobToRender[4]=='maya-vray':
                    vrayRenderer(clientSetting,jobToRender)
            #RENDERER======================================================================================================
        else:
            statPrint('client disabled - work mem and thread block')
    else:
        statPrint('client disabled - database block')
    return

def statPrint(textVar):
    time.sleep(0.2)
    nowVar=datetime.datetime.now()
    timeVar=str(nowVar.hour)+':'+str(nowVar.minute)+':'+str(nowVar.second)+' '+str(nowVar.year)+'/'+\
                                                        str(nowVar.month)+'/'+str(nowVar.day)
    #Print to screen output
    print '['+str(timeVar)+'] '+str(textVar)
    return

startService()