__author__ = 'andrew.willis'

#Shepard Render - Job Submission Module
#Andrew Willis 2014

#Module import
import os, shutil, sys, sqlite3, imp, uuid
import hashlib, time, datetime, gc, socket
import xml.etree.cElementTree as ET

#Determining root path
rootPathVar=os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

if os.path.isfile(rootPathVar+'/constellationDatabase.db')==False:
    raise StandardError, 'error : constellation database non-exists'

#This function will collect, parse, and submit job data to shared database.
def submit(projectVar=None, userVar=None, softwareVar=None, scriptPathVar=None, targetPathVar=None,\
             frameStartVar=None, frameEndVar=None, blockCount=None, priorityVar=None, renderLayer=None, cameraSet=None):
    global rootPathVar

    #Validate script path. Reject if file is not exist.
    if os.path.isfile(scriptPathVar)==False:
        raise   ValueError, 'error : non-existence script path'

    #Validating input credential. Make sure every field is not empty
    if softwareVar==None or scriptPathVar==None or targetPathVar==None or \
        frameStartVar==None or frameEndVar==None or projectVar==None or userVar==None or renderLayer==None or priorityVar==None or cameraSet==None :
        raise StandardError, 'error : incomplete credential'

    if str(type(renderLayer))!="<type 'list'>":
        raise ValueError, 'error : invalid renderLayer value - expecting list'

    #Submitting procedure

    for rdrLayerVar in renderLayer:
        assignedId=str(uuid.uuid4())
        for chk in range(int(frameStartVar), int(frameEndVar), int(blockCount)):
            blockStartFrame=chk
            blockEndFrame=chk+(int(blockCount)-1)
            if blockEndFrame>=int(frameEndVar):
                blockEndFrame=int(frameEndVar)

            connectionVar=sqlite3.connect('constellationDatabase.db')
            connectionVar.execute("INSERT INTO constellationJobTable (jobProject, jobUuid, jobUser, jobSoftware, jobScriptPath,"\
                                  "jobTargetPath, jobFrameStart, jobFrameEnd, jobStatus, jobPriority, jobEnabler, jobLayer,jobCamera) VALUES "\
                                  "('"+projectVar+"','"+assignedId+"','"+userVar+"','"+softwareVar+"','"+scriptPathVar+"'"\
                                    ",'"+targetPathVar+"','"+str(blockStartFrame)+"','"+str(blockEndFrame)+"','QUEUE','"+priorityVar+"','ENABLED','"+str(rdrLayerVar)+"','"+str(cameraSet)+"')")
            connectionVar.commit()
    return