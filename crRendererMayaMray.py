__author__ = 'Andrewwillish'

#Constellation Render Manager - Renderer Module
#Maya Mental Ray

#import module
import os, time, shutil, datetime
import xml.etree.cElementTree as ET

#Determining system root
systemRootVar = str(os.environ['WINDIR']).replace('\\Windows','')

def render(clientSetting, jobToRender, useThread, useMemory):
    #CHANGE CLIENT AND JOB STATUS======================================================================================

    #CHANGE CLIENT AND JOB STATUS======================================================================================

    statPrint('processing job id:'+str(jobToRender[0])+' uuid:'+str(jobToRender[1]))
    #PRE-PROCESSING====================================================================================================
    statPrint('pre-processing')
    #PRE-PROCESSING====================================================================================================
    return

def statPrint(textVar):
    time.sleep(0.2)
    nowVar=datetime.datetime.now()
    timeVar=str(nowVar.hour)+':'+str(nowVar.minute)+':'+str(nowVar.second)+' '+str(nowVar.year)+'/'+\
                                                        str(nowVar.month)+'/'+str(nowVar.day)
    #Print to screen output
    print '['+str(timeVar)+'] '+str(textVar)
    return