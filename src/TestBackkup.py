"""
To Do List:

+ Program the header creation for files without headers
    + Create function to allow user to rename column headers
    + Create output table header
+ Create preferences menu
+ Create dictionary(?) that includes room type and room size:
    add group gender category
    only list available rooms with matching gender with enough space for people
+ Ensure all list operations are dynamic and not hard coded
+ Edit roomSort function to allow to define row from which to start
    + Prime the function with code to unassign all of the rooms from the current room down
    + When reporting results, clear out the assigned rooms from the first unassigned room down
        +Check jack group gender; perform match based on whether matches gender or not
+ Figure out way to incorporate room genders
    + Add column in room availability?
    

+ Check to see if "Has header?" boolean check is working
+ Create a save/open system that works with the current layout to save progress

"""


global MAX_ROOMMATES, MAX_PREF_LIST_LENGTH, MAX_POINTS, FILE_LOAD_LIST
global GROUP_LIST_HASHEADER, ROOM_LIST_HASHEADER, jackList, roomDict

MAX_ROOMMATES = 4
MAX_PREF_LIST_LENGTH = 10
MAX_POINTS = 5
FILE_LOAD_LIST = []
GROUP_LIST_HASHEADER = True
ROOM_LIST_HASHEADER = True
jackList = []
roomList = []
assignmentDict = {}

import random
from PyQt5.Qt import QWidget
from PyQt5.QtWidgets import (QTableWidget, QLineEdit, QTableWidgetItem, QMainWindow,
                             QTabWidget, QAction, QApplication, QFileDialog, QVBoxLayout,
                             QGridLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy,
                             QMessageBox, QCheckBox)
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt

class JackGroup:
    def __init__(self, inPoints, inType, inNameList, inPrefList, assignedRoomIn = 0):
        self.points = inPoints
        self.nameList = inNameList
        if inType.lower() == "male":
            self.groupType = "male"
        elif inType.lower() == "female":
            self.groupType = "female"
        elif inType.lower() == "freshman":
            self.groupType = "freshman"
        else:
            self.groupType = "error"
            self.errorMessage = QMessageBox()
            self.errorMessage.setIcon(QMessageBox.Critical)
            self.errorMessage.setWindowIcon(QIcon("icon\error.png"))
            self.errorMessage.setText("Invalid group type: " + str(inType))
            self.errorMessage.setDetailedText("Group Type Options:\nMale\nFemale\nFreshman")
            self.errorMessage.setWindowTitle("Group Creation Error")
            self.errorMessage.setStandardButtons(QMessageBox.Ok)
            self.errorMessage.setEscapeButton(QMessageBox.Close)
            self.errorMessage.show()
        self.prefList = inPrefList
        self.assignedRoom = assignedRoomIn
    
    def __str__(self):
        return ("Points: " + str(self.points) + "; Group Type: " + str(self.groupType) + "; Assigned Room: " + str(self.assignedRoom) + "; Members: " + str(self.nameList) + "; Room Pref: " + str(self.prefList))

class Room:
    def __init__(self, inNumber, inType, inAssigned):
        self.number = inNumber
        if inType.lower() == "male":
            self.type = "male"
        elif inType.lower() == "female":
            self.type = "female"
        elif inType.lower() == "freshman":
            self.type = "freshman"
        else:
            self.type = "error"
            self.errorMessage = QMessageBox()
            self.errorMessage.setIcon(QMessageBox.Critical)
            self.errorMessage.setWindowIcon(QIcon("icon\error.png"))
            self.errorMessage.setText("Invalid room type: " + str(inType))
            self.errorMessage.setDetailedText("Room Type Options:\nMale\nFemale\nFreshman")
            self.errorMessage.setWindowTitle("Room Creation Error")
            self.errorMessage.setStandardButtons(QMessageBox.Ok)
            self.errorMessage.setEscapeButton(QMessageBox.Close)
            self.errorMessage.show()
        self.unassigned = inAssigned
        
    def __str__(self):
        return("Number: " + str(self.number) + "; Type: " + str(self.inType) + "; Assigned: " + str(self.assigned))
               
#Used to sort the jackGroup object lists
def pointSortKey(self):
        return self.points      
      
def roomSortKey(self):
        return self.assignedRoom

