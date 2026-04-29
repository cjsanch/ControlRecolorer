from core.MayaWidget import MayaWidget
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QLineEdit, QColorDialog, QWidget, QFrame
import maya.cmds as mc

import importlib
import core.MayaUtilities
importlib.reload(core.MayaUtilities)

#class that handles the color overide of the control curves
class ControlColorer:
    def __init__(self):
        self.controllerColorRGB = [0,0,0] #the initial color of the color selection, also where it is stored

    def SetColorOverride(self):
        selection = mc.ls(selection=True, ufe=True) #checks if there is currently a selection
        if not selection: #raises a warning if there is not a selection
            raise Exception("Please make a selection before applying the color override")
                     
        mc.editDisplayLayerMembers("defaultLayer", selection, noRecurse=True) #allows the color override to work even if the selected objects are in a display layer
        for item in selection:

            mc.setAttr(item + ".overrideEnabled", 1) #enables the color override for the selected objects
            mc.setAttr(item + ".overrideRGBColors", 1) #enables the use of RGB values for the color override

            mc.setAttr(item + ".overrideColorR", self.controllerColorRGB[0]) #sets the red value of the color override
            mc.setAttr(item + ".overrideColorG", self.controllerColorRGB[1]) #sets the green value of the color override
            mc.setAttr(item + ".overrideColorB", self.controllerColorRGB[2]) #sets the blue value of the color override

    def SetCurveWidth(self):
        selection = mc.ls(selection=True) #checks if there is currently a selection

        for obj in selection:
            shapes = mc.listRelatives(obj, shapes=True, fullPath=True) #gets the shape nodes of the selected objects

            for shape in shapes:
                if mc.nodeType(shape) == "nurbsCurve": #checks if the shape node is a nurbs curve
                    mc.setAttr(shape + ".lineWidth", self.lineWidth) #sets the line width of the nurbs curve to the value entered by the user

    def AddAttribute(self):
        selection = mc.ls(selection=True) #checks if there is currently a selection
        duplicateObjects = [] #list objects that already have the attribute
        for obj in selection:
            if mc.attributeQuery(self.nameBase, node=obj, exists=True): #checks if the attribute already exists on the object
                print(f"{obj} already has an attribute named {self.nameBase}") #print to console for debugging
                duplicateObjects.append(obj) #add the object to list of duplicates
                continue

            mc.addAttr(obj, longName=self.nameBase, attributeType="long", min=0, max=1, defaultValue=0, keyable=True) #adds the attribute to selected
        return duplicateObjects #returns the list of duplicate objects

    def SetLineWidth(self, newLineWidth):
        self.lineWidth = float (newLineWidth) #stores value of line width entered by the user
        self.lineWidth = max(0, min(self.lineWidth, 10)) #clamps the line width value between 0 and 10
        print(f"line width is set to: {self.lineWidth}") #prints to console for debugging

    def SetAttributeName(self, newAttributeName):
        self.nameBase = newAttributeName #stores the name entered by the user
        print(f"name base is set to: {self.nameBase}") #prints to console for debugging

