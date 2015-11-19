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

# ping server (not needed, but fun to do :-)
r = requests.post(server_url + '/ping')

if r.status_code != requests.codes.ok:
    print('No connection to DiMe server!')
    sys.exit(1)

# make search query
query = "dime"
if len(sys.argv) > 1:
    query = ' '.join(sys.argv[1:])

r = requests.get(server_url + '/search?query={}&limit=10'.format(query),
                 headers={'content-type': 'application/json'},
                 auth=(server_username, server_password),
                 timeout=10)

if r.status_code != requests.codes.ok:
    print('ErrorNo connection to DiMe server!')
    sys.exit(1)

print('DiMe returns:', json.dumps(r.json(), indent=2))
