#Constellation Render Manager
#Andrew Willis 2014

import maya.utils as utils
import maya.cmds as cmds
import maya.mel as mel
import imp, os
import maya.OpenMaya as om
import getpass

#Determining root path
#Note: hard code root path to fit with current studio mapping.
rootPathVar='A:/visualExpert/development/constellationRender/'

def launcherscr(scr,srvrname):
    try:
        imp.load_compiled(scr,srvrname+scr+'.pyc')
    except:
        imp.load_source(scr,srvrname+scr+'.py')
    #return

def osLaunch(procNameVar, procPathVar):
    os.startfile(rootPathVar+procNameVar+'.bat')
    return

def menutls(*args):
    global rootPathVar
    gMainWindow = mel.eval('$temp1=$gMainWindow')
    mainzmenu=cmds.menu(tearOff=True,l='Constellation Render',p=gMainWindow)
    cmds.menuItem(parent=mainzmenu, l='Submit Job',c=lambda*args:launcherscr('constellationRenderMayaSubmit',rootPathVar))
    cmds.menuItem(parent=mainzmenu,d=True)
    cmds.menuItem(parent=mainzmenu,l='Launch Controller',c=lambda*args:osLaunch('constellationRender - controller',rootPathVar))
    cmds.menuItem(parent=mainzmenu,l='Launch Client',c=lambda*args:osLaunch('constellationRender - client',rootPathVar))
    return
    
utils.executeDeferred (menutls)
