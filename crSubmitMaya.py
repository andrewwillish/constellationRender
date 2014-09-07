#Constellation Render Manager - Maya Submitter

#Import module
import maya.cmds as cmds
import crSubmitCore, getpass, os
import socket

class constellationMayaSubmitter:
    def __init__(self):
        global renderLayerTextScroll, projectTextField, softwareTextField, userTextField, scriptTextField, targetTextField
        global startIntField, endIntField, blockIntField, priorityIntField, softwareOptMenu, cameraOptMenu
        if cmds.window('constellationSubmitter',exists=True):
            cmds.deleteUI('constellationSubmitter',wnd=True)

        cmds.window('constellationSubmitter',t='Constellation Submitter',s=False)
        cmas=cmds.columnLayout(adj=True)

        ccmas=cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[(1, 150), (2, 305)],p=cmas)

        cm1=cmds.frameLayout(l='Render Layer',w=150,p=ccmas)
        renderLayerTextScroll=cmds.textScrollList(ams=True)

        cm2=cmds.frameLayout(l='Job Setting',p=ccmas)
        ccm2=cmds.columnLayout(adj=True)
        cmds.rowColumnLayout( numberOfColumns=4, columnWidth=[(1, 55), (2, 90), (3, 55), (4, 90)],p=ccm2)
        cmds.text(l='  Project:', al='left')
        projectTextField=cmds.textField()
        cmds.text(l='  Software:', al='left')
        softwareOptMenu=cmds.optionMenu(l='')
        cmds.menuItem(l='')
        cmds.menuItem(l='maya')
        cmds.menuItem(l='maya-vray')
        cmds.menuItem(l='nuke')

        cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[(1, 55),(2, 235)],p=ccm2)
        cmds.text(l='  User:', al='left')
        userTextField=cmds.textField()

        cmds.text(l='  Camera:', al='left')
        cameraOptMenu=cmds.optionMenu(l='',w=235)
        cmds.menuItem(l='')
        for chk in cmds.ls(type='camera'):
            cmds.menuItem(l=str(chk).replace('Shape',''))

        cmds.text(l='  Script:', al='left')
        scriptTextField=cmds.textField()

        cmds.text(l='  Target:', al='left')
        targetTextField=cmds.textField()

        cmds.rowColumnLayout( numberOfColumns=4, columnWidth=[(1, 55), (2, 90), (3, 55), (4, 90)],p=ccm2)
        cmds.text(l='  Start:', al='left')
        startIntField=cmds.intField()
        cmds.text(l='  End:', al='left')
        endIntField=cmds.intField()
        cmds.text(l='  Block:', al='left')
        blockIntField=cmds.intField()
        cmds.text(l='  Priority:', al='left')
        priorityIntField=cmds.intField()

        cmds.separator(p=ccm2)

        cmds.rowColumnLayout( numberOfColumns=3, columnWidth=[(1, 200),(2, 100)],p=ccm2)
        submitJobButton=cmds.button(l='SUBMIT JOB',bgc=[1.0,0.643835616566,0.0],c=self.submitProc)
        refreshButton=cmds.button(l='REFRESH',bgc=[1,1,0],c=self.refreshFun)

        cmds.showWindow()

        #Populate field
        cmds.textScrollList(renderLayerTextScroll,e=True,ra=True)
        for chk in cmds.ls(type='renderLayer'):
            if chk.endswith('defaultRenderLayer')==False:
                cmds.textScrollList(renderLayerTextScroll,e=True,a=str(chk))
                cmds.textScrollList(renderLayerTextScroll,e=True,si=str(chk))

        cmds.textField(projectTextField,e=True,tx='default')
        cmds.textField(userTextField,e=True,tx=str(getpass.getuser()))
        cmds.textField(scriptTextField,e=True, tx=str(cmds.file(q=True,sn=True)))

        targetVar=cmds.renderSettings(ign=True)[0]
        targetVar=targetVar[:targetVar.find('\\<')]
        cmds.textField(targetTextField,e=True,tx=str(targetVar))

        cmds.intField(startIntField,e=True,value=cmds.getAttr('defaultRenderGlobals.startFrame'))
        cmds.intField(endIntField,e=True,value=cmds.getAttr('defaultRenderGlobals.endFrame'))
        cmds.intField(blockIntField,e=True,value=10)
        cmds.intField(priorityIntField,e=True,value=50)
        return

    def submitProc(self,*args):
        global renderLayerTextScroll, projectTextField, softwareTextField, userTextField, scriptTextField, targetTextField
        global startIntField, endIntField, blockIntField, priorityIntField, softwareOptMenu, cameraOptMenu

        #save file
        cmds.file(save=True)
        allLayerLis=cmds.textScrollList(renderLayerTextScroll,q=True,si=True)

        #validate field
        if str(cmds.textField(projectTextField,q=True,tx=True))=='' or\
                                             str(cmds.textField(userTextField,q=True,tx=True))=='' or\
                                             str(cmds.optionMenu(softwareOptMenu,q=True,value=True))=='' or\
                                             str(cmds.textField(scriptTextField,q=True,tx=True))=='' or\
                                             str(cmds.textField(targetTextField,q=True,tx=True))=='' or\
                                             str(cmds.intField(startIntField,q=True,value=True))=='' or\
                                             str(str(cmds.intField(endIntField,q=True,value=True)))=='' or\
                                             str(cmds.intField(blockIntField,q=True,value=True))=='' or\
                                             str(cmds.intField(priorityIntField,q=True,value=True))=='' or\
                                             allLayerLis==[]:
            cmds.confirmDialog(icn='warning', t='Error',m='Incomplete credential!',button=['Ok'])
            raise StandardError, 'error : incomplete credential'

        try:
            #create directory check
            layerLis=allLayerLis
            cameraLis=[str(cmds.optionMenu(cameraOptMenu,q=True,value=True))]
            sceneNameVar=cmds.file(q=True,sn=True)
            sceneNameVar=sceneNameVar[sceneNameVar.rfind('/')+1:sceneNameVar.find('.ma')]

            dirPathVar=str(cmds.textField(targetTextField,q=True,tx=True))
            checkDirVar=dirPathVar[:dirPathVar.rfind('/')]

            layerParsedLis=[]
            for chk in layerLis:
                layerParsedLis.append(checkDirVar.replace('<Layer>',str(chk)))

            cameraParsedLis=[]
            for chk in layerParsedLis:
                for chb in cameraLis:
                    cameraParsedLis.append(chk.replace('<Camera>',str(chb)))

            finalParsedLis=[]
            for chk in cameraParsedLis:
                finalParsedLis.append(chk.replace('<Scene>',sceneNameVar.replace('.ma','')))

            for chk in finalParsedLis:
                if os.path.isdir(chk)==False:
                    os.makedirs(chk)
        except:
            cmds.confirmDialog(icn='warning', t='Error',m='Invalid file name prefix!',button=['Ok'])
            raise StandardError, 'error : invalid naming prefix'


        crSubmitCore.submit(projectVar=str(cmds.textField(projectTextField,q=True,tx=True)),\
                                             userVar=str(cmds.textField(userTextField,q=True,tx=True)),\
                                             softwareVar=str(cmds.optionMenu(softwareOptMenu,q=True,value=True)),\
                                             scriptPathVar=str(cmds.textField(scriptTextField,q=True,tx=True)),\
                                             targetPathVar=str(cmds.textField(targetTextField,q=True,tx=True)),\
                                             frameStartVar=str(cmds.intField(startIntField,q=True,value=True)),\
                                             frameEndVar=str(str(cmds.intField(endIntField,q=True,value=True))),\
                                             blockCount=str(cmds.intField(blockIntField,q=True,value=True)),\
                                             priorityVar=str(cmds.intField(priorityIntField,q=True,value=True)),\
                                             renderLayer=allLayerLis,\
                                             cameraSet=str(cmds.optionMenu(cameraOptMenu,q=True,value=True)))
        cmds.confirmDialog(icn='information',t='Done',m='Job has been submitted to database.',button=['OK'])
        cmds.deleteUI('constellationSubmitter',wnd=True)
        return

    def refreshFun(self,*args):
        import crSubmitMaya
        reload (crSubmitMaya)
        return

constellationMayaSubmitter()