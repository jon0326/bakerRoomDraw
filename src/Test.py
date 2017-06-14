"""
To Do List:
+ Some error where the rooms are not being unassigned before a sort. When running a sort (full sort):
    reset ALL rooms to 0
    + Check to see if sorting from row will work
    + Prompt when someone assigns room to either assign room in availability list (blocking others from getting) or undo
+ Shuffle check - 
    + Check if ordered before shuffling - show Yes / No / Cancel prompt
    + Check if ordered before sorting full list or from current row - show Yes / No / Cancel prompt
    
+ Make help menu    
+ Make "New" menu
"""

global MAX_ROOMMATES, MAX_PREF_LIST_LENGTH, MAX_POINTS, FILE_LOAD_LIST
global GROUP_LIST_HASHEADER, ROOM_LIST_HASHEADER, jackList, roomDict

#Constants for CSV layout
MAX_ROOMMATES = 8
MAX_PREF_LIST_LENGTH = 5
MAX_POINTS = 6.00
GROUP_LIST_HASHEADER = True
ROOM_LIST_HASHEADER = True

#Convenience constants
FILE_LOAD_LIST = []
jackList = []
roomList = []
roomObjectDict = {}

#Room CSV Column Values
ROOM_NUMBER_COL = 0
ROOM_TYPE_COL = 1
ROOM_SIZE_COL = 2
ROOM_AVAI_COL = 3

#Jack Group CSV Column Values
GROUP_POINTS_COL = 0
GROUP_TYPE_COL = 1

import csv
import random

from PyQt5.QtWidgets import (QApplication, QDialog, QFileDialog, QMainWindow, QMessageBox, QTableWidgetItem)
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi

