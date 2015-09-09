from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QLabel
import sys

from PyQt5 import QtCore, QtGui, uic

# For opening links
import webbrowser


#Clickable QLabel
class ExtendedQLabel(QLabel):
#class ExtendedQLabel(QtGui.QLabel):

    def __init__(self):
    #def __init(self, parent):
	#super(ExtendedQLabel, self).__init__()
        #QLabel.__init__(self, parent)
        #Initialize ExtendedQLabel as a QLabel object
        QLabel.__init__(self, 'Test')
        #Set color of labels
        self.palette = QtGui.QPalette()
        self.setPalette(self.palette)
        self.palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.darkBlue)

        #print self.text()
    	self.uristr = str(self.text())
    	self.setMouseTracking(True)

    	#Set tooltip functionality
    	#self.setToolTip("Abstract2")	

		#self.setToolTip('')
		#self.

    def mouseReleaseEvent(self, ev):
        self.emit(SIGNAL('clicked()'))

#    def mouse_over_event(self, ev):
#	self.emit(SIGNAL('Mouse_over()'))

    def open_url(self):
		dumstr = str(self.uristr)    	
		#dumstr = str(self.text())
		webbrowser.open(dumstr)
