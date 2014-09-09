__author__ = 'andrew.willis'

#Constellation Render Manager - Client Service Module
#Andrew Willis 2014

#Module import
import os, shutil, sys, sqlite3, imp, time, threading, thread
import hashlib, time, datetime, socket, subprocess
from multiprocessing import Process
import xml.etree.cElementTree as ET
from threading import Thread

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
    #Check if the client has been regstered to the database or not
    allClientLis=connectionVar.execute("SELECT * FROM constellationClientTable")
    templis=[]
    for chk in allClientLis:
        templis.append(chk[1])

    if clientName not in templis:
        raise StandardError, 'error : client has not been registered'

    #Executing instruction function
    #while True:
    #    instructionFunc()
    return

#This function contain all the render instruction. Customized render procedure here.
#Render instruction command : <mayaDir> -rl <layer> -s <startFrame> -e <endFrame> <filePath>
def instructionFunc():
    #Fetch client setting from database
    clientSetting=(connectionVar.execute("SELECT * FROM constellationClientTable WHERE clientName='"\
                                        +str(socket.gethostname())+"'").fetchall())[0]
    #Check client activation status
    if clientSetting[3]=='ACTIVE':
        #Fetch all job array
        allJobLis=connectionVar.execute("SELECT * FROM constellationJobTable WHERE jobEnabler='ENABLED' AND jobStatus='QUEUE'").fetchall()

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
            for jobRecord in allJobLis:
                if jobToRender==None:
                    if int(jobRecord[13])==highestPrior:
                        jobToRender=jobRecord

            #Determine and fetch renderer path from renderer.xml
            rendererVar=str(jobToRender[4])

            tree=ET.parse(rootPathVar+'/renderer.xml')
            root=tree.getroot()

            for rendererParse in root:
                if str(rendererParse.tag)==rendererVar:
                    rendererPath=str(rendererParse.text)

            #Validate renderer location. If renderer doesn't exist rendering will skip and client will automatically suspended.
            if os.path.isfile(rendererPath.replace('"',''))==True:
                #RENDERING RUN=============================================================================================
                #PRE-RENDER
                #Changing job status to rendering
                connectionVar.execute("UPDATE constellationJobTable SET jobStatus='RENDERING' where JobId='"+str(jobToRender[0])+"'")
                connectionVar.commit()

                #Changing client status to rendering
                connectionVar.execute("UPDATE constellationClientTable SET clientStatus='RENDERING' WHERE clientName='"+str(socket.gethostname())+"'")
                connectionVar.commit()

                #Changing client job status
                connectionVar.execute("UPDATE constellationClientTable SET clientJob='"+jobToRender[1]+"' WHERE clientName='"+str(socket.gethostname())+"'")
                connectionVar.commit()

                #Checking render directory make one if non exists
                pathInstructionVar=jobToRender[6]
                layerVar=jobToRender[9]
                cameraVar=jobToRender[14]
                sceneVar=jobToRender[5]
                sceneVar=sceneVar[sceneVar.rfind('/')+1:sceneVar.rfind('.ma')]

                pathInstructionVar=pathInstructionVar[:pathInstructionVar.rfind('/')]
                pathInstructionVar=pathInstructionVar.replace('<Layer>',str(layerVar))
                pathInstructionVar=pathInstructionVar.replace('<Camera>',str(cameraVar))
                pathInstructionVar=pathInstructionVar.replace('<Scene>',str(sceneVar))

                if os.path.isdir(pathInstructionVar)==False:
                    os.makedirs(pathInstructionVar)

                #Building render command
                if rendererVar=='maya':
                    renderCommandVar=rendererPath+' -rl '+jobToRender[9]+' -s '+jobToRender[7]+' -e '+jobToRender[8]+' '
                    renderCommandVar=renderCommandVar+'"'+jobToRender[5]+'"'
                elif rendererVar=='maya-vray':
                    renderCommandVar=rendererPath+' -rl '+jobToRender[9]+' -s '+jobToRender[7]+' -e '+jobToRender[8]+' -r vray '
                    renderCommandVar=renderCommandVar+'"'+jobToRender[5]+'"'
                    print renderCommandVar

                #RENDER
                #os.system(renderCommandVar)
                #startupinfo=subprocess.STARTUPINFO()
                #startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                #subprocess.call(renderCommandVar,startupinfo=startupinfo)

                #dummy render process
                import random,time
                error=random.randint(1,10)
                if error>7:
                    #make error command line
                    renderCommandVar='"C:\Program Files\Autodesk\Maya2013.5\bin\Render.exe" -rd "D:\test" -fnc "name_#.ext" -im "test" "C:\Users\andrew.wil\localTestRender.ma"'
                else:
                    renderCommandVar="dir"
                renderRun=subprocess.Popen([renderCommandVar],sell=True,stderr=subprocess.PIPE)


                #POST-RENDER
                #Changing job status to done
                connectionVar.execute("UPDATE constellationJobTable SET jobStatus='DONE' where JobId='"+str(jobToRender[0])+"'")
                connectionVar.commit()

                #Changing client job status
                connectionVar.execute("UPDATE constellationClientTable SET clientJob=NULL WHERE clientName='"+str(socket.gethostname())+"'")
                connectionVar.commit()

                #Changing client status to cooldown for 5 seconds
                connectionVar.execute("UPDATE constellationClientTable SET clientStatus='COOLDOWN' WHERE clientName='"+str(socket.gethostname())+"'")
                connectionVar.commit()
                time.sleep(5)

                #Changing client status to cooldown for 5 seconds
                connectionVar.execute("UPDATE constellationClientTable SET clientStatus='STANDBY' WHERE clientName='"+str(socket.gethostname())+"'")
                connectionVar.commit()
                #RENDERING RUN=============================================================================================
            else:
                #Changing client status to SUSPENDED
                connectionVar.execute("UPDATE constellationClientTable SET clientBlocked='SUSPENDED-RDRR' where clientName='"+str(socket.gethostname())+"'")
                connectionVar.commit()
                connectionVar.execute("UPDATE constellationClientTable SET clientStatus='SUSPENDED' where clientName='"+str(socket.gethostname())+"'")
                connectionVar.commit()
        else:
            time.sleep(2)
    elif clientSetting[3]=='STOPPING':
        connectionVar.execute("UPDATE constellationClientTable SET clientBlocked='SUSPENDED' where clientName='"+str(socket.gethostname())+"'")
        connectionVar.commit()
        connectionVar.execute("UPDATE constellationClientTable SET clientStatus='SUSPENDED' where clientName='"+str(socket.gethostname())+"'")
        connectionVar.commit()
        time.sleep(2)
    elif clientSetting[3]=='SUSPENDED-RDRR':
        connectionVar.execute("UPDATE constellationClientTable SET clientBlocked='SUSPENDED-RDRR' where clientName='"+str(socket.gethostname())+"'")
        connectionVar.commit()
        connectionVar.execute("UPDATE constellationClientTable SET clientStatus='SUSPENDED' where clientName='"+str(socket.gethostname())+"'")
        connectionVar.commit()
        time.sleep(2)
    elif clientSetting[3]=='STOPPING-OFF':
        connectionVar.execute("UPDATE constellationClientTable SET clientStatus='OFFLINE' where clientName='"+str(socket.gethostname())+"'")
        connectionVar.commit()
        time.sleep(2)
        sys.exit()
    else:
        connectionVar.execute("UPDATE constellationClientTable SET clientStatus='SUSPENDED' where clientName='"+str(socket.gethostname())+"'")
        connectionVar.commit()
        time.sleep(2)
    return

setupClient()