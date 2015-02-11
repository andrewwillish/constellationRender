__author__ = 'andrew.willis'

#Shepard Render - Controller Module
#Andrew Willis 2014

#Module import
import os, sqlite3, subprocess
import socket
import xml.etree.cElementTree as ET
import uuid
import struct

#Determining root path
rootPathVar = os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

#Determining system root
systemRootVar = str(os.environ['WINDIR']).replace('\\Windows','')

#Connect to database
if not os.path.isfile(rootPathVar+'/constellationDatabase.db'): raise StandardError, 'error : constellation database non-exists'
connectionVar = sqlite3.connect(rootPathVar+'/constellationDatabase.db')

#wake on lan
def wolTrig(client=None):
    clientSetting = None
    for clientParse in listAllClient():
        if clientParse[1] == client:
            clientSetting = clientParse

    if clientSetting is not None:
        macaddress = clientSetting[10]
        # Check macaddress format and try to compensate.
        if len(macaddress) == 12:
            pass
        elif len(macaddress) == 12 + 5:
            sep = macaddress[2]
            macaddress = macaddress.replace(sep, '')
        else:
            raise ValueError('Incorrect MAC address format')

        # Pad the synchronization stream.
        data = ''.join(['FFFFFFFFFFFF', macaddress * 20])
        send_data = ''

        # Split up the hex values and pack.
        for i in range(0, len(data), 2):
            send_data = ''.join([send_data,
                                 struct.pack('B', int(data[i: i + 2], 16))])

        # Broadcast it to the LAN.
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(send_data, ('<broadcast>', 7))
    return

#client communication
def clientCom(client=None, message = None, portBase = None):
    if client is None or message is None or portBase is None: raise StandardError, 'no client specified'
    clientSetting = None
    for clientParse in listAllClient():
        if clientParse[1] == client:
            clientSetting = clientParse

    if clientSetting is not None:
        socketVar = socket.socket()
        host = str(clientSetting[1])
        port = int(portBase) + int(clientSetting[0])
        socketVar.connect((host, port))
        socketVar.send(str(message))
        socketVar.close()
    return

#This function start cyclic process only in client module.
def setupClient(client = None, classification = None):
    #validate classification
    if classification is None or client is None: raise StandardError, 'error : client classification not specified'

    #Register client to database
    try:
        macAddr = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
        connectionVar.execute("INSERT INTO constellationClientTable "\
            "("\
            "clientName,clientBlocked,clientMemory,clientThread,clientWorkMemory,clientWorkThread,clientStatus,clientClassification,clientJob,clientMacAddr)"\
            "VALUES ("\
            "'"+str(client)+"',"\
            "'OFFLINE',"\
            "'0',"\
            "'0',"\
            "'0',"\
            "'0',"\
            "'STANDBY',"\
            "'"+str(classification)+"',"\
            "'',"\
            "'"+str(macAddr)+"')")
        connectionVar.commit()
    except Exception as e:
        raise StandardError, str(e)

    #create local workspace
    try:
        if not os.path.isdir(systemRootVar+'/crClient/renderTemp'):
            os.makedirs(systemRootVar+'/crClient/renderTemp')
            os.makedirs(systemRootVar+'/crClient/data')
    except Exception as e:
        raise StandardError, str(e)

    #create working hour .xml
    try:
        root = ET.Element("root")
        sunday = ET.SubElement(root,'sunday')
        sunday.set('workHourStart','-')
        sunday.set('workHourEnd','-')
        monday = ET.SubElement(root,'monday')
        monday.set('workHourStart','0800AM')
        monday.set('workHourEnd','1000PM')
        tuesday = ET.SubElement(root,'tuesday')
        tuesday.set('workHourStart','0800AM')
        tuesday.set('workHourEnd','1000PM')
        wednesday = ET.SubElement(root,'wednesday')
        wednesday.set('workHourStart','0800AM')
        wednesday.set('workHourEnd','1000PM')
        thursday = ET.SubElement(root,'thursday')
        thursday.set('workHourStart','0800AM')
        thursday.set('workHourEnd','1000PM')
        friday = ET.SubElement(root,'friday')
        friday.set('workHourStart','0800AM')
        friday.set('workHourEnd','1000PM')
        saturday = ET.SubElement(root,'saturday')
        saturday.set('workHourStart','-')
        saturday.set('workHourEnd','-')
        tree = ET.ElementTree(root)
        tree.write(systemRootVar+'/crClient/data/workHour.xml')
    except Exception as e:
        raise StandardError, str(e)
    return

