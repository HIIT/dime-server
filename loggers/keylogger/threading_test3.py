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



from dime_search import *
################################################################

# linux only!
assert("linux" in sys.platform)


 
class MyApp(QtGui.QWidget):
 def __init__(self, parent=None):
  QtGui.QWidget.__init__(self, parent)
 
  self.setGeometry(300, 300, 280, 600)
  self.setWindowTitle('threads')
 
  self.layout = QtGui.QVBoxLayout(self)
 
  self.testButton = QtGui.QPushButton("test")
  self.connect(self.testButton, QtCore.SIGNAL("released()"), self.test_pressed)
  self.listwidget = QtGui.QListWidget(self)
 
  self.layout.addWidget(self.testButton)
  self.layout.addWidget(self.listwidget)

 def add(self, text):
  """ Add item to list widget """
  print "Add: " + text
  self.listwidget.addItem(text)
  self.listwidget.sortItems()
 
 def addBatch(self,text="test",iters=6,delay=0.3):
  """ Add several items to list widget """
  for i in range(iters):
   sleep(delay) # artificial time delay
   self.add(text+" "+str(i))
 
 def test_pressed(self):
  print 'Main: Test'
  self.testButton.setDisabled(True)
  self.listwidget.clear()
  # adding entries just from main application: locks ui
  #self.addBatch("_non_thread",iters=6,delay=0.3)
  # adding by emitting signal in different thread
  self.WorkThreadObj  = LoggerThread()
  self.SearchThreadObj = SearchThread()
  self.connect(self.WorkThreadObj, QtCore.SIGNAL("update(QString)"), self.SearchThreadObj.get_new_word)
  self.connect( self.SearchThreadObj, QtCore.SIGNAL("update(QString)"), self.add )
  #self.connect( self.SearchThreadObj, QtCore.SIGNAL("update(str)"), self.add )
  #self.connect( self.workThread, QtCore.SIGNAL("update(QString)"), self.add )
  self.WorkThreadObj.start()
  self.SearchThreadObj.start()

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
   #dumstr = 'hello'
   #dstr = query.toUtf8()
   #dstr = dstr.__str__()
    dstr = str(self.query)
    print 'SearchThread:', dstr 
   
   #jsons = search_dime_linrel_summing_previous_estimates(dstr)
   #print 'len ', len(jsons)
   #if len(jsons):
   # content = str(jsons[0]['uri'])
    #self.emit( QtCore.SIGNAL('update(QString)'), "from work thread " + str(i) )

   # self.emit( QtCore.SIGNAL('update(QString)'), content)
    content = 'hello'
    self.emit( QtCore.SIGNAL('update(QString)'), content)
    self.oldquery = self.query
   #self.emit( QtCore.SIGNAL('update(str)'), content)

  #self.terminate()

# #
# class query_receiver_and_emitter(QtCore.QThread):
#     def __init__(self):
#         QtCore.QThread.__init__(self)
#     def take_querystrlist_and_emit_signal(querystrlist)
#         self.emit( QtCore.SIGNAL('update(QString)'), querystrlist[-nwords:])


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
          #update_data(srvurl, username, password)
          update_dictionary()
      
        if os.path.isfile('doctm.data') and os.path.isfile('varlist.list'):
          pass
        else:
          update_doctm()
          update_doc_tfidf_list()
          #update_docsim_model()
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
                    #self.emit( QtCore.SIGNAL('update(str)'), dumstr2[-nwords:])
                    #win.update_groupbox(iconfile)

                    # if var2:
                    #         if var3: 
                    #           #Update stuff
                    #           update_data(srvurl, username, password)
                    #           update_dictionary()
                    #           update_doctm()
                    #           update_docsim_model()
                    #           #update_X()
                    #           update_Xt_and_docindlist()                           
                    #         #
                    #         dumstr2 = ''
                    #         for i in range( len(wordlist) ):
                    #                dumstr2 = dumstr2 + wordlist[i] + ' ' 

                    #         self.emit( QtCore.SIGNAL('update(QString)'), dumstr2)
                    #         #self.emit( QtCore.SIGNAL('update(str)'), dumstr2)
                    #         #
                    #         f = open("typedwords.txt","a")
                    #         #print str(cdate) + ' ' + str(ctime) + ' ' + dumstr2 + '\n'
                    #         f.write(str(cdate) + ' ' + str(ctime) + ' ' + dumstr2 + '\n')
                    #         f.close()

                    #         #Clear the dummy string
                    #         dumstr = ''
                    #         dumstr2= ''

                    #         #Remove content from wordlist
                    #         del wordlist[:]

                    #         countspaces = 0

                    #         now = time()

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

