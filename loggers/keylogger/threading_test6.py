#!/usr/local/lib/python2.7
# -*- coding: utf-8 -*-

#import sys, time
from PyQt4 import QtCore, QtGui

# For Keylogger
import sys
import datetime #For import date and time
from time import sleep, time
import ctypes as ct
from ctypes.util import find_library

import datetime
import os
import Queue
import threading

from fetch_keys_linux import *

from update_dict_lda_and_Am import *

from dime_search import *

#Includes the definition of clickable label
from ExtendedQLabel import *

#For getting web page title
#import lxml.html
import urllib2
from BeautifulSoup import BeautifulSoup

#
import re

#For checking data types
import types

################################################################

# linux only!
assert("linux" in sys.platform)

class MyApp(QtGui.QWidget):
 def __init__(self, parent=None):
  QtGui.QWidget.__init__(self, parent)

  #Read user.ini file
  self.srvurl, self.username, self.password, self.time_interval, self.nspaces, self.nwords, self.updateinterval = self.read_user_ini()
  self.data = []
  self.keywords = ''


  #Create visible stuff
  val = 5
  iconfile = 'web.png'
  self.gbtitle = QtGui.QLabel('Web sites')
  self.listWidget1 = self.create_QListWidget(20, iconfile)

  iconfile = 'mail.png'
  self.gbtitle2 = QtGui.QLabel('E-Mails')
  self.listWidget2 = self.create_QListWidget(20, iconfile)

  iconfile = 'doc.png'
  self.gbtitle3 = QtGui.QLabel('Docs')
  self.listWidget3 = self.create_QListWidget(20, iconfile)


  #Buttons
  #Start button
  self.testButton  = QtGui.QPushButton("Start")
  self.connect(self.testButton, QtCore.SIGNAL("released()"), self.test_pressed)

  #Radio buttons for choosing search function
  self.radiobutton1= QtGui.QRadioButton("DocSim")
  #self.radiobutton1.emit(QtCore.SIGNAL('released()'))
  self.connect(self.radiobutton1, QtCore.SIGNAL("released()"), self.choose_search_function1)

  self.radiobutton2= QtGui.QRadioButton("LinRel")
  #self.radiobutton2.emit( QtCore.SIGNAL('released()'))
  self.connect(self.radiobutton2, QtCore.SIGNAL("released()"), self.choose_search_function2)

  self.radiobutton3= QtGui.QRadioButton("LinRel (omitting history)")
  #self.radiobutton2.emit( QtCore.SIGNAL('released()'))
  self.connect(self.radiobutton3, QtCore.SIGNAL("released()"), self.choose_search_function3)

  self.radiobutton4= QtGui.QRadioButton("LinRel Keyword Search")
  #self.radiobutton2.emit( QtCore.SIGNAL('released()'))
  self.connect(self.radiobutton4, QtCore.SIGNAL("released()"), self.choose_search_function4)  

  #
  self.buttonlist = []


  #Layout for Web Pages
  self.vlayout1 = QtGui.QVBoxLayout()
  self.vlayout1.addWidget(self.gbtitle)
  self.vlayout1.addWidget(self.listWidget1)
  #
  self.vlayout2 = QtGui.QVBoxLayout()
  self.vlayout2.addWidget(self.gbtitle2)
  self.vlayout2.addWidget(self.listWidget2)
  #  
  self.vlayout3 = QtGui.QVBoxLayout()
  self.vlayout3.addWidget(self.gbtitle3)
  self.vlayout3.addWidget(self.listWidget3)
  #
  self.vlayout4 = QtGui.QVBoxLayout()
  #self.vlayout4.addWidget(QtGui.QLabel(' '))
  self.vlayout4.addWidget(self.testButton)
  #vlayout5 is a sub layout for vlayout4
  self.vlayout5 = QtGui.QVBoxLayout()
  self.vlayout5.addWidget(self.radiobutton1)
  self.vlayout5.addWidget(self.radiobutton2)
  #self.vlayout5.addWidget(self.radiobutton3)
  self.vlayout5.addWidget(self.radiobutton4)
  #Groupbox for radiobuttons
  self.mygroupbox = QtGui.QGroupBox('Search Method')
  self.mygroupbox.setLayout(self.vlayout5)
  self.vlayout4.addWidget(self.mygroupbox)

  #Add layouts
  self.hlayout = QtGui.QHBoxLayout()
  self.hlayout.addLayout(self.vlayout1)
  self.hlayout.addLayout(self.vlayout2)
  self.hlayout.addLayout(self.vlayout3)
  self.hlayout.addLayout(self.vlayout4)

  #Master vertical layout:
  self.mastervlayout = QtGui.QVBoxLayout(self)

  #Add self.hlayout to self.mastervlayout
  self.mastervlayout.addLayout(self.hlayout)

  #
  self.hlayout2 = QtGui.QHBoxLayout()
  self.keywordlabel = QtGui.QLabel('Suggested keywords: ')
  self.keywordlabel.setStyleSheet('color: green')
  self.hlayout2.addWidget(self.keywordlabel)
  #
  self.hlayout3 = QtGui.QHBoxLayout()
  #Create buttons
  self.buttonlist = []
  numofkwbuttons = 10
  for i in range(numofkwbuttons):
                  #keywordstr = keywordstr + urlstrs[i] + ', '
                  dumbutton = QtGui.QPushButton('button'+ str(i))
                  self.buttonlist.append(dumbutton)
  for i in range( len(self.buttonlist) ):
                  self.buttonlist[i].hide()
                  #keywordstr = keywordstr + urlstrs[i] + ', '
                  self.hlayout3.addWidget(self.buttonlist[i])
                  self.connect(self.buttonlist[i], QtCore.SIGNAL("clicked()"), self.emit_search_command)
                  #Hide buttons initially


  #
  self.mastervlayout.addWidget(self.keywordlabel)
  #Add self.hlayout2 to self.mastervlayout
  self.mastervlayout.addLayout(self.hlayout2)
  self.mastervlayout.addLayout(self.hlayout3)

  #
  self.setWindowTitle("ProActive Search") 

 #Runs the Keylogger and Search 
 def test_pressed(self):
  print 'Main: Test'
  self.testButton.setDisabled(True)
  #self.listwidget.clear()

  #Create  thread objects
  self.LoggerThreadObj  = LoggerThread()
  self.SearchThreadObj = SearchThread()

  #Data connection from logger thread to search thread
  self.connect(self.LoggerThreadObj, QtCore.SIGNAL("update(QString)"), self.SearchThreadObj.get_new_word)
  #self.connect(self.SearchThreadObj, QtCore.SIGNAL("finished(PyQt_PyObject)"), self.update_links_and_kwbuttons)

  #Data connections from search thread to main thread
  self.connect(self.SearchThreadObj, QtCore.SIGNAL("finished(PyQt_PyObject)"), self.get_data_from_search_thread_and_update_visible_stuff)
  self.connect(self.SearchThreadObj, QtCore.SIGNAL("finished(PyQt_PyObject)"), self.get_keywords_from_search_thread_and_update_visible_stuff)

  #Data connections from main thread to search thread
  self.connect(self, QtCore.SIGNAL("finished(PyQt_PyObject)"), self.SearchThreadObj.change_search_function)
  self.connect(self, QtCore.SIGNAL("update(QString)"), self.SearchThreadObj.get_new_word_from_main_thread)
  
  #Start thread processes
  self.LoggerThreadObj.start()
  self.SearchThreadObj.start()

 def emit_search_command(self):
  #if searchfuncid == 0:
    sender = self.sender()
    print 'Main: Sending new word from main: ',  sender.text().toAscii()
    self.emit(QtCore.SIGNAL('update(QString)'),sender.text())

 def choose_search_function1(self):
  #if searchfuncid == 0:
    print 'Main: Search function is DocSim'
    self.emit(QtCore.SIGNAL('finished(PyQt_PyObject)'), 0)
  # elif searchfuncid == 1:
  #   print 'Main: Search function is LinRel'

 def choose_search_function2(self):
  #if searchfuncid == 0:
    print 'Main: Search function is LinRel'
    self.emit(QtCore.SIGNAL('finished(PyQt_PyObject)'), 1)
  #elif searchfuncid == 1:
  #  print 'Main: Search function is LinRel'

 def choose_search_function3(self):
  #if searchfuncid == 0:
    print 'Main: Search function is LinRel'
    self.emit(QtCore.SIGNAL('finished(PyQt_PyObject)'), 2)
  #elif searchfuncid == 1:
  #  print 'Main: Search function is LinRel'

 def choose_search_function4(self):
  #if searchfuncid == 0:
    print 'Main: Search function is LinRel'
    self.emit(QtCore.SIGNAL('finished(PyQt_PyObject)'), 3)
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

    listWidget.connect(listWidget,SIGNAL("itemClicked(QListWidgetItem*)"),
              self.open_url)

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

 #
 def update_links_and_kwbuttons(self, urlstrs):
    i = 0
    j = 0
    k = 0

    # if len(urlstrs) > 0:
    # if type(urlstrs) is types.ListType:
    #   #
    #   if type(urlstrs[0]) is types.UnicodeType and  :
    #     print 'Main: update_links: got a list of keywords!!!'
    #     keywordstr = 'Suggested keywords: '
    #     print 'Main suggested keywords: ', urlstrs
    #     ncols = self.hlayout3.count()
    #     print 'Num of widgets ', ncols
    #     #Remove old buttons
    #     if len(self.buttonlist) > 0:
    #       for i in range( len(urlstrs) ):
    #                       #keywordstr = keywordstr + urlstrs[i] + ', ' 
    #                       #self.hlayout2.removeWidget(self.buttonlist[i])                  
    #                       #self.hlayout3.itemAt(i).widget().setParent(None) 
    #                       #self.hlayout3.itemAt(i).setParent(None)
    #                       if i < ncols:
    #                         self.buttonlist[i].setText(str(urlstrs[i]))
    #                         self.buttonlist[i].show()
    #     #print urlstrs
    #     return
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

          nlinks = 15
          nsuggestedlinks = 5
          for ijson in range( len(urlstrs) ):
                                      #title    = None
                                      linkstr  = self.unicode_to_str( urlstrs[ijson]["uri"] )
                                      ctime    = str(urlstrs[ijson]["timeCreated"])
                                      typestr  = str(urlstrs[ijson]["type"])
                                      storedas = str(urlstrs[ijson]["isStoredAs"])
                                      dataid   = str(urlstrs[ijson]["id"])
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
                                          self.listWidget3.item(j).setText(visiblestr) 
                                          self.listWidget3.item(j).setWhatsThis(linkstr+"*"+linkstr2)
                                          self.listWidget3.item(j).setToolTip(tooltipstr)
                                          self.listWidget3.item(j).setHidden(False)
                                          #self.datelist3[j].setText(datestr)
                                          #self.labellist3[j].setAlignment(Qt.AlignLeft)
                                          j = j + 1
                                      elif storedasl in ["MailboxDataObject"]:
                                          #print 'Main: mail ', storedasl

                                          #Create link to DiMe server
                                          dumlink = self.srvurl.split('/')[2]
                                          linkstr = linkstr2 = 'http://' + dumlink + '/infoelem?id=' + dataid
                                          #print 'Main: linkstr ', linkstr
                                          visiblestr = linkstrshort + '  ' + datestr
                                          self.listWidget2.item(k).setText(visiblestr) 
                                          self.listWidget2.item(k).setWhatsThis(linkstr+'*'+linkstr2)
                                          self.listWidget2.item(k).setToolTip(tooltipstr)
                                          self.listWidget2.item(j).setHidden(False)
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

                                        if title is None:
                                          #print 'Main: Web page title is: ', title
                                          title = linkstrshort

                                        #Create link to DiMe server
                                        dumlink = self.srvurl.split('/')[2]
                                        linkstr2 = 'http://' + dumlink + '/infoelem?id=' + dataid                                    

                                        visiblestr = title + '  ' + datestr
                                        self.listWidget1.item(i).setText(visiblestr) 
                                        self.listWidget1.item(i).setWhatsThis(linkstr+'*'+linkstr2)
                                        self.listWidget1.item(i).setToolTip(tooltipstr)
                                        self.listWidget1.item(i).setHidden(False)
                                        i = i + 1  


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
          print 'Main suggested keywords: ', keywordlist
          ncols = self.hlayout3.count()
          print 'Num of widgets ', ncols
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

 #
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
        return ustr.encode('utf-8')
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





