#!/usr/bin/env python

import time

from gi.repository import Gtk, GLib

try: 
       from gi.repository import AppIndicator3 as AppIndicator  
except:  
       from gi.repository import AppIndicator

class Indicator:

    def __init__(self):
        # param1: identifier of this indicator
        # param2: name of icon. this will be searched for in the standard them
        # dirs
        # finally, the category. We're monitoring CPUs, so HARDWARE.
        self.ind = AppIndicator.Indicator.new(
                            "indicator-zg2dime", 
                            "important",
                            AppIndicator.IndicatorCategory.APPLICATION_STATUS)

        # need to set this for indicator to be shown
        self.ind.set_status (AppIndicator.IndicatorStatus.ACTIVE)

        # have to give indicator a menu
        self.menu = Gtk.Menu()

        # you can use this menu item for experimenting
        item = Gtk.MenuItem()
        item.set_label("zg2dime.py logger started on " + time.strftime("%c"))
        item.show()
        self.menu.append(item)
        
        self.zgitem = Gtk.MenuItem()
        self.zgitem.set_label("Zeitgeist: waiting for data...")
        self.zgitem.hide()
        self.menu.append(self.zgitem)

        self.chitem = Gtk.MenuItem()
        self.chitem.set_label("Chrome: waiting for data...")
        self.chitem.hide()
        self.menu.append(self.chitem)

        # this is for exiting the app
        #item = Gtk.MenuItem()
        #item.set_label("Exit")
        #item.connect("activate", self.handler_menu_exit)
        #item.show()
        #self.menu.append(item)

        self.menu.show()
        self.ind.set_menu(self.menu)

    def update(self, stats):
        self.zgitem.set_label("Zeitgeist: Events sent: %d, data sent: %d bytes" % (stats['nevents'], stats['data_sent']))
        self.zgitem.show()

    def handler_menu_exit(self, evt):
        print "handler_menu_exit";

    def main(self):
        Gtk.main()

if __name__ == '__main__':
    ind = Indicator()
    ind.main()
