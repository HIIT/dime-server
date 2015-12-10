#!/usr/local/lib/python2.7
# -*- coding: utf-8 -*-

#import sys, time
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# For Keylogger
import sys
import datetime #For import date and time
from time import sleep, time, strftime, localtime
import ctypes as ct
from ctypes.util import find_library

import os
#import queue
import threading

import argparse

#For updating data and other files (dictionary, Document term matrices etc.)
from update_files import *

from dime_search2 import *

#Includes the definition of clickable label
#from ExtendedQLabel import *

#For getting web page title
#import lxml.html
#import urllib.request, urllib.error, urllib.parse
#from BeautifulSoup import BeautifulSoup

#
import webbrowser

#
import re

#
import math

#For checking data types
import types

#Animation for processing
#from simple_animation import *
#from not_so_simple_animation import *

#Import loggerthread
if sys.platform == "linux":
  from loggerthread_linux import *
elif sys.platform == "darwin":
  from loggerthread_osx import *
else:
  print("Unsupported platform")
  sys.exit()

#Import search thread
#from searchthread import *
from test_searchthread import *

################################################################

# linux only!
# assert("linux" in sys.platform)

class MainWindow(QMainWindow):
  def __init__(self):
    super(MainWindow, self).__init__(parent, Qt.WindowStaysOnTopHint)
    #
    self.main_widget = MyApp()
    #
    self.setCentralWidget(self.main_widget)
    #
    self.show()


class MyListWidget(QListWidget):

    itemDoubleClicked = pyqtSignal('QListWidgetItem')

    def __init__(self, parent=None):
        super(MyListWidget, self).__init__(parent)

    def mousePressEvent(self, event):
        button = event.button()
        # print("mousePressEvent", button)
        print("mousePressEvent", event)
        item = self.itemAt(event.pos())
        print(item)
        if item is not None and button == 2:
            self.itemDoubleClicked.emit(item)
        super(MyListWidget, self).mousePressEvent(event)


class MyQLineEdit(QLineEdit):

    explicitQueryFieldClicked = pyqtSignal()

    def __init__(self, parent=None):
        super(MyQLineEdit, self).__init__(parent)
        self.setFixedWidth(300)
        
    def mousePressEvent(self, event):

        button = event.button()
        print("mousePressEvent", button)
        #item = self.itemAt(event.pos())
        #if item is not None and button == 2:
        self.explicitQueryFieldClicked.emit()
        #super(MyListWidget, self).mousePressEvent(event)




