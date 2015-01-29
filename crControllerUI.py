__author__='andrew.willis'

#Shepard Render Controller UI Module
#Andrew Willis 2014

#Module import
import sys, sqlite3, os, socket
import datetime
import crControllerCore
from PyQt4 import QtCore, QtGui, uic
import time

#Determining root path
rootPathVar = os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

class crControllerUI(QtGui.QWidget):
    def __init__(self, *args):
        QtGui.QMainWindow.__init__(self, *args)
        self.main = uic.loadUi(rootPathVar+'/controllerUI.ui')
        self.main.show()
        self.main.setFixedSize(1268, 591)

        self.refreshFun()

        self.main.refreshBtn.clicked.connect(self.refreshFun)
        self.main.activateClientBtn.clicked.connect(lambda*args:self.clientBlocker(switch=1))
        self.main.suspendClientBtn.clicked.connect(lambda*args:self.clientBlocker(switch=0))

        self.main.enableJobBtn.clicked.connect(self.enableJob)
        self.main.disableJobBtn.clicked.connect(self.disableJob)
        self.main.resetJobBtn.clicked.connect(self.resetJob)

        self.main.deleteJobBtn.clicked.connect(self.deleteJob)
        self.main.deleteAllBtn.clicked.connect(self.deleteAll)
        self.main.deleteDoneBtn.clicked.connect(self.deleteDone)
        self.main.offlineClientButton.clicked.connect(self.shutDownClient)

        self.main.outputBtn.clicked.connect(self.openOutputFolder)

        self.main.jobTable.itemSelectionChanged.connect(self.populatePriorityFun)
        self.main.updateSelectedBtn.clicked.connect(self.prioritySet)
        self.main.onlineClientButton.clicked.connect(self.onlineClient)
        return

    def onlineClient(self):
        selectedRecordLis = self.main.clientTable.selectedItems()
        for chk in range(len(selectedRecordLis)/4):
            clientNameVar = str(selectedRecordLis[chk].text())
            crControllerCore.onlineClient(client =  clientNameVar)

        time.sleep(1)
        self.refreshFun()
        return

    def shutDownClient(self):
        repVar = QtGui.QMessageBox.question(None,\
                                          'Shut Down Client',\
                                          'Shut down selected client? Client will finish job assigned to it before shut down.',\
                                          QtGui.QMessageBox.Ok,\
                                          QtGui.QMessageBox.Cancel)
        if repVar == 1024:
            selectedRecordLis = self.main.clientTable.selectedItems()

            if selectedRecordLis == []:
                QtGui.QMessageBox.warning(None,'Error','There is no record selected.')
                raise StandardError, 'error : no record selected'

            for chk in range(len(selectedRecordLis)/4):
                clientNameVar = str(selectedRecordLis[chk].text())
                crControllerCore.changeClientStatus(clientName=str(clientNameVar),\
                                                    blockClient='OFFLINE')
        self.refreshFun()
        return

    def populatePriorityFun(self):
        selectedRowLis = self.main.jobTable.selectedItems()

        if (len(selectedRowLis)/13) == 1:
            self.main.prioritySpinBox.setValue(int(selectedRowLis[10].text()))
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
            crControllerCore.changeJobRecordBlocked(jobUuid=jobUuid,\
                                                        blockStatus='DISABLED')
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
            crControllerCore.changeJobRecordBlocked(jobUuid=jobUuid,\
                                                        blockStatus='ENABLED')
        self.refreshFun()
        return

    #Function to activate and suspend client
    def clientBlocker(self,switch=None):
        #switch 0=SUSPENDED 1=ACTIVE

        selectedRecordLis = self.main.clientTable.selectedItems()

        if selectedRecordLis == []:
            QtGui.QMessageBox.warning(None,'Error','There is no record selected.')
            raise StandardError, 'error : no record selected'

        for chk in range(len(selectedRecordLis)/4):
            clientNameVar = str(selectedRecordLis[chk].text())
            if switch==0:
                crControllerCore.changeClientStatus(clientName=clientNameVar,\
                                                               blockClient='DISABLED')
            else:
                crControllerCore.changeClientStatus(clientName=clientNameVar,\
                                                               blockClient='ENABLED')
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
                if chb[10] == 'DONE':
                    countStatusDone += 1
                if chb[10] == 'RENDERING':
                    countStatusRendering += 1
                if chb[10] == 'QUEUE':
                    countStatusQueue += 1
                if chb[10] == 'ERROR':
                    countStatusError += 1
                tempStatusLis.append(chb[10])
            if countStatusDone == len(tempStatusLis):
                statusinVar = 'DONE'
            elif countStatusQueue == len(tempStatusLis):
                statusinVar = 'QUEUE'
            elif countStatusRendering > 0:
                statusinVar = 'RENDERING'
            elif countStatusDone > 0 and countStatusQueue > 0 and countStatusRendering == 0:
                statusinVar = 'HALTED'

            if countStatusError > 0:
                statusinVar = 'ERROR'

            #Determining color code
            if statusinVar == 'DONE':
                colorCodeVar = QtGui.QColor(100,100,100)
            elif statusinVar == 'QUEUE':
                colorCodeVar = QtGui.QColor(150,150,150)
            elif statusinVar == 'RENDERING':
                colorCodeVar = QtGui.QColor(100,250,100)
            elif statusinVar == 'HALTED':
                colorCodeVar = QtGui.QColor(150,150,0)
            elif statusinVar == 'ERROR':
                colorCodeVar=QtGui.QColor(180,180,0)
            if str(chk[0][11]) == 'DISABLED':
                colorCodeVar = QtGui.QColor(255,0,0)

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
            counter=0
            for chb in chk:
                if chb[10]=='QUEUE':
                    counter+=1

            itemVar=QtGui.QTableWidgetItem(str(counter))
            itemVar.setBackgroundColor(colorCodeVar)
            self.main.jobTable.setItem(cnt,7,itemVar)
            leftVar=counter
            #done
            counter=0
            for chb in chk:
                if chb[10]=='DONE' or chb[10]=='ERROR':
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
                hailCon.settimeout(5)
                hailHost = clientRow[1]
                hailPort = 1989 + int(clientRow[0])
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
                    if clientRow[3] != 'OFFLINE':
                        connectionVar = sqlite3.connect(rootPathVar+'/constellationDatabase.db')
                        connectionVar.execute("UPDATE constellationClientTable SET clientBlocked='DISABLED' WHERE clientName='"+str(clientRow[1])+"'")
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
                cnt+=1
        self.main.clientTable.resizeColumnsToContents()
        return

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = crControllerUI()
    sys.exit(app.exec_())