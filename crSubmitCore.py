__author__ = 'andrew.willis'

#Constellation Render Manager - Job Submission Core
#Andrew Willis 2014

#Module import
import os, shutil, sys, sqlite3, imp, uuid
import hashlib, time, datetime, gc, socket
import xml.etree.cElementTree as ET
import maya.cmds as cmds

#Determining root path
rootPathVar = os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

#check if database exists
if not os.path.isfile(rootPathVar+'/constellationDatabase.db'):
    raise StandardError, 'error : constellation database non-exists'

#This function will collect, parse, and submit job data to shared database.
def submit(projectVar=None, userVar=None, softwareVar=None, scriptPathVar=None, targetPathVar=None,\
             frameStartVar=None, frameEndVar=None, blockCount=None, priorityVar=None, renderLayer=None, cameraSet=None,\
             classificationVar=None,enablerVar=True):
    global rootPathVar

    #Validate script path. Reject if file is not exist.
    if not os.path.isfile(scriptPathVar):raise ValueError, 'error : non-existence script path'

    #Validating input credential. Make sure every field is not empty
    print [softwareVar, scriptPathVar, targetPathVar, frameStartVar, frameEndVar, projectVar, \
        userVar, renderLayer, priorityVar, cameraSet, classificationVar]
    if None in [softwareVar, scriptPathVar, targetPathVar, frameStartVar, frameEndVar, projectVar, \
        userVar, renderLayer, priorityVar, cameraSet, classificationVar]:raise StandardError, 'error : incomplete credential'

    if str(type(renderLayer)) != "<type 'list'>":raise ValueError, 'error : invalid renderLayer value - expecting list'

    #Submitting procedure
    for rdrLayerVar in renderLayer:
        #parse each render layer for overwritten render layer
        cmds.editRenderLayerGlobals(crl=rdrLayerVar)
        if int(frameStartVar) == int(cmds.getAttr('defaultRenderGlobals.startFrame')):
            parseStartFrameVar=frameStartVar
        else:
            parseStartFrameVar=int(cmds.getAttr('defaultRenderGlobals.startFrame'))

        if int(frameEndVar)==int(cmds.getAttr('defaultRenderGlobals.endFrame')):
            parseEndFrameVar=int(frameEndVar)+1
        else:
            parseEndFrameVar=int(cmds.getAttr('defaultRenderGlobals.endFrame'))+1

        assignedId = str(uuid.uuid4())
        #separate job to block and upload it to server database
        for chk in range(int(parseStartFrameVar), int(parseEndFrameVar), int(blockCount)):
            blockStartFrame = chk
            blockEndFrame = chk+(int(blockCount)-1)
            if blockEndFrame >= int(parseEndFrameVar)-1: blockEndFrame = int(parseEndFrameVar)-1


            connectionVar = sqlite3.connect(rootPathVar+'/constellationDatabase.db')
            connectionVar.execute("INSERT INTO constellationJobTable "\
                                  "(jobProject,jobUuid,jobUser,jobSoftware,jobScriptPath,jobTargetPath,jobFrameStart,"\
                "jobFrameEnd, jobStatus, jobPriority, jobBlocked, jobLayer,jobClassification,jobCamera) VALUES "\
                                  "('"+projectVar+"'"\
                ",'"+assignedId+"'"\
                ",'"+userVar+"'"\
                ",'"+softwareVar+"'"\
                ",'"+scriptPathVar+"'"\
                ",'"+targetPathVar+"'"\
                ",'"+str(blockStartFrame)+"'"\
                ",'"+str(blockEndFrame)+"'"\
                ",'QUEUE'"\
                ",'"+priorityVar+"'"\
                ",'"+str(enablerVar)+"'"\
                ",'"+str(rdrLayerVar)+"'"\
                ",'"+str(classificationVar)+"'"\
                ",'"+str(cameraSet)+"')")
            connectionVar.commit()
    return