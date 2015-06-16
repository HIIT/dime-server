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

# For DiMe server queries
import requests
import socket
import json

import subprocess   # for running bash script

# For opening links
import webbrowser

#For GUI
from PyQt4 import QtCore, QtGui, uic

import ExtendedQLabel

from PyQt4.QtGui import *
from PyQt4.QtCore import *


#form_class = uic.loadUiType("guikeylog3.ui")[0]

class WindowClass(QtGui.QMainWindow):
#class WindowClass(QtGui.QWidget):
    
    def __init__(self):
      super(WindowClass, self).__init__()
      #QtGui.QWidget.__init__(self)

      #Set the window title
      self.setWindowTitle('Keylogger')

      #Always on top
      self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

      #Create menubar
      menubar = self.menuBar()
      filemenu = menubar.addMenu('&File')
      filemenu.addAction('Quit', self.quitting)

      #Bind the event handlers to the button
      self.quitbutton = QtGui.QPushButton("Quit",self)
      self.quitbutton.resize(40,20)
      self.quitbutton.clicked.connect(self.quitting)
      self.quitbutton.move(270,7)
      #self.quitbutton.move(50,5)


      #Set color of labels
      palette = QtGui.QPalette()
      palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.darkGreen)

      #Make clickable labels
      self.pathlabel = ExtendedQLabel.ExtendedQLabel()
      self.connect(self.pathlabel, SIGNAL('clicked()'), self.pathlabel.open_url)
      self.pathlabel.resize(200,20)
      self.pathlabel.move(30,40)
      self.pathlabel.setPalette(palette)

      self.pathlabel_2 = ExtendedQLabel.ExtendedQLabel("",self)
      self.connect(self.pathlabel_2, SIGNAL('clicked()'), self.pathlabel_2.open_url)
      self.pathlabel_2.resize(200,20)
      self.pathlabel_2.move(30,70)
      self.pathlabel_2.setPalette(palette)

      self.pathlabel_3 = ExtendedQLabel.ExtendedQLabel("",self)
      self.connect(self.pathlabel_3, SIGNAL('clicked()'), self.pathlabel_3.open_url)
      self.pathlabel_3.resize(200,20)
      self.pathlabel_3.move(30,90)
      self.pathlabel_3.setPalette(palette)

      self.pathlabel_4 = ExtendedQLabel.ExtendedQLabel("",self)
      self.connect(self.pathlabel_4, SIGNAL('clicked()'), self.pathlabel_4.open_url)      
      self.pathlabel_4.resize(200,20)
      self.pathlabel_4.move(30,110)
      self.pathlabel_4.setPalette(palette)

      self.pathlabel_5 = ExtendedQLabel.ExtendedQLabel("",self)
      self.connect(self.pathlabel_5, SIGNAL('clicked()'), self.pathlabel_5.open_url)
      self.pathlabel_5.resize(200,20)
      self.pathlabel_5.move(30,130)
      self.pathlabel_5.setPalette(palette)

      #Create labellist
      self.labellist = []
      self.labellist.append(self.pathlabel)
      self.labellist.append(self.pathlabel_2)
      self.labellist.append(self.pathlabel_3)
      self.labellist.append(self.pathlabel_4)
      self.labellist.append(self.pathlabel_5)
      
      #Create QGroupbox
      self.mygroupbox = QtGui.QGroupBox("Links to suggested resources:",self)
      self.myform = QtGui.QFormLayout()
      #Add rows into Layout
      self.myform.addRow(self.labellist[0])
      self.myform.addRow(self.labellist[1])
      self.myform.addRow(self.labellist[2])
      self.myform.addRow(self.labellist[3])
      self.myform.addRow(self.labellist[4])
      #Add self.myform to self.mygroupbox
      self.mygroupbox.setLayout(self.myform)

      #Create scrollbar area
      self.scrollArea = QtGui.QScrollArea(self)
      self.scrollArea.setWidget(self.mygroupbox)
      self.scrollArea.setWidgetResizable(True)
      self.scrollArea.setFixedHeight(200)
      self.scrollArea.setFixedWidth(300)
      self.scrollArea.move(10,30)
      
      #
      #self.setGeometry(300, 600, 400, 200)
      self.setGeometry(0, 0, 320, 240)

      #Get the current path
      self.pathstr = os.path.dirname(os.path.realpath(sys.argv[0]))

      #Initial time
      self.cdate          = str(datetime.datetime.now().date())
      self.time           = str(datetime.datetime.now().time())
      #
      self.done           = False
      #
      self.sleep_interval = 1.005

    def startlog(self):
      threading.Thread(target = log3, args = () ).start()

    def show_link(self):
      threading.Thread(target = update_visible_link, args = (self,)).start()

    def open_url(self):
      global urlstr
      webbrowser.open(urlstr)

    def quitting(self):
      global var
      var = False
      QtCore.QCoreApplication.instance().quit()

################################################################


# linux only!
assert("linux" in sys.platform)


x11 = ct.cdll.LoadLibrary(find_library("X11"))
display = x11.XOpenDisplay(None)


