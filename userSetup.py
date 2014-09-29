#Constellation Render Manager
#Andrew Willis 2014

import maya.utils as utils
import maya.cmds as cmds
import maya.mel as mel
import imp, os
import maya.OpenMaya as om
import getpass

#Determining root path
rootPathVar='Y:/TECH/constellationRender/'

def launcherscr(scr,srvrname):
    print srvrname+scr+'.py'
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
    cmds.menuItem(parent=mainzmenu, l='Submit Job',c=lambda*args:launcherscr('crSubmitUIMaya',rootPathVar))
    cmds.menuItem(parent=mainzmenu,d=True)
    cmds.menuItem(parent=mainzmenu,l='Launch Client Service',c=lambda*args:osLaunch('_crClientServiceLaunch.bat',rootPathVar))
    cmds.menuItem(parent=mainzmenu,l='Launch Client Console',c=lambda*args:osLaunch('_crClientConsole.bat',rootPathVar))
    return
    
utils.executeDeferred (menutls)
