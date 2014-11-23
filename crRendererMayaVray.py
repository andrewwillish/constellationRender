__author__ = 'Andrewwillish'

#Constellation Render Manager - Renderer Module
#Maya V-Ray

#import module
import os, time, shutil, datetime, subprocess, sys, sqlite3, socket
import xml.etree.cElementTree as ET
import crControllerCore
from datetime import timedelta
import calendar

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
    rendererPath=None
    if os.path.isfile(rootPathVar+'/renderer.xml'):
        tree=ET.parse(rootPathVar+'/renderer.xml')
        root=tree.getroot()

        for chk in root:
            if str(chk.tag)==str(jobToRender[4]):
                rendererPath= chk.text
    #GET RENDERER======================================================================================================

    if rendererPath!=None:
        #<pathToRenderer> -rd <"localTarget"> -fnc <"fileNamingConvention"> -im <"imageName"> <renderFilePath>
        statPrint('starting job id:'+str(jobToRender[0])+' uuid:'+str(jobToRender[1]))

        #WRITELOG=======================================================================================================
        connectionVar.execute("INSERT INTO constellationLogTable (clientName,jobUuid,logDescription) "\
            "VALUES ('"+str(clientName)+"','"+str(jobToRender[1])+"','process started')")
        connectionVar.commit()
        #WRITELOG=======================================================================================================

        #CREATE DIRECTORY===============================================================================================
        #vray unable to create their own output directory so we need to create one
        #please note that CR only able to parse <Layer>,<Camera>,and <Scene> tag and not passes
        statPrint('creating directory <special for vray only>')
        directoryInst=jobToRender[6]
        cameraName=jobToRender[14]
        layerName=jobToRender[9]
        sceneName=str(jobToRender[5])[str(jobToRender[5]).rfind('/')+1:]
        sceneName=sceneName.replace('.ma','')

        directoryInst=directoryInst.replace('<Layer>',str(layerName))
        directoryInst=directoryInst.replace('<Camera>',str(cameraName))
        directoryInst=directoryInst.replace('<Scene>',str(sceneName))
        directoryInst=directoryInst[:directoryInst.rfind('\\')]

        dirResult=None
        if os.path.isdir(directoryInst)==True:
            dirResult=True
        else:
            try:
                os.makedirs(directoryInst)
                dirResult=True
            except:
                dirResult=False

        #dev error report:
        #Error reported where the renderer created an extra directory within the output
        #directory. Last part of the directoryInst which actually the file name instruction
        #will be removed on the following code.as
        directoryInst = directoryInst[:directoryInst.rfind('/')]
        print 'directoryInst ', directoryInst
        #CREATE DIRECTORY===============================================================================================

        if dirResult==True and os.path.isdir(directoryInst):
            #PRE-PROCESSING=================================================================================================
            statPrint('pre-processing')
            #writing render instruction
            renderInst=str(rendererPath)+' -r vray -rl '+str(jobToRender[9])+' -threads '+str(useThread)+' -cam '+str(jobToRender[14])+' -s '+\
                       str(jobToRender[7])+' -e '+str(jobToRender[8])+\
                       ' '+'"'+str(jobToRender[5]).replace('/','\\')+'"'
            #PRE-PROCESSING=================================================================================================

            #RENDERTIME WATCHER=============================================================================================
            startEpoch=calendar.timegm(time.gmtime())
            #RENDERTIME WATCHER=============================================================================================

            #PROCESSING=====================================================================================================
            statPrint('processing')
            renderRunError=None
            try:
                subprocess.check_output(renderInst, shell=True, stderr=subprocess.STDOUT)
            except Exception as renderRunError:
                pass
            #PROCESSING=====================================================================================================

            #RENDERTIME WATCHER=============================================================================================
            endEpoch=calendar.timegm(time.gmtime())
            averageTime=(endEpoch-startEpoch)/((int(jobToRender[8])-int(jobToRender[7]))+1)
            #RENDERTIME WATCHER=============================================================================================

            #POST-PROCESSING================================================================================================
            statPrint('post-processing')
            if renderRunError==None:
                #rendering finished without error.
                #Write job render average
                currentRenderTime=connectionVar.execute("SELECT * FROM constellationJobTable WHERE jobId='"+str(jobToRender[0])+"'").fetchall()
                if len(currentRenderTime)!=1:
                    statPrint('unable to record average render time database fetch anomaly')
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

                #WRITELOG=======================================================================================================
                connectionVar.execute("INSERT INTO constellationLogTable (clientName,jobUuid,logDescription) "\
                    "VALUES ('"+str(clientName)+"','"+str(jobToRender[1])+"','process finished')")
                connectionVar.commit()
                #WRITELOG=======================================================================================================

            else:
                #rendering finished with error. block appropriate client
                #rendering finished without error.
                #change status to ERROR to all job uuid [block everything that share the same uuid]
                connectionVar.execute("UPDATE constellationJobTable SET jobStatus='ERROR' WHERE jobUuid='"+str(jobToRender[1])+"'")
                connectionVar.commit()

                #change client status to STANDBY
                connectionVar.execute("UPDATE constellationClientTable SET clientStatus='STANDBY' "\
                    ",clientJob=''"
                    "WHERE clientName='"+clientName+"'")
                connectionVar.commit()

                #WRITELOG=======================================================================================================
                connectionVar.execute("INSERT INTO constellationLogTable (clientName,jobUuid,logDescription) "\
                    "VALUES ('"+str(clientName)+"','"+str(jobToRender[1])+"','process failed:\n "+str(renderRunError)+"')")
                connectionVar.commit()
                #WRITELOG=======================================================================================================

            #POST-PROCESSING================================================================================================
        else:
            #rendering process unable to start due to unable to create directory output
            #change status to ERROR to all job uuid [block everything that share the same uuid]
            connectionVar.execute("UPDATE constellationJobTable SET jobStatus='ERROR' WHERE jobUuid='"+str(jobToRender[1])+"'")
            connectionVar.commit()

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
    else:
        statPrint('no renderer specified')
        #change client status to STANDBY
        connectionVar.execute("UPDATE constellationClientTable SET clientStatus='STANDBY' "\
            ",clientJob='',clientBlocked='DISABLED'"
            "WHERE clientName='"+clientName+"'")
        connectionVar.commit()
    return

def statPrint(textVar):
    time.sleep(0.2)
    nowVar=datetime.datetime.now()
    timeVar=str(nowVar.hour)+':'+str(nowVar.minute)+':'+str(nowVar.second)+' '+str(nowVar.year)+'/'+\
                                                        str(nowVar.month)+'/'+str(nowVar.day)
    #Print to screen output
    print '['+str(timeVar)+'] '+str(textVar)
    return