#change class of a client
def changeClass(client=None,classification=None):
    #validate classification
    if classification is None or client is None:
        raise StandardError, 'error : client classification or name are not specified'

    try:
        connectionVar.execute("UPDATE constellationClientTable "\
            "SET clientClassification='"+str(classification)+"' WHERE clientName='"+str(client)+"'")
        connectionVar.commit()
    except Exception as e:
        raise StandardError, str(e)
    return

#This function list all recorded job.
def listAllJob():
    returnLis = (connectionVar.execute("SELECT * FROM constellationJobTable")).fetchall()
    return returnLis

#This function list all job grouped based on uuid
def listAllJobGrouped():
    allLis = (connectionVar.execute("SELECT * FROM constellationJobTable")).fetchall()

    tempLis = []
    uuidLis = []
    groupedJobLis = []
    currentRecVar = ''

    for chk in allLis:
        if chk[1] != currentRecVar:
            uuidLis.append(chk[1])
            currentRecVar = chk[1]

    for chk in uuidLis:
        for chb in allLis:
            if chk in chb:
                tempLis.append(chb)
        groupedJobLis.append(tempLis)
        tempLis = []
    return groupedJobLis

#This function search for job with specific field in it.
def searchJob(id=None, project=None, user=None, software=None, scriptPath=None,\
            status=None, priorityAbove=None, priorityBelow=None):
    #Get all recorded job from database
    allJobLis = (connectionVar.execute("SELECT * FROM constellationJobTable")).fetchall()

    #Declaring tempLis for temporary structural search
    #Search will systematically done by searching one condition, save it to a list, then re-search it again with
    #next condition. This way all condition can be met.
    tempLis = []
    towriteLis = allJobLis

    #Search by ID
    if id is not None:
        for check in towriteLis:
            if str(id) == str(check[0]):
                tempLis.append(check)
        towriteLis = tempLis

    #Search by project
    if user is not None:
        for check in towriteLis:
            if str(user) == str(check[1]):
                tempLis.append(check)
        towriteLis = tempLis

    #Search by user
    if user is not None:
        for check in towriteLis:
            if str(user) == str(check[2]):
                tempLis.append(check)
        towriteLis = tempLis

    #Search by software
    if software is not None:
        if software == 0:
            software = 'maya'
        elif software == 1:
            software = 'nuke'
        if software == 'maya' or software == 'nuke':
            for check in towriteLis:
                if str(software) == str(check[3]):
                    tempLis.append(check)
            towriteLis = tempLis
        else:
            raise ValueError, 'error : invalid software value'

    #Search by scriptPath
    if scriptPath is not None:
        for check in towriteLis:
            if str(check[4]).find(str(scriptPath)) != -1:
                tempLis.append(check)
        towriteLis = tempLis

    #Search by user
    if status is not None:
        for check in towriteLis:
            if str(status) == str(check[8]):
                tempLis.append(check)
        towriteLis = tempLis

    #Search by priorityAbove
    if priorityAbove is not None:
        for check in towriteLis:
            if int(priorityAbove) <= int(check[10]):
                tempLis.append(check)
        towriteLis = tempLis

    #Search by priorityBelow
    if priorityBelow is not None:
        for check in towriteLis:
            if int(priorityBelow) >= int(check[10]):
                tempLis.append(check)
        towriteLis = tempLis
    return towriteLis

#This function open output folder
def openOutput(uid=None):
    recordVar = connectionVar.execute("SELECT * FROM constellationJobTable WHERE jobUuid='"+str(uid)+"'").fetchall()
    recordVar = recordVar[0]

    pathInstructionVar = recordVar[6]
    layerVar = recordVar[9]
    cameraVar = recordVar[14]
    sceneVar = recordVar[5]
    sceneVar = sceneVar[sceneVar.rfind('/')+1:sceneVar.rfind('.ma')]


    renderer = recordVar[4]
    if renderer == 'maya-vray':
        pathInstructionVar = pathInstructionVar[:pathInstructionVar.rfind('/')]
        pathInstructionVar = pathInstructionVar.replace('<Layer>',str(layerVar))
        pathInstructionVar = pathInstructionVar.replace('<Camera>',str(cameraVar))
        pathInstructionVar = pathInstructionVar.replace('<Scene>',str(sceneVar))

        subprocess.Popen(r'explorer /select,"'+pathInstructionVar.replace('/','\\')+'\\'+'"')

    elif renderer == 'maya-mray':
        pathInstructionVar = pathInstructionVar[:pathInstructionVar.rfind('/')]
        pathInstructionVar = pathInstructionVar.replace('<RenderLayer>',str(layerVar))
        pathInstructionVar = pathInstructionVar.replace('<Camera>',str(cameraVar))
        pathInstructionVar = pathInstructionVar.replace('<Scene>',str(sceneVar))
        pathInstructionVar = pathInstructionVar.replace('<RenderPass>','')
        pathInstructionVar = pathInstructionVar.replace ('\\', '/')

    if pathInstructionVar != '':
        if os.path.isdir(pathInstructionVar):
            subprocess.Popen(r'explorer /select,"'+pathInstructionVar.replace('/','\\')+'\\'+'"')
        else:
            raise StandardError, 'error : directory not found'
    return

