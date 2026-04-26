from core.MayaWidget import MayaWidget
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QLineEdit, QColorDialog, QWidget
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

class ControlColorerWidget(MayaWidget):
    def __init__(self):
        super().__init__() #initializes the parent widget
        self.setWindowTitle("Control Curve Recolorer") #sets the title of the window
        self.masterLayout = QVBoxLayout() #the main vertical layout for the widget
        self.infoLayout = QHBoxLayout() #the horizontal layout for the widget
        self.setLayout(self.masterLayout)  #assigns the layout to the widget
        self.colorer = ControlColorer() #creates the instance of the control colorer class
        self.colorSelected = False #intial state of the button selection to check if a selection has been made before applying the color override

        self.masterLayout.addWidget(QLabel("Select the curve(s) you want to recolor, and then: ")) #the instructions that are displayed to the user

        self.infoLayout = QHBoxLayout() #horizontal input layout
        self.masterLayout.addLayout(self.infoLayout) #adds the horizontal layout to the main vertical layout
        self.infoLayout.addWidget(QLabel("Select a Base Color:")) #the label for the color selection button

        self.controlColorBtn = QPushButton("Select Color") #the button that opens the color selection dialog
        self.controlColorBtn.clicked.connect(self.controlColorBtnClicked) #connects the button to the color selection function
        self.infoLayout.addWidget (self.controlColorBtn) #adds the button to the layout

        self.controlColorBtn = QPushButton("Apply Color to Selected") #the button that applies the color override to the selected objects
        self.controlColorBtn.clicked.connect(self.setColorOverrideBtnClicked) #connects the button to the function that applies the color override
        self.masterLayout.addWidget (self.controlColorBtn) #adds the button to the layout

    def controlColorBtnClicked(self):
        pickedColor = QColorDialog().getColor() #opens the color selection dialog and stores the selected color
        self.colorer.controllerColorRGB[0] = pickedColor.redF() #stores the red value of the selected color
        self.colorer.controllerColorRGB[1] = pickedColor.greenF() #stores the green value of the selected color
        self.colorer.controllerColorRGB[2] = pickedColor.blueF() #stores the blue value of the selected color
        print(self.colorer.controllerColorRGB) #prints the selected colors RGB values to the console
        self.colorSelected = True #updates the state of the button selection to indicate that a color has been selected

    def setColorOverrideBtnClicked(self):
        selection = mc.ls(selection=True, ufe=True)
        if not selection: #if there are no objects selected, raise a warning to the user 
            self.raiseSelectionWarning() #calls the selection warning function
            return
        
        if not self.colorSelected: #if no color has been selected, raise a warning to the user
            self.raiseColorWarning()
            return
        
        self.colorer.SetColorOverride() #calls the function to apply the color override to the selected objects

    def raiseSelectionWarning(self):       
        self.popupWindow = QWidget() #creates a new window to display the warning message
        self.popupWindow.setWindowTitle("Warning") #titles the warning window
        self.popupWindow.setFixedSize(250,80) #sets the size of the warning window and makes it so the user cannot resize it
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
        self.popupWindow.setFixedSize(250,80) #sets the size of the warning window and makes it so the user cannot resize it
        self.popupLayout = QVBoxLayout() #creates a vertical layout for the warning window
        self.popupWindow.setLayout(self.popupLayout) #assigns the layout to the warning window

        self.popupInfoLabel = QLabel("Please select a color before applying.") #the warning message that is displayed to the user
        self.popupLayout.addWidget(self.popupInfoLabel) #adds the warning message to the layout

        self.popupCloseBtn = QPushButton("Ok") #the button that the user clicks to close the warning window
        self.popupCloseBtn.clicked.connect(self.popupCloseBtnClicked) #connects the button to the function that closes the warning window
        self.popupLayout.addWidget(self.popupCloseBtn) #adds the button to the layout

        self.popupWindow.show() #displays the warning window to the user
        raise Exception("Please select a color before applying") #raises an exception to the console to show that an error has occurred
    
    def popupCloseBtnClicked(self):
        if hasattr(self, "popupWindow") and self.popupWindow: #if the popup window exists and is currently open, close it 
            self.popupWindow.close() #closes the window
                    
    def getWidgetHash(self):
        return "3923fcd8bf8e146af389a6de3aff0f88f88663498ae29837e621n3ben923f8"  #returns the unique identifier

def Run():
        controlColorerWidget = ControlColorerWidget() #creates the widget instance
        controlColorerWidget.show() #displays the widget to the user

Run() #runs the tool