# coding=UTF-8

from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5 import QtGui, QtCore

from fetch_keys_linux import *

import time
import datetime

#
class LoggerThread(QtCore.QThread):

  #update = pyqtSignal(unicode)
  update = pyqtSignal(str)

  def __init__(self):
    QtCore.QThread.__init__(self)
    self.dumstr2 = ''
    self.var = True
    self.wordlist = []

  def start_logger_loop(self):
    self.var = True

  def stop_logger_loop(self):
    self.var = False

  def clear_dumstring(self):
    print("Logger thread: dum string cleared!!")
    self.dumstr2 = ''
    self.wordlist = []

  #
  def insert_old_dumstring(self, old_dumstring):
    self.dumstr2 = old_dumstring
    #self.wordlist = old_dumstring.split()
    self.wordlist = self.dumstr2.split()
    print("Logger thread: old dum string inserted:", self.dumstr2, self.wordlist)



  #Keylogger 
  def run(self):
    print('Logger thread: Run Run')

    #Read user.ini
    srvurl, username, password, time_interval, nspaces, numwords, updateinterval = read_user_ini()
    settingsl = [srvurl, username, password, time_interval, nspaces, numwords, updateinterval]

    #Number 
    numoftopics = 10

    #List of urls
    urlstr = []

    #global urlstr
    global var
    #
    sleep_interval = 0.005
    nokeypress_interval = 4.0

    #starttime = datetime.datetime.now().time().second
    now = time.time()
    dumstr = ''
    
    string_to_send = None
    timestamp = now

    print("Logger thread: Ready for logging")

    while self.var:

      time.sleep(sleep_interval)
      changed, modifiers, keys = fetch_keys()

      #print modifiers
      #print changed, modifiers, keys
      keys  = str(keys)
      
      #Take care that ctrl is not pressed at the same time
      if not (modifiers['left ctrl'] or modifiers['right ctrl']):
        #Take current time
        cdate = datetime.datetime.now().date()
        ctime = datetime.datetime.now().time()

        cmachtime = time.time()
        var2 = cmachtime > now + float(time_interval)
        var3 = cmachtime > now + float(updateinterval)

        if keys == 'None':
          keys = ''
          #if cmachtime > timestamp + nokeypress_interval and string_to_send is not None:
          if string_to_send is not None:
            #self.emit( QtCore.SIGNAL('update(QString)'), string_to_send)
            self.update.emit(string_to_send)
            string_to_send = None
        #
        else:
          timestamp = time.time()
                                  
          if keys == '<backspace>':
            keys = ''
            #Convert current string into list of characters
            duml = list(dumstr)
            if len(duml) > 0:
              #Delete the last character from the string list
              del( duml[len(duml)-1] )
              #Convert back to string
              dumstr = "".join(duml)

          elif keys in ['<enter>', '<tab>','<right ctrl>','<left ctrl>',' ']:
            print('Logger thread: keys: ', keys)
            print('Logger thread: changed: ', changed[0])
            #keys = ' '
            self.wordlist.append(dumstr)
            #print wordlist
            print('Logger thread: wordlist:', self.wordlist[-numwords:])
            dwordlist = self.wordlist[-numwords:]

            dumstr = ''
            self.dumstr2 = ''
            for i in range( len(dwordlist) ):
              self.dumstr2 = self.dumstr2 + dwordlist[i] + ' '

            #Print the typed words to a file 'typedwords.txt'
            f = open('typedwords.txt', 'a')
            f.write(str(cdate) + ' ' + str(ctime) + ' ' + self.dumstr2 + '\n')

            string_to_send = self.dumstr2

            if var2:
              #Empty the dumstr2 after time_interval period of time
              self.dumstr2 = ''

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