def makeRoomDictFromObjList(inRoomList):
    workingDic = {}
    for room in inRoomList:
        workingDic[int(room.number)] = room
    return workingDic

def getAvailableRoomsFromRow(inRoomList, inGroupList, inRow):
    roomList = inRoomList
    groupList = inGroupList
    row = inRow
    avaiRoomList = []
    for room in roomList:
        if room.unassigned and int(room.number) != 0:            
            avaiRoomList.append(int(room.number))
    for group_number in range(row, len(groupList)):
        if int(groupList[group_number].assignedRoom) != 0:
            avaiRoomList.append(int(groupList[group_number].assignedRoom))
    avaiRoomList = [value for value in avaiRoomList if value != 0]
    avaiRoomList.sort()
    return(avaiRoomList)

def createRoomTableFromCSV(inRoomTable, fileDir):
    roomLoadInput = open(fileDir, 'r')
    inRoomList = []
    for row in roomLoadInput:
        tempRoomList = []
        tempRow = row.split(',')
        for cell in tempRow:
            cell = ' '.join(cell.split())
            tempRoomList.append(cell)
        inRoomList.append(tempRoomList)       
    if ROOM_LIST_HASHEADER == True:
        inRoomTable.setRowCount(len(inRoomList)-1)
        roomHeader = inRoomList[0]
        inRoomList.pop(0)
    else:
        inRoomTable.setRowCount(len(inRoomList))
        roomHeader = ["Number", "Type", "Assigned"]
    inRoomTable.setColumnCount(3)
    inRoomTable.setHorizontalHeaderLabels(roomHeader)
    for x_val in range(len(inRoomList[0])):
        for y_val in range(len(inRoomList)):
            inRoomTable.setItem(y_val, x_val, QTableWidgetItem(inRoomList[y_val][x_val]))

def createJackGroupTableFromCSV(inJackTable, fileDir):
    jackGroupLoadInput = open(fileDir, 'r')
    inJackGroupList = []
    for row in jackGroupLoadInput:
        tempRoomList = []
        tempRow = row.split(',')
        for cell in tempRow:
            cell = ' '.join(cell.split())
            tempRoomList.append(cell)
        inJackGroupList.append(tempRoomList)       
    if GROUP_LIST_HASHEADER == True:
        inJackTable.setRowCount(len(inJackGroupList)-1)
        jackHeader = inJackGroupList[0]
        inJackGroupList.pop(0)
    else:
        inJackTable.setRowCount(len(inJackGroupList))
        jackHeader = ["Points", "Group Type"]
        for index in range(1,MAX_ROOMMATES+1):
            jackHeader.append("Member " + str(index))
        for index in range(1,MAX_PREF_LIST_LENGTH+1):
            jackHeader.append("Choice " + str(index))       
        jackHeader.append("Assigned Room") 
    inJackTable.setColumnCount(len(inJackGroupList[0]))
    inJackTable.setHorizontalHeaderLabels(jackHeader)
    for x_val in range(len(inJackGroupList[0])):
        for y_val in range(len(inJackGroupList)):
            inJackTable.setItem(y_val, x_val, QTableWidgetItem(inJackGroupList[y_val][x_val]))

def createBlankOutputTable(inOutputTable, numRows):
    inOutputTable.setRowCount(numRows)
    outputHeader = ["Assigned Room"]
    for index in range(1,MAX_ROOMMATES+1):
        outputHeader.append("Member " + str(index))
    inOutputTable.setColumnCount(MAX_ROOMMATES+1)
    inOutputTable.setHorizontalHeaderLabels(outputHeader)

def getDataFromTable(inTable):
    workingList = []
    for y_val in range(inTable.rowCount()):
        tempRow = []
        for x_val in range(inTable.columnCount()):
            tempRow.append(inTable.item(y_val, x_val).text())
        workingList.append(tempRow)
    return workingList

