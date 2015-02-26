__author__ = 'Andrewwillish'

#Constellation Render Manager - Renderer Module
#Maya Mental Ray - Continuous

#Launch note:
#It is very important that the python session for this script is from maya.

#import module
import maya.standalone as standalone
standalone.initialize(name='python')
import maya.mel as mel
import maya.cmds as cmds
import os, time, datetime, subprocess, socket
import xml.etree.cElementTree as ET
import ctypes
import calendar
import re

#get client name
clientName=str(socket.gethostname())

#Determining system root
systemRootVar = str(os.environ['WINDIR']).replace('\\Windows','')

#Determining root path
rootPathVar=os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

def render(clientSetting, jobToRender, useThread, useMemory, connectionVar):
    #CHANGE CLIENT AND JOB STATUS======================================================================================
    #change client status to RENDERING
    connectionVar.execute("UPDATE constellationClientTable SET clientStatus='RENDERING' "\
        ",clientJob='"+str(jobToRender[0])+"'"
        "WHERE clientName='"+clientName+"'")
    connectionVar.commit()

    #change job status to RENDERING
    connectionVar.execute("UPDATE constellationJobTable SET jobStatus='RENDERING' WHERE jobId='"+str(jobToRender[0])+"'")
    connectionVar.commit()
    #CHANGE CLIENT AND JOB STATUS======================================================================================

    #GET RENDERER======================================================================================================
    rendererPath = None
    if os.path.isfile(rootPathVar+'/renderer.xml'):
        tree = ET.parse(rootPathVar+'/renderer.xml')
        root = tree.getroot()

        for chk in root:
            if str(chk.tag) == str(jobToRender[4]):
                rendererPath = chk.text
    #GET RENDERER======================================================================================================

    if rendererPath is not None:
        #<pathToRenderer> -rd <"localTarget"> -fnc <"fileNamingConvention"> -im <"imageName"> <renderFilePath>
        statPrint('starting job id:'+str(jobToRender[0])+' uuid:'+str(jobToRender[1]), colorStat=10)

        #WRITELOG=======================================================================================================
        connectionVar.execute("INSERT INTO constellationLogTable (clientName,jobUuid,logDescription) "\
            "VALUES ('"+str(clientName)+"','"+str(jobToRender[1])+"','process started')")
        connectionVar.commit()
        #WRITELOG=======================================================================================================

        #CHECKPOINT CHECK===============================================================================================
        directoryInst = jobToRender[6]
        cameraName = jobToRender[14]
        layerName = jobToRender[9]
        sceneName = str(jobToRender[5])[str(jobToRender[5]).rfind('/')+1:]
        sceneName = sceneName.replace('.ma','')

        directoryInst = directoryInst.replace('<RenderLayer>',str(layerName))
        directoryInst = directoryInst.replace('<Camera>',str(cameraName))
        directoryInst = directoryInst.replace('<Scene>',str(sceneName))
        directoryInst = directoryInst.replace('\\', '/')
        directoryInst = directoryInst.replace('.%e', '')
        directoryRoot = directoryInst[:directoryInst.rfind('/')]

        if not os.path.isdir(directoryRoot): os.makedirs(directoryRoot)

        startRange = None
        endRange = str(jobToRender[8])
        padRe = re.search( r'%(.*)n', directoryInst)
        if padRe: padding = padRe.group(1)
        for number in range(int(jobToRender[7]), int(jobToRender[8])):
            searchInst = re.sub(r'%(.*)n', str(number).zfill(int(padding)), directoryInst)
            for itemInDir in os.listdir(directoryRoot):
                if directoryRoot+'/'+str(itemInDir[:itemInDir.rfind('.')]) == searchInst:
                    startRange = int(number)

        if startRange == endRange or startRange is None: startRange = int(jobToRender[7])
        #CHECKPOINT CHECK===============================================================================================

        #PRE-PROCESSING=================================================================================================
        statPrint('pre-processing', colorStat=14)
        #writing render instruction
        renderInst = str(rendererPath)+' -rl '+str(jobToRender[9])+' -cam '+str(jobToRender[14])+' -s '+\
                   str(startRange)+' -e '+\
                   str(endRange)+' -mr:rt '+\
                   str(useThread)+' -mr:mem '+\
                   str(useMemory)+' '+'"'+str(jobToRender[5]).replace('/','\\')+'"'
        #PRE-PROCESSING=================================================================================================

        #RENDERTIME WATCHER=============================================================================================
        startEpoch = calendar.timegm(time.gmtime())
        #RENDERTIME WATCHER=============================================================================================

        #PROCESSING=====================================================================================================
        renderRunError = None
        try:
            mel.eval("BatchScript;")
        except Exception as e:
            renderRunError = str(e)
        #PROCESSING=====================================================================================================

        #RENDERTIME WATCHER=============================================================================================
        endEpoch=calendar.timegm(time.gmtime())
        averageTime=(endEpoch-startEpoch)/((int(jobToRender[8])-int(jobToRender[7]))+1)
        #RENDERTIME WATCHER=============================================================================================

        #POST-PROCESSING================================================================================================
        statPrint('post-processing', colorStat=14)
        if renderRunError is None:
            #rendering finished without error.
            #Write job render average
            currentRenderTime = connectionVar.execute("SELECT * FROM constellationJobTable WHERE jobId='"+str(jobToRender[0])+"'").fetchall()
            if len(currentRenderTime) != 1:
                statPrint('unable to record average render time database fetch anomaly', colorStat=12)
            else:
                newRenderTime = averageTime
                connectionVar.execute("UPDATE constellationJobTable SET jobRenderTime='"+str(newRenderTime)+"' WHERE jobId='"+str(jobToRender[0])+"'")
                connectionVar.commit()

            #change job status to DONE
            connectionVar.execute("UPDATE constellationJobTable SET jobStatus='DONE' WHERE jobId='"+str(jobToRender[0])+"'")
            connectionVar.commit()

            #change client status to STANDBY
            connectionVar.execute("UPDATE constellationClientTable SET clientStatus='STANDBY' "\
                ",clientJob=''"
                "WHERE clientName='"+clientName+"'")
            connectionVar.commit()

            #WRITELOG=======================================================================================================
            connectionVar.execute("INSERT INTO constellationLogTable (clientName,jobUuid,logDescription) "\
                "VALUES ('"+str(clientName)+"','"+str(jobToRender[1])+"','process finished')")
            connectionVar.commit()
            #WRITELOG=======================================================================================================

        else:
            #rendering finished with error. block appropriate client
            #rendering finished without error.

            statPrint('process error check job log for detail', colorStat=12)

            #change status to RENDERING to all job uuid [block everything that share the same uuid]
            connectionVar.execute("UPDATE constellationJobTable SET jobStatus='ERROR', jobBlocked='DISABLED' WHERE jobUuid='"+str(jobToRender[1])+"'")
            connectionVar.commit()

            statPrint('job Uuid:'+str(jobToRender[1])+' blocked and disabled', colorStat=12)

            #change client status to STANDBY
            connectionVar.execute("UPDATE constellationClientTable SET clientStatus='STANDBY' "\
                ",clientJob=''"
                "WHERE clientName='"+clientName+"'")
            connectionVar.commit()

            #WRITELOG=======================================================================================================
            connectionVar.execute("INSERT INTO constellationLogTable (clientName,jobUuid,logDescription) "\
                "VALUES ('"+str(clientName)+"','"+str(jobToRender[1])+"','process failed:\n "+str(renderRunError).replace("'","")+"')")
            connectionVar.commit()
            #WRITELOG=======================================================================================================

        #POST-PROCESSING================================================================================================
    else:
        statPrint('no renderer specified', colorStat=12)
        #change client status to STANDBY and DISABLED
        connectionVar.execute("UPDATE constellationClientTable SET clientStatus='STANDBY' "\
            ",clientJob='',clientBlocked='DISABLED'"
            "WHERE clientName='"+clientName+"'")
        connectionVar.commit()
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