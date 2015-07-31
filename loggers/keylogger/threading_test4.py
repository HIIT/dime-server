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

################################################################

# linux only!
assert("linux" in sys.platform)

class MyApp(QtGui.QWidget):
 def __init__(self, parent=None):
  QtGui.QWidget.__init__(self, parent)
 
  # self.setGeometry(300, 300, 280, 600)
  # self.setWindowTitle('threads')
 
  # self.layout = QtGui.QVBoxLayout(self)
 
  self.testButton = QtGui.QPushButton("Start")
  self.connect(self.testButton, QtCore.SIGNAL("released()"), self.test_pressed)
  #self.listwidget = QtGui.QListWidget(self)
 
  # self.layout.addWidget(self.testButton)
  # self.layout.addWidget(self.listwidget)


  #QtGui.QWidget.__init__(self)

  #Read user.ini file
  self.srvurl, self.username, self.password, self.time_interval, self.nspaces, self.nwords, self.updateinterval = self.read_user_ini()

  # mygroupbox.setLayout(myform)
  val = 5
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
  layout.addWidget(self.testButton)

  self.setWindowTitle("ProActive Search")  

 def add(self, text):
  """ Add item to list widget """
  print "Add: " + text[0]['plainTextContent']
  self.listwidget.addItem(text[0]['uri'])
  self.listwidget.sortItems()
 
 def addBatch(self,text="test",iters=6,delay=0.3):
  """ Add several items to list widget """
  for i in range(iters):
   sleep(delay) # artificial time delay
   self.add(text+" "+str(i))
 
 def test_pressed(self):
  print 'Main: Test'
  self.testButton.setDisabled(True)
  #self.listwidget.clear()

  self.WorkThreadObj  = LoggerThread()
  self.SearchThreadObj = SearchThread()
  self.connect(self.WorkThreadObj, QtCore.SIGNAL("update(QString)"), self.SearchThreadObj.get_new_word)
  #self.connect( self.SearchThreadObj, QtCore.SIGNAL("update(QString)"), self.add )
  #self.connect( self.SearchThreadObj, QtCore.SIGNAL("finished(PyQt_PyObject)"), self.add )
  self.connect( self.SearchThreadObj, QtCore.SIGNAL("finished(PyQt_PyObject)"), self.update_links )

  self.WorkThreadObj.start()
  self.SearchThreadObj.start()

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
                          if storedasl in ["LocalFileDataObject"]:
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


 def create_groupbox(self, gbtitle, labellist, datelist, iconfile):
    mygroupbox = QtGui.QGroupBox(gbtitle)
    #myform = QtGui.QFormLayout()
    myform = QtGui.QVBoxLayout()
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
        
        boxl = QtGui.QHBoxLayout()
        boxl.setSpacing(10)
        boxl.addWidget(label1, Qt.AlignLeft)
        boxl.addWidget(labellist[i], Qt.AlignLeft)
        boxl.addWidget(datelist[i], Qt.AlignLeft)
        boxl.addStretch(10)
        myform.addItem(boxl)
        # #grid = QtGui.QGridLayout()
        # grid.setSpacing(2)
        # grid.addWidget(label1,1,0, Qt.AlignLeft)
        # #grid.setHorizontalSpacing(1)
        # grid.addWidget(labellist[i],1,1,Qt.AlignLeft)
        # #grid.addWidget(datelist[i],1,2, Qt.AlignRight)
        # myform.addItem(grid)
        # #myform.addRow(labellist[i])
    
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


 def update_links(self, urlstrs):
    i = 0
    j = 0
    k = 0

    #Initialize rake object
    rake_object = rake.Rake("SmartStoplist.txt", 5, 5, 4)

    if urlstrs != None:
         nsuggestedlinks = len(urlstrs)
         nlinks = len(self.labellist)
    nlinks = len(self.labellist)
    nsuggestedlinks = 5
    if nsuggestedlinks <= nlinks:
                #for i in range( len(self.labellist) ):
                for i in range( len(urlstrs) ):
                                linkstr  = self.unicode_to_str( urlstrs[i]["uri"] )
                                ctime    = str(urlstrs[i]["timeCreated"])
                                typestr  = str(urlstrs[i]["type"])
                                storedas = str(urlstrs[i]["isStoredAs"])
                                dataid   = str(urlstrs[i]["id"])
                                storedasl = storedas.split('#')[1]
                                print 'Main storedasl: ', storedasl
                                content  = self.safe_get_value(urlstrs[i], "plainTextContent")
                                keywords = rake_object.run(content)
                                #print ctime
                                timeint = int(ctime) / 1000
                                #print timeint
                                date = datetime.datetime.fromtimestamp(timeint)
                                datestr = date.__str__()

                                if len(linkstr) > 20:
                                  linkstrshort = linkstr[0:40]
                                

                                if len(keywords) > 0:
                                  tooltipstr = re.sub("[^\w]", " ", content)
                                  #self.labellist[i].setToolTip(tooltipstr)
                                  keywordstr = "Keywords: " + keywords[0][0]
                                else:
                                  keywordstr = 'Keywords: '
                                  #self.labellist[i].setText(keywords[0][0])

                                if storedasl in ["LocalFileDataObject" ]:
                                    print 'Main: doc', linkstr
                                    self.labellist3[j].setText(linkstrshort) 
                                    self.labellist3[j].uristr = linkstr
                                    self.labellist3[j].setToolTip(keywordstr)
                                    self.datelist3[j].setText(datestr)
                                    #self.labellist3[j].setAlignment(Qt.AlignLeft)

                                    j = j + 1
                                elif storedasl in ["MailboxDataObject"]:
                                    print 'Main: mail ', storedasl
                                    dumlink = self.srvurl.split('/')[2]
                                    linkstr = 'http://' + dumlink + '/message?id=' + dataid
                                    print 'linkstr ', linkstr
                                    self.labellist2[k].setText(linkstrshort)
                                    self.labellist2[k].uristr = linkstr
                                    self.labellist2[k].setToolTip(keywordstr)
                                    self.datelist2[k].setText(datestr)
                                    #self.labellist3[j].setAlignment(Qt.AlignLeft)

                                    k = k + 1                                  
                                else:
                                  print 'Main: web ', linkstr
                                  title = None
                                  try:
                                    dumt = urllib2.urlopen(linkstr)
                                    soup = BeautifulSoup(dumt)
                                    try: 
                                      if soup.title is not None:
                                        title = soup.title.string
                                    except (AttributeError, ValueError):
                                      #print 'attr. error'
                                      pass
                                  except (urllib2.HTTPError, urllib2.URLError, ValueError):
                                    pass

                                  if title is None:
                                    title = linkstrshort

                                  self.labellist[i].setText(title)
                                  self.labellist[i].uristr = linkstr
                                  self.labellist[i].setToolTip(keywordstr)
                                  self.datelist[i].setText(datestr)
                                    

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


 def unicode_to_str(self, ustr):
    """Converts unicode strings to 8-bit strings."""
    try:
        return ustr.encode('utf-8')
    except UnicodeEncodeError:
        print "UnicodeEncodeError"
    return ""


 def safe_get_value(self, dicti, key):
    if dicti.has_key(key):
        return dicti[key]
    return ''

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
  self.query = None
  self.oldquery = None

 def __del__(self):
   self.wait()

 def get_new_word(self, newquery):
  print "SearchThread: got new query:", newquery
  self.query = newquery

 def run(self):
   self.search()

 def search(self):
  while True:
   sleep(0.3) # artificial time delay
   if self.query is not None and self.query != self.oldquery:
    dstr = str(self.query)
    print 'SearchThread:', dstr 
   
    jsons = search_dime_linrel_summing_previous_estimates(dstr)
    print 'len jsons', len(jsons)
    if len(jsons) > 0:
     #content = str(jsons[0]['uri'])
     #print jsons[0]
     #self.emit( QtCore.SIGNAL('update(QString)'), content)
     self.emit( QtCore.SIGNAL('finished(PyQt_PyObject)'), jsons)

    self.oldquery = self.query


