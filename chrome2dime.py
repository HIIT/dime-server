#!/usr/bin/env python

#import os.path
import sys
import socket
import subprocess
import requests
import json
import hashlib
import sqlite3

def json_to_md5(payload):
    json_payload = json.dumps(payload)
    md5 = hashlib.md5()
    md5.update(json_payload)
    return md5.hexdigest()

hostname = socket.gethostbyaddr(socket.gethostname())[0]

server_url = 'http://localhost:8080/logger/zeitgeist'
debug = 0

if len(sys.argv)>0 and sys.argv[-1] == 'debug':
    #server_url = 'http://httpbin.org/post'
    debug = 1

history_file = "/home/jmakoske/.config/google-chrome/Default/History"
conn = sqlite3.connect(history_file)
c = conn.cursor()

i = 0
for row in c.execute('''select strftime('%Y-%m-%dT%H:%M:%SZ',(last_visit_time/1000000)-11644473600, 'unixepoch'),url,title from  urls order by last_visit_time desc'''):

    storage = 'net'
    mimetype = 'unknown'
        
    datetime = row[0]
    uri      = row[1]
    text     = row[2]
    #print "[%s] => [%s]" % (sd, item_datetime)

    payload = {'origin':                 hostname,
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
    
    r = requests.post(server_url, data=json_payload, headers=headers)
    print(r.text)
    print "########################################################"
    
    i = i+1
    
    if debug:
        break

print "Submitted %d entries" % i
