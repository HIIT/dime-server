# coding=UTF-8

from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5 import QtGui

import time
import datetime
import zmq

#
class LoggerThread(QThread):

  update = pyqtSignal(str)

  special_keys = {33: 'å', 39: 'ä', 41: 'ö'}
  
  def __init__(self):
    QThread.__init__(self)
    self.var = True
    self.context = zmq.Context()
    self.socket = self.context.socket(zmq.SUB)
    self.socket.connect("tcp://127.0.0.1:5000")
    self.socket.setsockopt_string(zmq.SUBSCRIBE, "")

    self.dumstr2 = ''
    self.wordlist = []

  def start_logger_loop(self):
    self.var = True


  def clear_dumstring(self):
    print("Logger thread: dum string cleared!!")
    self.dumstr2 = ''
    self.wordlist = []

  #
  def insert_old_dumstring(self, old_dumstring):
    self.dumstr2 = old_dumstring
    self.wordlist = self.dumstr2.split()
    print("Logger thread: old dum string inserted:", self.dumstr2, self.wordlist)


  def stop_logger_loop(self):
    self.var = False

  #Keylogger 
  def run(self):
    print('Logger thread: Run Run')

    #Read user.ini
    srvurl, username, password, time_interval, nspaces, nwords, updateinterval, _ignoredapps = read_user_ini()
    settingsl = [srvurl, username, password, time_interval, nspaces, nwords, updateinterval, _ignoredapps]

    #Number 
    numoftopics = 10

    #List of urls
    urlstr = []

    #global urlstr
    global var

    countspaces = 0
    #sleep_interval = 0.005
    #nokeypress_interval = 4.0

    #starttime = datetime.datetime.now().time().second
    now = time.time()
    dumstr = ''

    string_to_send = None
    timestamp = now

    ignoredapps = _ignoredapps.split(';')

    print("Logger thread: Ready for logging")

    while self.var:

      #time.sleep(sleep_interval)
      #changed, modifiers, keys = socket.recv()
      key_kc = self.socket.recv()
      key_kc = key_kc.decode("utf-8")

      print(type(key_kc))
      #The keys is a string of the form "keyvalue:keycode"
      keys = "?"
      application = "?"
      try:
        keys, kc, application = key_kc.split(":")
      except ValueError:
        kc = -1
      try:
        kc = int(kc)
      except ValueError:
        kc = -1

      if kc in self.special_keys:
        keys = self.special_keys[kc]

      print('keys: ', keys, 'kc: ', kc)

      if application in ignoredapps:
        print('Ignoring key pressed in an ignored application:', application)
        continue

      #print modifiers
      #print changed, modifiers, keys
      keys  = str(keys)

      #Take care that ctrl is not pressed at the same time
      if True: #not (modifiers['left ctrl'] or modifiers['right ctrl']):
          #Take current time
          cdate = datetime.datetime.now().date()
          ctime = datetime.datetime.now().time()

          cmachtime = time.time()
          var2 = cmachtime > now + float(time_interval)
          var3 = cmachtime > now + float(updateinterval)

          if kc == 51:
            keys = ''
            #Convert current string into list of characters
            duml = list(dumstr)
            if len(duml) > 0:
              #Delete the last character from the string list
              del( duml[len(duml)-1] )
              #Convert back to string
              dumstr = "".join(duml)

          #elif keys in ['<enter>', '<tab>','<right ctrl>','<left ctrl>',' ']:
          elif kc in [36, 48, 49]:
            print('Keycodes: ', kc)
            print('Logger thread: keys: ', keys)
            #print 'Logger thread: changed: ', changed[0]
            #keys = ' '
            if len(dumstr)>0:
              self.wordlist.append(dumstr)
            #print wordlist
            print('Logger thread: wordlist:', self.wordlist[-nwords:])
            dwordlist = self.wordlist[-nwords:]
            #dumstr = dumstr + keys
            countspaces = countspaces + 1
            dumstr = ''
            self.dumstr2 = ''
            for i in range( len(dwordlist) ):
              self.dumstr2 = self.dumstr2 + dwordlist[i] + ' '

            #Print the typed words to a file 'typedwords.txt'
            f = open('typedwords.txt', 'a')
            f.write(str(cdate) + ' ' + str(ctime) + ' ' + self.dumstr2 + '\n')

            self.update.emit(self.dumstr2)

            if var2:
              #Empty the dumstr2 after time_interval period of time
              self.dumstr2 = ''

          elif kc in [-1, 123, 124, 125, 126]: # arrow keys
            pass

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
            if stringlist[i] == "ignored_applications:":
                    ignoredapps = stringlist[i+1]

    return srvurl, usrname, password, time_interval, nspaces, numwords, updateinterval, ignoredapps
