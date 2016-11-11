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

def print_res(r):
    print('DiMe returns [HTTP {}]:'.format(r.status_code))
    print(json.dumps(r.json(), indent=2))
    
#------------------------------------------------------------------------------



r = requests.post(server_url + '/ping', auth=(server_username, server_password))
print_res(r)

if r.status_code != requests.codes.ok:
    print('No connection to DiMe server!')
    sys.exit(1)

r = requests.post(server_url + '/updateleaderboard',
                  headers={'content-type': 'application/json'},
                  auth=(server_username, server_password),
                  timeout=10)

print('DiMe returns [HTTP {}]:'.format(r.status_code))
print(json.dumps(r.json(), indent=2))
