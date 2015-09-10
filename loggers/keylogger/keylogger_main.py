#!/usr/local/lib/python2.7
# -*- coding: utf-8 -*-

#import sys, time
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# For Keylogger
import sys
import datetime #For import date and time
from time import sleep, time
import ctypes as ct
from ctypes.util import find_library

import os
import Queue
import threading

from update_dict_lda_and_Am import *

from dime_search import *

#Includes the definition of clickable label
from ExtendedQLabel import *

#For getting web page title
#import lxml.html
import urllib2
#from BeautifulSoup import BeautifulSoup

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
if sys.platform == "linux2":
  from loggerthread_linux import *
elif sys.platform == "darwin":
  from loggerthread_osx import *
else:
  print "Unsupported platform"
  sys.exit()

#Import search thread
from searchthread import *

################################################################

# linux only!
# assert("linux" in sys.platform)

class MyApp(QWidget):
#class MyApp(QMainWindow):

 finished = pyqtSignal(int)
 update = pyqtSignal(unicode)
 
 def __init__(self, parent=None):
  QWidget.__init__(self, parent)
  #QMainWindow.__init__(self, parent)
  #widget = QWidget(self)
  #self.setCentralWidget(widget)

  #Read user.ini file
  self.srvurl, self.username, self.password, self.time_interval, self.nspaces, self.nwords, self.updateinterval = self.read_user_ini()
  self.data = []
  self.keywords = ''

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

  #self.testButton.clicked.connect(self.anim1.tl.start)
  #self.overlay.resize(event.size())

  #Create data files
  check_update()

  #Create  thread objects
  self.LoggerThreadObj  = LoggerThread()
  self.SearchThreadObj = SearchThread()

  #Data connection from logger thread to search thread
  self.LoggerThreadObj.update.connect(self.SearchThreadObj.get_new_word)

  #self.connect(self.LoggerThreadObj, QtCore.SIGNAL("update(QString)"), self.anim1.tl.start)
  #self.connect(self, QtCore.SIGNAL("update(QString)"), self.anim1.tl.start)
  #self.connect(self.SearchThreadObj, QtCore.SIGNAL("finished(PyQt_PyObject)"), self.update_links_and_kwbuttons)

  #Data connections from search thread to main thread
  self.SearchThreadObj.send_links.connect(self.get_data_from_search_thread_and_update_visible_stuff)
  self.SearchThreadObj.send_keywords.connect(self.get_keywords_from_search_thread_and_update_visible_stuff)
  #self.SearchThreadObj.start_search.connect(self.anim1.tl.start)
  #self.SearchThreadObj.start_search.connect(self.animation.start)
  self.SearchThreadObj.start_search.connect(self.start_animation)

  #self.SearchThreadObj.all_done.connect(self.anim1.tl.stop)
  #self.SearchThreadObj.all_done.connect(self.animation.stop)
  self.SearchThreadObj.all_done.connect(self.stop_animation)

  #Data connections from main thread to search thread
  self.finished.connect(self.SearchThreadObj.change_search_function)
  self.update.connect(self.SearchThreadObj.get_new_word_from_main_thread)

  #Create visible stuff
  val = 5
  iconfile = 'web.png'
  self.gbtitle = QLabel('Web sites')
  self.listWidget1 = self.create_QListWidget(20, iconfile)

  iconfile = 'mail.png'
  self.gbtitle2 = QLabel('E-Mails')
  self.listWidget2 = self.create_QListWidget(20, iconfile)
  #
  iconfile = 'doc.png'
  self.gbtitle3 = QLabel('Docs')
  self.listWidget3 = self.create_QListWidget(20, iconfile)


  #Buttons
  #Start button
  self.testButton  = QPushButton("Start")
  #self.connect(self.testButton, QtCore.SIGNAL("released()"), self.test_pressed)
  self.testButton.released.connect(self.start_keylogger)
  #
  self.stopButton  = QPushButton("Stop")
  self.stopButton.released.connect(self.stop_keylogger)

  #
  self.testButton.setDisabled(True)
  self.stopButton.setDisabled(False)   
  self.LoggerThreadObj.start()
  self.SearchThreadObj.start()

  #Slider for exploitation/exploration slider
  self.eeslider    = QSlider(Qt.Horizontal)
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
  self.radiobutton1.click()

  self.radiobutton2= QRadioButton("LinRel + DiMe search")
  self.radiobutton2.released.connect(self.choose_search_function2)

  self.radiobutton3= QRadioButton("LinRel (omitting history)")
  self.radiobutton3.released.connect(self.choose_search_function3)

  self.radiobutton4= QRadioButton("LinRel + DocSim")
  self.radiobutton4.released.connect(self.choose_search_function4)

  #Connect animation to logger thread and search thread
  # self.testButton.clicked.connect(self.anim1.tl.start)
  # self.stopButton.clicked.connect(self.anim1.tl.stop)


  #
  self.buttonlist = []


  #Layout for Web Pages
  self.vlayout1 = QVBoxLayout()
  self.vlayout1.addWidget(self.gbtitle)
  self.vlayout1.addWidget(self.listWidget1)
  #
  self.vlayout2 = QVBoxLayout()
  self.vlayout2.addWidget(self.gbtitle2)
  self.vlayout2.addWidget(self.listWidget2)
  #  
  self.vlayout3 = QVBoxLayout()
  self.vlayout3.addWidget(self.gbtitle3)
  self.vlayout3.addWidget(self.listWidget3)
  #
  self.vlayout4 = QVBoxLayout()
  #self.vlayout4.addWidget(QLabel(' '))
  self.subhlayout= QHBoxLayout()
  self.subhlayout.addWidget(self.testButton)
  self.subhlayout.addWidget(self.stopButton)
  #self.subhlayout.addWidget(self.anim1)
  self.subhlayout.addWidget(self.animlabel)
  #self.movie.start()

  self.vlayout4.addLayout(self.subhlayout)

  self.subhlayout2= QHBoxLayout()
  self.subhlayout2.addWidget(self.eesliderl1)
  self.subhlayout2.addWidget(self.eeslider)
  self.subhlayout2.addWidget(self.eesliderl2)
  self.vlayout4.addLayout(self.subhlayout2)
  #vlayout5 is a sub layout for vlayout4
  self.vlayout5 = QVBoxLayout()
  self.vlayout5.addWidget(self.radiobutton1)
  self.vlayout5.addWidget(self.radiobutton2)
  #self.vlayout5.addWidget(self.radiobutton3)
  self.vlayout5.addWidget(self.radiobutton4)

  #Groupbox for radiobuttons
  self.mygroupbox = QGroupBox('Search Method')
  self.mygroupbox.setLayout(self.vlayout5)
  self.vlayout4.addWidget(self.mygroupbox)

  #Add layouts
  self.hlayout = QHBoxLayout()
  self.hlayout.addLayout(self.vlayout1)
  self.hlayout.addLayout(self.vlayout2)
  self.hlayout.addLayout(self.vlayout3)
  self.hlayout.addLayout(self.vlayout4)

  #Master vertical layout:
  self.mastervlayout = QVBoxLayout(self)

  #Add self.hlayout to self.mastervlayout
  self.mastervlayout.addLayout(self.hlayout)

  #
  self.hlayout2 = QHBoxLayout()
  self.keywordlabel = QLabel('Suggested keywords: ')
  self.keywordlabel.setStyleSheet('color: green')
  self.hlayout2.addWidget(self.keywordlabel)
  #
  self.hlayout3 = QHBoxLayout()
  #Create buttons
  self.buttonlist = []
  numofkwbuttons = 10
  for i in range(numofkwbuttons):
                  #keywordstr = keywordstr + urlstrs[i] + ', '
                  dumbutton = QPushButton('button'+ str(i))
                  self.buttonlist.append(dumbutton)
  for i in range( len(self.buttonlist) ):
                  self.buttonlist[i].hide()
                  #keywordstr = keywordstr + urlstrs[i] + ', '
                  self.hlayout3.addWidget(self.buttonlist[i])
                  self.buttonlist[i].clicked.connect(self.emit_search_command)
                  #Hide buttons initially


  #
  self.mastervlayout.addWidget(self.keywordlabel)
  #Add self.hlayout2 to self.mastervlayout
  self.mastervlayout.addLayout(self.hlayout2)
  self.mastervlayout.addLayout(self.hlayout3)

  #
  self.setWindowTitle("ProActive Search") 


 def stop_animation(self):
  self.animlabel.setMovie(None)
  self.animlabel.setPixmap(QPixmap('empty.gif'))

 def start_animation(self):
  self.animlabel.setMovie(self.animation)
  self.animation.start()

 #Runs the Keylogger and Search 
 def test_pressed(self):
  print 'Main: Test'
  self.testButton.setDisabled(True)
  self.stopButton.setDisabled(False)  
  #self.listwidget.clear()

  #Start thread processes
  check_update()
  self.LoggerThreadObj.start()
  self.SearchThreadObj.start()
 
 def stop_keylogger(self):
    print 'Stop logger!'
    self.stopButton.setDisabled(True)
    self.testButton.setDisabled(False)
    self.LoggerThreadObj.stop_logger_loop()

 def start_keylogger(self):
    print 'Start logger!'
    self.stopButton.setDisabled(False)
    self.testButton.setDisabled(True)
    self.LoggerThreadObj.start_logger_loop()    
    self.LoggerThreadObj.start()

 def change_c(self,value):
    print 'Value: ', value
    #self.emit(QtCore.SIGNAL(''))

 def emit_search_command(self):
  #if searchfuncid == 0:
    sender = self.sender()
    sender_text = sender.text()
    print 'Main: Sending new word from main: ', sender_text , type(sender_text)
    self.update.emit(sender_text)

 def choose_search_function1(self):
  #if searchfuncid == 0:
    print 'Main: Search function is DocSim'
    #check_update()
    self.finished.emit(0)
  # elif searchfuncid == 1:
  #   print 'Main: Search function is LinRel'

 def choose_search_function2(self):
  #if searchfuncid == 0:
    print 'Main: Search function is LinRel'
    #check_update()
    self.finished.emit(1)
    #elif searchfuncid == 1:
  #  print 'Main: Search function is LinRel'

 def choose_search_function3(self):
  #if searchfuncid == 0:
    print 'Main: Search function is LinRel'
    #check_update()
    self.finished.emit(2)
    #elif searchfuncid == 1:
  #  print 'Main: Search function is LinRel'

 def choose_search_function4(self):
  #if searchfuncid == 0:
    print 'Main: Search function is LinRel'
    #check_update()
    self.finished.emit(3)
  #elif searchfuncid == 1:
  #  print 'Main: Search function is LinRel'


 def create_QListWidget(self, val, icon_file):
    listWidget = QListWidget()
    for i in range(val):
        dumitem = QListWidgetItem(listWidget)
        dstr = ''
        dumitem.setText(dstr)
        dumitem.setWhatsThis('')
        dumitem.setToolTip('')
        icon = QIcon(icon_file)
        dumitem.setIcon(icon)
        dumitem.setHidden(True)

    listWidget.itemClicked.connect(self.open_url)

    return listWidget

 def update_QListWidget(self, listWidget, data):
    nrows = listWidget.count()
    njsons= len(data)
    for i in range(nrows):
        listitem = listWidget.item(i)
        listitem.setText('No heippa!')
        listitem.setWhatsThis('https://www.gmail.com')


 def safe_get_value(self, dicti, key):
  if dicti.has_key(key):
   return dicti[key]
  return ''

 def get_data_from_search_thread_and_update_visible_stuff(self, data):
    self.data = data
    self.update_links_and_kwbuttons(self.data)

 def get_keywords_from_search_thread_and_update_visible_stuff(self, keywords):    
    self.keywords = keywords
    self.update_kwbuttons(self.keywords)
    self.color_kwbuttons()

 #
 def update_links_and_kwbuttons(self, urlstrs):
    i = 0
    j = 0
    k = 0

    if type(urlstrs) is types.ListType:
      if len(urlstrs) > 0:
        if type(urlstrs[0]) is types.DictType:
          #Set hidden listWidgetItems that are not used
          for dj in range(self.listWidget1.count()):
            self.listWidget1.item(dj).setHidden(True)    
          for dj in range(self.listWidget2.count()):
            self.listWidget2.item(dj).setHidden(True)
          for dj in range(self.listWidget3.count()):
            self.listWidget3.item(dj).setHidden(True)      

          #Initialize rake object
          #rake_object = rake.Rake("SmartStoplist.txt", 5, 5, 4)
          for ijson in range( len(urlstrs) ):
                                      #title    = None
                                      linkstr   = self.unicode_to_str( urlstrs[ijson]["uri"] )
                                      ctime     = str(urlstrs[ijson]["timeCreated"])
                                      typestr   = str(urlstrs[ijson]["type"])
                                      storedas  = str(urlstrs[ijson]["isStoredAs"])
                                      dataid    = str(urlstrs[ijson]["id"])
                                      storedasl = storedas.split('#')[1]



                                      #print 'Main: storedasl: ', storedasl
                                      #content  = self.safe_get_value(urlstrs[ijson], "plainTextContent") 
                                      content = ''
                                      #keywords = rake_object.run(content)
                                      keywords = ''
                                      #print ctime 
                                      timeint = int(ctime) / 1000
                                      #print timeint
                                      date = datetime.datetime.fromtimestamp(timeint)
                                      datestr = date.__str__()

                                      if len(linkstr) > 20:
                                        linkstrshort = linkstr[0:40]
                                      else:
                                        linkstrshort = linkstr
                                      

                                      if len(keywords) > 0:
                                        tooltipstr = re.sub("[^\w]", " ", content)
                                        #self.labellist[i].setToolTip(tooltipstr)
                                        tooltipstr = "Keywords: " + keywords[0][0]
                                      else:
                                        tooltipstr = 'Keywords: '
                                        #self.labellist[i].setText(keywords[0][0])

                                      if storedasl in ["LocalFileDataObject" ]:
                                          #print 'Main: doc', linkstr

                                          #Create link to DiMe server
                                          dumlink = self.srvurl.split('/')[2]
                                          linkstr2 = 'http://' + dumlink + '/infoelem?id=' + dataid

                                          visiblestr = linkstrshort + '  ' + datestr
                                          if j < len(self.listWidget3):
                                            self.listWidget3.item(j).setText(visiblestr) 
                                            self.listWidget3.item(j).setWhatsThis(linkstr+"*"+linkstr2)
                                            self.listWidget3.item(j).setToolTip(tooltipstr)
                                            self.listWidget3.item(j).setHidden(False)
                                          #self.datelist3[j].setText(datestr)
                                          #self.labellist3[j].setAlignment(Qt.AlignLeft)
                                          j = j + 1
                                      elif storedasl in ["MailboxDataObject"]:
                                          #print 'Main: mail ', storedasl
                                          subj = "[no subject]"
                                          if urlstrs[ijson].has_key("subject"):
                                            subj = self.unicode_to_str(urlstrs[ijson]["subject"])
                                          #Create link to DiMe server
                                          dumlink = self.srvurl.split('/')[2]
                                          linkstr = linkstr2 = 'http://' + dumlink + '/infoelem?id=' + dataid
                                          #print 'Main: linkstr ', linkstr
                                          visiblestr = subj + '  ' + datestr
                                          if k < len(self.listWidget2):
                                            self.listWidget2.item(k).setText(visiblestr) 
                                            self.listWidget2.item(k).setWhatsThis(linkstr+'*'+linkstr2)
                                            self.listWidget2.item(k).setToolTip(tooltipstr)
                                            self.listWidget2.item(k).setHidden(False)
                                          #self.labellist3[j].setAlignment(Qt.AlignLeft)

                                          k = k + 1                                  
                                      else:
                                        #print 'Main: web ', linkstr
                                        title = None

                                        #title = str(urlstrs[ijson]["Title"])
                                        # try:
                                        #   #print 'Finding Web page title:'
                                        #   dumt = urllib2.urlopen(linkstr)
                                        #   soup = BeautifulSoup(dumt)
                                        #   #print 'Soup title: ', soup.title.string
                                        #   try: 
                                        #     if soup.title.string is not None:                                        
                                        #       title = soup.title.string
                                        #       #print 'Soup title2 :', title
                                        #   except (AttributeError, ValueError):
                                        #     #print 'attr. error'
                                        #     pass
                                        # except (urllib2.HTTPError, urllib2.URLError, ValueError):
                                        #   pass

                                        # if title is None:
                                        #   title = linkstrshort
                                        try:
                                          title   = urlstrs[ijson]["title"]
                                        except KeyError:
                                          title   = linkstrshort

                                        #Create link to DiMe server
                                        dumlink = self.srvurl.split('/')[2]
                                        linkstr2 = 'http://' + dumlink + '/infoelem?id=' + dataid                                    
                                        if i < len(self.listWidget1):
                                          visiblestr = title + '  ' + datestr
                                          self.listWidget1.item(i).setText(visiblestr) 
                                          self.listWidget1.item(i).setWhatsThis(linkstr+'*'+linkstr2)
                                          self.listWidget1.item(i).setToolTip(tooltipstr)
                                          self.listWidget1.item(i).setHidden(False)
                                        i = i + 1  
                                        #print i


 def update_kwbuttons(self, keywordlist):
    i = 0
    j = 0
    k = 0
    #print 'Main: update_links_and_kwbuttons: urlstrs: ', urlstrs[len(urlstrs)-1]
    #print 'type of el.: ', type(urlstrs[10])
    if type(keywordlist) is types.ListType:
      if len(keywordlist) > 0:
        #
        if type(keywordlist[0]) is types.UnicodeType:
          print 'Main: update_links: got a list of keywords!!!'
          keywordstr = 'Suggested keywords: '
          print 'Main: keyword button labels keywords: ', keywordlist
          ncols = self.hlayout3.count()
          #print 'Num of widgets ', ncols
          #Remove old buttons
          if len(self.buttonlist) > 0:
            for i in range( len(keywordlist) ):
                            #keywordstr = keywordstr + urlstrs[i] + ', ' 
                            #self.hlayout2.removeWidget(self.buttonlist[i])                  
                            #self.hlayout3.itemAt(i).widget().setParent(None) 
                            #self.hlayout3.itemAt(i).setParent(None)
                            if i < ncols:
                              #self.unicode_to_str(keywordlist[i])
                              self.buttonlist[i].setText(keywordlist[i])
                              #self.buttonlist[i].setText(self.unicode_to_str(keywordlist[i]))
                              self.buttonlist[i].show()  
    return


 def color_kwbuttons(self):
  if not self.is_non_zero_file('data/test_wordlist.list'):
   return
  f = open('data/test_wordlist.list','r')
  test_wordlist = pickle.load(f)
  print test_wordlist
  for i in range(len(self.buttonlist)):
    buttext = self.buttonlist[i].text()
    #print buttext
    if buttext in test_wordlist:
      #print 'True!!'
      # buttextcol    = QColor('red')
      # butbackgrdcol = QColor('red')
      # redpalette = QPalette(buttextcol, butbackgrdcol)
      # self.buttonlist[i].setPalette(redpalette)
      self.buttonlist[i].setStyleSheet("background-color: GreenYellow")
    else:
      self.buttonlist[i].setStyleSheet("background-color: white")
  #for i in range(len(self.keywords))

 def is_non_zero_file(self, fpath):
  return True if os.path.isfile(fpath) and os.path.getsize(fpath) > 0 else False

 def read_user_ini(self):

    f          = open('user.ini','r')
    dumstr     = f.read()
    stringlist = dumstr.split()

    for i in range( len(stringlist) ):
            if stringlist[i] == "server_url:":
                    srvurl = stringlist[i+1]
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
            if stringlist[i] == "numwords:":
                    dum_string = stringlist[i+1]
                    numwords = int(dum_string)                      
            if stringlist[i] == "updating_interval:":
                    dum_string = stringlist[i+1]
                    updateinterval = float(dum_string)                        

    return srvurl, usrname, password, time_interval, nspaces, numwords, updateinterval

 #films 
 #
 def unicode_to_str(self, ustr):
    """Converts unicode strings to 8-bit strings."""
    try:
        str = ustr.encode('utf-8')
        return ''.join([c for c in str if ord(c) > 31])
    except UnicodeEncodeError:
        print "Main: UnicodeEncodeError"
    return ""


 #
 def open_url(self, listWidgetitem):
  #global urlstr
  #webbrowser.open(urlstr)
  webpagel = listWidgetitem.whatsThis().split('*')[0]
  dimelink = listWidgetitem.whatsThis().split('*')[1]
  #webbrowser.open(str(listWidgetitem.whatsThis()))
  #webbrowser.open(webpagel)
  webbrowser.open(dimelink)

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
  QtCore.QCoreApplication.instance().quit()

 #Quit
 def closeEvent(self, event):
     self.quitting()






# run
app  = QApplication(sys.argv)
test = MyApp()
test.show()
app.exec_()

