__author__ = 'andrew.willis'

#Constellation Render Manager - Client Service Module
#Andrew Willis 2014

#import standard module
import os, sys, sqlite3, time, thread, socket
import datetime, ctypes
import xml.etree.cElementTree as ET
import signal

#import renderer module
import crRendererMayaMray, crRendererMayaVray, crControllerCore

#Determining root path
rootPathVar = os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

#Connect to database
if not os.path.isfile(rootPathVar+'/constellationDatabase.db'): raise StandardError, 'error : constellation database non-exists'
connectionVar = sqlite3.connect(rootPathVar+'/constellationDatabase.db')

#Determining client name
clientName = str(socket.gethostname())

#Determining system root
systemRootVar = str(os.environ['WINDIR']).replace('\\Windows','')

os.system('cls')

#This function start cyclic process only in client module.
def startService():
    statPrint('starting client service', colorStat=10)
    statPrint('Constellation Render v4.2 build 0', colorStat=10)
    time.sleep(3)

    currentPid = os.getpid()

    #Check if the client has been registered to the database
    allClientLis = connectionVar.execute("SELECT * FROM constellationClientTable")
    templis = []
    for chk in allClientLis: templis.append(chk[1])
    if clientName not in templis:
        statPrint(clientName+' is not registered as a client', colorStat = 12)
        raise StandardError, 'error : client has not been registered'

    #check local workspace made
    if not os.path.isdir(systemRootVar+'/crClient'):
        os.makedirs(systemRootVar+'/crClient')
        os.makedirs(systemRootVar+'/crClient/tempRender')
        statPrint('local workspace created')

    #set client to enabled
    connectionVar.execute("UPDATE constellationClientTable SET"\
        " clientBlocked='ENABLED' WHERE clientName='"+str(clientName)+"'")
    connectionVar.commit()

    #Fetch client setting from database
    clientSetting = (connectionVar.execute("SELECT * FROM constellationClientTable WHERE clientName='"\
                                        +str(socket.gethostname())+"'").fetchall())
    if len(clientSetting) != 1:
        statPrint('database respond anomaly', colorStat = 12)
        raise StandardError, 'error : database respond anomaly'
    clientSetting = clientSetting[0]

    #start hail server
    try:
        thread.start_new_thread(hailServer,(clientSetting, currentPid, ))
        statPrint('hail service started', colorStat=10)
    except Exception as e:
        os._exit(1)
        raise StandardError, str(e)

    #Executing instruction function
    os.system('cls')
    while True:
        try:
            instructionFunc(clientSetting)
        except Exception as e:
            statPrint('General block error see log for detail', colorStat = 12)
            connectionVar.execute("INSERT INTO constellationLogTable (clientName,jobUuid,logDescription) "\
                "VALUES ('"+str(clientName)+"','n/a','error crClientService General block error:"+str(e)+"')")
    return

#hail function service
def hailServer(clientSetting, currentPid):
    socketVar = socket.socket()
    host = socket.gethostname()
    port = 1989+int(clientSetting[0])
    try:
        socketVar.bind((host,port))
    except:
        os._exit(1)
    socketVar.listen(5)
    while True:
        con, addr = socketVar.accept()
        messageVar = con.recv(1024)
        if messageVar == 'stallCheck':
            con.send('ok')
        elif messageVar == 'quit':
            os.kill(currentPid, signal.SIGTERM)
            #os.system("tskill "+str(currentPid))
        elif messageVar == 'shutDown':
            os.system("shutdown -s -t 5")
        elif messageVar == 'restart':
            os.system("shutdown -r -t 5")
        con.close()
    return