# this will hold the keyboard state.  32 bytes, with each
# bit representing the state for a single key.
keyboard = (ct.c_char * 32)()

# these are the locations (byte, byte value) of special
# keys to watch
shift_keys = ((6,4), (7,64))
modifiers = {
    "left shift": (6,4),
    "right shift": (7,64),
    "left ctrl": (4,32),
    "right ctrl": (13,2),
    "left alt": (8,1),
    "right alt": (13,16)
}
last_pressed = set()
last_pressed_adjusted = set()
last_modifier_state = {}
caps_lock_state = 0

# key is byte number, value is a dictionary whose
# keys are values for that byte, and values are the
# keys corresponding to those byte values
key_mapping = {
    1: {
        0b00000010: "<esc>",
        0b00000100: ("1", "!"),
        #0b00001000: ("2", "@"),
        0b00001000: ("2", "@"),
        0b00010000: ("3", "#"),
        0b00100000: ("4", "$"),
        0b01000000: ("5", "%"),
        #0b10000000: ("6", "^"),
        0b10000000: ("6", "&"),
    },
    2: {
        #0b00000001: ("7", "&"),
        0b00000001: ("7", "/"),
        #0b00000010: ("8", "*"),
        0b00000010: ("8", "("),
        #0b00000100: ("9", "("),
        0b00000100: ("9", ")"),
        #0b00001000: ("0", ")"),
        0b00001000: ("0", "="),
        #0b00010000: ("-", "_"),
        0b00010000: ("+", "?"),
        #0b00100000: ("=", "+"),
        0b00100000: ("´", "`"),
        0b01000000: "<backspace>",
        0b10000000: "<tab>",
    },
    3: {
        0b00000001: ("q", "Q"),
        0b00000010: ("w", "W"),
        0b00000100: ("e", "E"),
        0b00001000: ("r", "R"),
        0b00010000: ("t", "T"),
        0b00100000: ("y", "Y"),
        0b01000000: ("u", "U"),
        0b10000000: ("i", "I"),
    },
    4: {
        0b00000001: ("o", "O"),
        0b00000010: ("p", "P"),
        0b00000100: ("[", "{"),
        0b00001000: ("]", "}"),
        0b00010000: "<enter>",
        0b00100000: "<left ctrl>",
        0b01000000: ("a", "A"),
        0b10000000: ("s", "S"),
    },
    5: {
        0b00000001: ("d", "D"),
        0b00000010: ("f", "F"),
        0b00000100: ("g", "G"),
        0b00001000: ("h", "H"),
        0b00010000: ("j", "J"),
        0b00100000: ("k", "K"),
        0b01000000: ("l", "L"),
        0b10000000: ("ö", "Ö"),
        #0b10000000: (";", ":"),
    },
    6: {
        #0b00000001: ("'", "\""),
        0b00000001: ("ä", "Ä"),
        0b00000010: ("`", "~"),
        #0b00000100: "<left shift>",
        0b00001000: ("\\", "|"),
        0b00010000: ("z", "Z"),
        0b00100000: ("x", "X"),
        0b01000000: ("c", "C"),
        0b10000000: ("v", "V"),
    },
    7: {
        0b00000001: ("b", "B"),
        0b00000010: ("n", "N"),
        0b00000100: ("m", "M"),
        #0b00001000: (",", "<"),
        0b00001000: (",", ";"),
        #0b00010000: (".", ">"),
        0b00010000: (".", ":"),
        #0b00100000: ("/", "?"),
        0b00100000: ("-", "_"),
        #0b01000000: "<right shift>",
    },
    8: {
        #0b00000001: "<left alt>",
        0b00000010: " ",
        0b00000100: "<caps lock>",
    },
    13: {
        0b00000010: "<right ctrl>",
        #0b00010000: "<right alt>",
    },
}




def fetch_keys_raw():
    x11.XQueryKeymap(display, keyboard)
    return keyboard


def fetch_keys():
    global caps_lock_state, last_pressed, last_pressed_adjusted, last_modifier_state
    keypresses_raw = fetch_keys_raw()

    # check modifier states (ctrl, alt, shift keys)
    modifier_state = {}
    for mod, (i, byte) in modifiers.iteritems():
        modifier_state[mod] = bool(ord(keypresses_raw[i]) & byte)
    
    # shift pressed?
    shift = 0
    for i, byte in shift_keys:
        if ord(keypresses_raw[i]) & byte:
            shift = 1
            break

    # caps lock state
    if ord(keypresses_raw[8]) & 4: caps_lock_state = int(not caps_lock_state)


    # aggregate the pressed keys
    pressed = []
    for i, k in enumerate(keypresses_raw):
        o = ord(k)
        if o:
            for byte,key in key_mapping.get(i, {}).iteritems():
                if byte & o:
                    if isinstance(key, tuple): key = key[shift or caps_lock_state]
                    pressed.append(key)

    
    tmp = pressed
    pressed = list(set(pressed).difference(last_pressed))
    state_changed = tmp != last_pressed and (pressed or last_pressed_adjusted)
    last_pressed = tmp
    last_pressed_adjusted = pressed

    if pressed: pressed = pressed[0]
    else: pressed = None


    state_changed = last_modifier_state and (state_changed or modifier_state != last_modifier_state)
    last_modifier_state = modifier_state

    return state_changed, modifier_state, pressed



