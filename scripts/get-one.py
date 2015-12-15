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

r = requests.get(server_url + '/data/informationelement/1?keywords=true',
                 headers={'content-type': 'application/json'},
                 auth=(server_username, server_password),
                 timeout=10)

if r.status_code != requests.codes.ok:
    print('HTTP Error:', r.status_code)
    sys.exit(1)

print('DiMe returns:', json.dumps(r.json(), indent=2))
