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

payload = {
    '@type':    'FunfEvent',
    'appId':    'foobar1234',
    'actor':    'TestMobileLogger',
    'origin':   socket.gethostbyaddr(socket.gethostname())[0],
    'start':    time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()),
    'probeName': 'WifiProbe',
    'funfValue': '{"some": "json", "here": "ok"}'
}

print('Uploading: ', json.dumps(payload, indent=2))

r = requests.post(server_url + '/data/event',
                  data=json.dumps(payload),
                  headers={'content-type': 'application/json'},
                  auth=(server_username, server_password),
                  timeout=10)

print('DiMe returns:', json.dumps(r.json(), indent=2))
