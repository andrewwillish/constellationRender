__author__ = 'andrew.willis'

#Shepard Render - Controller Module
#Andrew Willis 2014

#Module import
import os, shutil, sys, sqlite3, imp, subprocess
import hashlib, time, datetime, socket
import xml.etree.cElementTree as ET

#Determining root path
rootPathVar=os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

#Determining system root
systemRootVar = str(os.environ['WINDIR']).replace('\\Windows','')

#Connect to database
if os.path.isfile(rootPathVar+'/constellationDatabase.db')==False:
    raise StandardError, 'error : constellation database non-exists'
connectionVar=sqlite3.connect(rootPathVar+'/constellationDatabase.db')

#This function start cyclic process only in client module.
def setupClient(client=None,classification=None):
    #validate classification
    if classification==None or client==None:
        raise StandardError, 'error : client classification not specified'

    #Register client to database
    try:
        connectionVar.execute("INSERT INTO constellationClientTable "\
            "("\
            "clientName,clientBlocked,clientMemory,clientThread,clientWorkMemory,clientWorkThread,clientStatus,clientClassification)"\
            "VALUES ("\
            "'"+str(client)+"',"\
            "'DISABLED',"\
            "'0',"\
            "'0',"\
            "'0',"\
            "'0',"\
            "'OFFLINE',"\
            "'"+str(classification)+"')")
        connectionVar.commit()
    except Exception as e:
        raise StandardError, str(e)

    #create local workspace
    try:
        print systemRootVar+'/crClient/renderTemp'
        if os.path.isdir(systemRootVar+'/crClient/renderTemp')==False:
            os.makedirs(systemRootVar+'/crClient/renderTemp')
            os.makedirs(systemRootVar+'/crClient/data')
    except Exception as e:
        raise StandardError, str(e)

    #create working hour .xml
    try:
        root=ET.Element("root")
        sunday=ET.SubElement(root,'sunday')
        sunday.set('workHourStart','-')
        sunday.set('workHourEnd','-')
        monday=ET.SubElement(root,'monday')
        monday.set('workHourStart','0800AM')
        monday.set('workHourEnd','1000PM')
        tuesday=ET.SubElement(root,'tuesday')
        tuesday.set('workHourStart','0800AM')
        tuesday.set('workHourEnd','1000PM')
        wednesday=ET.SubElement(root,'wednesday')
        wednesday.set('workHourStart','0800AM')
        wednesday.set('workHourEnd','1000PM')
        thursday=ET.SubElement(root,'thursday')
        thursday.set('workHourStart','0800AM')
        thursday.set('workHourEnd','1000PM')
        friday=ET.SubElement(root,'friday')
        friday.set('workHourStart','0800AM')
        friday.set('workHourEnd','1000PM')
        saturday=ET.SubElement(root,'saturday')
        saturday.set('workHourStart','-')
        saturday.set('workHourEnd','-')
        tree=ET.ElementTree(root)
        tree.write(systemRootVar+'/crClient/data/workHour.xml')
    except Exception as e:
        raise StandardError, str(e)
    return

def changeClass(client=None,classification=None):
    #validate classification
    if classification==None or client==None:
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
    returnLis=(connectionVar.execute("SELECT * FROM constellationJobTable")).fetchall()
    return returnLis

#This function list all job grouped based on uuid
def listAllJobGrouped():
    allLis=(connectionVar.execute("SELECT * FROM constellationJobTable")).fetchall()

    tempLis=[]
    uuidLis=[]
    groupedJobLis=[]
    currentRecVar=''

    for chk in allLis:
        if chk[1]!=currentRecVar:
            uuidLis.append(chk[1])
            currentRecVar=chk[1]

    for chk in uuidLis:
        for chb in allLis:
            if chk in chb:
                tempLis.append(chb)
        groupedJobLis.append(tempLis)
        tempLis=[]
    return groupedJobLis