"""********
* SavePrompt
***********
*
* Pass in a room availability table, jack group table, open rooms table, and assigned
* room table. Imports from the savePrompt.ui file to create the widgets within the
* GUI.
* 
* Allows users to choose which of the four tables to save as CSVs using a save file prompt.
* Will not allow save if a table isn't set to be ignored but doesn't have a path
* defined, or if multiple files set to the same destination. 
*
********"""
class SavePrompt(QDialog):
    def __init__(self, inRmAvTab, inJkGrTab, inOpRmTab, inAsRmTab):
        super(SavePrompt, self).__init__()
        self.saveWidget = loadUi('savePrompt.ui',self) #Import XML file (extension .ui)
        self.saveWidget.setWindowIcon(QIcon('icon/save.png'))
        
        self.inRmAvTable = inRmAvTab #Room Availability Table
        self.inJkGrTable = inJkGrTab #Jack Group Table
        self.inOpRmTable = inOpRmTab #Open Rooms Table
        self.inAsRmTable = inAsRmTab #Assigned Room Table
        
        """********
        * GUI Object Guide
        ***********
        * rmAv... = Room Availability
        * jkGr... = Jack Groups
        * opRm... = Open Rooms
        * asRm... = Assigned Rooms
        *
        * ...Check = Ignore? Y/N Checkbox
        * ...Label = Text label
        * ...Text = LineEdit (single line text field; set to not be editable)
        * ...Browse = Browse button
        *
        * saveBttn = Save Button object
        *
        ********"""
        
        # Connect four check boxes to appropriate functions to toggle associated elements in save prompt
        self.saveWidget.rmAvCheck.stateChanged.connect(self.rmAvCheckFunc) 
        self.saveWidget.jkGrCheck.stateChanged.connect(self.jkGrCheckFunc)
        self.saveWidget.opRmCheck.stateChanged.connect(self.opRmCheckFunc)
        self.saveWidget.asRmCheck.stateChanged.connect(self.asRmCheckFunc)
        
        # Connect four browse buttons to the functions to set their line edits to the save path
        self.saveWidget.rmAvBrowse.clicked.connect(self.rmAvBrowseFunc)
        self.saveWidget.jkGrBrowse.clicked.connect(self.jkGrBrowseFunc)
        self.saveWidget.opRmBrowse.clicked.connect(self.opRmBrowseFunc)
        self.saveWidget.asRmBrowse.clicked.connect(self.asRmBrowseFunc)
        
        # Connect save button to function to check input and try to save file
        self.saveWidget.saveBttn.clicked.connect(self.saveFunc)
    
    """********
    * allUnique
    ***********
    *
    * Pass in a list. Return True if no duplicates; False if any duplicates
    *
    ********"""
    def allUnique(self, inStringList):
        seen = set()
        return not any(i in seen or seen.add(i) for i in inStringList)
    
    """********
    * saveFunc
    ***********
    *
    * Checks to ensure that any tables with enabled and unselected checkboxes have valid input. 
    * Compiles list of error messages for anything set up incorrectly.
    *
    ********"""
    def saveFunc(self):
        continueSave = True #set to false if there's any error. When false, will stop Save
        errorMessage = ""  #Stores the full string of error messages  
        self.saveList = [] #List of all the enabled, included, non-blank save paths + intended file names
        
        #Check Room Availabilty is enabled and set to be included
        if self.saveWidget.rmAvCheck.isEnabled() and self.saveWidget.rmAvCheck.checkState() == 0:
            #Throw error if blank
            if self.saveWidget.rmAvText.text() == "":
                #Store error to display
                continueSave = False
                errorMessage += "<p>Must choose to ignore <i>Room Availability Save</i> or select file to save as</p>"
            else:
                #if okay, include in duplicate check
                self.saveList.append(self.saveWidget.rmAvText.text())
                
        #Check Jack Group is enabled and set to be included in save
        if self.saveWidget.jkGrCheck.isEnabled() and self.saveWidget.jkGrCheck.checkState() == 0:
            #Throw error if blank
            if self.saveWidget.jkGrText.text() == "":
                #store error to display
                continueSave = False
                errorMessage += "<p>Must choose to ignore <i>Jack Group Save</i> or select file to save as</p>"
            else:
                #if fine, include in list to check for duplicates
                self.saveList.append(self.saveWidget.jkGrText.text())
                
        #Check Open Rooms is enabled and set to be included in save
        if self.saveWidget.opRmCheck.isEnabled() and self.saveWidget.opRmCheck.checkState() == 0:
            #Throw error if blank
            if self.saveWidget.opRmText.text() == "":
                    #store error to display
                    continueSave = False
                    errorMessage += "<p>Must choose to ignore <i>Open Rooms Save</i> or select file to save as</p>"
            else:
                #if fine, include in check
                self.saveList.append(self.saveWidget.opRmText.text())
                
        #Check Assigned Room is enabled and set to be included in save
        if self.saveWidget.asRmCheck.isEnabled() and self.saveWidget.asRmCheck.checkState() == 0:
            #Throw error if blank
            if self.saveWidget.asRmText.text() == "":
                #store error to display
                continueSave = False
                errorMessage += "<p>Must choose to ignore <i>Assigned Rooms Save</i> or select file to save as</p>"
            else:
                #if fine, include in list to check
                self.saveList.append(self.saveWidget.asRmText.text())
            
        #Make sure all file names are unique to avoid issues with overwriting an intended save
        if not self.allUnique(self.saveList):
            #if aren't all unique, throw error
            continueSave = False
            errorMessage += "<p>All file names must be unique</p>"        
        
        #If there is an error, show message
        if not continueSave:
            self.errorMessage = QMessageBox()
            self.errorMessage.setWindowIcon(QIcon("icon\error.png"))
            self.errorMessage.setIcon(QMessageBox.Critical)
            self.errorMessage.setText(errorMessage)
            self.errorMessage.setWindowTitle("Save Prompt Error")
            self.errorMessage.setStandardButtons(QMessageBox.Ok)
            self.errorMessage.setEscapeButton(QMessageBox.Close)
            self.errorMessage.show()
        else:
            #If no errors, try to save all files that are enabled and have all the info to be saved
            if self.saveWidget.rmAvCheck.isEnabled() and self.saveWidget.rmAvCheck.checkState() == 0:
                #Store all cells' data
                data = getDataFromTable(self.inRmAvTable)
                #Get the header labels to write to the top of the file
                tempHeader = []
                for col in range(0,self.inRmAvTable.columnCount()):
                    tempHeader.append(self.inRmAvTable.horizontalHeaderItem(col).text())
                
                #Write the header and all rows from the room availability to a csv
                with open(self.rmAvText.text(), 'w', newline='') as csvfile:
                    csvWrite = csv.writer(csvfile)
                    csvWrite.writerow(tempHeader)
                    csvWrite.writerows(data)
            
            #do same as above for Jack Groups
            if self.saveWidget.jkGrCheck.isEnabled() and self.saveWidget.jkGrCheck.checkState() == 0:
                data = getDataFromTable(self.inJkGrTable)
                tempHeader = []
                for col in range(0,self.inJkGrTable.columnCount()):
                    tempHeader.append(self.inJkGrTable.horizontalHeaderItem(col).text())
                        
                with open(self.jkGrText.text(), 'w', newline='') as csvfile:
                    csvWrite = csv.writer(csvfile)
                    csvWrite.writerow(tempHeader)
                    csvWrite.writerows(data)
                    
            #Same as above for Open Rooms
            if self.saveWidget.opRmCheck.isEnabled() and self.saveWidget.opRmCheck.checkState() == 0:
                workingList = []
                #Since not all cells are populated, must skip blank cells to avoid crashing
                for y_val in range(self.inOpRmTable.rowCount()):
                    tempRow = []
                    for x_val in range(self.inOpRmTable.columnCount()):
                        tempItem = self.inOpRmTable.item(y_val, x_val)
                        if tempItem != None:
                            tempRow.append(tempItem.text())
                    workingList.append(tempRow)

                with open(self.opRmText.text(), 'w', newline='') as csvfile:
                    csvWrite = csv.writer(csvfile)
                    csvWrite.writerows(workingList)
            
            #same as Open Rooms, but for Assigned Rooms, including the fact that not all cells in table widget
            #    are populated with a tableItemWidget, so must skip any blank cells to keep from crashing
            if self.saveWidget.asRmCheck.isEnabled() and self.saveWidget.asRmCheck.checkState() == 0:
                workingList = []
                for y_val in range(self.inAsRmTable.rowCount()):
                    tempRow = []
                    for x_val in range(self.inAsRmTable.columnCount()):
                        tempItem = self.inAsRmTable.item(y_val, x_val)
                        if tempItem != None:
                            tempRow.append(tempItem.text())
                    workingList.append(tempRow)
                tempHeader = []
                for col in range(0,self.inAsRmTable.columnCount()):
                    tempHeader.append(self.inAsRmTable.horizontalHeaderItem(col).text())
                        
                with open(self.asRmText.text(), 'w', newline='') as csvfile:
                    csvWrite = csv.writer(csvfile)
                    csvWrite.writerow(tempHeader)
                    csvWrite.writerows(workingList)
        
    """********
    * setSaveAccess
    ***********
    *
    * Used to not show saves when the tables are not populated yet
    *
    ********"""
    def setSaveAccess(self):
        #Save not accessible if room availability list not created 
        if self.inRmAvTable.rowCount() < 1:
            self.saveWidget.rmAvCheck.setEnabled(False)
            self.saveWidget.rmAvText.setEnabled(False)
            self.saveWidget.rmAvBrowse.setEnabled(False)
        
        #Save not accessible if jack groups list not created
        if self.inJkGrTable.rowCount() < 1:
            self.saveWidget.jkGrCheck.setEnabled(False)
            self.saveWidget.jkGrText.setEnabled(False)
            self.saveWidget.jkGrBrowse.setEnabled(False)
        
        #Save not accessible if open rooms table not created
        if self.inOpRmTable.rowCount() < 1:
            self.saveWidget.opRmCheck.setEnabled(False)
            self.saveWidget.opRmText.setEnabled(False)
            self.saveWidget.opRmBrowse.setEnabled(False)
        
        #Save not accessible if Assigned Rooms table isn't created
        #    Includes check to not allow save if it's not populated, as it is only used for output and not input
        #    Open room table will only exist IF it's populated, so check not included.
        #    Room Availability and Jack Groups table can be created from "new" and saved 
        if self.inAsRmTable.rowCount() < 1:
            self.saveWidget.asRmCheck.setEnabled(False)
            self.saveWidget.asRmText.setEnabled(False)
            self.saveWidget.asRmBrowse.setEnabled(False)
        
        if self.inAsRmTable.item(0,0) == None:
            self.saveWidget.asRmCheck.setEnabled(False)
            self.saveWidget.asRmText.setEnabled(False)
            self.saveWidget.asRmBrowse.setEnabled(False)
    
    """********
    * ...BrowseFunc 
    * ...CheckFunc
    ***********
    *
    * BrowseFunc
    *    Used to open save file dialog and store path + file name in associated line edit
    *
    * CheckFunc
    *    Used to toggle accessibility of browse buttons and line edits
    *
    ********"""
    def rmAvBrowseFunc(self):
        rmAvFilename = QFileDialog.getSaveFileName(self, 'Room Availability Save', '', 'CSV (*.csv)')
        if rmAvFilename:
            self.rmAvText.setText(rmAvFilename[0])

    def rmAvCheckFunc(self):
        self.saveWidget.rmAvText.setEnabled(self.saveWidget.rmAvCheck.checkState() == 0)
        self.saveWidget.rmAvBrowse.setEnabled(self.saveWidget.rmAvCheck.checkState() == 0)
    
    def jkGrBrowseFunc(self):
        jkGrFilename = QFileDialog.getSaveFileName(self, 'Jack Group Save', '', 'CSV (*.csv)')
        if jkGrFilename:
            self.jkGrText.setText(jkGrFilename[0])
                        
    def jkGrCheckFunc(self):
        self.saveWidget.jkGrText.setEnabled(self.saveWidget.jkGrCheck.checkState() == 0)
        self.saveWidget.jkGrBrowse.setEnabled(self.saveWidget.jkGrCheck.checkState() == 0)
    
    def opRmBrowseFunc(self):
        opRmFilename = QFileDialog.getSaveFileName(self, 'Open Room List Save', '', 'CSV (*.csv)')
        if opRmFilename:
            self.opRmText.setText(opRmFilename[0])
                         
    def opRmCheckFunc(self):
        self.saveWidget.opRmText.setEnabled(self.saveWidget.opRmCheck.checkState() == 0)
        self.saveWidget.opRmBrowse.setEnabled(self.saveWidget.opRmCheck.checkState() == 0)
    
    def asRmBrowseFunc(self):
        asRmFilename = QFileDialog.getSaveFileName(self, 'Assigned room List Save', '', 'CSV (*.csv)')
        if asRmFilename:
            self.asRmText.setText(asRmFilename[0])   
                       
    def asRmCheckFunc(self):
        self.saveWidget.asRmText.setEnabled(self.saveWidget.asRmCheck.checkState() == 0)
        self.saveWidget.asRmBrowse.setEnabled(self.saveWidget.asRmCheck.checkState() == 0)

"""********
* JackGroup
***********
*
* Object holds information about groups jacking:
*    points (float) - The rounded amount of points each group has to jack with
*    nameList (list of strings) - The list of names of people jacking as a group
*    type - The string containing the type of group
*        Supported types
*            male, female
*            Will be set to "error" and throw error message if the type is not supported
*    preList - list of ints indicating the ranked preference of rooms (1st is most wanted; last is least wanted)
*    groupSize - int indicating number of people in the group, set automatically from number of names in list
*
********"""
class JackGroup:
    def __init__(self, inPoints, inType, inNameList, inPrefList, assignedRoomIn = 0):
        self.points = float(inPoints)
        self.nameList = inNameList
        if inType.lower() == "male":
            self.groupType = "male"
        elif inType.lower() == "female":
            self.groupType = "female"
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
        self.groupSize = 0
        for obj in self.nameList:
            if obj != '':
                self.groupSize += 1
    
    #Return all values in string when converted to string
    def __str__(self):
        return ("Points: " + str(self.points) + "; Group Type: " + str(self.groupType) + "; Assigned Room: " + str(self.assignedRoom) + "; Members: " + str(self.nameList) + "; Room Pref: " + str(self.prefList))