class ControlColorerWidget(MayaWidget):
    def __init__(self):
        super().__init__() #initializes the parent widget
        self.setWindowTitle("Control Curve Tools") #sets the title of the window
        self.masterLayout = QVBoxLayout() #the main vertical layout for the widget
        self.infoLayout = QHBoxLayout() #the horizontal layout for the widget
        self.setLayout(self.masterLayout)  #assigns the layout to the widget
        self.resize(400,280)
        self.colorer = ControlColorer() #creates the instance of the control colorer class
        self.colorSelected = False #intial state of the button selection to check if a selection has been made before applying the color override
        self.widthSelected = False #^
        self.nameSelected = False #^^

        self.masterLayout.addWidget(QLabel("Select the curve(s) you want to modify, and then: ")) #the instructions that are displayed to the user

        self.infoLayout = QHBoxLayout() #horizontal input layout
        self.masterLayout.addLayout(self.infoLayout) #adds the horizontal layout to the main vertical layout
        self.infoLayout.addWidget(QLabel("Select a Base Color:")) #the label for the color selection button

        self.controlColorBtn = QPushButton("Select Color") #the button that opens the color selection dialog
        self.controlColorBtn.clicked.connect(self.controlColorBtnClicked) #connects the button to the color selection function
        self.infoLayout.addWidget (self.controlColorBtn) #adds the button to the layout

        self.applyColorBtn = QPushButton("Apply Color to Selected") #the button that applies the color override to the selected objects
        self.applyColorBtn.clicked.connect(self.setColorOverrideBtnClicked) #connects the button to the function that applies the color override
        self.masterLayout.addWidget (self.applyColorBtn) #adds the button to the layout

        self.line = QFrame() #horizontal line
        self.line.setFrameShape(QFrame.Shape.HLine) #sets shape of horizontal line
        self.line.setFrameShadow(QFrame.Shadow.Sunken) #sets shadow of horizontal line
        self.masterLayout.addWidget(self.line) #adds line to layout

        self.infoLayout = QHBoxLayout() #horizontal input layout
        self.masterLayout.addLayout(self.infoLayout) #adds the horizontal layout to the main vertical layout
        self.infoLayout.addWidget(QLabel("Choose line width:")) #the label for the color selection button
        #--------------------------------------------------------------------
        self.lineWidthEdit = QLineEdit() #text input box
        self.wdthValidator = QtGui.QIntValidator(0,10) #sets a validator that only allows values between 0 and 10 to be entered
        self.lineWidthEdit.setValidator(self.wdthValidator) #applies the validator to the text input box
        self.lineWidthEdit.setPlaceholderText ("Enter a number... (1-10)") #placeholder text that the user sees
        self.infoLayout.addWidget(self.lineWidthEdit) #adds to main layout
        self.setWidthBtn = QPushButton("Set Width") #the button that opens the color selection dialog
        self.setWidthBtn.clicked.connect(self.setWidthBtnClicked) #connects the button to the color selection function
        self.infoLayout.addWidget (self.setWidthBtn) #adds the button to the layout

        self.adjustWidthBtn = QPushButton("Adjust Width of Selected") #the button that applies the color override to the selected objects
        self.adjustWidthBtn.clicked.connect(self.adjustWidthBtnClicked) #connects the button to the function that applies the color override
        self.masterLayout.addWidget (self.adjustWidthBtn) #adds the button to the layout
        #--------------------------------------------------------------------
        self.line = QFrame() #horizontal line
        self.line.setFrameShape(QFrame.Shape.HLine) #sets shape of horizontal line
        self.line.setFrameShadow(QFrame.Shadow.Sunken) #sets shadow of horizontal line
        self.masterLayout.addWidget(self.line) #adds line to layout
        self.infoLayout = QHBoxLayout() #horizontal input layout
        self.masterLayout.addLayout(self.infoLayout) #adds the horizontal layout to the main vertical layout
        self.infoLayout.addWidget(QLabel("Choose attribute name:")) #the label for the color selection button
        #--------------------------------------------------------------------
        self.attributeNameEdit = QLineEdit() #text input box
        self.attributeNameEdit.setMaxLength(30) #the max length of characters that the user can enter
        self.attributeNameEdit.setPlaceholderText ("Enter a name...") #placeholder text that the user sees
        self.infoLayout.addWidget(self.attributeNameEdit) #adds to main layout
        self.setAttributeNameBtn = QPushButton("Set Name") #the button that opens the color selection dialog
        self.setAttributeNameBtn.clicked.connect(self.setNameBtnClicked) #connects the button to the color selection function
        self.infoLayout.addWidget (self.setAttributeNameBtn) #adds the button to the layout

        self.addAttributeBtn = QPushButton("Add Attribute to Selected") #the button that applies the color override to the selected objects
        self.addAttributeBtn.clicked.connect(self.addAttributeBtnClicked) #connects the button to the function that applies the color override
        self.masterLayout.addWidget (self.addAttributeBtn) #adds the button to the layout
        #--------------------------------------------------------------------

    def controlColorBtnClicked(self):
        pickedColor = QColorDialog().getColor() #opens the color selection dialog and stores the selected color
        self.colorer.controllerColorRGB[0] = pickedColor.redF() #stores the red value of the selected color
        self.colorer.controllerColorRGB[1] = pickedColor.greenF() #stores the green value of the selected color
        self.colorer.controllerColorRGB[2] = pickedColor.blueF() #stores the blue value of the selected color
        print(self.colorer.controllerColorRGB) #prints the selected colors RGB values to the console
        self.colorSelected = True #updates the state of the button selection to indicate that a color has been selected

    def setWidthBtnClicked(self):
        self.checkInputValue() #checks if the user has entered a value

        if self.widthSelected is True: #check if a value has been entered
            self.colorer.SetLineWidth(self.lineWidthEdit.text()) #calls the function to apply the width
        else:
            print("theres nothing")
            self.raiseNoWidthWarning() #raises a warning to the user to enter a value before applying the width change

    def adjustWidthBtnClicked(self):
        print("adjust width button click") #prints to console for debugging
        selection = mc.ls(selection=True, ufe=True)
        if not selection: #if there are no objects selected, raise a warning to the user 
            self.raiseSelectionWarning() #calls the selection warning function
            return

        if self.widthSelected is True:
            self.colorer.SetCurveWidth() #calls the function to apply the width change to the selected objects
        else:
            print("theres nothing") #prints to console for debugging
            self.raiseNoWidthWarning() #raises a warning to the user to enter a value before applying the width change

    def setNameBtnClicked(self):
        self.checkInputValueName() #checks if the user has entered a value

        if self.nameSelected is True:
            self.colorer.SetAttributeName(self.attributeNameEdit.text()) #calls the function to store the name entered by the user
        else:
            print("theres nothing")
            self.raiseNoNameWarning() #raises a warning to the user to enter a value before applying the attribute

    def addAttributeBtnClicked(self):
        print("add attribute button click")
        selection = mc.ls(selection=True, ufe=True)
        if not selection: #if there are no objects selected, raise a warning to the user 
            self.raiseSelectionWarning() #calls the selection warning function
            return

        if self.nameSelected is True:
            duplicateObjects = self.colorer.AddAttribute() #calls the function to add the attribute
            if duplicateObjects:
                self.raiseSameNameWarning() #raise a warning to the user
        else:
            print("theres nothing")
            self.raiseNoNameWarning() #raises a warning to the user to enter a value before applying the attribute
    
    def checkInputValue(self):
        if len(self.lineWidthEdit.text().strip()) > 0: #checks if the user has entered a value
            print("True, value entered", self.lineWidthEdit.text()) #prints to console for debugging
            self.widthSelected = True 
        else:
            print("False, no value entered") #prints to console for debugging

    def checkInputValueName(self): 
        if len(self.attributeNameEdit.text().strip()) > 0: #checks if the user has entered a value
            print("True, value entered", self.attributeNameEdit.text()) #prints to console for debugging
            self.nameSelected = True #updates the state of the button selection to indicate that a name has been entered
        else:
            print("False, no value entered") #prints to console for debugging

    def setColorOverrideBtnClicked(self):
        selection = mc.ls(selection=True, ufe=True)
        if not selection: #if there are no objects selected, raise a warning to the user 
            self.raiseSelectionWarning() #calls the selection warning function
            return
        
        if not self.colorSelected: #if no color has been selected, raise a warning to the user
            self.raiseColorWarning() #calls the color warning function
            return
        
        self.colorer.SetColorOverride() #calls the function to apply the color override to the selected objects

    def popupCloseBtnClicked(self):
        if hasattr(self, "popupWindow") and self.popupWindow: #if the popup window exists and is currently open, close it 
            self.popupWindow.close() #closes the window

    def raiseSelectionWarning(self):       
        self.popupWindow = QWidget() #creates a new window to display the warning message
        self.popupWindow.setWindowTitle("Warning") #titles the warning window
        self.popupWindow.setFixedSize(280,80) #sets the size of the warning window and makes it so the user cannot resize it
        self.popupLayout = QVBoxLayout() #creates a vertical layout for the warning window
        self.popupWindow.setLayout(self.popupLayout) #assigns the layout to the warning window

        self.popupInfoLabel = QLabel("Please make a selection before applying.") #the warning message that is displayed to the user
        self.popupLayout.addWidget(self.popupInfoLabel) #adds the warning message to the layout

        self.popupCloseBtn = QPushButton("Ok") #the button that the user clicks to close the warning window
        self.popupCloseBtn.clicked.connect(self.popupCloseBtnClicked) #connects the button to the function that closes the warning window
        self.popupLayout.addWidget(self.popupCloseBtn) #adds the button to the layout

        self.popupWindow.show() #displays the warning window to the user
        raise Exception("Please make a selection before applying the color override") #raises an exception to the console to show that an error has occurred

    def raiseColorWarning(self):       
        self.popupWindow = QWidget() #creates a new window to display the warning message
        self.popupWindow.setWindowTitle("Warning") #titles the warning window
        self.popupWindow.setFixedSize(280,80) #sets the size of the warning window and makes it so the user cannot resize it
        self.popupLayout = QVBoxLayout() #creates a vertical layout for the warning window
        self.popupWindow.setLayout(self.popupLayout) #assigns the layout to the warning window

        self.popupInfoLabel = QLabel("Please select a color before applying.") #the warning message that is displayed to the user
        self.popupLayout.addWidget(self.popupInfoLabel) #adds the warning message to the layout

        self.popupCloseBtn = QPushButton("Ok") #the button that the user clicks to close the warning window
        self.popupCloseBtn.clicked.connect(self.popupCloseBtnClicked) #connects the button to the function that closes the warning window
        self.popupLayout.addWidget(self.popupCloseBtn) #adds the button to the layout

        self.popupWindow.show() #displays the warning window to the user
        raise Exception("Please select a color before applying") #raises an exception to the console to show that an error has occurred
    
    def raiseNoWidthWarning(self):       
        self.popupWindow = QWidget() #creates a new window to display the warning message
        self.popupWindow.setWindowTitle("Warning") #titles the warning window
        self.popupWindow.setFixedSize(280,80) #sets the size of the warning window and makes it so the user cannot resize it
        self.popupLayout = QVBoxLayout() #creates a vertical layout for the warning window
        self.popupWindow.setLayout(self.popupLayout) #assigns the layout to the warning window

        self.popupInfoLabel = QLabel("Please enter and set a value, then adjust width.") #the warning message that is displayed to the user
        self.popupLayout.addWidget(self.popupInfoLabel) #adds the warning message to the layout

        self.popupCloseBtn = QPushButton("Ok") #the button that the user clicks to close the warning window
        self.popupCloseBtn.clicked.connect(self.popupCloseBtnClicked) #connects the button to the function that closes the warning window
        self.popupLayout.addWidget(self.popupCloseBtn) #adds the button to the layout

        self.popupWindow.show() #displays the warning window to the user
        raise Exception("Please enter and set a value, then adjust width.") #raises an exception to the console to show that an error has occurred

    def raiseNoNameWarning(self):       
        self.popupWindow = QWidget() #creates a new window to display the warning message
        self.popupWindow.setWindowTitle("Warning") #titles the warning window
        self.popupWindow.setFixedSize(280,80) #sets the size of the warning window and makes it so the user cannot resize it
        self.popupLayout = QVBoxLayout() #creates a vertical layout for the warning window
        self.popupWindow.setLayout(self.popupLayout) #assigns the layout to the warning window

        self.popupInfoLabel = QLabel("Please enter and set a name, then apply.") #the warning message that is displayed to the user
        self.popupLayout.addWidget(self.popupInfoLabel) #adds the warning message to the layout

        self.popupCloseBtn = QPushButton("Ok") #the button that the user clicks to close the warning window
        self.popupCloseBtn.clicked.connect(self.popupCloseBtnClicked) #connects the button to the function that closes the warning window
        self.popupLayout.addWidget(self.popupCloseBtn) #adds the button to the layout

        self.popupWindow.show() #displays the warning window to the user
        raise Exception("Please enter and set a name, then apply.") #raises an exception to the console to show that an error has occurred

    def raiseSameNameWarning(self):       
        self.popupWindow = QWidget() #creates a new window to display the warning message
        self.popupWindow.setWindowTitle("Warning") #titles the warning window
        self.popupWindow.setFixedSize(280,80) #sets the size of the warning window and makes it so the user cannot resize it
        self.popupLayout = QVBoxLayout() #creates a vertical layout for the warning window
        self.popupWindow.setLayout(self.popupLayout) #assigns the layout to the warning window

        self.popupInfoLabel = QLabel("An attribute with that name already exists.") #the warning message that is displayed to the user
        self.popupLayout.addWidget(self.popupInfoLabel) #adds the warning message to the layout

        self.popupCloseBtn = QPushButton("Ok") #the button that the user clicks to close the warning window
        self.popupCloseBtn.clicked.connect(self.popupCloseBtnClicked) #connects the button to the function that closes the warning window
        self.popupLayout.addWidget(self.popupCloseBtn) #adds the button to the layout

        self.popupWindow.show() #displays the warning window to the user
        raise Exception("An attribute with that name already exists.") #raises an exception to the console to show that an error has occurred

    def getWidgetHash(self):
        return "3923fcd8bf8e146af389a6de3aff0f88f88663498ae29837e621n3ben923f8"  #returns the unique identifier

def Run():
        controlColorerWidget = ControlColorerWidget() #creates the widget instance
        controlColorerWidget.show() #displays the widget to the user

Run() #runs the tool