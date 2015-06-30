#!/usr/bin/python
# -*- coding: utf-8 -*-

#For keylogging
from fetch_keys import *

#For searching from DiMe 
from dime_search import *

#For GUI
from PyQt4 import QtCore, QtGui, uic
#
from PyQt4.QtGui import *
from PyQt4.QtCore import *

#Includes the definition of clickable label
import ExtendedQLabel

#
import re


# Definition of GUI
class WindowClass(QtGui.QMainWindow):
#class WindowClass(QtGui.QWidget):
    
    def __init__(self):
      super(WindowClass, self).__init__()

      #Set the window title
      self.setWindowTitle('Proactive Search')

      #Always on top
      self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

      #Create menubar
      menubar = self.menuBar()
      filemenu = menubar.addMenu('&File')
      filemenu.addAction('Quit', self.quitting)

      #Quit button
      self.quitbutton = QtGui.QPushButton("Quit",self)
      self.quitbutton.resize(40,20)
      self.quitbutton.clicked.connect(self.quitting)
      self.quitbutton.move(270,7)

      #Stop/Start button
      ssbuttonstr = "Stop logging"
      self.ssbutton = QtGui.QPushButton(ssbuttonstr,self)
      self.ssbutton.setStyleSheet("color: red")
      self.ssbutton.resize(90,20)
      self.ssbutton.clicked.connect(self.stopstart)
      self.ssbutton.move(10,7)

      #Set color of labels
      palette = QtGui.QPalette()
      palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.darkGreen)

      #Create QGroupbox
      self.mygroupbox = QtGui.QGroupBox()
      #Create layout
      self.myform = QtGui.QFormLayout()
      #Add self.myform to self.mygroupbox layout
      self.mygroupbox.setLayout(self.myform)

      #Make labellist
      self.labellist = []

      #Create status label    
      self.statuslabel = QtGui.QLabel("Logging ongoing")
      self.statuslabel.setStyleSheet("color: darkGreen")
      self.myform.addRow(self.statuslabel)

      #Create infolabel    
      self.infolabel = QtGui.QLabel("Links to suggested resources:")
      self.myform.addRow(self.infolabel)

      #Make clickable labels
      for i in range(5):
        #
        dumlabel = ExtendedQLabel.ExtendedQLabel("", self)
	dumlabel.connect(dumlabel, SIGNAL('clicked()'), dumlabel.open_url)
	dumlabel.setPalette(palette)
	#Add to label list
	self.labellist.append(dumlabel) 
	#
	self.myform.addRow(self.labellist[i])

      #Create scrollbar area
      self.scrollArea = QtGui.QScrollArea(self)
      self.scrollArea.setWidget(self.mygroupbox)
      self.scrollArea.setWidgetResizable(True)
      self.scrollArea.setFixedHeight(200)
      self.scrollArea.setFixedWidth(300)
      self.scrollArea.move(10,30)
      
      #
      self.setGeometry(0, 0, 320, 240)

      #Get the current path
      self.pathstr = os.path.dirname(os.path.realpath(sys.argv[0]))

      #Read user.ini file
      self.username, self.password, self.time_interval, self.nspaces = self.read_user_ini()

      #Initial time
      self.cdate          = str(datetime.datetime.now().date())
      self.time           = str(datetime.datetime.now().time())
      #
      self.done           = False
      #
      self.sleep_interval = 1.005

    def startlog(self):
        threading.Thread(target = log, args = (self,) ).start()

    def show_link(self):
	threading.Thread(target = update_visible_link, args = (self,)).start()

    def update_links(self, urlstr):
        #pass
        i = 0
        #sleep(2.0)
        #for i in len(r.json())
        if urlstr != None:
		nsuggestedlinks = len(urlstr.json())
		nlinks          = len(self.labellist) 
		if nsuggestedlinks <= nlinks:
	                for i in range( len(urlstr.json()) ):
        	                        linkstr = str( urlstr.json()[i]["uri"] )
                	                self.labellist[i].setText(linkstr)
                        	        plaintext    = urlstr.json()[i]["plainTextContent"]
                                	tooltipstr   = re.sub("[^\w]", " ", plaintext)
	                                self.labellist[i].setToolTip(tooltipstr[0:120])


    def read_user_ini(self):

        f          = open('user.ini','r')
        dumstr     = f.read()
        stringlist = dumstr.split()

        for i in range( len(stringlist) ):
                if stringlist[i] == "usrname:":
                        usrname = stringlist[i+1]
                if stringlist[i] == "password:":
                        password = stringlist[i+1]
                if stringlist[i] == "time_interval:":
                        time_interval_string = stringlist[i+1]
                        time_interval = float(time_interval_string)
                if stringlist[i] == "nspaces:":
                        nspaces_string = stringlist[i+1]
                        nspaces = int(nspaces_string)

        return usrname, password, time_interval, nspaces

    #
    def open_url(self):
      global urlstr
      webbrowser.open(urlstr)

    #
    def stopstart(self):
      global var

      if var == True:
	      var = False
	      self.ssbutton.setText("Start logging")
	      self.ssbutton.setStyleSheet("background-color: lightGreen")
	      self.statuslabel.setText("Logging disabled")
	      self.statuslabel.setStyleSheet("color: red")
      elif var == False:
	      var = True
	      self.ssbutton.setText("Stop logging")
	      self.ssbutton.setStyleSheet("color: red")
	      self.statuslabel.setText("Logging ongoing")
	      self.statuslabel.setStyleSheet("color: green")
	      #self.statuslabel.setStyleSheet("background-color: lightRed")
              self.startlog()

    def quitting(self):
      global var
      var = False
      QtCore.QCoreApplication.instance().quit()

    #Quit
    def closeEvent(self, event):
        self.quitting()