"""********
* Room
***********
*
* Object storing information on rooms in jack:
*    number - int of room number
*    type - string of room type
*        Supported types:
*            male, female, freshman, single
*            Note: Freshman and Single will result in rooms not being assigned, regardless of availability
*    size - int, max number of beds
*    unassigned - bool, if assigned (False) or not (True)
* 
********"""
class Room:
    def __init__(self, inNumber, inType, inSize, inAssigned):
        
        if inNumber.isnumeric():
            self.number = int(inNumber)
        else:
            self.number = 0
            self.errorMessage = QMessageBox()
            self.errorMessage.setIcon(QMessageBox.Critical)
            self.errorMessage.setWindowIcon(QIcon("icon\error.png"))
            self.errorMessage.setText("Invalid room number: " + str(inNumber))
            self.errorMessage.setDetailedText("Room number must be positive integer")
            self.errorMessage.setWindowTitle("Room Creation Error")
            self.errorMessage.setStandardButtons(QMessageBox.Ok)
            self.errorMessage.setEscapeButton(QMessageBox.Close)
            self.errorMessage.show()
            
        if inType.lower() == "male":
            self.type = "male"
        elif inType.lower() == "female":
            self.type = "female"
        elif inType.lower() == "freshman":
            self.type = "freshman"
        elif inType.lower() == "single":
            self.type = "single"
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
            
        if inSize.isnumeric():
            self.size = inSize
        else:
            self.size = 0
            self.errorMessage = QMessageBox()
            self.errorMessage.setIcon(QMessageBox.Critical)
            self.errorMessage.setWindowIcon(QIcon("icon\error.png"))
            self.errorMessage.setText("Invalid room size: " + str(inSize))
            self.errorMessage.setDetailedText("Room Size must be positive integer")
            self.errorMessage.setWindowTitle("Room Creation Error")
            self.errorMessage.setStandardButtons(QMessageBox.Ok)
            self.errorMessage.setEscapeButton(QMessageBox.Close)
            self.errorMessage.show()
        
        if inAssigned.lower() == "true" or inAssigned.lower() == "false":
            self.unassigned = inAssigned
            
        else:
            self.type = "error"
            self.errorMessage = QMessageBox()
            self.errorMessage.setIcon(QMessageBox.Critical)
            self.errorMessage.setWindowIcon(QIcon("icon\error.png"))
            self.errorMessage.setText("Invalid room availability: " + str(inAssigned))
            self.errorMessage.setDetailedText("Room availability either True or False")
            self.errorMessage.setWindowTitle("Room Creation Error")
            self.errorMessage.setStandardButtons(QMessageBox.Ok)
            self.errorMessage.setEscapeButton(QMessageBox.Close)
            self.errorMessage.show()
        
    def __str__(self):
        return("Number: " + str(self.number) + "; Type: " + str(self.inType) + "; Assigned: " + str(self.assigned))
                   
#Used to sort the jackGroup object lists
#    By points
def pointSortKey(self):
        return self.points      
  
    #Sort by assigned room number
def roomSortKey(self):
        return self.assignedRoom

"""********
* makeRoomDictFromObjList
***********
*
* Sets up and returns a dictionary of room objects, key: room number
*
********"""
def makeRoomDictFromObjList(inRoomList):
    workingDic = {}
    for room in inRoomList:
        workingDic[int(room.number)] = room
    return workingDic

"""********
* getAvailableRoomsFromRow
***********
*
* Pass in list of room objects and list of jack groups, plus the current row (as int)
*
* Returns a sorted list of all rooms that have not been assigned
*
********"""
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

"""********
* createRoomTableFromCSV
***********
*
* Pass in Room Table and a string with the path to the CSV containing room info
*
********"""
def createRoomTableFromCSV(inRoomTable, fileDir):
    #create reader
    roomLoadInput = open(fileDir, 'r')
    inRoomList = []
    
    #block signals to prevent Change events from being called when cells are populated
    inRoomTable.blockSignals(True)
    
    #for every row in CSV,
    for row in roomLoadInput:
        tempRoomList = []
        #split into list of cells and strip of whitespace
        tempRow = row.split(',')
        for cell in tempRow:
            cell = ' '.join(cell.split())
            tempRoomList.append(cell)
        inRoomList.append(tempRoomList)       
    #if the file has a header, set the table headers to the file headers
    if ROOM_LIST_HASHEADER == True:
        inRoomTable.setRowCount(len(inRoomList)-1)
        roomHeader = inRoomList[0]
        inRoomList.pop(0)
    #otherwise, use default headers
    else:
        inRoomTable.setRowCount(len(inRoomList))
        roomHeader = ["Number", "Type", "Max Occupancy", "Assigned"]
    inRoomTable.setColumnCount(4)
    inRoomTable.setHorizontalHeaderLabels(roomHeader)
    
    #populate the table with all the values
    for x_val in range(len(inRoomList[0])):
        for y_val in range(len(inRoomList)):
            inRoomTable.setItem(y_val, x_val, QTableWidgetItem(inRoomList[y_val][x_val]))
    
    #create room objects from the table
    createRoomsFromTable(inRoomTable)
    global roomObjectDict
    
    #update the dictionary (room number: room object)
    roomObjectDict = makeRoomDictFromObjList(roomList)
    
    #allow table to pass signals again
    inRoomTable.blockSignals(False)

"""********
* createJackGroupTableFromCsv
***********
*
* Pass in table to be populated with jack group info from CSV
*
********"""    
def createJackGroupTableFromCSV(inJackTable, fileDir):
    #create reader
    jackGroupLoadInput = open(fileDir, 'r')
    inJackGroupList = []
    
    #block signals to prevent from calling Change function as cells are populated
    inJackTable.blockSignals(True)
    #import every row
    for row in jackGroupLoadInput:
        tempRoomList = []
        tempRow = row.split(',')
        for cell in tempRow:
            #strip of any white space
            cell = ' '.join(cell.split())
            tempRoomList.append(cell)
        inJackGroupList.append(tempRoomList)
    #if file has header, set table headers to file headers
    if GROUP_LIST_HASHEADER == True:
        inJackTable.setRowCount(len(inJackGroupList)-1)
        jackHeader = inJackGroupList[0]
        inJackGroupList.pop(0)
    else:
        #otherwise, use default labels
        inJackTable.setRowCount(len(inJackGroupList))
        jackHeader = ["Points", "Group Type"]
        for index in range(2,MAX_ROOMMATES+2):
            jackHeader.append("Member " + str(index))
        for index in range(MAX_ROOMMATES + 2,MAX_ROOMMATES + MAX_PREF_LIST_LENGTH+2):
            jackHeader.append("Choice " + str(index))       
        jackHeader.append("Assigned Room")
    inJackTable.setColumnCount(len(jackHeader))
    inJackTable.setHorizontalHeaderLabels(jackHeader)
    
    #Populate cells
    for x_val in range(len(jackHeader)):
        for y_val in range(len(inJackGroupList)):
            inJackTable.setItem(y_val, x_val, QTableWidgetItem(inJackGroupList[y_val][x_val]))
    #Create jack group objects from the table    
    createJackGroupsFromTable(inJackTable)
    #allow table to pass signals again
    inJackTable.blockSignals(False)

