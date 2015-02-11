__author__='andrew.willis'

#Shepard Render Controller UI Module
#Andrew Willis 2014

#Module import
import sys, sqlite3, os, socket
import datetime
import crControllerCore
from PyQt4 import QtGui, uic, QtCore
import time
import math

#Determining root path
rootPathVar = os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

class crControllerUI(QtGui.QWidget):
    def __init__(self, *args):
        QtGui.QMainWindow.__init__(self, *args)
        self.main = uic.loadUi(rootPathVar+'/controllerUI.ui')
        self.main.show()
        self.main.setFixedSize(1319, 591)

        self.main.clientTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.main.clientTable.customContextMenuRequested.connect(self.clientPopup)

        self.main.jobTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.main.jobTable.customContextMenuRequested.connect(self.jobPopup)

        self.refreshFun()

        self.main.refreshBtn.clicked.connect(self.refreshFun)

        self.main.deleteAllBtn.clicked.connect(self.deleteAll)
        self.main.deleteDoneBtn.clicked.connect(self.deleteDone)

        self.main.outputBtn.clicked.connect(self.openOutputFolder)

        self.main.jobTable.itemSelectionChanged.connect(self.populatePriorityFun)
        self.main.updateSelectedBtn.clicked.connect(self.prioritySet)

        self.main.jobTable.itemSelectionChanged.connect(self.populateInformation)
        self.main.jobTable.clicked.connect(self.populateInformation)
        self.main.generateBatchButton.clicked.connect(self.genBatch)
        self.main.deleteJobButton.clicked.connect(self.deleteJob)
        self.main.jobInformationGroup.setEnabled(0)
        return

    def populateInformation(self):
        selectedRowLis = self.main.jobTable.selectedItems()
        if (len(selectedRowLis)/13) == 1:
            #single selection populate the information
            self.main.jobInformationGroup.setEnabled(1)

            jobGrouped = None
            for item in  crControllerCore.listAllJobGrouped():
                if item[0][1] == str(selectedRowLis[0].text()):
                    jobGrouped = item

            if jobGrouped is not None:
                #calculate total block, rendering block, done block, queue block
                #total block
                totalBlock = len(jobGrouped)
                #rendering block
                renderBlock = 0
                for i in jobGrouped:
                    if i[10] == 'RENDERING':renderBlock += 1
                #done block
                doneBlock = 0
                for i in jobGrouped:
                    if i[10] == 'DONE':doneBlock += 1
                #queue block
                queueBlock = 0
                for i in jobGrouped:
                    if i[10] == 'QUEUE':queueBlock += 1

                #build the table
                self.main.progressTable.clear()
                columnCount = 10
                self.main.progressTable.setColumnCount(columnCount)
                for i in range(0, columnCount):
                    self.main.progressTable.setColumnWidth(i, 60)
                rowAmount = math.ceil(float(totalBlock) / float(columnCount))
                self.main.progressTable.setRowCount(int(rowAmount))

                #populate the progress bar
                self.main.queueProgBar.setValue((float(queueBlock)/float(totalBlock))*100.0)
                self.main.inRdrProgBar.setValue((float(renderBlock)/float(totalBlock))*100.0)
                self.main.doneProgBar.setValue((float(doneBlock)/float(totalBlock))*100.0)

                #populate job information
                self.main.uuidLbl.setText(jobGrouped[0][1])
                self.main.layerLbl.setText(jobGrouped[0][9])
                self.main.filePathLbl.setText(jobGrouped[0][5])

                self.main.softwareLbl.setText(jobGrouped[0][4])
                self.main.statusLbl.setText(str(selectedRowLis[6].text()))
                self.main.blockedLbl.setText(jobGrouped[0][11])
                self.main.rdrTimeLbl.setText(str(selectedRowLis[13].text()))
                instruct = crControllerCore.genBatch(uuid = jobGrouped[0][1])
                self.main.commandLbl.setText(instruct)

                #populate the table
                column = 0
                width = 0
                for item in jobGrouped:
                    clients = crControllerCore.listAllClient()
                    renderingClient = ''
                    for clt in clients:
                        if str(clt[2]) == str(item[0]):renderingClient = clt[1]
                    if column == columnCount:
                        column = 0
                        width += 1
                    blockRange = str(item[7])+'-'+str(item[8])
                    blockItem = QtGui.QTableWidgetItem(renderingClient+"\r\n"+blockRange)
                    if item[10] == 'QUEUE':
                        blockItem.setBackgroundColor(QtGui.QColor(200, 200, 200))
                    elif item[10] == 'DONE':
                        blockItem.setBackgroundColor(QtGui.QColor(0, 200, 0))
                    elif item[10] == 'RENDERING':
                        blockItem.setBackgroundColor(QtGui.QColor(255, 255, 100))
                    elif item[10] == 'ERROR':
                        blockItem.setBackgroundColor(QtGui.QColor(255, 98, 101))
                    else:
                        blockItem.setBackgroundColor(QtGui.QColor(0, 0, 0))
                    self.main.progressTable.setItem(width, column, blockItem)
                    column +=1
            self.main.progressTable.resizeColumnsToContents()
            self.main.progressTable.resizeRowsToContents()
        else:
            #multiple selection clear all the information
            self.main.jobInformationGroup.setEnabled(0)
            self.main.progressTable.clear()

            self.main.uuidLbl.clear()
            self.main.layerLbl.clear()
            self.main.filePathLbl.clear()

            self.main.softwareLbl.clear()
            self.main.statusLbl.clear()
            self.main.blockedLbl.clear()
            self.main.rdrTimeLbl.clear()
            self.main.commandLbl.clear()

            self.main.queueProgBar.setValue(0)
            self.main.inRdrProgBar.setValue(0)
            self.main.doneProgBar.setValue(0)
        return

    def jobPopup(self, pos):
        menu = QtGui.QMenu()
        enaDisaMen = menu.addMenu('Enable / Disable Job')
        enaJob = enaDisaMen.addAction('Enable Job')
        disaJob = enaDisaMen.addAction('Disable Job')
        menu.addSeparator()
        resJob = menu.addAction('Reset Job')
        delJob = menu.addAction('Delete Job')
        menu.addSeparator()
        genBatch = menu.addAction('Generate Batch')
        action = menu.exec_(self.main.jobTable.viewport().mapToGlobal(pos))
        if action == enaJob: self.enableJob()
        elif action == disaJob: self.disableJob()
        elif action == resJob: self.resetJob()
        elif action == delJob: self.deleteJob()
        elif action == genBatch: self.genBatch()
        return

    def clientPopup(self, pos):
        menu = QtGui.QMenu()
        enaClient = menu.addAction('Enable Client')
        disaClient = menu.addAction('Disable Client')
        menu.addSeparator()
        delClt = menu.addAction('Delete Client')
        menu.addSeparator()
        clt = menu.addMenu('Client')
        strtClt = clt.addAction('Start Client (Tender Required)')
        shutDownClt = clt.addAction('Instruct Client to Shutdown')
        mch = menu.addMenu('Machine')
        wolMch = mch.addAction('Wake On Lan')
        mch.addSeparator()
        shutDownMch = mch.addAction('Shut Down')
        restartMch = mch.addAction('Restart')
        menu.addSeparator()
        chgClass = menu.addAction('Change Class')
        menu.addSeparator()
        clrJob = menu.addAction('Clear Job')

        action = menu.exec_(self.main.clientTable.viewport().mapToGlobal(pos))
        if action == enaClient: self.clientBlocker(switch=1)
        elif action == disaClient: self.clientBlocker(switch=0)
        elif action == delClt: self.deleteClient()
        elif action == strtClt: self.onlineClient()
        elif action == shutDownClt: self.shutDownClient()
        elif action == shutDownMch: self.shutDownMachine()
        elif action == restartMch: self.restartMachine()
        elif action == wolMch: self.wolTrig()
        elif action == chgClass: self.changeClass()
        elif action == clrJob: self.clearJobFromClient()
        return

    def clearJobFromClient(self):
        selectedRecordLis = self.main.clientTable.selectedItems()
        if selectedRecordLis == []:
            QtGui.QMessageBox.warning(None,'Error','There is no record selected.')
            raise StandardError, 'error : no record selected'
        for chk in range(len(selectedRecordLis)/4):
            clientNameVar = str(selectedRecordLis[chk].text())
            for clientRow in crControllerCore.listAllClient():
                hailCon = socket.socket()
                hailCon.settimeout(4)
                hailHost = clientRow[1]
                hailPort = 1990 + int(clientRow[0])
                repVar = None
                try:
                    hailCon.connect((hailHost, hailPort))
                    hailCon.send('stallCheck')
                    repVar = hailCon.recv(1024)
                    hailCon.close()
                except:
                    pass
                if repVar is not None:
                    QtGui.QMessageBox.warning(None,'Error','Client is ONLINE. Turn client off before clear stall job.')
                    raise StandardError, 'error : client is online.'
                else:
                    crControllerCore.clearStat(clientName=clientNameVar)
        time.sleep(2)
        self.refreshFun()
        return

    def resetClient(self):
        selectedRecordLis = self.main.clientTable.selectedItems()
        if selectedRecordLis == []:
            QtGui.QMessageBox.warning(None,'Error','There is no record selected.')
            raise StandardError, 'error : no record selected'

        for chk in range(len(selectedRecordLis)/4):
            clientNameVar = str(selectedRecordLis[chk].text())
            crControllerCore.clientCom(client=clientNameVar, message='quit', portBase=1990)
            crControllerCore.clientCom(client=clientNameVar, message='wakeUp', portBase=1991)
        time.sleep(5)
        self.refreshFun()
        return

    def restartClient(self):
        selectedRecordLis = self.main.clientTable.selectedItems()
        if selectedRecordLis == []:
            QtGui.QMessageBox.warning(None,'Error','There is no record selected.')
            raise StandardError, 'error : no record selected'

        for chk in range(len(selectedRecordLis)/4):
            clientNameVar = str(selectedRecordLis[chk].text())
            crControllerCore.clientCom(client=clientNameVar, message='restartClient', portBase=1990)
        time.sleep(2)
        self.refreshFun()
        return

    def changeClass(self):
        selectedRecordLis = self.main.clientTable.selectedItems()
        if selectedRecordLis == []:
            QtGui.QMessageBox.warning(None, 'Error','There is no record selected.')
            raise StandardError, 'error : no record selected'

        newClass, ok = QtGui.QInputDialog.getText(None, 'Const. Render', \
    'Enter new classification.\nPlease be aware that previously assigned job to old class will not be rendered by this client.')

        for chk in range(len(selectedRecordLis)/4):
            clientNameVar = str(selectedRecordLis[chk].text())
            if ok:
                crControllerCore.changeClass(client=clientNameVar, classification=newClass)
        self.refreshFun()
        return

    def wolTrig(self):
        selectedRecordLis = self.main.clientTable.selectedItems()
        if selectedRecordLis == []:
            QtGui.QMessageBox.warning(None,'Error','There is no record selected.')
            raise StandardError, 'error : no record selected'

        for chk in range(len(selectedRecordLis)/4):
            clientNameVar = str(selectedRecordLis[chk].text())
            crControllerCore.wolTrig(client=clientNameVar)
        self.refreshFun()
        return

    def restartMachine(self):
        selectedRecordLis = self.main.clientTable.selectedItems()
        if selectedRecordLis == []:
            QtGui.QMessageBox.warning(None,'Error','There is no record selected.')
            raise StandardError, 'error : no record selected'

        for chk in range(len(selectedRecordLis)/4):
            clientNameVar = str(selectedRecordLis[chk].text())
            crControllerCore.clientCom(client=clientNameVar, message='restart', portBase=1990)
        time.sleep(2)
        self.refreshFun()
        return

    def shutDownMachine(self):
        selectedRecordLis = self.main.clientTable.selectedItems()
        if selectedRecordLis == []:
            QtGui.QMessageBox.warning(None,'Error','There is no record selected.')
            raise StandardError, 'error : no record selected'

        for chk in range(len(selectedRecordLis)/4):
            clientNameVar = str(selectedRecordLis[chk].text())
            crControllerCore.clientCom(client=clientNameVar, message='shutDown', portBase=1990)
        time.sleep(2)
        self.refreshFun()
        return

    def genBatch(self):
        selectedRowLis = self.main.jobTable.selectedItems()
        if selectedRowLis == []:
            QtGui.QMessageBox.warning(None,'Error','There is no job selected.')
            raise StandardError, 'error : no record selected'
        instructionLis = []
        if (len(selectedRowLis)/13) == 1:
            instructionLis.append(crControllerCore.genBatch(uuid = selectedRowLis[0].text()))
        repVar = str(QtGui.QFileDialog.getSaveFileName(None, 'Save Batch file'))
        if not repVar.endswith('.bat'):repVar = repVar+'.bat'
        opn = open(repVar, 'w')
        for item in instructionLis:
            opn.write(str(item)+'\n')
        opn.close()
        return

    def deleteClient(self):
        selectedRecordLis = self.main.clientTable.selectedItems()
        if selectedRecordLis == []:
            QtGui.QMessageBox.warning(None,'Error','There is no record selected.')
            raise StandardError, 'error : no record selected'

        repVar = QtGui.QMessageBox.question(None, 'Const. Render', 'Delete selected client?',\
                                            QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if repVar == 16384:
            for chk in range(len(selectedRecordLis)/4):
                clientNameVar = str(selectedRecordLis[chk].text())
                crControllerCore.clientCom(client=clientNameVar, message='quit', portBase=1990)
                crControllerCore.deleteClient(clientName = clientNameVar)
        self.refreshFun()
        return

    def onlineClient(self):
        selectedRecordLis = self.main.clientTable.selectedItems()
        if selectedRecordLis == []:
            QtGui.QMessageBox.warning(None,'Error','There is no record selected.')
            raise StandardError, 'error : no record selected'
        for chk in range(len(selectedRecordLis)/4):
            clientNameVar = str(selectedRecordLis[chk].text())
            crControllerCore.clientCom(client=clientNameVar, message='wakeUp', portBase=1991)

        time.sleep(5)
        self.refreshFun()
        return

    def shutDownClient(self):
        selectedRecordLis = self.main.clientTable.selectedItems()
        if selectedRecordLis == []:
            QtGui.QMessageBox.warning(None,'Error','There is no record selected.')
            raise StandardError, 'error : no record selected'

        repVar = QtGui.QMessageBox.question(None,\
                                          'Const. Render 4.2',\
                                          'Shutdown client?',\
                                          QtGui.QMessageBox.Ok,\
                                          QtGui.QMessageBox.Cancel)
        if repVar == 1024:
            for chk in range(len(selectedRecordLis)/4):
                clientNameVar = str(selectedRecordLis[chk].text())
                crControllerCore.changeClientStatus(clientName=str(clientNameVar), blockClient='OFFLINE')
        self.refreshFun()
        return

    def populatePriorityFun(self):
        selectedRowLis = self.main.jobTable.selectedItems()

        if (len(selectedRowLis)/13) == 1:self.main.prioritySpinBox.setValue(int(selectedRowLis[10].text()))
        return

    def prioritySet(self):
        selectedRowLis = self.main.jobTable.selectedItems()
        priorityVar = str(self.main.prioritySpinBox.value())

        cnt = 0
        while cnt <= (len(selectedRowLis)/13)-1:
            uuidVar = str(selectedRowLis[cnt].text())
            crControllerCore.changeJobPrior(uid=uuidVar, priority=priorityVar)
            cnt+=1

        self.refreshFun()
        return

    def prioritySet2(self):
        rowCountVar = int(self.main.jobTable.rowCount())

        cnt = 0
        while cnt <= (rowCountVar-1):
            try:
                self.main.jobTable.selectRow(cnt)
                singSelVar = self.main.jobTable.selectedItems()
                uuidVar = str(singSelVar[0].text())
                newValVar = self.main.jobTable.cellWidget(cnt,10)
                newValVar = str(newValVar.value())
                crControllerCore.changeJobPrior(uid=uuidVar, priority=newValVar)
            except:
                pass
            cnt += 1
        self.main.jobTable.clearSelection()
        return

    def openOutputFolder(self):
        selectedRecordLis = self.main.jobTable.selectedItems()
        if selectedRecordLis != []:
            if len(selectedRecordLis) > 14:
                QtGui.QMessageBox.warning(None, 'Error', 'Unable to open multiple job folder output.')
            else:
                try:
                    uuidVar = selectedRecordLis[0]
                    crControllerCore.openOutput(uid=str(uuidVar.text()))
                except Exception as e:
                    print str(e)
                    QtGui.QMessageBox.warning(None, 'Error', 'Folder non-exist.')
        return

    def deleteDone(self):
        repVar = QtGui.QMessageBox.question(None,\
                                          'Delete Done Job',\
                                          'Delete Done job? This operation can not be undone.',\
                                          QtGui.QMessageBox.Ok,\
                                          QtGui.QMessageBox.Cancel)
        if repVar == 1024:crControllerCore.clearJobRecord(done=True)
        self.refreshFun()
        return

    def deleteAll(self):
        repVar = QtGui.QMessageBox.question(None,\
                                          'Delete All Job',\
                                          'Delete All job? This operation can not be undone.',\
                                          QtGui.QMessageBox.Ok,\
                                          QtGui.QMessageBox.Cancel)
        if repVar == 1024:crControllerCore.clearJobRecord(all=True)
        self.refreshFun()
        return

    def deleteJob(self):
        selectedRecordLis = self.main.jobTable.selectedItems()
        if selectedRecordLis == []:
            QtGui.QMessageBox.warning(None, 'Error','There is no record selected.')
            raise StandardError, 'error : no record selected'

        repVar=QtGui.QMessageBox.question(None,\
                                          'Delete Job',\
                                          'Delete selected job? This operation can not be undone.',\
                                          QtGui.QMessageBox.Ok,\
                                          QtGui.QMessageBox.Cancel)

        if repVar == 1024:
            for chk in range(len(selectedRecordLis)/12):
                jobUuid = str(selectedRecordLis[chk].text())
                crControllerCore.clearJobRecord(uid=jobUuid)
            self.refreshFun()
        return

    def resetJob(self):
        selectedRecordLis = self.main.jobTable.selectedItems()
        if selectedRecordLis == []:
            QtGui.QMessageBox.warning(None,'Error','There is no record selected.')
            raise StandardError, 'error : no record selected'

        repVar = QtGui.QMessageBox.question(None,\
                                          'Reset Job',\
                                          'Reset selected job? Previous rendered file will be deleted.',\
                                          QtGui.QMessageBox.Ok,\
                                          QtGui.QMessageBox.Cancel)
        if repVar == 1024:
            for chk in range(len(selectedRecordLis)/12):
                jobUuid= str(selectedRecordLis[chk].text())
                crControllerCore.resetJobRecord(uid=jobUuid)
            self.refreshFun()
        return

    #Function to disable job:
    def disableJob(self):
        selectedRecordLis = self.main.jobTable.selectedItems()

        if selectedRecordLis == []:
            QtGui.QMessageBox.warning(None,'Error','There is no record selected.')
            raise StandardError, 'error : no record selected'

        for chk in range(len(selectedRecordLis)/13):
            jobUuid = str(selectedRecordLis[chk].text())
            crControllerCore.changeJobRecordBlocked(jobUuid=jobUuid, blockStatus='DISABLED')
        self.refreshFun()
        return

    #Function to enable job:
    def enableJob(self):
        selectedRecordLis = self.main.jobTable.selectedItems()

        if selectedRecordLis == []:
            QtGui.QMessageBox.warning(None,'Error','There is no record selected.')
            raise StandardError, 'error : no record selected'

        for chk in range(len(selectedRecordLis)/13):
            jobUuid= str(selectedRecordLis[chk].text())
            crControllerCore.changeJobRecordBlocked(jobUuid=jobUuid,  blockStatus='ENABLED')
        self.refreshFun()
        return

    #Function to activate and suspend client
    def clientBlocker(self,switch=None):
        selectedRecordLis = self.main.clientTable.selectedItems()

        if selectedRecordLis == []:
            QtGui.QMessageBox.warning(None,'Error','There is no record selected.')
            raise StandardError, 'error : no record selected'

        for chk in range(len(selectedRecordLis)/4):
            clientNameVar = str(selectedRecordLis[chk].text())
            if switch == 0:
                crControllerCore.changeClientStatus(clientName=clientNameVar, blockClient='DISABLED')
            else:
                crControllerCore.changeClientStatus(clientName=clientNameVar, blockClient='ENABLED')
        self.refreshFun()
        return

    #Head function for refresh
    def refreshFun(self):
        self.populateClientFun()
        self.populateJobFun()
        return

    #Function to populate job table
    def populateJobFun(self):
        self.main.jobTable.setRowCount(0)
        self.main.jobTable.setRowCount(len(crControllerCore.listAllJobGrouped()))

        cnt=0
        for chk in reversed(crControllerCore.listAllJobGrouped()):
            #Status and blocker Extend
            tempStatusLis = []
            countStatusDone = 0
            countStatusRendering = 0
            countStatusQueue = 0
            countStatusError = 0
            for chb in chk:
                if chb[10] == 'DONE': countStatusDone += 1
                if chb[10] == 'RENDERING': countStatusRendering += 1
                if chb[10] == 'QUEUE': countStatusQueue += 1
                if chb[10] == 'ERROR': countStatusError += 1
                tempStatusLis.append(chb[10])
            if countStatusDone == len(tempStatusLis):statusinVar = 'DONE'
            elif countStatusQueue == len(tempStatusLis):statusinVar = 'QUEUE'
            elif countStatusRendering > 0:statusinVar = 'RENDERING'
            elif countStatusDone > 0 and countStatusQueue > 0 and countStatusRendering == 0:
                statusinVar = 'HALTED'

            if countStatusError > 0:statusinVar = 'ERROR'

            #Determining color code
            if statusinVar == 'DONE':colorCodeVar = QtGui.QColor(100,100,100)
            elif statusinVar == 'QUEUE':colorCodeVar = QtGui.QColor(150,150,150)
            elif statusinVar == 'RENDERING':colorCodeVar = QtGui.QColor(100,250,100)
            elif statusinVar == 'HALTED':colorCodeVar = QtGui.QColor(150,150,0)
            elif statusinVar == 'ERROR':colorCodeVar=QtGui.QColor(180,180,0)
            if str(chk[0][11]) == 'DISABLED':colorCodeVar = QtGui.QColor(255,0,0)

            #uuid
            itemVar=QtGui.QTableWidgetItem(str(chk[0][1]))
            itemVar.setBackgroundColor(colorCodeVar)
            self.main.jobTable.setItem(cnt,0,itemVar)
            #project
            itemVar=QtGui.QTableWidgetItem(str(chk[0][2]))
            itemVar.setBackgroundColor(colorCodeVar)
            self.main.jobTable.setItem(cnt,1,itemVar)
            #software
            itemVar=QtGui.QTableWidgetItem(str(chk[0][4]))
            itemVar.setBackgroundColor(colorCodeVar)
            self.main.jobTable.setItem(cnt,2,itemVar)
            #user
            itemVar=QtGui.QTableWidgetItem(str(chk[0][3]))
            itemVar.setBackgroundColor(colorCodeVar)
            self.main.jobTable.setItem(cnt,3,itemVar)
            #file
            itemVar=QtGui.QTableWidgetItem('...'+str(chk[0][5])[len(str(chk[0][5]))-15:])
            itemVar.setBackgroundColor(colorCodeVar)
            self.main.jobTable.setItem(cnt,4,itemVar)
            #layer
            itemVar=QtGui.QTableWidgetItem(str(chk[0][9]))
            itemVar.setBackgroundColor(colorCodeVar)
            self.main.jobTable.setItem(cnt,5,itemVar)
            #status
            itemVar=QtGui.QTableWidgetItem(statusinVar)
            itemVar.setBackgroundColor(colorCodeVar)
            self.main.jobTable.setItem(cnt,6,itemVar)
            #left
            counter = 0
            for chb in chk:
                if chb[10] == 'QUEUE':counter += 1

            itemVar=QtGui.QTableWidgetItem(str(counter))
            itemVar.setBackgroundColor(colorCodeVar)
            self.main.jobTable.setItem(cnt,7,itemVar)
            leftVar=counter
            #done
            counter = 0
            for chb in chk:
                if chb[10] == 'DONE' or chb[10]=='ERROR':
                    counter+=1

            itemVar=QtGui.QTableWidgetItem(str(counter))
            itemVar.setBackgroundColor(colorCodeVar)
            self.main.jobTable.setItem(cnt,8,itemVar)
            doneVar=counter
            #Percentage progress
            counter=0
            for chb in chk:
                if chb[10]=='RENDERING':
                    counter+=1
            renderingVar=counter
            donePerc=(float(doneVar)/(float(leftVar)+float(doneVar)+float(renderingVar)))*100.0
            renderingPerc=(float(renderingVar)/(float(leftVar)+float(doneVar)+float(renderingVar)))*100.0
            donePerc=("%.1f" % donePerc)
            renderingPerc=("%.1f" % renderingPerc)

            itemVar=QtGui.QTableWidgetItem(str(donePerc)+'('+str(renderingPerc)+')')
            itemVar.setBackgroundColor(colorCodeVar)
            self.main.jobTable.setItem(cnt,9,itemVar)

            #Priority
            itemVar=QtGui.QTableWidgetItem(str(chk[0][13]))
            itemVar.setBackgroundColor(colorCodeVar)
            self.main.jobTable.setItem(cnt,10,itemVar)

            #Blocked
            itemVar=QtGui.QTableWidgetItem(str(chk[0][11]))
            itemVar.setBackgroundColor(colorCodeVar)
            self.main.jobTable.setItem(cnt,11,itemVar)
            #datetime
            itemVar=QtGui.QTableWidgetItem(str(chk[0][12]))
            itemVar.setBackgroundColor(colorCodeVar)
            self.main.jobTable.setItem(cnt,12,itemVar)

            #average render time
            renderTotal=0
            counter=0
            for chb in chk:
                if chb[16]!=None:
                    runTime=int(chb[16])
                    renderTotal=renderTotal+int(runTime)
                    counter+=1

            if renderTotal==0:
                averageTime=0
            else:
                averageTime=renderTotal/counter
            averageTime=datetime.timedelta(seconds=averageTime)
            itemVar=QtGui.QTableWidgetItem(str(averageTime))
            itemVar.setBackgroundColor(colorCodeVar)
            self.main.jobTable.setItem(cnt,13,itemVar)
            cnt+=1
        self.main.jobTable.resizeColumnsToContents()
        return

    #Function to populate client table
    def populateClientFun(self):
        self.main.clientTable.setRowCount(0)
        if crControllerCore.listAllClient()[0] != '<no client registered to the network>':
            #client status actual
            for clientRow in crControllerCore.listAllClient():
                hailCon = socket.socket()
                hailCon.settimeout(4)
                hailHost = clientRow[1]
                hailPort = 1990 + int(clientRow[0])
                repVar = None
                try:
                    hailCon.connect((hailHost, hailPort))
                    hailCon.send('stallCheck')
                    repVar = hailCon.recv(1024)
                    hailCon.close()
                except:
                    pass
                if repVar is None:
                    #change client status to OFFLINE
                    #if clientRow[3] != 'OFFLINE':
                    connectionVar = sqlite3.connect(rootPathVar+'/constellationDatabase.db')
                    connectionVar.execute("UPDATE constellationClientTable SET clientBlocked='OFFLINE' WHERE clientName='"+str(clientRow[1])+"'")
                    connectionVar.commit()
                    connectionVar.close()

            #populating the clientTable
            self.main.clientTable.setRowCount(len(crControllerCore.listAllClient()))
            cnt = 0
            for chk in crControllerCore.listAllClient():
                if chk[3] == 'ENABLED':colorCodeVar = QtGui.QColor(0,150,0)
                elif chk[3] == 'DISABLED':colorCodeVar = QtGui.QColor(150,150,0)
                elif chk[3] == 'OFFLINE':colorCodeVar = QtGui.QColor(150,0,0)

                itemVar = QtGui.QTableWidgetItem(str(chk[1]))
                itemVar.setBackgroundColor(colorCodeVar)
                self.main.clientTable.setItem(cnt, 0, itemVar)

                itemVar = QtGui.QTableWidgetItem(str(chk[9]))
                itemVar.setBackgroundColor(colorCodeVar)
                self.main.clientTable.setItem(cnt, 1, itemVar)

                itemVar = QtGui.QTableWidgetItem(str(chk[2]))
                itemVar.setBackgroundColor(colorCodeVar)
                self.main.clientTable.setItem(cnt, 2, itemVar)

                itemVar = QtGui.QTableWidgetItem(str(chk[3]))
                itemVar.setBackgroundColor(colorCodeVar)
                self.main.clientTable.setItem(cnt, 3, itemVar)

                itemVar = QtGui.QTableWidgetItem(str(chk[8]))
                itemVar.setBackgroundColor(colorCodeVar)
                self.main.clientTable.setItem(cnt, 4, itemVar)
                cnt+=1
        self.main.clientTable.resizeColumnsToContents()
        return

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = crControllerUI()
    sys.exit(app.exec_())