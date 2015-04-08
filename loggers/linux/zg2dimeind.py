#!/usr/bin/env python

import time

from gi.repository import Gtk, GLib

try: 
       from gi.repository import AppIndicator3 as AppIndicator  
except:  
       from gi.repository import AppIndicator

from zg2dimeglobals import config

# -----------------------------------------------------------------------

class Indicator:

# -----------------------------------------------------------------------

    def __init__(self):
        # param1: identifier of this indicator
        # param2: name of icon. this will be searched for in the standard them
        # dirs
        # finally, the category. We're monitoring CPUs, so HARDWARE.
        self.ind = AppIndicator.Indicator.new(
                            "indicator-zg2dime", 
                            config['icon_indicator'],
                            AppIndicator.IndicatorCategory.APPLICATION_STATUS)

        # need to set this for indicator to be shown
        self.ind.set_status(AppIndicator.IndicatorStatus.ACTIVE)

        # have to give indicator a menu
        self.menu = Gtk.Menu()

        # you can use this menu item for experimenting
        item = Gtk.MenuItem()
        item.set_label("zg2dime.py logger started on " + time.strftime("%c"))
        item.show()
        self.menu.append(item)
        
        self.zeitgeistitem = Gtk.MenuItem()
        self.zeitgeistitem.set_label("Zeitgeist: waiting for data...")
        self.zeitgeistitem.hide()
        self.menu.append(self.zeitgeistitem)

        self.chromeitem = Gtk.MenuItem()
        self.chromeitem.set_label("Chrome: waiting for data...")
        self.chromeitem.hide()
        self.menu.append(self.chromeitem)

        self.chromiumitem = Gtk.MenuItem()
        self.chromiumitem.set_label("Chromium: waiting for data...")
        self.chromiumitem.hide()
        self.menu.append(self.chromiumitem)

        self.firefoxitem = Gtk.MenuItem()
        self.firefoxitem.set_label("Chromium: waiting for data...")
        self.firefoxitem.hide()
        self.menu.append(self.firefoxitem)

        # this is for exiting the app
        #item = Gtk.MenuItem()
        #item.set_label("Exit")
        #item.connect("activate", self.handler_menu_exit)
        #item.show()
        #self.menu.append(item)

        self.menu.show()
        self.ind.set_menu(self.menu)

# -----------------------------------------------------------------------

    def agostr(self, ago):
        if ago<10:
            return '(last just now)'
        agounit = 'secs'
        if ago>(24*60*60):
            ago = int(ago/(24*60*60))
            if ago==1:
                agounit = 'day'
            else:
                agounit = 'days'
        elif ago>(60*60):
            ago = int(ago/(60*60))
            if ago==1:
                agounit = 'hour'
            else:
                agounit = 'hours'
        elif ago>60:
            ago = int(ago/60)
            if ago==1:
                agounit = 'min'
            else:
                agounit = 'mins'

        return '(last %d %s ago)' % (ago, agounit)

# -----------------------------------------------------------------------

    def update(self, stats):
        now = int(time.time())

        if stats['zeitgeist']['events_sent']:
            ago = now-stats['zeitgeist']['latest']
            self.zeitgeistitem.set_label(("Zeitgeist: Events sent: %d %s, "+
                                         "data sent: %d bytes") % 
                                         (stats['zeitgeist']['events_sent'], 
                                          self.agostr(ago), 
                                          stats['zeitgeist']['data_sent']))
            self.zeitgeistitem.show()

        if stats['chrome']['events_sent']:
            ago = now-stats['chrome']['latest']
            self.chromeitem.set_label(("Chrome: Events sent: %d %s, "+
                                      "data sent: %d bytes") % 
                                      (stats['chrome']['events_sent'], 
                                       self.agostr(ago), 
                                       stats['chrome']['data_sent']))
            self.chromeitem.show()

        if stats['chromium']['events_sent']:
            ago = now-stats['chromium']['latest']
            self.chromiumitem.set_label(("Chromium: Events sent: %d %s, "+
                                      "data sent: %d bytes") % 
                                      (stats['chromium']['events_sent'], 
                                       self.agostr(ago), 
                                       stats['chromium']['data_sent']))
            self.chromiumitem.show()

        if stats['firefox']['events_sent']:
            ago = now-stats['firefox']['latest']
            self.firefoxitem.set_label(("Firefox: Events sent: %d %s, "+
                                      "data sent: %d bytes") % 
                                      (stats['firefox']['events_sent'], 
                                       self.agostr(ago), 
                                       stats['firefox']['data_sent']))
            self.firefoxitem.show()

#    def handler_menu_exit(self, evt):
#        print "handler_menu_exit";

# -----------------------------------------------------------------------

    def main(self):
        Gtk.main()

# -----------------------------------------------------------------------

if __name__ == '__main__':
    ind = Indicator()
    ind.main()
