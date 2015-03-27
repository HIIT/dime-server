#!/usr/bin/env python

import os.path
import sys
import shutil
import socket
import subprocess
import requests
import json
import hashlib
import sqlite3
import time

from zg2dimeglobals import config
import zg2dimeconf as conf

debug = False

# -----------------------------------------------------------------------

def json_to_md5(payload):
    json_payload = json.dumps(payload)
    md5 = hashlib.md5()
    md5.update(json_payload)
    return md5.hexdigest()

# -----------------------------------------------------------------------

def run():

    print "Starting the chrome2dime.py logger on " + time.strftime("%c")

    if not config.has_key('history_file_chrome'):
        print "ERROR: Chrome history file not specified"
        return

    if not os.path.isfile(config['history_file_chrome']):
        print "ERROR: Chrome history file not found at: " + config['history_file_chrome']
        return

    shutil.copy(config['history_file_chrome'], config['tmpfile_chrome'])
    if not os.path.isfile(config['tmpfile_chrome']):
        print "ERROR: Failed copying Chrome history to: " + config['tmpfile_chrome']
        return

    conn = sqlite3.connect(config['tmpfile_chrome'])
    c = conn.cursor()
    
    i = 0
    for row in c.execute('''select strftime('%Y-%m-%dT%H:%M:%SZ',(last_visit_time/1000000)-11644473600, 'unixepoch'),url,title from  urls order by last_visit_time desc'''):

        storage = 'net'
        mimetype = 'unknown'
        
        datetime = row[0]
        uri      = row[1]
        text     = row[2]
        #print "[%s] => [%s]" % (sd, item_datetime)

        payload = {'origin':                 config['hostname'],
                   'actor':                  'Google Chrome',
                   'interpretation':         'http://www.zeitgeist-project.com/ontologies/2010/01/27/zg#AccessEvent',
                   'manifestation':          'http://www.zeitgeist-project.com/ontologies/2010/01/27/zg#UserActivity',
                   'timestamp':              datetime,
                   'subject': {
                       'uri':            uri,
                       'interpretation': 'http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#Document',
                       'manifestation':  'http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#RemoteDataObject',
                       'mimetype':       mimetype,
                       'storage':        storage,
                       'text':           text}
                  }

        payload['subject']['id'] = json_to_md5(payload['subject'])
        payload['id'] = json_to_md5(payload)
        json_payload = json.dumps(payload)
        print(json_payload)
    
        headers = {'content-type': 'application/json'}
    
        r = requests.post(config['server_url'], data=json_payload, headers=headers)
        print(r.text)
        print "########################################################"
    
        i = i+1
    
        if i>=config['nevents_chrome'] or debug:
            break

    print "Submitted %d entries" % i

    return True

# -----------------------------------------------------------------------

if __name__ == '__main__':

    print "Starting the zg2dime.py logger on " + time.strftime("%c")

    config['hostname'] = socket.gethostbyaddr(socket.gethostname())[0]

    conf.process_config("zg2dime.ini")
    conf.process_config("user.ini")

    if len(sys.argv)>1:
        if sys.argv[-1] == 'debug':
            config['server_url'] = 'http://httpbin.org/post'
            debug = True
        elif sys.argv[-1] == 'lots':
            config['nevents_chrome'] = 1000
        else:
            print "ERROR: Unrecognized command-line option: " +  sys.argv[-1]
            sys.exit()

    run()

# -----------------------------------------------------------------------