"""********
* createBlankOutputTable
***********
*
* Pass in a table and an int with number of rows.
*
* First row: Assigned room; Last Rows: Room mate names 
*
********"""    
def createBlankOutputTable(inOutputTable, numRows):
    inOutputTable.setRowCount(numRows)
    outputHeader = ["Assigned Room"]
    for index in range(1,MAX_ROOMMATES+1):
        outputHeader.append("Member " + str(index))
    inOutputTable.setColumnCount(MAX_ROOMMATES+1)
    inOutputTable.setHorizontalHeaderLabels(outputHeader)

"""********
* getDataFromTable 
***********
*
* Pass in any fully populated table. Return a list of the data
*
********"""
def getDataFromTable(inTable):
    workingList = []
    for y_val in range(inTable.rowCount()):
        tempRow = []
        for x_val in range(inTable.columnCount()):
            tempRow.append(inTable.item(y_val, x_val).text())
        workingList.append(tempRow)
    return workingList

"""********
* createJackGroupsFromTable
***********
*
* Pass in table and and create jack groups, and append to global JackList
*
********"""
def createJackGroupsFromTable(sourceTable):
    global jackList
    jackList = []
    workingList = getDataFromTable(sourceTable)
    for row in workingList:
        groupSetupIndex = 0
        tempNamesList = []
        tempRoomPrefList = []
        tempGroupType = row[GROUP_TYPE_COL]
        tempPoints = float(row[GROUP_POINTS_COL])
        groupSetupIndex = 2
        while groupSetupIndex < MAX_ROOMMATES + 2:
            if row[groupSetupIndex] != "":
                tempNamesList.append(row[groupSetupIndex])
            groupSetupIndex += 1
        while groupSetupIndex < MAX_ROOMMATES + MAX_PREF_LIST_LENGTH + 2:
            if row[groupSetupIndex] != "":
                tempRoomPrefList.append(int(row[groupSetupIndex]))
            groupSetupIndex += 1
        tempAssignedRoom = int(row[groupSetupIndex])
        jackList.append(JackGroup(tempPoints, tempGroupType, tempNamesList, tempRoomPrefList, tempAssignedRoom))

