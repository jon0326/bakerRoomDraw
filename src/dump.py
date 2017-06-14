"""********
* TabsWidget
***********
*
* Maintains the tables and tabs for the GUI
*
********"""       
class TabsWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
                
        self.tabs = QTabWidget()
        self.tabs.resize(300,200)
        
        self.errorColor = QColor(245,142,144)
        self.roomErrorColor = QColor(255,223,186)
        self.normalColor = QColor(255,255,255)
        
        #Set up Room Tab
        self.roomTab = QWidget()
        self.tabs.addTab(self.roomTab, "Room Availability")   
        self.roomTable = QTableWidget()
        self.roomTab.layout = QVBoxLayout(self)
        self.roomTab.layout.addWidget(self.roomTable)
        self.roomTab.setLayout(self.roomTab.layout)
        self.roomTable.verticalHeader().setVisible(False)
        self.roomTable.cellChanged.connect(self.cellCheck)
        
        self.groupTab = QWidget()
        self.tabs.addTab(self.groupTab, "Jack Groups")
        self.groupTable = QTableWidget()
        self.groupHeader = []  
        self.groupTab.layout = QVBoxLayout(self)
        self.groupTab.layout.addWidget(self.groupTable)
        self.groupTab.setLayout(self.groupTab.layout)
        self.groupTable.cellChanged.connect(self.cellCheck)
        
        self.opRmTab = QWidget()
        self.tabs.addTab(self.opRmTab, "Open Rooms")
        self.openRoomTable = QTableWidget()
        self.opRmTab.layout = QVBoxLayout(self)
        self.opRmTab.layout.addWidget(self.openRoomTable)
        self.opRmTab.setLayout(self.opRmTab.layout)
        
        self.outputTab = QWidget()    
        self.tabs.addTab(self.outputTab, "Sorted Rooms")
        self.outputTable = QTableWidget()
        self.outputTable.verticalHeader().setVisible(False)
        self.outputHeader = []  
        self.outputTab.layout = QVBoxLayout(self)
        self.outputTab.layout.addWidget(self.outputTable)
        self.outputTab.setLayout(self.outputTab.layout)
        
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)   
        self.lastClick = QTableWidgetItem()
        self.lastClick.setText('0') 
        self.thisClick = QTableWidgetItem()
        self.lastClick.setText('0')
        
        self.openMenu = OpenPrompt(self.roomTable, self.groupTable, self.outputTable)
        self.savePrompt = SavePrompt(self.roomTable, self.groupTable, self.openRoomTable, self.outputTable)

    
    def cellCheck(self):
        validateData(self.roomTable, self.groupTable)
       
    def showOpenMenu(self):
        self.openMenu.show() 
        
    def showSavePrompt(self):
        self.savePrompt = SavePrompt(self.roomTable, self.groupTable, self.openRoomTable, self.outputTable)
        self.savePrompt.setSaveAccess()
        self.savePrompt.show() 
        
    def sortByPoints(self):
        continueCheck = validateData(self.roomTable, self.groupTable)
        if continueCheck[0] == False:
            self.errorMessage = QMessageBox()
            self.errorMessage.setWindowIcon(QIcon("icon\error.png"))
            self.errorMessage.setIcon(QMessageBox.Critical)
            self.errorMessage.setText(continueCheck[1])
            self.errorMessage.setWindowTitle("Room Assignment Error")
            self.errorMessage.setStandardButtons(QMessageBox.Ok)
            self.errorMessage.setEscapeButton(QMessageBox.Close)
            self.errorMessage.show()
        elif continueCheck[0] == True:
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
                self.groupTable.blockSignals(True)
                for x_val in range(len(outList[0])):
                    for y_val in range(len(outList)):
                        
                        self.groupTable.setItem(y_val, x_val, QTableWidgetItem(outList[y_val][x_val]))
                self.groupTable.blockSignals(False)
                createJackGroupsFromTable(self.groupTable)
    
    """********
    * getFirstUnassignedGroup 
    ***********
    *
    * From row (beginning of table if not defined), find the first jack group that is not assigned a room.
    *
    * If all have been assigned, return -1
    *
    ********"""
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

    """********
    * assignRoom 
    ***********
    * 
    * Given ordered list of jack groups with preferences, assign each group to their first possible preference
    * not assigned to someone with more points.
    *
    * If gets to a group with no rooms on their preference list unassigned, will stop and show jack group
    * names and their row within the table. Also populates Open Rooms table with list of open rooms,
    * according to sex assigned to room and sorted by room size.
    *
    * When complete, will show message that is done and will populate the Assigned Rooms tab with an
    * ordered list of all assignments, with room number and names of people assigned to that room.
    *
    ********"""
    def assignRoom(self):
        global jackList, roomList, roomObjectDict
        
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
                if currentPrefList[roomIndex] == jackList[groupIndex].assignedRoom and roomAvaiList[currentPrefList[roomIndex]].type == jackList[groupIndex].groupType and int(jackList[groupIndex].groupSize) <= int(roomAvaiList[currentPrefList[roomIndex]].size):
                    roomAvaiList[currentPrefList[roomIndex]].unassigned = False
                    sortedYet = True
                #if the room isn't available
                elif currentPrefList[roomIndex] not in roomAvaiList:
                    roomIndex += 1
                #if the room is a new one for them that isn't taken    
                elif roomAvaiList[currentPrefList[roomIndex]].unassigned and roomAvaiList[currentPrefList[roomIndex]].type == jackList[groupIndex].groupType and int(jackList[groupIndex].groupSize) <= int(roomAvaiList[currentPrefList[roomIndex]].size):
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
        roomObjectDict = roomAvaiList
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

            self.groupTable.blockSignals(True)
            for y_val in range(len(jackList)):
                self.groupTable.setItem(y_val, MAX_ROOMMATES+MAX_PREF_LIST_LENGTH+2, QTableWidgetItem(str(jackList[y_val].assignedRoom)))
            self.groupTable.blockSignals(False)    
            listOpenRooms = getRemainingOpenRooms()
            openRoomTableInput = generateOpRmTbInFromList(listOpenRooms)
            self.openRoomTable.setShowGrid(False)
            self.openRoomTable.setColumnCount(11)
            self.openRoomTable.setRowCount(len(openRoomTableInput))
            self.openRoomTable.horizontalHeader().setVisible(False)
            self.openRoomTable.verticalHeader().setVisible(False)
            for row_count in range(0,len(openRoomTableInput)):
                for column_count in range(0,len(openRoomTableInput[row_count])):
                    self.openRoomTable.setItem(row_count,column_count,QTableWidgetItem(str(openRoomTableInput[row_count][column_count])))
            self.openRoomTable.setVisible(False)
            self.openRoomTable.resizeColumnsToContents()
            self.openRoomTable.setVisible(True)
            ####GENERATE THE OUTPUT TABLE
                
            self.errorMessage = QMessageBox()
            self.errorMessage.setWindowIcon(QIcon("icon\contact.png"))
            self.errorMessage.setIcon(QMessageBox.Information)
            self.errorMessage.setText("<p><b>Group:</b><br/> " + tempNameList + "</p><p><b>Table Row:</b><br/>" + str(loopIndex+1) + "</p>")
            self.errorMessage.setWindowTitle("Contact Following")
            self.errorMessage.setStandardButtons(QMessageBox.Ok)
            self.errorMessage.setEscapeButton(QMessageBox.Close)
            self.errorMessage.show()
        
        elif loopIndex == -1:
            self.groupTable.blockSignals(True)
            roomOrderList = sorted(jackList, key = roomSortKey)
            for y_val in range(len(jackList)):
                self.groupTable.setItem(y_val, MAX_ROOMMATES+MAX_PREF_LIST_LENGTH+2, QTableWidgetItem(str(jackList[y_val].assignedRoom)))
                self.outputTable.setItem(y_val,0,QTableWidgetItem(str(roomOrderList[y_val].assignedRoom)))
                for x_val in range(1,len(roomOrderList[y_val].nameList)+1):
                    self.outputTable.setItem(y_val,x_val,QTableWidgetItem(str(roomOrderList[y_val].nameList[x_val-1])))
            self.groupTable.blockSignals(False)
            
            listOpenRooms = getRemainingOpenRooms()
            openRoomTableInput = generateOpRmTbInFromList(listOpenRooms)
            self.openRoomTable.setShowGrid(False)
            self.openRoomTable.setColumnCount(11)
            self.openRoomTable.setRowCount(len(openRoomTableInput))
            self.openRoomTable.horizontalHeader().setVisible(False)
            self.openRoomTable.verticalHeader().setVisible(False)
            for row_count in range(0,len(openRoomTableInput)):
                for column_count in range(0,len(openRoomTableInput[row_count])):
                    self.openRoomTable.setItem(row_count,column_count,QTableWidgetItem(str(openRoomTableInput[row_count][column_count])))
            self.openRoomTable.setVisible(False)
            self.openRoomTable.resizeColumnsToContents()
            self.openRoomTable.setVisible(True)
            
            self.errorMessage = QMessageBox()
            self.errorMessage.setWindowIcon(QIcon("icon\new.png"))
            self.errorMessage.setIcon(QMessageBox.Information)
            self.errorMessage.setText("Every group has room assigned")
            self.errorMessage.setWindowTitle("Assignment Complete")
            self.errorMessage.setStandardButtons(QMessageBox.Ok)
            self.errorMessage.setEscapeButton(QMessageBox.Close)
            self.errorMessage.show()
    
    """********
    * assignRoomFromRow 
    ***********
    *
    * Same as assignRoom, except goes from currently selected row
    *
    ********"""
    def assignRoomFromRow(self):
        global jackList, roomList, roomObjectDict
        
        
        if self.groupTable.currentRow() > -1:
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
                        if currentPrefList[roomIndex] == jackList[groupIndex].assignedRoom and roomAvaiList[currentPrefList[roomIndex]].type == jackList[groupIndex].groupType and int(jackList[groupIndex].groupSize) <= int(roomAvaiList[currentPrefList[roomIndex]].size):
                            roomAvaiList[currentPrefList[roomIndex]].unassigned = False
                            sortedYet = True
                        #if the room isn't available
                        elif currentPrefList[roomIndex] not in roomAvaiList:
                            roomIndex += 1
                        #if the room is a new one for them that isn't taken    
                        elif roomAvaiList[currentPrefList[roomIndex]].unassigned and roomAvaiList[currentPrefList[roomIndex]].type == jackList[groupIndex].groupType and int(jackList[groupIndex].groupSize) <= int(roomAvaiList[currentPrefList[roomIndex]].size):
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
                roomObjectDict = roomAvaiList
        
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
                    self.groupTable.blockSignals(True)
                    for y_val in range(len(jackList)):
                        self.groupTable.setItem(y_val, MAX_ROOMMATES+MAX_PREF_LIST_LENGTH+2, QTableWidgetItem(str(jackList[y_val].assignedRoom)))
                    self.groupTable.blockSignals(False)        
                    listOpenRooms = getRemainingOpenRooms()
                    openRoomTableInput = generateOpRmTbInFromList(listOpenRooms)
                    self.openRoomTable.setShowGrid(False)
                    self.openRoomTable.setColumnCount(11)
                    self.openRoomTable.setRowCount(len(openRoomTableInput))
                    self.openRoomTable.horizontalHeader().setVisible(False)
                    self.openRoomTable.verticalHeader().setVisible(False)
                    for row_count in range(0,len(openRoomTableInput)):
                        for column_count in range(0,len(openRoomTableInput[row_count])):
                            self.openRoomTable.setItem(row_count,column_count,QTableWidgetItem(str(openRoomTableInput[row_count][column_count])))
                    self.openRoomTable.setVisible(False)
                    self.openRoomTable.resizeColumnsToContents()
                    self.openRoomTable.setVisible(True)
                    
                    self.errorMessage = QMessageBox()
                    self.errorMessage.setWindowIcon(QIcon("icon\contact.png"))
                    self.errorMessage.setIcon(QMessageBox.Information)
                    self.errorMessage.setText("<p><b>Group:</b><br/> " + tempNameList + "</p><p><b>Table Row:</b><br/>" + str(loopIndex+1) + "</p>")
                    self.errorMessage.setWindowTitle("Contact Following")
                    self.errorMessage.setStandardButtons(QMessageBox.Ok)
                    self.errorMessage.setEscapeButton(QMessageBox.Close)
                    self.errorMessage.show()
                        
                elif loopIndex == -1:
                    self.groupTable.blockSignals(True)
                    roomOrderList = sorted(jackList, key = roomSortKey)
                    for y_val in range(len(jackList)):
                        self.groupTable.setItem(y_val, MAX_ROOMMATES+MAX_PREF_LIST_LENGTH+2, QTableWidgetItem(str(jackList[y_val].assignedRoom)))
                        self.outputTable.setItem(y_val,0,QTableWidgetItem(str(roomOrderList[y_val].assignedRoom)))
                        for x_val in range(1,len(roomOrderList[y_val].nameList)+1):
                            self.outputTable.setItem(y_val,x_val,QTableWidgetItem(str(roomOrderList[y_val].nameList[x_val-1])))
                    self.groupTable.blockSignals(False)
                    
                    listOpenRooms = getRemainingOpenRooms()
                    openRoomTableInput = generateOpRmTbInFromList(listOpenRooms)
                    self.openRoomTable.setShowGrid(False)
                    self.openRoomTable.setColumnCount(11)
                    self.openRoomTable.setRowCount(len(openRoomTableInput))
                    self.openRoomTable.horizontalHeader().setVisible(False)
                    self.openRoomTable.verticalHeader().setVisible(False)
                    for row_count in range(0,len(openRoomTableInput)):
                        for column_count in range(0,len(openRoomTableInput[row_count])):
                            self.openRoomTable.setItem(row_count,column_count,QTableWidgetItem(str(openRoomTableInput[row_count][column_count])))
                    self.openRoomTable.setVisible(False)
                    self.openRoomTable.resizeColumnsToContents()
                    self.openRoomTable.setVisible(True)
                        
                    self.errorMessage = QMessageBox()
                    self.errorMessage.setWindowIcon(QIcon("icon\new.png"))
                    self.errorMessage.setIcon(QMessageBox.Information)
                    self.errorMessage.setText("Every group has room assigned")
                    self.errorMessage.setWindowTitle("Assignment Complete")
                    self.errorMessage.setStandardButtons(QMessageBox.Ok)
                    self.errorMessage.setEscapeButton(QMessageBox.Close)
                    self.errorMessage.show()