################################################################

###
def log(win):

      #global urlstr
      global var

      countspaces = 0
      sleep_interval = 0.005
      timeinterval = 10

      #starttime = datetime.datetime.now().time().second
      now = time()
      flag = 0
      flag2= 0
      dumstr = ''
      wordlist = []
      #Show the links of suggested resources in the window
      #update_kurllabel2(self)

      #f = open('typedwords.txt', 'a')
      while var:

        sleep(sleep_interval)
        changed, modifiers, keys = fetch_keys()
        keys  = str(keys)


        #Take current time
        cdate = datetime.datetime.now().date()
        ctime = datetime.datetime.now().time()

        cmachtime = time()
        var2 = cmachtime > now + win.time_interval

        if keys == 'None':
                keys = ''

        elif keys == '<backspace>':
                keys = ''
                #Convert current string into list of characters
                duml = list(dumstr)
                if len(duml) > 0:
                        #Delete the last character from the list
                        del( duml[len(duml)-1] )
                        #Convert back to string
                        dumstr = "".join(duml)

        elif keys in ['<enter>', '<tab>','<right ctrl>','<left ctrl>'," "]:

                #keys = ' '
                wordlist.append(dumstr)
                #dumstr = dumstr + keys
                countspaces = countspaces + 1
                dumstr = ''

                if var2:
                        #
                        dumstr2 = ''
                        for i in range( len(wordlist) ):
                               dumstr2 = dumstr2 + wordlist[i] + ' '

                        #
                        f = open("typedwords.txt","a")
                        f.write(str(cdate) + ' ' + str(ctime) + ' ' + dumstr2 + '\n')
                        f.close()

                        #Make query to DiMe
                        urlstr = search_dime(win.username, win.password, dumstr2)
                        #Update visible links
                        win.update_links(urlstr)

                        #Add the suggested url into a history file
                        if urlstr != None:
                                f2 = open("suggested_pages.txt","a")
                                f2.write(str(cdate) + ' ' + str(ctime) + ' ' + str(urlstr.json()[0]["uri"]) + '\n')
                                f2.close()

                        #Clear the dummy string
                        dumstr = ''
                        dumstr2= ''

                        #Remove content from wordlist
                        del wordlist[:]

                        countspaces = 0

                        flag = 1
                        flag2= 0

                        now = time()

        else:
                cdate = datetime.datetime.now().date()
                ctime = datetime.datetime.now().time()
                dumstr = dumstr + keys

####################################################################


if __name__ == "__main__":

  #Important global variables!
  global urlstr
  #Initialize urlstr
  urlstr = search_dime("petrihiit","p3tr1h11t","python")

  global var
  var = True

  #Make the QGui.QApplication object
  app = QtGui.QApplication(sys.argv)
  #Set Taskbar icon for app object
  app.setWindowIcon(QtGui.QIcon('keyboard.png'))

  #Get screen dimensions
  screen = app.desktop()
  sl = screen.width()
  sh = screen.height()

  #Make a WindowClass object
  newwindow = WindowClass()
  newwindow.show()

  #Move the window into the right corner
  newwindow.move(sl-350,0)

  #Start keylogger
  newwindow.startlog()

  #Start
  app.exec_()