"""********
* createRoomsFromTable
***********
*
* Populate global RoomList from source table 
*
********"""
def createRoomsFromTable(sourceTable):
    global roomList
    roomList = []
    workingList = getDataFromTable(sourceTable)
    for row in workingList:
        roomList.append(Room(row[0], row[1], row[2], row[3]))

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        #load the gui from the .ui xml file created in Qt Creator 
        self.mainWindow = loadUi('MainWindow.ui', self)
        
        #Assign favIcon
        self.setWindowIcon(QIcon('bakerCrest.png'))
                
        #Assign icons to menu elements
        self.mainWindow.actionNew.setIcon(QIcon('icon/new.png'))
        self.mainWindow.actionOpen.setIcon(QIcon('icon/open.png'))
        self.mainWindow.actionSave.setIcon(QIcon('icon/save.png'))
        self.mainWindow.actionShuffle.setIcon(QIcon('icon/sort.png'))
        self.mainWindow.menuAssignRooms.setIcon(QIcon('icon/run.png'))
        
        #Set up function to check cells when edited in Room Availability or Jack Group tables         
        self.mainWindow.roomAvailabilityTable.cellChanged.connect(self.cellCheck)
        self.mainWindow.jackGroupTable.cellChanged.connect(self.cellCheck)
        
        
        #self.mainWindow.actionNew.triggered.connect(...)
        self.mainWindow.actionOpen.triggered.connect(self.showOpenPrompt)
        self.mainWindow.actionSave.triggered.connect(self.showSavePrompt)
        self.mainWindow.actionShuffle.triggered.connect(self.sortByPoints)
        self.mainWindow.actionAssignFromStart.triggered.connect(self.assignPrompt)
        #self.mainWindow.actionAssignFromCurrentRow(...)
        """
        self.mainWindow.actionSave.triggered.connect()
        self.mainWindow.actionShuffletriggered.connect(self.sortByPoints)
        
        self.mainWindow.actionAssignFromStart.triggered.connect(self.gui.assignRoom)
        self.mainWindow.actionAssignFromCurrentRow.triggered.connect(self.gui.assignRoomFromRow) 
        """
        
        
        self.openPrompt = OpenPrompt(self.mainWindow.roomAvailabilityTable, self.mainWindow.jackGroupTable, self.mainWindow.sortedRoomsTable)
        self.savePrompt = SavePrompt(self.mainWindow.roomAvailabilityTable, self.mainWindow.jackGroupTable, self.mainWindow.openRoomsTable, self.mainWindow.sortedRoomsTable)
        
        self.show()
        
        #self.newFile.triggered.connect(self.showNewDialog)
            #Write New Dialog
            #New: allow to self
            
    def assignPrompt(self):
        if self.mainWindow.roomAvailabilityTable.rowCount() > 0 and self.mainWindow.jackGroupTable.rowCount() > 0:
            self.assignMsg = QMessageBox()
            self.assignMsg.setWindowIcon(QIcon("icon\sort.png"))
            self.assignMsg.setText("<p>Do you want to sort and shuffle the jack groups before assigning?</p>"+
                                   "<p style=\"color: dimgray\">Note:<ul style=\"list-style-type:none\"><li>Must be sorted at least once before assigning rooms to grant proper priority to Bakerites with more points</li><li>Not recommended you reshuffle list after you begin assigning rooms</li></p>")
            self.assignMsg.setWindowTitle("Pre-Assignment Shuffle")
            self.assignMsg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            self.assignMsg.buttonClicked.connect(self.assignPromptMngr)
            self.assignMsg.show()
            
    def assignPromptMngr(self, buttonIn):
        if buttonIn.text() == "&Yes":
            print("yes")
            self.sortByPoints()
            print("sorted")
            self.assignRoom()
            print("assigned")
        elif buttonIn.text() == "&No":
            self.assignRoom()
    
    def assignRoom(self):
        global jackList, roomList, roomObjectDict
        
        createJackGroupsFromTable(self.mainWindow.jackGroupTable)
        createRoomsFromTable(self.mainWindow.roomAvailabilityTable)
        print("created lists")
        
        roomAvaiList = makeRoomDictFromObjList(roomList)
        groupIndex = 0
        numGroups = len(jackList)
        roomIndex = 0
        sortedYet = False
        
        print("dict made and variables set")
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
        print("Finished assignment")
        loopIndex = self.getFirstUnassignedGroup()
        print("Got unassigned group")
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

            self.mainWindow.jackGroupTable.blockSignals(True)
            for y_val in range(len(jackList)):
                self.mainWindow.jackGroupTable.setItem(y_val, MAX_ROOMMATES+MAX_PREF_LIST_LENGTH+2, QTableWidgetItem(str(jackList[y_val].assignedRoom)))
            self.mainWindow.jackGroupTable.blockSignals(False)    
            listOpenRooms = getRemainingOpenRooms()
            openRoomTableInput = generateOpRmTbInFromList(listOpenRooms)
            self.mainWindow.openRoomsTable.setShowGrid(False)
            self.mainWindow.openRoomsTable.setColumnCount(11)
            self.mainWindow.openRoomsTable.setRowCount(len(openRoomTableInput))
            self.mainWindow.openRoomsTable.horizontalHeader().setVisible(False)
            self.mainWindow.openRoomsTable.verticalHeader().setVisible(False)
            for row_count in range(0,len(openRoomTableInput)):
                for column_count in range(0,len(openRoomTableInput[row_count])):
                    self.mainWindow.openRoomsTable.setItem(row_count,column_count,QTableWidgetItem(str(openRoomTableInput[row_count][column_count])))
            self.mainWindow.openRoomsTable.setVisible(False)
            self.mainWindow.openRoomsTable.resizeColumnsToContents()
            self.mainWindow.openRoomsTable.setVisible(True)
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
            print("finished")
            self.mainWindow.jackGroupTable.blockSignals(True)
            roomOrderList = sorted(jackList, key = roomSortKey)
            for y_val in range(len(jackList)):
                self.mainWindow.jackGroupTable.setItem(y_val, MAX_ROOMMATES+MAX_PREF_LIST_LENGTH+2, QTableWidgetItem(str(jackList[y_val].assignedRoom)))
                self.mainWindow.sortedRoomsTable.setItem(y_val,0,QTableWidgetItem(str(roomOrderList[y_val].assignedRoom)))
                for x_val in range(1,len(roomOrderList[y_val].nameList)+1):
                    self.mainWindow.sortedRoomsTable.setItem(y_val,x_val,QTableWidgetItem(str(roomOrderList[y_val].nameList[x_val-1])))
            self.mainWindow.jackGroupTable.blockSignals(False)
            
            listOpenRooms = getRemainingOpenRooms()
            openRoomTableInput = generateOpRmTbInFromList(listOpenRooms)
            self.mainWindow.openRoomsTable.setShowGrid(False)
            self.mainWindow.openRoomsTable.setColumnCount(11)
            self.mainWindow.openRoomsTable.setRowCount(len(openRoomTableInput))
            self.mainWindow.openRoomsTable.horizontalHeader().setVisible(False)
            self.mainWindow.openRoomsTable.verticalHeader().setVisible(False)
            for row_count in range(0,len(openRoomTableInput)):
                for column_count in range(0,len(openRoomTableInput[row_count])):
                    self.mainWindow.openRoomsTable.setItem(row_count,column_count,QTableWidgetItem(str(openRoomTableInput[row_count][column_count])))
            self.mainWindow.openRoomsTable.setVisible(False)
            self.mainWindow.openRoomsTable.resizeColumnsToContents()
            self.mainWindow.openRoomsTable.setVisible(True)
            
            self.errorMessage = QMessageBox()
            self.errorMessage.setWindowIcon(QIcon("icon\new.png"))
            self.errorMessage.setIcon(QMessageBox.Information)
            self.errorMessage.setText("Every group has room assigned")
            self.errorMessage.setWindowTitle("Assignment Complete")
            self.errorMessage.setStandardButtons(QMessageBox.Ok)
            self.errorMessage.setEscapeButton(QMessageBox.Close)
            self.errorMessage.show()         
    
    def cellCheck(self):
        global jacklist, roomList, roomObjectDict
        validCheck = validateData(self.mainWindow.roomAvailabilityTable, self.mainWindow.jackGroupTable)
        if validCheck[0] == True:
            createJackGroupsFromTable(self.mainWindow.jackGroupTable)
            createRoomsFromTable(self.mainWindow.roomAvailabilityTable)
            roomObjectDict = makeRoomDictFromObjList(roomList)
            
        
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
        
    def showOpenPrompt(self):
        self.openPrompt.show()
    
    def showSavePrompt(self):
        self.savePrompt = SavePrompt(self.mainWindow.roomAvailabilityTable, self.mainWindow.jackGroupTable, self.mainWindow.openRoomsTable, self.mainWindow.sortedRoomsTable)
        self.savePrompt.setSaveAccess()
        self.savePrompt.show()
        
    def sortByPoints(self):
        continueCheck = validateData(self.mainWindow.roomAvailabilityTable, self.mainWindow.jackGroupTable)
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
            if self.mainWindow.jackGroupTable.columnCount() > 0 and self.mainWindow.jackGroupTable.rowCount() > 0:
                tempList = []
                outList = []
                curPoints = 0
                loopCheck = True
                curIndex = 0
                sortList = getDataFromTable(self.mainWindow.jackGroupTable)
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
                self.mainWindow.jackGroupTable.blockSignals(True)
                for x_val in range(len(outList[0])):
                    for y_val in range(len(outList)):
                        
                        self.mainWindow.jackGroupTable.setItem(y_val, x_val, QTableWidgetItem(outList[y_val][x_val]))
                self.mainWindow.jackGroupTable.blockSignals(False)
                createJackGroupsFromTable(self.mainWindow.jackGroupTable)
        
    def validateData(self, inRmTable, inJkGrTable):
        valid = True
        errorMessage = ''
        roomNumberError = 0
        duplicateRoomError = 0.0
        roomTypeError = 0
        roomSizeError = 0
        roomAvaiError = 0
        groupPointError = 0
        groupTypeError = 0
        roomExistError = 0
        groupNameListError = 0
        groupRoomPrefListError = 0
        duplicateGroupRoomPrefError = 0.0
        groupRoomAssignmentError = 0
        
        errorColor = QColor(245,142,144)
        roomErrorColor = QColor(255,223,186)
        normalColor = QColor(255,255,255)
        
        inRmTable.blockSignals(True)
        inJkGrTable.blockSignals(True)
        for row_count in range(0, inRmTable.rowCount()):        
            for column_count in range(0, inRmTable.columnCount()):
                curItem = inRmTable.item(row_count, column_count)
                #check to make sure room numbers are integers
                if column_count == ROOM_NUMBER_COL:
                    if not curItem.text().isnumeric():
                        valid = False
                        roomNumberError += 1
                        curItem.setBackground(errorColor)
                        curItem.setToolTip("Must be positive integer")
                    elif int(curItem.text()) < 0:
                        valid = False
                        roomNumberError += 1
                        curItem.setBackground(errorColor)
                        curItem.setToolTip("Must be positive integer")
                    else:
                        matchList = inRmTable.findItems(curItem.text(), Qt.MatchExactly)
                        matchList = [item for item in matchList if (inRmTable.column(item) == ROOM_NUMBER_COL)]
                        if len(matchList) == 1:
                            if matchList[0].text().isnumeric():
                                if int(matchList[0].text()) > 0:
                                    matchList[0].setBackground(normalColor)
                                    matchList[0].setToolTip("")
                        else:
                            valid = False
                            for item in matchList:
                                if inRmTable.column(item) == ROOM_NUMBER_COL:
                                    if item.text().isnumeric():
                                        if int(matchList[0].text()) > 0:
                                            item.setBackground(roomErrorColor)
                                            item.setToolTip("Duplicate room")
                            duplicateRoomError += 1.0/len(matchList)
                            
                elif column_count == ROOM_TYPE_COL:
                    rmType = curItem.text().lower()
                    if rmType != 'male' and rmType != 'female' and rmType != 'freshman' and rmType != 'single':
                        valid = False
                        roomTypeError += 1
                        curItem.setBackground(errorColor)
                        curItem.setToolTip("Invalid room type")
                    else:
                        curItem.setBackground(normalColor)
                        curItem.setToolTip("")
                elif column_count == ROOM_SIZE_COL:
                    if not curItem.text().isnumeric():
                        valid = False
                        roomSizeError += 1
                        curItem.setBackground(errorColor)
                        curItem.setToolTip("Must be positive integer")
                    elif int(curItem.text()) < 0:
                        valid = False
                        roomSizeError += 1
                        curItem.setBackground(errorColor)
                        curItem.setToolTip("Must be positive integer")
                    elif int(curItem.text()) > MAX_ROOMMATES:
                        valid = False
                        roomSizeError += 1
                        curItem.setBackground(errorColor)
                        curItem.setToolTip("Exceeds defined max occupancy")
                    else:
                        curItem.setBackground(normalColor)
                        curItem.setToolTip("")
                elif column_count == ROOM_AVAI_COL:
                    rmType = curItem.text().lower()
                    if rmType != 'true' and rmType != 'false':
                        valid = False
                        roomAvaiError += 1
                        curItem.setBackground(errorColor)
                        curItem.setToolTip("Invalid availability")
                    else:
                        curItem.setBackground(normalColor)
                        curItem.setToolTip("")
        for row_count in range(0, inJkGrTable.rowCount()):        
            for column_count in range(0, inJkGrTable.columnCount()):
                curItem = inJkGrTable.item(row_count, column_count)
                print("Edit")
                print(roomObjectDict[int(curItem.text())].unassigned)
                #check to make sure room numbers are integers
                if column_count == GROUP_POINTS_COL:
                    if not canCastToFloat(curItem.text()):
                        valid = False
                        groupPointError += 1
                        curItem.setBackground(errorColor)
                        curItem.setToolTip("Must be a number (float: 0.00)\ngreater than 0")
                    elif float(curItem.text()) < 0:
                        valid = False
                        groupPointError += 1
                        curItem.setBackground(errorColor)
                        curItem.setToolTip("Must be a number (float: 0.00)\ngreater than 0")
                    elif float(curItem.text()) > float(MAX_POINTS) and float(MAX_POINTS) != 0.0:
                        valid = False
                        groupPointError += 1
                        curItem.setBackground(roomErrorColor)
                        curItem.setToolTip("Exceeds defined max points")
                    else:
                        curItem.setBackground(normalColor)
                        curItem.setToolTip("")
                elif column_count == GROUP_TYPE_COL:
                    grType = curItem.text().lower()
                    if grType != 'male' and grType != 'female':
                        valid = False
                        groupTypeError += 1
                        curItem.setBackground(errorColor)
                        curItem.setToolTip("Invalid group type")
                    else:
                        curItem.setBackground(normalColor)
                        curItem.setToolTip("")
                elif column_count > GROUP_TYPE_COL and column_count < GROUP_TYPE_COL + MAX_ROOMMATES + 1:
                    if canCastToFloat(curItem.text()) and curItem.text() != '':
                        valid = False
                        groupNameListError += 1
                        curItem.setBackground(errorColor)
                        curItem.setToolTip("Jack group member name\nshould not be a number")
                    else:
                        curItem.setBackground(normalColor)
                        curItem.setToolTip("")
                elif column_count > MAX_ROOMMATES + 1 and column_count != MAX_ROOMMATES + MAX_PREF_LIST_LENGTH + 2:
                    if curItem.text() == "":
                        curItem.setBackground(normalColor)
                        curItem.setToolTip("")
                    elif not curItem.text().isnumeric():
                        valid = False
                        groupRoomPrefListError += 1
                        curItem.setBackground(errorColor)
                        curItem.setToolTip("Must be positive integer")
                    elif int(curItem.text()) < 0:
                        valid = False
                        groupRoomPrefListError += 1
                        curItem.setBackground(errorColor)
                        curItem.setToolTip("Must be positive integer")
                    elif not int(curItem.text()) in roomObjectDict:
                        valid = False
                        roomExistError += 1
                        curItem.setBackground(errorColor)
                        curItem.setToolTip("Room does not exist")     
                    elif jackList[inJkGrTable.row(curItem)].groupType != roomObjectDict[int(curItem.text())].type:
                        curItem.setBackground(roomErrorColor)
                        curItem.setToolTip("Room/Group Type Mismatch")
                    elif roomObjectDict[int(curItem.text())].unassigned == 'true':
                        curItem.setBackground(roomErrorColor)
                        curItem.setToolTip("Room not available")            
                    else:
                        matchList = inJkGrTable.findItems(curItem.text(), Qt.MatchExactly)
                        matchList = [item for item in matchList if (inJkGrTable.row(curItem) == inJkGrTable.row(item) and inJkGrTable.column(item) > MAX_ROOMMATES + 1 and inJkGrTable.column(item) != MAX_ROOMMATES + MAX_PREF_LIST_LENGTH + 2 )]
                        if len(matchList) == 1:
                            if matchList[0].text().isnumeric():
                                if int(matchList[0].text()) > 0:
                                    matchList[0].setBackground(normalColor)
                                    matchList[0].setToolTip("")
                        else:
                            valid = False
                            for item in matchList:
                                if inJkGrTable.column(item) > MAX_ROOMMATES + 1 and inJkGrTable.column(item) != MAX_ROOMMATES + MAX_PREF_LIST_LENGTH + 2:
                                    if item.text().isnumeric():
                                        if int(matchList[0].text()) > 0:
                                            item.setBackground(roomErrorColor)
                                            item.setToolTip("Occurs " +str(len(matchList)) + " times\nin preference list")
                            duplicateGroupRoomPrefError += 1.0/len(matchList)
                        
                elif column_count == MAX_ROOMMATES + MAX_PREF_LIST_LENGTH + 2:
                    if not curItem.text().isnumeric():
                        valid = False
                        groupRoomAssignmentError += 1
                        curItem.setBackground(errorColor)
                        curItem.setToolTip("Must be positive integer")
                    elif int(curItem.text()) < 0:
                        valid = False
                        groupRoomAssignmentError += 1
                        curItem.setBackground(errorColor)
                        curItem.setToolTip("Must be positive integer")
                    else:
                        curItem.setBackground(normalColor)
                        curItem.setToolTip("")
                        
        if not valid:
            if roomNumberError > 0:
                errorMessage += ("<p>Non-Integer Room Numbers: " + str(roomNumberError) +"</p>")
            if duplicateRoomError > 0:
                errorMessage += ("<p>Duplicate Rooms: " + str(int(duplicateRoomError)) +"</p>")
            if roomTypeError > 0:
                errorMessage += ("<p>Invalid Room Types: " + str(roomTypeError) + "</p>")
            if roomSizeError > 0:
                errorMessage += ("<p>Invalid Room Sizes: " + str(roomSizeError) + "</p>")
            if roomAvaiError > 0:
                errorMessage += ("<p>Invalid Room Availability: " + str(roomAvaiError) + "</p>")
            if groupPointError > 0:
                errorMessage += ("<p>Invalid Group Points: " + str(groupPointError) + "</p>")
            if groupTypeError > 0:
                errorMessage += ("<p>Invalid Group Types: " + str(groupTypeError) + "</p>")
            if groupNameListError > 0:
                errorMessage += ("<p>Names listed as numbers: " + str(groupNameListError) + "</p>")
            if groupRoomPrefListError > 0:
                errorMessage += ("<p>Invalid Room Preferences: " + str(groupRoomPrefListError) + "</p>")
            if duplicateGroupRoomPrefError > 0:
                errorMessage += ("<p>Duplicated Rooms: " + str(int(duplicateGroupRoomPrefError)) +"</p>")
            if roomExistError > 0:
                errorMessage += ("<p>Requested Rooms Not on List: " + str(int(roomExistError)) + "</p>")
            if groupRoomAssignmentError > 0:
                errorMessage += ("<p>Invalid Room Assignments: " + str(groupRoomAssignmentError) + "</p>")
                                          
        inRmTable.blockSignals(False)
        inJkGrTable.blockSignals(False)
        return [valid, errorMessage]

