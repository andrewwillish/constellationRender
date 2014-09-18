__author__ = 'Andrewwillish'

#Constellation Render Manager - Renderer Module
#Maya Mental Ray

#import module
import os, time, shutil, datetime, subprocess
import xml.etree.cElementTree as ET

#Determining system root
systemRootVar = str(os.environ['WINDIR']).replace('\\Windows','')

#Determining root path
rootPathVar=os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

def render(clientSetting, jobToRender, useThread, useMemory):
    #CHANGE CLIENT AND JOB STATUS======================================================================================

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
        statPrint('processing job id:'+str(jobToRender[0])+' uuid:'+str(jobToRender[1]))
        #PRE-PROCESSING=================================================================================================
        statPrint('pre-processing')

        #writing render instruction
        renderInst=str(rendererPath)+' -rl '+str(jobToRender[9])+' -s '+\
                   str(jobToRender[7])+' -e '+\
                   str(jobToRender[8])+' -mr:rt '+\
                   str(useThread)+' -mr:mem '+\
                   str(useMemory)+' '+'"'+str(jobToRender[5])+'"'
        #PRE-PROCESSING=================================================================================================

        #PROCESSING=====================================================================================================
        statPrint('processing')
        print renderInst
        renderRun= subprocess.Popen([renderInst],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

        renderRunError=renderRun.stderr.readline()
        print renderRunError
        #PROCESSING=====================================================================================================

        #POST-PROCESSING================================================================================================
        statPrint('post-processing')
        #POST-PROCESSING================================================================================================
    return

def statPrint(textVar):
    time.sleep(0.2)
    nowVar=datetime.datetime.now()
    timeVar=str(nowVar.hour)+':'+str(nowVar.minute)+':'+str(nowVar.second)+' '+str(nowVar.year)+'/'+\
                                                        str(nowVar.month)+'/'+str(nowVar.day)
    #Print to screen output
    print '['+str(timeVar)+'] '+str(textVar)
    return