class MyApp(QWidget):
#class MyApp(QMainWindow):

 finished = pyqtSignal(int)
 update = pyqtSignal(str)
 do_old_query = pyqtSignal(list)

 #Signal for sending old written string to logger thread
 send_old_dumstring = pyqtSignal(str)

 #Signal for sending explicit search string
 send_explicit_search_query = pyqtSignal(str)

 def __init__(self, parent=None):
  QWidget.__init__(self, parent)
  #QMainWindow.__init__(self, parent)
  #widget = QWidget(self)
  #self.setCentralWidget(widget)

  #Variable for counting iteration
  self.iteration_index = 0
  
  #Read user.ini file
  self.srvurl, self.username, self.password, self.time_interval, self.nspaces, self.nwords, self.updateinterval, self.data_update_interval, self.nokeypress_interval, self.mu, self.n_results = read_user_ini()
  #self.data = []
  self.keywords = []
  self.list_of_lists_of_old_keywords = []
  self.old_queries = []

  #List of documents checked as useful by the user
  self.useful_docs = {}

  #Index for current element in history list
  self.hist_ind = 0
  #Animation objects
  # self.anim1 = MyView()
  # self.anim1.scale(0.3,0.3)
  # self.anim1.setStyleSheet("border: 0px; background-color: transparent")
  # self.anim1.show() 
  

  self.animlabel = QLabel()
  self.animation = QMovie("images-loader.gif")
  self.animlabel.setMovie(self.animation)
  # self.anim1 = Overlay(self)
  # #self.anim1.scale(0.5,0.5)
  # self.anim1.setStyleSheet("border: 0px; background-color: transparent")
  # self.anim1.hide()

  #self.startStopButton.clicked.connect(self.anim1.tl.start)
  #self.overlay.resize(event.size())

  #Create data files
  check_update()

  #Create  thread objects
  self.LoggerThreadObj  = LoggerThread()
  self.SearchThreadObj = SearchThread()

  #Set parameter values for the search thread
  self.SearchThreadObj.emphasize_kws = args.emphasize_kws
  self.SearchThreadObj.c = args.c
  self.SearchThreadObj.mmr_lambda = args.mmr
  if args.solr:
    self.SearchThreadObj.servertype = "both"
  elif args.solronly:
    self.SearchThreadObj.servertype = "solr"

  #Data connection from logger thread to search thread
  if not args.only_explicit_search:
    self.LoggerThreadObj.update.connect(self.SearchThreadObj.get_new_word)
    self.LoggerThreadObj.update.connect(self.log_new_word)

  #Data connections from search thread to main thread
  self.SearchThreadObj.send_links.connect(self.get_data_from_search_thread_and_update_visible_stuff)
  self.SearchThreadObj.send_keywords.connect(self.get_keywords_from_search_thread_and_update_visible_stuff)
  self.SearchThreadObj.send_query_string_and_corresponding_relevance_vector.connect(self.get_query_string_from_search_thread)  

  self.SearchThreadObj.start_search.connect(self.start_animation)
  self.SearchThreadObj.all_done.connect(self.stop_animation)

  #Data connections via signals from main thread to search and logger thread 
  self.finished.connect(self.SearchThreadObj.change_search_function)
  self.update.connect(self.SearchThreadObj.get_new_word_from_main_thread)
  self.do_old_query.connect(self.SearchThreadObj.get_old_query_from_main_thread)
  self.send_explicit_search_query.connect(self.SearchThreadObj.get_explicit_query_from_main_thread)
  self.send_explicit_search_query.connect(self.LoggerThreadObj.insert_old_dumstring)
  self.send_old_dumstring.connect(self.LoggerThreadObj.insert_old_dumstring)
  self.send_old_dumstring.connect(self.log_new_word)

  #Create visible stuff
  val = 5
  self.iconfile1 = 'web.png'
  self.gbtitle = QLabel('Web sites')
  self.listWidget1 = self.create_QListWidget(20, self.iconfile1)
  # self.gbtitle.hide()
  # self.listWidget1.hide()

  #self.iconfile2 = 'mail.png'
  self.iconfile3 = 'doc.png'
  self.gbtitle2 = QLabel('Read documents')
  self.listWidget2 = self.create_QListWidget(20, self.iconfile3)
  self.listWidget2.verticalScrollBar().sliderReleased.connect(self.rdwslider_released)

  self.gbtitle3 = QLabel('External documents')
  self.listWidget3 = self.create_QListWidget(20, self.iconfile3)
  self.listWidget3.verticalScrollBar().sliderReleased.connect(self.edwslider_released)

  #List of useful docs
  self.useful_docs_title = QLabel('Found documents [0]')
  self.useful_docs_listWidget = self.create_QListWidget(0, self.iconfile3)
  #self.useful_docs_listWidget.setFixedHeight(120)

  #Buttons
  #Start button
  self.startStopButton  = QPushButton("Stop")
  #self.connect(self.startStopButton, QtCore.SIGNAL("released()"), self.test_pressed)
  self.startStopButton.released.connect(self.start_stop_keylogger)
  self.startStopButton.released.connect(self.log_startstopbutton)
  #
  #self.stopButton  = QPushButton("Stop")
  #self.stopButton.released.connect(self.stop_keylogger)

  #Button for deleting keyword history
  self.clearButton  = QPushButton("Clear")
  self.clearButton.setToolTip("Clears the keyword history")
  #
  self.clearButton.released.connect(self.clear_kw_history)
  self.clearButton.released.connect(self.disable_buttons)
  self.clearButton.released.connect(self.hide_lists)
  self.clearButton.released.connect(self.SearchThreadObj.clear_query_string)
  self.clearButton.released.connect(self.LoggerThreadObj.clear_dumstring)
  self.clearButton.released.connect(self.log_clearbutton)

  #Button for getting previous keywords and search results
  self.backButton  = QPushButton("<-")
  self.backButton.setToolTip("Back in history")
  self.backButton.setEnabled(False)
  self.forwardButton  = QPushButton("->")
  self.forwardButton.setToolTip("Forward in history")
  self.forwardButton.setEnabled(False)
  #
  self.backButton.released.connect(self.repeat_old_query)
  self.backButton.released.connect(self.log_backbutton)
  self.forwardButton.released.connect(self.repeat_old_query)
  self.forwardButton.released.connect(self.log_forwardbutton)

  #Text field for explicit queries
  self.explicit_query_field = MyQLineEdit()
  self.explicit_query_field.explicitQueryFieldClicked.connect(self.only_stop_keylogger)
  self.explicit_query_field.returnPressed.connect(self.emit_explicit_search)

  #Add search button for explicit search
  self.explicit_query_button = QPushButton("Search!")
  self.explicit_query_button.clicked.connect(self.emit_explicit_search)

  #self.explicit_query_button.connect(self.emit_explicit_query)
  
  #self.clearButton.setGeometry(1,1,1,1)
  #self.clearButton.setFixedWidth(60)
  #self.clearButton.setFixedHeight(20)

  #
  #self.startStopButton.setDisabled(True)
  #self.stopButton.setDisabled(False)   
  self.LoggerThreadObj.start()
  self.SearchThreadObj.start()

  #Slider for exploitation/exploration slider
  #self.eeslider    = QSlider(Qt.Horizontal)
  self.eeslider    = QSlider(Qt.Vertical)
  self.eeslider.setRange(0,200)
  self.eeslider.setTickInterval(200)
  #self.eeslider.setFocusPolicy(QtCore.Qt.NoFocus)
  #self.connect(self.eeslider, QtCore.SIGNAL("valueChanged(int)"),self.change_c)
  self.eeslider.valueChanged.connect(self.SearchThreadObj.recompute_keywords)
  self.eesliderl1  = QLabel("Exploit")
  self.eesliderl2  = QLabel("Explore")

  #Radio buttons for choosing search function
  self.radiobutton1= QRadioButton("DocSim")
  self.radiobutton1.released.connect(self.choose_search_function1)

  self.radiobutton2= QRadioButton("LinRel + DiMe search")
  self.radiobutton2.released.connect(self.choose_search_function2)
  self.radiobutton2.click()

  self.radiobutton3= QRadioButton("LinRel (omitting history)")
  self.radiobutton3.released.connect(self.choose_search_function3)

  self.radiobutton4= QRadioButton("LinRel + DocSim")
  self.radiobutton4.released.connect(self.choose_search_function4)

  #
  self.buttonlist = []

  #


  #Layout for Web Pages
  self.vlayout1 = QVBoxLayout()
  self.vlayout1.addWidget(self.gbtitle)
  self.vlayout1.addWidget(self.listWidget1)
  #
  self.vlayout2w = QWidget()
  self.vlayout2 = QVBoxLayout()
  self.vlayout2.setContentsMargins(0,0,0,2)
  self.vlayout2.addWidget(self.gbtitle2)
  self.vlayout2.addWidget(self.listWidget2)
  self.vlayout2w.setLayout(self.vlayout2)
  #
  self.vlayout3w = QWidget()
  self.vlayout3 = QVBoxLayout()
  self.vlayout3.setContentsMargins(0,3,0,2)
  self.vlayout3.addWidget(self.gbtitle3)
  self.vlayout3.addWidget(self.listWidget3)
  self.vlayout3w.setLayout(self.vlayout3)
  #
  self.vlayout6w = QWidget()
  self.vlayout6 = QVBoxLayout()
  self.vlayout6.setContentsMargins(0,3,0,2)
  self.vlayout6.addWidget(self.useful_docs_title)
  self.vlayout6.addWidget(self.useful_docs_listWidget)
  self.vlayout6w.setLayout(self.vlayout6)

  #
  self.vlayout4 = QVBoxLayout()
  self.vlayout4.setSpacing(5)
  self.vlayout4.setAlignment(Qt.AlignCenter)
  #self.vlayout4.addWidget(QLabel(' '))
  #self.subvlayout= QVBoxLayout()
  #self.subvlayout.addWidget(self.startStopButton)
  #self.subvlayout.addWidget(self.clearButton)
  #self.subhlayout.addWidget(self.anim1)
  #self.subvlayout.addWidget(self.animlabel)
  #self.movie.start()


  #self.vlayout4.addWidget(self.startStopButton)
  #self.vlayout4.addWidget(self.clearButton)



  #self.vlayout4.addLayout(self.smallhlayout)

  self.vlayout4.addStretch()
  self.vlayout4.addWidget(self.animlabel)
  self.animlabel.setAlignment(Qt.AlignCenter)
  self.animlabel.setFixedWidth(50)
  self.vlayout4.addStretch()

  #self.vlayout4.itemAt(3).setAlignment(Qt.AlignCenter)
  #self.movie.start()

  #self.vlayout4.addLayout(self.subvlayout)
  #self.vlayout4.addWidget(self.clearButton)

  #self.subhlayout2= QHBoxLayout()
  #self.vlayout4.addWidget(self.eesliderl2)
  #self.vlayout4.addWidget(self.eeslider)
  #self.vlayout4.addWidget(self.eesliderl1)
  #Align the slider to center
  #self.vlayout4.itemAt(2).setAlignment(Qt.AlignCenter)
  #self.vlayout4.itemAt(3).setAlignment(Qt.AlignCenter)
  #self.vlayout4.itemAt(4).setAlignment(Qt.AlignCenter)

  #self.vlayout4.addLayout(self.subhlayout2)
  #vlayout5 is a sub layout for vlayout4
  self.vlayout5 = QVBoxLayout()
  self.vlayout5.setSpacing(5)
  self.vlayout5.setAlignment(Qt.AlignCenter)
  if not args.only_explicit_search:
    self.vlayout5.addWidget(self.eesliderl2)
    self.vlayout5.addWidget(self.eeslider)
    self.vlayout5.addWidget(self.eesliderl1)
    self.vlayout5.itemAt(0).setAlignment(Qt.AlignCenter)
    self.vlayout5.itemAt(1).setAlignment(Qt.AlignCenter)
    self.vlayout5.itemAt(2).setAlignment(Qt.AlignCenter)
  #self.vlayout5.addWidget(self.radiobutton1)
  #self.vlayout5.addWidget(self.radiobutton2)
  #self.vlayout5.addWidget(self.radiobutton3)
  #self.vlayout5.addWidget(self.radiobutton4)

  #Groupbox for radiobuttons
  # self.mygroupbox = QGroupBox('Search Method')
  # self.mygroupbox.setLayout(self.vlayout5)
  # self.vlayout4.addWidget(self.mygroupbox)

  #Add layouts
  #self.hlayout = QHBoxLayout()

  #self.hlayout.addLayout(self.vlayout1)

  #self.hlayout.addLayout(self.vlayout4)
  #self.hlayout.addLayout(self.vlayout5)

  #Master vertical layout:
  self.mastermaterhlayout = QHBoxLayout(self)
  self.mastervlayout = QVBoxLayout()

  #Create layout for back/forward, search field, and search button
  self.smallhlayout = QHBoxLayout()
  if not args.only_explicit_search:
    self.smallhlayout.addWidget(self.backButton)
    self.smallhlayout.addWidget(self.forwardButton)  
    self.smallhlayout.addWidget(self.clearButton)
    self.smallhlayout.addWidget(self.startStopButton)

  #
  self.smallhlayout.addStretch()
  self.smallhlayout.addWidget(self.animlabel)
  self.animlabel.setAlignment(Qt.AlignCenter)
  self.smallhlayout.addStretch()

  #self.explicit_query_layout = QHBoxLayout()
  #self.explicit_query_layout.addLayout(self.smallhlayout)
  self.smallhlayout.addWidget(self.explicit_query_field)
  self.smallhlayout.addWidget(self.explicit_query_button)

  self.mastervlayout.addLayout(self.smallhlayout)
  #self.mastervlayout.addLayout(self.explicit_query_layout)

  self.splitter = QSplitter(Qt.Vertical)
  self.splitter.setHandleWidth(1)
  #Add self.hlayout to self.mastervlayout
  if not args.solronly:
    self.splitter.addWidget(self.vlayout2w)

  if args.solr or args.solronly:
    self.splitter.addWidget(self.vlayout3w)

  self.splitter.addWidget(self.vlayout6w)

  self.mastervlayout.addWidget(self.splitter)

  #self.mastervlayout.addLayout(self.hlayout)
  #
  #self.hlayout2 = QHBoxLayout()
  #self.keywordlabel = QLabel('Suggested keywords: ')
  #self.keywordlabel.setStyleSheet('color: green')
  #self.hlayout2.addWidget(self.keywordlabel)

  #Horizontal layouts for keyword buttons
  self.hlayout3 = QHBoxLayout()
  #self.hlayout4 = QHBoxLayout()


  # #Create "previous" -button
  # self.previousbutton = QPushButton('<')
  # self.previousbutton.setHidden(True)
  # self.hlayout3.addWidget(self.previousbutton)
  # self.previousbutton.clicked.connect(self.show_previous_kw_buttons)


  #Create kw-buttons
  self.numofkwbuttons = 50
  self.buttonlist = self.create_buttonwidget_list(self.numofkwbuttons)
  #Set the buttons hidden
  # for i in range(len(self.buttonlist)):
  #   self.buttonlist[i].hide()

  #Create scroll area for buttons
  #self.scrollArea = self.create_horizontal_scroll_area_for_buttonwidget_list(self.buttonlist)
  self.scrollArea = self.create_vertical_scroll_area_for_buttonwidget_list(self.buttonlist)
    # self.scrollArea.hide()



  # self.buttonlist = []
  # self.numofkwbuttons = 10
  # for i in range(self.numofkwbuttons):
  #                 #keywordstr = keywordstr + urlstrs[i] + ', '
  #                 dumbutton = QPushButton('button'+ str(i))
  #                 self.buttonlist.append(dumbutton)

  # for i in range( len(self.buttonlist) ):
  #                 self.buttonlist[i].hide()
  #                 #keywordstr = keywordstr + urlstrs[i] + ', '
  #                 self.hlayout3.addWidget(self.buttonlist[i])
  #                 self.buttonlist[i].clicked.connect(self.emit_search_command)




  # #Create "more" -button
  # self.morebutton = QPushButton('>')
  # self.morebutton.setHidden(True)
  # self.hlayout3.addWidget(self.morebutton)
  # self.morebutton.clicked.connect(self.show_next_kw_buttons)

  #
  self.kw_subset_ind = 0

  #
  #self.mastervlayout.addLayout(self.hlayout2)
  #Add scrollArea of keyword buttons
  #self.mastervlayout.addWidget(self.scrollArea)
  #self.hlayout.addWidget(self.scrollArea)
  #self.mastervlayout.addLayout(self.hlayout4)
  
  #
  if not args.only_explicit_search:
    self.mastermaterhlayout.addWidget(self.scrollArea)
  #
  self.mastermaterhlayout.addLayout(self.mastervlayout)

  #
  self.setWindowTitle("Re:Know Proactive Search")
  self.setWindowFlags(Qt.WindowStaysOnTopHint|Qt.FramelessWindowHint)
  #self.setStyleSheet('font-size: 10pt')
  screen = QDesktopWidget().screenGeometry()
  self.setGeometry(screen.width()-1024, 0, 1024, 600)

  self.solrdict = {"uri": "url",
                   "keywords": "keyword",
                   "authors": "author",
                   "year": "last_modified"}
 
 def hide_buttons(self):
  for button in self.buttonlist:
    button.hide()

 def disable_buttons(self):
  for button in self.buttonlist:
    button.setText("")
    button.setStyleSheet("background-color: white")
    button.setEnabled(False)

 def enable_buttons(self):
  for button in self.buttonlist:
    button.setEnabled(True)

 #
 def create_buttonwidget_list(self, numofkwbuttons):
  #Create kw-buttons
  buttonlist = []
  #self.numofkwbuttons = 10
  for i in range(self.numofkwbuttons):
                  #keywordstr = keywordstr + urlstrs[i] + ', '
                  dumbutton = QPushButton('button'+ str(i))
                  #dumbutton.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
                  dumbutton.setStyleSheet("background-color: white; width: 100")
                  buttonlist.append(dumbutton)
  #Initially hide the buttons
  # for i in range(len(buttonlist)):
  #   buttonlist[i].setVisible(False)
  #Connect each button to the 'emit_search_command' -function
  for i in range(len(buttonlist)):
    buttonlist[i].clicked.connect(self.emit_search_command)

  return buttonlist

 #
 def create_buttonwidget_list2(self, numofbtns):

    #Create button labels
    btnwidgetlist = []
    numshow = 10
    numofbtns = 10

    #Create buttons
    for i in range(numofbtns):
        
        #
        btnname = 'Button '+str(i)
        btnwidget = button_with_x(btnname,str(i))
        btnwidget.layout().itemAt(1).widget().clicked.connect(self.removeButton)
        btnwidget.layout().itemAt(0).widget().clicked.connect(self.printText)
        btnwidget.setFixedWidth(100)

        #
        print("WIDTH: ",btnwidget.width())
        if(i>numshow):
            btnwidget.hide()
        print(type(btnwidget))

        #
        btnwidgetlist.append(btnwidget)

        #
        print(btnwidgetlist[i])

        # print(isinstance(btnwidget, QtGui.QWidget))
        print(isinstance(btnwidget, QWidget))        

    return btnwidgetlist


 #Create scroll area for buttons
 def create_horizontal_scroll_area_for_buttonwidget_list(self, btnwidgetlist):
    #
    #Create layout for buttonlist
    self.btnlayout = QHBoxLayout()        
    self.btnlayout.setSizeConstraint(QLayout.SetMinimumSize)
    if sys.platform == "linux":
        self.btnlayout.setSpacing(1)
    #Add buttons to the layout
    for i,btnwidget in enumerate(btnwidgetlist):
        self.btnlayout.addWidget(btnwidget)

    #Add spaces to the right end of the layout
    #self.btnlayout.addSpacing(self.btnlayout.)

    #Create a QWidget containing self.btnlayout
    self.dwidget = QWidget()
    self.dwidget.setLayout(self.btnlayout)
    self.dwidget.layout().setContentsMargins(0,0,0,0)
    #self.dwidget.layout().insertStretch(-1,0)

    #Create Scroll area
    scrollArea = QScrollArea()
    scrollArea.setWidget(self.dwidget)    
    scrollArea.setFixedHeight(50)
    scrollArea.setFrameStyle(0)

    return scrollArea


 #Create scroll area for buttons
 def create_vertical_scroll_area_for_buttonwidget_list(self, btnwidgetlist):
    #
    #Create layout for buttonlist
    self.btnlayout = QVBoxLayout()        
    self.btnlayout.setSizeConstraint(QLayout.SetMinimumSize)
    if sys.platform == "linux":
        self.btnlayout.setSpacing(1)
    #Add buttons to the layout
    for i,btnwidget in enumerate(btnwidgetlist):
        self.btnlayout.addWidget(btnwidget)

    #Add spaces to the right end of the layout
    #self.btnlayout.addSpacing(self.btnlayout.)

    #Create a QWidget containing self.btnlayout
    self.dwidget = QWidget()
    self.dwidget.setLayout(self.btnlayout)
    #self.dwidget.layout().setContentsMargins(0,0,0,0)
    #self.dwidget.layout().insertStretch(-1,0)

    #Create Scroll area
    scrollArea = QScrollArea()
    #scrollArea.setMinimumWidth(100)
    scrollArea.setWidget(self.dwidget)    
    scrollArea.setFixedWidth(145)
    #scrollArea.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
    #scrollArea.setFixedHeight(50)
    scrollArea.setFrameStyle(0)
    scrollArea.verticalScrollBar().sliderReleased.connect(self.bwslider_released)

    return scrollArea



 def bwslider_released(self):
   self.slider_released("buttonslider")

 def rdwslider_released(self):
   self.slider_released("readdocumentslider")

 def edwslider_released(self):
   self.slider_released("externaldocumentslider")

 def slider_released(self, slidertype):
   if args.record:
     f = open('data/test_output.txt','a')
     f.write(self.titlerow("SLIDER"))
     f.write(str(self.iteration_index)+", "+slidertype+"\n")
     f.close()

 def titlerow(self, titletype):
   now = time()
   return "#{0}: {1} {2}\n".format(titletype, str(now),
                                   strftime("%c", localtime(now)))

 def log_new_word(self, newquery):
   if args.record:
     f = open('data/test_output.txt','a')
     f.write(self.titlerow("INPUT"))
     f.write(str(self.iteration_index)+", "+newquery+"\n")
     f.close()

 def log_clearbutton(self):
   self.log_button("clear")

 def log_startstopbutton(self):
   self.log_button("startstop")

 def log_backbutton(self):
   self.log_button("back")

 def log_forwardbutton(self):
   self.log_button("forward")

 def log_button(self, buttontype):
   if args.record:
     f = open('data/test_output.txt','a')
     f.write(self.titlerow("BUTTON"))
     f.write(str(self.iteration_index)+", "+buttontype+"\n")
     f.close()

 def stop_animation(self):
  self.enable_buttons()
  self.animlabel.setMovie(None)
  self.animlabel.setPixmap(QPixmap('empty.gif'))

 def start_animation(self):
  self.disable_buttons()
  self.animlabel.setMovie(self.animation)
  self.animation.start()

 # #Runs the Keylogger and Search 
 # def test_pressed(self):
 #  #print('Main: Test')
 #  #self.startStopButton.setDisabled(True)
 #  #self.stopButton.setDisabled(False)  
 #  #self.listwidget.clear()

 #  #Start thread processes
 #  check_update()
 #  self.LoggerThreadObj.start()
 #  self.SearchThreadObj.start()
 
 #def stop_keylogger(self):
 #   print 'Stop logger!'
 #   #self.stopButton.setDisabled(True)
 #   self.startStopButton.setDisabled(False)
 #   self.LoggerThreadObj.stop_logger_loop()

 def only_stop_keylogger(self):
    if self.startStopButton.text() == "Stop":
      self.startStopButton.setText("Start")
      self.LoggerThreadObj.stop_logger_loop()

 def start_stop_keylogger(self):
    print('Start or stop logger!')
    #self.stopButton.setDisabled(False)
    if self.startStopButton.text() == "Start":
      self.startStopButton.setText("Stop")
      self.LoggerThreadObj.start_logger_loop()
      self.LoggerThreadObj.start()
    else:
      self.startStopButton.setText("Start")
      self.LoggerThreadObj.stop_logger_loop()

 def change_c(self,value):
    print('Value: ', value)
    #self.emit(QtCore.SIGNAL(''))


 def emit_explicit_search(self):
    print("Main: Explicit search: ", self.explicit_query_field.text())
    if self.startStopButton.text() == "Start":
      self.startStopButton.setText("Stop")
      self.LoggerThreadObj.start_logger_loop()
      self.LoggerThreadObj.start()

    #Send the explicit query string by emitting 'send_explicit_search_query'-signal
    self.send_explicit_search_query.emit(self.explicit_query_field.text())

    if args.record:
      f = open('data/test_output.txt','a')
      f.write(self.titlerow("EXPLICIT"))
      f.write(str(self.iteration_index)+", "+self.explicit_query_field.text()+"\n")
      f.close()
   
    #Clear the query field    
    if not args.only_explicit_search:
      self.explicit_query_field.clear()


 def emit_search_command(self):
  #if searchfuncid == 0:
    sender = self.sender()
    sender_text = sender.text()
    print('Main: Sending new word from main: ', sender_text , type(sender_text))
    self.update.emit(sender_text)

    if args.record:
      for i,button in enumerate(self.buttonlist):
        if sender_text==button.text():
          button_ind = i
      f = open('data/test_output.txt','a')
      f.write(self.titlerow("CLICKED"))
      f.write(str(self.iteration_index)+", "+sender_text+", "+str(button_ind)+"\n")                                      
      f.close()


 def choose_search_function1(self):
  #if searchfuncid == 0:
    print('Main: Search function is DocSim')
    #check_update()
    self.finished.emit(0)
  # elif searchfuncid == 1:
  #   print 'Main: Search function is LinRel'

 def choose_search_function2(self):
  #if searchfuncid == 0:
    print('Main: Search function is LinRel')
    #check_update()
    self.finished.emit(1)
    #elif searchfuncid == 1:
  #  print 'Main: Search function is LinRel'

 def choose_search_function3(self):
  #if searchfuncid == 0:
    print('Main: Search function is LinRel')
    #check_update()
    self.finished.emit(2)
    #elif searchfuncid == 1:
  #  print 'Main: Search function is LinRel'

 def choose_search_function4(self):
  #if searchfuncid == 0:
    print('Main: Search function is LinRel')
    #check_update()
    self.finished.emit(3)
  #elif searchfuncid == 1:
  #  print 'Main: Search function is LinRel'


 def create_QListWidget(self, val, icon_file):
    listWidget = MyListWidget()
    for i in range(val):
        dumitem = QListWidgetItem(listWidget)
        dstr = ''
        dumitem.setText(dstr)
        dumitem.setWhatsThis('')
        dumitem.setToolTip('')
        icon = QIcon(icon_file)
        dumitem.setIcon(icon)
        dumitem.setHidden(True)
        dumitem.setFlags(Qt.ItemIsUserCheckable)
        dumitem.setCheckState(Qt.Unchecked)
    #
    listWidget.itemDoubleClicked.connect(self.open_url)
    listWidget.itemClicked.connect(self.check_item)

    return listWidget

 def update_QListWidget(self, listWidget, data):
    nrows = listWidget.count()
    njsons= len(data)
    for i in range(nrows):
        listitem = listWidget.item(i)
        listitem.setText('No heippa!')
        listitem.setWhatsThis('https://www.gmail.com')

 def get_value(self, dicti, key, solrmode=False):
  if solrmode:
    key = self.solrkey(key)
  if key in dicti:
    val = dicti[key]
    if solrmode:
      if key in ["url", "title"]:
        val = val[0]
      elif key == "last_modified":
        parts = val[0].split("-")
        val = int(parts[0])
    return val
  return ''

 def has_key(self, dicti, key, solrmode=False):
  if solrmode:
    key = self.solrkey(key)
  if key in dicti:
    return True
  return False

 def solrkey(self, key):
   if key in self.solrdict:
     return self.solrdict[key]
   return key

 def get_data_from_search_thread_and_update_visible_stuff(self, dimedata, solrdata):
   print("Main: got {0} DiMe items, {1} Solr items".format(len(dimedata), len(solrdata)))
   self.hide_lists()
   if len(dimedata)>0:
     self.update_links(dimedata, self.listWidget2, False)
   if len(solrdata)>0:
     self.update_links(solrdata, self.listWidget3, True)

 def get_query_string_from_search_thread(self, query_string_and_corresponding_relevance_vector):

    #inputs:
    #query_string_and_corresponding_relevance_vector = [query_string, r]
    if len(self.old_queries) < 11:
      self.old_queries.append(query_string_and_corresponding_relevance_vector)
    else:
      self.old_queries.append(query_string_and_corresponding_relevance_vector)
      del(self.old_queries[0])
    #
    self.hist_ind = len(self.old_queries)-1
    #
    if self.hist_ind > 0:
      self.backButton.setEnabled(True)
      self.forwardButton.setEnabled(False)


 def get_keywords_from_search_thread_and_update_visible_stuff(self, keywords):    
    if len(self.list_of_lists_of_old_keywords) < 11:
      self.list_of_lists_of_old_keywords.append(self.keywords)
    else:
      self.list_of_lists_of_old_keywords.append(self.keywords)
      del(self.list_of_lists_of_old_keywords[0])

    self.keywords = keywords
    #print("MAIN: ",self.keywords)
    self.update_kwbuttons(self.keywords)
    self.color_kwbuttons()


 def get_old_keywords_and_update_visible_stuff(self):
      self.update_kwbuttons(self.old_keywords[-1])
      self.color_kwbuttons()    
      del(self.list_of_lists_of_old_keywords[-1])


 def repeat_old_query(self):
      #
      #print("NUMBER OF STATES: ", self.hist_ind)
      #
      sender = self.sender()
      sender_text = sender.text()
      #
      if sender_text == "<-":
        #
        self.hist_ind = self.hist_ind - 1
        if self.hist_ind > 0:
          #print("NUMBER OF STATES: ", self.hist_ind)
          self.do_old_query.emit(self.old_queries[self.hist_ind])
          self.send_old_dumstring.emit(self.old_queries[self.hist_ind][0])
          self.forwardButton.setEnabled(True)
        elif self.hist_ind == 0:
          self.do_old_query.emit(self.old_queries[self.hist_ind])
          self.send_old_dumstring.emit(self.old_queries[self.hist_ind][0])          
          self.backButton.setEnabled(False)
        else: 
          self.hist_ind = 0
          self.backButton.setEnabled(False)
      elif sender_text == "->":
        #
        self.hist_ind = self.hist_ind + 1
        if self.hist_ind < len(self.old_queries)-1:
          self.do_old_query.emit(self.old_queries[self.hist_ind])
          self.send_old_dumstring.emit(self.old_queries[self.hist_ind][0])
          self.backButton.setEnabled(True)
        elif self.hist_ind == len(self.old_queries)-1:
          self.do_old_query.emit(self.old_queries[self.hist_ind])
          self.send_old_dumstring.emit(self.old_queries[self.hist_ind][0])        
          self.forwardButton.setEnabled(False)
        else:
          self.hist_ind = len(self.old_queries)-1
          self.forwardButton.setEnabled(False)

        #

 def hide_lists(self):
   for dj in range(self.listWidget1.count()):
     self.listWidget1.item(dj).setHidden(True)
     self.listWidget1.item(dj).setCheckState(Qt.Unchecked)
   for dj in range(self.listWidget2.count()):
     self.listWidget2.item(dj).setHidden(True)
     self.listWidget2.item(dj).setCheckState(Qt.Unchecked)
   for dj in range(self.listWidget3.count()):
     self.listWidget3.item(dj).setHidden(True)
     self.listWidget3.item(dj).setCheckState(Qt.Unchecked)

 def update_links(self, resultlist, listwidget, solrmode):

   #For indicating the beginning of new iteration,
   #increase the value of self.iteration_index
   self.iteration_index = self.iteration_index + 1

   i, j, k = 0, 0, 0

   seen_uris = set()
   
   if (type(resultlist) is list and len(resultlist) > 0
       and type(resultlist[0]) is dict):

     #Set hidden listWidgetItems that are not used

     for resultidx, resultitem in enumerate(resultlist):

       linkstr   = self.get_value(resultitem, "uri", solrmode)
       if linkstr in seen_uris:
         continue
       seen_uris.add(linkstr)

       dataid    = str(self.get_value(resultitem, "id", solrmode))
       score    = str(self.get_value(resultitem, "score"))

       if self.has_key(resultitem, "isStoredAs", solrmode):
         storedas  = str(self.get_value(resultitem, "isStoredAs", solrmode))
         storedasl = storedas.split('#')[1]
       else:
         storedasl = "LocalFileDataObject"

       if self.has_key(resultitem, "timeCreated", solrmode):
         ctime = str(self.get_value(resultitem, "timeCreated", solrmode))
         date = datetime.datetime.fromtimestamp(int(int(ctime) / 1000))
         datestr = date.__str__()
       else:
         datestr = ""

       if len(linkstr) > 20:
         linkstrshort = linkstr[0:40]
       else:
         linkstrshort = linkstr

       tooltipstr = self.process_keywords(self.get_value(resultitem,
                                                         "keywords",
                                                         solrmode))

       if storedasl in ["LocalFileDataObject", "EmbeddedFileDataObject"]:

         if self.has_key(resultitem, "title", solrmode):
           title = self.get_value(resultitem, "title", solrmode)
           title = title.replace('\n', '').replace('\r', '')
         else:
           title = linkstrshort

         authors = self.process_authors(self.get_value(resultitem, "authors",
                                                       solrmode),
                                        solrmode)

         yearstr = ""
         if self.has_key(resultitem, "year", solrmode):
           year = self.get_value(resultitem, "year", solrmode)
           if year>0:
             yearstr = str(year)+"."

         #Create link to DiMe server
         dumlink = self.srvurl.split('/')[2]
         linkstr2 = 'http://' + dumlink + '/infoelem?id=' + dataid

         if solrmode: #if args.singlelist:
           visiblestr = title + '. ' + authors + '. ' + yearstr
         else:
           visiblestr = linkstr
           if len(datestr) > 0:
              visiblestr +=  ' (' + datestr + ')'

         if len(score) > 0:
           visiblestr += ' [' + score + ']'

         if j < len(listwidget):
           listwidget.item(j).setText(visiblestr)
           listwidget.item(j).setToolTip(tooltipstr)
           listwidget.item(j).setHidden(False)
           whatsthisstr = linkstr+"*"+linkstr2
           listwidget.item(j).setWhatsThis(whatsthisstr)
           #If linkstr already in useful_docs, mark as checked
           if whatsthisstr in self.useful_docs.keys():
             listwidget.item(j).setCheckState(Qt.Checked)

         j = j + 1

       elif storedasl in ["MailboxDataObject"]:

         subj = "[no subject]"
         if self.has_key(resultitem, "subject"):
           subj = self.get_value(resultitem, "subject")

         #Create link to DiMe server
         dumlink = self.srvurl.split('/')[2]
         linkstr = linkstr2 = 'http://' + dumlink + '/infoelem?id=' + dataid

         visiblestr = subj + '  (' + datestr + ')'

         if k < len(self.listWidget2):
           self.listWidget2.item(j).setText(visiblestr)
           self.listWidget2.item(j).setToolTip(tooltipstr)
           self.listWidget2.item(j).setHidden(False)
           whatsthisstr = linkstr+"*"+linkstr2
           self.listWidget2.item(j).setWhatsThis(whatsthisstr)
           #If linkstr already in useful_docs, mark as checked
           if whatsthisstr in self.useful_docs.keys():
             self.listWidget2.item(j).setCheckState(Qt.Checked)

         k = k + 1

       else: # Assuming web item

         if self.has_key(resultitem, "title"):
           title = self.get_value(resultitem, "title")
         else:
           title   = linkstrshort

         #Create link to DiMe server
         dumlink = self.srvurl.split('/')[2]
         linkstr2 = 'http://' + dumlink + '/infoelem?id=' + dataid

         if i < len(self.listWidget1):
           visiblestr = title + '  (' + datestr + ')'
           self.listWidget1.item(j).setText(visiblestr)
           self.listWidget1.item(j).setToolTip(tooltipstr)
           self.listWidget1.item(j).setHidden(False)
           whatsthisstr = linkstr+"*"+linkstr2
           self.listWidget1.item(j).setWhatsThis(whatsthisstr)
           #If linkstr already in useful_docs, mark as checked
           if whatsthisstr in self.useful_docs.keys():
             self.listWidget1.item(j).setCheckState(Qt.Checked)

         i = i + 1

       #If record-mode chosen, record the resouce id and uri
       if args.record:
         if resultidx == 0:
           f = open('data/test_output.txt','a')
         f.write(self.titlerow("RESOURCES"))
         f.write(str(self.iteration_index)+", "+dataid+", "+title+", "
                 +linkstr+", "+str(resultidx)+"\n")

     if args.record:
       f.close()

 def process_authors(self, alist, solrmode):
   authorstring = ""
   first = True;
   for a in alist:
     if not first:
       authorstring += ", "
     first = False

     if solrmode:
       parts = a.split(",")
       if len(parts)>1:
         fn = parts[1].strip()
         authorstring += fn[0] + ". "
       authorstring += parts[0].strip()
     else:
       if "firstName" in a:
         fn = a["firstName"].strip()
         authorstring += fn[0] + ". "
       if "lastName" in a:
         authorstring += a["lastName"].strip()
   return authorstring

 #
 def process_keywords(self, kwlist):
   keywordsstring = "Keywords:\n"
   first = True;
   for kw in kwlist:
     if not first:
       keywordsstring += ";\n"
     first = False
     keywordsstring += kw
   return keywordsstring

 #
 def update_kwbuttons(self, keywordlist):

    #First hide all buttons
 #   for i in range(len(self.buttonlist)):
 #     self.buttonlist[i].hide()

    #
    i = 0
    j = 0
    k = 0

    #print 'Main: update_links_and_kwbuttons: urlstrs: ', urlstrs[len(urlstrs)-1]
    #print 'type of el.: ', type(urlstrs[10])
    if type(keywordlist) is list:
      if len(keywordlist) > 0:
        #
        if type(keywordlist[0]) is str:
          #print('Main: update_links: got a list of keywords!!!')
          #print('Main: keyword button labels keywords: ', keywordlist)
          ncols = self.hlayout3.count()
          #print 'Num of widgets ', ncols
          #Remove old buttons
          if len(self.buttonlist) > 0:
            for i in range( len(keywordlist) ):
                            #self.hlayout2.removeWidget(self.buttonlist[i])                  
                            #self.hlayout3.itemAt(i).widget().setParent(None) 
                            #self.hlayout3.itemAt(i).setParent(None)
                            if i < len(self.buttonlist):
                              #self.unicode_to_str(keywordlist[i])
                              self.buttonlist[i].setText(keywordlist[i])
                              #self.buttonlist[i].setText(self.unicode_to_str(keywordlist[i]))
                              #self.btnlayout.itemAt(i).widget().setVisible(True)
                              self.buttonlist[i].show()

                              #If record-mode chosen, record the suggested keywords
                              if args.record:
                                #Record suggestions
                                if i == 0:
                                  f = open('data/test_output.txt','a')
                                  f.write(self.titlerow("KEYWORDS"))
                                f.write(str(self.iteration_index)+", "+keywordlist[i]+", "+str(i)+"\n")
            if args.record:
              f.close()

      if not args.only_explicit_search:
        self.scrollArea.show()
        self.scrollArea.verticalScrollBar().setSliderPosition(0)






    return

 #
 # def show_next_kw_buttons(self,keywordlist):
 #  print(self.keywords)
 #  if len(self.keywords) > 0:
 #    self.kw_subset_ind = self.kw_subset_ind + 1

 #    startind = self.kw_subset_ind*self.numofkwbuttons
 #    self.update_kwbuttons(self.keywords[startind:startind+self.numofkwbuttons])    
 #    self.previousbutton.setHidden(False)

 # #
 # def show_previous_kw_buttons(self,keywordlist):
 #  print(self.keywords)
 #  if len(self.keywords) > 0:
 #    if(self.kw_subset_ind>0):
 #      #
 #      self.kw_subset_ind = self.kw_subset_ind - 1
 #      startind = self.kw_subset_ind*self.numofkwbuttons
 #      self.update_kwbuttons(self.keywords[startind:startind+self.numofkwbuttons])
 #      #
 #      if self.kw_subset_ind == 0:
 #        self.previousbutton.setHidden(True)

 #    else:
 #      #
 #      self.previousbutton.setHidden(True)
    
    
        


 def clear_kw_history(self):
  if os.path.isfile('data/r_old.npy'):
    os.remove('data/r_old.npy')

 def color_kwbuttons(self):
  #
  if not self.is_non_zero_file('data/test_wordlist.list'):
   return

  test_wordlist = pickle.load(open('data/test_wordlist.list','rb'))
  for i in range(len(self.buttonlist)):
    buttext = self.buttonlist[i].text()
    if buttext in test_wordlist:
      self.buttonlist[i].setStyleSheet("background-color: GreenYellow")
    else:
      self.buttonlist[i].setStyleSheet("background-color: white")

 def is_non_zero_file(self, fpath):
  return True if os.path.isfile(fpath) and os.path.getsize(fpath) > 0 else False

 #
 def unicode_to_str(self, ustr):
    """Converts unicode strings to 8-bit strings."""
    try:
        str = ustr.encode('utf-8')
        return ''.join([c for c in str if ord(c) > 31])
    except UnicodeEncodeError:
        print("Main: UnicodeEncodeError")
    return ""


 #
 def check_item(self, listWidgetitem):

   #Take the position of the checked item in the list of suggested resources
   if self.listWidget1.row(listWidgetitem) > 0:
     row = self.listWidget1.row(listWidgetitem)
   elif self.listWidget2.row(listWidgetitem) > 0:
     row = self.listWidget2.row(listWidgetitem)
   elif self.listWidget3.row(listWidgetitem) > 0:  
     row = self.listWidget3.row(listWidgetitem)
   else:
     row = 0
   print("ROW:",row)

   if listWidgetitem.checkState() == Qt.Checked:
     listWidgetitem.setCheckState(Qt.Unchecked)
     
     #Remove from useful_docs
     linkstr = listWidgetitem.whatsThis()
     del(self.useful_docs[linkstr])
     
     #Remove from useful_docs_listWidget
     for i in range(self.useful_docs_listWidget.count()):
       print("i ",self.useful_docs_listWidget.item(i).whatsThis())
       if self.useful_docs_listWidget.item(i).whatsThis() == linkstr:
         #print("TAKE ITEM")
         self.useful_docs_listWidget.takeItem(i)
         break

     #If recording enabled, record the checked items for current iteration
     if args.record:
       #Record suggestions
       f = open('data/test_output.txt','a')
       f.write(self.titlerow("UNCHECKED"))
       f.write(str(self.iteration_index)+", "+listWidgetitem.text()+", "+linkstr+", "+str(row)+", "+"\n")
       f.close()         

   else:
     #Set checked the chosen item
     listWidgetitem.setCheckState(Qt.Checked)

     #Add to useful_docs dict
     linkstr = listWidgetitem.whatsThis()
     text = listWidgetitem.text()
     parts = text.split("[")
     if len(parts)>1:
       text = parts[0]

     self.useful_docs[linkstr] = text

     #Add to useful_docs_listWidget
     listWidgetItem = QListWidgetItem(self.useful_docs[linkstr])
     listWidgetItem.setWhatsThis(linkstr)
     listWidgetItem.setToolTip('')
     icon = QIcon(self.iconfile3)
     listWidgetItem.setIcon(icon)
     listWidgetItem.setHidden(False)
     listWidgetItem.setFlags(Qt.ItemIsUserCheckable)
     listWidgetItem.setCheckState(Qt.Checked)

     self.useful_docs_listWidget.addItem(listWidgetItem)

     #If recording enabled, record the checked items for current iteration
     if args.record:
       #Record suggestions
       f = open('data/test_output.txt','a')
       f.write(self.titlerow("CHECKED"))
       f.write(str(self.iteration_index)+", "+text+", "+linkstr+", "+str(row)+", "+"\n")
       f.close()

   #
   udc = 'Found documents [{0}]'.format(self.useful_docs_listWidget.count()) 
   self.useful_docs_title.setText(udc)
   #self.update_links(self.data)





 #
 def open_url(self, listWidgetitem):

  #Take the position of the checked item in the list of suggested resources
  if self.listWidget1.row(listWidgetitem) > 0:
   row = self.listWidget1.row(listWidgetitem)
  elif self.listWidget2.row(listWidgetitem) > 0:
   row = self.listWidget2.row(listWidgetitem)
  elif self.listWidget3.row(listWidgetitem) > 0:  
   row = self.listWidget3.row(listWidgetitem)
  else:
   row = 0
  print("ROW:",row)

  #global urlstr
  #webbrowser.open(urlstr)
  whatsThisString = listWidgetitem.whatsThis()
  if "*" in whatsThisString:
    webpagel = listWidgetitem.whatsThis().split('*')[0]
    dimelink = listWidgetitem.whatsThis().split('*')[1]
  else:
    webpagel = listWidgetitem.whatsThis()
    dimelink = webpagel
  #webbrowser.open(str(listWidgetitem.whatsThis()))
  #webbrowser.open(webpagel)
  if True: #args.singlelist:
    webbrowser.open(webpagel)
  else:
    webbrowser.open(dimelink)

  #
  if args.record:
    f = open('data/test_output.txt','a')
    f.write(self.titlerow("VISITED"))
    f.write(str(self.iteration_index)+", "+listWidgetitem.text()+", "+whatsThisString+", "+str(row)+"\n")
    f.close()

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

 def quitting(self):
  global var
  var = False
  #QtCore.QCoreApplication.instance().quit()

 #Quit
 def closeEvent(self, event):
     self.quitting()


if __name__ == "__main__":


  parser = argparse.ArgumentParser()
  
  parser.add_argument("--solr", action='store_true',
                      help="show also Solr documents")
  parser.add_argument("--solronly", action='store_true',
                      help="show only Solr documents")
  parser.add_argument("--only_explicit_search", action='store_true', 
                      help="Keylogging and LinRel computations are disbled.")
  parser.add_argument('--emphasize_kws', metavar='LAMBDA', action='store', type=int, default=0, help='Emphasize clicked keywords.')

  #
  parser.add_argument("--record", action='store_true',
                      help="Records suggested resources, keywords and user interaction.")

  parser.add_argument('--c', metavar='N', action='store', type=float,
                      default=1.0, help='Exploration/Exploitation coeff.')
  parser.add_argument('--mmr', metavar='LAMBDA', action='store', type=float,
                      default=-1.0, help='use MMR with parameter lambda')

  args = parser.parse_args()

  if args.solr and args.solronly:
      print('Both "--solr" and "--solronly" cannot be set')
      sys.exit()

  # run
  app  = QApplication(sys.argv)
  #test = MainWindow()
  
  #
  test = MyApp()
  #test.scrollArea.hide()
  test.disable_buttons()

  test.show()
  app.exec_()