"""********
*canCastToFloat
***********
*
* True if input can be cast as float; false if not
*
********"""
def canCastToFloat(inputVal):
        try:
            float(inputVal)
            return True
        except ValueError:
            return False

"""********
* getRemainingOpenRooms
***********
*
* Get lists of any rooms, sorted by the number of max room mates (1, 2 ... max - 1, max)
*
* Format: [[list of singles], [list of doubles], [list of triples], [list of quads], etc.]
*
* Returns separate list for male and female rooms, as [maleRoomsList, femaleRoomsList]
*
********"""
def getRemainingOpenRooms():
    maleRooms = []
    maleTemp = []
    femaleRooms = []
    femaleTemp = []
    #Male rooms
    for occupancyAmt in range(1,MAX_ROOMMATES+1):
        maleTemp = [room for room in roomObjectDict if (int(roomObjectDict[room].size) == occupancyAmt and bool(roomObjectDict[room].unassigned) == True and str(roomObjectDict[room].type) == "male")]
        maleTemp.sort()
        maleRooms.append(maleTemp)
        femaleTemp = [room for room in roomObjectDict if (int(roomObjectDict[room].size) == occupancyAmt and bool(roomObjectDict[room].unassigned) == True and str(roomObjectDict[room].type) == "female")]
        femaleTemp.sort()
        femaleRooms.append(femaleTemp)
    return([maleRooms,femaleRooms])


