#!/usr/bin/python
# -*- coding: utf-8 -*-

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


#For keylogging
from fetch_keys_osx import *

#For searching from DiMe 
from dime_search import *

#For GUI
from PyQt4 import QtCore, QtGui, uic
#
from PyQt4.QtGui import *
from PyQt4.QtCore import *

#Includes the definition of clickable label
from ExtendedQLabel import *

#
import re

#
from update_dict_lda_and_Am import *

#
import subprocess

#
import os

# Definition of GUI
class Window(QtGui.QWidget):
    def __init__(self, val):
        QtGui.QWidget.__init__(self)

        #Read user.ini file
        self.srvurl, self.username, self.password, self.time_interval, self.nspaces, self.nw, self.updateinterval = self.read_user_ini()

        # mygroupbox.setLayout(myform)
        urlstrs = ''
        iconfile = 'web.png'
        self.gbtitle = 'Web sites'
        self.labellist, self.datelist = self.create_labellist(val, urlstrs)
        self.scrollarea = self.create_groupbox(self.gbtitle, self.labellist, self.datelist, iconfile)
        iconfile = 'mail.png'
        self.gbtitle2= 'E-mails'
        self.labellist2, self.datelist2 = self.create_labellist(val, urlstrs)
        self.scrollarea2 = self.create_groupbox(self.gbtitle2, self.labellist2, self.datelist2, iconfile)
        iconfile = 'doc.png'
        self.gbtitle3= 'Docs'
        self.labellist3, self.datelist3 = self.create_labellist(val, urlstrs)
        self.scrollarea3 = self.create_groupbox(self.gbtitle3, self.labellist3, self.datelist3, iconfile)

        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(self.scrollarea)
        layout.addWidget(self.scrollarea2)
        layout.addWidget(self.scrollarea3)

        self.setWindowTitle("ProActive Search")

    def create_labellist(self, val, urlstrs):
        labellist = []
        datelist = []
        if len(urlstrs) > 0:
          for i in range( len(urlstrs) ):
                          linkstr = str( urlstrs[i]["uri"] )
                          ctime   = str(urlstrs[i]["timeCreated"])
                          typestr = str(urlstrs[i]["type"])
                          storedas = str(urlstrs[i]["isStoredAs"])
                          #print ctime
                          timeint = int(ctime) / 1000
                          #print timeint
                          date = datetime.datetime.fromtimestamp(timeint)
                          datestr = date.__str__()

                          labellist[i].setText(linkstr)
                          datelist[i].setText(datestr)
                          storedasl = storedas.split('#')[1]
                          #if typestr in ['http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#PaginatedTextDocument', 'http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#Document']:
                          #print storedasl
                          if storedasl in ["LocalFileDataObject" ]:
                              labellist3[j].setText(linkstr)
                              j = j + 1
        else:
          for i in range(val):
              #dumlabel = ExtendedQLabel('Hello')
              dumlabel = ExtendedQLabel()
              dumlabel.setAlignment(Qt.AlignLeft)
              dumlabel.connect(dumlabel, SIGNAL('clicked()'), dumlabel.open_url)
              #labellist.append(QtGui.QLabel('mylabel'))
              labellist.append(dumlabel)

              datelist.append(QtGui.QLabel('date'))

        return labellist, datelist

    def update_labellist(self, urlstrs):
        j=0

        labellist  = []
        labellist2 = []
        labellist3 = []
        datelist  = []
        datelist2 = []
        datelist3 = []
        if len(urlstrs) > 0:
          for i in range( len(urlstrs) ):
                          linkstr = str( urlstrs[i]["uri"] )
                          ctime   = str(urlstrs[i]["timeCreated"])
                          typestr = str(urlstrs[i]["type"])
                          storedas = str(urlstrs[i]["isStoredAs"])

                          dumlabel = ExtendedQLabel(linkstr, self)
                          dumlabel.connect(dumlabel, SIGNAL('clicked()'), dumlabel.open_url)      

                          #print ctime
                          timeint = int(ctime) / 1000
                          #print timeint
                          date = datetime.datetime.fromtimestamp(timeint)
                          datestr = date.__str__()

                          labellist.append(dumlabel)
                          datelist.append(datestr)

                          storedasl = storedas.split('#')[1]
                          #if typestr in ['http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#PaginatedTextDocument', 'http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#Document']:
                          #print storedasl
                          if storedasl in ["LocalFileDataObject" ]:
                              dumlabel = ExtendedQLabel()
                              dumlabel.connect(dumlabel, SIGNAL('clicked()'), dumlabel.open_url)                                        
                              labellist3[j].setText(linkstr)
                              j = j + 1
        else:
          pass

        labellist2 = labellist
        datelist2 = datelist

        self.labellist = labellist
        self.labellist2= labellist2
        self.labellist3= labellist3

        self.datelist = datelist
        self.datelist2= datelist2
        self.datelist3= datelist3
        #return labellist, labellist2, labellist3, datelist, datelist2, datelist3


    def create_groupbox(self, gbtitle, labellist, datelist, iconfile):
        mygroupbox = QtGui.QGroupBox(gbtitle)
        myform = QtGui.QFormLayout()
        #self.labellist = []
        #self.datelist = []
        combolist = []

        #
        for i in range(len(labellist)):
            #dumlabel = ExtendedQLabel('Hello', self)
            #dumlabel.connect(dumlabel, SIGNAL('clicked()'), dumlabel.open_url)
            #self.labellist.append(dumlabel)

            datelist.append(QtGui.QLabel('date'))

            #
            image = QtGui.QImage(iconfile)
            icon = QtGui.QPixmap.fromImage(image)
            icon = icon.scaledToHeight(20)
            
            label1 = QtGui.QLabel('Hello')

            label1.setPixmap(icon)
            label2 = QtGui.QLabel('test_urls')
            #label2.setPicture(picture)
            grid = QtGui.QGridLayout()
            grid.setSpacing(2)
            grid.addWidget(label1,1,0, Qt.AlignLeft)
            #grid.setHorizontalSpacing(1)
            grid.addWidget(labellist[i],1,1,Qt.AlignLeft)
            #grid.addWidget(datelist[i],1,2, Qt.AlignRight)
            myform.addItem(grid)
            #myform.addRow(labellist[i])
        
        mygroupbox.setLayout(myform)

        scrollarea = QtGui.QScrollArea()
        scrollarea.setWidget(mygroupbox)
        scrollarea.setWidgetResizable(True)
        
        return scrollarea
        #return mygroupbox 


    def update_groupbox(self, iconfile):
        mygroupbox = QtGui.QGroupBox(self.gbtitle)
        myform = QtGui.QFormLayout()
        #self.labellist = []
        #self.datelist = []
        combolist = []

        #
        for i in range(len(self.labellist)):
            #self.datelist[i] = '20.09.2015'

            #
            image = QtGui.QImage(iconfile)
            icon = QtGui.QPixmap.fromImage(image)
            icon = icon.scaledToHeight(20)
            label1 = QtGui.QLabel('')
            label1.setPixmap(icon)

            #label2.setPicture(picture)
            grid = QtGui.QGridLayout()
            grid.setSpacing(10)
            grid.addWidget(label1,1,0)
            grid.addWidget(self.labellist[i],1,1)
            grid.addWidget(QtGui.QLabel('Date'),1,2)
            myform.addItem(grid)
            #myform.addRow(labellist[i])
        
        mygroupbox.setLayout(myform)

        scrollarea = QtGui.QScrollArea()
        scrollarea.setWidget(mygroupbox)
        scrollarea.setWidgetResizable(True)
        
        self.scrollarea = scrollarea

    def startlog(self):
        threading.Thread(target = log_osx, args = (self,) ).start()

    def show_link(self):
        threading.Thread(target = update_visible_link, args = (self,)).start()


    def update_links3(self, urlstrs):
        i = 0
        j = 0

        #Initialize rake object
        rake_object = rake.Rake("SmartStoplist.txt", 5, 3, 4)

        if urlstrs != None:
             nsuggestedlinks = len(urlstrs)
             nlinks = len(self.labellist)
        nlinks = len(self.labellist)
        nsuggestedlinks = 5
        if nsuggestedlinks <= nlinks:
                    #for i in range( len(self.labellist) ):
                    for i in range( len(urlstrs) ):
                                    linkstr  = str( urlstrs[i]["uri"] )
                                    ctime    = str(urlstrs[i]["timeCreated"])
                                    typestr  = str(urlstrs[i]["type"])
                                    storedas = str(urlstrs[i]["isStoredAs"])
                                    content  = urlstrs[i]["plainTextContent"]
                                    keywords = rake_object.run(content)
                                    #print ctime
                                    timeint = int(ctime) / 1000
                                    #print timeint
                                    date = datetime.datetime.fromtimestamp(timeint)
                                    datestr = date.__str__()

                                    if len(keywords) > 0:
                                      tooltipstr = re.sub("[^\w]", " ", content)
                                      self.labellist[i].setToolTip(tooltipstr)
                                      self.labellist[i].setText(keywords[0][0])
                                    else:
                                      pass
                                    self.labellist[i].uristr = linkstr
                                    self.datelist[i].setText(datestr)
                                    storedasl = storedas.split('#')[1]
                                    #if typestr in ['http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#PaginatedTextDocument', 'http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#Document']:
                                    #print storedasl
                                    if storedasl in ["LocalFileDataObject" ]:
                                        self.labellist3[j].setText(linkstr)
                                        self.labellist3[j].setAlignment(Qt.AlignLeft)
                                        j = j + 1


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
                        numwords = int(nspaces_string)                      
                if stringlist[i] == "updating_interval:":
                        dum_string = stringlist[i+1]
                        updateinterval = float(dum_string)                        

        return srvurl, usrname, password, time_interval, nspaces, numwords, updateinterval

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

