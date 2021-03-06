__author__ = 'Andrewwillish'

#Constellation Render Manager - Renderer Module
#Maya V-Ray

#import module
import os, time, shutil, datetime, subprocess, sys, sqlite3, socket
import xml.etree.cElementTree as ET
import crControllerCore, ctypes
from datetime import timedelta
import calendar
import re

#get client name
clientName = str(socket.gethostname())

#Determining system root
systemRootVar = str(os.environ['WINDIR']).replace('\\Windows','')

#Determining root path
rootPathVar = os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

def render(clientSetting, jobToRender, useThread, useMemory, connectionVar):
    #CHANGE CLIENT AND JOB STATUS=======================================================================================
    #change client status to RENDERING
    connectionVar = sqlite3.connect(rootPathVar+'/constellationDatabase.db')
    connectionVar.execute("UPDATE constellationClientTable SET clientStatus='RENDERING' "\
        ",clientJob='"+str(jobToRender[0])+"'"
        "WHERE clientName='"+clientName+"'")
    connectionVar.commit()

    #change job status to RENDERING
    connectionVar.execute("UPDATE constellationJobTable SET jobStatus='RENDERING' WHERE jobId='"+str(jobToRender[0])+"'")
    connectionVar.commit()
    connectionVar.close()
    #CHANGE CLIENT AND JOB STATUS=======================================================================================

    #GET RENDERER=======================================================================================================
    rendererPath = None
    if os.path.isfile(rootPathVar+'/renderer.xml'):
        tree = ET.parse(rootPathVar+'/renderer.xml')
        root = tree.getroot()

        for chk in root:
            if str(chk.tag) == str(jobToRender[4]):
                rendererPath = chk.text
    #GET RENDERER=======================================================================================================

    if rendererPath is not None:
        #<pathToRenderer> -rd <"localTarget"> -fnc <"fileNamingConvention"> -im <"imageName"> <renderFilePath>
        statPrint('starting job id:'+str(jobToRender[0])+' uuid:'+str(jobToRender[1]), colorStat=10)

        #WRITELOG=======================================================================================================
        connectionVar = sqlite3.connect(rootPathVar+'/constellationDatabase.db')
        connectionVar.execute("INSERT INTO constellationLogTable (clientName,jobUuid,logDescription) "\
            "VALUES ('"+str(clientName)+"','"+str(jobToRender[1])+"','process started')")
        connectionVar.commit()
        connectionVar.close()
        #WRITELOG=======================================================================================================

        #CREATE DIRECTORY===============================================================================================
        #vray unable to create their own output directory so we need to create one
        #please note that CR only able to parse <Layer>,<Camera>,and <Scene> tag and not passes
        statPrint('creating directory', colorStat=14)
        directoryInst = jobToRender[6]
        cameraName = jobToRender[14]
        layerName = jobToRender[9]
        sceneName = str(jobToRender[5])[str(jobToRender[5]).rfind('/')+1:]
        sceneName = sceneName.replace('.ma','')

        directoryInst = directoryInst.replace('<Layer>',str(layerName))
        directoryInst = directoryInst.replace('<Camera>',str(cameraName))
        directoryInst = directoryInst.replace('<Scene>',str(sceneName))
        directoryInst = directoryInst.replace('\\', '/')
        directoryInst = directoryInst.replace('.%e', '')
        directoryRoot = directoryInst[:directoryInst.rfind('/')]

        dirResult = None
        if os.path.isdir(directoryRoot):
            dirResult = True
        else:
            try:
                os.makedirs(directoryRoot)
                dirResult = True
            except:
                dirResult = False
        #CREATE DIRECTORY===============================================================================================

        #CHECKPOINT CHECK===============================================================================================
        #This checkpoint will check for any previous rendered frame. If previous frame exists
        #the renderer will skip it and start rendering from the last frame rendered.
        #Please note the renderer will re-render the previous frame in case its not rendered.

        if dirResult:
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

        if dirResult is True and os.path.isdir(directoryRoot):
            #PRE-PROCESSING=============================================================================================
            statPrint('pre-processing', colorStat=14)
            #writing render instruction
            renderInst = str(rendererPath)+' -r vray -rl '+str(jobToRender[9])+' -threads '+str(useThread)+' -cam '+str(jobToRender[14])+' -s '+\
                       str(startRange)+' -e '+str(endRange)+\
                       ' '+'"'+str(jobToRender[5]).replace('/','\\')+'"'
            #PRE-PROCESSING=============================================================================================

            #RENDERTIME WATCHER=========================================================================================
            startEpoch = calendar.timegm(time.gmtime())
            #RENDERTIME WATCHER=========================================================================================

            #PROCESSING=================================================================================================
            statPrint('processing', colorStat=14)
            renderRunError = None
            try:
                subprocess.check_output(renderInst, shell=True, stderr=subprocess.STDOUT)
            except Exception as renderRunError:
                pass
            #PROCESSING=================================================================================================

            #RENDERTIME WATCHER=========================================================================================
            endEpoch = calendar.timegm(time.gmtime())
            averageTime = (endEpoch-startEpoch)/((int(jobToRender[8])-int(jobToRender[7]))+1)
            #RENDERTIME WATCHER=========================================================================================

            #POST-PROCESSING============================================================================================
            statPrint('post-processing', colorStat=14)
            if renderRunError is None:
                #rendering finished without error.
                #Write job render average
                connectionVar = sqlite3.connect(rootPathVar+'/constellationDatabase.db')
                currentRenderTime=connectionVar.execute("SELECT * FROM constellationJobTable WHERE jobId='"+str(jobToRender[0])+"'").fetchall()
                if len(currentRenderTime)!=1:
                    statPrint('unable to record average render time database fetch anomaly', colorStat=12)
                else:
                    newRenderTime=averageTime
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

                #WRITELOG===============================================================================================
                connectionVar.execute("INSERT INTO constellationLogTable (clientName,jobUuid,logDescription) "\
                    "VALUES ('"+str(clientName)+"','"+str(jobToRender[1])+"','process finished')")
                connectionVar.commit()
                #WRITELOG===============================================================================================
                connectionVar.close()
            else:
                #rendering finished with error. block appropriate client
                #rendering finished without error.
                #change status to ERROR to all job uuid [block everything that share the same uuid]
                connectionVar = sqlite3.connect(rootPathVar+'/constellationDatabase.db')
                connectionVar.execute("UPDATE constellationJobTable SET jobStatus='ERROR' WHERE jobUuid='"+str(jobToRender[1])+"'")
                connectionVar.commit()

                #change client status to STANDBY
                connectionVar.execute("UPDATE constellationClientTable SET clientStatus='STANDBY' "\
                    ",clientJob=''"
                    "WHERE clientName='"+clientName+"'")
                connectionVar.commit()

                #WRITELOG===============================================================================================
                connectionVar.execute("INSERT INTO constellationLogTable (clientName,jobUuid,logDescription) "\
                    "VALUES ('"+str(clientName)+"','"+str(jobToRender[1])+"','process failed:\n "+str(renderRunError)+"')")
                connectionVar.commit()
                #WRITELOG===============================================================================================
                connectionVar.close()
            #POST-PROCESSING============================================================================================
        else:
            #rendering process unable to start due to unable to create directory output
            #change status to ERROR to all job uuid [block everything that share the same uuid]

            statPrint('process error check job log for detail', colorStat=12)

            connectionVar = sqlite3.connect(rootPathVar+'/constellationDatabase.db')
            connectionVar.execute("UPDATE constellationJobTable SET jobStatus='ERROR' WHERE jobUuid='"+str(jobToRender[1])+"'")
            connectionVar.commit()

            statPrint('job Uuid:'+str(jobToRender[1])+' blocked and disabled', colorStat=12)

            #change client status to STANDBY
            connectionVar.execute("UPDATE constellationClientTable SET clientStatus='STANDBY' "\
                ",clientJob=''"
                "WHERE clientName='"+clientName+"'")
            connectionVar.commit()

            #WRITELOG===================================================================================================
            connectionVar.execute("INSERT INTO constellationLogTable (clientName,jobUuid,logDescription) "\
                "VALUES ('"+str(clientName)+"','"+str(jobToRender[1])+"','process failed:unable to create directory')")
            connectionVar.commit()
            #WRITELOG===================================================================================================
            connectionVar.close()
    else:
        statPrint('no renderer specified', colorStat=12)
        #change client status to STANDBY
        connectionVar = sqlite3.connect(rootPathVar+'/constellationDatabase.db')
        connectionVar.execute("UPDATE constellationClientTable SET clientStatus='STANDBY' "\
            ",clientJob='',clientBlocked='DISABLED'"
            "WHERE clientName='"+clientName+"'")
        connectionVar.commit()
        connectionVar.close()
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