#--------------------------------------------------------

#
class SearchThread(QtCore.QThread):

 def __init__(self):
  QtCore.QThread.__init__(self)
  self.query = 'Hello User'
  self.oldquery = None
  self.searchfuncid = 0
  self.extrasearch = False

 def __del__(self):
   self.wait()

 def change_search_function(self, searchfuncid):
  self.searchfuncid = searchfuncid
  print 'Search thread: search function changed to', str(searchfuncid)
  if searchfuncid == 1 or searchfuncid == 2 or searchfuncid == 3:
    #Update LinRel data files
    print 'Search thread: Updating Linrel data files!!!'
    print 'Search thread: path: ', os.getcwd()
    check_update()

 def get_new_word(self, newquery):
  #newquer is a QString, so it has to be changed to a unicode string
  asciiquery = newquery.toAscii()
  #Convert to Unicode
  newquery = unicode(asciiquery, 'utf-8')
  #newquery = unicode(newquery)
  print "Search thread: got new query:", newquery
  self.query = newquery

 def get_new_word_from_main_thread(self, keywords):
  if self.query is None:
    self.query = ''
  #
  utf8keyword = keywords.toUtf8()
  print 'ASCII KEYWORD: ', utf8keyword
  keywords = unicode(utf8keyword, 'utf-8')
  self.query = self.query + ' ' + keywords


  print "Search thread: got new query from main:", self.query
  self.extrasearch = True



 def run(self):
   self.search()

 def search(self):
  while True:

    if self.extrasearch:
      print 'Search thread: got extra search command from main!'      
      jsons, docinds = search_dime_docsim(dstr)      
      self.extrasearch = False    

    sleep(0.3) # artificial time delay

    if self.query is not None and self.query != self.oldquery:
      #self.query = unicode(self.query, 'utf-8')
      dstr = self.query
      #dstr = unicode(dstr, 'utf-8')
      print 'Search thread:', dstr 


      if self.searchfuncid == 0:
        jsons, docinds = search_dime_docsim(dstr)      
        print 'Search thread: Ready for new search!'
      elif self.searchfuncid == 1:
        #Create/update relevant data files if necessary and store into 'data/' folder in current path batman 
        jsons, kws = search_dime_linrel_summing_previous_estimates(dstr)
        print 'Search thread: Ready for new search!'
        if len(jsons) > 0:
          #Return keyword list
          self.emit( QtCore.SIGNAL('finished(PyQt_PyObject)'), kws)
      elif self.searchfuncid == 2:
        #Create/update relevant data files if necessary and store into 'data/' folder in current path batman 
        jsons = search_dime_linrel_without_summing_previous_estimates(dstr)
        print 'Search thread: Ready for new search!'   
      elif self.searchfuncid == 3:
        #Create/update relevant data files if necessary and store into 'data/' folder in current path batman 
        jsons, kws = search_dime_linrel_keyword_search(dstr)   
        if len(jsons) > 0:
          #Return keyword list
          self.emit( QtCore.SIGNAL('finished(PyQt_PyObject)'), kws)      
        print 'Search thread: Ready for new search!'         
        

      print 'Search thread: len jsons ', len(jsons)
      if len(jsons) > 0:
       #Return keyword list
       #self.emit( QtCore.SIGNAL('finished(PyQt_PyObject)'), kws)
       #Return jsons
       self.emit( QtCore.SIGNAL('finished(PyQt_PyObject)'), jsons)

       #Write first url's appearing in jsons list to a 'suggested_pages.txt'
       cdate = datetime.datetime.now().date()
       ctime = datetime.datetime.now().time()
       f = open("suggested_pages.txt","a")
       f.write(str(cdate) + ' ' + str(ctime) + ' ' + str(jsons[0]["uri"]) + '\n')
       f.close()

    self.oldquery = self.query