###
def log2():	

      global urlstr

      sleep_interval = 0.005
      flag = 0
      flag2= 0
      dumstr = ''

      #Show the links of suggested resources in the window
      #update_kurllabel2(self)
	
      f = open('typedwords.txt', 'a')
      while var:
		
        strdum = ''
        sleep(sleep_interval)
        changed, modifiers, keys = fetch_keys()
        keys  = str(keys)


        #Take current time
        cdate = str(datetime.datetime.now().date())
        ctime = str(datetime.datetime.now().time())

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

        elif keys == ' ' or keys == '<tab>' or keys == '<enter>' or keys == '<left ctrl>' or keys == '<right ctrl>':

                f.write(cdate + ' ' + ctime + ' ' + dumstr + '\n')

		if flag2 == 1:

			#Make query from DiMe
			urlstr = search_dime(dumstr)
			print urlstr

			#Add the suggested url into a history file
			if urlstr != None:
				f2 = open("suggested_pages.txt","a")
				f2.write(cdate + ' ' + ctime + ' ' + str(urlstr.json()[0]) + '\n')
				f2.close()

			#Clear the dummy string
			dumstr = ''

		flag = 1
		flag2= 0
        else:
	        cdate = str(datetime.datetime.now().date())
                ctime = str(datetime.datetime.now().time())
		dumstr = dumstr + keys
		flag2= 1


      f.close()



###
def log3():

      global urlstr

      countspaces = 0
      sleep_interval = 0.005
      timeinterval = 10

      #starttime = datetime.datetime.now().time().second
      now = time()
      flag = 0
      flag2= 0
      dumstr = ''

      #Show the links of suggested resources in the window
      #update_kurllabel2(self)

      f = open('typedwords.txt', 'a')
      while var:

        strdum = ''
        sleep(sleep_interval)
        changed, modifiers, keys = fetch_keys()
        keys  = str(keys)


        #Take current time
        cdate = datetime.datetime.now().date()
        ctime = datetime.datetime.now().time()

	cmachtime = time()
        var2 = cmachtime > now + timeinterval

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
		keys = ' '
		dumstr = dumstr + keys
		countspaces = countspaces + 1
        else:
                cdate = datetime.datetime.now().date()
                ctime = datetime.datetime.now().time()
                dumstr = dumstr + keys
        
	if var2 or countspaces == 5:
                f.write(str(cdate) + ' ' + str(ctime) + ' ' + dumstr + '\n')

                #Make query from DiMe
                urlstr = search_dime(dumstr)
		print "foo"
		print countspaces
                print urlstr

                #Add the suggested url into a history file
                if urlstr != None:
	                f2 = open("suggested_pages.txt","a")
                	f2.write(str(cdate) + ' ' + str(ctime) + ' ' + str(urlstr.json()[0]["uri"]) + '\n')
                        f2.close()

                #Clear the dummy string
                dumstr = ''
		countspaces = 0

                flag = 1
                flag2= 0

		now = time()



      f.close()



def update_visible_link(self):
      i = 0
      global urlstr
      global var

      while var:
        sleep(2.0)
        #for i in len(r.json())
	if urlstr != None:
		for i in range( len(urlstr.json()) ):
			if i == 0:
				self.pathlabel.setText(str(urlstr.json()[i]["uri"]))
			elif i == 1:
				self.pathlabel_2.setText(str(urlstr.json()[i]["uri"]))
			elif i == 2:
				self.pathlabel_3.setText(str(urlstr.json()[i]["uri"]))
			elif i == 3:
				self.pathlabel_4.setText(str(urlstr.json()[i]["uri"]))
			elif i == 4:
				self.pathlabel_5.setText(str(urlstr.json()[i]["uri"]))


def search_dime(query):
#def search_dime(server_username, server_password, query)
	#------------------------------------------------------------------------------

	server_url = 'http://localhost:8080/api'
	server_username = 'petrihiit'
	server_password = 'p3tr1h11t'

	#------------------------------------------------------------------------------

	# ping server (not needed, but fun to do :-)
	r = requests.post(server_url + '/ping')

	if r.status_code != requests.codes.ok:
	    print('No connection to DiMe server!')
	    sys.exit(1)

	# make search query
	#query = "dime"
	#query = "python"
	print query

	r = requests.get(server_url + '/search?query={}&limit=5'.format(query),
        	         headers={'content-type': 'application/json'},
                	 auth=(server_username, server_password),
	                 timeout=10)
	
	print len(r.json())

	if len(r.json()) > 0:
		if r.status_code != requests.codes.ok:
		    #print('ErrorNo connection to DiMe server!')
		    r = None
		    #sys.exit(1)

		return r


if __name__ == "__main__":

  #Important global variables!
  global urlstr
  #Initialize urlstr
  urlstr = search_dime("python")

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


  #Start the url updating 
  newwindow.show_link()  

  #Start keylogger
  newwindow.startlog()

  #Start
  app.exec_()

  #
  sys.exit(app.exec_())