def createJackGroupsFromTable(sourceTable):
    global jackList
    jackList = []
    workingList = getDataFromTable(sourceTable)
    for row in workingList:
        groupSetupIndex = 0
        tempNamesList = []
        tempRoomPrefList = []
        tempGroupType = row[1]
        tempPoints = float(row[0])
        groupSetupIndex = 2
        while groupSetupIndex - 1 < MAX_ROOMMATES + 1:
            if row[groupSetupIndex] != "":
                tempNamesList.append(row[groupSetupIndex])
            groupSetupIndex += 1
        while groupSetupIndex - 1 < MAX_ROOMMATES + MAX_PREF_LIST_LENGTH + 1:
            if row[groupSetupIndex] != "":
                tempRoomPrefList.append(int(row[groupSetupIndex]))
            groupSetupIndex += 1
        tempAssignedRoom = int(row[groupSetupIndex])
        jackList.append(JackGroup(tempPoints, tempGroupType, tempNamesList, tempRoomPrefList, tempAssignedRoom))
        
def createRoomsFromTable(sourceTable):
    global roomList
    roomList = []
    workingList = getDataFromTable(sourceTable)
    for row in workingList:
        roomList.append(Room(row[0], row[1], row[2]))

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.gui = TabsWidget(self)
        self.setGeometry(50,50,700,500)
        self.setWindowTitle("Room Assignment")
        self.setWindowIcon(QIcon('bakerCrest.png'))
        
        #Set Up Menu Buttons
        self.newFile = QAction(QIcon('icon/new.png'),'New', self)
        self.newFile.setShortcut('Ctrl+N')
        self.newFile.setStatusTip('Create new file')
        #self.newFile.triggered.connect(self.showNewDialog)
            #Write New Dialog
            #New: allow to set         
        self.openFile = QAction(QIcon('icon/open.png'),'Open', self)
        self.openFile.setShortcut('Ctrl+O')
        self.openFile.setStatusTip('Open new file')
        self.openFile.triggered.connect(self.gui.showOpenMenu)
        
        self.saveFile = QAction(QIcon('icon/save.png'), 'Save', self)
        self.saveFile.setShortcut('Ctrl+S')
        self.saveFile.setStatusTip('Save current file')
        #self.saveFile.triggered.connect(self.showSaveDialog)
                    #Need to write showSaveDialog
        
        self.shuffleData= QAction(QIcon('icon/sort.png'), 'Shuffle', self)
        self.shuffleData.setShortcut('Ctrl+M')
        self.shuffleData.setStatusTip('Shuffle jack groups by point')    
        self.shuffleData.triggered.connect(self.gui.sortByPoints)
        
        self.sortRooms = QAction(QIcon('icon/run.png'), 'Assign Rooms', self)
        self.sortRooms.setShortcut('Ctrl+L')
        self.sortRooms.setStatusTip('Assign rooms by priority')    
        self.sortRooms.triggered.connect(self.gui.assignRoom)        
        
        self.sortRoomsFromRow = QAction(QIcon('icon/run.png'), 'Assign Rooms Starting Current Row', self)
        self.sortRoomsFromRow.setShortcut('Ctrl+P')
        self.sortRoomsFromRow.setStatusTip('Assign rooms by priority from current row in Jack Group table')    
        self.sortRoomsFromRow.triggered.connect(self.gui.assignRoomFromRow)      
               
                     
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.newFile)
        fileMenu.addAction(self.openFile)
        fileMenu.addAction(self.saveFile)
        processMenu = menubar.addMenu('&Process')
        processMenu.addAction(self.shuffleData)
        processMenu.addAction(self.sortRooms)
        processMenu.addAction(self.sortRoomsFromRow)
                
        self.setCentralWidget(self.gui)
        self.statusBar()
            
        self.show()
        