#This function search for job with specific field in it.
def searchJob(id=None, project=None, user=None, software=None, scriptPath=None,\
            status=None, priorityAbove=None, priorityBelow=None):
    #Get all recorded job from database
    allJobLis=(connectionVar.execute("SELECT * FROM constellationJobTable")).fetchall()

    #Declaring tempLis for temporary structural search
    #Search will systematically done by searching one condition, save it to a list, then re-search it again with
    #next condition. This way all condition can be met.
    tempLis=[]
    towriteLis=allJobLis

    #Search by ID
    if id!=None:
        for check in towriteLis:
            if str(id)==str(check[0]):
                tempLis.append(check)
        towriteLis=tempLis

    #Search by project
    if user!=None:
        for check in towriteLis:
            if str(user)==str(check[1]):
                tempLis.append(check)
        towriteLis=tempLis

    #Search by user
    if user!=None:
        for check in towriteLis:
            if str(user)==str(check[2]):
                tempLis.append(check)
        towriteLis=tempLis

    #Search by software
    if software!=None:
        if software==0:
            software='maya'
        elif software ==1:
            software='nuke'
        if software=='maya' or software=='nuke':
            for check in towriteLis:
                if str(software)==str(check[3]):
                    tempLis.append(check)
            towriteLis=tempLis
        else:
            raise ValueError, 'error : invalid software value'

    #Search by scriptPath
    if scriptPath!=None:
        for check in towriteLis:
            if str(check[4]).find(str(scriptPath))!=-1:
                tempLis.append(check)
        towriteLis=tempLis

    #Search by user
    if status!=None:
        for check in towriteLis:
            if str(status)==str(check[8]):
                tempLis.append(check)
        towriteLis=tempLis

    #Search by priorityAbove
    if priorityAbove!=None:
        for check in towriteLis:
            if int(priorityAbove)<=int(check[10]):
                tempLis.append(check)
        towriteLis=tempLis

    #Search by priorityBelow
    if priorityBelow!=None:
        for check in towriteLis:
            if int(priorityBelow)>=int(check[10]):
                tempLis.append(check)
        towriteLis=tempLis

    return towriteLis

#This function open output folder
def openOutput(uid=None, renderer=None):
    recordVar=connectionVar.execute("SELECT * FROM constellationJobTable WHERE jobUuid='"+str(uid)+"'").fetchall()
    recordVar=recordVar[0]

    pathInstructionVar=recordVar[6]
    layerVar=recordVar[9]
    cameraVar=recordVar[14]
    sceneVar=recordVar[5]
    sceneVar=sceneVar[sceneVar.rfind('/')+1:sceneVar.rfind('.ma')]


    renderer=recordVar[4]
    if renderer=='maya-vray':
        pathInstructionVar=pathInstructionVar[:pathInstructionVar.rfind('/')]
        pathInstructionVar=pathInstructionVar.replace('<Layer>',str(layerVar))
        pathInstructionVar=pathInstructionVar.replace('<Camera>',str(cameraVar))
        pathInstructionVar=pathInstructionVar.replace('<Scene>',str(sceneVar))

        subprocess.Popen(r'explorer /select,"'+pathInstructionVar.replace('/','\\')+'\\'+'"')

    elif renderer=='maya-mray':
        pathInstructionVar=pathInstructionVar[:pathInstructionVar.rfind('/')]
        pathInstructionVar=pathInstructionVar.replace('<RenderLayer>',str(layerVar))
        pathInstructionVar=pathInstructionVar.replace('<Camera>',str(cameraVar))
        pathInstructionVar=pathInstructionVar.replace('<Scene>',str(sceneVar))
        pathInstructionVar=pathInstructionVar.replace('<RenderPass>','')

        pathInstructionVar=pathInstructionVar[:pathInstructionVar.rfind('\\')]
        while pathInstructionVar.endswith('\\'):
            pathInstructionVar=pathInstructionVar[:pathInstructionVar.rfind('\\')]

    if pathInstructionVar!='':
        if os.path.isdir(pathInstructionVar)==True:
            subprocess.Popen(r'explorer /select,"'+pathInstructionVar.replace('/','\\')+'\\'+'"')
        else:
            raise StandardError, 'error : directory not found'
    return

#This function will delete all or done job by uid
def clearJobRecord(uid=None, done=False, all=False):
    #Shield to prevent double operation both all and done
    if done==True and all==True:
        raise StandardError, 'error : dobule operation not allowed'

    #Delete all DONE job
    if done==True:
        for chk in listAllJobGrouped():
            tempStatusLis=[]
            countStatusDone=0
            countStatusRendering=0
            countStatusQueue=0
            for chb in chk:
                if chb[10]=='DONE':
                    countStatusDone+=1
                if chb[10]=='RENDERING':
                    countStatusRendering+=1
                if chb[10]=='QUEUE':
                    countStatusQueue+=1
                tempStatusLis.append(chb[10])
            if countStatusDone==len(tempStatusLis):
                statusinVar='DONE'
            elif countStatusQueue==len(tempStatusLis):
                statusinVar='QUEUE'
            elif countStatusRendering>0:
                statusinVar='RENDERING'
            elif countStatusDone>0 and countStatusQueue>0 and countStatusRendering==0:
                statusinVar='HALTED'

            if statusinVar=='DONE':
                for chb in chk:
                    connectionVar.execute("DELETE FROM constellationJobTable WHERE jobUuid='"+chb[1]+"'")
                    connectionVar.commit()

    #Delete all job
    if all==True:
        connectionVar.execute("DELETE FROM constellationJobTable;")
        connectionVar.commit()

    #Delete job based by UUID
    if uid!=None:
        connectionVar.execute("DELETE FROM constellationJobTable WHERE jobUuid='"+str(uid)+"'")
        connectionVar.commit()
    return