#
class LoggerThread(QtCore.QThread):

  def __init__(self):
    QtCore.QThread.__init__(self)

  #Keylogger
  def run(self):
        print 'Logger thread: Run Run'
        #Read user.ini
        srvurl, username, password, time_interval, nspaces, nwords, updateinterval = read_user_ini()
        settingsl = [srvurl, username, password, time_interval, nspaces, nwords, updateinterval]

        #Number 
        numoftopics = 10

        #List of urls
        urlstr = []

        #global urlstr
        global var

        countspaces = 0
        sleep_interval = 0.005

        #starttime = datetime.datetime.now().time().second
        now = time()
        dumstr = ''
        wordlist = []

        print "Logger thread: Ready for logging"

        while True:

          sleep(0.005)
          changed, modifiers, keys = fetch_keys()

          #print modifiers
          #print changed, modifiers, keys
          keys  = str(keys)
          

          #Take care that ctrl is not pressed at the same time
          if not (modifiers['left ctrl'] or modifiers['right ctrl']):
            #Take current time
            cdate = datetime.datetime.now().date()
            ctime = datetime.datetime.now().time()

            cmachtime = time()
            var2 = cmachtime > now + float(time_interval)
            var3 = cmachtime > now + float(updateinterval)

            if keys == 'None':
                    keys = ''

            elif keys == '<backspace>':
                    keys = ''
                    #Convert current string into list of characters
                    duml = list(dumstr)
                    if len(duml) > 0:
                            #Delete the last character from the string list
                            del( duml[len(duml)-1] )
                            #Convert back to string
                            dumstr = "".join(duml)

            elif keys in ['<enter>', '<tab>','<right ctrl>','<left ctrl>',' ']:
                    print 'Logger thread: keys: ', keys
                    print 'Logger thread: changed: ', changed[0]
                    #keys = ' '
                    wordlist.append(dumstr)
                    #print wordlist
                    print 'Logger thread: wordlist:', wordlist[-nwords:]
                    dwordlist = wordlist[-nwords:]
                    #dumstr = dumstr + keys
                    countspaces = countspaces + 1
                    dumstr = ''
                    dumstr2 = ''
                    for i in range( len(dwordlist) ):
                        dumstr2 = dumstr2 + dwordlist[i] + ' '

                    #Print the typed words to a file 'typedwords.txt'
                    f = open('typedwords.txt', 'a')
                    f.write(str(cdate) + ' ' + str(ctime) + ' ' + dumstr2 + '\n')

                    #Emit the typed words to a search thread
                    self.emit( QtCore.SIGNAL('update(QString)'), dumstr2)

                    if var2:
                      #Empty the dumstr2 after time_interval period of time
                      dumstr2 = ''

            else:
                    cdate = datetime.datetime.now().date()
                    ctime = datetime.datetime.now().time()
                    dumstr = dumstr + keys


def read_user_ini():

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

def unicode_to_str(ustr):
  """Converts unicode strings to 8-bit strings."""
  try:
      return ustr.encode('utf-8')
  except UnicodeEncodeError:
      print "Main: UnicodeEncodeError"
  return ""


# run
app  = QtGui.QApplication(sys.argv)
test = MyApp()
test.show()
app.exec_()