#clear job status
def clearStat(clientName=None):
    #validate parameter
    if clientName is None: raise StandardError, 'no client name specified'

    #check if there is any stalled rendering. clear it back to queue.
    for client in listAllClient():
        if clientName == str(client[1]) and client[2] != '':
            try:
                connectionVar.execute("UPDATE constellationJobTable SET jobStatus='QUEUE' WHERE jobId='"+str(client[2])+"'")
                connectionVar.commit()
                connectionVar.execute("UPDATE constellationClientTable SET clientJob='', clientStatus='STANDBY' WHERE clientName='"+str(clientName)+"'")
                connectionVar.commit()
            except:
                pass
    return

#delete client
def deleteClient(clientName = None):
    #validate parameter
    if clientName is None: raise StandardError, 'no client name specified'

    #check if there is any stalled rendering. clear it back to queue.
    for client in listAllClient():
        if clientName == str(client[1]) and client[2] != '':
            try:
                connectionVar.execute("UPDATE constellationJobTable SET jobStatus='QUEUE' WHERE jobId='"+str(client[2])+"'")
                connectionVar.commit()
            except:
                pass

    #database delete query
    connectionVar.execute("DELETE FROM constellationClientTable WHERE clientName='"+str(clientName)+"'")
    connectionVar.commit()
    return

#generate command line and export it to batch file
def genBatch(uuid = None):
    jobData = connectionVar.execute("SELECT * FROM constellationJobTable WHERE jobUuid='"+str(uuid)+"'").fetchall()
    startMark = jobData[0][7]
    endMark = jobData[len(jobData)-1][8]

    rendererPath = None
    if os.path.isfile(rootPathVar+'/renderer.xml'):
        tree = ET.parse(rootPathVar+'/renderer.xml')
        root = tree.getroot()

        for chk in root:
            if str(chk.tag) == str(jobData[0][4]):
                rendererPath = chk.text

    renderInst=str(rendererPath)+' -rl '+str(jobData[0][9])+' -cam '+str(jobData[0][14])+' -s '+\
               str(startMark)+' -e '+\
               str(endMark)+' -mr:rt '+\
               str(0)+' -mr:mem '+\
               str(0)+' '+'"'+str(jobData[0][5]).replace('/','\\')+'"'
    return renderInst

#This function will delete all or done job by uid
def clearJobRecord(uid=None, done=False, all=False):
    #validate parameter
    if done and all:raise StandardError, 'error : dobule operation not allowed'

    #Delete all DONE job
    if done:
        for chk in listAllJobGrouped():
            tempStatusLis = []
            countStatusDone = 0
            countStatusRendering = 0
            countStatusQueue = 0
            for chb in chk:
                if chb[10] == 'DONE':
                    countStatusDone += 1
                if chb[10] == 'RENDERING':
                    countStatusRendering += 1
                if chb[10] == 'QUEUE':
                    countStatusQueue += 1
                tempStatusLis.append(chb[10])
            if countStatusDone == len(tempStatusLis):
                statusinVar = 'DONE'
            elif countStatusQueue == len(tempStatusLis):
                statusinVar = 'QUEUE'
            elif countStatusRendering > 0:
                statusinVar = 'RENDERING'
            elif countStatusDone > 0 and countStatusQueue > 0 and countStatusRendering == 0:
                statusinVar = 'HALTED'

            if statusinVar == 'DONE':
                for chb in chk:
                    connectionVar.execute("DELETE FROM constellationJobTable WHERE jobUuid='"+chb[1]+"'")
                    connectionVar.commit()

    #Delete all job
    if all:
        connectionVar.execute("DELETE FROM constellationJobTable;")
        connectionVar.commit()

        for clItem in listAllClient():
            connectionVar.execute("UPDATE constellationClientTable SET clientJob = '' WHERE clientId='"+str(clItem[0])+"'")
            connectionVar.commit()

    #Delete job based by UUID
    if uid is not None:
        groupedJob = connectionVar.execute("SELECT * FROM constellationJobTable WHERE jobUuid='"+str(uid)+"'").fetchall()
        for item in groupedJob:
            jobId = str(item[0])
            for clItem in listAllClient():
                currentJob = clItem[2]
                if jobId == currentJob:
                    connectionVar.execute("UPDATE constellationClientTable SET clientJob = '' WHERE clientId='"+str(clItem[0])+"'")
                    connectionVar.commit()

                    #continue here to force the running process to stop and restart the client

        connectionVar.execute("DELETE FROM constellationJobTable WHERE jobUuid='"+str(uid)+"'")
        connectionVar.commit()
    return

