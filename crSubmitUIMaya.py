#Constellation Render Manager - Maya Submitter UI

#Import module
import maya.cmds as cmds
import crSubmitCore, getpass, os
import socket

#Determining root path
rootPathVar = os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

class constellationMayaSubmitter:
    #invoke UI element
    def __init__(self):
        if cmds.window('constellationSubmitter', exists=True):cmds.deleteUI('constellationSubmitter', wnd=True)

        cmds.window('constellationSubmitter',t='Constellation Submitter',s=False)
        cmas = cmds.columnLayout(adj=True)

        ccmas = cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[(1, 150), (2, 305)],p=cmas)

        cm1 = cmds.frameLayout(l='Render Layer',w=150,p=ccmas)
        cmds.textScrollList('newJobRenderLayer',ams=True)

        cm2 = cmds.frameLayout(l='Job Setting',p=ccmas)
        ccm2 = cmds.columnLayout(adj=True)
        cmds.rowColumnLayout( numberOfColumns=4, columnWidth=[(1, 55), (2, 90), (3, 55), (4, 90)],p=ccm2)
        cmds.text(l='  Project:', al='left')
        cmds.textField('newJobProject')
        cmds.text(l='  Software:', al='left')
        cmds.optionMenu('newJobSoftware',l='', cc=self.rendererChange)
        cmds.menuItem(l='')
        cmds.menuItem(l='maya-mray')
        cmds.menuItem(l='maya-vray')
        cmds.menuItem(l='nuke')

        cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[(1, 55),(2, 235)],p=ccm2)
        cmds.text(l='  User:', al='left')
        cmds.textField('newJobUser')

        cmds.text(l='  Camera:', al='left')
        cmds.optionMenu('newJobCamera',l='',w=235)
        cmds.menuItem(l='')
        for chk in cmds.ls(type='camera'):
            cmds.menuItem(l=str(chk).replace('Shape',''))

        cmds.text(l='  Script:', al='left')
        cmds.textField('newJobScriptPath')

        cmds.text(l='  Target:', al='left')
        cmds.textField('newJobTarget')

        cmds.rowColumnLayout( numberOfColumns=4, columnWidth=[(1, 55), (2, 90), (3, 55), (4, 90)],p=ccm2)
        cmds.text(l='  Start:', al='left')
        cmds.intField('newJobStartFrame')
        cmds.text(l='  End:', al='left')
        cmds.intField('newJobEndFrame')
        cmds.text(l='  f/Block:', al='left')
        cmds.intField('newJobFpb')
        cmds.text(l='  Priority:', al='left')
        cmds.intField('newJobPriority')
        cmds.text(l='  Classif:', al='left')
        cmds.optionMenu('newJobClassification',w=85)
        cmds.menuItem(l='',p='newJobClassification')
        for chk in ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']:
            cmds.menuItem(l=chk,p='newJobClassification')
        cmds.text(l='  Enable:', al='left')
        cmds.optionMenu('newJobEnabler',w=85)
        cmds.menuItem(l='ENABLED')
        cmds.menuItem(l='DISABLED')

        cmds.separator(p=ccm2)

        cmds.rowColumnLayout( numberOfColumns=3, columnWidth=[(1, 200),(2, 100)],p=ccm2)
        cmds.button(l='SUBMIT JOB',bgc=[1.0,0.643835616566,0.0],c=self.submitProc)
        cmds.button(l='REFRESH',bgc=[1,1,0],c=self.refreshFun)

        cmds.showWindow()

        #Populate UI field
        cmds.textScrollList('newJobRenderLayer',e=True,ra=True)
        for chk in cmds.ls(type='renderLayer'):
            if not chk.endswith('defaultRenderLayer'):
                cmds.textScrollList('newJobRenderLayer', e=True, a=str(chk))
                cmds.textScrollList('newJobRenderLayer', e=True, si=str(chk))

        cmds.textField('newJobProject',e=True,tx='default')
        cmds.textField('newJobUser',e=True,tx=str(getpass.getuser()))
        cmds.textField('newJobScriptPath',e=True, tx=str(cmds.file(q=True,sn=True)))

        cmds.editRenderLayerGlobals(crl='defaultRenderLayer')
        cmds.intField('newJobStartFrame',e=True,value=cmds.getAttr('defaultRenderGlobals.startFrame'))
        cmds.intField('newJobEndFrame',e=True,value=cmds.getAttr('defaultRenderGlobals.endFrame'))
        cmds.intField('newJobFpb',e=True,value=10)
        cmds.intField('newJobPriority',e=True,value=50)
        return

    def rendererChange(self, *args):
        newJobRenderer = cmds.optionMenu('newJobSoftware', q=True, v=True)
        if newJobRenderer == 'maya-mray':
            targetVar = cmds.renderSettings(ign=True)[0]
            cmds.textField('newJobTarget', e=True, tx=str(targetVar))
        elif newJobRenderer == 'maya-vray':
            if cmds.objExists('vraySettings'):
                targetVar = cmds.getAttr('vraySettings.fileNamePrefix', asString=True)
                padding = cmds.getAttr('vraySettings.fileNamePadding', asString=True)
                if cmds.getAttr('vraySettings.imageFormatStr', asString=True) == 'exr (multichannel)':
                    textVar = targetVar+'%'+str(padding)+'n.%e'
                else:
                    textVar = targetVar+'.%'+str(padding)+'n.%e'
                cmds.textField('newJobTarget', e=True, tx=str(textVar))
            else:
                cmds.confirmDialog(icn='warning', t='CR', m='No V-ray setting node exist!', button=['OK'])
                cmds.optionMenu('newJobSoftware', e=True, sl=1)
                cmds.textField('newJobTarget', e=True, tx='')
        return

    def submitProc(self,*args):
        #save file to its own directory.
        #Note: mark in wiki render file need to be accessible to all client
        repVar = cmds.confirmDialog(icn='question', t='Const. Render', m='Would you like to save?', button = ['SAVE', 'DO NOT SAVE', 'CANCEL'])
        if repVar == 'SAVE':
            cmds.file(save=True)
        elif repVar == 'CANCEL':
            cmds.error('cancelled by user')
        allLayerLis=cmds.textScrollList('newJobRenderLayer',q=True,si=True)

        #validate field
        if str(cmds.textField('newJobProject',q=True,tx=True))=='' or\
                                             str(cmds.textField('newJobUser',q=True,tx=True))=='' or\
                                             str(cmds.optionMenu('newJobSoftware',q=True,value=True))=='' or\
                                             str(cmds.textField('newJobScriptPath',q=True,tx=True))=='' or\
                                             str(cmds.textField('newJobTarget',q=True,tx=True))=='' or\
                                             str(cmds.intField('newJobStartFrame',q=True,value=True))=='' or\
                                             str(str(cmds.intField('newJobEndFrame',q=True,value=True)))=='' or\
                                             str(cmds.intField('newJobFpb',q=True,value=True))=='' or\
                                             str(cmds.optionMenu('newJobClassification',q=True,value=True))=='' or\
                                             str(cmds.optionMenu('newJobEnabler',q=True,value=True))=='' or\
                                             str(cmds.intField('newJobPriority',q=True,value=True))=='' or\
                                             allLayerLis==[]:
            cmds.confirmDialog(icn='warning', t='Error',m='Incomplete credential!',button=['Ok'])
            raise StandardError, 'error : incomplete credential'

        #upload job information to server database
        try:
            crSubmitCore.submit(projectVar=str(cmds.textField('newJobProject',q=True,tx=True)),\
                                                 userVar=str(cmds.textField('newJobUser',q=True,tx=True)),\
                                                 softwareVar=str(cmds.optionMenu('newJobSoftware',q=True,value=True)),\
                                                 scriptPathVar=str(cmds.textField('newJobScriptPath',q=True,tx=True)),\
                                                 targetPathVar=str(cmds.textField('newJobTarget',q=True,tx=True)),\
                                                 frameStartVar=str(cmds.intField('newJobStartFrame',q=True,value=True)),\
                                                 frameEndVar=str(str(cmds.intField('newJobEndFrame',q=True,value=True))),\
                                                 blockCount=str(cmds.intField('newJobFpb',q=True,value=True)),\
                                                 priorityVar=str(cmds.intField('newJobPriority',q=True,value=True)),\
                                                 renderLayer=allLayerLis,\
                                                 classificationVar=str(cmds.optionMenu('newJobClassification',q=True,value=True)),\
                                                 enablerVar=str(cmds.optionMenu('newJobEnabler',q=True,value=True)),\
                                                 cameraSet=str(cmds.optionMenu('newJobCamera',q=True,value=True)))
            cmds.confirmDialog(icn='information',t='Done',m='Job has been submitted to database.',button=['OK'])
        except Exception as e:
            cmds.confirmDialog(icn='warning',\
                               t='Error',\
                               m=str(e),\
                               button=['OK'])
            raise StandardError, str(e)
        cmds.deleteUI('constellationSubmitter',wnd=True)
        return

    def refreshFun(self,*args):
        import crSubmitUIMaya
        reload (crSubmitUIMaya)
        return

constellationMayaSubmitter()