class OpenPrompt(QWidget):
    def __init__(self, inRmAvTab, inJkGrTab, inOutputTab):
       
        super().__init__()
        self.layout = QGridLayout(self)
        self.fadedColor = QColor(155,155,155)
        self.setGeometry(400,400,600,220)
        self.setWindowTitle("Import Files")
        self.setWindowIcon(QIcon('icon/open.png'))
        self.inRmAvTable = inRmAvTab
        self.inJkGrTable = inJkGrTab
        self.inOutputTable = inOutputTab
        
        #Make Load Labels
        self.rmLabel = QLabel()
        self.grLabel = QLabel()
        self.rmLabel.setText("Room Availability CSV:")
        self.grLabel.setText("Jack Groups CSV:")
        self.rmLabel.setAlignment(Qt.AlignRight)
        self.grLabel.setAlignment(Qt.AlignRight)
        
        #Create text fields
        self.textSize = self.rmLabel.sizeHint().height() * 2
        self.rmDirectory = QLineEdit()
        self.rmDirectory.setReadOnly(ROOM_LIST_HASHEADER)
        self.rmDirectory.setMaximumHeight(self.textSize)
        self.rmDirectory.setText('Please select file')
        self.rmHeaderCheck = QCheckBox("Has header?")
        
        self.grDirectory = QLineEdit()
        self.grDirectory.setReadOnly(GROUP_LIST_HASHEADER)
        self.grDirectory.setMaximumHeight(self.textSize)
        self.grDirectory.setText('Please select file')
        self.grHeaderCheck = QCheckBox("Has header?")
        
        #Create File Selection Buttons
        self.rmButton = QPushButton("Browse", self)
        self.rmButton.clicked.connect(self.getRoomFileDirectory)
        self.grButton = QPushButton("Browse", self)
        self.grButton.clicked.connect(self.getGroupFileDirectory)
        
        self.blankSpace = QSpacerItem(0,30,QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.blankSpace2 = QSpacerItem(0,30,QSizePolicy.Minimum, QSizePolicy.Minimum)
        
        #Create Constants
        self.groupSizeLabel = QLabel ()
        self.groupSizeLabel.setText("Max Group Size:")
        self.groupSizeLabel.setAlignment(Qt.AlignRight)
        self.groupSizeIn = QLineEdit()
        self.groupSizeIn.setInputMask("00")
        self.groupSizeIn.setMaximumHeight(self.textSize)
        self.groupSizeIn.setMaximumWidth(self.textSize)
        self.groupSizeIn.setText(str(MAX_ROOMMATES))
        
        self.prefListSizeLabel = QLabel ()
        self.prefListSizeLabel.setText("Max Room Choices:")
        self.prefListSizeLabel.setAlignment(Qt.AlignRight)
        self.prefListSizeIn = QLineEdit()
        self.prefListSizeIn.setInputMask("00")
        self.prefListSizeIn.setMaximumHeight(self.textSize)
        self.prefListSizeIn.setMaximumWidth(self.textSize)
        self.prefListSizeIn.setText(str(MAX_PREF_LIST_LENGTH))
                
        self.maxPointsLabel = QLabel ()
        self.maxPointsLabel.setText("Max Points:")
        self.maxPointsLabel.setAlignment(Qt.AlignRight)
        self.maxPtsIn = QLineEdit()
        self.maxPtsIn.setInputMask("00")
        self.maxPtsIn.setMaximumHeight(self.textSize)
        self.maxPtsIn.setMaximumWidth(self.textSize)
        self.maxPtsIn.setText(str(MAX_POINTS))
                      
        self.finImportButton = QPushButton("Import", self)
        self.finImportButton.clicked.connect(self.checkData)
        
        #Create Layout
        self.layout.addWidget(self.rmLabel,0,0)
        self.layout.addWidget(self.rmDirectory,0,1,1,3)
        self.layout.addWidget(self.rmButton,0,4)
        self.layout.addWidget(self.rmHeaderCheck,0,5)
        self.layout.addWidget(self.grLabel,1,0)
        self.layout.addWidget(self.grDirectory,1,1,1,3)
        self.layout.addWidget(self.grButton,1,4)
        self.layout.addWidget(self.grHeaderCheck,1,5)
        self.layout.addItem(self.blankSpace,2,0)
        self.layout.addWidget(self.groupSizeLabel,3,0)
        self.layout.addWidget(self.groupSizeIn,3,1)        
        self.layout.addWidget(self.prefListSizeLabel,3,3)
        self.layout.addWidget(self.prefListSizeIn,3,4)               
        self.layout.addWidget(self.maxPointsLabel,4,0)
        self.layout.addWidget(self.maxPtsIn,4,1)
        self.layout.addItem(self.blankSpace2,5,0)
        self.layout.addWidget(self.finImportButton,6,2,1,2)
        
    def showOkMessage(self, inType, inIcon, inErrorText, inTitle):
        self.errorMessage = QMessageBox()
        if inType == "critical":
            self.errorMessage.setIcon(QMessageBox.Critical)
        self.errorMessage.setWindowIcon(QIcon("icon\\" + inIcon + ".png"))
        self.errorMessage.setText(inErrorText)
        self.errorMessage.setWindowTitle(inTitle)
        self.errorMessage.setStandardButtons(QMessageBox.Ok)
        self.errorMessage.setEscapeButton(QMessageBox.Close)
        self.errorMessage.show()  
        
    """***********************
    "
    " checkData
    "
    "********
    "
    " Checks the input from the open prompt fields to make sure all integers are set
    " as integers and fall within reasonable ranges. Displays error messages and 
    " doesn't load files and allows users to change data if necessary before populating
    " the tables on the appropriate tbas.
    "
    ***********************"""
    def checkData(self):
        global ROOM_LIST_HASHEADER, GROUP_LIST_HASHEADER, MAX_POINTS
        global MAX_PREF_LIST_LENGTH, MAX_ROOMMATES
        #verify data are at least GENERALLY correct
        #    NOTE: No file data verification at this point
        if int(self.groupSizeIn.text()) <= 0:
            self.showOkMessage("critical", "error", "Enter maximum jack group size larger than 0", "Value Error")
        elif int(self.prefListSizeIn.text()) <= 0:
            self.showOkMessage("critical", "error", "Enter maximum room preference list length longer than 0", "Value Error")
        elif int(self.maxPtsIn.text()) <= 0:
            self.showOkMessage("critical", "error", "Enter max points as positive integer (0 if max doesn't matter)", "Value Error")
        elif self.rmDirectory.text() == "Please select file" or self.rmDirectory.text() == "Please select valid file":
            self.showOkMessage("critical", "error", "Select CSV file for room availability list", "Value Error")
        elif self.grDirectory.text() == "Please select file" or self.grDirectory.text() == "Please select valid file":
            self.showOkMessage("critical", "error", "Select CSV file for jack groups list", "Value Error")
        #if no obvious errors with input, continue
        else:
            #Set the Constant
            MAX_ROOMMATES = int(self.groupSizeIn.text())
            MAX_PREF_LIST_LENGTH = int(self.prefListSizeIn.text())
            MAX_POINTS = int(self.maxPtsIn.text())
            FILE_LOAD_LIST = [self.rmDirectory.text(), self.grDirectory.text()]
            GROUP_LIST_HASHEADER = (self.grHeaderCheck.checkState() == 2)
            ROOM_LIST_HASHEADER = (self.rmHeaderCheck.checkState() == 2)
            
            #Populate the tables on the Room Availability and Jack Group tab
            createRoomTableFromCSV(self.inRmAvTable, FILE_LOAD_LIST[0])
            createJackGroupTableFromCSV(self.inJkGrTable, FILE_LOAD_LIST[1])
            createBlankOutputTable(self.inOutputTable,self.inJkGrTable.rowCount())
            
            #Hide the open prompt
            self.hide()
            
    def getRoomFileDirectory(self):
        tempDirectory = QFileDialog.getOpenFileName(self, 'Open Room Availability List', '', 'CSV (*.csv)')
        if tempDirectory[0]:
            self.rmDirectory.setText(tempDirectory[0])
        elif self.rmDirectory.text() == "Please select file":
            self.rmDirectory.setText("Please select valid file")
        
    def getGroupFileDirectory(self):
        tempDirectory = QFileDialog.getOpenFileName(self, 'Open Jack Groups List', '', 'CSV (*.csv)')
        if tempDirectory[0]:
            self.grDirectory.setText(tempDirectory[0])
        elif self.grDirectory.text() == "Please select file":
            self.grDirectory.setText("Please select valid file")
        
class TabsWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
                
        self.tabs = QTabWidget()
        self.tabs.resize(300,200)
        
        self.errorColor = QColor(245,142,144)
        
        #Set up Room Tab
        self.roomTab = QWidget()
        self.tabs.addTab(self.roomTab, "Room Availability")   
        self.roomTable = QTableWidget()
        self.roomTab.layout = QVBoxLayout(self)
        self.roomTab.layout.addWidget(self.roomTable)
        self.roomTab.setLayout(self.roomTab.layout)
         
        self.groupTab = QWidget()
        self.tabs.addTab(self.groupTab, "Jack Groups")
        self.groupTable = QTableWidget()
        self.groupHeader = []  
        self.groupTab.layout = QVBoxLayout(self)
        self.groupTab.layout.addWidget(self.groupTable)
        self.groupTab.setLayout(self.groupTab.layout)
        
        self.outputTab = QWidget()    
        self.tabs.addTab(self.outputTab, "Sorted Rooms")
        self.outputTable = QTableWidget()
        self.outputHeader = []  
        self.outputTab.layout = QVBoxLayout(self)
        self.outputTab.layout.addWidget(self.outputTable)
        self.outputTab.setLayout(self.outputTab.layout)
        
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)     
        
        self.openMenu = OpenPrompt(self.roomTable, self.groupTable, self.outputTable)
        
    def showOpenMenu(self):
        self.openMenu.show()           
    
    def sortByPoints(self):
        if self.groupTable.columnCount() > 0 and self.groupTable.rowCount() > 0:
            tempList = []
            outList = []
            curPoints = 0
            loopCheck = True
            curIndex = 0
            sortList = getDataFromTable(self.groupTable)
            sortList.sort(key=lambda x: x[0], reverse = True)
            curPoints = sortList[0][0]
            length = len(sortList)
            while curIndex < length and loopCheck:
                while sortList[curIndex][0] == curPoints and loopCheck:
                    tempList.append(sortList[curIndex])
                    if curIndex + 1 < length:
                        curIndex += 1
                    else:
                        loopCheck = False
                random.shuffle(tempList)
                for obj in tempList:
                    outList.append(obj)
                tempList = []
                if curIndex < length:
                    curPoints = sortList[curIndex][0]
                else:
                    loopCheck = False
            for x_val in range(len(outList[0])):
                for y_val in range(len(outList)):
                    self.groupTable.setItem(y_val, x_val, QTableWidgetItem(outList[y_val][x_val]))
            createJackGroupsFromTable(self.groupTable)
            
    def getFirstUnassignedGroup(self, startRow = 0):
        loopIndex = startRow
        loopBool = True
        while loopBool and loopIndex < len(jackList):
            if jackList[loopIndex].assignedRoom == 0:
                loopBool = False
            else:
                loopIndex += 1
        if loopIndex < len(jackList):
            return(loopIndex)
        else:
            return(-1)


    def assignRoom(self):
        global jackList, roomList
        
        createJackGroupsFromTable(self.groupTable)
        createRoomsFromTable(self.roomTable)
        
        roomAvaiList = makeRoomDictFromObjList(roomList)
        groupIndex = 0
        numGroups = len(jackList)
        roomIndex = 0
        sortedYet = False
        
        while groupIndex < numGroups:
            roomIndex = 0
            sortedYet = False
            currentPrefList = jackList[groupIndex].prefList
            numPreferences = len(currentPrefList)
            while not sortedYet and roomIndex < numPreferences:
                #if the current room is the one they're in, end loop
                if currentPrefList[roomIndex] == jackList[groupIndex].assignedRoom:
                    roomAvaiList[currentPrefList[roomIndex]].unassigned = False
                    sortedYet = True
                #if the room isn't available
                elif currentPrefList[roomIndex] not in roomAvaiList:
                    roomIndex += 1
                #if the room is a new one for them that isn't taken    
                elif roomAvaiList[currentPrefList[roomIndex]].unassigned:
                    sortedYet = True
                    #open up old room
                    if jackList[groupIndex].assignedRoom != 0:
                        roomAvaiList[jackList[groupIndex].assignedRoom].unassigned = True
                    #assign them to the new room
                    jackList[groupIndex].assignedRoom = currentPrefList[roomIndex]
                    #mark the new room as taken
                    roomAvaiList[currentPrefList[roomIndex]].unassigned = False
                    #reset the loop
                    roomIndex = 0
                    groupIndex = 0
                #if isn't their current room, and isn't available, move on to next room
                else:
                    #move on to next room
                    roomIndex += 1
            groupIndex += 1

        loopIndex = self.getFirstUnassignedGroup()
        if loopIndex < len(jackList) and loopIndex != -1:
            #Clear out all the assigned rooms after the first unassigned room
            for group_number in range(loopIndex, len(jackList)):
                if int(jackList[group_number].assignedRoom) != 0:
                    roomAvaiList[jackList[group_number].assignedRoom].unassigned = True
                    jackList[group_number].assignedRoom = 0
            
            tempNameList = ""
            tempNameList += jackList[loopIndex].nameList[0]
            for nameIndex in range(1,len(jackList[loopIndex].nameList)):
                if jackList[loopIndex].nameList[nameIndex] != "":
                    tempNameList += ", " + jackList[loopIndex].nameList[nameIndex]
            tempOpenRooms = getAvailableRoomsFromRow(roomList, jackList, loopIndex)
            
            #Create a list of rooms
            tempRoomList = ""
            tempRoomList += str(tempOpenRooms[0])
            count = 0
            for roomIndex in range(1,len(tempOpenRooms)):
                count += 1
                if count == 11:
                    tempRoomList += "\n" + str(tempOpenRooms[roomIndex])
                    count = 1
                else:
                    tempRoomList += ", " + str(tempOpenRooms[roomIndex])
                
            for y_val in range(len(jackList)):
                self.groupTable.setItem(y_val, MAX_ROOMMATES+MAX_PREF_LIST_LENGTH+2, QTableWidgetItem(str(jackList[y_val].assignedRoom)))
                
            self.errorMessage = QMessageBox()
            self.errorMessage.setWindowIcon(QIcon("icon\contact.png"))
            self.errorMessage.setIcon(QMessageBox.Information)
            self.errorMessage.setText("Group: " + tempNameList + "\n\nAvailable Rooms:\n" + tempRoomList
                                      + "\n\nTable Row: " + str(loopIndex+1))
            self.errorMessage.setWindowTitle("Contact Following")
            self.errorMessage.setStandardButtons(QMessageBox.Ok)
            self.errorMessage.setEscapeButton(QMessageBox.Close)
            self.errorMessage.show()
                
        elif loopIndex == -1:
            roomOrderList = sorted(jackList, key = roomSortKey)
            for y_val in range(len(jackList)):
                self.groupTable.setItem(y_val, MAX_ROOMMATES+MAX_PREF_LIST_LENGTH+2, QTableWidgetItem(str(jackList[y_val].assignedRoom)))
                self.outputTable.setItem(y_val,0,QTableWidgetItem(str(roomOrderList[y_val].assignedRoom)))
                for x_val in range(1,len(roomOrderList[y_val].nameList)+1):
                    self.outputTable.setItem(y_val,x_val,QTableWidgetItem(str(roomOrderList[y_val].nameList[x_val-1])))
    
    def assignRoomFromRow(self):
        global jackList, roomList
        
        createJackGroupsFromTable(self.groupTable)
        createRoomsFromTable(self.roomTable)
        roomAvaiList = makeRoomDictFromObjList(roomList)
        abort = False
        
        #from top of table to current row
        for group_number in range(0, self.groupTable.currentRow()):
            #if a room is assigned
            if int(jackList[group_number].assignedRoom) != 0:
                #AND the room has not been assigned to someone else
                if roomAvaiList[jackList[group_number].assignedRoom].unassigned:
                    #set the room as not available
                    roomAvaiList[jackList[group_number].assignedRoom].unassigned = False
                #if a room has been assigned twice, 
                elif not roomAvaiList[jackList[group_number].assignedRoom].unassigned:
                    self.errorMessage = QMessageBox()
                    self.errorMessage.setWindowIcon(QIcon("icon\error.png"))
                    self.errorMessage.setIcon(QMessageBox.Critical)
                    self.errorMessage.setText("Room " + str(jackList[group_number].assignedRoom) + " has been assigned multiple times.")
                    self.errorMessage.setWindowTitle("Room Assignment Error")
                    self.errorMessage.setStandardButtons(QMessageBox.Ok)
                    self.errorMessage.setEscapeButton(QMessageBox.Close)
                    self.errorMessage.show()
                    abort = True
        for group_number in range(self.groupTable.currentRow(), len(jackList)):
            if int(jackList[group_number].assignedRoom) != 0:
                roomAvaiList[jackList[group_number].assignedRoom].unassigned = True
                jackList[group_number].assignedRoom = 0
                
        if not abort:
            groupIndex = self.groupTable.currentRow()
            numGroups = len(jackList)
            roomIndex = 0
            sortedYet = False
            
            while groupIndex < numGroups:
                roomIndex = 0
                sortedYet = False
                currentPrefList = jackList[groupIndex].prefList
                numPreferences = len(currentPrefList)
                while not sortedYet and roomIndex < numPreferences:
                    #if the current room is the one they're in, end loop
                    if currentPrefList[roomIndex] == jackList[groupIndex].assignedRoom:
                        roomAvaiList[currentPrefList[roomIndex]].unassigned = False
                        sortedYet = True
                    #if the room isn't available
                    elif currentPrefList[roomIndex] not in roomAvaiList:
                        roomIndex += 1
                    #if the room is a new one for them that isn't taken    
                    elif roomAvaiList[currentPrefList[roomIndex]].unassigned:
                        sortedYet = True
                        #open up old room
                        if jackList[groupIndex].assignedRoom != 0:
                            roomAvaiList[jackList[groupIndex].assignedRoom].unassigned = True
                        #assign them to the new room
                        jackList[groupIndex].assignedRoom = currentPrefList[roomIndex]
                        #mark the new room as taken
                        roomAvaiList[currentPrefList[roomIndex]].unassigned = False
                        #reset the loop
                        roomIndex = 0
                        groupIndex = 0
                    #if isn't their current room, and isn't available, move on to next room
                    else:
                        #move on to next room
                        roomIndex += 1
                groupIndex += 1
    
            loopIndex = self.getFirstUnassignedGroup()
            if loopIndex < len(jackList) and loopIndex != -1:
                #Clear out all the assigned rooms after the first unassigned room
                for group_number in range(loopIndex, len(jackList)):
                    if int(jackList[group_number].assignedRoom) != 0:
                        roomAvaiList[jackList[group_number].assignedRoom].unassigned = True
                        jackList[group_number].assignedRoom = 0
                
                tempNameList = ""
                tempNameList += jackList[loopIndex].nameList[0]
                for nameIndex in range(1,len(jackList[loopIndex].nameList)):
                    if jackList[loopIndex].nameList[nameIndex] != "":
                        tempNameList += ", " + jackList[loopIndex].nameList[nameIndex]
                tempOpenRooms = getAvailableRoomsFromRow(roomList, jackList, loopIndex)
                
                #Create a list of rooms
                tempRoomList = ""
                tempRoomList += str(tempOpenRooms[0])
                count = 0
                for roomIndex in range(1,len(tempOpenRooms)):
                    count += 1
                    if count == 11:
                        tempRoomList += "\n" + str(tempOpenRooms[roomIndex])
                        count = 1
                    else:
                        tempRoomList += ", " + str(tempOpenRooms[roomIndex])
                
                for y_val in range(len(jackList)):
                    self.groupTable.setItem(y_val, MAX_ROOMMATES+MAX_PREF_LIST_LENGTH+2, QTableWidgetItem(str(jackList[y_val].assignedRoom)))
                    
                self.errorMessage = QMessageBox()
                self.errorMessage.setWindowIcon(QIcon("icon\contact.png"))
                self.errorMessage.setIcon(QMessageBox.Information)
                self.errorMessage.setText("Group: " + tempNameList + "\n\nAvailable Rooms:\n" + tempRoomList
                                          + "\n\nTable Row: " + str(loopIndex+1))
                self.errorMessage.setWindowTitle("Contact Following")
                self.errorMessage.setStandardButtons(QMessageBox.Ok)
                self.errorMessage.setEscapeButton(QMessageBox.Close)
                self.errorMessage.show()
                    
            elif loopIndex == -1:
                roomOrderList = sorted(jackList, key = roomSortKey)
                for y_val in range(len(jackList)):
                    print(y_val)
                    self.groupTable.setItem(y_val, MAX_ROOMMATES+MAX_PREF_LIST_LENGTH+2, QTableWidgetItem(str(jackList[y_val].assignedRoom)))
                    self.outputTable.setItem(y_val,0,QTableWidgetItem(str(roomOrderList[y_val].assignedRoom)))
                    for x_val in range(1,len(roomOrderList[y_val].nameList)+1):
                        self.outputTable.setItem(y_val,x_val,QTableWidgetItem(str(roomOrderList[y_val].nameList[x_val-1])))
        
if __name__ == '__main__':
    import sys
    
    app = QApplication(sys.argv)
    ex = App()    
    sys.exit(app.exec_())