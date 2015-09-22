#!/usr/bin/env python3

import requests
import sys
import socket
import time
import json

#------------------------------------------------------------------------------

server_url = 'http://localhost:8080/api'
server_username = 'testuser'
server_password = 'testuser123'

#------------------------------------------------------------------------------

r = requests.post(server_url + '/ping')

if r.status_code != requests.codes.ok:
    print('No connection to DiMe server!')
    sys.exit(1)

print('DiMe returns:', json.dumps(r.json(), indent=2))

# Set all the standard event fields
payload = {
    '@type':    'SearchEvent',
    'actor':    'logger-example.py',
    'origin':   socket.gethostbyaddr(socket.gethostname())[0],
    'type':     'http://www.hiit.fi/ontologies/dime/#ExampleSearchEvent',
    'start':    time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()),
    'tags': ['tag1', 'tag2'],
    'duration': 0,
}

payload['query'] = "dummy search"

r = requests.post(server_url + '/data/event',
                  data=json.dumps(payload),
                  headers={'content-type': 'application/json'},
                  auth=(server_username, server_password),
                  timeout=10)

print('DiMe returns:', json.dumps(r.json(), indent=2))
