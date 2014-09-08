__author__ = 'andrew.willis'

#Constellation Render 3.0 - Setup Module
#Andrew Willis 2014

#Module import
import os, shutil, sys, sqlite3, imp
import time, datetime, socket
import xml.etree.cElementTree as ET

#Determining root path
rootPathVar=os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

#This function is to add new renderer for constellation. There are 2 renderer supported until now which is
#maya and nuke. Adding supported renderer will require hard coding in client part.
def addRenderer( nameVar, pathVar):
    #Validate xml existence
    if os.path.isfile(rootPathVar+'/renderer.xml')==False:
        raise IOError, 'renderer.xml does not exists'

    #Path input validation
    if os.path.isfile(pathVar)==False:
        raise ValueError, 'error : invalid renderer path'

    #Name input validation to ensure only 0 and 1 entered
    #note: 0=maya, 1=nuke
    nameVar=int(nameVar)
    if nameVar==0:
        nameVar='maya-mray'
    elif nameVar==1:
        nameVar='maya-vray'
    elif nameVar==2:
        nameVar='maya-hardware'
    elif nameVar==3:
        nameVar='maya-software'
    elif nameVar==4:
        nameVar='nuke'
    else:
        raise ValueError, 'unsupported renderer type'

    #Quotation check within pathVar
    if pathVar.endswith('"')==False:
        pathVar=pathVar+'"'
    if pathVar.startswith('"')==False:
        pathVar='"'+pathVar

    #Fetching renderer root from renderer.xml
    tree=ET.parse(rootPathVar+'/renderer.xml')
    root=tree.getroot()

    #Checking renderer existence. To update existing renderer please delete it first then
    #enter the new one.
    tempLis=[]
    for chk in root:
        tempLis.append(str(chk.tag))
    if nameVar in tempLis:
        raise StandardError, nameVar+' renderer already registered'

    #Writing renderer to renderer.xml if there is no error from existence check
    addField=ET.SubElement(root,str(nameVar))
    addField.text=str(pathVar)
    tree=ET.ElementTree(root)
    tree.write(rootPathVar+'/renderer.xml')
    return

#This function delete renderer from renderer.xml
def deleteRenderer(nameVar):
    #Validate xml existence
    if os.path.isfile(rootPathVar+'/renderer.xml')==False:
        raise IOError, 'renderer.xml does not exists'

    #Fetching root from renderer.xml
    tree=ET.parse(rootPathVar+'/renderer.xml')
    root=tree.getroot()

    #Search and delete renderer
    removalVar=''
    for chk in root:
        if str(chk.tag)==nameVar:
            removalVar=chk

    if removalVar!='':
        root.remove(removalVar)
        tree=ET.ElementTree(root)
        tree.write(rootPathVar+'/renderer.xml')
    else:
        raise ValueError, 'no renderer named '+str(nameVar)
    return

#This function list all recorded renderer
def listRenderer():
    #Validate xml existence
    if os.path.isfile(rootPathVar+'/renderer.xml')==False:
        raise IOError, 'renderer.xml does not exists'

    allRendererLis=[]
    tree=ET.parse(rootPathVar+'/renderer.xml')
    root=tree.getroot()
    for chk in root:
        tempLis=(chk.tag,chk.text)
        allRendererLis.append(tempLis)
    if allRendererLis==[]:
        allRendererLis=['<no renderer recorded>']
    return allRendererLis

#This function setup all needed database and file for constellation render dependencies module
def setupJobTable():
    #Setup main database called constellationDatabase.db
    if os.path.isfile(rootPathVar+'/constellationDatabase.db')==False:
        connectionVar=sqlite3.connect('constellationDatabase.db')

    try:
        connectionVar=sqlite3.connect('constellationDatabase.db')
        #Create constellationJobTable to record submitted job
        connectionVar.execute("CREATE TABLE constellationJobTable "\
                "(jobId INTEGER PRIMARY KEY AUTOINCREMENT,"\
            "jobUuid CHAR(50) NOT NULL UNIQUE,"\
            "jobProject CHAR(50) NOT NULL,"\
            "jobUser CHAR(50) NOT NULL,"\
            "jobSoftware CHAR(50) NOT NULL,"\
            "jobScriptPath CHAR(50) NOT NULL,"\
            "jobTargetPath CHAR(50) NOT NULL,"\
            "jobFrameStart CHAR(50) NOT NULL,"\
            "jobFrameEnd CHAR(50) NOT NULL,"\
            "jobLayer CHAR(50) NOT NULL,"\
            "jobStatus CHAR(50) NOT NULL,"\
            "jobBlocked CHAR(50) NOT NULL,"\
            "jobRegistered DATETIME DEFAULT CURRENT_TIMESTAMP,"\
            "jobPriority CHAR(50) NOT NULL,"\
            "jobCamera CHAR(50),"\
            "jobClassification CHAR(50),"\
            "jobRenderTime CHAR(50))")
        connectionVar.commit()
        returnVar=1
    except:
        returnVar=0
    return returnVar

def setupLogTable():
    #Setup main database called constellationDatabase.db
    if os.path.isfile(rootPathVar+'/constellationDatabase.db')==False:
        connectionVar=sqlite3.connect('constellationDatabase.db')

    try:
        connectionVar=sqlite3.connect('constellationDatabase.db')
        #Create constellationClientTable to record working client
        connectionVar.execute("CREATE TABLE constellationLogTable "\
                "(logId INTEGER PRIMARY KEY AUTOINCREMENT,"\
            "clientName CHAR(50)  NOT NULL,"\
            "jobUuid CHAR(50),"\
            "logDescription CHAR(50),"\
            "logRegistered DATETIME DEFAULT CURRENT_TIMESTAMP)")
        connectionVar.commit()
        returnVar=1
    except Exception as e:
        print str(e)
        returnVar=0
    return returnVar

def setupClientTable():
    #Setup main database called constellationDatabase.db
    if os.path.isfile(rootPathVar+'/constellationDatabase.db')==False:
        connectionVar=sqlite3.connect('constellationDatabase.db')

    try:
        connectionVar=sqlite3.connect('constellationDatabase.db')
        #Create constellationClientTable to record working client
        connectionVar.execute("CREATE TABLE constellationClientTable "\
                "(clientId INTEGER PRIMARY KEY AUTOINCREMENT,"\
            "clientName CHAR(50) NOT NULL, UNIQUE,"\
            "clientJob CHAR(50),"\
            "clientBlocked CHAR(50),"\
            "clientMemory CHAR(50),"\
            "clientThread CHAR(50),"\
            "clientWorkMemory CHAR(50),"\
            "clientWorkThread CHAR(50),"\
            "clientClassification CHAR(50),"\
            "clientStatus CHAR(50) NOT NULL)")
        connectionVar.commit()
        returnVar=1
    except Exception as e:
        print str(e)
        returnVar=0
    return returnVar

def setupRenderer():
    #Generating renderer.xml to record renderer
    if os.path.isfile(rootPathVar+'/renderer.xml')==False:
        root=ET.Element('root')
        tree=ET.ElementTree(root)
        tree.write(rootPathVar+'/renderer.xml')
        returnVar=1
    else:
        returnVar=0
    return returnVar
