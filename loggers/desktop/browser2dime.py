#!/usr/bin/env python

import sys
import time

from zg2dimeglobals import config
import zg2dimeconf as conf
import zg2dimecommon as common
import chrome2dime

# -----------------------------------------------------------------------

if __name__ == '__main__':

    print "Starting the browser2dime.py logger on " + time.strftime("%c")

    conf.configure()

    if len(sys.argv)>1:
        if sys.argv[-1] == 'debug':
            config['server_url'] = 'http://httpbin.org/post'
            config['nevents'] = 1
        elif sys.argv[-1] == 'all':
            config['nevents'] = 1000

    pingstring = "Pinging DiMe server at location: " + config['server_url'] + " : "
    if common.ping_server():
        print pingstring + "OK"
    else:
        print pingstring + "FAILED"

    documents = set()

    actors = config['actors'].copy()

    if config['use_chrome']:
        chromelogger = chrome2dime.Browserlogger('chrome')
    if config['use_chromium']:
        chromiumlogger = chrome2dime.Browserlogger('chromium')
    if config['use_firefox']:
        firefoxlogger = chrome2dime.Browserlogger('firefox')

    nextrun_chrome, nextrun_chromium, nextrun_firefox = 0, 0, 0

    while 1:
        now = int(time.time())

        if config['use_chrome'] and now > nextrun_chrome:
            chromelogger.run()
            nextrun_chrome = now + config['interval_chrome']
            print ("Chrome logger done, next run on %s (waiting for %s secs)"
            % (time.strftime("%c", time.localtime(nextrun_chrome)), 
               config['interval_chrome']))

        if config['use_chromium'] and now > nextrun_chromium:
            chromiumlogger.run()
            nextrun_chromium = now + config['interval_chromium']
            print ("Chromium logger done, next run on %s (waiting for %s secs)"
            % (time.strftime("%c", time.localtime(nextrun_chromium)), 
               config['interval_chromium']))

        if config['use_firefox'] and now > nextrun_firefox:
            firefoxlogger.run()
            nextrun_firefox = now + config['interval_firefox']
            print ("Firefox logger done, next run on %s (waiting for %s secs)"
            % (time.strftime("%c", time.localtime(nextrun_firefox)), 
               config['interval_firefox']))

        time.sleep(1)

# -----------------------------------------------------------------------
