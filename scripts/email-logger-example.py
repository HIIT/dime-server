#!/usr/bin/env python3

import requests
import sys
import socket
import time
import json

#------------------------------------------------------------------------------

server_url = 'http://localhost:8080/api'
server_username = 'mvsjober'
server_password = 'tBaiTwIIAjB+YGg24F59zH9p'

#------------------------------------------------------------------------------

r = requests.post(server_url + '/ping')

if r.status_code != requests.codes.ok:
    print('No connection to DiMe server!')
    sys.exit(1)

print('DiMe returns:', json.dumps(r.json(), indent=2))

# Set all the standard event fields
payload = {
    '@type':    'MessageEvent',
    'actor':    'email-logger-example.py',
    'origin':   socket.gethostbyaddr(socket.gethostname())[0],
    'type':     'http://www.hiit.fi/ontologies/dime/#EmailEvent',
    'start':    time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()),
    'duration': 0,
    'targettedResource': {
        '@type': 'Message',
        'uri':   'Message-ID:558A8F73.20602@cs.helsinki.fi',
        'type':  'http://www.semanticdesktop.org/ontologies/2007/03/22/nmo/#Email',
        'plainTextContent': """
Hi,
I share with you a summary of the suggestions I collected since the last 
Big Meeting.

Patrik""",
        'isStoredAs': 'http://www.semanticdesktop.org/ontologies/2007/03/22/nmo/#MailboxDataObject',
        'date':       'Wed, 24 Jun 2015 14:07:31 +0300',
        'subject':    '[Reknow-principal-researchers] Suggestions for how to improve the Re:Know Big Meetings',
        'fromString': 'Patrik Floreen <patrik.floreen@cs.helsinki.fi>',
        'toString':   'reknow-principal-researchers@hiit.fi',
        'tags': ['email', 'reknow'],
        #'ccString': [],
        #'attachments': [],
        #'rawMessage': '' # the full raw message here...
    }
}

r = requests.post(server_url + '/data/event',
                  data=json.dumps(payload),
                  headers={'content-type': 'application/json'},
                  auth=(server_username, server_password),
                  timeout=10)

print('DiMe returns:', json.dumps(r.json(), indent=2))