def log_osx(win):

    #number of topics
    numoftopics = 10

    #Number of words taken from keyboard stream
    nw = win.nw

    #
    urlstr = ''

    #global urlstr
    global var
    
    sleep_interval = win.time_interval
    timeinterval = win.time_interval
    update_time_interval = win.time_interval + 20.0
    #starttime = datetime.datetime.now().time().second
    starttime = time()

    querystrprev = ''

    #Before searching, update data
    update_data(win.srvurl, win.username, win.password)
    update_dictionary()
    update_doctm()
    update_topic_model_and_doctid(numoftopics)
    #update_topic_keywords()
    update_docsim_model()
    update_X()
    update_Xt_and_docindlist([0])

    print "Ready for logging!"

    while var:
        now = time()
        print now    
        #Update dictionary, lda -model and A matrix
        if now > starttime + update_time_interval:
            #Update stuff
            #Before searching, update data
            update_data(win.srvurl, win.username, win.password)
            update_dictionary()
            update_doctm()
            update_topic_model_and_doctid(numoftopics)
            #update_topic_keywords()
            update_docsim_model()
            update_X()
            update_Xt_and_docindlist([0])          
            #
            starttime = time()
        #
        sleep(sleep_interval)
        
        #Take current time
        cdate = datetime.datetime.now().date()
        ctime = datetime.datetime.now().time()
        
        cmachtime = time()
        var2 = cmachtime > now + win.time_interval

        #Open file of typed words
        #and take nw last words from 'typedwords.txt'
        if os.path.isfile('typedwords.txt'):
            f = open("typedwords.txt", "r")
            dstrl  = f.read().split()
            f.close()
        else:
            dstrl = ''

        querystrl= dstrl[len(dstrl)-nw:len(dstrl)]
        querystr = " ".join(querystrl)
        print "Typed words: ", querystr

        if querystr != querystrprev:
            #Make query to DiMe
            #urlstr = search_dime(win.username, win.password, querystr)
            #urlstr = search_dime_lda(win.username, win.password, dstr2)
            #urlstr = search_dime_linrel(win.username, win.password, dstr2)
            urlstr = search_dime_linrel_summing_previous_estimates(querystr)

        #print urlstr[0]
        querystrprev = querystr

        #Update visible links
        if len(urlstr) > 0:
            win.update_links3(urlstr)

        #Add the suggested url into a history file
        if len(urlstr) > 0:
            f2 = open("suggested_pages.txt","a")
            #f2.write(str(cdate) + ' ' + str(ctime) + ' ' + str(urlstr.json()[0]["uri"]) + '\n')
            f2.write(str(cdate) + ' ' + str(ctime) + ' ' + str(urlstr[0]["uri"]) + '\n')
            f2.close()
                
        now = time()    


if __name__ == "__main__":

  #Important global variables!
  global urlstr
  #Initialize urlstr
  #urlstr = search_dime("petrihiit","p3tr1h11t","python")

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
  newwindow = Window(5)

  #Make window frameless
  #newwindow.setWindowFlags(QtCore.Qt.CustomizeWindowHint)

  newwindow.show()

  #Move the window into the right corner
  newwindow.move(sl-350,0)



  #Determine the dimensions
  newwindow.resize(sl-100, 50)

  #Start keylogger
  newwindow.startlog()

  #Start
  app.exec_()