#
class LoggerThread(QtCore.QThread):

  def __init__(self):
    QtCore.QThread.__init__(self)

  #Keylogger
  def run(self):
        print 'Run Run'
        #Read user.ini
        srvurl, username, password, time_interval, nspaces, nwords, updateinterval = read_user_ini()

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

        #Before searching, update data
        if os.path.isfile('json_data.txt') and os.path.isfile('/tmp/tmpdict.dict'):
          pass
        else:
          update_data(srvurl, username, password)
          update_dictionary()
      
        if os.path.isfile('doctm.data') and os.path.isfile('varlist.list'):
          pass
        else:
          update_doctm()
          update_doc_tfidf_list()
          update_docsim_model()
          update_tfidf_model()
        
        if os.path.isfile('/tmp/similarityvec'):
          pass
        else:
          update_docsim_model()

        #update_X()
        if os.path.isfile('docindlist.list'):
          pass
        else:
          update_Xt_and_docindlist([0])

        #Create stopwordlist
        create_stopwordlist()

        print "Ready for logging"

        #f = open('typedwords.txt', 'a')
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
                    print 'keys: ', keys
                    print 'changed: ', changed[0]
                    #keys = ' '
                    wordlist.append(dumstr)
                    print wordlist
                    print wordlist[-nwords:]
                    #dumstr = dumstr + keys
                    countspaces = countspaces + 1
                    dumstr = ''
                    dumstr2 = ''
                    for i in range( len(wordlist) ):
                        dumstr2 = dumstr2 + wordlist[i] + ' '

                    self.emit( QtCore.SIGNAL('update(QString)'), dumstr2)

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
                    numwords = int(nspaces_string)                      
            if stringlist[i] == "updating_interval:":
                    dum_string = stringlist[i+1]
                    updateinterval = float(dum_string)  

    return srvurl, usrname, password, time_interval, nspaces, numwords, updateinterval


# run
app = QtGui.QApplication(sys.argv)
test = MyApp()
#test.test()
test.show()
app.exec_()