"""********
* generateOpRmTbInFromList
***********
*
* Takes list from getRemainingOpenRooms and breaks into rows of max 10 to populate Open Rooms table with
* Lists Males, then has header for number of roommates who can stay in each room
*
********"""
def generateOpRmTbInFromList(inOpenRooms):
    tableIn = []

    anyMale = False
    anyFemale = False
    tempRoomList = []
    maleTempList = []
    femaleTempList = []
    curIndex = 0
    rowPos = 0
    
    for row in inOpenRooms[0]:
        rowPos += 1
        if len(row) > 0:
            anyMale = True
            maleTempList.append([rowPos])
            curIndex = 0
            tempRoomList = [""]
            for cell in row:
                curIndex += 1
                tempRoomList.append(cell)
                if curIndex == 10:
                    maleTempList.append(tempRoomList)
                    tempRoomList = ([""])
                    curIndex = 0
            maleTempList.append(tempRoomList)
            if tempRoomList != [""]:
                maleTempList.append([""])
            
    rowPos = 0
    for row in inOpenRooms[1]:
        rowPos += 1
        if len(row) > 0:
            anyFemale = True
            femaleTempList.append([rowPos])
            curIndex = 0
            tempRoomList = [""]
            for cell in row:
                curIndex += 1
                tempRoomList.append(cell)
                if curIndex == 10:
                    femaleTempList.append(tempRoomList)
                    tempRoomList = ([""])
                    curIndex = 0
            femaleTempList.append(tempRoomList)
            if tempRoomList != [""]:
                femaleTempList.append([""])
                    
    if anyMale == True:
        tableIn.append(["Male"])
        for row in maleTempList:
            tableIn.append(row)
    if anyFemale == True:
        tableIn.append(["Female"])
        for row in femaleTempList:
            tableIn.append(row)
    
    return(tableIn)   
                
"""********
* validateData
***********
*
* Goes through Room Table and Jack Group table and highlights any cells with errors and sets tool tip 
*
********"""        
def validateData(inRmTable, inJkGrTable):
    valid = True
    errorMessage = ''
    roomNumberError = 0
    duplicateRoomError = 0.0
    roomTypeError = 0
    roomSizeError = 0
    roomAvaiError = 0
    groupPointError = 0
    groupTypeError = 0
    roomExistError = 0
    groupNameListError = 0
    groupRoomPrefListError = 0
    duplicateGroupRoomPrefError = 0.0
    groupRoomAssignmentError = 0
    
    errorColor = QColor(245,142,144)
    roomErrorColor = QColor(255,223,186)
    normalColor = QColor(255,255,255)
    
    inRmTable.blockSignals(True)
    inJkGrTable.blockSignals(True)
    for row_count in range(0, inRmTable.rowCount()):        
        for column_count in range(0, inRmTable.columnCount()):
            curItem = inRmTable.item(row_count, column_count)
            #check to make sure room numbers are integers
            if column_count == ROOM_NUMBER_COL:
                if not curItem.text().isnumeric():
                    valid = False
                    roomNumberError += 1
                    curItem.setBackground(errorColor)
                    curItem.setToolTip("Must be positive integer")
                elif int(curItem.text()) < 0:
                    valid = False
                    roomNumberError += 1
                    curItem.setBackground(errorColor)
                    curItem.setToolTip("Must be positive integer")
                else:
                    matchList = inRmTable.findItems(curItem.text(), Qt.MatchExactly)
                    matchList = [item for item in matchList if (inRmTable.column(item) == ROOM_NUMBER_COL)]
                    if len(matchList) == 1:
                        if matchList[0].text().isnumeric():
                            if int(matchList[0].text()) > 0:
                                matchList[0].setBackground(normalColor)
                                matchList[0].setToolTip("")
                    else:
                        valid = False
                        for item in matchList:
                            if inRmTable.column(item) == ROOM_NUMBER_COL:
                                if item.text().isnumeric():
                                    if int(matchList[0].text()) > 0:
                                        item.setBackground(roomErrorColor)
                                        item.setToolTip("Duplicate room")
                        duplicateRoomError += 1.0/len(matchList)
                    """
                    curItem.setBackground(normalColor)
                    curItem.setToolTip("")
                    """                    
            elif column_count == ROOM_TYPE_COL:
                rmType = curItem.text().lower()
                if rmType != 'male' and rmType != 'female' and rmType != 'freshman' and rmType != 'single':
                    valid = False
                    roomTypeError += 1
                    curItem.setBackground(errorColor)
                    curItem.setToolTip("Invalid room type")
                else:
                    curItem.setBackground(normalColor)
                    curItem.setToolTip("")
            elif column_count == ROOM_SIZE_COL:
                if not curItem.text().isnumeric():
                    valid = False
                    roomSizeError += 1
                    curItem.setBackground(errorColor)
                    curItem.setToolTip("Must be positive integer")
                elif int(curItem.text()) < 0:
                    valid = False
                    roomSizeError += 1
                    curItem.setBackground(errorColor)
                    curItem.setToolTip("Must be positive integer")
                elif int(curItem.text()) > MAX_ROOMMATES:
                    valid = False
                    roomSizeError += 1
                    curItem.setBackground(errorColor)
                    curItem.setToolTip("Exceeds defined max occupancy")
                else:
                    curItem.setBackground(normalColor)
                    curItem.setToolTip("")
            elif column_count == ROOM_AVAI_COL:
                rmType = curItem.text().lower()
                if rmType != 'true' and rmType != 'false':
                    valid = False
                    roomAvaiError += 1
                    curItem.setBackground(errorColor)
                    curItem.setToolTip("Invalid availability")
                else:
                    curItem.setBackground(normalColor)
                    curItem.setToolTip("")
    for row_count in range(0, inJkGrTable.rowCount()):        
        for column_count in range(0, inJkGrTable.columnCount()):
            curItem = inJkGrTable.item(row_count, column_count)
            #check to make sure room numbers are integers
            if column_count == GROUP_POINTS_COL:
                if not canCastToFloat(curItem.text()):
                    valid = False
                    groupPointError += 1
                    curItem.setBackground(errorColor)
                    curItem.setToolTip("Must be a number (float: 0.00)\ngreater than 0")
                elif float(curItem.text()) < 0:
                    valid = False
                    groupPointError += 1
                    curItem.setBackground(errorColor)
                    curItem.setToolTip("Must be a number (float: 0.00)\ngreater than 0")
                elif float(curItem.text()) > float(MAX_POINTS) and float(MAX_POINTS) != 0.0:
                    valid = False
                    groupPointError += 1
                    curItem.setBackground(roomErrorColor)
                    curItem.setToolTip("Exceeds defined max points")
                else:
                    curItem.setBackground(normalColor)
                    curItem.setToolTip("")
            elif column_count == GROUP_TYPE_COL:
                grType = curItem.text().lower()
                if grType != 'male' and grType != 'female':
                    valid = False
                    groupTypeError += 1
                    curItem.setBackground(errorColor)
                    curItem.setToolTip("Invalid group type")
                else:
                    curItem.setBackground(normalColor)
                    curItem.setToolTip("")
            elif column_count > GROUP_TYPE_COL and column_count < GROUP_TYPE_COL + MAX_ROOMMATES + 1:
                if canCastToFloat(curItem.text()) and curItem.text() != '':
                    valid = False
                    groupNameListError += 1
                    curItem.setBackground(errorColor)
                    curItem.setToolTip("Jack group member name\nshould not be a number")
                else:
                    curItem.setBackground(normalColor)
                    curItem.setToolTip("")
            elif column_count > MAX_ROOMMATES + 1 and column_count != MAX_ROOMMATES + MAX_PREF_LIST_LENGTH + 2:
                
                if curItem.text() == "":
                    curItem.setBackground(normalColor)
                    curItem.setToolTip("")
                elif not curItem.text().isnumeric():
                    valid = False
                    groupRoomPrefListError += 1
                    curItem.setBackground(errorColor)
                    curItem.setToolTip("Must be positive integer")
                elif int(curItem.text()) < 0:
                    valid = False
                    groupRoomPrefListError += 1
                    curItem.setBackground(errorColor)
                    curItem.setToolTip("Must be positive integer")
                elif not int(curItem.text()) in roomObjectDict:
                    valid = False
                    roomExistError += 1
                    curItem.setBackground(errorColor)
                    curItem.setToolTip("Room does not exist")     
                elif jackList[inJkGrTable.row(curItem)].groupType != roomObjectDict[int(curItem.text())].type:
                    curItem.setBackground(roomErrorColor)
                    curItem.setToolTip("Room/Group Type Mismatch")
                elif roomObjectDict[int(curItem.text())].unassigned.lower() == 'false':
                    curItem.setBackground(roomErrorColor)
                    curItem.setToolTip("Room not available")                 
                else:
                    matchList = inJkGrTable.findItems(curItem.text(), Qt.MatchExactly)
                    matchList = [item for item in matchList if (inJkGrTable.row(curItem) == inJkGrTable.row(item) and inJkGrTable.column(item) > MAX_ROOMMATES + 1 and inJkGrTable.column(item) != MAX_ROOMMATES + MAX_PREF_LIST_LENGTH + 2 )]
                    if len(matchList) == 1:
                        if matchList[0].text().isnumeric():
                            if int(matchList[0].text()) > 0:
                                matchList[0].setBackground(normalColor)
                                matchList[0].setToolTip("")
                    else:
                        valid = False
                        for item in matchList:
                            if inJkGrTable.column(item) > MAX_ROOMMATES + 1 and inJkGrTable.column(item) != MAX_ROOMMATES + MAX_PREF_LIST_LENGTH + 2:
                                if item.text().isnumeric():
                                    if int(matchList[0].text()) > 0:
                                        item.setBackground(roomErrorColor)
                                        item.setToolTip("Occurs " +str(len(matchList)) + " times\nin preference list")
                        duplicateGroupRoomPrefError += 1.0/len(matchList)
                    
            elif column_count == MAX_ROOMMATES + MAX_PREF_LIST_LENGTH + 2:
                if not curItem.text().isnumeric():
                    valid = False
                    groupRoomAssignmentError += 1
                    curItem.setBackground(errorColor)
                    curItem.setToolTip("Must be positive integer")
                elif int(curItem.text()) < 0:
                    valid = False
                    groupRoomAssignmentError += 1
                    curItem.setBackground(errorColor)
                    curItem.setToolTip("Must be positive integer")
                else:
                    curItem.setBackground(normalColor)
                    curItem.setToolTip("")
                    
    if not valid:
        if roomNumberError > 0:
            errorMessage += ("<p>Non-Integer Room Numbers: " + str(roomNumberError) +"</p>")
        if duplicateRoomError > 0:
            errorMessage += ("<p>Duplicate Rooms: " + str(int(duplicateRoomError)) +"</p>")
        if roomTypeError > 0:
            errorMessage += ("<p>Invalid Room Types: " + str(roomTypeError) + "</p>")
        if roomSizeError > 0:
            errorMessage += ("<p>Invalid Room Sizes: " + str(roomSizeError) + "</p>")
        if roomAvaiError > 0:
            errorMessage += ("<p>Invalid Room Availability: " + str(roomAvaiError) + "</p>")
        if groupPointError > 0:
            errorMessage += ("<p>Invalid Group Points: " + str(groupPointError) + "</p>")
        if groupTypeError > 0:
            errorMessage += ("<p>Invalid Group Types: " + str(groupTypeError) + "</p>")
        if groupNameListError > 0:
            errorMessage += ("<p>Names listed as numbers: " + str(groupNameListError) + "</p>")
        if groupRoomPrefListError > 0:
            errorMessage += ("<p>Invalid Room Preferences: " + str(groupRoomPrefListError) + "</p>")
        if duplicateGroupRoomPrefError > 0:
            errorMessage += ("<p>Duplicated Rooms: " + str(int(duplicateGroupRoomPrefError)) +"</p>")
        if roomExistError > 0:
            errorMessage += ("<p>Requested Rooms Not on List: " + str(int(roomExistError)) + "</p>")
        if groupRoomAssignmentError > 0:
            errorMessage += ("<p>Invalid Room Assignments: " + str(groupRoomAssignmentError) + "</p>")
                                      
    inRmTable.blockSignals(False)
    inJkGrTable.blockSignals(False)
    return [valid, errorMessage] 

