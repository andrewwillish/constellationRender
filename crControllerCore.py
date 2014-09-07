__author__ = 'andrew.willis'

#Shepard Render - Controller Module
#Andrew Willis 2014

#Module import
import os, shutil, sys, sqlite3, imp, subprocess
import hashlib, time, datetime, socket
import xml.etree.cElementTree as ET

#Determining root path
rootPathVar=os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

#Connect to database
if os.path.isfile(rootPathVar+'/constellationDatabase.db')==False:
    raise StandardError, 'error : constellation database non-exists'
connectionVar=sqlite3.connect('constellationDatabase.db')

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
def openOutput(uid=None):
    recordVar=connectionVar.execute("SELECT * FROM constellationJobTable WHERE jobUuid='"+str(uid)+"'").fetchall()
    recordVar=recordVar[0]

    pathInstructionVar=recordVar[6]
    layerVar=recordVar[9]
    cameraVar=recordVar[14]
    sceneVar=recordVar[5]
    sceneVar=sceneVar[sceneVar.rfind('/')+1:sceneVar.rfind('.ma')]

    pathInstructionVar=pathInstructionVar[:pathInstructionVar.rfind('/')]
    pathInstructionVar=pathInstructionVar.replace('<Layer>',str(layerVar))
    pathInstructionVar=pathInstructionVar.replace('<Camera>',str(cameraVar))
    pathInstructionVar=pathInstructionVar.replace('<Scene>',str(sceneVar))

    print pathInstructionVar

    subprocess.Popen(r'explorer /select,"'+pathInstructionVar.replace('/','\\')+'\\'+'"')
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
def changeJobRecord(uid=None, enabler=None):
    #Validate uid. Make sure its not None
    if uid==None:
        raise ValueError, 'error : no id specified'

    #Change job enabler. Enabler used to block and prevent a job being rendered by client.
    #Note enabler: 0=SUSPENDED 1=ENABLED
    if enabler!=None:
        if enabler not in [0,1]:
            raise ValueError, 'error : invalid value'

        if enabler==0:
            enabler='DISABLED'
        elif enabler==1:
            enabler='ENABLED'

        connectionVar.execute("UPDATE constellationJobTable SET jobEnabler='"+enabler+"' WHERE jobUuid='"+str(uid)+"'")
        connectionVar.commit()

    return

#This function list all client
def listAllClient():
    returnLis=(connectionVar.execute("SELECT * FROM constellationClientTable")).fetchall()
    if returnLis==[]:
        returnLis=['<no client registered to the network>']
    return returnLis

#This function change client status
def changeClientStatus(clientName=None, status=None, blockClient=None,offline=None):
    #Validate client id
    if clientName==None:
        raise ValueError, 'error : no id specified'

    #Processing status
    if status!=None:
        connectionVar.execute("UPDATE constellationClientTable SET clientStatus='"+status+"' WHERE clientName='"+str(clientName)+"'")
        connectionVar.commit()

    #Processing blockClient
    #Algorithm will check if the client is rendering or not. If its rendering the status will be stopping instead
    #of SUSPENDED. This is to avoid confusion later on.
    if blockClient!=None:
        if blockClient==True:
            clientBlocked='SUSPENDED'
            #Compare clientName with listAllClient() to find out client is rendering or not.
            for clientCheck in listAllClient():
                if clientCheck[1]==clientName:
                    if clientCheck[4]=='RENDERING':
                        clientBlocked='STOPPING'

            connectionVar.execute("UPDATE constellationClientTable SET clientBlocked='"+clientBlocked+"' WHERE clientName='"+str(clientName)+"'")
            connectionVar.commit()
        elif blockClient==False:
            connectionVar.execute("UPDATE constellationClientTable SET clientBlocked='ACTIVE' WHERE clientName='"+str(clientName)+"'")
            connectionVar.commit()

    if offline==True:
        connectionVar.execute("UPDATE constellationClientTable SET clientBlocked='STOPPING-OFF' WHERE clientName='"+str(clientName)+"'")
        connectionVar.commit()
    elif offline==False:
        connectionVar.execute("UPDATE constellationClientTable SET clientBlocked='ACTIVE' WHERE clientName='"+str(clientName)+"'")
        connectionVar.commit()
    return