#This function contain all the render instruction. Customized render procedure here.
#Render instruction command : <mayaDir> -rl <layer> -s <startFrame> -e <endFrame> <filePath>
def instructionFunc(clientSetting):
    #Re-fetch client setting from database
    clientSetting = (connectionVar.execute(\
        "SELECT * FROM constellationClientTable WHERE clientName='"+str(socket.gethostname())+"'").fetchall())
    if len(clientSetting) != 1:
        statPrint('database respond anomaly')
        raise StandardError, 'error : database respond anomaly'
    clientSetting = clientSetting[0]

    #Check client activatiqon status
    if clientSetting[3] == 'ENABLED':
        statPrint('--render cycle start--', colorStat=3)
        #THREAD AND MEMORY==================================================================================================
        #work hour is not fullly developed therefore only the programmer can alter the value
        #default will be set to run full force starting 2200 until 0900 from monday to friday
        #given all weekend the render will running full. This working hour treatment will be different
        #between renderer

        #determining thread and memory limit for each client
        try:
            #get current time and data
            currentVar = time.strftime("%I%M%p")
            currentTime = currentVar[:-2]
            currentClock = currentVar[-2:]

            #read working time instruction
            if os.path.isfile(systemRootVar+'/crClient/data/workHour.xml'):
                tree = ET.parse(systemRootVar+'/crClient/data/workHour.xml')
                root = tree.getroot()

                if len(root) != 7: raise StandardError, 'error : corrupted work hour instruction data'

                dayData = root[int(time.strftime("%w"))]
                tempStart = dayData.get('workHourStart')
                startTime = tempStart[:-2]
                startClock = tempStart[-2:]
                tempEnd = dayData.get('workHourEnd')
                endTime = tempEnd[:-2]
                endClock = tempEnd[-2:]

                #check back if the workhour system failed
                if (int(currentTime >= int(startTime) and currentClock == startClock)or \
                        int(currentTime <= int(endTime) and currentClock == endClock)):
                    #workhour thread and memory
                    useThread = str(clientSetting[6])
                    useMemory = str(clientSetting[7])
                else:
                    #happyhour thread and memory
                    useThread = str(clientSetting[4])
                    useMemory = str(clientSetting[5])
            else:
                useThread = '0'
                useMemory = '0'
        except:
            useThread = '0'
            useMemory = '0'

        if not useThread == '-1' or not useMemory == '-1':
            jobToRender = None

            #SELF-CHECK====================================================================================================
            #check if there are previous stalled job made by current client
            if jobToRender is None:
                statPrint('checking local stalled job', colorStat=6)
                for chk in crControllerCore.listAllClient():
                    if str(chk[9]) == 'RENDERING' and str(chk[1]) == str(clientName):
                        statPrint('previous stalled job detected', colorStat=4)
                        for chb in crControllerCore.listAllJob():
                            if str(chb[0]) == str(chk[2]):
                                jobToRender = chb
                                statPrint('resuming job id:'+str(jobToRender[0]), colorStat=10)
                if jobToRender is None:
                    statPrint('no local stalled job', colorStat=2)
            #SELF-CHECK=================================================================================================

            #HAIL=======================================================================================================
            if jobToRender is None:
                #hail transfer stalled job from one system to another by
                #check all the client that is rendering but not responding.
                statPrint('checking peer stalled job', colorStat=6)
                clientList = crControllerCore.listAllClient()
                for clientRow in clientList:
                    if jobToRender is None:
                        if clientRow[1] != clientName and clientRow[2] != '':
                            statPrint('hailing '+clientRow[1], colorStat=8)
                            hailCon = socket.socket()
                            hailCon.settimeout(10)
                            hailHost = clientRow[1]
                            hailPort = 1989 + int(clientRow[0])
                            repVar = None
                            try:
                                hailCon.connect((hailHost, hailPort))
                                hailCon.send('stallCheck')
                                repVar = hailCon.recv(1024)
                                hailCon.close()
                            except:
                                pass

                            if repVar is None:
                                statPrint('stalled job detected jobId='+str(clientRow[2]), colorStat=12)
                                connectionVar.execute("UPDATE constellationClientTable SET clientJob='',clientStatus='STANDBY' WHERE clientName='"+str(clientRow[1])+"'")
                                connectionVar.commit()
                                allJob = crControllerCore.listAllJob()
                                for chk in allJob:
                                    #compare if the id match and the classification match as well
                                    if str(chk[0]) == str(clientRow[2]) and str(chk[15]) == str(clientSetting[8]):
                                        jobToRender = chk
                                        statPrint('taking over job '+str(jobToRender[1])+' from '+str(clientRow[1]), colorStat=10)
                                        #set other client as disabled
                                        connectionVar.execute("UPDATE constellationClientTable SET clientBlocked='DISABLED', clientJob='',clientStatus='STANDBY' WHERE clientName='"+str(clientRow[1])+"'")
                                        connectionVar.commit()
                if jobToRender is None:
                    statPrint('no peer stalled job', colorStat=2)
            #HAIL=======================================================================================================

            #FETCH NEW==================================================================================================
            #by this stage if jobToRender is still None means there are no stall system
            if jobToRender is None:
                #Fetch all job array
                allJobLis=connectionVar.execute("SELECT * FROM constellationJobTable WHERE jobBlocked='ENABLED' "\
                    "AND jobStatus='QUEUE' AND jobClassification='"+str(clientSetting[8])+"'").fetchall()

                #Check if array result is empty. Empty list mean there are neither ENABLED or QUEUE job in database
                if allJobLis != []:
                    #Filter job to get the highest priority
                    highestPrior = 0
                    tempLis = []
                    for jobRecord in allJobLis:
                        if int(jobRecord[13]) > highestPrior:
                            highestPrior = int(jobRecord[13])

                    #Based on the highest priority searched, get the latest job in database
                    jobToRender = None
                    for jobRecord in reversed(allJobLis):
                        if int(jobRecord[13]) == highestPrior:
                            jobToRender = jobRecord
            #FETCH NEW==================================================================================================

            #RENDERER===================================================================================================
            try:
                if jobToRender is not None:
                    #find job renderer and pass the job to each individual renderer
                    if jobToRender[4] == 'maya-mray':
                        #re-routed
                        crRendererMayaMray.render(clientSetting,jobToRender, useThread, useMemory, connectionVar)
                    elif jobToRender[4] == 'maya-vray':
                        crRendererMayaVray.render(clientSetting,jobToRender, useThread, useMemory, connectionVar)
                else:
                    statPrint('client standby - no job available', colorStat=14)
            except Exception as err:
                #renderer block error write to log
                err = str(err).replace("'", "")
                statPrint('process failed: '+str(err), colorStat=12)
                connectionVar.execute("INSERT INTO constellationLogTable (clientName,jobUuid,logDescription) "\
                    "VALUES ('"+str(clientName)+"','"+str(jobToRender[1])+"','error crClientService renderer block:"+str(err)+"')")

                #renderer block error disable render job
                connectionVar.execute("UPDATE constellationJobTable SET jobStatus='ERROR', jobBlocked='DISABLED' WHERE jobUuid='"+str(jobToRender[1])+"'")

                #renderer block error set client back to standby
                connectionVar.execute("UPDATE constellationClientTable SET clientStatus='STANDBY' "\
                    ",clientJob=''"
                    "WHERE clientName='"+clientName+"'")
                connectionVar.commit()
            #RENDERER===================================================================================================
        else:
            statPrint('client disabled - work mem and thread block', colorStat=12)
        statPrint('--render cycle end--', colorStat=3)
        print ''
        time.sleep(2)
    elif clientSetting[3] == 'DISABLED':
        statPrint('client disabled - database block', colorStat=12)
    else:
        statPrint('client instructed to shutdown', colorStat=12)
        statPrint('bye bye', colorStat=12)
        time.sleep(2)
        sys.exit()
    os.system('cls')
    return

def statPrint(textVar, colorStat = None):
    time.sleep(0.2)
    nowVar = datetime.datetime.now()
    timeVar = str(nowVar.hour)+':'+str(nowVar.minute)+':'+str(nowVar.second)+' '+str(nowVar.year)+'/'+\
                                                        str(nowVar.month)+'/'+str(nowVar.day)

    #Print to screen output
    STD_OUTPUT_HANDLE_ID = ctypes.c_ulong(0xfffffff5)
    ctypes.windll.Kernel32.GetStdHandle.restype = ctypes.c_ulong
    std_output_hdl = ctypes.windll.Kernel32.GetStdHandle(STD_OUTPUT_HANDLE_ID)
    if colorStat is None: colorStat = 15
    ctypes.windll.Kernel32.SetConsoleTextAttribute(std_output_hdl, colorStat)
    print '['+str(timeVar)+'] '+str(textVar)
    return

startService()