"""********
* OpenPrompt
***********
*
* Called when user tries to open files. Only supports import from Room Availability and Jack Group
*
********"""
class OpenPrompt(QDialog):
    def __init__(self, inRmAvTab, inJkGrTab, inOutputTab):
       
        super(OpenPrompt,self).__init__()
        self.openPrompt = loadUi('OpenPrompt.ui', self) #import xml File
        self.openPrompt.setWindowTitle("Import CSVs to Process")
        
        self.openPrompt.rmHeaderCheck.setChecked(ROOM_LIST_HASHEADER)
        self.openPrompt.grHeaderCheck.setChecked(GROUP_LIST_HASHEADER)
        self.openPrompt.rmButton.clicked.connect(self.getRoomFileDirectory)
        self.openPrompt.grButton.clicked.connect(self.getGroupFileDirectory)
        self.openPrompt.groupSizeIn.setValue(int(MAX_ROOMMATES))
        self.openPrompt.prefListSizeIn.setValue(int(MAX_PREF_LIST_LENGTH))
        self.openPrompt.maxPtsIn.setValue(float(MAX_POINTS))
        self.openPrompt.finImportButton.clicked.connect(self.checkData)
        
        self.openPrompt.setWindowIcon(QIcon('icon/open.png'))
        self.inRmAvTable = inRmAvTab
        self.inJkGrTable = inJkGrTab
        self.inOutputTable = inOutputTab
        
    """********
    *showOkMessage 
    ***********
    *
    * Given type of message, an icon name, error text, and title, display a dialog with simple
    * "ok" button to close
    *
    ********"""
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
        
        continueCheck = True
        errorMsg = ""
        #verify data are at least GENERALLY correct
        #    NOTE: No file data verification at this point
        if int(self.openPrompt.groupSizeIn.value()) <= 0:
            continueCheck = False
            errorMsg += "<p>Enter maximum jack group size larger than 0</p>"
        if int(self.openPrompt.prefListSizeIn.value()) <= 0:
            continueCheck = False
            errorMsg += "<p>Enter maximum room preference list length longer than 0</p>"
        if float(self.openPrompt.maxPtsIn.value()) < 0.0:
            continueCheck = False
            errorMsg += "<p>Enter max points as positive integer (0 if max doesn't matter)</p>"
        if self.openPrompt.rmDirectory.text() == "Please select file" or self.openPrompt.rmDirectory.text() == "Please select valid file":
            continueCheck = False
            errorMsg += "<p>Select CSV file for room availability list</p>"
        if self.openPrompt.grDirectory.text() == "Please select file" or self.openPrompt.grDirectory.text() == "Please select valid file":
            continueCheck = False
            errorMsg += "<p>Select CSV file for jack groups list</p>"
        #if no obvious errors with input, continue
        if not continueCheck:
            self.showOkMessage("critical", "error", errorMsg, "Import Error")
        else:
            #Set the Constant
            MAX_ROOMMATES = int(self.openPrompt.groupSizeIn.value())
            MAX_PREF_LIST_LENGTH = int(self.openPrompt.prefListSizeIn.value())
            MAX_POINTS = float(self.openPrompt.maxPtsIn.value())
            FILE_LOAD_LIST = [self.openPrompt.rmDirectory.text(), self.openPrompt.grDirectory.text()]
            GROUP_LIST_HASHEADER = (self.openPrompt.grHeaderCheck.checkState() == 2)
            ROOM_LIST_HASHEADER = (self.openPrompt.rmHeaderCheck.checkState() == 2)
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



                
if __name__ == '__main__':
    import sys
    
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())