#This function reset job record
def resetJobRecord(uid=None):
    #Validate uid. Make sure its not None
    if uid==None:
        raise ValueError, 'error : no id entered'

    allJobLis=listAllJobGrouped()
    for chk in allJobLis:
        if chk[0][1]==str(uid):
            jobGroupLis=chk

    #Checking render directory make one if non exists
    pathInstructionVar=jobGroupLis[0][6]
    layerVar=jobGroupLis[0][9]
    cameraVar=jobGroupLis[0][14]
    sceneVar=jobGroupLis[0][5]
    sceneVar=sceneVar[sceneVar.rfind('/')+1:sceneVar.rfind('.ma')]

    pathInstructionVar=pathInstructionVar[:pathInstructionVar.rfind('/')]
    pathInstructionVar=pathInstructionVar.replace('<Layer>',str(layerVar))
    pathInstructionVar=pathInstructionVar.replace('<Camera>',str(cameraVar))
    pathInstructionVar=pathInstructionVar.replace('<Scene>',str(sceneVar))

    if os.path.isdir(pathInstructionVar)==False:
        os.makedirs(pathInstructionVar)

    for chk in os.listdir(pathInstructionVar):
        if os.path.isfile(pathInstructionVar+'/'+chk)==True:
            os.remove(pathInstructionVar+'/'+chk)

    connectionVar.execute("UPDATE constellationJobTable SET jobStatus='QUEUE' WHERE jobUuid='"+uid+"'")
    connectionVar.commit()
    return

#This function will change job record massively or singularly
def changeJobPrior(uid=None, priority=None):
    if uid==None or priority==None:
        raise ValueError, 'error : empty record'

    connectionVar.execute("UPDATE constellationJobTable SET jobPriority='"+str(priority)+"' WHERE jobUuid='"+str(uid)+"'")
    connectionVar.commit()
    return

#This function will change job record attribute
def changeJobRecord(jobId=None, status=None):
    #Validate uid. Make sure its not None
    if jobId==None:
        raise ValueError, 'error : no id specified'

    #change job status
    if status!=None:
        connectionVar.execute("UPDATE constellationJobTable SET jobStatus='"+str(status)+"' WHERE jobId='"+str(jobId)+"'")
        connectionVar.commit()

    return

#This function will change job record attribute
def changeJobRecordBlocked(jobUuid=None, blockStatus=None):
    #Validate uid. Make sure its not None
    if jobUuid==None:
        raise ValueError, 'error : no id specified'

    #change job status
    if blockStatus!=None:
        connectionVar.execute("UPDATE constellationJobTable SET jobBlocked='"+str(blockStatus)+"' WHERE jobUuid='"+str(jobUuid)+"'")
        connectionVar.commit()

    return

#This function list all client
def listAllClient():
    returnLis=(connectionVar.execute("SELECT * FROM constellationClientTable")).fetchall()
    if returnLis==[]:
        returnLis=['<no client registered to the network>']
    return returnLis

#This function change client status
def changeClientStatus(clientName=None,\
                       status=None,\
                       blockClient=None,\
                       clientJob=None):
    #Validate client id
    if clientName==None:
        raise ValueError, 'error : no id specified'

    #Processing status
    if status!=None:
        connectionVar.execute("UPDATE constellationClientTable SET clientStatus='"+status+"' WHERE clientName='"+str(clientName)+"'")
        connectionVar.commit()

    #Processing blockClient
    if blockClient!=None:
        if blockClient=='DISABLED':
            connectionVar.execute("UPDATE constellationClientTable SET clientBlocked='DISABLED' WHERE clientName='"+str(clientName)+"'")
            connectionVar.commit()
        elif blockClient=='ENABLED':
            connectionVar.execute("UPDATE constellationClientTable SET clientBlocked='ENABLED' WHERE clientName='"+str(clientName)+"'")
            connectionVar.commit()
        elif blockClient=='OFFLINE':
            connectionVar.execute("UPDATE constellationClientTable SET clientBlocked='OFFLINE' WHERE clientName='"+str(clientName)+"'")
            connectionVar.commit()

    if clientJob!=None:
        connectionVar.execute("UPDATE constellationClientTable SET clientJob='"+str(clientJob)+"' WHERE clientName='"+str(clientName)+"'")
        connectionVar.commit()
    return