#This function reset job record
def resetJobRecord(uid=None):
    #validate parameter
    if uid is None: raise ValueError, 'error : no id entered'

    allJobLis = listAllJobGrouped()
    for chk in allJobLis:
        if chk[0][1] == str(uid): filePath = chk[0][6]

    filePath = filePath.replace('\\', '/')
    filePath = filePath[:filePath.rfind('/')]

    if os.path.isdir(filePath):
        for itm in os.listdir(filePath):
            try:
                os.remove(filePath+'/'+itm)
            except:
                pass

    connectionVar.execute("UPDATE constellationJobTable SET jobStatus='QUEUE' WHERE jobUuid='"+uid+"'")
    connectionVar.commit()
    return

#This function will change job record massively or singularly
def changeJobPrior(uid=None, priority=None):
    #validate parameter
    if uid is None or priority is None:raise ValueError, 'error : empty record'

    connectionVar.execute("UPDATE constellationJobTable SET jobPriority='"+str(priority)+"' WHERE jobUuid='"+str(uid)+"'")
    connectionVar.commit()
    return

#This function will change job record attribute
def changeJobRecord(jobId=None, status=None):
    #validate parameter
    if jobId is None:raise ValueError, 'error : no id specified'

    #change job status
    if status is not None:
        connectionVar.execute("UPDATE constellationJobTable SET jobStatus='"+str(status)+"' WHERE jobId='"+str(jobId)+"'")
        connectionVar.commit()
    return

#This function will change job record attribute
def changeJobRecordBlocked(jobUuid=None, blockStatus=None):
    #validate parameter
    if jobUuid is None:raise ValueError, 'error : no id specified'

    if blockStatus is not None:
        connectionVar.execute("UPDATE constellationJobTable SET jobBlocked='"+str(blockStatus)+"' WHERE jobUuid='"+str(jobUuid)+"'")
        connectionVar.commit()
    return

#This function list all client.
def listAllClient():
    returnLis = (connectionVar.execute("SELECT * FROM constellationClientTable")).fetchall()
    if returnLis == []:returnLis = ['<no client registered to the network>']
    return returnLis

#This function change client status
def changeClientStatus(clientName=None, status=None, blockClient=None, clientJob=None):
    #validate parameter
    if clientName is None: raise ValueError, 'error : no id specified'

    #Processing status
    if status is not None:
        connectionVar.execute("UPDATE constellationClientTable SET clientStatus='"+status+"' WHERE clientName='"+str(clientName)+"'")
        connectionVar.commit()

    #Processing blockClient
    if blockClient is not None:
        if blockClient == 'DISABLED':
            connectionVar.execute("UPDATE constellationClientTable SET clientBlocked='DISABLED' WHERE clientName='"+str(clientName)+"'")
            connectionVar.commit()
        elif blockClient == 'ENABLED':
            connectionVar.execute("UPDATE constellationClientTable SET clientBlocked='ENABLED' WHERE clientName='"+str(clientName)+"'")
            connectionVar.commit()
        elif blockClient == 'OFFLINE':
            connectionVar.execute("UPDATE constellationClientTable SET clientBlocked='OFFLINE' WHERE clientName='"+str(clientName)+"'")
            connectionVar.commit()

    if clientJob is not None:
        connectionVar.execute("UPDATE constellationClientTable SET clientJob='"+str(clientJob)+"' WHERE clientName='"+str(clientName)+"'")
        connectionVar.commit()
    return